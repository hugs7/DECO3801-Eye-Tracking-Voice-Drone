"""
Module to draw on the screen
"""

import cv2

import landmarks
from colours import ColourMap as CM
import coordinate


def draw_landmarks(frame, face_landmarks: landmarks.Landmarks, frame_dim: coordinate.Coordinate) -> None:
    """
    Draws the landmarks on the frame
    :param frame: The frame to draw the landmarks on
    :param landmark_mapping: The mapping of landmarks
    :param frame_w: The width of the frame
    :param frame_h: The height of the frame
    :return: None
    """

    for id, landmark in enumerate(face_landmarks):
        landmark_coord = landmarks.normalise_landmark(landmark, frame_dim)

        point_class_label = face_landmarks.classify_point(id)
        point_class = face_landmarks.landmark_mapping.get(point_class_label, None)
        if point_class_label is None:
            raise ValueError(f"Point class not found for point {id}")

        colour = point_class["colour"]

        cv2.circle(frame, landmark_coord, 3, colour)
        cv2.putText(frame, str(id), landmark_coord, cv2.FONT_HERSHEY_SIMPLEX, 0.3, CM.white, 1, cv2.LINE_AA)
