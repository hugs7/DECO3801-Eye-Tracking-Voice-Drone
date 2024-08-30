"""
Camera Module For Tello Drone
"""

from djitellopy import tello
import cv2


def read_camera(drone: tello.Tello) -> cv2.typing.MatLike:

    img = drone.get_frame_read().frame
    return img
