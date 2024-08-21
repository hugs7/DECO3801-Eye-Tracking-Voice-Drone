"""
Module for handling camera and camera feed
Author: Hugo Burton
Last Updated: 02/08/2024
"""

from typing import Tuple
import cv2


def upscale(frame: cv2.VideoCapture, upscaled_dim: Tuple[int, int]) -> cv2.VideoCapture:
    """
    Upscale the frame
    :param frame: The frame to upscale
    :param upscaled_dim: The dimensions to upscale to (width, height)
    :return cv2.VideoCapture: The upscaled frame
    """

    upscaled_frame = cv2.resize(frame, upscaled_dim)

    return upscaled_frame
