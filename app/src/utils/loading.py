"""
Helper functions for handling loading / progress
"""

from threading import Lock
from typing import Dict

from common.logger_helper import init_logger

logger = init_logger()


def set_loading_status(loading_data: Dict, data_lock: Lock, status: str) -> None:
    """
    Set the loading status

    Args:
        loading_data: Shared data
        data_lock: Lock for shared data
        status: New status
    """
    logger.info(status)

    with data_lock:
        loading_data["status"] = status
