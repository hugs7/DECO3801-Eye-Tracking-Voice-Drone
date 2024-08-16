"""
Module for handling camera and camera feed
"""

from typing import Tuple
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh


def upscale(frame: cv2.VideoCapture, upscaled_dim: Tuple[int, int]) -> cv2.VideoCapture:
    """
    Upscale the frame
    :param frame: The frame to upscale
    :param upscaled_dim: The dimensions to upscale to (width, height)
    :return cv2.VideoCapture: The upscaled frame
    """

    upscaled_frame = cv2.resize(frame, upscaled_dim)

    return upscaled_frame
