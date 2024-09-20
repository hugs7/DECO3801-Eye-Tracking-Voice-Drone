"""
Defines class for Tello drone
"""

from datetime import datetime
from typing import Any

import cv2
from djitellopy import tello
from djitellopy.tello import Tello
from omegaconf import OmegaConf

from common.logger_helper import init_logger

from .drone import Drone

logger = init_logger()

MIN_SPEED = 10
MAX_SPEED = 100
DEFAULT_SPEED = 50

MIN_VIDEO_BITRATE = 1
MAX_VIDEO_BITRATE = 5

DEFAULT_FPS = 30


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
        tello_drone = Tello()
        self.drone = tello_drone
        self.success = self.connect()
        if not self.success:
            return

        self.__init_config(tello_config)
        self.__init_drone_params()

        self.last_command_time = datetime.now()
        self.in_flight = False

        logger.info("TelloDrone initialised.")

    def __init_config(self, tello_config: OmegaConf) -> None:
        """
        Initialises class variables from the Tello configuration

        Args:
            tello_config (OmegaConf): The Tello config object
        """

        self.config = tello_config

        self.poll_response = self.config.poll_response

    def __init_drone_params(self) -> None:
        """
        Initialises the drone parameters
        """

        self.drone.streamon()

        logger.debug("Initialising drone speed...")
        config_speed = self.config.default_speed
        if config_speed in range(MIN_SPEED, MAX_SPEED + 1):
            tello_speed = config_speed
            logger.debug("Setting drone speed to %s cm/s", tello_speed)
        else:
            tello_speed = DEFAULT_SPEED
            logger.warning("Invalid speed '%s' cm/s. Defaulting to %d cm/s", config_speed, tello_speed)

        self.drone.set_speed(tello_speed)

        logger.debug("Initialising video bitrate")
        config_video_bitrate = self.config.video_bitrate
        if config_video_bitrate == "auto":
            tello_video_bitrate = Tello.BITRATE_AUTO
        elif config_video_bitrate in range(MIN_VIDEO_BITRATE, MAX_VIDEO_BITRATE + 1):
            tello_video_bitrate = eval(f"Tello.BITRATE_{config_video_bitrate}")
            logger.debug("Setting video bitrate to %s", tello_video_bitrate)
        else:
            logger.warning("Invalid video bitrate '%s'. Defaulting to auto", config_video_bitrate)
            tello_video_bitrate = Tello.BITRATE_AUTO

        try:
            self.drone.set_video_bitrate(tello_video_bitrate)
        except tello.TelloException as e:
            logger.error("Failed to set video bitrate. Details: %s", e)

        logger.debug("Initialising video resolution...")
        config_res = self.config.video_resolution
        match config_res:
            case "480p":
                tello_res = Tello.RESOLUTION_480P
            case "720p":
                tello_res = Tello.RESOLUTION_720P
            case _:
                logger.warning("Invalid video resolution '%s'. Defaulting to 720p", config_res)
                tello_res = Tello.RESOLUTION_720P

        try:
            self.drone.set_video_resolution(tello_res)
        except tello.TelloException as e:
            logger.error("Failed to set video resolution. Details: %s", e)

        logger.debug("Initialising video fps...")
        config_fps = int(self.config.video_fps)
        match config_fps:
            case 5:
                tello_fps = Tello.FPS_5
            case 15:
                tello_fps = Tello.FPS_15
            case 30:
                tello_fps = Tello.FPS_30
            case _:
                logger.warning("Invalid video fps '%s'. Defaulting to %d", config_fps, DEFAULT_FPS)
                tello_fps = Tello.FPS_30
                config_fps = DEFAULT_FPS

        try:
            self.drone.set_video_fps(tello_fps)
        except tello.TelloException as e:
            logger.error("Failed to set video fps. Details: %s", e)

        self.video_fps = config_fps

        # Forward-facing 10080x720p colour camera or 320x240 greyscale
        # IR down-facing camera
        logger.debug("Initialising camera selection...")
        config_camera = self.config.camera_selection
        match config_camera:
            case "forward":
                camera_selection = Tello.CAMERA_FORWARD
            case "downward":
                camera_selection = Tello.CAMERA_DOWNWARD
            case _:
                logger.warning("Invalid camera selection '%s'. Defaulting to forward", config_camera)
                camera_selection = Tello.CAMERA_FORWARD

        try:
            self.drone.set_video_direction(camera_selection)
        except tello.TelloException as e:
            logger.error("Failed to set camera selection. Details: %s", e)

    def connect(self) -> bool:
        """
        Connects to the drone

        Returns:
            bool: True if the drone connected successfully, False otherwise
        """

        logger.info("Connecting to the Tello Drone...")

        try:
            self.drone.connect()
        except tello.TelloException as e:
            logger.error("There was an issue connecting to the drone. Check you are on the correct WiFi network.")
            logger.error("Details %s", e)
            return False

        logger.info("Connected to the Tello Drone")
        logger.info("Drone battery: %d", self.drone.get_battery())
        return True

    def read_camera(self) -> cv2.typing.MatLike:
        """
        Reads the camera feed from the drone

        Returns:
            img - the image from the camera feed
        """

        frame_read = self.drone.get_frame_read()
        img = frame_read.frame

        return img

    def _send_command(self, command):
        """
        Sends a command to the drone, either with or without a return
        depending on config.
        """

        if self.poll_response:
            self.drone.send_control_command(command)
        else:
            if not self.__has_waited_between_commands():
                logger.info("Wait before sending command")
                return

            self.drone.send_command_without_return(command)

    def rotate_clockwise(self, degrees: int) -> None:
        command = "cw {}".format(degrees)
        self._send_command(command)

    def rotate_counter_clockwise(self, degrees: int) -> None:
        command = "ccw {}".format(degrees)
        self._send_command(command)

    def move_up(self, cm: int) -> None:
        command = "up {}".format(cm)
        self._send_command(command)

    def move_down(self, cm: int) -> None:
        command = "down {}".format(cm)
        self._send_command(command)

    def move_left(self, cm: int) -> None:
        command = "left {}".format(cm)
        self._send_command(command)

    def move_right(self, cm: int) -> None:
        command = "right {}".format(cm)
        self._send_command(command)

    def move_forward(self, cm: int) -> None:
        command = "forward {}".format(cm)
        self._send_command(command)

    def move_backward(self, cm: int) -> None:
        command = "back {}".format(cm)
        self._send_command(command)

    def takeoff(self) -> None:
        command = "takeoff"
        self._send_command(command)
        self.in_flight = True

    def land(self) -> None:
        command = "land"
        self._send_command(command)
        self.in_flight = False

    def flip_forward(self) -> None:
        command = "flip f"
        self._send_command(command)

    def emergency(self) -> None:
        command = "emergency"
        self._send_command(command)
        self.in_flight = False

    def motor_on(self) -> None:
        self.drone.turn_motor_on()

    def motor_off(self) -> None:
        self.drone.turn_motor_off()

    def __getattribute__(self, name: str) -> Any:
        if name != "drone" and name in self.drone.__dict__:
            return getattr(self.drone, name)

        return super().__getattribute__(name)

    def get_height(self) -> int:
        # Must exist as is defined as an abstract method in Drone
        return self.drone.get_height()

    def __has_waited_between_commands(self) -> bool:
        """
        Checks if the time between commands is greater than the minimum time between commands
        :return: True if the time between commands is greater than the minimum time between commands
        """
        time_diff = datetime.now() - self.last_command_time
        return time_diff.total_seconds() >= self.drone.TIME_BTW_COMMANDS
