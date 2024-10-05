"""
Helper functions for handling loading / progress
"""

from typing import Dict, Any
from threading import Lock

from common.logger_helper import init_logger

logger = init_logger()


class LoadingHelper:
    def __init__(self, loading_shared_data: Dict, data_lock: Lock, num_stages: int):
        """
        Initialise the loading helper

        Args:
            loading_shared_data: Shared data
            data_lock: Lock for shared data
        """
        self.loading_shared_data = loading_shared_data
        self.data_lock = data_lock
        self.num_stages = num_stages
        self.num_tasks = 0

        self.current_stage_name = ""
        self.current_stage = 0
        self.current_task_name = ""
        self.current_task = 0

    def set_stage(self, title: str, num_tasks: int) -> None:
        """
        Sets a new stage in the loading process

        Args:
            title: New title
            num_tasks: Number of tasks in this stage
        """
        self.current_stage_name = title
        logger.info("Title: %s", title)
        self.__set_progress_value("title", title)
        self.num_tasks = num_tasks
        self.current_task = 0
        self.current_stage += 1
        if self.current_stage > self.num_stages:
            raise ValueError("Current stage exceeds number of stages %d", self.num_stages)
        self.__update_progress()

    def set_loading_task(self, task: str) -> None:
        """
        Set the message of the current task.

        Args:
            task: The message to set for the current task
        """
        self.current_task_name = task
        logger.info("Status: %s", task)
        self.__set_progress_value("task", task)
        self.current_task += 1
        if self.current_task > self.num_tasks:
            raise ValueError("Current task exceeds number of tasks for stage %s", self.current_stage_name)
        self.__update_progress()

    def __update_progress(self) -> None:
        """
        Updates the progress bar based on the current loading stage and task
        """
        stage_progress = round((self.current_stage / self.num_stages) * 100)
        task_progress = round((self.current_task / self.num_tasks) * (100 / self.num_stages))

        overall_progress = stage_progress + task_progress
        if not overall_progress in range(0, 101):
            raise ValueError("Overall progress is not within the range 0-100: %d", overall_progress)

        self.__set_progress_value("progress", overall_progress)

    def __set_progress_value(self, key: str, value: Any) -> None:
        """
        Sets a value within the progress dictionary

        Args:
            key: The key to set
            value: The value to set
        """

        with self.data_lock:
            self.loading_shared_data["progress"][key] = value
