"""
Controller for handling progress.
"""

from typing import Dict, Any
from threading import Lock
import asyncio

from PyQt6.QtCore import pyqtSignal

from common.logger_helper import init_logger

logger = init_logger()


class ProgressController:
    def __init__(self, loading_shared_data: Dict, data_lock: Lock, num_stages: int, progress_signal: pyqtSignal):
        """
        Initialise the loading helper

        Args:
            loading_shared_data: Shared data
            data_lock: Lock for shared data
        """
        self.loading_shared_data = loading_shared_data
        self.data_lock = data_lock
        self.num_stages = num_stages
        self.progress_signal: pyqtSignal = progress_signal

        self.num_tasks = 0

        self.current_stage_name = ""
        self.current_stage = -1
        self.current_task_name = ""
        self.current_task = -1

        self.overall_progress = 0.0

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

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
        if self.loop.is_running():
            asyncio.create_task(self.async_increment_progress(task, estimated_time))
        else:
            self.loop.run_until_complete(self.async_increment_progress(task, estimated_time))

    async def async_increment_progress(self, task: str, estimated_time: float, steps: int = 100) -> None:
        """
        Asynchronously increments progress over the estimated time.

        Args:
            task: The message to set for the current task
            estimated_time: The estimated time to complete the task in seconds
            steps: The number of steps to increment progress
        """
        self.current_task_name = task
        self.__set_status_value("task", task)

        if self.current_task > self.num_tasks:
            raise ValueError(f"Current task exceeds number of tasks for stage {self.current_stage_name}")

        self.__calculate_base_progress()

        steps = 100
        time_per_step = estimated_time / steps
        scaling = 1 / (self.num_stages * self.num_tasks)
        begin_progress = self.overall_progress

        for i in range(steps):
            progress_increment = self.__calculate_percentage(i, steps, scaling)
            new_progress = self.overall_progress + progress_increment
            self.set_progress(new_progress)
            await asyncio.sleep(time_per_step)

        self.current_task += 1

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
        if not 0 <= int_progress <= 100:
            raise ValueError("Overall progress is not within the range 0-100: %d", int_progress)
        self.progress_signal.emit("progress", int_progress)
        # self.__set_status_value("progress", int_progress)

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
