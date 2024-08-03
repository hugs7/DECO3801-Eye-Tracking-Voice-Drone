"""
Module to track eye movement
"""

import cv2
import numpy as np

import calibrate
import landmarks
import coordinate


def track_eye_movement(
    frame: np.ndarray,
    face_landmarks: landmarks.Landmarks,
    frame_dim: coordinate.Coordinate2D,
    reference_positions,
) -> None:
    """
    Tracks eye movement based on the face landmarks and draws a dot for where the user is looking
    :param frame: The frame to draw on
    :param face_landmarks: The face landmarks
    :param frame_dim: The dimensions of the frame
    :param reference_positions: The reference positions as per calibration
    :return: None
    """

    sensitivity = 25
    for eye in ["left", "right"]:
        iris_x, iris_y = landmarks.normalise_landmark(face_landmarks[landmarks.eye_landmarks[eye]["top"]], frame_dim)
        ref_x, ref_y = reference_positions[eye]["top"]

        dx = iris_x - ref_x
        dy = iris_y - ref_y

        # Overlay a dot corresponding to the eye movement
        overlay_x = frame_dim.x // 2 + dx * sensitivity
        overlay_y = frame_dim.y // 2 + dy * sensitivity
        cv2.circle(frame, (overlay_x, overlay_y), 5, (255, 0, 0), cv2.FILLED)
