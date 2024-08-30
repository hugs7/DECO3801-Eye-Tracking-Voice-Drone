"""
Main file for the drone
"""

from typing import Union
import cv2

import constants as c

import controller
import mavic
import tello


def loop(drone):
    """
    Defines main loop for the drone
    """

    controller.handle_input(drone)

    img = read_camera_feed(drone)
    render_drone_feed(img)

    cv2.waitKey(1)


def read_camera_feed(drone: Union[mavic.MavicDrone, tello.TelloDrone]):
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
    Initialiees the drone
    """

    if drone_type == c.MAVIC:
        vehicle = mavic.MavicDrone(c.MAVIC_IP, c.MAVIC_PORT)
    elif drone_type == c.TELLO:
        vehicle = tello.TelloDrone()

    return vehicle


def main():
    drone_type = c.TELLO  # / c.MAVIC

    drone = init(drone_type)

    while True:
        loop(drone)


if __name__ == "__main__":
    main()
