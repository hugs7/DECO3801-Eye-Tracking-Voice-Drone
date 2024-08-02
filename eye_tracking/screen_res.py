"""
Screen res
02/08/2024
"""

import cv2

cam = cv2.VideoCapture(0)
run = True


while run:
    _, frame = cam.read()

    cv2.imshow("Eye Tracking", frame)
    cv2.waitKey(1)
