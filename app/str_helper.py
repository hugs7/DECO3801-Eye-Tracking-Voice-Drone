"""
String helper functions
"""


def to_title_case(s: str) -> str:
    """
    Convert a string to title case.
    :param s: String
    :return: Title case string
    """
    # Replace _ with space
    s = s.replace("_", " ")

    return s.title()
