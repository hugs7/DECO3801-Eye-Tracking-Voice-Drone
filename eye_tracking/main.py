"""
Eye tracking driver
02/08/2024
"""

import init

from gaze.demo import Demo


def main():
    """
    Defines entry point for the eye tracking application
    """

    config = init.init_ptgaze()

    demo = Demo(config)
    demo.run()


if __name__ == "__main__":
    main()
