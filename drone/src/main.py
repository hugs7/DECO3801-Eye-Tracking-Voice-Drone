"""
Main file for the drone
"""

import os
import sys

from PyQt6.QtWidgets import QApplication

# Add the project root to the path. Must execute prior to user imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print("Project root: ", project_root)
sys.path.insert(0, project_root)

from .controller import Controller
from .gui import DroneApp
from . import init


def main():
    drone_config = init.init()
    controller = None

    if not drone_config.gui_only:
        drone = init.init_drone(drone_config)
        if drone.success:
            controller = Controller(drone)

    gui = QApplication(sys.argv)
    drone_window = DroneApp(controller)
    drone_window.show()
    gui.exec()


if __name__ == "__main__":
    main()
