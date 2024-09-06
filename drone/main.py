"""
Main file for the drone
"""

from typing import Union
import cv2

import constants as c
import controller
import models
import init


def loop(drone):
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


def main():
    config = init.init()
    drone = init.init_drone(config)

    while True:
        loop(drone)


if __name__ == "__main__":
    main()
