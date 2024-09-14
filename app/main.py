"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import importlib
import logging
from threading import Thread, Event, Lock
from time import sleep
import os
import sys

from omegaconf import OmegaConf

import constants as c
from thread_helper import get_function_module
from logger_helper import init_root_logger, disable_logger

root_logger = init_root_logger()


def dynamic_import(module_path: str, alias: str):
    """
    Dynamically imports a module based on the given path.

    Args:
        module_path: Relative path to the module to import
        alias: Alias for the imported module's main function

    Returns:
        Imported module's function
    """
    # Go up one directory from app/main.py to project root
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), ".."))

    # Adjust the system path to include project root
    sys.path.insert(0, project_root)

    # Dynamically import the module
    module = importlib.import_module(module_path)

    return getattr(module, alias)


eye_tracking = dynamic_import("eye_tracking.src.main", "main")
voice_control = dynamic_import("voice_control.src.main", "main")
drone = dynamic_import("drone", "main")

# === Globals ===

stop_event = Event()
data_lock = Lock()


def is_any_thread_alive(threads):
    return any(t.is_alive() for t in threads)


def main():
    root_logger.debug(">>> Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, voice_control, drone]
    shared_data = OmegaConf.create({
        get_function_module(func): OmegaConf.create() for func in thread_functions})
    threads = [
        Thread(target=lambda func=func: func(stop_event, shared_data,
               data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    disable_logger("voice_control")
    logging.getLogger("eye_tracking").setLevel(logging.DEBUG)
    logging.getLogger("drone").setLevel(logging.DEBUG)

    # Start all threads
    for thread in threads:
        thread.start()

    try:
        # Periodically check if any thread is alive
        while is_any_thread_alive(threads):
            # Sleep for a short duration to prevent busy-waiting
            sleep(c.BUSY_WAIT_PERIOD_SECONDS)
    except KeyboardInterrupt:
        root_logger.critical("Interrupted! Stopping all threads...")
        stop_event.set()

        # Ensure all threads are properly joined after signaling them to stop
        for thread in threads:
            thread.join()

    root_logger.debug("<<< End")


if __name__ == "__main__":
    main()
