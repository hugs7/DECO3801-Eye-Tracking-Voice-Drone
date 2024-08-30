"""
Tell Connect Module
"""

from djitellopy import tello
import KeyboardTelloModule as kp


def tello_connect() -> tello.Tello:
    # Start Connection With Drone
    Drone = tello.Tello()
    Drone.connect()

    return Drone


def init():
    # Initialize Keyboard Input
    kp.init()
