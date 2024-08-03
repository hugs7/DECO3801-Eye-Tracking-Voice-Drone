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
