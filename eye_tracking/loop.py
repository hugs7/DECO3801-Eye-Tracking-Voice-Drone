"""
Defines main loop for eye tracking
"""

from typing import Tuple, List, Dict, TypedDict
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import coordinate
import calibrate
import draw
import eye_movement
import controller
import landmarks
import pose_estimation
import camera
from colours import ColourMap as CM
from custom_types.NormalisedLandmark import NormalisedLandmark


class LoopData(TypedDict):
    calibration_data: Dict[str, Tuple[float, float]]
    calibrating: bool
    calibrated: bool
    show_landmarks: bool
    show_settings: bool


loop_data: LoopData = {
    "calibration_data": None,
    "calibrating": False,
    "calibrated": False,
    "show_landmarks": True,
    "show_settings": False,
}


def main_loop(
    cam: cv2.VideoCapture,
    face_mesh: FaceMesh,
    landmark_mapping: landmarks.LandmarkMapping,
    frame_dim: coordinate.Coordinate2D,
    landmark_visibility: Dict[str, bool],
) -> bool:
    """
    Defines one iteration of the main loop
    to track eye movement
    :param cam: The camera object
    :param face_mesh: The face mesh object
    :param landmark_mapping: The landmark mapping
    :param frame_dim: The dimensions to upscale to
    :return bool: Whether to continue running
    """

    global loop_data

    points, frame = camera.read_camera_feed(cam, face_mesh)
    upscaled_frame, frame_dim = camera.upscale(frame, frame_dim)

    if points:
        landmarks: List[NormalisedLandmark] = points[0].landmark
        if not loop_data["calibrated"]:
            draw.render_text(upscaled_frame, "Look at the centre of the screen then press 'c' to begin calibration")

        if loop_data["show_landmarks"]:
            draw.draw_landmarks(upscaled_frame, landmarks, landmark_mapping, frame_dim, landmark_visibility)

        if loop_data["calibrating"]:
            # We enter the calibration mode
            calibrating, calibrated = calibrate.perform_calibration(landmarks, loop_data["calibration_data"], upscaled_frame)
            loop_data["calibrating"] = calibrating
            loop_data["calibrated"] = calibrated

            if loop_data["calibrated"]:
                print("Calibrated")
                print(loop_data["calibration_data"])
                pose_estimation.estimate_gaze(upscaled_frame, landmarks, landmark_mapping, loop_data["calibration_data"])

        elif loop_data["calibrated"]:
            # eye_movement.track_eye_movement(upscaled_frame, landmarks, frame_dim)
            pass

        # pose_estimation.estimate_pose(upscaled_frame, landmarks, landmark_mapping)

    # Draw buttons
    if loop_data["show_settings"]:
        draw.draw_buttons(upscaled_frame, frame_dim, landmark_visibility)

    # Render
    cv2.imshow(constants.EYE_TRACKING_WINDOW_NAME, upscaled_frame)

    # Only wait for key if not in calibration mode or face not detected
    run = True
    if not loop_data["calibrating"] or not points:
        run = controller.handle_loop_key_events(landmarks, landmark_mapping, frame_dim, loop_data, points)

    return run
