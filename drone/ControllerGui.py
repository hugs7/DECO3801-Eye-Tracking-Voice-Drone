"""
Controller
"""

import time


class Controller:
    def __init__(self, drone):
        self.drone = drone

    def get_frame(self):
        return self.drone.get_frame()


    def handle_input(self, command):
        """Handles the input of a drone from voice, Gaze or manual input
        @Param
        command - String involving either up, down, left, right, forward, backward,
            cw(rotate clockwise), ccw (rotate counter clockwise)
        value - an int of the amount to change the drones direction by, if command is rotational
            use degrees and if a directional value use cm in direction
        """
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
                self.drone.rotate_clockwise(90)
            case "ROTATE CCW":
                # run counter clockwise rotation TODO add function to multiply
                # value by correct amount for rotational movement
                yv = -rotationSpeed
                self.drone.rotate_counter_clockwise(90)
            case "UP":
                # run up directional command with value
                ud = liftSpeed
                self.drone.move_up(50)
            case "DOWN":
                # run down directional command with value
                ud = -liftSpeed
                self.drone.move_down(50)
            case "LEFT":
                # run left directional command with value
                lr = -speed
                self.drone.move_left(50)
            case "RIGHT":
                # run right directional command with value
                lr = speed
                self.drone.move_right(50)
            case "FORWARD":
                # run forward directional command with value
                fb = moveSpeed
                self.drone.move_forward(50)
            case "BACKWARD":
                # run back directional command with value
                fb = -moveSpeed
                self.drone.move_back(50)
            case "TAKEOFF":
                # xtra = 1
                self.drone.takeoff()
            case "LAND":
                # xtra = 2
                self.drone.land()
            case "FLIP FORWARD":
                # xtra = 3
                self.drone.flip_forward()
        # drone.send_rc_control(lr, fb, ud, yv)
        time.sleep(0.1)  # Ensure value is correctly calculated above
        # drone.send_rc_control(0,0,0,0)
