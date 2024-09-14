"""
Module for date and time related functions
"""

from datetime import datetime

from common.logger_helper import init_logger

logger = init_logger()


def timestamp(format="%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'.

    Args:
        format (str): The format string for the timestamp.

    Returns:
        str: The current timestamp.
    """
    timestamp = datetime.now().strftime(format)
    logger.info(f"Timestamp: {timestamp}")

    return timestamp


def timestamp_filename_safe() -> str:
    """
    Returns the current timestamp in a filename-safe format 'YYYY-MM-DD_HH-MM-SS'.

    Returns:
        str: The current timestamp.
    """
    return timestamp("%Y-%m-%d_%H-%M-%S")
