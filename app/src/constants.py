"""
Constants for the app
"""

# GUI Constants

WINDOW_TITLE = "Gaze and Voice Aware Drone"

WIN_MIN_WIDTH = 800
WIN_MIN_HEIGHT = 600

WIDGET_PADDING = 10  # px

BATTERY_STATS_WIDGET = "battery_and_stats_widget"
BATTERY_WIDGET_BORDER_COLOUR = "#8f8f8f"
BATTERY_WIDGET_BORDER_WIDTH = 1  # px
BATTERY_WIDGET_BORDER_RADIUS = 5  # px

BATTERY_PROGRESS = "battery_progress"
BATTERY_PROGRESS_BORDER_WIDTH = 1     # px
BATTERY_PROGRESS_WIDTH = 100  # px
BATTERY_PROGRESS_HEIGHT = 20  # px
BATTERY_TEXT_WIDTH = 50  # px
BATTERY_GOOD_CHUNK_COLOUR = "#00ff00"
BATTERY_WARNING_CHUNK_COLOUR = "#ffcc00"
BATTERY_DANGER_CHUNK_COLOUR = "#ff0000"

BATTERY_INDICATOR_COLOLURS = {
    # Lower bound: Colour
    40: BATTERY_GOOD_CHUNK_COLOUR,
    20: BATTERY_WARNING_CHUNK_COLOUR,
    10: BATTERY_DANGER_CHUNK_COLOUR,
}

BATTERY_PROGRESS_BORDER_COLOUR = "#8f8f8f"
BATTERY_PROGRESS_BORDER_WIDTH = 1  # px
BATTERY_PROGRESS_BORDER_RADIUS = 5  # px

FLIGHT_PARAMS_X_PADDING = 10  # px
FLIGHT_STATS_X_MARGIN = 120  # px
FLIGHT_STATS_Y_MARGIN = 50  # px

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
