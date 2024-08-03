"""
Dictionary Helper
"""


def check_property_exists(value: dict, key: str, class_name: str):
    """
    Checks if a key exists in a dictionary
    :param value: The dictionary to check
    :param key: The key to check for
    :param class_name: The name of the class
    """

    if key not in value:
        raise ValueError(f"Expected key '{key}' in {class_name}")
