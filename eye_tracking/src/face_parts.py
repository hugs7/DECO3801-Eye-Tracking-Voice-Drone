import enum
from typing import Optional

import numpy as np
from scipy.spatial.transform import Rotation


class FacePartsName(enum.Enum):
    FACE = enum.auto()
    REYE = enum.auto()
    LEYE = enum.auto()


class FaceParts:
    def __init__(self, name: FacePartsName):
        self.name = name
        self.center: Optional[np.ndarray] = None
        self.head_pose_rot: Optional[Rotation] = None
        self.normalizing_rot: Optional[Rotation] = None
        self.normalized_head_rot2d: Optional[np.ndarray] = None
        self.normalized_image: Optional[np.ndarray] = None

        self.normalized_gaze_angles: Optional[np.ndarray] = None
        self.normalized_gaze_vector: Optional[np.ndarray] = None
        self.gaze_vector: Optional[np.ndarray] = None

    @property
    def distance(self) -> float:
        """
        Computes distance from the camera to the face part
        :return: Distance in meters
        """
        return np.linalg.norm(self.center)

    def angle_to_vector(self) -> None:
        """
        Converts normalized gaze angles to a gaze vector
        """

        pitch, yaw = self.normalized_gaze_angles
        self.normalized_gaze_vector = -np.array([np.cos(pitch) * np.sin(yaw), np.sin(pitch), np.cos(pitch) * np.cos(yaw)])

    def denormalize_gaze_vector(self) -> None:
        """
        Denormalizes the gaze vector
        """

        normalizing_rot = self.normalizing_rot.as_matrix()
        # Here gaze vector is a row vector, and rotation matrices are
        # orthogonal, so multiplying the rotation matrix from the right is
        # the same as multiplying the inverse of the rotation matrix to the
        # column gaze vector from the left.
        self.gaze_vector = self.normalized_gaze_vector @ normalizing_rot

    @staticmethod
    def vector_to_angle(vector: np.ndarray) -> np.ndarray:
        """
        Converts a gaze vector to pitch and yaw angles
        :param vector: Gaze vector
        :return: Pitch and yaw angles
        """

        assert vector.shape == (3,)
        x, y, z = vector
        pitch = np.arcsin(-y)
        yaw = np.arctan2(-x, -z)
        return np.array([pitch, yaw])
