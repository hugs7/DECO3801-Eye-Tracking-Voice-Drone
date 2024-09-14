"""
Module for date and time related functions
"""

import logging
from datetime import datetime


logger = logging.getLogger(__name__)


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
