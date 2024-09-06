"""
Mock Eye Tracking module
Hugo Burton
06/09/2024
"""

from time import sleep
import logging


def loop():
    """
    Eye Tracking Loop
    """

    logging.info(" >>> Begin Eye Tracking loop")
    sleep(10)
    logging.info(" <<< End Eye Tracking loop")


def main():
    logging.info("Init eye tracking module")

    while True:
        loop()


if __name__ == "__main__":
    main()
