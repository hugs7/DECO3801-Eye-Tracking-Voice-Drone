"""
Mock Eye Tracking module
Hugo Burton
06/09/2024
"""

from typing import Optional
from threading import Event
import logging
from time import sleep

from thread_helper import thread_exit_handler


def loop():
    """
    Eye Tracking Loop
    """

    logging.info(" >>> Begin Eye Tracking loop")
    sleep(10)
    logging.info(" <<< End Eye Tracking loop")


def main(stop_event: Optional[Event]):
    logging.info("Init eye tracking module")

    while True:
        loop()
        thread_exit_handler(stop_event)


if __name__ == "__main__":
    main()
