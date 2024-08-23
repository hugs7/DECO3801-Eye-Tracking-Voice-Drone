"""
Utils for image processing transforms
Author: Hugo Burton
Last Updated: 23/08/2024
"""

from typing import Any

import torchvision.transforms as T


def create_transform() -> Any:
    return T.ToTensor()


import cv2
import numpy as np
from typing import Tuple


def upscale(frame: cv2.VideoCapture, upscaled_dim: Tuple[int, int]) -> cv2.VideoCapture:
    """
    Upscale the frame
    :param frame: The frame to upscale
    :param upscaled_dim: The dimensions to upscale to (width, height)
    :return cv2.VideoCapture: The upscaled frame
    """

    upscaled_frame = cv2.resize(frame, upscaled_dim)

    return upscaled_frame


def flip_image(image: np.ndarray) -> np.ndarray:
    """
    Flip the image
    :param image: The image to flip
    :return np.ndarray: The flipped image
    """

    return image[:, ::-1]
