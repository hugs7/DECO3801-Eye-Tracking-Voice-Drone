"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union

import pygame

from .models.tello_drone import TelloDrone
from .models.mavic_drone import MavicDrone


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

KEY_MAPPING = {
    "Left": "LEFT",
    "Right": "RIGHT",
    "Up": "UP",
    "Down": "DOWN",
    "w": "FORWARD",
    "s": "BACKWARD",
    "l": "LAND",
    "space": "TAKEOFF",
    "q": "ROTATE CW",
    "e": "ROTATE CCW",
    "z": "FLIP FORWARD",
}


class Controller:
    """
    Controller for the drone, handles the input of a drone from voice, Gaze or manual input
    """

    def __init__(self, drone: Union[TelloDrone, MavicDrone]):
        """
        Initialises the drone controller

        Args:
            drone [Union[TelloDrone, MavicDrone]]: The drone to control.
        """

        self.model = drone

    def perform_command(self, command: str):
        """
        Handler for sending an action to the drone given a command.

        Args:
            command (str): The command to send to the drone.
        command - String involving either up, down, left, right, forward, backward,
            cw(rotate clockwise), ccw (rotate counter clockwise)
        value - an int of the amount to change the drones direction by, if command is rotational
            use degrees and if a directional value use cm in direction
        """
        if command not in KEY_MAPPING:
            return
        command = KEY_MAPPING[command]
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 10
        liftSpeed = 10
        moveSpeed = 10
        rotationSpeed = 10
        print(command)

        match command:
            case "ROTATE CW":
                # run clockwise rotation TODO add function to multiply
                # value by correct amount for rotational movement
                yv = rotationSpeed
                self.model.rotate_clockwise(90)
            case "ROTATE CCW":
                # run counter clockwise rotation TODO add function to multiply
                # value by correct amount for rotational movement
                yv = -rotationSpeed
                self.model.rotate_counter_clockwise(90)
            case "UP":
                # run up directional command with value
                ud = liftSpeed
                self.model.move_up(50)
            case "DOWN":
                # run down directional command with value
                ud = -liftSpeed
                self.model.move_down(50)
            case "LEFT":
                # run left directional command with value
                lr = -speed
                self.model.move_left(50)
            case "RIGHT":
                # run right directional command with value
                lr = speed
                self.model.move_right(50)
            case "FORWARD":
                # run forward directional command with value
                fb = moveSpeed
                self.model.move_forward(50)
            case "BACKWARD":
                # run back directional command with value
                fb = -moveSpeed
                self.model.move_backward(50)
            case "TAKEOFF":
                # xtra = 1
                self.model.takeoff()
            case "LAND":
                # xtra = 2
                self.model.land()
            case "FLIP FORWARD":
                # xtra = 3
                self.model.flip_forward()
