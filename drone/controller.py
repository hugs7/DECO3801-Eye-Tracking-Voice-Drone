"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union
import pygame
import time
import mavic_drone
import tello_drone

CONTROLLER_MAPPING = {
    81: "LEFT",         # ASCII for Left Arrow in OpenCV (cv2.waitKey())
    83: "RIGHT",        # ASCII for Right Arrow in OpenCV (cv2.waitKey())
    82: "UP",           # ASCII for Up Arrow in OpenCV (cv2.waitKey())
    84: "DOWN",         # ASCII for Down Arrow in OpenCV (cv2.waitKey())
    ord('w'): "FORWARD", # ASCII for 'w'
    ord('s'): "BACKWARD",# ASCII for 's'
    ord('l'): "LAND",    # ASCII for 'l'
    ord(' '): "TAKEOFF", # ASCII for space bar
    ord('q'): "ROTATE CW",# ASCII for 'q'
    ord('e'): "ROTATE CCW",# ASCII for 'e'
    ord('z'): "FLIP FORWARD",# ASCII for 'z'
}

def get_key(command):
    print(command)
    if command in CONTROLLER_MAPPING:
        return CONTROLLER_MAPPING[command]


def handle_input(drone: Union[tello_drone.TelloDrone, mavic_drone.MavicDrone], command) -> None:
    """
    Handles the input of a drone from voice, Gaze or manual input
    :param drone: The drone object to control
    :param command: String involving either up, down, left, right, forward, backward,
        cw(rotate clockwise), ccw (rotate counter clockwise)
    value - an int of the amount to change the drones direction by, if command is rotational
        use degrees and if a directional value use cm in direction
    """
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 10
    liftSpeed = 10
    moveSpeed = 10
    rotationSpeed = 10
    sysCom = get_key(command)
    print(sysCom)

    match sysCom:
        case "ROTATE CW":
            # run clockwise rotation TODO add function to multiply
            # value by correct amount for rotational movement
            yv = rotationSpeed
            drone.rotate_clockwise(90)
        case "ROTATE CCW":
            # run counter clockwise rotation TODO add function to multiply
            # value by correct amount for rotational movement
            yv = -rotationSpeed
            drone.rotate_counter_clockwise(90)
        case "UP":
            # run up directional command with value
            ud = liftSpeed
            drone.move_up(50)
        case "DOWN":
            # run down directional command with value
            ud = -liftSpeed
            drone.move_down(50)
        case "LEFT":
            # run left directional command with value
            lr = -speed
            drone.move_left(50)
        case "RIGHT":
            # run right directional command with value
            lr = speed
            drone.move_right(50)
        case "FORWARD":
            # run forward directional command with value
            fb = moveSpeed
            drone.move_forward(50)
        case "BACKWARD":
            # run back directional command with value
            fb = -moveSpeed
            drone.move_back(50)
        case "TAKEOFF":
            # xtra = 1
            drone.takeoff(2)
        case "LAND":
            # xtra = 2
            drone.land()
        case "FLIP FORWARD":
            # xtra = 3
            drone.flip_forward()
    # drone.send_rc_control(lr, fb, ud, yv)
    time.sleep(0.1)  # Ensure value is correctly calculated above
    # drone.send_rc_control(0,0,0,0)
