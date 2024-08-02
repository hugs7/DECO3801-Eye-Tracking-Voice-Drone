import cv2
import time
import mediapipe as mp
from mediapipe.python.solutions.face_mesh import FaceMesh
import landmarks as lm

# Initialize variables
run = True
calibrated = False
reference_positions = {"left": {}, "right": {}}
window_width = 1280  # Replace with your desired width
window_height = 900
windowName = "eyetracking"
print_interval = 5  # Time interval in seconds
last_print_time = time.time()

# Initialize video capture and face mesh detector
cam = cv2.VideoCapture(0)
face_mesh = FaceMesh(refine_landmarks=True, max_num_faces=1)


def normalise_landmark(landmark, frame_w, frame_h):
    x = int(landmark.x * frame_w)
    y = int(landmark.y * frame_h)
    return x, y


def calibrate_eye_positions(landmarks, frame_w, frame_h):
    for eye in ["left", "right"]:
        for pos in ["top", "bottom", "left", "right"]:
            x, y = normalise_landmark(landmarks[lm.eye_landmarks[eye][pos]], frame_w, frame_h)
            reference_positions[eye][pos] = (x, y)


def track_eye_movement(landmarks, frame_w, frame_h):
    for eye in ["left", "right"]:
        iris_x, iris_y = normalise_landmark(landmarks[lm.eye_landmarks[eye]["top"]], frame_w, frame_h)
        ref_x, ref_y = reference_positions[eye]["top"]

        dx = iris_x - ref_x
        dy = iris_y - ref_y

        # Overlay a dot corresponding to the eye movement
        overlay_x = frame_w // 2 + dx * 5  # Adjust the multiplier as needed
        overlay_y = frame_h // 2 + dy * 5  # Adjust the multiplier as needed
        cv2.circle(frame, (overlay_x, overlay_y), 5, (255, 0, 0), cv2.FILLED)


# Set the desired window size
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

        if not calibrated:
            cv2.putText(
                frame,
                "Look at the camera and press Enter to calibrate",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        for id, landmark in enumerate(landmarks):
            x, y = normalise_landmark(landmark, frame_w, frame_h)

            if id in lm.face_landmarks:
                colour = (0, 255, 0)
            else:
                colour = (0, 0, 255)

            cv2.circle(frame, (x, y), 3, colour)
            cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

        if calibrated:
            track_eye_movement(landmarks, frame_w, frame_h)

    cv2.imshow(windowName, frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        run = False
    elif key == ord("\r"):  # Enter key to calibrate
        if points:
            calibrate_eye_positions(landmarks, frame_w, frame_h)
            calibrated = True

# Release the resources
cam.release()
cv2.destroyAllWindows()
