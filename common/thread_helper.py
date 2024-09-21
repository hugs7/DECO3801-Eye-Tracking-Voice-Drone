"""
Helps with child threads
"""

from typing import Optional
from datetime import datetime
import time
from threading import Event, current_thread

from . import logger_helper as lh
from .gui_helper import fps_to_ms, ms_to_fps
from . import constants as c

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


def ms_delta(start_time: datetime, end_time: datetime) -> float:
    """
    Calculates the time difference between two datetime objects in milliseconds

    Args:
        start_time: The start time
        end_time: The end time

    Returns:
        The time difference in milliseconds
    """
    return (end_time - start_time).total_seconds() * c.MILLISECONDS_PER_SECOND


def run_loop_with_max_tickrate(max_fps: int, callback: callable, *args, **kwargs) -> None:
    """
    Runs a loop with a minimum execution time. Passes the fps / tickrate to the callback.

    Args:
        max_fps (int): The maximum frames per second. If 0, the loop will run as
        fast as possible.
        callback (callable): The function to be called in the loop. If the callback returns False,
                             the loop will exit.
        *args: Positional arguments to pass to the callback.
        **kwargs: Keyword arguments to pass to the callback.
    """
    min_loop_ms = fps_to_ms(max_fps)
    last_loop_start_time = datetime.now()

    while True:
        now = datetime.now()
        tick_rate = ms_to_fps(ms_delta(last_loop_start_time, now))
        callback_res = callback(*args, **kwargs, tick_rate=tick_rate)
        if callback_res is False:
            logger.debug("Callback returned False. Exiting loop...")
            break

        if min_loop_ms > 0:
            now = datetime.now()
            ms_diff = ms_delta(last_loop_start_time, now)

            if ms_diff < min_loop_ms:
                second_to_wait = (min_loop_ms - ms_diff) / c.MILLISECONDS_PER_SECOND
                time.sleep(second_to_wait)

        last_loop_start_time = datetime.now()
