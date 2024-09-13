"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union, Optional
import pygame
import time
import cv2

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
    def __init__(self, droneModel):
        self.model = droneModel

    def get_frame(self):
        frame = self.model.read_camera()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    


    def handle_input(self, command):
        """Handles the input of a drone from voice, Gaze or manual input
        @Param
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
                self.model.drone.rotate_clockwise(90)
            case "ROTATE CCW":
                # run counter clockwise rotation TODO add function to multiply
                # value by correct amount for rotational movement
                yv = -rotationSpeed
                self.model.drone.rotate_counter_clockwise(90)
            case "UP":
                # run up directional command with value
                ud = liftSpeed
                self.model.drone.move_up(50)
            case "DOWN":
                # run down directional command with value
                ud = -liftSpeed
                self.model.drone.move_down(50)
            case "LEFT":
                # run left directional command with value
                lr = -speed
                self.model.drone.move_left(50)
            case "RIGHT":
                # run right directional command with value
                lr = speed
                self.model.drone.move_right(50)
            case "FORWARD":
                # run forward directional command with value
                fb = moveSpeed
                self.model.drone.move_forward(50)
            case "BACKWARD":
                # run back directional command with value
                fb = -moveSpeed
                self.model.drone.move_back(50)
            case "TAKEOFF":
                # xtra = 1
                self.model.drone.takeoff()
            case "LAND":
                # xtra = 2
                self.model.drone.land()
            case "FLIP FORWARD":
                # xtra = 3
                self.model.drone.flip_forward()
        # drone.send_rc_control(lr, fb, ud, yv)
        time.sleep(0.1)  # Ensure value is correctly calculated above
        # drone.send_rc_control(0,0,0,0)
