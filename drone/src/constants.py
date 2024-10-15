"""
Constants file. Please define in UPPER_SNAKE_CASE
"""

from .drone_actions import DroneActions

# === Drone Types ===
MAVIC = "mavic"
TELLO = "tello"
DRONE_TYPES = [MAVIC, TELLO]

# === Rendered Window ===
WINDOW_NAME = "Drone Capture"

# === Drone Controlling ===
ALTITUDE_THRESHOLD_MULTIPLIER = 0.95

# === Tello ===
TELLO_SPEED_CM_S = 100

# === Mavic ===


# Drone Local GUI

WIN_MIN_WIDTH = 800
WIN_MIN_HEIGHT = 600


# === Drone Actions ===

DRONE_MOVEMENT_ACTIONS = [
    DroneActions.UP,
    DroneActions.DOWN,
    DroneActions.LEFT,
    DroneActions.RIGHT,
    DroneActions.FORWARD,
    DroneActions.BACKWARD,
]

DRONE_ROTATION_ACTIONS = [
    DroneActions.ROTATE_CCW,
    DroneActions.ROTATE_CW,
]

DRONE_ACTIONS_OTHER = [
    DroneActions.TAKEOFF,
    DroneActions.LAND,
    DroneActions.EMERGENCY,
    DroneActions.MOTOR_OFF,
    DroneActions.MOTOR_ON,
    DroneActions.SPEED,
]
