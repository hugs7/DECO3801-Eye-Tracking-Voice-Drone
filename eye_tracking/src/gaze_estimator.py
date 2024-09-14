"""
Class to run the gaze estimation model
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

import logging
from typing import List

import numpy as np
import torch
from omegaconf import DictConfig

from .camera import Camera
from .face import Face
from .face_parts import FacePartsName
from .face_model_mediapipe import FaceModelMediaPipe
from .utils import transforms

from .head_pose_estimation import HeadPoseNormalizer, LandmarkEstimator
from .models import create_model

logger = logging.getLogger(__name__)


class GazeEstimator:
    EYE_KEYS = [FacePartsName.REYE, FacePartsName.LEYE]

    def __init__(self, config: DictConfig):
        self._config = config

        self._face_model3d = FaceModelMediaPipe()

        self.camera = Camera(config.gaze_estimator.camera_params)
        self._normalized_camera = Camera(
            config.gaze_estimator.normalized_camera_params)

        self._landmark_estimator = LandmarkEstimator(config)
        self._head_pose_normalizer = HeadPoseNormalizer(
            self.camera, self._normalized_camera, self._config.gaze_estimator.normalized_camera_distance
        )
        self._gaze_estimation_model = self._load_model()
        self._transform = transforms.create_transform()

    def _load_model(self) -> torch.nn.Module:
        """
        Load the gaze estimation model from checkpoint

        Returns:
            Gaze estimation model
        """
        model = create_model(self._config)
        checkpoint = torch.load(
            self._config.gaze_estimator.checkpoint, map_location="cpu")
        model.load_state_dict(checkpoint["model"])
        model.to(torch.device(self._config.device))
        model.eval()
        return model

    def detect_faces(self, image: np.ndarray) -> List[Face]:
        """
        Detect faces in the image and return a list of Face objects

        Args:
            image: RGB image

        Returns:
            List of Face objects
        """
        return self._landmark_estimator.detect_faces(image)

    def detect_faces_raw(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect faces in the image and return a list of raw landmarks

        Args:
            image: RGB image

        Returns:
            List of raw landmarks
        """
        return self._landmark_estimator.detect_faces_raw(image)

    def estimate_gaze(self, image: np.ndarray, face: Face) -> None:
        """
        Estimate gaze for the given face

        Args:
            image: RGB image
            face: Face object
        """
        self._face_model3d.estimate_head_pose(face, self.camera)
        self._face_model3d.compute_3d_pose(face)
        self._face_model3d.compute_face_eye_centers(face)

        for key in self.EYE_KEYS:
            eye = getattr(face, key.name.lower())
            self._head_pose_normalizer.normalize(image, eye)

        self._run_mpiigaze_model(face)

    @torch.no_grad()
    def _run_mpiigaze_model(self, face: Face) -> None:
        """
        Run the MPIIGaze model to estimate gaze

        Args:
            face: Face object
        """

        images = []
        head_poses = []

        for key in self.EYE_KEYS:
            eye = getattr(face, key.name.lower())
            image = eye.normalized_image
            normalized_head_pose = eye.normalized_head_rot2d

            if key == FacePartsName.REYE:
                image = transforms.flip_image(image).copy()
                normalized_head_pose *= np.array([1, -1])

            image = self._transform(image)
            images.append(image)
            head_poses.append(normalized_head_pose)

        images = torch.stack(images)
        head_poses = np.array(head_poses).astype(np.float32)
        head_poses = torch.from_numpy(head_poses)

        device = torch.device(self._config.device)
        images = images.to(device)
        head_poses = head_poses.to(device)
        predictions = self._gaze_estimation_model(images, head_poses)
        predictions = predictions.cpu().numpy()

        for i, key in enumerate(self.EYE_KEYS):
            eye = getattr(face, key.name.lower())
            eye.normalized_gaze_angles = predictions[i]

            if key == FacePartsName.REYE:
                eye.normalized_gaze_angles *= np.array([1, -1])

            eye.angle_to_vector()
            eye.denormalize_gaze_vector()
