"""
Controller for handling progress.
"""

import time
from threading import Thread, Event

from PyQt6.QtCore import pyqtSignal

from common.logger_helper import init_logger
from common.thread_helper import thread_loop_handler

from app.src import constants as c

logger = init_logger()


class ProgressController:
    def __init__(self, num_stages: int, progress_signal: pyqtSignal):
        """
        Initialise the loading helper

        Args:
            loading_shared_data: Shared data
            data_lock: Lock for shared data
        """
        self.num_stages = num_stages
        self.progress_signal: pyqtSignal = progress_signal
        self.complete: bool = False

        self.num_tasks = 0

        self.current_stage_name = ""
        self.current_stage = -1
        self.current_task_name = ""
        self.current_task = -1

        self.previous_progress: int = 0
        self.base_progress: int = 0

        self.progress_sim_thread = None
        self.stop_event = Event()

    def set_stage(self, title: str, num_tasks: int) -> None:
        """
        Sets a new stage in the loading process

        Args:
            title: New title
            num_tasks: Number of tasks in this stage
        """
        if self.complete:
            raise ValueError("Progress is already complete")

        self.current_stage_name = title
        logger.info("Title: %s", title)
        self.progress_signal.emit(c.LOADING_STAGE, title)
        self.num_tasks = num_tasks
        self.current_task = 0
        self.current_stage += 1

        if self.current_stage > self.num_stages:
            raise ValueError("Current stage exceeds number of stages %d", self.num_stages)

        self.__calculate_base_progress()
        self.set_progress(self.base_progress)

    def set_loading_task(self, task: str, estimated_time: float) -> None:
        """
        Set the message of the current task.

        Args:
            task: The message to set for the current task
            estimated_time: The estimated time to complete the task in seconds
        """
        if self.complete:
            raise ValueError("Progress is already complete")

        if self.progress_sim_thread is not None:
            self.stop_progress_simulation()
            self.current_task += 1
            self.stop_event.clear()

        self.current_task_name = task
        self.progress_signal.emit(c.LOADING_TASK, task)

        if self.current_task > self.num_tasks:
            raise ValueError(f"Current task exceeds number of tasks for stage {self.current_stage_name}")

        self.__calculate_base_progress()

        scaling = 1 / (self.num_stages * self.num_tasks)
        begin_progress = self.base_progress
        logger.info("Begin progress for task %s: %d", task, begin_progress)

        self.progress_sim_thread = Thread(
            target=self._simulate_progress, args=(estimated_time, scaling, self.stop_event), name="progress_sim_thread"
        )
        self.progress_sim_thread.start()

    def _simulate_progress(self, estimated_time: float, scaling: float, stop_event: Event, steps: int = 100) -> None:
        """
        Asynchronously increments progress over the estimated time.

        Args:
            estimated_time: The estimated time to complete the task in seconds
            stop_event: Event to stop the progress simulation
            scaling: Scaling factor for the progress
            steps: The number of steps to increment progress
        """

        time_per_step = estimated_time / steps

        for i in range(steps):
            progress_increment = self.__calculate_percentage(i, steps, scaling)
            new_progress = self.base_progress + progress_increment
            self.set_progress(int(new_progress))
            time.sleep(time_per_step)
            keep_running = thread_loop_handler(stop_event, True)
            if not keep_running or self.complete:
                return

    def stop_progress_simulation(self) -> None:
        """
        Stops the progress simulation thread
        """
        self.stop_event.set()
        self.progress_sim_thread.join()

    def __calculate_base_progress(self) -> None:
        """
        Calculates the progress based on the loading stage and task. Does not
        consider the simulated progress.
        """
        stage_progress = self.__calculate_percentage(self.current_stage, self.num_stages)
        task_progress = self.__calculate_percentage(self.current_task, self.num_tasks, 1 / self.num_stages)

        self.base_progress = int(stage_progress + task_progress)

    def set_progress(self, progress: int) -> None:
        """
        Sets the progress value

        Args:
            progress [int]: The progress value
        """

        if progress == self.previous_progress:
            # No change in progress
            return

        self.progress_signal.emit(c.LOADING_PROGRESS, str(progress))
        self.previous_progress = progress
        if progress >= 100:
            self.progress_signal.emit(c.LOADING_ACTION, c.LOADING_CLOSE)
            self.complete = True

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
