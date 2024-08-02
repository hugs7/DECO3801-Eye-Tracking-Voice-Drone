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
    if event == cv2.EVENT_LBUTTONDOWN and faces:
        for face in faces:
            lstOfPoints = [detector.findDistance(face[i], (x, y))[0] for i in range(0, 468)]
            print(lstOfPoints.index(min(lstOfPoints)))


def track_face(img, face):
    for i in range(0, 468):
        cv2.circle(img, (face[i][0], face[i][1]), 1, (0, 255, 0), cv2.FILLED)


while run:
    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    windowName = "eyetracking"
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

    img, faces = detector.findFaceMesh(frame, draw=False)
    print("Num faces", len(faces))
    if faces:
        for face in faces:
            track_face(img, face)
        cv2.imshow(windowName, img)
        cv2.setMouseCallback(windowName, lambda event, x, y, flags, params: click_event(event, x, y, faces, detector))

    else:
        cv2.imshow(windowName, img)
        cv2.waitKey(1)

    # cv2.imshow(windowName, frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        run = False

# Release the resources
cam.release()
cv2.destroyAllWindows()
