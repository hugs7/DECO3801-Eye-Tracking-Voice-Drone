"""
Screen res
02/08/2024
"""

import cv2
import time
import pyautogui
import mediapipe as mp
from cvzone.FaceMeshModule import FaceMeshDetector

# Initialize variables
run = True
print_interval = 5  # Time interval in seconds
last_print_time = time.time()

# Initialize video capture and face mesh detector
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
detector = FaceMeshDetector(maxFaces=1)


def normalise_landmark(landmark, frame_w, frame_h):
    x = int(landmark.x * frame_w)
    y = int(landmark.y * frame_h)
    return x, y


def click_event(event, x, y, faces, detector):
    if event == cv2.EVENT_LBUTTONDOWN and faces[0]:
        lstOfPoints = [detector.findDistance(faces[0][i], (x, y))[0] for i in range(0, 468)]
        print(lstOfPoints.index(min(lstOfPoints)))


while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    # if points:
    #     landmarks = points[0].landmark
    #     current_time = time.time()
    #     # if current_time - last_print_time > print_interval:
    #     last_print_time = current_time
    #     # print(type(landmarks))
    #     for id, landmark in enumerate(landmarks[400:]):
    #         x, y = normalise_landmark(landmark, frame_w, frame_h)
    #         cv2.circle(frame, (x, y), 3, (0, 255, 0))
    #         print(x, y)
    #         # if id == 1:
    #         #     pyautogui.moveTo(x, y)

    if cam.get(cv2.CAP_PROP_POS_FRAMES) == cam.get(cv2.CAP_PROP_FRAME_COUNT):
        cam.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cam.read()
    img, faces = detector.findFaceMesh(img, draw=False)
    if faces:
        face = faces[0]
        for i in range(0, 468):
            cv2.circle(img, (face[i][0], face[i][1]), 1, (0, 255, 0), cv2.FILLED)
        cv2.imshow("Image", img)
        cv2.setMouseCallback("Image", lambda event, x, y, flags, params: click_event(event, x, y, faces, detector))
        cv2.waitKey(1)
    else:
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    cv2.imshow("Eye Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the resources
cam.release()
cv2.destroyAllWindows()
