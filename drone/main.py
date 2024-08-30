"""
Main file for the drone
"""

from typing import Union
import pygame

import controller
import mavic_drone
import tello_drone


def loop(drone):
    """
    Defines main loop for the drone
    """

    controller.handle_input(drone)


def drone_connect(drone_type: str):
    """
    Connects to the drone
    """

    if drone_type == "mavic":
        drone = mavic_drone.mavic_connect()
    elif drone_type == "tello":
        drone = tello_drone.tello_connect()

    return drone


def init(drone_type):
    """
    Initialiees the drone
    """

    drone = drone_connect(drone_type)
    if drone_type == "mavic":
        pass
    elif drone_type == "tello":
        tello_drone.init()

    return drone


def main():
    drone_type = "tello"  # "mavic"

    drone = init(drone_type)

    while True:
        loop(drone)


if __name__ == "__main__":
    main()
