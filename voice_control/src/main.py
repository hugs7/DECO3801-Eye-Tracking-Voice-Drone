"""
Main module for the voice control program.
"""

import init
from typing import Optional, Dict
from threading import Event, Lock

from voice_control.src.voice_controller import VoiceController
from logger_helper import init_root_logger
import audio

root_logger = init_root_logger()


def main(stop_event: Optional[Event] = None, shared_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
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

    voice_procesor = VoiceController(
        config, stop_event, shared_data, data_lock)
    voice_procesor.run()

    root_logger.info("Done.")


if __name__ == "__main__":
    main()
