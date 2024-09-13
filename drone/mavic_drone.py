"""
Defines class for Mavic drone
"""

from dronekit import connect, VehicleMode

import constants as c
from abs_drone import AbstractDrone
import cv2
import time
from pymavlink import mavutil
import socket

class MavicDrone(AbstractDrone):
    def __init__(self) -> NotImplementedError:
        ip = self.fetch_ip()
        self.vehicle = self.__connect(ip, c.MAVIC_PORT)
    def fetch_ip(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    def __connect(self, ip, port):
        connection_string = f"{ip}:{port}"
        print(f"Connecting to mavic on: {connection_string}")

        # Try connecting with a longer timeout
        try:
            vehicle = connect(connection_string, wait_ready=True, timeout=60)
            print("Connected to vehicle!")
            self.arm()
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
        #while not self._is_armable():
        #    print(" Waiting for vehicle to initialise...")
        #    time.sleep(1)

        print("Arming motors")
        self.__set_vehicle_mode("GUIDED")
        self.vehicle.armed = True
    
    def send_ned_velocity(self, velocity_x, velocity_y, velocity_z, duration) -> None:
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
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

        # send command to vehicle on 1 Hz cycle
        for x in range(0,duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(1)

    def rotate_clockwise(self, degrees: int) -> None:
        raise NotImplementedError

    def rotate_counter_clockwise(self, degrees: int) -> None:
        raise NotImplementedError

    # Could change these units to metres if needed

    def move_up(self, cm: int) -> None:
        print("moving up")
        self.send_ned_velocity(0, 0, 1, 2)

    def move_down(self, cm: int) -> None:
        print("moving down")
        self.send_ned_velocity(0, 0, -1, 2)

    def move_left(self, cm: int) -> None:
        print("sending move left y axis axis \n")
        self.send_ned_velocity(-1, 0, 0, 2)

    def move_right(self, cm: int) -> None:
        print("sending move right y axis axis \n")
        self.send_ned_velocity(1, 0, 0, 2)

    def move_forward(self, cm: int) -> None:
        """Move vehicle forward
        """
        print("sending move forward x axis \n")
        self.send_ned_velocity(0, -1, 0, 2)
        return
    def move_back(self, cm: int) -> None:
        print("sending move back x axis axis \n")
        self.send_ned_velocity(0, 1, 0, 2)

    def takeoff(self, target_altitude_metres: int) -> None:
        """
        Takes off the drone to the specified altitude
        :param target_altitude_metres: The target altitude in metres
        :return: None
        """
        while not self._is_armed():
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(target_altitude_metres)
        
        while True:
            print(f"Drone altitude: {self.get_altitude()}")

            # Break and return from function just below target altitude.
            alt = self.get_altitude()
            if alt >= target_altitude_metres * c.ALTITUDE_THRESHOLD_MULTIPLIER:
                print(f"Reached altitude: {alt} (of target {target_altitude_metres} m)")
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
