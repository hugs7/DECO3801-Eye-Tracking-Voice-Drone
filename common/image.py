"""
Common image utilities
"""

import numpy as np
import cv2


def blend_frame(frame: np.ndarray, overlay: np.ndarray, alpha: float) -> np.ndarray:
    """
    Blends two frames together using alpha blending.

    Args:
        frame (np.ndarray): The base frame
        overlay (np.ndarray): The overlay frame
        alpha (float): The alpha value for blending

    Returns:
        np.ndarray: The blended frame
    """

    img = np.zeros_like(frame, np.uint8)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, img)

    return img
