"""
Entry point for the eye tracking driver
Author: Hugo Burton
Last Updated: 21/08/2024
"""

from typing import Optional, Dict
from threading import Event, Lock
import os
import sys

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from . import init
from .gaze_detector import GazeDetector


def main(stop_event: Optional[Event] = None, thread_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    """
    Defines entry point for the eye tracking application

    Args:
        (Only provided if running as a child thread)
        stop_event: Event to signal stop
        thread_data: Shared data between threads
        data_lock: Lock for shared data

    Returns:
        None
    """

    config = init.init_ptgaze()

    gaze_detector = GazeDetector(config, stop_event, thread_data, data_lock)
    gaze_detector.run()


if __name__ == "__main__":
    main()
