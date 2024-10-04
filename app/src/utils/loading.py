"""
Helper functions for handling loading / progress
"""

from threading import Lock
from typing import Dict

from common.logger_helper import init_logger

logger = init_logger()


class LoadingHelper:
    def __init__(self, loading_data: Dict, data_lock: Lock):
        """
        Initialise the loading helper

        Args:
            loading_data: Shared data
            data_lock: Lock for shared data
        """
        self.loading_data = loading_data
        self.data_lock = data_lock

    def set_loading_status(self, status: str) -> None:
        """
        Set the loading status

        Args:
            status: New status
        """
        logger.info(status)

        with self.data_lock:
            self.loading_data["status"] = status
