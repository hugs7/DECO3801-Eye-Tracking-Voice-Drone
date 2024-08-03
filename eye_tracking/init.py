"""
Initialises the eye_tracking package.
"""

import os
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import landmarks
import utils.file_helper as file_helper


def landmark_mapping_init() -> landmarks.Landmarks:
    """
    Initialises the mapping for landmarks on the face
    """

    LANDMARK_MAPPING_PATH = file_helper.resolve_path(os.path.join(constants.MAPPINGS_FOLDER, "landmark_mapping.json"))

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)
    lmks = landmarks.Landmarks(landmark_mapping)

    return lmks


def window_init(window_width: int, window_height: int):
    """
    Initialises the window for the eye tracking application
    :param window_width: The width of the window
    :param window_height: The height of the window
    """

    # Set the desired window size
    cv2.namedWindow(constants.EYE_TRACKING_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(constants.EYE_TRACKING_WINDOW_NAME, window_width, window_height)


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
