from dronekit import connect, VehicleMode
import time
import pygame
import KeyboardTelloModule as kp


def arm_and_takeoff(aTargetAltitude, vehicle):

    print ("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print (" Waiting for vehicle to initialise...")
        time.sleep(1)
        
    print ("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    while not vehicle.armed:
        print (" Waiting for arming...")
        time.sleep(1)

    print ("Taking off!")
    #vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Check that vehicle has reached takeoff altitude
    while True:
        print (" Altitude: "), vehicle.location.global_relative_frame.alt 
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
            print ("Reached target altitude")
            break
        time.sleep(1)

def getKey(command, vehicle):
    if command == pygame.K_SPACE:
        # Initialize the takeoff sequence to 20m
        print("Taking off..")

        arm_and_takeoff(1, vehicle)

        print("Take off complete")

            # Hover for 10 seconds
        time.sleep(10)

        print("Now let's land")
        vehicle.mode = VehicleMode("LAND")
    """key_mapping = {
        pygame.K_LEFT : "LEFT",
        pygame.K_RIGHT : "RIGHT",
        pygame.K_UP : "UP",
        pygame.K_DOWN : "DOWN",
        pygame.K_w : "FORWARD",
        pygame.K_s : "BACKWARD",
        pygame.K_l : "LAND",
        pygame.K_SPACE : "TAKEOFF",
        pygame.K_q : "ROTATE CW",
        pygame.K_e : "ROTATE CCW",
        pygame.K_z : "FLIP FORWARD"
    }
    if command in key_mapping:
        return key_mapping[command]"""

def main():
    # Replace 'YOUR_PHONE_IP' with the actual IP address of your phone
    kp.init()
    connection_string = 'udp:192.168.69.244:14551'

    print(f"Connecting to vehicle on: {connection_string}")

    # Try connecting with a longer timeout
    try:
        vehicle = connect(connection_string, wait_ready=True, timeout=60)
        print("Connected to vehicle!")
    except Exception as e:
        print(f"Failed to connect: {e}")
    keyValues = kp.getKey() #Get The Return Value And Stored It On Variable
    if keyValues == pygame.K_ESCAPE:
        exit(0)

if __name__ == '__main__':
    while True:
        main()

# Close vehicle object
#vehicle.close()
"""import cv2
import socket

# The local IP address and port of the video stream
video_stream_ip = '0.0.0.0'
video_stream_port = 5600

# Create a video stream URL
video_stream_url = f'http://{video_stream_ip}:{video_stream_port}'

# Open the video stream using OpenCV
cap = cv2.VideoCapture(video_stream_url)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

print("Video stream opened successfully.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Failed to grab frame.")
        break
    
    # Display the resulting frame
    cv2.imshow('Video Stream', frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture and close windows
cap.release()"""
