"""
Utils for image processing transforms
Author: Hugo Burton
Last Updated: 23/08/2024
"""

from typing import Tuple
import cv2
import numpy as np
from common.logger_helper import init_logger
import torchvision.transforms as T

logger = init_logger()


def create_transform() -> T.ToTensor:
    """
    Create a transform object instance which can
    be used to transform images
    :return Any: The transform object
    """
    return T.ToTensor()


def upscale(frame: cv2.VideoCapture, upscaled_dim: Tuple[int, int]) -> cv2.VideoCapture:
    """
    Upscale the frame

    Args:
        frame: The frame to upscale
        upscaled_dim: The dimensions to upscale to (width, height)
    :return cv2.VideoCapture: The upscaled frame
    """

    logger.debug(f"Upscaling frame to {upscaled_dim}")
    upscaled_frame = cv2.resize(frame, upscaled_dim)

    return upscaled_frame


def flip_image(image: np.ndarray) -> np.ndarray:
    """
    Flip the image

    Args:
        image: The image to flip
    :return np.ndarray: The flipped image
    """

    logger.debug("Flipping image")
    return image[:, ::-1]


def add_2d_point(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    """
    Add two tuples together

    Args:
        a: The first tuple
        b: The second tuple
    :return Tuple[int, int]: The sum of the two tuples
    """

    return a[0] + b[0], a[1] + b[1]
