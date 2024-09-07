"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import importlib
import logging
from threading import Thread, Event, Lock
from time import sleep

import constants as c
from thread_helper import get_function_module
from logger_helper import init_root_logger

root_logger = init_root_logger()


def dynamic_import(module_name: str, alias: str):
    """
    Dynamically imports a module based on the current script context.
    :param module_name: Name of the module to import
    :param alias: Alias for the imported module
    :return: Imported module
    """
    if __name__ == "__main__":
        module = importlib.import_module(module_name)
    else:
        # Handle relative imports
        module = importlib.import_module(f".{module_name}", package=__package__)

    return getattr(module, alias)


eye_tracking = dynamic_import("eye_tracking", "main")
voice_control = dynamic_import("voice_control", "main")
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
    shared_data = {f"{get_function_module(func)}_data": None for func in thread_functions}
    threads = [
        Thread(target=lambda func=func: func(stop_event, shared_data, data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    logging.getLogger("voice_control").setLevel(logging.CRITICAL + 1)
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
