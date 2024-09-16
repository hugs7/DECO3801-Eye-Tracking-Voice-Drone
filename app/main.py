"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread, Event, Lock
from time import sleep
from typing import List
import sys
from omegaconf import OmegaConf

# Must go before any other imports
from import_helper import dynamic_import

from common.logger_helper import init_logger

from gui import MainApp, QApplication
import constants as c
from thread_helper import get_function_module
from conf_helper import safe_get

logger = init_logger()

eye_tracking = dynamic_import("eye_tracking.src.main", "main")
voice_control = dynamic_import("voice_control.src.main", "main")
drone = dynamic_import("drone", "main")

# === Globals ===

stop_event = Event()
data_lock = Lock()


def is_any_thread_alive(threads: List[Thread]):
    return any(t.is_alive() for t in threads)


def main():
    logger.info(">>> Begin")

    # Create threads for each of the components
    thread_functions = [eye_tracking, voice_control, drone]
    shared_data = OmegaConf.create({get_function_module(func): OmegaConf.create() for func in thread_functions})
    threads = [
        Thread(target=lambda func=func: func(stop_event, shared_data, data_lock), name=f"thread_{get_function_module(func)}")
        for func in thread_functions
    ]

    # Start all threads
    logger.info("Initialising threads")
    for thread in threads:
        thread.start()

    logger.info("Initialising GUI")
    try:
        # Gui
        gui = QApplication(sys.argv)
        main_window = MainApp(shared_data, stop_event)
        main_window.show()
        gui.exec_()
    except KeyboardInterrupt:
        logger.critical("Interrupted! Stopping all threads...")

    logger.info("Signalling all threads to stop")
    stop_event.set()

    # Ensure all threads are properly joined after signaling them to stop
    for thread in threads:
        thread.join()

    logger.info("Closing GUI")
    gui.quit()

    logger.debug("<<< End")


if __name__ == "__main__":
    main()
