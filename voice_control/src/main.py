"""
Entry point for the voice control module.
"""

from typing import Optional, Dict
from threading import Event, Lock
from multiprocessing import Process, Manager
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from omegaconf import OmegaConf

from common.logger_helper import init_logger

from . import init
from .voice_controller import VoiceController

logger = init_logger()


def run_voice_controller(config, shared_manager_data: Optional[Dict] = None) -> None:
    """
    Initialises and runs the voice controller. Handles keyboard interrupts gracefully.

    Args:
        config: The configuration object
        shared_manager_data: Shared data for the voice controller process. Can be
                             None if not running in thread mode.


    Returns:
        None
    """

    voice_controller = VoiceController(config, shared_manager_data)
    try:
        voice_controller.run()
    except KeyboardInterrupt:
        logger.critical("Keyboard interrupt received. Stopping voice controller.")


def main(stop_event: Optional[Event] = None, shared_data: Optional[OmegaConf] = None, data_lock: Optional[Lock] = None):
    """
    The main function that runs the voice control program.

    Args:
        (Only provided if running as a child thread)
        stop_event: Event to signal stop
        shared_data: Shared data between threads
        data_lock: Lock for shared data

    Returns:
        None
    """

    config = init.init()

    required_args = [stop_event, shared_data, data_lock]
    running_in_thread = any(required_args)

    if running_in_thread:
        # If running in thread mode, all or none of the required args must be provided
        if not all(required_args):
            raise ValueError("All or none of stop_event, shared_data, data_lock must be provided.")

        logger.info("Running in thread mode")

        # Lazily import thread helpers only if running in thread mode
        from app.thread_helper import thread_loop_handler

        manager = Manager()
        shared_manager_data = manager.dict()
        shared_manager_data.update(shared_data)
    else:
        logger.info("Running in main mode")
        shared_manager_data = None

    # Start voice controller in a separate process
    voice_controller = Process(target=run_voice_controller, args=(config, shared_manager_data))
    voice_controller.name = "VoiceController"
    voice_controller.start()

    while voice_controller.is_alive():
        if running_in_thread:
            thread_loop_handler(stop_event)

    voice_controller.join()

    logger.info("Done.")


if __name__ == "__main__":
    main()
