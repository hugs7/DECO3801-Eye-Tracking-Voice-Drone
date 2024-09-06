"""
Mock drone module
Hugo Burton
06/09/2024
"""

from time import sleep

import logging


def loop():
    # Simulate work
    logging.info(" >>> Begin drone loop")
    sleep(1)
    logging.info(" <<< End drone loop")


def main():
    logging.info("Init drone module")

    while True:
        loop()


if __name__ == "__main__":
    main()
