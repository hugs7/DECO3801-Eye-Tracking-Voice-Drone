"""
Module to draw on the screen
"""

from typing import List, Dict, Tuple
import cv2
import cv2.typing as cv_t
import numpy as np

import landmarks
from colours import ColourMap as CM
import coordinate
import constants
from custom_types.NormalisedLandmark import NormalisedLandmark
import calibrate


def draw_landmarks(
    frame: np.ndarray,
    face_landmarks: List[NormalisedLandmark],
    landmark_mapping: landmarks.Landmarks,
    frame_dim: coordinate.Coordinate2D,
    landmark_visibility: Dict[str, bool],
) -> None:
    """
    Draws the landmarks on the frame
    :param frame: The frame to draw the landmarks on
    :param face_landmarks: The landmarks processed by the face mesh
    :param landmark_mapping: The mapping of landmarks
    :param frame_dim: The dimensions of the frame
    :param landmark_visibility: The visibility of the landmarks in sections of the face
    :return: None
    """

    dot_radius = 7
    font_scale = 0.8
    thickness = 1

    for id, landmark in enumerate(face_landmarks):
        point_class = landmark_mapping.classify_point(id)

        # Check if visibility is on for this landmark
        visibility = landmark_visibility.get(point_class.name)
        if visibility is None:
            raise ValueError(f"Visibility not found for point {id}")
        if not visibility:
            continue

        landmark_coord = landmarks.normalise_landmark(landmark, frame_dim)
        if point_class is None:
            raise ValueError(f"Point class not found for point {id}")

        centre = landmark_coord.to_point()
        colour = point_class.colour.get_colour_bgr()
        cv2.circle(frame, centre, dot_radius, colour, cv2.FILLED)
        cv2.putText(frame, str(id), centre, cv2.FONT_HERSHEY_SIMPLEX, font_scale, colour, thickness, cv2.LINE_AA)


def draw_buttons(frame: np.ndarray, frame_dim: coordinate.Coordinate2D, landmark_visibility: Dict[str, bool]) -> None:
    font_scale = 1
    button_positions = calculate_button_positions(frame_dim, landmark_visibility)
    for part, (top_left, bottom_right) in button_positions.items():
        color = (0, 255, 0) if landmark_visibility[part] else (0, 0, 255)
        cv2.rectangle(frame, top_left, bottom_right, color, -1)
        cv2.putText(frame, part, (top_left[0] + 10, top_left[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, font_scale, CM.black.get_colour_bgr(), 2)


def calculate_button_positions(
    frame_dim: coordinate.Coordinate2D, landmark_visibility: Dict[str, int]
) -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
    positions = {}
    num_buttons_per_row = frame_dim.x // (constants.BUTTON_WIDTH + constants.BUTTON_PADDING_X)
    total_rows = (len(landmark_visibility) + num_buttons_per_row - 1) // num_buttons_per_row  # Total rows needed

    for i, part in enumerate(landmark_visibility.keys()):
        col = i % num_buttons_per_row
        row = i // num_buttons_per_row

        top_left = (
            col * (constants.BUTTON_WIDTH + constants.BUTTON_PADDING_X),
            frame_dim.y - ((total_rows - row) * (constants.BUTTON_HEIGHT + constants.BUTTON_PADDING_Y)),
        )
        bottom_right = (top_left[0] + constants.BUTTON_WIDTH, top_left[1] + constants.BUTTON_HEIGHT)

        positions[part] = (top_left, bottom_right)
    return positions


def render_text(upscaled_frame: cv2.VideoCapture, text: str) -> None:
    """
    Renders text on screen in the top left corner
    :param upscaled_frame: The frame to render the text on
    :param text: The text to render
    :return: None
    """

    cv2.putText(
        upscaled_frame,
        text,
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        CM.white.get_colour_bgr(),
        2,
        cv2.LINE_AA,
    )


def render_calibration_grid(
    frame: cv2.VideoCapture, frame_dim: coordinate.Coordinate2D, calibration_step: calibrate.CalibrationStep
) -> None:
    """
    Renders the calibration grid on the screen
    :param frame_dim: The dimensions of the frame
    :return: None
    """

    # Give 10% padding from the edge of the screen on both axes
    padding_percentage = 0.1
    padding_from_edge_x = int(padding_percentage * frame_dim.x)
    padding_from_edge_y = int(padding_percentage * frame_dim.y)

    # Define dot positions programmatically
    CalibrationStep = calibrate.CalibrationStep
    positions = {
        CalibrationStep.CENTER: (frame_dim.x // 2, frame_dim.y // 2),
        CalibrationStep.TOP_LEFT: (padding_from_edge_x, padding_from_edge_y),
        CalibrationStep.TOP_RIGHT: (frame_dim.x - padding_from_edge_x, padding_from_edge_y),
        CalibrationStep.BOTTOM_LEFT: (padding_from_edge_x, frame_dim.y - padding_from_edge_y),
        CalibrationStep.BOTTOM_RIGHT: (
            frame_dim.x - padding_from_edge_x,
            frame_dim.y - padding_from_edge_y,
        ),
        CalibrationStep.MIDDLE_TOP: (frame_dim.x // 2, padding_from_edge_y),
        CalibrationStep.MIDDLE_BOTTOM: (frame_dim.x // 2, frame_dim.y - padding_from_edge_y),
        CalibrationStep.MIDDLE_LEFT: (padding_from_edge_x, frame_dim.y // 2),
        CalibrationStep.MIDDLE_RIGHT: (frame_dim.x - padding_from_edge_x, frame_dim.y // 2),
    }

    # Draw dots on the frame
    for pos_name, coord in positions.items():
        if pos_name == calibration_step:
            colour = CM.green
        else:
            colour = CM.grey

        cv2.circle(frame, coord, constants.CALIBRATION_GRID_DOT_RADIUS, colour.get_colour_bgr(), -1, cv2.FILLED)
