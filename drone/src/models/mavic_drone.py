"""
Defines class for Mavic drone
"""

import cv2
import time
from typing import Any, Optional
from omegaconf import OmegaConf
from pymavlink import mavutil

from common.logger_helper import init_logger

from .. import constants as c

from .drone import Drone

logger = init_logger()


class MavicDrone(Drone):
    """
    Implements a Mavic drone wrapper class
    """
    video_fps = 1
    def __init__(self, mavic_config: OmegaConf):
        """
        Initialises the Mavic drone

        Args:
            mavic_config (OmegaConf): The Mavic config object
        """
        self.config = mavic_config

        self.vehicle = self.connect()
        self.success = self.vehicle is not None
        if not self.success:
            self.success = False
            return

        from dronekit import VehicleMode

        self.VehicleMode = VehicleMode

    def connect(self) -> Optional[Any]:
        """
        Connects to the Mavic drone

        Returns:
            Optional[vehicle]: The vehicle object or None if connection failed
        """
        logger.info("Importing libraries...")
        from dronekit import connect as mavic_connect

        logger.info("Connecting to the Mavic drone...")

        ip = self.config.ip
        port = self.config.port
        logger.info("IP: %s", ip)
        logger.info("Port: %s", port)

        connection_string = f"udp:{ip}:{port}"
        logger.debug("Connecting to mavic on with connection: %s",
                     connection_string)

        try:
            vehicle = mavic_connect(
                connection_string, wait_ready=True, timeout=60)
        except Exception as e:
            logger.error("Failed to connect to Mavic drone")
            logger.error("Details %s", e)
            return

        logger.info("Connected to Mavic!")
        return vehicle

    def read_camera(self) -> cv2.typing.MatLike:
        ok = False
        img = None

        return ok, img

    def __set_vehicle_mode(self, mode: str) -> None:
        """
        Sets the vehicle mode to the specified mode

        Args:
            mode (str): The mode to set the vehicle to
        """

        logger.info("Setting vehicle mode to %s", mode)
        self.vehicle.mode = self.VehicleMode(mode)

    def _is_armable(self) -> bool:
        """
        Checks if the drone is ready to be armed

        Returns:
            bool: True if the drone is armable, False otherwise
        """

        return self.vehicle.is_armable

    def _is_armed(self) -> bool:
        """
        Checks if the drone is armed

        Returns:
            bool: True if the drone is armed, False otherwise
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

    def send_ned_velocity(self, velocity_x, velocity_y, velocity_z, duration, yaw=0) -> None:
        """
        Move vehicle in direction based on specified velocity vectors and
        for the specified duration.

        This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only 
        velocity components 
        (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned).
        
        Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
        with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
        velocity persists until it is canceled. The code below should work on either version 
        (sending the message multiple times does not cause problems).
        
        See the above link for information on the type_mask (0=enable, 1=ignore). 
        At time of writing, acceleration and yaw bits are ignored.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            yaw, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

        # send command to vehicle on 1 Hz cycle
        for x in range(0,duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def rotate_clockwise(self, degrees: int) -> None:
        print("rotating clockwise")
        self.send_ned_velocity(0, 0, 0, 5, yaw=degrees)

        

    def rotate_counter_clockwise(self, degrees: int) -> None:
        print("rotating clockwise")
        self.send_ned_velocity(0, 0, 0, 5, yaw=(-degrees))

    # Could change these units to metres if needed

    def move_up(self, cm = 5) -> None:
        print("moving up")
        self.send_ned_velocity(0, 0, cm, 2)

    def move_down(self, cm = 5) -> None:
        print("moving down")
        self.send_ned_velocity(0, 0, 0 - cm, 2)

    def move_left(self, cm = 5) -> None:
        print("sending move left y axis axis \n")
        self.send_ned_velocity(0 - cm, 0, 0, 2)

    def move_right(self, cm = 5) -> None:
        print("sending move right y axis axis \n")
        self.send_ned_velocity(cm, 0, 0, 2)

    def move_forward(self, cm = 5) -> None:
        """Move vehicle forward
        """
        print("sending move forward x axis \n")
        self.send_ned_velocity(0, 0 - cm, 0, 2)
        
    def move_backward(self, cm = 5) -> None:
        print("sending move backward x axis \n")
        self.send_ned_velocity(0, cm, 0, 2)

    def takeoff(self, target_altitude_metres = 2) -> None:
        """
        Takes off the drone to the specified altitude

        Args:
            target_altitude_metres (int): The target altitude to take off to
        """
        #while not self._is_armed():
        #    logger.info(" Waiting for arming...")
        #    time.sleep(1)

        logger.info("Taking off!")
        self.vehicle.simple_takeoff(target_altitude_metres)

        while True:
            alt = self.get_height()

            logger.info("Drone altitude: %d", alt)
            # Break and return from function just below target altitude.
            if alt >= target_altitude_metres * c.ALTITUDE_THRESHOLD_MULTIPLIER:
                logger.info("Reached altitude: %d of target %d m", alt,
                            target_altitude_metres)
                break
            time.sleep(1)

    def land(self):
        """
        Lands the drone
        """
        logger.info("Landing the drone")
        self.__set_vehicle_mode("LAND")

    def __get_global_relative_frame(self) -> Any:
        """
        Gets the global relative frame of the drone

        Returns:
            global_relative_frame: The global relative frame of the drone
        """
        location = self.vehicle.location
        return location.global_relative_frame

    # Polling methods

    def get_height(self) -> int:
        """
        Gets the altitude of the drone

        Returns:
            altitude: The altitude of the drone
        """
        global_relative_frame = self.__get_global_relative_frame()
        altitude = global_relative_frame.alt
        return altitude
