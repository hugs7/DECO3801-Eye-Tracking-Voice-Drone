"""
This module contains helper functions for string manipulation.
"""


def to_title_case(text: str) -> str:
    """
    Convert the input text to title case.

    Args:
        text (str): The input text.

    Returns:
        str: The text in title case.
    """

    text = text.replace("_", " ")
    return text.title()


def trim(text: str) -> str:
    """
    Remove leading and trailing whitespace from the input text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with leading and trailing whitespace removed.
    """

    text = text.replace("\n", "\\n")
    return text.strip()
