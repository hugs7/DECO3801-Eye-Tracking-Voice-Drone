"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread, Event, Lock
from time import sleep
from typing import List

from omegaconf import OmegaConf

from import_helper import dynamic_import
from common.logger_helper import init_logger

import constants as c
from thread_helper import get_function_module
from conf_helper import safe_get


logger = init_logger()

logger.info(">>> Begin")

logger.info("Initialising modules...")
eye_tracking = dynamic_import("eye_tracking.src.main", "main")
voice_control = dynamic_import("voice_control.src.main", "main")
drone = dynamic_import("drone", "main")
logger.info("Modules initialised.")

# === Globals ===

stop_event = Event()
data_lock = Lock()


def is_any_thread_alive(threads: List[Thread]):
    return any(t.is_alive() for t in threads)


def main_loop(shared_data: OmegaConf):
    """
    Main loop in parent thread.

    Args:
        shared_data: Shared data between threads

    Returns:
        None
    """

    # Read shared eye gaze
    eye_tracking_data = shared_data.eye_tracking
    gaze_side = safe_get(eye_tracking_data, "gaze_side")

    if gaze_side is not None:
        logger.info(f"Received gaze side: {gaze_side}")


def main():
    logger.info(">>> Main Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, voice_control, drone]
    shared_data = OmegaConf.create({get_function_module(func): OmegaConf.create() for func in thread_functions})
    threads = [
        Thread(target=lambda func=func: func(stop_event, shared_data, data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    try:
        # Periodically check if any thread is alive
        while is_any_thread_alive(threads):
            main_loop(shared_data)

            # Sleep for a short duration to prevent busy-waiting
            sleep(c.BUSY_WAIT_PERIOD_SECONDS)
    except KeyboardInterrupt:
        logger.critical("Interrupted! Stopping all threads...")
        stop_event.set()

        # Ensure all threads are properly joined after signaling them to stop
        for thread in threads:
            thread.join()

    logger.debug("<<< End")


if __name__ == "__main__":
    main()
