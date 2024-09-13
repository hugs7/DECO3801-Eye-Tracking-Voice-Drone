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
        self.connect()

        # Start Camera Display Stream
        self.drone.streamon()
        self.drone.set_speed(c.TELLO_SPEED_CM_S)

        print("Drone battery:", self.drone.get_battery())

    def connect(self) -> None:
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
    
    def rotate_clockwise(self, degrees: int) -> None:
        """
        Rotates the drone clockwise by the specified number of degrees
        """
        self.drone.rotate_clockwise(degrees)

    def rotate_counter_clockwise(self, degrees: int) -> None:
        """
        Rotates the drone counter-clockwise by the specified number of degrees
        """
        self.drone.rotate_counter_clockwise(degrees)

    def move_up(self, cm: int) -> None:
        """
        Moves the drone up by the specified number of cm
        """
        self.drone.move_up(cm)

    def move_down(self, cm: int) -> None:
        """
        Moves the drone down by the specified number of cm
        """
        self.drone.move_down(cm)

    def move_left(self, cm: int) -> None:
        """
        Moves the drone left by the specified number of cm
        """
        self.drone.move_left(cm)

    def move_right(self, cm: int) -> None:
        """
        Moves the drone right by the specified number of cm
        """
        self.drone.move_right(cm)

    def move_forward(self, cm: int) -> None:
        """
        Moves the drone forward by the specified number of cm
        """
        self.drone.move_forward(cm)

    def move_backward(self, cm: int) -> None:
        """
        Moves the drone backward by the specified number of cm
        """
        self.drone.move_back(cm)

    def takeoff(self) -> None:
        """
        Takes off the drone
        """
        self.drone.takeoff()

    def land(self) -> None:
        """
        Lands the drone
        """
        self.drone.land()

    def get_altitude(self) -> int:
        """
        Gets the current altitude of the drone
        :return: Altitude in cm
        """
        pass
        # return self.drone.get_height()

    def flip_forward(self) -> None:
        self.drone.flip_forward()
