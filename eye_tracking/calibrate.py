"""
Module to help with eye tracking calibration
"""

from typing import TypedDict

import landmarks
import coordinate

from custom_types.NormalisedLandmark import NormalisedLandmark


class ReferencePositions(TypedDict):
    top: tuple
    bottom: tuple
    left: tuple
    right: tuple


def calibrate_eye_positions(face_landmarks: NormalisedLandmark, frame_dim: coordinate.Coordinate) -> ReferencePositions:
    """
    Calibrate eye positions based on the landmarks
    :param face_landmarks: The landmarks to calibrate from the face mesh
    :param frame_dim: The dimensions of the frame
    :return ReferencePositions: The reference positions
    """

    reference_positions = ReferencePositions()

    for eye in ["left", "right"]:
        for pos in ["top", "bottom", "left", "right"]:

            landmark_coord = landmarks.normalise_landmark(face_landmarks[face_landmarks.eye_landmarks[eye][pos]], frame_dim)
            reference_positions[eye][pos] = landmark_coord

    return reference_positions
