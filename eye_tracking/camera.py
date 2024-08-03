"""
Module for handling camera and camera feed
"""

from typing import Tuple, Any
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import coordinate


def read_camera_feed(cam: cv2.VideoCapture, face_mesh: FaceMesh) -> Tuple[Any, cv2.VideoCapture]:
    """
    Read the camera feed
    :param cam: The camera object
    :return Tuple[Any, cv2.VideoCapture]: The points and the upscaled frame
    :raises Exception: If failed to read camera feed
    """

    success, frame = cam.read()
    if not success:
        raise Exception("Failed to read camera feed")

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    return points, frame


def upscale(frame: cv2.VideoCapture, window_dim: coordinate.Coordinate3D) -> Tuple[cv2.VideoCapture, coordinate.Coordinate3D]:
    """
    Upscale the frame
    :param frame: The frame to upscale
    :param frame_dim: The dimensions to upscale to
    :return cv2.VideoCapture: The upscaled frame
    """

    upscaled_frame = cv2.resize(frame, window_dim.to_tuple())
    frame_h, frame_w, frame_depth = upscaled_frame.shape
    window_dim = coordinate.Coordinate3D(frame_w, frame_h, frame_depth)

    return upscaled_frame, window_dim
