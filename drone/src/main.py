"""
Main file for the drone
"""

from typing import Union
import os
import sys

import cv2
from PyQt6.QtWidgets import QApplication

# Add the project root to the path. Must execute prior to user imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print("Project root: ", project_root)
sys.path.insert(0, project_root)

from . import constants as c
from .controller import Controller
from . import models
from .gui import DroneApp
from . import init


def loop(drone: Union[models.MavicDrone, models.TelloDrone], controller: Controller) -> None:
    """
    Defines main loop for the drone

    Args:
        drone: The drone object
        controller: The controller object
    """

    controller.perform_command(drone)

    img = read_camera_feed(drone)
    render_drone_feed(img)

    cv2.waitKey(1)


def read_camera_feed(drone: Union[models.MavicDrone, models.TelloDrone]) -> None:
    """
    Reads the camera feed from the drone

    Args:
        drone (Union[models.MavicDrone, models.TelloDrone]): The drone object
    """

    output_dim = (960, 720)

    img = drone.read_camera()
    img = cv2.resize(img, output_dim)


def render_drone_feed(img: cv2.typing.MatLike) -> None:
    """
    Renders the drone feed

    Args:
        img: The image to render
    """

    cv2.imshow(c.WINDOW_NAME, img)


def main():
    drone_config = init.init()
    drone = init.init_drone(drone_config)
    if drone.success:
        controller = Controller(drone)

    gui = QApplication(sys.argv)
    drone_window = DroneApp(controller)
    drone_window.show()
    gui.exec()


if __name__ == "__main__":
    main()
