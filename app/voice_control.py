"""
Mock voice control module
Hugo Burton
06/09/2024
"""

from typing import Optional, Dict
from threading import Event, Lock
from time import sleep

from thread_helper import thread_exit_handler
from logger_helper import init_logger

logger = init_logger()


def loop():
    """
    Voice Control Loop
    """

    logger.debug(">>> Begin voice control loop")
    sleep(0.9)
    logger.debug("<<< End voice control loop")


def main(stop_event: Optional[Event] = None, shared_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    logger.info("Init voice control module")

    while True:
        loop()
        thread_exit_handler(stop_event)


if __name__ == "__main__":
    main()
