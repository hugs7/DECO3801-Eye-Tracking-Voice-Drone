"""
Defines main loop for eye tracking
"""

from typing import Tuple
import cv2

import constants
import coordinate
import calibrate
import draw
import eye_movement
import landmarks
from colours import ColourMap as CM


def main_loop(calibrated: bool, cam, face_mesh, landmark_mapping: landmarks.LandmarkMapping) -> Tuple[bool, bool]:
    """
    Defines one iteration of the main loop
    to track eye movement
    :param calibrated: Whether the eye has been calibrated
    :return Tuple[bool, bool]: The run status and calibration status
    """

    # Define globals
    global run, reference_positions

    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape
    frame_dims = coordinate.Coorrdinate(frame_w, frame_h)

    if points:
        landmarks = points[0].landmark

        if not calibrated:
            cv2.putText(
                frame,
                "Look at the camera and press Enter to calibrate",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                CM.white.get_colour(),
                2,
                cv2.LINE_AA,
            )

        draw.draw_landmarks(frame, landmarks, frame_dims)

        if calibrated:
            eye_movement.track_eye_movement(frame, landmarks, frame_dims)

    cv2.imshow(constants.EYE_TRACKING_WINDOW_NAME, frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        run = False
    elif key == ord("\r"):  # Enter key to calibrate
        if points:
            reference_positions = calibrate.calibrate_eye_positions(landmarks, frame_w, frame_h)
            calibrated = True

    return run, calibrated
