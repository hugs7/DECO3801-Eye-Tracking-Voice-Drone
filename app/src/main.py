"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import sys
from typing import List, Dict, Any, Tuple
from threading import Thread, Event, Lock
from multiprocessing import Manager, Process

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# Must go before any other user imports to ensure project directory is added to sys.path
from utils.import_helper import dynamic_import
from utils.loading import LoadingHelper

from gui import MainApp
from loading_gui import LoadingGUI

from common.logger_helper import init_logger
from common.thread_helper import get_function_module


logger = init_logger()


def is_any_thread_alive(threads: List[Thread]):
    """
    Check if any thread is alive.
    """
    return any(t.is_alive() for t in threads)


def initialise_modules(loading_shared_data: Dict, loading_helper: LoadingHelper, stop_event: Event, data_lock: Lock) -> None:
    """
    Initialise the modules, and emit a signal when complete.

    Args:
        loading_shared_data: Shared data
        loading_helper: Loading helper
        stop_event: Stop event
        data_lock: Lock for shared data
    """
    loading_helper.set_stage("Initialising Modules", 3)

    loading_helper.set_loading_task("Initialising eye tracking module")
    eye_tracking = dynamic_import("eye_tracking.src.main", "main")

    loading_helper.set_loading_task("Initialising voice control module")
    voice_control = dynamic_import("voice_control.src.main", "main")

    loading_helper.set_loading_task("Initialising drone module")
    drone = dynamic_import("drone.src.main", "main")

    logger.info("Modules initialised.")

    try:
        # =========== Processes ===========

        # Due to blocking operation, the voice control module is run in a Process
        # (instead of a Thread) to allow for parallel execution and termination on
        # parent process exit. As a result, the shared data is managed by a Manager
        # object to allow for inter-process communication.
        loading_helper.set_stage("Initialising processes", 3)
        loading_helper.set_loading_task("Initialising IPC data manager")
        manager = Manager()
        interprocess_data = manager.dict()
        loading_helper.set_loading_task("Configuring IPC data")
        loading_shared_data["interprocess_data"] = interprocess_data
        loading_helper.set_loading_task("Initialising process functions")
        process_functions = {voice_control: {"command_queue": manager.Queue()}}
        process_shared_dict = {get_function_module(func): init_val for func, init_val in process_functions.items()}
        interprocess_data.update(process_shared_dict)
        processes = [
            Process(target=func, args=(interprocess_data,), name=f"process_{get_function_module(func)}") for func in process_functions
        ]
        loading_shared_data["processes"] = processes

        loading_helper.set_stage("Starting processes", len(processes))
        for process in processes:
            loading_helper.set_loading_task(f"Starting process {process.name}")
            process.start()

        # =========== Threads ===========

        # The remaining components (eye tracking and drone) are run in threads.
        # Threads use a different thread_data object because threads share memory.
        # but also require a lock to prevent race conditions when accessing shared data.
        loading_helper.set_stage("Initialising threads", 2)
        thread_functions = [eye_tracking, drone]
        loading_helper.set_loading_task("Initialising shared data dictionary")
        thread_data = {get_function_module(func): {} for func in thread_functions}
        loading_shared_data["thread_data"] = thread_data
        loading_helper.set_loading_task("Initialising thread functions")
        threads = [
            Thread(target=lambda func=func: func(stop_event, thread_data, data_lock), name=f"thread_{get_function_module(func)}")
            for func in thread_functions
        ]
        loading_shared_data["threads"] = threads

        loading_helper.set_stage("Starting threads", len(threads))
        for thread in threads:
            loading_helper.set_loading_task(f"Starting thread {thread.name}")
            thread.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected, stopping threads and processes.")

    logger.info("Modules initialised.")


def main():
    logger.info(">>> Main Begin")

    gui = QApplication(sys.argv)
    loading_data_lock = Lock()
    loading_stop_event = Event()
    loading_shared_data = {"status": dict()}
    loading_window = LoadingGUI(loading_shared_data, loading_data_lock, loading_stop_event)
    loading_helper = LoadingHelper(loading_shared_data, loading_data_lock, 6)

    try:
        stop_event = Event()
        data_lock = Lock()
        init_thread = Thread(
            target=initialise_modules, args=(loading_shared_data, loading_helper, stop_event, data_lock), name="init_thread"
        )
        init_thread.start()

        loading_window.show()
        gui.exec()

        init_thread.join()

        logger.info("Initialisation complete, closing loading screen.")
        loading_stop_event.set()
        loading_window.close()

        # Define lock and stop event early to ensure KeyboardInterrupt
        # can signal all threads to stop.
        stop_event = Event()
        data_lock = Lock()

        # Gather data from initialisation thread.
        thread_data: Dict[str, Any] = loading_shared_data["thread_data"]
        interprocess_data: Dict[str, Any] = loading_shared_data["interprocess_data"]
        threads: List[Thread] = loading_shared_data["threads"]
        processes: List[Process] = loading_shared_data["processes"]

        logger.info("Launching Main GUI")
        gui = QApplication(sys.argv)
        main_window = MainApp(stop_event, thread_data, data_lock, interprocess_data)
        main_window.show()
        gui.exec()
    except KeyboardInterrupt:
        logger.critical("Interrupted! Stopping all threads...")

    logger.info("Signalling all threads to stop")
    stop_event.set()

    # Ensure all threads and processes are properly joined after signaling them to stop.
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
