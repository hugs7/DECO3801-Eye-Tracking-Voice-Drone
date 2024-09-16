"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

import sys
from typing import List
from threading import Thread, Event, Lock
from multiprocessing import Manager, Process

from omegaconf import OmegaConf
from PyQt5.QtWidgets import QApplication

# Must go before any other user imports
from import_helper import dynamic_import

from common.logger_helper import init_logger

from gui import MainApp
from thread_helper import get_function_module

logger = init_logger()

if __name__ == "__main__":
    logger.info(">>> Begin")

    logger.info("Initialising modules...")
    eye_tracking = dynamic_import("eye_tracking.src.main", "main")
    voice_control = dynamic_import("voice_control.src.main", "main")
    drone = dynamic_import("drone", "main")
    logger.info("Modules initialised.")

    # === Globals ===

    stop_event = Event()
    data_lock = Lock()
elif __name__ == "__mp_main__":
    logger.info(">>> Begin Multiprocessing")


def is_any_thread_alive(threads: List[Thread]):
    return any(t.is_alive() for t in threads)


def main():
    logger.info(">>> Main Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, drone]
    thread_data = {get_function_module(func): {} for func in thread_functions}
    threads = [
        Thread(target=lambda func=func: func(stop_event, thread_data, data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    # Voice Control is process
    try:
        logger.info("Initialising voice process")
        manager = Manager()
        interprocess_data = manager.dict()
        process_functions = {voice_control: {"command_queue": manager.Queue()}}
        process_shared_dict = {get_function_module(func): init_val for func, init_val in process_functions.items()}
        interprocess_data.update(process_shared_dict)
        processes = [
            Process(target=func, args=(interprocess_data,), name=f"process_{get_function_module(func)}") for func in process_functions
        ]

        logger.info("Initialising drone process")
        for process in processes:
            logger.debug(f"Starting process {process.name}")
            process.start()

        # Start all threads
        logger.info("Initialising threads")
        for thread in threads:
            logger.debug(f"Starting thread {thread.name}")
            thread.start()

        # Gui
        logger.info("Initialising GUI")
        gui = QApplication(sys.argv)
        main_window = MainApp(stop_event, thread_data, data_lock, interprocess_data)
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
