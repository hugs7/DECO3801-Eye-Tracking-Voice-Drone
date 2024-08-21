from typing import List

import face_alignment
import face_alignment.detection.sfd
import mediapipe
import numpy as np
from omegaconf import DictConfig

from gaze.common import Face


class LandmarkEstimator:
    def __init__(self, config: DictConfig):
        self.mode = config.face_detector.mode
        if self.mode == "dlib":
            raise NotImplementedError("Dlib is not supported for landmark estimation")
        elif self.mode == "face_alignment_dlib":
            raise NotImplementedError("Dlib is not supported for landmark estimation")
        elif self.mode == "face_alignment_sfd":
            self.detector = face_alignment.detection.sfd.sfd_detector.SFDDetector(device=config.device)
            self.predictor = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device=config.device)
        elif self.mode == "mediapipe":
            self.detector = mediapipe.solutions.face_mesh.FaceMesh(
                max_num_faces=config.face_detector.mediapipe_max_num_faces,
                static_image_mode=config.face_detector.mediapipe_static_image_mode,
            )
        else:
            raise ValueError

    def detect_faces(self, image: np.ndarray) -> List[Face]:
        if self.mode == "dlib":
            return self._detect_faces_dlib(image)
        elif self.mode == "face_alignment_dlib":
            return self._detect_faces_face_alignment_dlib(image)
        elif self.mode == "face_alignment_sfd":
            return self._detect_faces_face_alignment_sfd(image)
        elif self.mode == "mediapipe":
            return self._detect_faces_mediapipe(image)
        else:
            raise ValueError

    def _detect_faces_dlib(self, image: np.ndarray) -> List[Face]:
        bboxes = self.detector(self._get_bgr_frame(image), 0)
        detected = []
        for bbox in bboxes:
            predictions = self.predictor(self._get_bgr_frame(image), bbox)
            landmarks = np.array([(pt.x, pt.y) for pt in predictions.parts()], dtype=np.float32)
            bbox = np.array([[bbox.left(), bbox.top()], [bbox.right(), bbox.bottom()]], dtype=np.float32)
            detected.append(Face(bbox, landmarks))
        return detected

    def _detect_faces_face_alignment_dlib(self, image: np.ndarray) -> List[Face]:
        bboxes = self.detector(self._get_bgr_frame(image), 0)
        bboxes = [[bbox.left(), bbox.top(), bbox.right(), bbox.bottom()] for bbox in bboxes]
        predictions = self.predictor.get_landmarks(self._get_bgr_frame(image), detected_faces=bboxes)
        if predictions is None:
            predictions = []
        detected = []
        for bbox, landmarks in zip(bboxes, predictions):
            bbox = np.array(bbox, dtype=np.float32).reshape(2, 2)
            detected.append(Face(bbox, landmarks))
        return detected

    def _detect_faces_face_alignment_sfd(self, image: np.ndarray) -> List[Face]:
        bboxes = self.detector.detect_from_image(self._get_bgr_frame(image).copy())
        bboxes = [bbox[:4] for bbox in bboxes]
        predictions = self.predictor.get_landmarks(self._get_bgr_frame(image), detected_faces=bboxes)
        if predictions is None:
            predictions = []
        detected = []
        for bbox, landmarks in zip(bboxes, predictions):
            bbox = np.array(bbox, dtype=np.float32).reshape(2, 2)
            detected.append(Face(bbox, landmarks))
        return detected

    def _detect_faces_mediapipe(self, image: np.ndarray) -> List[Face]:
        h, w = image.shape[:2]
        predictions = self.detector.process(self._get_bgr_frame(image))
        detected = []
        if predictions.multi_face_landmarks:
            for prediction in predictions.multi_face_landmarks:
                pts = np.array([(pt.x * w, pt.y * h) for pt in prediction.landmark], dtype=np.float64)
                bbox = np.vstack([pts.min(axis=0), pts.max(axis=0)])
                bbox = np.round(bbox).astype(np.int32)
                detected.append(Face(bbox, pts))
        return detected

    def _get_bgr_frame(self, image: np.ndarray) -> np.ndarray:
        """
        Converts an RGB image to BGR to be used by OpenCV
        """
        return image[:, :, ::-1]
