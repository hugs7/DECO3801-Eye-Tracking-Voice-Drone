"""
Module to handle normalisation of the head pose.
"""

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

from ..camera import Camera
from ..face_parts import FaceParts, FacePartsName


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalizes a vector to have unit length.

    Args:
        vector (np.ndarray): The vector to normalize.

    Returns:
        np.ndarray: The normalized vector.
    """
    return vector / np.linalg.norm(vector)


class HeadPoseNormalizer:
    """
    Class to handle normalisation of the head pose so as to make the face
    appear frontal in the image.
    """

    def __init__(self, camera: Camera, normalized_camera: Camera, normalized_distance: float):
        """
        Initializes the HeadPoseNormalizer.

        Args:
            camera (Camera): The camera used to capture the image.
            normalized_camera (Camera): The camera used to normalize the image.
            normalized_distance (float): The distance to the normalized camera.
        """
        self.camera = camera
        self.normalized_camera = normalized_camera
        self.normalized_distance = normalized_distance

    def normalize(self, image: np.ndarray, eye_or_face: FaceParts) -> None:
        """
        Normalizes the image and head pose of the face parts.

        Args:
            image (np.ndarray): The image to normalize.
            eye_or_face (FaceParts): The face parts to normalize.
        """
        eye_or_face.normalizing_rot = self._compute_normalizing_rotation(eye_or_face.center, eye_or_face.head_pose_rot)
        self._normalize_image(image, eye_or_face)
        self._normalize_head_pose(eye_or_face)

    def _normalize_image(self, image: np.ndarray, eye_or_face: FaceParts) -> None:
        """
        Normalizes the image of the face parts.

        Args:
            image (np.ndarray): The image to normalize.
            eye_or_face (FaceParts): The face parts to normalize.
        """
        camera_matrix_inv = np.linalg.inv(self.camera.camera_matrix)
        normalized_camera_matrix = self.normalized_camera.camera_matrix

        scale = self._get_scale_matrix(eye_or_face.distance)
        conversion_matrix = scale @ eye_or_face.normalizing_rot.as_matrix()

        projection_matrix = normalized_camera_matrix @ conversion_matrix @ camera_matrix_inv

        normalized_image = cv2.warpPerspective(image, projection_matrix, (self.normalized_camera.width, self.normalized_camera.height))

        if eye_or_face.name in {FacePartsName.REYE, FacePartsName.LEYE}:
            normalized_image = cv2.cvtColor(normalized_image, cv2.COLOR_BGR2GRAY)
            normalized_image = cv2.equalizeHist(normalized_image)
        eye_or_face.normalized_image = normalized_image

    @staticmethod
    def _normalize_head_pose(eye_or_face: FaceParts) -> None:
        """
        Normalizes the head pose of the face parts.

        Args:
            eye_or_face (FaceParts): The face parts to normalize.
        """

        normalized_head_rot = eye_or_face.head_pose_rot * eye_or_face.normalizing_rot
        euler_angles2d = normalized_head_rot.as_euler("XYZ")[:2]
        eye_or_face.normalized_head_rot2d = euler_angles2d * np.array([1, -1])

    @staticmethod
    def _compute_normalizing_rotation(center: np.ndarray, head_rot: Rotation) -> Rotation:
        """
        Computes the normalizing rotation for the head pose.

        Args:
            center (np.ndarray): The center of the face parts.
            head_rot (Rotation): The head rotation to normalize.

        Returns:
            Rotation: The normalizing rotation.
        """
        # See section 4.2 and Figure 9 of https://arxiv.org/abs/1711.09017
        z_axis = _normalize_vector(center.ravel())
        head_rot = head_rot.as_matrix()
        head_x_axis = head_rot[:, 0]
        y_axis = _normalize_vector(np.cross(z_axis, head_x_axis))
        x_axis = _normalize_vector(np.cross(y_axis, z_axis))
        return Rotation.from_matrix(np.vstack([x_axis, y_axis, z_axis]))

    def _get_scale_matrix(self, distance: float) -> np.ndarray:
        """
        Returns the scale matrix to normalize the distance.

        Args:
            distance (float): The distance to normalize.

        Returns:
            np.ndarray: The scale matrix.
        """
        return np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, self.normalized_distance / distance],
            ],
            dtype=np.float32,
        )
