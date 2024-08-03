"""
Defines main loop for eye tracking
"""

from typing import Tuple, List
import cv2

import constants
import coordinate
import calibrate
import draw
import eye_movement
import landmarks
import pose_estimation

from colours import ColourMap as CM
from custom_types.NormalisedLandmark import NormalisedLandmark


def main_loop(
    calibrated: bool, cam, face_mesh, landmark_mapping: landmarks.LandmarkMapping, upscale_dim: coordinate.Coordinate
) -> Tuple[bool, bool]:
    """
    Defines one iteration of the main loop
    to track eye movement
    :param run: Whether the program should continue running
    :param calibrated: Whether the eye has been calibrated
    :param cam: The camera object
    :param face_mesh: The face mesh object
    :param landmark_mapping: The landmark mapping
    :param upscale_dim: The dimensions to upscale to
    :return Tuple[bool, bool]: The run status and calibration status
    """

    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape
    frame_dim = coordinate.Coordinate(frame_w, frame_h)

    # Upscale the frame
    upscaled_frame = cv2.resize(frame, upscale_dim.to_tuple())

    if points:
        landmarks: List[NormalisedLandmark] = points[0].landmark

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

        draw.draw_landmarks(upscaled_frame, landmarks, landmark_mapping, upscale_dim)

        if calibrated:
            eye_movement.track_eye_movement(upscaled_frame, landmarks, frame_dim)

        pose_estimation.estimate_pose(upscaled_frame, landmarks, landmark_mapping)

    # Render
    cv2.imshow(constants.EYE_TRACKING_WINDOW_NAME, upscaled_frame)

    key = cv2.waitKey(1) & 0xFF
    run = True
    if key == ord("q"):
        run = False
    elif key == ord("\r"):  # Enter key to calibrate
        if points:
            reference_positions = calibrate.calibrate_eye_positions(landmarks, frame_dim)
            calibrated = True

    return run, calibrated
