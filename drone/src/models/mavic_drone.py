"""
Defines class for Mavic drone
"""

from dronekit import connect, VehicleMode
import cv2
import time
from omegaconf import OmegaConf

from common.logger_helper import init_logger

from .. import constants as c

from .drone import Drone

logger = init_logger()


class MavicDrone(Drone):
    def __init__(self, mavic_config: OmegaConf):
        """
        Initialises the Mavic drone

        Args:
            mavic_config (OmegaConf): The Mavic config object
        """
        self.config = mavic_config

        self.vehicle = self.connect()

    def connect(self):
        """
        Connects to the Mavic drone

        Returns:
            vehicle: The vehicle object
        """
        logger.info("Connecting to the Mavic drone...")

        ip = self.config.ip
        port = self.config.port
        logger.info("IP: %s", ip)
        logger.info("Port: %s", port)

        connection_string = f"udp:{ip}:{port}"
        logger.debug(f"Connecting to mavic on with connection: %s", connection_string)

        try:
            vehicle = connect(connection_string, wait_ready=True, timeout=60)
            vehicle = None
        except Exception as e:
            logger.error("Failed to connect to Mavic drone")
            logger.error("Details %s", e)
            exit(1)

        logger.info("Connected to Mavic!")
        return vehicle

    def read_camera(self) -> cv2.typing.MatLike:
        """
        TODO: Read the camera feed from the mavic drone
        """

        img = None

        return img

    def __set_vehicle_mode(self, mode: str) -> None:
        # self.vehicle.mode = VehicleMode(mode)
        self.vehicle.mode = None

    def _is_armable(self) -> bool:
        """
        Checks if the drone is ready to be armed
        """

        return self.vehicle.is_armable

    def _is_armed(self) -> bool:
        """
        Checks if the drone is armed
        :return: True if the drone is armed, False otherwise
        """
        return self.vehicle.armed

    def arm(self) -> None:
        """
        Arms the drone for flight. User is not allowed to fly the drone until it is armed
        Cannot arm until the drone's autopilot is ready.
        """
        logger.info("Performing basic pre-arm checks")
        while not self._is_armable():
            logger.info(" Waiting for vehicle to initialise...")
            time.sleep(1)

        logger.info("Arming motors")
        self.__set_vehicle_mode("GUIDED")
        self.vehicle.armed = True

    def rotate_clockwise(self, degrees: int) -> None:
        raise NotImplementedError

    def rotate_counter_clockwise(self, degrees: int) -> None:
        raise NotImplementedError

    # Could change these units to metres if needed

    def move_up(self, cm: int) -> None:
        raise NotImplementedError

    def move_down(self, cm: int) -> None:
        raise NotImplementedError

    def move_left(self, cm: int) -> None:
        raise NotImplementedError

    def move_right(self, cm: int) -> None:
        raise NotImplementedError

    def move_forward(self, cm: int) -> None:
        raise NotImplementedError

    def move_backward(self, cm: int) -> None:
        raise NotImplementedError

    def takeoff(self, target_altitude_metres: int) -> None:
        """
        Takes off the drone to the specified altitude
        :param target_altitude_metres: The target altitude in metres
        :return: None
        """
        while not self._is_armed():
            logger.info(" Waiting for arming...")
            time.sleep(1)

        logger.info("Taking off!")
        self.vehicle.simple_takeoff(target_altitude_metres)

        while True:
            logger.info(f"Drone altitude: {self.get_altitude()}")

            # Break and return from function just below target altitude.
            alt = self.get_altitude()
            if alt >= target_altitude_metres * c.ALTITUDE_THRESHOLD_MULTIPLIER:
                logger.info(f"Reached altitude: {alt} (of target {target_altitude_metres} m)")
                break
            time.sleep(1)

    def land(self):
        self.__set_vehicle_mode("LAND")

    def __get_global_relative_frame(self):
        location = self.vehicle.location
        return location.global_relative_frame

    # Polling methods

    def get_altitude(self) -> int:
        """
        Gets the altitude of the drone
        :return: The altitude of the drone
        """
        global_relative_frame = self.__get_global_relative_frame()
        altitude = global_relative_frame.alt
        return altitude
