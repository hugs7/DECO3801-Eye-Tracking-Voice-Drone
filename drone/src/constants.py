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

# === Drone Stat Params ===

BATTERY = "battery"
PITCH = "pitch"
ROLL = "roll"
YAW = "yaw"
SPEED_X = "speed_x"
SPEED_Y = "speed_y"
SPEED_Z = "speed_z"
ACCELERATION_X = "acceleration_x"
ACCELERATION_Y = "acceleration_y"
CCELERATION_Z = "cceleration_z"
LOWEST_TEMPERATURE = "lowest_temperature"
HIGHEST_TEMPERATURE = "highest_temperature"
TEMPERATURE = "temperature"
HEIGHT = "height"
DISTANCE_TOF = "distance_tof"
BAROMETER = "barometer"
FLIGHT_TIME = "flight_time"

FLIGHT_STATISTICS = [
    # PITCH,
    # ROLL,
    # YAW,
    # SPEED_X,
    # SPEED_Y,
    # SPEED_Z,
    # ACCELERATION_X,
    # ACCELERATION_Y,
    # CCELERATION_Z,
    # LOWEST_TEMPERATURE,
    # HIGHEST_TEMPERATURE,
    # TEMPERATURE,
    # HEIGHT,
    # DISTANCE_TOF,
    # BAROMETER,
    # FLIGHT_TIME,
    # BATTERYsstart,
]

# === Config ===

DEFAULT_CONFIG = {
    "drone_type": "tello",
    "mavic": {
        "ip": "192.168.x.x",
        "port": 14551,
        "connection_timeout": 60,
    },
    "tello": {
        "wifi": {
            "ssid": "TELLO-XXXXX",
            "password": "",
        },
        "poll_response": False,
        "default_speed": 50,
        "video_settings_supported": False,
        "video_bitrate": "auto",
        "video_resolution": "720p",
        "video_fps": 30,
        "camera_selection": "forward",
    },
    "controller": {
        "connect_to_drone": True,
        "max_tick_rate": 30,
        "keyboard_bindings": {
            "land": "l",
            "takeoff": 32,  # Space key
            "up": 16777235,  # Up arrow
            "down": 16777237,  # Down arrow
            "left": "a",
            "right": "d",
            "forward": "w",
            "backward": "s",
            "emergency": 16777223,  # Delete key
            "flip forward": "f",
            "cw": "e",
            "ccw": "q",
            "motor on": "9",
            "motor off": "0",
        },
        "drone_stat_params": {
            BATTERY: 0.2,
        },
    },
}
