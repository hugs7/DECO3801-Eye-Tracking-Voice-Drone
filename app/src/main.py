"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread, Event, Lock
from multiprocessing import Manager, Process
from typing import List

from omegaconf import OmegaConf

# Must go first to ensure project directory is added to sys.path
from utils.import_helper import dynamic_import
from utils.conf_helper import safe_get

from common.logger_helper import init_logger
from common.thread_helper import get_function_module


logger = init_logger()

if __name__ == "__main__":
    logger.info(">>> Begin")

    logger.info("Initialising modules...")
    eye_tracking = dynamic_import("eye_tracking.src.main", "main")
    voice_control = dynamic_import("voice_control.src.main", "main")
    drone = dynamic_import("drone", "main")
    logger.info("Modules initialised.")
elif __name__ == "__mp_main__":
    logger.info(">>> Begin Multiprocessing")


def is_any_thread_alive(threads: List[Thread]):
    """
    Check if any thread is alive.
    """
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
        logger.info("Initialising voice process")
        manager = Manager()
        interprocess_data = manager.dict()
        process_functions = {voice_control: {"command_queue": manager.Queue()}}
        process_shared_dict = {get_function_module(func): init_val for func, init_val in process_functions.items()}
        interprocess_data.update(process_shared_dict)
        processes = [
            Process(target=func, args=(interprocess_data,), name=f"process_{get_function_module(func)}") for func in process_functions
        ]

        logger.info("Initialising processes")
        for process in processes:
            logger.debug(f"Starting process {process.name}")
            process.start()

        # =========== Threads ===========

        # The remaining components (eye tracking and drone) are run in threads.
        # Threads use a different shared_data object because threads share memory.
        # but also require a lock to prevent race conditions when accessing shared data.
        thread_functions = [eye_tracking, drone]
        shared_data = OmegaConf.create({get_function_module(func): OmegaConf.create() for func in thread_functions})
        threads = [
            Thread(target=lambda func=func: func(stop_event, shared_data, data_lock), name=f"thread_{get_function_module(func)}")
            for func in thread_functions
        ]
        logger.info("Initialising threads")
        for thread in threads:
            logger.debug(f"Starting thread {thread.name}")
            thread.start()

        while is_any_thread_alive(threads):
            main_loop(shared_data)
    except KeyboardInterrupt:
        logger.critical("Interrupted! Stopping all threads...")
        stop_event.set()

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

    logger.debug("<<< End")


if __name__ == "__main__":
    main()