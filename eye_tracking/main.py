"""
Eye tracking driver
02/08/2024
"""

import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import init
import loop
import coordinate


def main():
    landmark_mapping = init.landmark_mapping_init()

    # Initialise variables
    run = True
    window_width = 1280
    window_height = 900
    feed_ratio = window_width / window_height
    upscaled_window_width = 2400
    upscaled_window_height = int(upscaled_window_width / feed_ratio)
    upscaled_dim = coordinate.Coordinate(upscaled_window_width, upscaled_window_height)
    landmark_visibility = init.set_landmark_button_visibility()
    init.window_init(window_width, window_height, landmark_visibility, upscaled_dim)

    cam = init.camera_init()
    face_mesh = init.face_mesh_init()

    while run:
        run = loop.main_loop(cam, face_mesh, landmark_mapping, upscaled_dim, landmark_visibility)

    # Release the resources
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
