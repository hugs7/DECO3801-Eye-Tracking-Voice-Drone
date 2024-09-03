from djitellopy import tello
import cv2

class TelloModel:
    def __init__(self):
        self.drone = tello.Tello()
        self.drone.connect()
        self.drone.streamon()

    def get_frame(self):
        frame = self.tello.get_frame_read().frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame