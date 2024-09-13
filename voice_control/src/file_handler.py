"""
File handling functions for the voice control project.
"""

import os
import site


def get_project_root() -> str:
    """
    Returns the root folder of the project, assuming 'voice_control' is part of the directory structure.

    Returns:
        str: The path to the root folder of the project (one level above the 'voice_control' folder).
    """

    return site.getsitepackages()[0]


def get_package_folder() -> str:
    """
    Returns the path to the 'voice_control' folder.

    Returns:
        str: The path to the 'voice_control' folder.
    """
    project_root = get_project_root()
    return os.path.join(project_root, "voice_control")


def get_data_folder() -> str:
    """
    Returns the path to the 'data' folder inside the 'voice_control' folder.

    Returns:
        str: The path to the 'data' folder.
    """
    voice_control_folder = get_package_folder()
    return os.path.join(voice_control_folder, "data")


def get_context_file() -> str:
    """
    Returns the full path to the 'context.jsonl' file in the 'data' folder inside 'voice_control'.

    Returns:
        str: The full path to the 'context.jsonl' file.
    """
    data_folder = get_data_folder()
    return os.path.join(data_folder, "context.jsonl")


def file_exists(file_path: str) -> bool:
    """
    Checks if a file exists at the specified path.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)
