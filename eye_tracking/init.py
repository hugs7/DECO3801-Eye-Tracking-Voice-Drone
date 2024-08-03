"""
Initialises the eye_tracking package.
"""

import os
from typing import Dict
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import coordinate
import landmarks
import utils.file_helper as file_helper
import controller


def landmark_mapping_init() -> landmarks.Landmarks:
    """
    Initialises the mapping for landmarks on the face
    """

    LANDMARK_MAPPING_PATH = file_helper.resolve_path(os.path.join(constants.MAPPINGS_FOLDER, "landmark_mapping.json"))

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)
    lmks = landmarks.Landmarks(landmark_mapping)

    return lmks


def window_init(window_width: int, window_height: int, landmark_visibility: Dict[str, bool], upscaled_dim: coordinate.Coordinate) -> None:
    """
    Initialises the window for the eye tracking application
    :param window_width: The width of the window
    :param window_height: The height of the window
    """

    # Set the desired window size
    cv2.namedWindow(constants.EYE_TRACKING_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(constants.EYE_TRACKING_WINDOW_NAME, window_width, window_height)

    mouse_params = {
        "landmark_visibility": landmark_visibility,
        "upscaled_dim": upscaled_dim,
    }
    cv2.setMouseCallback(constants.EYE_TRACKING_WINDOW_NAME, controller.mouse_callback, mouse_params)


def camera_init() -> cv2.VideoCapture:
    """
    Initialises the camera
    :return cv2.VideoCapture: The camera object
    """
    cam = cv2.VideoCapture(0)
    return cam


def face_mesh_init() -> FaceMesh:
    """
    Initialises the face mesh detector
    :return FaceMesh: The face mesh detector
    """
    face_mesh = FaceMesh(refine_landmarks=True, max_num_faces=1)
    return face_mesh


def set_landmark_button_visibility() -> Dict[str, bool]:
    return {
        "left": True,  # Left eye
        "right": True,  # Right eye
        "eyebrow_left": True,
        "eyebrow_right": True,
        "upper_eyelid_left": True,
        "upper_eyelid_right": True,
        "lower_eyelid_left": True,
        "lower_eyelid_right": True,
        "under_eye_left": True,
        "under_eye_right": True,
        "eyesocket_outside_left": True,
        "eyesocket_outside_right": True,
        "above_eye_left": True,
        "above_eye_right": True,
        "lips": True,
        "nose_bridge": True,
        "nose_lower": True,
        "nostrils": True,
        "tear_trough_left": True,
        "tear_trough_right": True,
        "chin": True,
        "cheek_left": True,
        "cheek_right": True,
        "ear_left": True,
        "ear_right": True,
        "temporal_left": True,
        "temporal_right": True,
        "philtrum": True,
        "upper_lip": True,
        "forehead": True,
    }
