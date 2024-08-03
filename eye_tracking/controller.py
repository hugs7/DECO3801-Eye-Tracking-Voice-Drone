"""
Controller for options in the cv2 window
"""

from typing import Dict, List
import cv2

import draw
import loop
import calibrate

from custom_types.NormalisedLandmark import NormalisedLandmark


def mouse_callback(event, x, y, flag, params) -> None:
    """
    Callback for mouse events occurring in the window
    :param event: The event
    :param x: The x coordinate
    :param y: The y coordinate
    :param flag: The flag
    :param params: The parameters
    :return None
    """

    landmark_visibility = params["landmark_visibility"]
    upscaled_dim = params["upscaled_dim"]
    if event == cv2.EVENT_LBUTTONDOWN:
        button_positions = draw.calculate_button_positions(upscaled_dim, landmark_visibility)
        for part, (top_left, bottom_right) in button_positions.items():
            if top_left[0] <= x <= bottom_right[0] and top_left[1] <= y <= bottom_right[1]:
                toggle_landmark_part(part, landmark_visibility)


def toggle_landmark_part(part, landmark_visibility: Dict[str, bool]) -> None:
    """
    Toggles the visibility of a landmark part
    :param part: The part to toggle
    :param landmark_visibility: The visibility of the landmarks
    :return None
    """
    landmark_visibility[part] = not landmark_visibility[part]
    print(f"Toggled {part} to {landmark_visibility[part]}")


def handle_loop_key_events(landmark_mapping, frame_dim, loop_data: loop.LoopData, points) -> bool:
    """
    Handles key events in the loop
    :param landmark_mapping: The landmark mapping
    :param frame_dim: The frame dimensions
    :param loop_data: The loop data
    :param points: The points
    :return: Whether to continue running
    """
    run = True
    key = cv2.waitKey(1) & 0xFF
    if is_key_event(key, "q"):
        run = False
    elif is_key_event(key, "c"):
        # 'c' to begin calibration
        calibration_data = calibrate.calibrate_init(landmark_mapping, frame_dim)
        print("initiating calibration", calibration_data)
        loop_data["calibration_data"] = calibration_data
        loop_data["calibrating"] = True
    elif is_key_event(key, "l"):
        # 'l' to toggle landmarks
        toggle_setting("show_landmarks", loop_data)
    elif is_key_event(key, "o"):
        # 'o' to toggle options
        toggle_setting("show_settings", loop_data)

    return run


def toggle_setting(setting_key: str, loop_data: loop.LoopData) -> None:
    """
    Toggles a setting in the loop data
    :param setting_key: The setting key to toggle
    :param loop_data: The loop data
    :return: None
    """

    loop_data[setting_key] = not loop_data[setting_key]
    print(f"Toggled {setting_key} to {loop_data[setting_key]}")


def is_key_event(key: int, key_binding: str) -> bool:
    """
    Checks if the event is a key event
    :param key: The key event to check
    :param key_binding: The key binding to trigger the event
    :return: Whether the event is a key event
    """
    return key == ord(key_binding)
