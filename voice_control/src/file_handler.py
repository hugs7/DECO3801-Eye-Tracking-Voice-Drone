"""
File handling functions for the voice control project.
"""

import logging
import os
import pathlib


logger = logging.getLogger(__name__)


def get_project_root() -> str:
    """
    Returns the root folder of the project, assuming 'voice_control' is part of the directory structure.

    Returns:
        str: The path to the root folder of the project (one level above the 'voice_control' folder).
    """

    project_root = pathlib.Path(__file__).parent.parent.parent.resolve()
    print(project_root)
    logger.info(f"Project root: {project_root}")
    return project_root


def get_package_folder() -> str:
    """
    Returns the path to the 'voice_control' folder.

    Returns:
        str: The path to the 'voice_control' folder.
    """
    project_root = get_project_root()
    package_folder = os.path.join(project_root, "voice_control")
    logger.info(f"Package folder: {package_folder}")
    return package_folder


def get_data_folder() -> str:
    """
    Returns the path to the 'data' folder inside the 'voice_control' folder.

    Returns:
        str: The path to the 'data' folder.
    """
    voice_control_folder = get_package_folder()
    data_folder = os.path.join(voice_control_folder, "data")
    logger.info(f"Data folder: {data_folder}")
    return data_folder


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

    exists = os.path.exists(file_path)
    if (exists):
        logger.debug(f"File exists: {file_path}")
    else:
        logger.debug(f"File does not exist: {file_path}")

    return exists


def create_folder_if_not_exists(folder_path: str):
    """
    Creates a folder at the specified path if it does not already exist.

    Args:
        folder_path (str): The path to the folder to create.
    """

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"Folder created: {folder_path}")
    else:
        logger.debug(f"Folder already exists: {folder_path}")
