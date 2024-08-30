"""
Defines class for Tello drone
"""

from ..drone import Drone
from djitellopy import tello
import cv2
import KeyboardTelloModule as kp

import constants as c


class TelloDrone(Drone):
    def __init__(self) -> None:
        tello_drone = tello.Tello()
        tello_drone.connect()

        # Start Camera Display Stream
        tello_drone.streamon()
        tello_drone.set_speed(c.TELLO_SPEED_CM_S)

        self.drone = tello_drone

        print("Drone battery:", tello_drone.get_battery())

        # Initialize Keyboard Input
        kp.init()
        return tello_drone

    def read_camera(self) -> cv2.typing.MatLike:
        """
        Reads the camera feed from the drone
        :return: img - the image from the camera feed
        """

        frame_read = self.drone.get_frame_read()
        img = frame_read.frame
        return img