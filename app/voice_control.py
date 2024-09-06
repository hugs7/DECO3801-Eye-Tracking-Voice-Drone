"""
Mock voice control module
Hugo Burton
06/09/2024
"""

from time import sleep
import logging
from typing import Optional
from threading import Event
from thread_helper import thread_event_handler


def loop():
    """
    Voice Control Loop
    """

    logging.info(" >>> Begin voice control loop")
    sleep(10)
    logging.info(" <<< End voice control loop")


def main(stop_event: Optional[Event]):
    logging.info("Init voice control module")

    while True:
        loop()
        thread_event_handler(stop_event)


if __name__ == "__main__":
    main()
