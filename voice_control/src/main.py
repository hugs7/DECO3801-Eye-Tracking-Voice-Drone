"""
Entry point for the voice control module.
"""

from typing import Optional, Dict
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

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
    voice_controller.run()


def main(manager_data: Optional[Dict] = None):
    """
    The main function that runs the voice control program.

    Args:
        shared_data (Dict): Shared data between threads: (Only provided if running as a child thread)

    Returns:
        None
    """

    config = init.init()

    running_in_thread = manager_data is not None

    if running_in_thread:
        logger.info("Running as process.")
    else:
        logger.info("Running in main mode")

    run_voice_controller(config, manager_data)

    logger.info("Done.")


if __name__ == "__main__":
    main()
