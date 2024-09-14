"""
Helps with child threads
"""

from typing import Optional
from threading import Event, current_thread

import logging

logger = logging.getLogger(__name__)


def is_main_thread() -> bool:
    """
    Checks if the current thread is the main thread
    :return: True if the current thread is the main thread, False otherwise
    """
    return current_thread().name == "MainThread"


def thread_exit_handler(stop_event: Optional[Event]) -> None:
    """
    Helper function to handle stop event in threads.
    :param stop_event: Event to signal stop

    Returns:
        None
    """
    if stop_event is None:
        # Module is running independently (main thread)
        return

    # Module is running as a child thread
    if stop_event.is_set():
        thread = current_thread()
        logger.critical(
            f"Received stop signal from '{thread.name}'. Exiting thread...")
        raise SystemExit


def get_function_name(func) -> str:
    """
    Inspects the func to get the function's name
    :param func: Function to inspect
    :return: Function name
    """
    return func.__name__


def get_function_module(func) -> str:
    """
    Inspects the func to get the function's module
    :param func: Function to inspect
    :return: Module name
    """
    return func.__module__
