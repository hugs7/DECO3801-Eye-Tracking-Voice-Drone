"""
Common keyboard module
"""

from typing import Dict, List
from threading import Lock

import common.constants as cc

from .PeekableQueue import PeekableQueue
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


def keyboard_event_loop(data_lock: Lock, keyboard_queue: PeekableQueue, keyboard_bindings: Dict) -> List[int]:
    """
    Keyboard event loop that reads key presses and adds them to the keyboard queue.

    Args:
        data_lock: The lock to protect the keyboard queue
        keyboard_queue: The queue to add key presses to
        keyboard_bindings: The dictionary containing the key bindings

    Returns:
        key_buffer (List[int]): The list of key codes that were pressed
    """
    if keyboard_queue is None:
        logger.warning("Keyboard queue not initialised in shared data.")
        return []

    # Define a buffer so that we are not locking the data for too long.
    # Not critical while keyboard inputs are simple, however, this is good
    # practice for more complex inputs.
    key_buffer: List[int] = []

    with data_lock:
        i = 0
        while i < keyboard_queue.qsize():
            key_code = keyboard_queue.peek(i)
            is_bound = is_key_bound(keyboard_bindings, key_code)
            if is_bound:
                key_code = keyboard_queue.get()
                key_buffer.append(key_code)
            else:
                i += 1
                logger.trace("Key %s not bound in keybindings", get_key_chr(key_code))

    return key_buffer


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
