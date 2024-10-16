"""
Main file for the drone
"""

import os
import sys
from typing import Optional, Dict
from threading import Event, Lock


# Add the project root to the path. Must execute prior to user imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print("Project root: ", project_root)
sys.path.insert(0, project_root)

from common.logger_helper import init_logger

from .controller import Controller

from . import init

logger = init_logger()


def main(stop_event: Optional[Event] = None, thread_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    """
    Defines entry point for the drone module

    Args:
        (Only provided if running as a child thread)
        stop_event: Event to signal stop
        thread_data: Shared data between threads
        data_lock: Lock for shared data
    """
    drone_config = init.init()
    drone = init.init_drone(drone_config, stop_event)

    controller = Controller(drone, drone_config.controller, stop_event, thread_data, data_lock)
    controller.run()


if __name__ == "__main__":
    main()
