#import module for tello:
from djitellopy import tello
import pygame
#import module for time:
import time

#import the previous keyboard input module file from the first step:
import KeyboardTelloModule as kp

#import opencv python module:
import cv2
#Global Variable
global img

#Initialize Keyboard Input
kp.init()
def getKey():
    key_mapping = {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        "w": pygame.K_w,
        "s": pygame.K_s,
        "d": pygame.K_d,
        "a": pygame.K_a,
        "q": pygame.K_q,
        "e": pygame.K_e,
        "z": pygame.K_z
    }
#Start Connection With Drone
Drone = tello.Tello()
Drone.connect()
def handle_input(input):
    if input == pygame.K_l:
        Drone.land()
        print("I am recognising land")
    elif input == pygame.K_SPACE:
        print("I am recognising takeoff")
        Drone.takeoff()
    elif input == pygame.K_w:
        #Recognised W key press
        print("I am recognising Forward")
        Drone.move_forward(20)
    elif input == pygame.K_s:
        #recognised S key press
        print("I am recognising Back")
        Drone.move_back(20)
    elif input == pygame.K_a:
        Drone.move_left(20)
    elif input == pygame.K_d:
        Drone.move_right(20)
    elif input == pygame.K_LEFT:
        print("I am recognising left turn")
        Drone.rotate_counter_clockwise(10)
    elif input == pygame.K_RIGHT:
        print("I am recognising Right turn")
        Drone.rotate_clockwise(10)
    elif input == pygame.K_UP:
        print("I am recognising Up")
        Drone.move_up(20)
    elif input == pygame.K_DOWN:
        print("I am recognising Down")
        Drone.move_down(20)


#Get Battery Info
print(Drone.get_battery())

#Start Camera Display Stream
Drone.streamon()
while True:
#Get The Return Value And Stored It On Variable:
    keyValues = kp.getKey() #Get The Return Value And Stored It On Variable
    handle_input(keyValues)
#Control The Drone:
#Get Frame From Drone Camera Camera 
    img = Drone.get_frame_read().frame
    img = cv2.resize(img, (1080,720))
#Show The Frame
    cv2.imshow("DroneCapture", img)
    cv2.waitKey(1)