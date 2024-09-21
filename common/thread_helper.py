"""
Helps with child threads
"""

from typing import Optional
from datetime import datetime
import time
from threading import Event, current_thread

from . import logger_helper as lh
from .gui_helper import fps_to_ms

logger = lh.init_logger()


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


def run_loop_with_max_tickrate(max_fps: int, callback: callable, *args, **kwargs) -> None:
    """
    Runs a loop with a minimum execution time.

    Args:
        max_fps (int): The maximum frames per second. If 0, the loop will run as
        fast as possible.
        callback (callable): The function to be called in the loop.
        *args: Positional arguments to pass to the callback.
        **kwargs: Keyword arguments to pass to the callback.
    """
    min_loop_time = fps_to_ms(max_fps)
    last_loop_start_time = datetime.now()

    while True:
        callback(*args, **kwargs)

        if min_loop_time == 0:
            continue

        now = datetime.now()
        diff = now - last_loop_start_time

        if diff.total_seconds() * 1000 < min_loop_time:
            time.sleep((min_loop_time - diff.total_seconds() * 1000) / 1000)

        last_loop_start_time = datetime.now()
