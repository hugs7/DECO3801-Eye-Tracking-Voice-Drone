"""
Helper with loops
"""

import time
from datetime import datetime

from . import constants as c
from .logger_helper import init_logger
from .gui_helper import fps_to_ms, ms_to_fps

logger = init_logger()


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
