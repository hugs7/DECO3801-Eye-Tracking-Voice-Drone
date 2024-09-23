"""
Helper functions for GUI
"""

from . import constants as c


def fps_to_ms(fps: int) -> int:
    """
    Convert frames per second to milliseconds.

    Args:
        fps: Frames per second

    Returns:
        Milliseconds per frame
    """

    if fps == 0:
        return 0

    return c.MILLISECONDS_PER_SECOND // fps


def ms_to_fps(ms: float) -> float:
    """
    Convert milliseconds to frames per second.

    Args:
        ms: Milliseconds per frame

    Returns:
        [float] Frames per second
    """

    if ms == 0:
        return float("inf")

    return c.MILLISECONDS_PER_SECOND / ms
