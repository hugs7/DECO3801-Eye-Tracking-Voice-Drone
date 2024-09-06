"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import importlib
from threading import Thread, Event
import logging
from time import sleep

from thread_helper import get_function_name


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


def is_any_thread_alive(threads):
    return any(t.is_alive() for t in threads)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(" >>> Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, voice_control, drone]
    threads = [Thread(target=lambda: func(stop_event), name=f"thread_{get_function_name(func)}") for func in thread_functions]

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
