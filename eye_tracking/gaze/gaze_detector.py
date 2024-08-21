"""
Main class for the gaze detector.
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

import datetime
import logging
import pathlib
from typing import Optional, Tuple

import cv2
import numpy as np
from omegaconf import DictConfig

from .common import Face, FacePartsName, Visualizer
from .gaze_estimator import GazeEstimator
from gaze import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GazeDetector:
    QUIT_KEYS = {27, ord("q")}

    def __init__(self, config: DictConfig):
        self.config = config
        self.gaze_estimator = GazeEstimator(config)
        face_model_3d = utils.get_3d_face_model(config)
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

        # Calibration
        self.calibrated = False
        self.calibrating = False
        self.calibration_landmarks = None

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

            ok, frame = self._read_camera()
            if not ok:
                break

            self._process_image(frame)

            if self.config.demo.display_on_screen:
                cv2.imshow("frame", self.visualizer.image)
        self.cap.release()
        if self.writer:
            self.writer.release()

    def _read_camera(self) -> Tuple[bool, np.ndarray]:
        ok, frame = self.cap.read()
        if not ok:
            return ok, frame

        # Upscale feed
        upscaled_frame = utils.upscale(frame, self.config.demo.upscale_dim)
        return ok, upscaled_frame

    def _process_image(self, image) -> None:
        undistorted = self._undistort_image(image)

        self.visualizer.set_image(image.copy())
        if self.calibrated:
            faces = self.gaze_estimator.detect_faces(undistorted)
            for face in faces:
                self.gaze_estimator.estimate_gaze(undistorted, face)
                self._draw_face_bbox(face)
                self._draw_head_pose(face)
                self._draw_landmarks(face)
                self._draw_face_template_model(face)
                self._draw_gaze_vector(face)
                self._display_normalized_image(face)

        # if self.calibrating:
        #     if self.calibration_landmarks is not None:
        #         self.visualizer.draw_3d_points(self.calibration_landmarks, color=(255, 0, 0), size=1)

        if self.config.demo.use_camera:
            self.visualizer.image = self.visualizer.image[:, ::-1]
        if self.writer:
            self.writer.write(self.visualizer.image)

    def _undistort_image(self, image: np.ndarray) -> np.ndarray:
        return cv2.undistort(image, self.gaze_estimator.camera.camera_matrix, self.gaze_estimator.camera.dist_coefficients)

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
        elif key == ord("c"):
            if self.calibrating:
                # Disable calibration
                self.calibrating = False
                logger.info("Setting calibrated to True")
                self.calibrated = True
                self.calibration_landmarks = None
            else:
                # Calibrate
                logger.info("Setting calibrated to False")
                self.calibrated = False
                self._calibrate_landmarks()
        else:
            return False
        return True

    def _calibrate_landmarks(
        self,
    ):
        self.calibrating = True
        # Read camera
        ok, frame = self._read_camera()
        if not ok:
            logger.error("Failed to read camera. Calibration failed.")
            self.calibrating = False
            return

        undistorted = self._undistort_image(frame)
        faces = self.gaze_estimator.detect_faces_raw(undistorted)
        if len(faces) != 1:
            logger.info("Ensure only one face is visible in the camera feed then press 'c' to calibrate again.")
            self.calibrating = False
            return

        face_landmarks = faces[0]
        self.calibration_landmarks = face_landmarks
        # Add 1 meter to the z-axis
        self.calibration_landmarks[:, 2] += 1

        self.gaze_estimator._face_model3d.set_landmark_calibration(self.calibration_landmarks)
        logger.info("Calibration successful.")

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
        """
        Landmarks are 2D points in the upscaled image (pixels).
        """
        if not self.show_landmarks:
            return
        self.visualizer.draw_points(face.landmarks, color=(0, 255, 255), size=1)

    def _draw_face_template_model(self, face: Face) -> None:
        """
        Face Template Model is the 3D model of the face in world coordinates (metres)
        """
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
            normalized = utils.flip_image(normalized)
        cv2.imshow("normalized", normalized)

    def _draw_gaze_vector(self, face: Face) -> None:
        length = self.config.demo.gaze_visualization_length

        if self.config.mode == "MPIIGaze":
            for key in [FacePartsName.REYE, FacePartsName.LEYE]:
                eye = getattr(face, key.name.lower())
                end_point = eye.center + length * eye.gaze_vector  # eye.gaze_vector.z is always -1. We scale by length
                self.visualizer.draw_3d_line(eye.center, end_point)

                point_on_screen = eye.center + (eye.distance - 0.2) * eye.gaze_vector  # Will adjust the distance offset
                self.visualizer.draw_3d_points(np.array([point_on_screen]), color=(0, 255, 0), size=5)
                pitch, yaw = np.rad2deg(eye.vector_to_angle(eye.gaze_vector))
                logger.info(f"[{key.name.lower()}] pitch: {pitch:.2f}, yaw: {yaw:.2f}")
        elif self.config.mode in ["MPIIFaceGaze", "ETH-XGaze"]:
            self.visualizer.draw_3d_line(face.center, face.center + length * face.gaze_vector)
            pitch, yaw = np.rad2deg(face.vector_to_angle(face.gaze_vector))
            logger.info(f"[face] pitch: {pitch:.2f}, yaw: {yaw:.2f}")
        else:
            raise ValueError
