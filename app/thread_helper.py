"""
Helps with child threads
"""

from typing import Optional
from threading import Event

import logging


def thread_exit_handler(stop_event: Optional[Event]) -> None:
    """
    Helper function to handle stop event in threads.
    :param stop_event: Event to signal stop
    :return: None
    """
    if stop_event is None:
        # Module is running independently (main thread)
        return

    # Module is running as a child thread
    if stop_event.is_set():
        logging.info("Received stop signal. Exiting thread...")
        raise SystemExit
