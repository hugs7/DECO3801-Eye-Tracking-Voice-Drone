"""
Flight Statistics definition
"""
from enum import Enum


class FlightStatistics(Enum):
    BATTERY = "battery"
    PITCH = "pitch"
    ROLL = "roll"
    YAW = "yaw"
    SPEED_X = "speed_x"
    SPEED_Y = "speed_y"
    SPEED_Z = "speed_z"
    ACCELERATION_X = "acceleration_x"
    ACCELERATION_Y = "acceleration_y"
    ACCELERATION_Z = "acceleration_z"
    LOWEST_TEMPERATURE = "lowest_temperature"
    HIGHEST_TEMPERATURE = "highest_temperature"
    TEMPERATURE = "temperature"
    HEIGHT = "height"
    DISTANCE_TOF = "distance_tof"
    BAROMETER = "barometer"
    FLIGHT_TIME = "flight_time"
