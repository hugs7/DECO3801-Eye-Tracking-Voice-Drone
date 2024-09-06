"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union, Optional
import pygame
import time
import models

CONTROLLER_MAPPING = {
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_w: "FORWARD",
    pygame.K_s: "BACKWARD",
    pygame.K_l: "LAND",
    pygame.K_SPACE: "TAKEOFF",
    pygame.K_q: "ROTATE CW",
    pygame.K_e: "ROTATE CCW",
    pygame.K_z: "FLIP FORWARD",
}


def get_key_input() -> Optional[int]:
    """
    Returns a key pressed by the user in the terminal
    :return: The key pressed by the user or None if no key was pressed in the delay cycle
    """
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            return event.key


def get_to_command(key: int) -> Optional[str]:
    """
    Takes a key and returns the command associated with it according to the CONTROLLER_MAPPING
    :param key: The key to get the command for
    :return: The command associated with the key or None if the key is not in the CONTROLLER_MAPPING
    """
    if key in CONTROLLER_MAPPING:
        return CONTROLLER_MAPPING[key]


def handle_input(drone: Union[models.TelloDrone, models.MavicDrone], command: str) -> None:
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
    sysCom = get_to_command(command)
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
            drone.takeoff()
        case "LAND":
            # xtra = 2
            drone.land()
        case "FLIP FORWARD":
            # xtra = 3
            drone.flip_forward()
    # drone.send_rc_control(lr, fb, ud, yv)
    time.sleep(0.1)  # Ensure value is correctly calculated above
    # drone.send_rc_control(0,0,0,0)
