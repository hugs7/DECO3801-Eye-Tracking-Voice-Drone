"""
Common keyboard module
"""

from .logger_helper import init_logger

logger = init_logger()


def get_key_chr(key_code: int) -> str:
    """
    Wrapper function for getting the character representation of a key code.

    Args:
        key_code: The key code to convert to a character

    Returns:
        The character representation of the key code
    """

    if 0 <= key_code <= 0x10FFFF:
        try:
            key_chr = chr(key_code).lower()
        except ValueError:
            logger.error("Failed to obtain character from key code %d", key_code)
            key_chr = ""
    else:
        key_chr = ""

    return key_chr
