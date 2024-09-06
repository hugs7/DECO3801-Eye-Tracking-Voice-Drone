"""
Mock voice control module
Hugo Burton
06/09/2024
"""

from time import sleep
import logging


def loop():
    """
    Voice Control Loop
    """

    logging.info(" >>> Begin voice control loop")
    sleep(10)
    logging.info(" <<< End voice control loop")


def main():
    logging.info("Init voice control module")

    while True:
        loop()


if __name__ == "__main__":
    main()
