"""
Mock voice control module
Hugo Burton
06/09/2024
"""

from time import sleep

import logging


def loop():
    # Simulate work
    logging.info(" >>> Begin voice control loop")
    sleep(1)
    logging.info(" <<< End voice control loop")


def main():
    while True:
        loop()


if __name__ == "__main__":
    main()
