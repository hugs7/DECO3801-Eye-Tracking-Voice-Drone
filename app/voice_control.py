"""
Mock voice control module
Hugo Burton
06/09/2024
"""

from time import sleep
import logging
from typing import Optional, Dict
from threading import Event, Lock
from thread_helper import thread_exit_handler


def loop():
    """
    Voice Control Loop
    """

    logging.info(" >>> Begin voice control loop")
    sleep(0.9)
    logging.info(" <<< End voice control loop")


def main(stop_event: Optional[Event] = None, shared_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    logging.info("Init voice control module")

    while True:
        loop()
        thread_exit_handler(stop_event)


if __name__ == "__main__":
    main()
