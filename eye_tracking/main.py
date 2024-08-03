"""
Eye tracking driver
02/08/2024
"""

import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import init
import loop


def main():
    landmark_mapping = init.landmark_mapping_init()

    # Initialise variables
    run = True
    calibrated = False
    window_width = 1280
    window_height = 900

    init.window_init(window_width, window_height)

    cam = init.camera_init()
    face_mesh = init.face_mesh_init()

    while run:
        run, calibrated = loop.main_loop(calibrated, cam, face_mesh, landmark_mapping)

    # Release the resources
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
