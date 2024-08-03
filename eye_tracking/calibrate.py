"""
Module to help with eye tracking calibration
"""

from typing import Optional
from enum import Enum
import cv2

import landmarks
import constants
import coordinate
from custom_types.NormalisedLandmark import NormalisedLandmark
from colours import ColourMap as CM


class CalibrationStep(Enum):
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    MIDDLE_TOP = "middle-top"
    MIDDLE_BOTTOM = "middle-bottom"
    MIDDLE_LEFT = "middle-left"
    MIDDLE_RIGHT = "middle-right"


calibration_order = [
    CalibrationStep.CENTER,
    CalibrationStep.TOP_LEFT,
    CalibrationStep.TOP_RIGHT,
    CalibrationStep.BOTTOM_LEFT,
    CalibrationStep.BOTTOM_RIGHT,
    CalibrationStep.MIDDLE_TOP,
    CalibrationStep.MIDDLE_BOTTOM,
    CalibrationStep.MIDDLE_LEFT,
    CalibrationStep.MIDDLE_RIGHT,
]


def get_next_calibration_step(step: CalibrationStep) -> Optional[CalibrationStep]:
    """
    Get the next calibration step
    :param step: The current step
    :return: The next step
    """
    current_index = calibration_order.index(step)
    next_index = current_index + 1
    if next_index >= len(calibration_order):
        return None

    return calibration_order[next_index]


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

        # Boolean for if user is looking straight ahead. User will need to
        # keep their head straight during calibration
        self.looking_straight: bool = True

        self.step = calibration_order[0]


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
            eye_landmarks: landmarks.EyeLandmarks = landmark_mapping.get_part_by_name(eye)
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
    positions = {
        CalibrationStep.CENTER: (calibration_data.frame_dim.x // 2, calibration_data.frame_dim.y // 2),
        CalibrationStep.TOP_LEFT: (padding_from_edge_x, padding_from_edge_y),
        CalibrationStep.TOP_RIGHT: (calibration_data.frame_dim.x - padding_from_edge_x, padding_from_edge_y),
        CalibrationStep.BOTTOM_LEFT: (padding_from_edge_x, calibration_data.frame_dim.y - padding_from_edge_y),
        CalibrationStep.BOTTOM_RIGHT: (
            calibration_data.frame_dim.x - padding_from_edge_x,
            calibration_data.frame_dim.y - padding_from_edge_y,
        ),
        CalibrationStep.MIDDLE_TOP: (calibration_data.frame_dim.x // 2, padding_from_edge_y),
        CalibrationStep.MIDDLE_BOTTOM: (calibration_data.frame_dim.x // 2, calibration_data.frame_dim.y - padding_from_edge_y),
        CalibrationStep.MIDDLE_LEFT: (padding_from_edge_x, calibration_data.frame_dim.y // 2),
        CalibrationStep.MIDDLE_RIGHT: (calibration_data.frame_dim.x - padding_from_edge_x, calibration_data.frame_dim.y // 2),
    }

    # Draw dots on the frame
    for pos_name, coord in positions.items():
        if pos_name == calibration_data.step:
            colour = CM.green
        else:
            colour = CM.grey

        cv2.circle(frame, coord, dot_radius, colour.get_colour_bgr(), -1, cv2.FILLED)

    key = cv2.waitKey(1) & 0xFF
    if key != 255:
        print(f"Key: {key}")

    if key == ord(constants.BACKSPACE_KEY):
        # Continue with calibration
        next_step = get_next_calibration_step(calibration_data.step)
        if next_step is None:
            print("Calibration complete")
        else:
            # Capture data from the current step
            # We need to capture (for each eye) the top, bottom, left, right, and centre points
            # as well as the coordinates of the positions around the eye
            for eye in ["left", "right"]:
                eye_reference
                eye_landmarks = calibration_data.landmark_mapping.get_part_by_name(eye)
                eye_points = eye_landmarks.points
                for pos in ["top", "bottom", "left", "right", "centre"]:
                    pos_id = eye_points.get_side(pos)
                    eye_coord = face_landmarks[pos_id]
                    landmark_coord = landmarks.normalise_landmark(eye_coord, frame_dim)
                    # reference_positions[eye][pos] = landmark_coord

            calibration_data.step = next_step
            print(f"Moving to next calibration step: {calibration_data.step}")

    elif key == ord("q") or key == ord(constants.ESCAPE_KEY):
        print("Calibration cancelled")
        calibration_data.step = CalibrationStep.CENTER
        calibration_data.looking_straight = True
