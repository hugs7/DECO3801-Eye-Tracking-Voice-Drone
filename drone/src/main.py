"""
Main file for the drone
"""

import os
import sys
from typing import Optional, Dict
from threading import Event, Lock

from PyQt6.QtWidgets import QApplication

# Add the project root to the path. Must execute prior to user imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print("Project root: ", project_root)
sys.path.insert(0, project_root)

from .controller import Controller
from .gui import DroneApp
from . import init


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
    controller = None

    if not drone_config.gui_only:
        drone = init.init_drone(drone_config)
        if drone.success:
            controller = Controller(drone, drone_config.controller, stop_event, thread_data, data_lock)

    running_in_thread = thread_data is not None
    if not running_in_thread:
        gui = QApplication(sys.argv)
        drone_window = DroneApp(controller)
        drone_window.show()
        gui.exec()


if __name__ == "__main__":
    main()
