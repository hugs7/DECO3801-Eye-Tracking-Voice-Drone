"""
Module to help with eye tracking calibration
"""

from typing import TypedDict
from enum import Enum
import cv2

import landmarks
import coordinate
from custom_types.NormalisedLandmark import NormalisedLandmark
from colours import ColourMap as CM


class CalibrationSteps(Enum):
    EYE_CENTRE = 1
    EYE_TOP = 2
    EYE_BOTTOM = 3
    EYE_LEFT = 4
    EYE_RIGHT = 5


class EyeReferencePosition:
    def __init__(
        self,
        top: NormalisedLandmark,
        bottom: NormalisedLandmark,
        left: NormalisedLandmark,
        right: NormalisedLandmark,
        centre: NormalisedLandmark,
    ):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.centre = centre


class CalibrationData:
    def __init__(self, landmark_mapping: landmarks.Landmarks, frame_dim: coordinate.Coordinate):
        self.landmark_mapping = landmark_mapping
        self.frame_dim = frame_dim

        self.step = CalibrationSteps.EYE_CENTRE


def calibrate_init(
    face_landmarks: NormalisedLandmark, landmark_mapping: landmarks.Landmarks, frame_dim: coordinate.Coordinate
) -> CalibrationData:
    """
    Calibrate eye positions based on the landmarks
    :param face_landmarks: The landmarks to calibrate from the face mesh
    :param landmark_mapping: The mapping of landmarks
    :param frame_dim: The dimensions of the frame
    :return ReferencePositions: The reference positions
    """

    reference_positions = CalibrationData(landmark_mapping, frame_dim)

    eye_landmark_mapping = landmark_mapping.eyes

    for eye in ["left", "right"]:
        for pos in ["top", "bottom", "left", "right", "centre"]:
            eye_landmarks: landmarks.EyeLandmarks = eye_landmark_mapping[eye]
            eye_points: landmarks.EyePoints = eye_landmarks.points
            pos_id = eye_points.get_side(pos)
            eye_coord = face_landmarks[pos_id]
            landmark_coord = landmarks.normalise_landmark(eye_coord, frame_dim)
            # reference_positions[eye][pos] = landmark_coord

    return reference_positions


def perform_calibration(calibration_data: CalibrationData, frame: cv2.VideoCapture):
    """
    Perform the calibration
    :param calibration_data: The calibration data
    :param frame: The frame to draw on
    :return: None
    """

    dot_radius = 30

    # Give 10% padding from the edge of the screen on both axes
    padding_percentage = 0.1
    frame_dim = calibration_data.frame_dim
    padding_from_edge_x = int(padding_percentage * frame_dim.x)
    padding_from_edge_y = int(padding_percentage * frame_dim.y)

    # Define dot positions programmatically
    positions = [
        (padding_from_edge_x, padding_from_edge_y),  # Top-left
        (calibration_data.frame_dim.x - padding_from_edge_x, padding_from_edge_y),  # Top-right
        (padding_from_edge_x, calibration_data.frame_dim.y - padding_from_edge_y),  # Bottom-left
        (calibration_data.frame_dim.x - padding_from_edge_x, calibration_data.frame_dim.y - padding_from_edge_y),  # Bottom-right
        (calibration_data.frame_dim.x // 2, calibration_data.frame_dim.y // 2),  # Center
        (calibration_data.frame_dim.x // 2, padding_from_edge_y),  # Middle-top
        (calibration_data.frame_dim.x // 2, calibration_data.frame_dim.y - padding_from_edge_y),  # Middle-bottom
        (padding_from_edge_x, calibration_data.frame_dim.y // 2),  # Middle-left
        (calibration_data.frame_dim.x - padding_from_edge_x, calibration_data.frame_dim.y // 2),  # Middle-right
    ]

    # Draw dots on the frame
    for pos in positions:
        cv2.circle(frame, pos, dot_radius, CM.red.get_colour(), -1, cv2.FILLED)
