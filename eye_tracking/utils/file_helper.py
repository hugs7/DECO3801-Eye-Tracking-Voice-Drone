"""
File Helper Utils
"""

import os
import json


def check_path_exists(path: str) -> bool:
    """
    Check if a path exists
    :param path: The path to check
    :return: True if the path exists, False otherwise
    """

    return os.path.exists(path)


def load_json(json_path) -> dict:
    """
    Loads a JSON file
    :param json_path: The path to the JSON file
    :return: The JSON data
    """

    if not check_path_exists(json_path):
        raise FileNotFoundError(f"JSON File not found: {json_path}")

    with open(json_path, "r") as file:
        return json.load(file)


def resolve_path(relative_path: str, expect_exists: bool = True) -> str:
    """
    Takes a path relative to the entry point and returns the absolute path
    :param relative_path: The relative path
    :param expect_exists: True if the path is expected to exist (default), False otherwise
    :return: The absolute path
    """

    # Get path of the entry point
    entry_point = os.path.dirname(os.path.abspath(__file__))

    # Join the entry point with the relative path
    absolute_path = os.path.join(entry_point, relative_path)

    if expect_exists and not check_path_exists(absolute_path):
        raise FileNotFoundError(f"Path not found: {absolute_path}")

    return absolute_path
