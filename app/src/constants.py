"""
Constants for the app
"""

# GUI Constants

WINDOW_TITLE = "Gaze and Voice Aware Drone"

WIN_MIN_WIDTH = 800
WIN_MIN_HEIGHT = 600

BATTERY_WIDGET_WIDTH = 160  # px
FLIGHT_PARAMS_X_PADDING = 10  # px
FLIGHT_STATS_X_PADDING = 120  # px
FLIGHT_STATS_Y_PADDING = 30  # px

# Loading Screen

LOADING_STAGE = "stage"
LOADING_TASK = "task"
LOADING_PROGRESS = "progress"
LOADING_ACTION = "action"
LOADING_CLOSE = "close"

THREAD_DATA = "thread_data"
IPC_DATA = "interprocess_data"
THREADS = "threads"
PROCESSES = "processes"

# === DEFAULT CONFIG ===

DEFAULT_GUI_CONFIG = {
    "timers": {
        "voice_command": 5,
        "webcam": 30,
        "drone_video": 30,
        "battery": 0.2,
    },
    "callback_delays": {
        "voice_command": 5000,
    }
}
