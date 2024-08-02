"""
Screen res
02/08/2024
"""

import cv2
import time
import mediapipe as mp

# Initialize variables
run = True
print_interval = 5  # Time interval in seconds
last_print_time = time.time()

# Initialize video capture and face mesh detector
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh()


def normalise_landmark(landmark, frame_w, frame_h):
    x = int(landmark.x * frame_w)
    y = int(landmark.y * frame_h)
    return x, y


while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    if points:
        landmarks = points[0].landmark
        current_time = time.time()
        if current_time - last_print_time > print_interval:
            last_print_time = current_time
            print(landmarks)
            for landmark in landmarks:
                x, y = normalise_landmark(landmark, frame_w, frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                # print(x, y)

    cv2.imshow("Eye Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the resources
cam.release()
cv2.destroyAllWindows()
