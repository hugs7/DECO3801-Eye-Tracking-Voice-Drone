"""
Tell Connect Module
"""

from djitellopy import tello
import KeyboardTelloModule as kp


def tello_connect() -> tello.Tello:
    # Start Connection With Drone
    drone = tello.Tello()
    drone.connect()

    # Start Camera Display Stream
    drone.streamon()
    drone.set_speed(100)

    print("Drone battery:", drone.get_battery())

    return drone


def init():
    # Initialize Keyboard Input
    kp.init()
