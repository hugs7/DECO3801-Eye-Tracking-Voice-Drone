"""
Main file for the drone
"""

from typing import Union
import cv2
import tkinter as tk

import constants as c
from controller import Controller
import models
from gui import DroneApp
import init


def loop(drone, controller):
    """
    Defines main loop for the drone
    """
    
    controller.handle_input(drone)

    img = read_camera_feed(drone)
    render_drone_feed(img)

    cv2.waitKey(1)


def read_camera_feed(drone: Union[models.MavicDrone, models.TelloDrone]):
    """
    Reads the camera feed from the drone
    """

    output_dim = (960, 720)

    img = drone.read_camera()
    img = drone.resize_frame(img, output_dim)


def render_drone_feed(img: cv2.typing.MatLike) -> None:
    """
    Renders the drone feed
    """

    cv2.imshow(c.WINDOW_NAME, img)


def init(drone_type):
    """
    Initialies the drone
    """

    match drone_type:
        case c.MAVIC:
            vehicle = models.MavicDrone(c.MAVIC_IP, c.MAVIC_PORT)
        case c.TELLO:
            vehicle = models.TelloDrone()
        case _:
            raise ValueError(f"Invalid drone type: {drone_type}")

    controller = Controller(vehicle)

    return controller


def main():
    drone_type = c.TELLO  # / c.MAVIC

    controller = init(drone_type)

    root = tk.Tk()
    DroneApp(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
