"""
Module to draw on the screen
"""

import cv2

import landmarks
from colours import ColourMap as CM


def draw_landmarks(frame, face_landmarks: landmarks.Landmarks, frame_w, frame_h) -> None:
    """
    Draws the landmarks on the frame
    :param frame: The frame to draw the landmarks on
    :param landmark_mapping: The mapping of landmarks
    :param frame_w: The width of the frame
    :param frame_h: The height of the frame
    :return: None
    """

    for id, landmark in enumerate(face_landmarks):
        x, y = landmarks.normalise_landmark(landmark, frame_w, frame_h)

        point_class_label = face_landmarks.classify_point(id)
        point_class = face_landmarks.landmark_mapping.get(point_class_label, None)
        if point_class_label is not None:
            if "colour" in point_class:
                colour = point_class["colour"]
            else:
                print(f"Point class {point_class} does not have a colour")
        else:
            if id in face_landmarks.face_landmarks:
                colour = (0, 255, 0)
            else:
                colour = (0, 0, 255)

        cv2.circle(frame, (x, y), 3, colour)
        cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, CM.white, 1, cv2.LINE_AA)
