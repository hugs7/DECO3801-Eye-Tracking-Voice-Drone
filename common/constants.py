"""
Common constants used in the project
"""

# Keyboard constants

ESC_KEY_CODE = 27
QUIT_KEYS = {chr(ESC_KEY_CODE)}


# Time constants

MILLISECONDS_PER_SECOND = 1000

# Process handling

PROCESS_TIMEOUT = 3  # seconds

# Threads

THREAD_CALLBACK = "callback"
THREAD_FPS = "fps"

# Modules

VOICE_CONTROL = "voice_control"
DRONE = "drone"
EYE_TRACKING = "eye_tracking"

# Keyboard

KEYBOARD_QUEUE = "keyboard_queue"
COMMAND_QUEUE = "command_queue"

# Video

VIDEO_FRAME = "video_frame"
TICK_RATE = "tick_rate"

# Eye Tracking
LEFT = "left"
RIGHT = "right"
SIDES = [LEFT, RIGHT]
GAZE_OVERLAY = "gaze_overlay"
GAZE_SIDE = "gaze_side"

# Voice Control
COMMAND_TEXT = "text"
PARSED_COMMAND = "parsed_command"

# GUI

DARK_THEME = "dark"
LIGHT_THEME = "light"

TEXT_WHITE = "white"
TEXT_BLACK = "black"

# Drone

FLIGHT_STATISTICS = "flight_statistics"
BATTERY = "battery"
