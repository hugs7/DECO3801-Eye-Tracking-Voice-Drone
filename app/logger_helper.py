"""
Logger helper module
"""

import logging
import inspect
from thread_helper import is_main_thread
from str_helper import to_title_case

RESET = "\033[0m"
BRIGHT_RED = "\033[91m"
CRITICAL_RED = "\033[41m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_INFO = "\033[96m"
GREY = "\033[90m"

TRACE_LEVEL_NUM = 5
TRACE_LEVEL_NAME = "TRACE"


def add_trace_level():
    """
    Add the TRACE level to the logging module.
    """
    logging.addLevelName(TRACE_LEVEL_NUM, TRACE_LEVEL_NAME)

    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, message, args, **kwargs)

    logging.Logger.trace = trace


add_trace_level()


class LoggerFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with the output name in title case and color based on log level.

        Args:
            record: Log record

        Returns:
            Formatted log record
        """
        # Add a custom field for title-cased logger name
        record.output_name = to_title_case(record.name)

        # Set color based on log level
        color = self.get_log_colour(record.levelno)

        formatted_message = super().format(record)
        return f"{color}{formatted_message}{RESET}"

    def get_log_colour(self, level: int) -> str:
        """
        Get the log colour based on the log level.

        Args:
            level: Log level

        Returns:
            Log colour
        """
        # Custom log levels
        if level == TRACE_LEVEL_NUM:
            return GREY

        # Standard log levels
        match level:
            case logging.DEBUG:
                return BRIGHT_BLUE
            case logging.INFO:
                return BRIGHT_INFO
            case logging.WARNING:
                return BRIGHT_YELLOW
            case logging.ERROR:
                return BRIGHT_RED
            case logging.CRITICAL:
                return CRITICAL_RED
            case _:
                return RESET


def init_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Initialise a named logger with the specified logging level.

    Args:
        level: Logging level

    Returns:
        Logger instance
    """

    # [1] gives the caller of this function
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])

    # Use the caller's module name for the logger
    logger_name = caller_module.__name__ if caller_module else "__main__"
    logger = logging.getLogger(logger_name)

    if is_main_thread():
        logger.setLevel(level)

    logger.propagate = False

    if not logger.hasHandlers():
        attach_formatter(logger)

    return logger


def init_root_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Initialise the root logger with the specified logging level.

    Args:
        level: Logging level

    Returns:
        Logger instance
    """

    logger = logging.getLogger()
    logger.setLevel(level)

    attach_formatter(logger)

    return logger


def attach_formatter(logger: logging.Logger) -> None:
    """
    Attach a formatter to the logger.

    Args:
        logger: Logger instance

    Returns:
        None
    """

    formatter = LoggerFormatter(
        "%(asctime)s  %(output_name)-13s %(levelname)-13s%(message)s")

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        for handler in logger.handlers:
            handler.setFormatter(formatter)


def disable_logger(logger_name: str) -> None:
    """
    Disable a logger and all its handlers.

    Args:
        logger_name: Logger name

    Returns:
        None
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL + 1)


def test_logger():
    """
    Test the logger helper functions
    """

    logger = init_logger(TRACE_LEVEL_NUM)

    logger.trace("This is a trace message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


if __name__ == "__main__":
    test_logger()
