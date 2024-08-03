"""
Module to draw on the screen
"""

from typing import List
import cv2
import cv2.typing as cv_t
from google.protobuf.internal.containers import RepeatedCompositeContainer
import numpy as np

import landmarks
import coordinate

from types.NormalisedLandmark import NormalisedLandmark


def draw_landmarks(
    frame: np.ndarray, face_landmarks: List[NormalisedLandmark], landmark_mapping: landmarks.Landmarks, frame_dim: coordinate.Coordinate
) -> None:
    """
    Draws the landmarks on the frame
    :param frame: The frame to draw the landmarks on
    :param face_landmarks: The landmarks processed by the face mesh
    :param landmark_mapping: The mapping of landmarks
    :param frame_dim: The dimensions of the frame
    :return: None
    """

    dot_radius = 3
    font_scale = 0.3
    thickness = 1

    for id, landmark in enumerate(face_landmarks):
        landmark_coord = landmarks.normalise_landmark(landmark, frame_dim)

        point_class = landmark_mapping.classify_point(id)
        if point_class is None:
            raise ValueError(f"Point class not found for point {id}")

        centre = landmark_coord.to_point()
        colour = point_class.colour.get_colour()
        cv2.circle(frame, centre, dot_radius, colour)
        cv2.putText(frame, str(id), centre, cv2.FONT_HERSHEY_SIMPLEX, font_scale, colour, thickness, cv2.LINE_AA)
