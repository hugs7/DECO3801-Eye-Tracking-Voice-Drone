#!/usr/bin/env python

import cv2
import numpy as np
from typing import List, Tuple

import landmarks
from custom_types.NormalisedLandmark import NormalisedLandmark
import coordinate
from colours import ColourMap as CM, Colour


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


def project_gaze_point(rotation_vector, translation_vector, camera_matrix, dist_coeffs, eye_landmark, frame, colour: Colour):
    """
    Project the gaze point and draw it on the frame.
    """
    # Project a 3D point (0, 0, 1000.0) onto the image plane.
    (gaze_point2D, _) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)

    # Draw gaze point
    p1 = (int(eye_landmark[0]), int(eye_landmark[1]))
    p2 = (int(gaze_point2D[0][0][0]), int(gaze_point2D[0][0][1]))

    cv2.line(frame, p1, p2, colour.get_colour(), 2)

    return p2


def estimate_pose(frame: np.ndarray, face_landmarks: List[NormalisedLandmark], landmark_mapping: landmarks.Landmarks):
    # Frame dimensions
    frame_h, frame_w, _ = frame.shape
    frame_size = coordinate.Coordinate(frame_w, frame_h)

    reference_points = {
        "nose_top": 1,
        "chin": 152,
        "left_eye_corner": 226,
        "right_eye_corner": 359,
        "left_mouth_corner": 146,
        "right_mouth_corner": 307,
    }

    image_points = []
    for point in reference_points.values():
        coord = get_image_coord_of_landmark(face_landmarks, point, frame_size)
        image_points.append(coord)

    image_points = np.array(image_points, dtype="double")

    # Define the 3D model points
    model_points = np.array(
        [
            (0.0, 0.0, 0.0),  # Nose tip
            (0.0, -330.0, -65.0),  # Chin
            (-225.0, 170.0, -135.0),  # Left eye corner
            (225.0, 170.0, -135.0),  # Right eye corner
            (-150.0, -150.0, -125.0),  # Left mouth corner
            (150.0, -150.0, -125.0),  # Right mouth corner
        ]
    )

    # Camera internals
    focal_length = frame_w
    center = (frame_w / 2, frame_h / 2)
    camera_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype="double")

    # Assuming no lens distortion
    dist_coeffs = np.zeros((4, 1))

    # Solve PnP
    (success, rotation_vector, translation_vector) = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )

    # Project a 3D point (0, 0, 1000.0) onto the image plane.
    (nose_end_point2D, jacobian) = cv2.projectPoints(
        np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs
    )

    # Draw landmarks and pose line
    dot_size = 10
    for p in image_points:
        cv2.circle(frame, (int(p[0]), int(p[1])), dot_size, CM.red.get_colour(), -1)

    p1 = (int(image_points[0][0]), int(image_points[0][1]))
    p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

    cv2.line(frame, p1, p2, CM.blue.get_colour(), 2)
    cv2.circle(frame, p2, 10, CM.red.get_colour(), -1)

    # Calculate and draw gaze points for both eyes
    eye_landmark_mapping = landmark_mapping.eyes
    for eye, eye_landmarks in eye_landmark_mapping.items():
        eye_landmarks: landmarks.EyeLandmarks
        landmark_points = eye_landmarks.points
        for side, colour in [
            ("centre", CM.blue),
            ("right", CM.cornflower_blue),
            ("top", CM.cyan),
            ("left", CM.magenta),
            ("bottom", CM.yellow),
        ]:
            eye_landmark = get_image_coord_of_landmark(face_landmarks, landmark_points.get_side(side), frame_size)
            project_gaze_point(rotation_vector, translation_vector, camera_matrix, dist_coeffs, eye_landmark, frame, colour)

    return rotation_vector, translation_vector
