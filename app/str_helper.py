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