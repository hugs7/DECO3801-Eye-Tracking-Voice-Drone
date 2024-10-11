"""
Common keyboard module
"""

from typing import Dict

import common.constants as cc

from .logger_helper import init_logger
from .omegaconf_helper import conf_key_from_value

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


def is_key_bound(keyboard_bindings: Dict, key_code: int) -> bool:
    """
    Check if an action is bound to a key or if the key is a quit key.

    Args:
        keyboard_bindings: The dictionary containing the key bindings
        key_code: The key code to check if it is bound

    Returns:
        True if the action is bound to a key, False otherwise
    """

    key_chr = get_key_chr(key_code)
    key_action = conf_key_from_value(keyboard_bindings, key_code, key_chr)
    return key_action is not None or key_chr in cc.QUIT_KEYS
