"""
Module for date and time related functions
"""

from logger_helper import init_logger
from datetime import datetime


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
