"""
Eye tracking driver
02/08/2024
"""

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures_v2

# Initialize gesture engine and video capture
gestures = EyeGestures_v2()
cap = VideoCapture(0)  
calibrate = True
screen_width = 500
screen_height= 500

# Process each frame
while True:
  ret, frame = cap.read()
  event, cevent = gestures.step(frame, calibrate, screen_width, screen_height)
  
  cursor_x, cursor_y = event.point[0], event.point[1]
  # calibration_radius: radius for data collection during calibration