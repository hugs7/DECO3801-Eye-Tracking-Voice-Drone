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

    attach_formatter(logger)

    return logger


def init_root_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Initialise the root logger with the specified logging level.
    :param level: Logging level
    :return: Logger instance
    """

    logger = logging.getLogger()
    logger.setLevel(level)

    attach_formatter(logger)

    return logger


def attach_formatter(logger: logging.Logger) -> None:
    """
    Attach a formatter to the logger.
    :param logger: Logger instance
    :return: None
    """

    formatter = logging.Formatter("%(asctime)s\t%(name)-13s\t%(levelname)s\t%(message)s")

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        for handler in logger.handlers:
            handler.setFormatter(formatter)
