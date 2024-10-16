"""
Main class for the gaze detector.
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

import datetime
import pathlib
from typing import Optional, Tuple, Dict
from threading import Event, Lock

import cv2
import numpy as np
from omegaconf import OmegaConf

from common import constants as cc, keyboard
from common.logger_helper import init_logger
from common.omegaconf_helper import conf_key_from_value
from common.loop import run_loop_with_max_tickrate
from common.PeekableQueue import PeekableQueue

from . import constants as c
from .face import Face
from .face_model_mediapipe import FaceModelMediaPipe
from .face_parts import FacePartsName
from .visualiser import Visualiser
from .gaze_estimator import GazeEstimator
from .utils import transforms

logger = init_logger()


class GazeDetector:
    """
    Gaze Detector class for eye tracking.
    """

    def __init__(
        self,
        config: OmegaConf,
        stop_event: Optional[Event] = None,
        thread_data: Optional[Dict] = None,
        data_lock: Optional[Lock] = None,
    ):
        """
        Args:
            config: Configuration object
            stop_event: Event object to stop the gaze detector
            thread_data: Shared data dictionary
            data_lock: Lock object for shared data
        """

        logger.info("Initialising Gaze Detector")

        required_args = [stop_event, thread_data, data_lock]
        self.running_in_thread = any(required_args)

        if self.running_in_thread:
            # If running in thread mode, all or none of the required args must be provided
            if not all(required_args):
                raise ValueError(
                    "All or none of stop_event, thread_data, data_lock must be provided.")

            logger.info("Running in thread mode")
            self.stop_event = stop_event
            self.thread_data = thread_data
            self.data_lock = data_lock

            logger.debug("Initialising thread helper functions")
            # Lazily import thread helpers only if running in thread mode
            from common.thread_helper import thread_loop_handler, thread_exit

            # Bind to class attributes so we can access them in class methods
            self.thread_loop_handler = thread_loop_handler
            self.thread_exit = thread_exit

            logger.debug("Thread initialisation complete")
        else:
            logger.info("Running in main mode")

        self.config = config
        self.gaze_estimator = GazeEstimator(config)
        face_model_3d = FaceModelMediaPipe()
        self.camera_visualiser = Visualiser(
            self.gaze_estimator.camera, face_model_3d.NOSE_INDEX)
        self.gaze_visualiser = Visualiser(
            self.gaze_estimator.camera, face_model_3d.NOSE_INDEX)

        self.cap = self._create_capture()
        self.output_dir = self._create_output_dir()
        self.writer = self._create_video_writer()

        self.loop_enabled = True
        self.stop = False
        self.show_bbox = self.config.demo.show_bbox
        self.show_head_pose = self.config.demo.show_head_pose
        self.show_landmarks = self.config.demo.show_landmarks
        self.show_normalized_image = self.config.demo.show_normalized_image
        self.show_template_model = self.config.demo.show_template_model
        self.show_gaze_vector = self.config.demo.show_gaze_vector

        # Calibration
        self.calibrated = False
        self.calibration_landmarks = None

        # Gaze Vector
        self.average_eye_distance = None
        self.average_eye_center = None
        self.average_gaze_vector = None

        # Point on screen
        self.point_buffer = []
        self.gaze_2d_point = None

        # Hitboxes
        self.hitboxes = None

        # Keyboard bindings
        self.keyboard_bindings = self.config.keyboard_bindings

    def _init_hitboxes(self) -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Initialise the left and right hit-boxes.

        Returns:
            Dictionary of hit-boxes: {LEFT: (top_left, bottom_right), RIGHT: (top_left, bottom_right)}
        """
        logger.info("Initializing hit-boxes")

        resolution_2d = self.camera_visualiser.get_2d_resolution()
        out_height, out_width = resolution_2d

        hitbox_width = int(out_width * self.config.demo.hitbox_width_proprtion)
        logger.debug("Hit-box width: %d", hitbox_width)

        # Left hit-box
        left_hitbox_top_left = (0, 0)
        left_hitbox_bottom_right = (hitbox_width, out_height)
        left_hitbox = {c.TOP_LEFT: left_hitbox_top_left,
                       c.BOTTOM_RIGHT: left_hitbox_bottom_right}
        logger.debug("Left hit-box: %d", left_hitbox)

        # Right hit-box
        right_hitbox_top_left = (int(out_width - hitbox_width), 0)
        right_hitbox_bottom_right = (out_width, out_height)
        right_hitbox = {c.TOP_LEFT: right_hitbox_top_left,
                        c.BOTTOM_RIGHT: right_hitbox_bottom_right}
        logger.debug("Right hit-box: %d", right_hitbox)

        return {cc.LEFT: left_hitbox, cc.RIGHT: right_hitbox}

    def run(self) -> None:
        """
        Wraps the main loop for the gaze detector based on config settings.

        Returns:
            None
        """
        if self.config.demo.use_camera or self.config.demo.video_path:
            self._run_on_video()
        elif self.config.demo.image_path:
            self._run_on_image()
        else:
            raise ValueError

    def _run_on_image(self):
        """
        Runs the gaze detector on a single image or frame.

        Returns:
            None
        """
        image = cv2.imread(self.config.demo.image_path)
        self._process_image(image)
        if self.config.demo.display_on_screen:
            while True:
                key_pressed = self._wait_key()
                if self.stop:
                    logger.info(
                        "Stopping gaze detector from user exit signal.")
                    break

                if key_pressed:
                    self._process_image(image)

                self._render_frame("image", 0.0)

        if self.config.demo.output_dir:
            name = pathlib.Path(self.config.demo.image_path).name
            output_path = pathlib.Path(self.config.demo.output_dir) / name
            logger.info("Saving output to %s", output_path)
            cv2.imwrite(output_path.as_posix(), self.camera_visualiser.image)

        if self.running_in_thread:
            # Exit parent thread
            self.thread_exit(self.stop_event)

    def _run_on_video(self) -> None:
        """
        Run the gaze detector on a video feed. Can be
        a camera feed or a video file.

        Returns:
            None
        """
        logger.info("Running gaze detector on video feed")
        if self.config.demo.display_on_screen:
            if self.running_in_thread:
                logger.info("Video feed will be relayed to GUI in main thread")
            else:
                logger.info("Video feed will be displayed on screen")

        run_loop_with_max_tickrate(
            self.config.demo.max_tick_rate, self._gaze_loop)

        self.cap.release()
        if self.writer:
            self.writer.release()

        if self.running_in_thread:
            # Exit parent thread
            self.thread_exit(self.stop_event)

    def _gaze_loop(self, tick_rate: float) -> bool:
        """
        A single iteration of the gaze loop in threaded mode.

        Returns:
            True if the gaze loop should continue, False otherwise
        """
        logger.debug(">>> Begin eye tracking loop")

        if self.running_in_thread:
            self.thread_loop_handler(self.stop_event)

        if self.config.demo.display_on_screen:
            self._wait_key()
            if self.stop:
                return False

        ok, frame = self._read_camera()
        if not ok:
            return False

        self._process_image(frame)

        if self.config.demo.display_on_screen:
            self._render_frame("frame", tick_rate)

        logger.debug("<<< End eye tracking loop")
        return not self.stop

    def _render_frame(self, win_name: str, tick_rate: float) -> None:
        """
        Renders a frame where it needs to go

        Args:
            win_name [str]: Window name
            tick_rate [float]: Tick rate of the gaze loop

        Returns:
            None
        """

        if self.running_in_thread:
            if self.camera_visualiser.image is None:
                logger.trace("No image to render.")
                return

            with self.data_lock:
                self.thread_data[cc.EYE_TRACKING][cc.VIDEO_FRAME] = self.camera_visualiser.image
                self.thread_data[cc.EYE_TRACKING][cc.TICK_RATE] = tick_rate

            logger.debug("Set video frame in shared data.")
        else:
            # Render fps on the image
            if self.config.demo.show_fps:
                self.camera_visualiser.draw_fps(tick_rate)

            cv2.imshow(win_name, self.camera_visualiser.image)

    def _read_camera(self) -> Tuple[bool, np.ndarray]:
        """
        Read the camera feed and upscale the frame.

        Returns:
            Tuple of boolean and frame
        """
        ok, frame = self.cap.read()
        if not ok:
            return ok, frame

        # Upscale feed
        upscaled_frame = transforms.upscale(
            frame, self.config.demo.upscale_dim)
        return ok, upscaled_frame

    def _process_image(self, image) -> None:
        """
        Process the image to detect faces and estimate gaze.

        Args:
            image: Image to process

        Returns:
            None
        """
        undistorted = self._undistort_image(image)
        self.camera_visualiser.set_image(image.copy())

        if self.loop_enabled:
            if self.hitboxes is None:
                self.hitboxes = self._init_hitboxes()

            faces = self.gaze_estimator.detect_faces(undistorted)
            for face in faces:
                self._draw_landmarks(face)
                self._draw_face_bbox(face)
                if self.calibrated:
                    self.gaze_estimator.estimate_gaze(undistorted, face)
                    self._draw_head_pose(face)
                    self._draw_face_template_model(face)
                    self._draw_gaze_vector(face)
                    self._draw_gaze_point()
                    self._display_normalized_image(face)

        if self.config.demo.use_camera:
            self.camera_visualiser.flip_image()

            if self.loop_enabled:
                self._flip_points()

        if self.loop_enabled:
            for face in faces:
                if self.calibrated:
                    self._draw_gaze_region()

        if self.writer:
            self.writer.write(self.camera_visualiser.image)

    def _undistort_image(self, image: np.ndarray) -> np.ndarray:
        """
        Undistort the image using the camera matrix and distortion coefficients.

        Args:
            image: Image to undistort

        Returns:
            Undistorted image
        """
        return cv2.undistort(image, self.gaze_estimator.camera.camera_matrix, self.gaze_estimator.camera.dist_coefficients)

    def _create_capture(self) -> Optional[cv2.VideoCapture]:
        """
        Create a capture object for the camera or video file.

        Returns:
            VideoCapture object or None
        """
        if self.config.demo.image_path:
            return None
        if self.config.demo.use_camera:
            # Determine if there is a camera to use
            if not cv2.VideoCapture(0).isOpened():
                logger.error("No camera available.")
                if self.running_in_thread:
                    self.thread_exit(self.stop_event)
                else:
                    raise ValueError("No camera available.")

            cap = cv2.VideoCapture(0)
        elif self.config.demo.video_path:
            cap = cv2.VideoCapture(self.config.demo.video_path)
        else:
            raise ValueError

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.gaze_estimator.camera.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.gaze_estimator.camera.height)
        return cap

    def _create_output_dir(self) -> Optional[pathlib.Path]:
        """
        Create the output directory if specified in the config.

        Returns:
            Path object or None
        """

        if not self.config.demo.output_dir:
            return
        output_dir = pathlib.Path(self.config.demo.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        return output_dir

    @staticmethod
    def _create_timestamp() -> str:
        """
        Create a timestamp in the format YYYYMMDD_HHMMSS.

        Returns:
            Timestamp string
        """
        dt = datetime.datetime.now()
        return dt.strftime("%Y%m%d_%H%M%S")

    def _create_video_writer(self) -> Optional[cv2.VideoWriter]:
        """
        Create a video writer object if the user has specified an output directory.

        Returns:
            VideoWriter object or None
        """
        if self.config.demo.image_path:
            return None
        if not self.output_dir:
            return None
        ext = self.config.demo.output_file_extension
        if ext == "mp4":
            fourcc = cv2.VideoWriter_fourcc(*"H264")
        elif ext == "avi":
            fourcc = cv2.VideoWriter_fourcc(*"PIM1")
        else:
            raise ValueError
        if self.config.demo.use_camera:
            output_name = f"{self._create_timestamp()}.{ext}"
        elif self.config.demo.video_path:
            name = pathlib.Path(self.config.demo.video_path).stem
            output_name = f"{name}.{ext}"
        else:
            raise ValueError
        output_path = self.output_dir / output_name
        writer = cv2.VideoWriter(output_path.as_posix(
        ), fourcc, 30, (self.gaze_estimator.camera.width, self.gaze_estimator.camera.height))
        if writer is None:
            raise RuntimeError
        return writer

    def _wait_key(self) -> bool:
        """
        Handles keyboard commands either from cv2 GUI if running as module or
        from GUI if running in thread mode. Will handle multiple keys if there is more
        than one in the queue.

        Returns:
            True if a recognised key is pressed (or any if there are multiple in the queue).
            False otherwise.
        """

        if self.running_in_thread:
            if cc.KEYBOARD_QUEUE not in self.thread_data.keys():
                logger.trace(
                    "Keyboard queue not yet initialised in shared data.")
                return False

            keyboard_queue: PeekableQueue = self.thread_data[cc.KEYBOARD_QUEUE]
            key_buffer = keyboard.keyboard_event_loop(
                self.data_lock, keyboard_queue, self.keyboard_bindings)

            accepted_keys = []
            for key_code in key_buffer:
                accepted_keys.append(self._handle_key_event(key_code))

            # Accept if any valid key was pressed
            return any(accepted_keys)
        else:
            key_code = cv2.waitKey(self.config.demo.wait_time) & 0xFF
            if key_code == 255:
                return False

            return self._handle_key_event(key_code)

    def _handle_key_event(self, key_code: int) -> bool:
        """
        Keyboard controller for the gaze detector.

        Args:
            key_code: Key code

        Returns:
            True if a recognised key is pressed, False otherwise
        """

        # Obtain lowercase version of key always. If we need to detect uppercase, we
        # can determine if the shift key is pressed.
        key_chr = keyboard.get_key_chr(key_code)

        logger.info("Received key: %s (%d)", key_chr, key_code)

        if key_chr in cc.QUIT_KEYS:
            self.stop = True
            return True

        key_action = conf_key_from_value(self.keyboard_bindings, key_chr)
        if key_action is None:
            logger.trace("Key %s not found in keybindings", key_chr)
            return False

        if key_action in c.LOOP_ACTIONS:
            match key_chr:
                case self.keyboard_bindings.bbox:
                    self.show_bbox = not self.show_bbox
                case self.keyboard_bindings.landmark:
                    self.show_landmarks = not self.show_landmarks
                case self.keyboard_bindings.head_pose:
                    self.show_head_pose = not self.show_head_pose
                case self.keyboard_bindings.normalized_image:
                    self.show_normalized_image = not self.show_normalized_image
                case self.keyboard_bindings.template_model:
                    self.show_template_model = not self.show_template_model
                case self.keyboard_bindings.gaze_vector:
                    self.show_gaze_vector = not self.show_gaze_vector
                case self.keyboard_bindings.calibrate:
                    # Calibrate
                    logger.info("Setting calibrated to False")
                    self.calibrated = False
                    self._calibrate_landmarks()
                case _:
                    return False

        match key_chr:
            case self.keyboard_bindings.loop_toggle:
                self.loop_enabled = not self.loop_enabled

        return True

    def _calibrate_landmarks(self) -> None:
        """
        Calibrate the face landmarks for gaze estimation.

        Returns:
            None
        """

        # Read camera
        ok, frame = self._read_camera()
        if not ok:
            logger.error("Failed to read camera. Calibration failed.")
            return

        undistorted = self._undistort_image(frame)
        faces = self.gaze_estimator.detect_faces_raw(undistorted)
        if len(faces) != 1:
            logger.info(
                "Ensure only one face is visible in the camera feed then press 'c' to calibrate again.")
            return

        face_landmarks = faces[0]
        self.calibration_landmarks = face_landmarks
        # Add 1 meter to the z-axis ??
        self.calibration_landmarks[:, 2] += 1

        self.gaze_estimator._face_model3d.set_landmark_calibration(
            self.calibration_landmarks)

        self.calibrated = True
        logger.info("Calibration successful.")

    def _flip_points(self) -> None:
        """
        Flips the 2D gaze point along the x-axis to match the flipped image.

        Returns:
            None
        """
        if self.gaze_2d_point is not None:
            self.gaze_2d_point = self.camera_visualiser.flip_point_x(
                self.gaze_2d_point)

    def _draw_face_bbox(self, face: Face) -> None:
        """
        Wrapper to draw a bounding box around the face.

        Args:
            face: Face object

        Returns:
            None
        """

        if not self.show_bbox:
            return
        self.camera_visualiser.draw_bbox(face.bbox)

    def _draw_head_pose(self, face: Face) -> None:
        """
        Draws the head pose of the user as a set of axes.

        Args:
            face: Face object

        Returns:
            None
        """

        if not self.show_head_pose:
            return
        # Draw the axes of the model coordinate system
        length = self.config.demo.head_pose_axis_length
        self.camera_visualiser.draw_model_axes(face, length, lw=2)

        euler_angles = face.head_pose_rot.as_euler("XYZ", degrees=True)
        pitch, yaw, roll = face.change_coordinate_system(euler_angles)
        logger.debug("[head] pitch: %d, yaw: %d, " f"roll: %d, distance: %d",
                     pitch, yaw, roll, face.distance)

    def _draw_landmarks(self, face: Face) -> None:
        """
        Landmarks are 2D points in the upscaled image (pixels).

        Args:
            face: Face object

        Returns:
            None
        """
        if not self.show_landmarks:
            return
        self.camera_visualiser.draw_points(
            face.landmarks, color=(0, 255, 255), size=1)

    def _draw_face_template_model(self, face: Face) -> None:
        """
        Face Template Model is the 3D model of the face in world coordinates (metres)

        Args:
            face: Face object

        Returns:
            None
        """
        if not self.show_template_model:
            return
        self.camera_visualiser.draw_3d_points(
            face.model3d, color=(255, 0, 525), size=1)

    def _display_normalized_image(self, face: Face) -> None:
        """
        Display the normalized eye images side by side.

        Args:
            face: Face object

        Returns:
            None
        """
        if not self.config.demo.display_on_screen:
            return

        if not self.show_normalized_image:
            return

        reye = face.reye.normalized_image
        leye = face.leye.normalized_image
        normalized = np.hstack([reye, leye])

        if self.config.demo.use_camera:
            normalized = transforms.flip_image(normalized)

        cv2.imshow("normalized", normalized)

    def _draw_gaze_vector(self, face: Face) -> None:
        """
        Draws the gaze vector of the user as a line in 3D space.

        Args:
            face: Face object

        Returns:
            None
        """
        if not self.show_gaze_vector:
            return

        length = self.config.demo.gaze_visualization_length

        for key in [FacePartsName.REYE, FacePartsName.LEYE]:
            eye = getattr(face, key.name.lower())
            # eye.gaze_vector.z is always -1. We scale by length
            end_point = eye.center + length * eye.gaze_vector
            self.camera_visualiser.draw_3d_line(eye.center, end_point)

            pitch, yaw = np.rad2deg(eye.vector_to_angle(eye.gaze_vector))
            logger.debug("[%s] pitch: %d, yaw: %d",
                         key.name.lower(), pitch, yaw)

        self.average_eye_distance = (
            face.reye.distance + face.leye.distance) / 2
        self.average_eye_center = (face.reye.center + face.leye.center) / 2
        self.average_gaze_vector = (
            face.reye.gaze_vector + face.leye.gaze_vector) / 2

        end_point = self.average_eye_center + length * self.average_gaze_vector
        self.camera_visualiser.draw_3d_line(self.average_eye_center, end_point)

    def _draw_gaze_point(self) -> None:
        """
        Projects the gaze vector onto the screen and draws a point at
        the estimated location the user is looking at.

        Returns:
            None
        """
        if not self.show_gaze_vector:
            return

        # Draw the point on the screen the user is looking at
        point_on_screen = (
            self.average_eye_center
            + (self.average_eye_distance *
               self.config.gaze_point.z_projection_multiplier) * self.average_gaze_vector
        )
        point_on_screen[1] *= self.config.gaze_point.gaze_vector_y_scale

        # Update buffer and calculate smoothed point
        self.point_buffer.append(point_on_screen)
        if len(self.point_buffer) > self.config.gaze_point.smoothing_frames:
            self.point_buffer.pop(0)

        smoothed_3d_point = np.mean(self.point_buffer, axis=0)
        self.gaze_2d_point = self.gaze_visualiser.draw_3d_point(
            smoothed_3d_point, color=(0, 0, 255), size=self.config.gaze_point.dot_size, clamp_to_screen=True
        )

    def _draw_gaze_region(self) -> None:
        """
        Highlights the region on the screen the user is looking at.

        Returns:
            None
        """
        if not self.show_gaze_vector:
            return

        base_bg_alpha = 0.05
        bg_alpha_boost_hitbox = 0.2
        bg_color = (0, 0, 255)

        # Determine if user is looking in one of the hit-boxes
        logger.info("Gaze 2d Point: %s", str(self.gaze_2d_point))

        # Set only when looking at a hitbox
        gaze_side = None

        for side in cc.SIDES:
            looking_hitbox = None
            side_hitbox = self.hitboxes[side]
            if side_hitbox[c.TOP_LEFT][0] <= self.gaze_2d_point[0] <= side_hitbox[c.BOTTOM_RIGHT][0]:
                looking_hitbox = side
                gaze_side = side

            text = f"Looking {looking_hitbox}" if looking_hitbox else ""
            border = None
            if looking_hitbox:
                bg_alpha = base_bg_alpha + bg_alpha_boost_hitbox
                border = (255, 0, 0)
            else:
                bg_alpha = base_bg_alpha

            top_left = side_hitbox[c.TOP_LEFT]
            bottom_right = side_hitbox[c.BOTTOM_RIGHT]
            gaze_overlay = self.gaze_visualiser.draw_labelled_rectangle(
                top_left, bottom_right, bg_color, bg_alpha, text, border_color=border, blend=not self.running_in_thread
            )
            self.gaze_visualiser.set_image(gaze_overlay)

        if self.running_in_thread:
            logger.info("Setting gaze side to %s in shared data.", gaze_side)
            with self.data_lock:
                self.thread_data[cc.EYE_TRACKING][cc.GAZE_SIDE] = gaze_side
                self.thread_data[cc.EYE_TRACKING][cc.GAZE_OVERLAY] = self.gaze_visualiser.image

            logger.debug("Shared data updated.")
