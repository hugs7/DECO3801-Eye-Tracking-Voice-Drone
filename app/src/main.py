"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import sys
from typing import List
from threading import Thread, Event, Lock
from multiprocessing import Manager, Process

from PyQt6.QtWidgets import QApplication

# Must go before any other user imports to ensure project directory is added to sys.path
from utils.import_helper import dynamic_import
from utils.loading import set_loading_status

from gui import MainApp
from loading_gui import LoadingGUI

from common.logger_helper import init_logger
from common.thread_helper import get_function_module


logger = init_logger()


if __name__ == "__main__":
    logger.info(">>> Begin")

    loading_gui = QApplication(sys.argv)
    loading_data_lock = Lock()
    loading_stop_event = Event()
    loading_shared_data = {"status": ""}
    loading_window = LoadingGUI(loading_shared_data, loading_data_lock, loading_stop_event)
    loading_gui_thread = Thread(target=loading_gui.exec, name="loading_gui_thread")
    loading_gui_thread.start()

    set_loading_status(loading_shared_data, loading_data_lock, "Initialising eye tracking module")
    eye_tracking = dynamic_import("eye_tracking.src.main", "main")
    set_loading_status(loading_shared_data, loading_data_lock, "Initialising voice control module")
    voice_control = dynamic_import("voice_control.src.main", "main")
    set_loading_status(loading_shared_data, loading_data_lock, "Initialising drone module")
    drone = dynamic_import("drone.src.main", "main")
    logger.info("Modules initialised.")
elif __name__ == "__mp_main__":
    logger.info(">>> Begin Multiprocessing")


def is_any_thread_alive(threads: List[Thread]):
    """
    Check if any thread is alive.
    """
    return any(t.is_alive() for t in threads)


def wrap_set_loading_status(status: str):
    """
    Wrapper for set_loading_status which uses shared loading data and lock as globals.

    Args:
        status: New status
    """
    # Check args are defined
    global_vars = globals()
    if "loading_shared_data" not in global_vars or "loading_data_lock" not in global_vars:
        raise ValueError("Loading shared data and lock must be defined as globals.")

    global loading_shared_data, loading_data_lock
    set_loading_status(loading_shared_data, loading_data_lock, status)


def main():
    logger.info(">>> Main Begin")

    # Define lock and stop event early to ensure KeyboardInterrupt
    # can signal all threads to stop.
    stop_event = Event()
    data_lock = Lock()

    try:
        # =========== Processes ===========

        # Due to blocking operation, the voice control module is run in a Process
        # (instead of a Thread) to allow for parallel execution and termination on
        # parent process exit. As a result, the shared data is managed by a Manager
        # object to allow for inter-process communication.
        wrap_set_loading_status("Initialising voice process")
        manager = Manager()
        interprocess_data = manager.dict()
        process_functions = {voice_control: {"command_queue": manager.Queue()}}
        process_shared_dict = {get_function_module(func): init_val for func, init_val in process_functions.items()}
        interprocess_data.update(process_shared_dict)
        processes = [
            Process(target=func, args=(interprocess_data,), name=f"process_{get_function_module(func)}") for func in process_functions
        ]

        wrap_set_loading_status("Initialising processes")
        for process in processes:
            logger.debug(f"Starting process {process.name}")
            process.start()

        # =========== Threads ===========

        # The remaining components (eye tracking and drone) are run in threads.
        # Threads use a different thread_data object because threads share memory.
        # but also require a lock to prevent race conditions when accessing shared data.
        thread_functions = [eye_tracking, drone]
        thread_data = {get_function_module(func): {} for func in thread_functions}
        threads = [
            Thread(target=lambda func=func: func(stop_event, thread_data, data_lock), name=f"thread_{get_function_module(func)}")
            for func in thread_functions
        ]
        wrap_set_loading_status("Starting threads")

        for thread in threads:
            logger.debug(f"Starting thread {thread.name}")
            thread.start()

        # Exit loading GUI
        loading_stop_event.set()
        loading_gui.quit()
        loading_gui_thread.join()

        # Main GUI
        # Keeps the main thread alive so we do not need a secondary while loop
        logger.info("Initialising GUI")
        gui = QApplication(sys.argv)
        main_window = MainApp(stop_event, thread_data, data_lock, interprocess_data)
        main_window.show()
        gui.exec()
    except KeyboardInterrupt:
        logger.critical("Interrupted! Stopping all threads...")

    logger.info("Signalling all threads to stop")
    stop_event.set()

    # Ensure all threads and processes are properly joined after signaling them to stop
    for process in processes:
        process.join()
        if process.is_alive():
            logger.info(f"Terminating process {process.name}")
            process.terminate()

    for thread in threads:
        thread.join()

    logger.info("Closing GUI")
    gui.quit()

    logger.debug("<<< End")


if __name__ == "__main__":
    main()
