"""
Logger helper module
"""

import logging
import inspect
from thread_helper import is_main_thread


def init_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Initialise a named logger with the specified logging level.
    :param level: Logging level
    :return: Logger instance
    """

    # Use inspect to find the caller's module
    caller_frame = inspect.stack()[1]  # [1] gives the caller of this function
    caller_module = inspect.getmodule(caller_frame[0])

    # Use the caller's module name for the logger
    logger_name = caller_module.__name__ if caller_module else "__main__"
    logger = logging.getLogger(logger_name)

    if is_main_thread():
        logger.setLevel(level)

    # Set format to include the logger name
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
