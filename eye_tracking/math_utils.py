"""
Math Utils
"""


def in_range(value, min_value, max_value) -> bool:
    """
    Check if a value is in a range
    :param value: The value to check
    :param min_value: The minimum value
    :param max_value: The maximum value
    :return: True if the value is in the range, False otherwise
    """

    return min_value <= value and value <= max_value
