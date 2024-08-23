from typing import List

import mediapipe
import numpy as np
from omegaconf import DictConfig

from face import Face


class LandmarkEstimator:
    def __init__(self, config: DictConfig):
        self.mode = config.face_detector.mode
        self.detector = mediapipe.solutions.face_mesh.FaceMesh(
            max_num_faces=config.face_detector.mediapipe_max_num_faces,
            static_image_mode=config.face_detector.mediapipe_static_image_mode,
            refine_landmarks=True,  # Adds eye pupil landmarks (468-477)
        )

    def detect_faces(self, image: np.ndarray) -> List[Face]:
        """
        Calculated landmarks scaled to the image size with a bounding box
        :param image: RGB image
        :return: List of faces
        """

        h, w = image.shape[:2]
        faces_landmarks = self._detect_faces_raw(image)
        detected = []
        if faces_landmarks:
            for face in faces_landmarks:
                pts = np.array([(pt[0] * w, pt[1] * h) for pt in face], dtype=np.float64)
                bbox = np.vstack([pts.min(axis=0), pts.max(axis=0)])
                bbox = np.round(bbox).astype(np.int32)
                detected.append(Face(bbox, pts))
        return detected

    def detect_faces_raw(self, image: np.ndarray) -> List[np.ndarray]:
        if self.mode == "mediapipe":
            return self._detect_faces_raw(image)
        else:
            raise ValueError

    def _detect_faces_raw(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Returns landmarks as they come from the mediapipe model (not scaled to the image size)
        :param image: RGB image
        :return: List of faces landmarks
        """
        predictions = self.detector.process(self._get_bgr_frame(image))
        faces_landmarks = []
        if predictions.multi_face_landmarks:
            for prediction in predictions.multi_face_landmarks:
                pts = np.array([(pt.x, pt.y, pt.z) for pt in prediction.landmark], dtype=np.float64)
                faces_landmarks.append(pts)

        return faces_landmarks

    def _get_bgr_frame(self, image: np.ndarray) -> np.ndarray:
        """
        Converts an RGB image to BGR to be used by OpenCV
        """
        return image[:, :, ::-1]
