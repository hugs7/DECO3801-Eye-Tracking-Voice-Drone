"""
Image helper functions
Hugo Burton
21/09/2024
"""

from typing import Optional

import cv2
import numpy as np

from .logger_helper import init_logger

logger = init_logger()


def encode_frame(frame: cv2.typing.MatLike) -> Optional[bytes]:
    """
    Encodes a frame to a byte string.

    Args:
        frame (cv2.typing.MatLike): The frame to encode

    Returns:
        Optional[bytes]: The encoded frame or None if encoding failed
    """

    success, encoded_img = cv2.imencode(".jpg", frame)
    if not success:
        logger.error("Failed to encode image.")
        return None

    buffer = encoded_img.tobytes()
    return buffer


def decode_frame(buffer: bytes) -> Optional[cv2.typing.MatLike]:
    """
    Decodes a byte string to a frame.

    Args:
        buffer (bytes): The byte string to decode

    Returns:
        Optional[cv2.typing.MatLike]: The decoded frame or None if decoding failed
    """

    try:
        nparr = np.frombuffer(buffer, np.uint8)
    except Exception as e:
        logger.error(f"Error decoding buffer: {e}")
        return None

    try:
        video_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        logger.error(f"Error decoding frame: {e}")
        return None
