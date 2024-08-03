#!/usr/bin/env python

import cv2
import numpy as np
from typing import List, Tuple

import landmarks
from custom_types.NormalisedLandmark import NormalisedLandmark
import coordinate
from colours import ColourMap as CM


def get_image_coord_of_landmark(face_landmarks: List[NormalisedLandmark], landmark_id: int, frame_dim: np.ndarray) -> Tuple[int, int]:
    """
    Get the image coordinates of a landmark
    :param face_landmarks: The face landmarks
    :param landmark_id: The landmark id
    :param frame_dim: The dimensions of the frame
    :return Tuple[int, int]: The image coordinates
    """

    lmk_pick = face_landmarks[landmark_id]
    normalised_landmark = landmarks.normalise_landmark(lmk_pick, frame_dim)

    return normalised_landmark.to_tuple()


def estimate_pose(frame: np.ndarray, face_landmarks: List[NormalisedLandmark], landmark_mapping: landmarks.Landmarks):
    # Read Image
    frame_x, frame_y, _ = frame.shape
    frame_size = coordinate.Coordinate(frame_x, frame_y)

    reference_points = {
        "nose_top": 1,
        "chin": 152,
        "left_eye_corner": 226,
        "right_eye_corner": 359,
        "left_mouth_corner": 146,
        "right_mouth_corner": 307,
    }

    # Get the image coordinates of the landmarks
    image_points = []
    model_points = []
    z_vals = [0.0, -65.0, -135.0, -135.0, -125.0, -125.0]
    for i, point in enumerate(reference_points.values()):
        coord = get_image_coord_of_landmark(face_landmarks, point, frame_size)
        image_points.append(coord)
        z = z_vals[i]
        model_points.append((coord[0], coord[1], z))

    # Convert to numpy array
    image_points = np.array(image_points, dtype="double")
    model_points = np.array(model_points, dtype="double")

    # Camera internals
    focal_length = 50
    center = (frame_size.y / 2, frame_size.x / 2)
    camera_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype="double")

    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )

    # Project a 3D point (0, 0, 1000.0) onto the image plane.
    # We use this to draw a line sticking out of the nose

    (nose_end_point2D, jacobian) = cv2.projectPoints(
        np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs
    )

    for p in image_points:
        cv2.circle(frame, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

    p1 = (int(image_points[0][0]), int(image_points[0][1]))
    p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

    cv2.line(frame, p1, p2, CM.blue.get_colour(), 2)
