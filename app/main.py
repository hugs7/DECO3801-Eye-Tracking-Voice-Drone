"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import importlib
from threading import Thread, Event
import logging
from time import sleep


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
        module = importlib.import_module(
            f".{module_name}", package=__package__)

    return getattr(module, alias)


eye_tracking = dynamic_import("eye_tracking", "main")
voice_control = dynamic_import("voice_control", "main")
drone = dynamic_import("drone", "main")


stop_event = Event()


def thread_wrapper(func) -> None:
    """
    Wrapper function to run a function in a thread.
    Passes a stop event to the function as a signal to stop execution.
    :param func: Function to run in a thread
    :return: None
    """
    while not stop_event.is_set():
        func(stop_event)


def is_any_thread_alive(threads):
    return any(t.is_alive() for t in threads)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(" >>> Begin")

    # Create threads for each of the components
    threads = [
        Thread(target=lambda: thread_wrapper(eye_tracking)),
        Thread(target=lambda: thread_wrapper(voice_control)),
        Thread(target=lambda: thread_wrapper(drone)),
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    try:
        # Periodically check if any thread is alive
        while is_any_thread_alive(threads):
            # Sleep for a short duration to prevent busy-waiting
            sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Interrupted! Stopping all threads...")
        stop_event.set()  # Signal all threads to stop

        # Ensure all threads are properly joined after signaling them to stop
        for thread in threads:
            thread.join()

    logging.info(" <<< End")


if __name__ == "__main__":
    main()
