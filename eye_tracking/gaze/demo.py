import datetime
import logging
import pathlib
from typing import Optional

import cv2
import numpy as np
from omegaconf import DictConfig

from .common import Face, FacePartsName, Visualizer
from .gaze_estimator import GazeEstimator
from .utils import get_3d_face_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom imports
import camera


class Demo:
    QUIT_KEYS = {27, ord("q")}

    def __init__(self, config: DictConfig):
        self.config = config
        self.gaze_estimator = GazeEstimator(config)
        face_model_3d = get_3d_face_model(config)
        self.visualizer = Visualizer(self.gaze_estimator.camera, face_model_3d.NOSE_INDEX)

        self.cap = self._create_capture()
        self.output_dir = self._create_output_dir()
        self.writer = self._create_video_writer()

        self.stop = False
        self.show_bbox = self.config.demo.show_bbox
        self.show_head_pose = self.config.demo.show_head_pose
        self.show_landmarks = self.config.demo.show_landmarks
        self.show_normalized_image = self.config.demo.show_normalized_image
        self.show_template_model = self.config.demo.show_template_model

    def run(self) -> None:
        if self.config.demo.use_camera or self.config.demo.video_path:
            self._run_on_video()
        elif self.config.demo.image_path:
            self._run_on_image()
        else:
            raise ValueError

    def _run_on_image(self):
        image = cv2.imread(self.config.demo.image_path)
        self._process_image(image)
        if self.config.demo.display_on_screen:
            while True:
                key_pressed = self._wait_key()
                if self.stop:
                    break
                if key_pressed:
                    self._process_image(image)
                cv2.imshow("image", self.visualizer.image)
        if self.config.demo.output_dir:
            name = pathlib.Path(self.config.demo.image_path).name
            output_path = pathlib.Path(self.config.demo.output_dir) / name
            cv2.imwrite(output_path.as_posix(), self.visualizer.image)

    def _run_on_video(self) -> None:
        while True:
            if self.config.demo.display_on_screen:
                self._wait_key()
                if self.stop:
                    break

            ok, frame = self.cap.read()
            if not ok:
                break

            # Upscale feed
            # upscaled_frame = camera.upscale(frame, self.config.demo.upscale_dim)
            self._process_image(frame)

            if self.config.demo.display_on_screen:
                cv2.imshow("frame", self.visualizer.image)
        self.cap.release()
        if self.writer:
            self.writer.release()

    def _process_image(self, image) -> None:
        undistorted = cv2.undistort(image, self.gaze_estimator.camera.camera_matrix, self.gaze_estimator.camera.dist_coefficients)

        self.visualizer.set_image(image.copy())
        faces = self.gaze_estimator.detect_faces(undistorted)
        for face in faces:
            self.gaze_estimator.estimate_gaze(undistorted, face)
            self._draw_face_bbox(face)
            self._draw_head_pose(face)
            self._draw_landmarks(face)
            self._draw_face_template_model(face)
            self._draw_gaze_vector(face)
            self._draw_gaze_dot_on_screen(face)
            self._display_normalized_image(face)

        if self.config.demo.use_camera:
            self.visualizer.image = self.visualizer.image[:, ::-1]
        if self.writer:
            self.writer.write(self.visualizer.image)

    def _create_capture(self) -> Optional[cv2.VideoCapture]:
        if self.config.demo.image_path:
            return None
        if self.config.demo.use_camera:
            cap = cv2.VideoCapture(0)
        elif self.config.demo.video_path:
            cap = cv2.VideoCapture(self.config.demo.video_path)
        else:
            raise ValueError
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.gaze_estimator.camera.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.gaze_estimator.camera.height)
        return cap

    def _create_output_dir(self) -> Optional[pathlib.Path]:
        if not self.config.demo.output_dir:
            return
        output_dir = pathlib.Path(self.config.demo.output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        return output_dir

    @staticmethod
    def _create_timestamp() -> str:
        dt = datetime.datetime.now()
        return dt.strftime("%Y%m%d_%H%M%S")

    def _create_video_writer(self) -> Optional[cv2.VideoWriter]:
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
        writer = cv2.VideoWriter(output_path.as_posix(), fourcc, 30, (self.gaze_estimator.camera.width, self.gaze_estimator.camera.height))
        if writer is None:
            raise RuntimeError
        return writer

    def _wait_key(self) -> bool:
        key = cv2.waitKey(self.config.demo.wait_time) & 0xFF
        if key in self.QUIT_KEYS:
            self.stop = True
        elif key == ord("b"):
            self.show_bbox = not self.show_bbox
        elif key == ord("l"):
            self.show_landmarks = not self.show_landmarks
        elif key == ord("h"):
            self.show_head_pose = not self.show_head_pose
        elif key == ord("n"):
            self.show_normalized_image = not self.show_normalized_image
        elif key == ord("t"):
            self.show_template_model = not self.show_template_model
        else:
            return False
        return True

    def _draw_face_bbox(self, face: Face) -> None:
        if not self.show_bbox:
            return
        self.visualizer.draw_bbox(face.bbox)

    def _draw_head_pose(self, face: Face) -> None:
        if not self.show_head_pose:
            return
        # Draw the axes of the model coordinate system
        length = self.config.demo.head_pose_axis_length
        self.visualizer.draw_model_axes(face, length, lw=2)

        euler_angles = face.head_pose_rot.as_euler("XYZ", degrees=True)
        pitch, yaw, roll = face.change_coordinate_system(euler_angles)
        logger.info(f"[head] pitch: {pitch:.2f}, yaw: {yaw:.2f}, " f"roll: {roll:.2f}, distance: {face.distance:.2f}")

    def _draw_landmarks(self, face: Face) -> None:
        if not self.show_landmarks:
            return
        self.visualizer.draw_points(face.landmarks, color=(0, 255, 255), size=1)

    def _draw_face_template_model(self, face: Face) -> None:
        if not self.show_template_model:
            return
        self.visualizer.draw_3d_points(face.model3d, color=(255, 0, 525), size=1)

    def _display_normalized_image(self, face: Face) -> None:
        if not self.config.demo.display_on_screen:
            return
        if not self.show_normalized_image:
            return
        if self.config.mode == "MPIIGaze":
            reye = face.reye.normalized_image
            leye = face.leye.normalized_image
            normalized = np.hstack([reye, leye])
        elif self.config.mode in ["MPIIFaceGaze", "ETH-XGaze"]:
            normalized = face.normalized_image
        else:
            raise ValueError
        if self.config.demo.use_camera:
            normalized = normalized[:, ::-1]
        cv2.imshow("normalized", normalized)

    def _draw_gaze_vector(self, face: Face) -> None:
        distance_from_screen = self._estimate_distance_from_screen(face)
        # length = self.config.demo.gaze_visualization_length
        length = distance_from_screen
        if self.config.mode == "MPIIGaze":
            for key in [FacePartsName.REYE, FacePartsName.LEYE]:
                eye = getattr(face, key.name.lower())
                self.visualizer.draw_3d_line(eye.center, eye.center + length * eye.gaze_vector)
                pitch, yaw = np.rad2deg(eye.vector_to_angle(eye.gaze_vector))
                logger.info(f"[{key.name.lower()}] pitch: {pitch:.2f}, yaw: {yaw:.2f}")
        elif self.config.mode in ["MPIIFaceGaze", "ETH-XGaze"]:
            self.visualizer.draw_3d_line(face.center, face.center + length * face.gaze_vector)
            pitch, yaw = np.rad2deg(face.vector_to_angle(face.gaze_vector))
            logger.info(f"[face] pitch: {pitch:.2f}, yaw: {yaw:.2f}")
        else:
            raise ValueError

    def _draw_gaze_dot_on_screen(self, face: Face) -> None:
        Z_screen = self._estimate_distance_from_screen(face)

        if self.config.mode == "MPIIGaze":
            for key in [FacePartsName.REYE, FacePartsName.LEYE]:
                eye = getattr(face, key.name.lower())

                # Calculate the pitch and yaw angles in radians
                pitch, yaw = np.arctan2(eye.gaze_vector[1], eye.gaze_vector[2]), np.arctan2(eye.gaze_vector[0], eye.gaze_vector[2])
                logger.info(f"[{key.name.lower()}] pitch: {np.rad2deg(pitch):.2f}, yaw: {np.rad2deg(yaw):.2f}")
                # Calculate the displacement on the screen (in pixels)
                dx = np.tan(yaw) * Z_screen
                dy = np.tan(pitch) * Z_screen

                # Assume the center of the screen corresponds to the center of the image
                screen_center_x = self.visualizer.image.shape[1] / 2
                screen_center_y = self.visualizer.image.shape[0] / 2

                # Determine the gaze point on the screen
                gaze_point_2d = (int(screen_center_x + dx), int(screen_center_y - dy))

                # Draw the gaze point on the image
                self.visualizer.draw_dot(gaze_point_2d, color=(0, 0, 255))
        elif self.config.mode in ["MPIIFaceGaze", "ETH-XGaze"]:
            gaze_point_3d = face.center + Z_screen * face.gaze_vector / face.gaze_vector[2]
            gaze_point_2d = self._project_to_screen(gaze_point_3d)
            self.visualizer.draw_dot(gaze_point_2d, color=(0, 0, 255))
        else:
            raise ValueError

    def _project_to_screen(self, point_3d) -> tuple:
        # Convert the 3D gaze point to 2D screen coordinates using the camera matrix
        point_2d = cv2.projectPoints(
            point_3d, np.eye(3), np.zeros(3), self.gaze_estimator.camera.camera_matrix, self.gaze_estimator.camera.dist_coefficients
        )[0]
        return tuple(int(coord) for coord in point_2d.ravel())

    def _estimate_distance_from_screen(self, face: Face) -> float:
        # Known physical distance between eyes (in meters), adjust this according to your model
        known_eye_distance = 0.063  # Average distance between eyes in meters

        # Get the 3D coordinates of the eye landmarks
        left_eye = face.landmarks[FacePartsName.LEYE.value]
        right_eye = face.landmarks[FacePartsName.REYE.value]

        # Calculate the pixel distance between the eyes in the image
        eye_distance_pixels = np.linalg.norm(left_eye - right_eye)

        # Focal length in pixels (from camera matrix)
        focal_length = self.gaze_estimator.camera.camera_matrix[0, 0]  # fx component

        # Estimate the distance from the camera to the face
        distance = (known_eye_distance * focal_length) / eye_distance_pixels
        logger.debug(
            f"Estimated distance from screen: pixels: {eye_distance_pixels:.2f}, foc_len: {focal_length:.2f}, phys: {distance:.2f} meters"
        )
        return distance
