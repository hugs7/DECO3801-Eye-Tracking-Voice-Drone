"""
Defines main loop for eye tracking
"""

from typing import Tuple, List, Dict, TypedDict
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import coordinate
import draw
import controller
import landmarks
import camera
from colours import ColourMap as CM
from custom_types.NormalisedLandmark import NormalisedLandmark


class LoopData(TypedDict):
    show_landmarks: bool
    show_settings: bool


loop_data: LoopData = {
    "show_landmarks": True,
    "show_settings": False,
}


def main_loop(
    cam: cv2.VideoCapture,
    face_mesh: FaceMesh,
    landmark_mapping: landmarks.LandmarkMapping,
    window_dim: coordinate.Coordinate3D,
    landmark_visibility: Dict[str, bool],
) -> bool:
    """
    Defines one iteration of the main loop
    to track eye movement
    :param cam: The camera object
    :param face_mesh: The face mesh object
    :param landmark_mapping: The landmark mapping
    :param window_dim: The dimensions of the window on screen
    :return bool: Whether to continue running
    """

    global loop_data

    points, frame = camera.read_camera_feed(cam, face_mesh)
    upscaled_frame, frame_dim = camera.upscale(frame, window_dim)

    if points:
        landmarks: List[NormalisedLandmark] = points[0].landmark
        if loop_data["show_landmarks"]:
            draw.draw_landmarks(upscaled_frame, landmarks, landmark_mapping, frame_dim, landmark_visibility)

    # Draw buttons
    if loop_data["show_settings"]:
        draw.draw_buttons(upscaled_frame, frame_dim, landmark_visibility)

    # Render
    cv2.imshow(constants.EYE_TRACKING_WINDOW_NAME, upscaled_frame)

    run = True
    run = controller.handle_loop_key_events(loop_data)

    return run
