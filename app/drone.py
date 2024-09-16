"""
Mock drone module
Hugo Burton
06/09/2024
"""

from typing import Optional, Dict
from threading import Event, Lock
from time import sleep

from thread_helper import thread_loop_handler, is_main_thread
from common.logger_helper import init_logger

logger = init_logger()


def loop(thread_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    """
    Drone Loop
    """

    logger.debug(">>> Begin drone loop")
    if not is_main_thread():
        pass
    sleep(1)
    logger.debug("<<< End drone loop")


def main(stop_event: Optional[Event] = None, thread_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
    logger.info("Init drone module")

    while True:
        loop(thread_data, data_lock)
        thread_loop_handler(stop_event)


if __name__ == "__main__":
    main()
