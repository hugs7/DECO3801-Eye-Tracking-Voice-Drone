"""
Drone actions definition
"""
from enum import Enum


class DroneActions(Enum):
    TAKEOFF = "takeoff"
    LAND = "land"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACKWARD = "backward"
    ROTATE_CW = "cw"
    ROTATE_CCW = "ccw"
    FLIP_FORWARD = "flip forward"
    SPEED = "speed"
    EMERGENCY = "emergency"
    MOTOR_ON = "motor on"
    MOTOR_OFF = "motor off"
