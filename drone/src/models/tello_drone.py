"""
Defines class for Tello drone
"""

from datetime import datetime
from typing import Any

import cv2
from djitellopy import tello
from omegaconf import OmegaConf

from common.logger_helper import init_logger

from .. import constants as c

from .drone import Drone

logger = init_logger()


class TelloDrone(Drone):
    """
    Implements a Tello drone wrapper class
    """

    def __init__(self, tello_config: OmegaConf) -> None:
        """
        Initialises the Tello drone

        Args:
            tello_config (OmegaConf): The Tello config object
        """

        logger.info("Initialising TelloDrone...")
        self.config = tello_config

        tello_drone = tello.Tello()
        self.drone = tello_drone
        self.connect()
        self.polling_flag = False

        # Start Camera Display Stream
        self.drone.streamon()
        self.drone.set_speed(c.TELLO_SPEED_CM_S)

        self.last_command_time = datetime.now()

        logger.info("Drone battery: %d", self.drone.get_battery())

    def connect(self) -> None:
        """
        Connects to the drone
        """

        logger.info("Connecting to the Tello Drone...")

        try:
            self.drone.connect()
        except tello.TelloException as e:
            logger.error("There was an issue connecting to the drone. Check you are on the correct WiFi network.")
            logger.error("Details %s", e)

        logger.info("Connected to the Tello Drone")

    def read_camera(self) -> cv2.typing.MatLike:
        """
        Reads the camera feed from the drone

        Returns:
            img - the image from the camera feed
        """

        frame_read = self.drone.get_frame_read()
        img = frame_read.frame

        return img

    def send_info(self, command):
        """
        Override for
        """

        if self.polling_flag:
            self.drone.send_control_command(command)
        else:
            if not self.__has_waited_between_commands():
                logger.info("Wait before sending command")
                return

            self.drone.send_command_without_return(command)

    def rotate_clockwise(self, degrees: int) -> None:
        command = "cw {}".format(degrees)
        self.send_info(command)

    def rotate_counter_clockwise(self, degrees: int) -> None:
        command = "ccw {}".format(degrees)
        self.send_info(command)

    def move_up(self, cm: int) -> None:
        command = "up {}".format(cm)
        self.send_info(command)

    def move_down(self, cm: int) -> None:
        command = "down {}".format(cm)
        self.send_info(command)

    def move_left(self, cm: int) -> None:
        command = "left {}".format(cm)
        self.send_info(command)

    def move_right(self, cm: int) -> None:
        command = "right {}".format(cm)
        self.send_info(command)

    def move_forward(self, cm: int) -> None:
        command = "forward {}".format(cm)
        self.send_info(command)

    def move_backward(self, cm: int) -> None:
        command = "back {}".format(cm)
        self.send_info(command)

    def takeoff(self) -> None:
        command = "takeoff"
        self.send_info(command)

    def land(self) -> None:
        command = "land"
        self.send_info(command)

    def flip_forward(self) -> None:
        command = "flip f"
        self.send_info(command)

    def __getattribute__(self, name: str) -> Any:
        """
        Returns attributes from the drone object. Usefulf for drone polling methods.
        E.g. drone.get_height()
        """
        if name in Drone.__dict__:
            # Use local method if it exists
            return super().__getattribute__(name)

        # Look for attribute in drone object
        return getattr(self.drone, name)

    def __has_waited_between_commands(self) -> bool:
        """
        Checks if the time between commands is greater than the minimum time between commands
        :return: True if the time between commands is greater than the minimum time between commands
        """
        time_diff = datetime.now() - self.last_command_time
        return time_diff.total_seconds() >= self.drone.TIME_BTW_COMMANDS
