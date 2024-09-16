"""
String helper functions
"""


def to_title_case(s: str) -> str:
    """
    Convert a string to title case.

    Args:
        s: String

    Returns:
        Title case string
    """
    # Replace _ with space
    s = s.replace("_", " ")

    return s.title()


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
