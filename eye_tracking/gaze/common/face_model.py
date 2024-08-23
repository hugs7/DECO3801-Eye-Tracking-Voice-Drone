import dataclasses

import cv2
import numpy as np
from scipy.spatial.transform import Rotation

from gaze.common.camera import Camera
from gaze.common.face import Face


class FaceModel:
    def __init__(
        self,
        reye_indices: np.ndarray,
        leye_indices: np.ndarray,
        mouth_indices: np.ndarray,
        nose_indices: np.ndarray,
        chin_index: int,
        nose_index: int,
    ):
        self.LANDMARKS = None
        self.REYE_INDICES = reye_indices
        self.LEYE_INDICES = leye_indices
        self.MOUTH_INDICES = mouth_indices
        self.NOSE_INDICES = nose_indices
        self.CHIN_INDEX = chin_index
        self.NOSE_INDEX = nose_index

    def check_landmarks(self, landmarks: np.ndarray) -> None:
        """
        Asserts that the landmarks array has the correct shape and that the
        nose landmark is at the origin.
        """

        assert landmarks is not None
        assert landmarks.shape == (478, 3)
        assert list(landmarks[self.NOSE_INDEX]) == [0, 0, 0]

    def set_landmark_calibration(self, landmarks: np.ndarray) -> None:
        """
        Updates the landmark calibration matrix which is used as the object
        points when solving the PnP problem.
        """
        # Normalise landmarks to have the nose at the origin
        normalised_landmarks = landmarks - landmarks[self.NOSE_INDEX]
        self.check_landmarks(normalised_landmarks)
        self.LANDMARKS = normalised_landmarks

    def estimate_head_pose(self, face: Face, camera: Camera) -> None:
        """Estimate the head pose by fitting 3D template model."""
        # If the number of the template points is small, cv2.solvePnP
        # becomes unstable, so set the default value for rvec and tvec
        # and set useExtrinsicGuess to True.
        # The default values of rvec and tvec below mean that the
        # initial estimate of the head pose is not rotated and the
        # face is in front of the camera.
        if self.LANDMARKS is None:
            raise ValueError("Landmark calibration matrix is not set.")

        self.check_landmarks(self.LANDMARKS)

        rvec = np.zeros(3, dtype=np.float32)
        tvec = np.array([0, 0, 1], dtype=np.float32)
        _, rvec, tvec = cv2.solvePnP(
            self.LANDMARKS,
            face.landmarks,  # This is in the 2D upscaled image 1280x900. Face is not normalised to have offset 0,0 at the nose.
            camera.camera_matrix,  # From sample params
            camera.dist_coefficients,  # No distortion coefficients
            rvec,
            tvec,
            useExtrinsicGuess=True,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        # Rvec is radians of each axis rotated relative to the camera
        # Tvec is the 3D position of the head in metres (in world coords) relative to the camera
        rot = Rotation.from_rotvec(rvec)  # Convert the rotation vector to a rotation matrix
        face.head_pose_rot = rot
        face.head_position = tvec  # 3D position of the head in world coordinates relative to the camera
        face.reye.head_pose_rot = rot
        face.leye.head_pose_rot = rot

    def compute_3d_pose(self, face: Face) -> None:
        """Compute the transformed model."""
        rot = face.head_pose_rot.as_matrix()  # Has units of radians
        face.model3d = self.LANDMARKS @ rot.T + face.head_position  # This is the 3D model of the face in world coordinates

    def compute_face_eye_centers(self, face: Face) -> None:
        """Compute the centers of the face and eyes.

        The face center is defined as the
        average coordinates of the six points at the corners of both
        eyes and the mouth.
        """
        face.center = face.model3d[np.concatenate([self.REYE_INDICES, self.LEYE_INDICES, self.MOUTH_INDICES])].mean(axis=0)

        # Face centre is world coordinates in 3D with units metres relative to the camera
        face.reye.center = face.model3d[self.REYE_INDICES].mean(axis=0)
        face.leye.center = face.model3d[self.LEYE_INDICES].mean(axis=0)
