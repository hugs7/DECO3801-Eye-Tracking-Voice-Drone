"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread
import logging

if __name__ == "__main__":
    from eye_tracking import main as eye_tracking_loop
    from voice_control import main as voice_control_loop
    from drone import main as drone_loop
else:
    from .eye_tracking import main as eye_tracking_loop
    from .voice_control import main as voice_control_loop
    from .drone import main as drone_loop


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(" >>> Begin")
    print("Welcome to mock drone controller!")

    # Create threads for each of the components
    threads = [
        Thread(target=eye_tracking_loop),
        Thread(target=voice_control_loop),
        Thread(target=drone_loop),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    logging.info(" <<< End")


if __name__ == "__main__":
    main()
