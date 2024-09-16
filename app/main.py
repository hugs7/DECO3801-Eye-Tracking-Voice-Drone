"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread, Event, Lock
from multiprocessing import Manager, Process
from typing import List
import sys
from omegaconf import OmegaConf

# Must go before any other imports
from import_helper import dynamic_import

from common.logger_helper import init_logger

from gui import MainApp, QApplication
from thread_helper import get_function_module

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


def main():
    logger.info(">>> Main Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, drone]
    shared_data = OmegaConf.create({get_function_module(func): OmegaConf.create() for func in thread_functions})
    threads = [
        Thread(target=lambda func=func: func(stop_event, shared_data, data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    # Voice Control is process
    try:
        logger.info("Initialising voice process")
        manager = Manager()
        manager_data = manager.dict()
        process_functions = [voice_control]
        process_shared_dict = {get_function_module(func): None for func in process_functions}
        manager_data.update(process_shared_dict)
        processes = [Process(target=func, args=(manager_data,), name=f"process_{get_function_module(func)}") for func in process_functions]
        for process in processes:
            process.start()

        # Start all threads
        logger.info("Initialising threads")
        for thread in threads:
            thread.start()

        # Gui
        logger.info("Initialising GUI")
        gui = QApplication(sys.argv)
        main_window = MainApp(shared_data, manager_data, stop_event)
        main_window.show()
        gui.exec_()
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
