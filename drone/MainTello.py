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

import CommandHandling as com

def main():
#Get The Return Value And Stored It On Variable:
    keyValues = kp.getKey() #Get The Return Value And Stored It On Variable
    if keyValues == pygame.K_ESCAPE:
        exit(0)
    com.handle_input(Drone, keyValues)
#Control The Drone:
#Get Frame From Drone Camera Camera 
    img = Drone.get_frame_read().frame
    img = cv2.resize(img, (1080,720))
#Show The Frame
    cv2.imshow("DroneCapture", img)
    cv2.waitKey(1)

if __name__ == '__main__':
    #Initialize Keyboard Input
    kp.init()
    
    #Start Connection With Drone
    Drone = tello.Tello()
    Drone.connect()

    #Get Battery Info
    print(Drone.get_battery())

    #Start Camera Display Stream
    Drone.streamon()
    Drone.set_speed(100)
    while True:
        main()
