"""
Entry point for the voice control module.
"""

from typing import Optional, Dict
import os
import sys

# Add the project root to the path. Must execute prior to common imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from common.logger_helper import init_logger

from . import init
from .voice_controller import VoiceController

logger = init_logger()


def main(manager_data: Optional[Dict] = None):
    """
    The main function that runs the voice control program.

    Args:
        manager_data (Optional[Dict]): Interprocess communication (IPC) data dictionary:
                                       (Only provided if running as a child process)

    Returns:
        None
    """

    config = init.init()

    running_in_thread = manager_data is not None

    if running_in_thread:
        logger.info("Running as process.")
    else:
        logger.info("Running in main mode")

    voice_controller = VoiceController(config, manager_data)
    voice_controller.run()

    logger.info("Done.")


if __name__ == "__main__":
    main()
