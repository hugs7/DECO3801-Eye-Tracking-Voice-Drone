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

#Start Connection With Drone
Drone = tello.Tello()
Drone.connect()
def handle_input(input):
    if input == pygame.K_l:
        Drone.land()
        print("I am recognising land")
    if input == pygame.K_SPACE:
        print("I am recognising takeoff")
        Drone.takeoff()

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