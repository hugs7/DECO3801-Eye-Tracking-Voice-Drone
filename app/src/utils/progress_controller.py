"""
Controller for handling progress.
"""

from typing import Dict, Any
from threading import Lock

from common.logger_helper import init_logger

logger = init_logger()


class ProgressController:
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

        self.overall_progress = 0.0

    def set_stage(self, title: str, num_tasks: int) -> None:
        """
        Sets a new stage in the loading process

        Args:
            title: New title
            num_tasks: Number of tasks in this stage
        """
        self.current_stage_name = title
        logger.info("Title: %s", title)
        self.__set_status_value("title", title)
        self.num_tasks = num_tasks
        self.current_task = 0
        self.current_stage += 1

        if self.current_stage > self.num_stages:
            raise ValueError("Current stage exceeds number of stages %d", self.num_stages)

        self.__calculate_base_progress()
        self.set_progress(self.overall_progress)

    def set_loading_task(self, task: str, estimated_time: float) -> None:
        """
        Set the message of the current task.

        Args:
            task: The message to set for the current task
            estimated_time: The estimated time to complete the task in seconds
        """
        self.current_task_name = task
        logger.info("Status: %s", task)
        self.__set_status_value("task", task)
        self.__set_status_value("estimated_time", estimated_time)
        self.current_task += 1

        if self.current_task > self.num_tasks:
            raise ValueError("Current task exceeds number of tasks for stage %s", self.current_stage_name)

        self.__calculate_base_progress()
        self.set_progress(self.overall_progress)

    def __calculate_base_progress(self) -> None:
        """
        Calculates the progress based on the loading stage and task. Does not
        consider the simulated progress.
        """
        stage_progress = self.__calculate_percentage(self.current_stage, self.num_stages)
        task_progress = self.__calculate_percentage(self.current_task, self.num_tasks, 1 / self.num_stages)

        self.overall_progress = stage_progress + task_progress

    def set_progress(self, progress: float) -> None:
        """
        Sets the progress value

        Args:
            progress: The progress value
        """
        int_progress = int(progress)
        if not int_progress in range(0, 101):
            raise ValueError("Overall progress is not within the range 0-100: %d", int_progress)
        self.__set_status_value("progress", int_progress)

    def __calculate_percentage(self, current: int, total: int, scaling: float = 1.0) -> float:
        """
        Calculates the percentage of the current value in relation to the total value

        Args:
            current: The current value
            total: The total value
            scaling: Scaling factor, default to 1.0. E.g. if scaling is 0.2, progress will be
                     calculated as (current / total) * 100 * scaling.

        Returns:
            int: The percentage
        """
        return (current / total) * 100 * scaling

    def __set_status_value(self, key: str, value: Any) -> None:
        """
        Sets a value within the status dictionary

        Args:
            key: The key to set
            value: The value to set
        """

        with self.data_lock:
            self.loading_shared_data["status"][key] = value
