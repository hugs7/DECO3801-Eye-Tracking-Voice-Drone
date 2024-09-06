"""
Mock drone module
Hugo Burton
06/09/2024
"""

from time import sleep
import logging
from typing import Optional
from threading import Event

from thread_helper import thread_exit_handler


def loop():
    # Simulate work
    logging.info(" >>> Begin drone loop")
    sleep(1)
    logging.info(" <<< End drone loop")


def main(stop_event: Optional[Event]):
    logging.info("Init drone module")

    while True:
        loop()
        thread_exit_handler(stop_event)


if __name__ == "__main__":
    main()
