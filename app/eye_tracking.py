"""
Mock Eye Tracking module
Hugo Burton
06/09/2024
"""

from typing import Optional
from threading import Event, Lock
from time import sleep
import random
from omegaconf import OmegaConf

from thread_helper import thread_exit_handler, is_main_thread
from logger_helper import init_logger

logger = init_logger()


def loop(shared_data: Optional[OmegaConf] = None, data_lock: Optional[Lock] = None):
    """
    Eye Tracking Loop
    """

    logger.debug(">>> Begin Eye Tracking loop")

    random_num = random.randint(1, 1500)
    sleep(1.4)
    logger.info(f"Set random number: {random_num}")
    if not is_main_thread():
        with data_lock:
            shared_data.eye_tracking = random_num

    logger.debug("<<< End Eye Tracking loop")


def main(stop_event: Optional[Event] = None, shared_data: Optional[OmegaConf] = None, data_lock: Optional[Lock] = None):
    logger.info("Init eye tracking module")

    while True:
        loop(shared_data, data_lock)
        thread_exit_handler(stop_event)


if __name__ == "__main__":
    main()
