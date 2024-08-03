"""
Module to help with eye tracking calibration
"""

from typing import TypedDict

import landmarks


class ReferencePositions(TypedDict):
    top: tuple
    bottom: tuple
    left: tuple
    right: tuple


def calibrate_eye_positions(landmarks, frame_w, frame_h) -> ReferencePositions:
    """
    Calibrate eye positions based on the landmarks
    :param landmarks: The landmarks to calibrate
    :param frame_w: The width of the frame
    :param frame_h: The height of the frame
    :return ReferencePositions: The reference positions
    """

    reference_positions = ReferencePositions()

    for eye in ["left", "right"]:
        for pos in ["top", "bottom", "left", "right"]:
            x, y = landmarks.normalise_landmark(landmarks[landmarks.eye_landmarks[eye][pos]], frame_w, frame_h)
            reference_positions[eye][pos] = (x, y)

    return reference_positions
