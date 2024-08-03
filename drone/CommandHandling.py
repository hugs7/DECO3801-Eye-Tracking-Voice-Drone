import djitellopy as Drone
import KeyboardTelloModule as kp
import cv2
import time
tello = Drone.Tello()

def handle_input(command, value):
    """Handles the input of a drone from voice, Gaze or manual input
    @Param
    command - String involving either up, down, left, right, forward, backward,
        cw(rotate clockwise), ccw (rotate counter clockwise)
    value - an int of the amount to change the drones direction by, if command is rotational
        use degrees and if a directional value use cm in direction
    """
    lr, fb, ud, yv = 0,0,0,0
    speed = 80 
    liftSpeed = 80
    moveSpeed = 85
    rotationSpeed = 100
    match command:
        case "cw":
            #run clockwise rotation TODO add function to multiply
            #value by correct amount for rotational movement
            yv = rotationSpeed
        case "ccw":
            #run counter clockwise rotation TODO add function to multiply
            #value by correct amount for rotational movement
            yv = -rotationSpeed
        case "up":
            #run up directional command with value
            ud = liftSpeed
        case "down":
            #run down directional command with value
            ud = -liftSpeed
        case "left":
            #run left directional command with value
            lr = -speed
        case "right":
            #run right directional command with value
            lr = speed
        case "forward":
            #run forward directional command with value
            fb = moveSpeed
        case "back":
            #run back directional command with value
            fb = -moveSpeed
    tello.send_rc_control(lr, fb, ud, yv)
    time.sleep(value) #Ensure value is correctly calculated above
    tello.send_rc_control(0,0,0,0)


