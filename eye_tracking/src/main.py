"""
Entry point for the eye tracking driver
Author: Hugo Burton
Last Updated: 21/08/2024
"""

import init
from typing import Optional, Dict
from threading import Event, Lock

from gaze_detector import GazeDetector


def main(stop_event: Optional[Event] = None, shared_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    """
    Defines entry point for the eye tracking application
    """

    config = init.init_ptgaze()

    gaze_detector = GazeDetector(config)
    gaze_detector.run(shared_data, data_lock)


if __name__ == "__main__":
    main()
