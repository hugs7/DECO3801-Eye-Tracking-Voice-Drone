"""
Helps with child threads
"""

from typing import Optional
from threading import Event, current_thread

from .logger_helper import init_logger

logger = init_logger()


def is_main_thread() -> bool:
    """
    Checks if the current thread is the main thread

    Returns:
        True if the current thread is the main thread, False otherwise
    """
    return current_thread().name == "MainThread"


def thread_loop_handler(stop_event: Optional[Event]) -> None:
    """
    Helper function to handle stop event in threads. Tells the interpreter
    to exit the thread loop if the stop event is set.

    Args:
        stop_event: Event to signal stop

    Returns:
        None
    """
    if stop_event is None:
        # Module is running independently (main thread)
        return

    # Module is running as a child thread
    if stop_event.is_set():
        thread = current_thread()
        logger.critical(f"Received stop signal from '{thread.name}'. Exiting thread...")
        raise SystemExit


def thread_exit(stop_event: Optional[Event]) -> None:
    """
    Exits the thread and handles the stop event.

    Args:
        stop_event: Event to signal stop

    Returns:
        None
    """

    if stop_event is None:
        # Module is running independently (main thread)
        return

    # Module is running as a child thread
    stop_event.set()
    thread_loop_handler(stop_event)


def get_function_name(func) -> str:
    """
    Inspects the func to get the function's name

    Args:
        func: Function to inspect

    Returns:
        Function name
    """
    return func.__name__


def get_function_module(func) -> str:
    """
    Inspects the func to get the function's module

    Args:
        func: Function to inspect

    Returns:
        Module name
    """
    module = func.__module__

    # Take first part of module path (if module is nested)
    return module.split(".")[0]
