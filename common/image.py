"""
Common image utilities
"""

from typing import Tuple
import numpy as np
import cv2


def blend_frame(frame: np.ndarray, overlay: np.ndarray, alpha: float) -> np.ndarray:
    """
    Blends two frames together using alpha blending. Assumes both frames are the same shape.

    Args:
        frame (np.ndarray): The base frame
        overlay (np.ndarray): The overlay frame
        alpha (float): The alpha value for blending

    Returns:
        np.ndarray: The blended frame
    """

    assert frame.shape == overlay.shape, "Frame and overlay must have the same shape"

    img = np.zeros_like(frame, np.uint8)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, img)

    return img


def rescale_frame(frame: np.ndarray, shape: Tuple[int, int, int]) -> np.ndarray:
    """
    Rescales the frame to the specified shape

    Args:
        frame (np.ndarray): The frame to rescale
        shape (Tuple[int, int, int]): The shape to rescale the frame to

    Returns:
        np.ndarray: The rescaled frame
    """

    return cv2.resize(frame, (shape[1], shape[0]), interpolation=cv2.INTER_AREA)
