"""
Controller for options in the cv2 window
"""

from typing import Dict
import cv2

import draw


def mouse_callback(event, x, y, flag, params):
    landmark_visibility = params["landmark_visibility"]
    upscaled_dim = params["upscaled_dim"]
    if event == cv2.EVENT_LBUTTONDOWN:
        button_positions = draw.calculate_button_positions(upscaled_dim, landmark_visibility)
        for part, (top_left, bottom_right) in button_positions.items():
            if top_left[0] <= x <= bottom_right[0] and top_left[1] <= y <= bottom_right[1]:
                toggle_landmark_part(part, landmark_visibility)


def toggle_landmark_part(part, landmark_visibility: Dict[str, bool]):
    landmark_visibility[part] = not landmark_visibility[part]
    print(f"Toggled {part} to {landmark_visibility[part]}")
