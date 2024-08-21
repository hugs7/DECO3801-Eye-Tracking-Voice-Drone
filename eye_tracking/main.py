"""
Eye tracking driver
02/08/2024
"""

import init

from gaze.gaze_detector import GazeDetector


def main():
    """
    Defines entry point for the eye tracking application
    """

    config = init.init_ptgaze()

    gaze_detector = GazeDetector(config)
    gaze_detector.run()


if __name__ == "__main__":
    main()
