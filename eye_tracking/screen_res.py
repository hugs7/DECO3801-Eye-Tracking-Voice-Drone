"""
Screen res
02/08/2024
"""

import cv2
import time
import mediapipe as mp
from cvzone.FaceMeshModule import FaceMeshDetector
from mediapipe.python.solutions.face_mesh import FaceMesh
import landmarks as lm

# Initialize variables
run = True
print_interval = 5  # Time interval in seconds
last_print_time = time.time()

# Initialize video capture and face mesh detector
cam = cv2.VideoCapture(0)
face_mesh = FaceMesh(refine_landmarks=True, max_num_faces=3)
detector = FaceMeshDetector(maxFaces=1)


def normalise_landmark(landmark, frame_w, frame_h):
    x = int(landmark.x * frame_w)
    y = int(landmark.y * frame_h)
    return x, y


def click_event(event, x, y, points, detector):
    if event == cv2.EVENT_LBUTTONDOWN and points:
        lstOfPoints = [detector.findDistance(points, (x, y))[0] for i in range(0, 468)]
        print(lstOfPoints.index(min(lstOfPoints)))


def track_face(img, face):
    for i in range(0, 468):
        cv2.circle(img, (face[i][0], face[i][1]), 1, (0, 255, 0), cv2.FILLED)


def face_detector(frame, windowName):
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


# Set the desired window size
window_width = 1280  # Replace with your desired width
window_height = 900
windowName = "eyetracking"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(windowName, window_width, window_height)

while run:
    success, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    if points:
        landmarks = points[0].landmark
        current_time = time.time()
        last_print_time = current_time

        for id, landmark in enumerate(landmarks):
            x, y = normalise_landmark(landmark, frame_w, frame_h)

            if id in lm.face_landmarks:
                colour = (0, 255, 0)
            else:
                colour = (0, 0, 255)

            cv2.circle(frame, (x, y), 3, colour)
            cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow(windowName, frame)
    cv2.setMouseCallback(windowName, lambda event, x, y, flags, params: click_event(event, x, y, points, detector))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        run = False

# Release the resources
cam.release()
cv2.destroyAllWindows()
