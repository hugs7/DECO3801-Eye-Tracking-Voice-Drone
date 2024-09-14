"""
Main module for the voice control program.
"""

from typing import Optional
from threading import Event, Lock
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

    voice_procesor = VoiceController(config, stop_event, shared_data, data_lock)
    voice_procesor.run()

    logger.info("Done.")


if __name__ == "__main__":
    main()
