"""
Eye tracking driver
02/08/2024
"""

import cv2

import init
import loop


def main():
    """
    Defines entry point for the eye tracking application
    """

    landmark_mapping = init.init_landmark_mapping()

    # Initialise variables
    run = True
    cam = init.camera_init()

    window_width = 1280
    window_height = 900

    frame_dim = init.init_window(window_width, window_height, landmark_visibility)

    landmark_visibility = init.init_landmark_visibility()
    face_mesh = init.init_face_mesh()

    while run:
        run = loop.main_loop(cam, face_mesh, landmark_mapping, frame_dim, landmark_visibility)

    # Clean up
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
