"""
Defines class for Tello drone
"""

from drone_model import Drone
from djitellopy import tello
import cv2

import constants as c


class TelloDrone(Drone):
    def __init__(self) -> None:
        tello_drone = tello.Tello()
        self.drone = tello_drone
        self.__connect()

        # Start Camera Display Stream
        self.drone.streamon()
        self.drone.set_speed(c.TELLO_SPEED_CM_S)

        print("Drone battery:", self.drone.get_battery())

    def __connect(self) -> None:
        """
        Connects to the drone
        """

        self.drone.connect()

    def read_camera(self) -> cv2.typing.MatLike:
        """
        Reads the camera feed from the drone
        :return: img - the image from the camera feed
        """

        frame_read = self.drone.get_frame_read()
        img = frame_read.frame

        return img
