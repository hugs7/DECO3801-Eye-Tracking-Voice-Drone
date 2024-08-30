"""
Defines class for Mavic drone
"""

from ..drone import Drone
from dronekit import connect, VehicleMode
import cv2
import time
import pygame


class MavicDrone(Drone):
    def __init__(self, ip: str, port: int) -> NotImplementedError:
        self.vehicle = self.__connect(ip, port)

    def __connect(self, ip, port):
        connection_string = f"udp:{ip}:{port}"
        print(f"Connecting to mavic on: {connection_string}")

        # Try connecting with a longer timeout
        try:
            vehicle = connect(connection_string, wait_ready=True, timeout=60)
            print("Connected to vehicle!")
        except Exception as e:
            print(f"Failed to connect: {e}")
            exit(1)

        return vehicle

    def read_camera(self) -> cv2.typing.MatLike:
        """
        TODO: Read the camera feed from the mavic drone
        """

        img = None

        return img

    def __set_vehicle_mode(self, mode: str) -> None:
        self.vehicle.mode = VehicleMode(mode)

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
        print("Performing basic pre-arm checks")
        while not self._is_armable():
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
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

            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        # vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Check that vehicle has reached takeoff altitude
        while True:
            print(" Altitude: "), vehicle.location.global_relative_frame.alt
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

    def land(self):
        self.__set_vehicle_mode("LAND")

    def __set_vehicle_mode(self, mode: str) -> None:
        self.vehicle.mode = VehicleMode(mode)

