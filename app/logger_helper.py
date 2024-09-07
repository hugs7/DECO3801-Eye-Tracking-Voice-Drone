"""
Logger helper module
"""

import logging
import inspect
from thread_helper import is_main_thread
from str_helper import to_title_case

RESET = "\033[0m"
BRIGHT_RED = "\033[91m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_INFO = "\033[96m"


class LoggerFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with the output name in title case and color based on log level.
        :param record: Log record
        :return: Formatted log record
        """
        # Add a custom field for title-cased logger name
        record.output_name = to_title_case(record.name)

        # Set color based on log level
        if record.levelno == logging.DEBUG:
            color = BRIGHT_BLUE
        elif record.levelno == logging.INFO:
            color = BRIGHT_INFO
        elif record.levelno == logging.WARNING:
            color = BRIGHT_YELLOW
        elif record.levelno == logging.ERROR:
            color = BRIGHT_RED
        elif record.levelno == logging.CRITICAL:
            color = BRIGHT_RED
        else:
            color = RESET

        formatted_message = super().format(record)
        return f"{color}{formatted_message}{RESET}"


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

    formatter = LoggerFormatter("%(asctime)s\t%(output_name)-13s\t%(levelname)s\t%(message)s")

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        for handler in logger.handlers:
            handler.setFormatter(formatter)
