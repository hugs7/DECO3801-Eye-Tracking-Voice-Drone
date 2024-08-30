"""
Main file for the drone
"""

from typing import Union
import cv2

import constants as c

import controller
import mavic_drone
import tello_drone


def loop(drone):
    """
    Defines main loop for the drone
    """

    controller.handle_input(drone)

    img = read_camera_feed(drone)

    render_drone_feed(img)

    cv2.waitKey(1)


def read_camera_feed(drone: Union[mavic_drone.Drone, tello_drone.Tello], drone_type: str):
    """
    Reads the camera feed from the drone
    """

    output_dim = (960, 720)

    if drone_type == c.MAVIC:
        img = mavic_drone.read_camera(drone)
    elif drone_type == c.TELLO:
        img = tello_drone.read_camera(drone)

    img = cv2.resize(img, output_dim)
    return img


def render_drone_feed(img: cv2.typing.MatLike):
    """
    Renders the drone feed
    """

    cv2.imshow(c.WINDOW_NAME, img)


def drone_connect(drone_type: str):
    """
    Connects to the drone
    """

    if drone_type == c.MAVIC:
        drone = mavic_drone.mavic_connect()
    elif drone_type == c.TELLO:
        drone = tello_drone.tello_connect()

    return drone


def init(drone_type):
    """
    Initialiees the drone
    """

    drone = drone_connect(drone_type)
    if drone_type == c.MAVIC:
        pass
    elif drone_type == c.TELLO:
        tello_drone.init()

    return drone


def main():
    drone_type = c.TELLO  # / c.MAVIC

    drone = init(drone_type)

    while True:
        loop(drone)


if __name__ == "__main__":
    main()
