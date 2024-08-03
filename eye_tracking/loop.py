"""
Defines main loop for eye tracking
"""

from typing import Tuple, List
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import coordinate
import calibrate
import draw
import eye_movement
import landmarks
import pose_estimation

from colours import ColourMap as CM
from custom_types.NormalisedLandmark import NormalisedLandmark

calibration_data = None
calibrated = False
show_landmarks = True


def main_loop(
    cam: cv2.VideoCapture, face_mesh: FaceMesh, landmark_mapping: landmarks.LandmarkMapping, upscale_dim: coordinate.Coordinate
) -> bool:
    """
    Defines one iteration of the main loop
    to track eye movement
    :param cam: The camera object
    :param face_mesh: The face mesh object
    :param landmark_mapping: The landmark mapping
    :param upscale_dim: The dimensions to upscale to
    :return bool: Whether to continue running
    """

    global calibrated, show_landmarks, calibration_data

    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    # Upscale the frame
    upscaled_frame = cv2.resize(frame, upscale_dim.to_tuple())
    frame_h, frame_w, _ = upscaled_frame.shape
    frame_dim = coordinate.Coordinate(frame_w, frame_h)

    if points:
        landmarks: List[NormalisedLandmark] = points[0].landmark
        if not calibrated:
            cv2.putText(
                upscaled_frame,
                "Look at the camera and press Enter to calibrate",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                CM.white.get_colour(),
                2,
                cv2.LINE_AA,
            )

        if show_landmarks:
            draw.draw_landmarks(upscaled_frame, landmarks, landmark_mapping, upscale_dim)

        if calibrated and calibration_data is not None:
            # We enter the calibration mode
            calibrate.perform_calibration(calibration_data, upscaled_frame)

        # if calibrated:
        #     eye_movement.track_eye_movement(upscaled_frame, landmarks, frame_dim)

        pose_estimation.estimate_pose(upscaled_frame, landmarks, landmark_mapping)

    # Render
    cv2.imshow(constants.EYE_TRACKING_WINDOW_NAME, upscaled_frame)

    key = cv2.waitKey(1) & 0xFF
    run = True
    if key == ord("q"):
        run = False
    elif key == ord("\r"):
        # Enter key to calibrate
        if points:
            calibration_data = calibrate.calibrate_init(landmarks, landmark_mapping, frame_dim)
            print("initiating calibration", calibration_data)
            calibrated = True
    elif key == ord("l"):
        # Toggle landmarks
        show_landmarks = not show_landmarks
        print(f"Show landmarks: {show_landmarks}")

    return run
