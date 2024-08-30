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

    def getKey(self, command):
        key_mapping = {
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_w: "FORWARD",
            pygame.K_s: "BACKWARD",
            pygame.K_l: "LAND",
            pygame.K_SPACE: "TAKEOFF",
            pygame.K_q: "ROTATE CW",
            pygame.K_e: "ROTATE CCW",
            pygame.K_z: "FLIP FORWARD",
        }
        if command in key_mapping:
            return key_mapping[command]

    def is_armable(self):
        return self.vehicle.is_armable

    def is_armed(self):
        return self.vehicle.armed

    def arm(self):
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not self.is_armable():
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

    def takeoff(self, aTargetAltitude, vehicle):
        while not self.is_armed():
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
