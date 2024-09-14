"""
File handling functions for the voice control project.
"""

import os
import pathlib
from typing import Optional

from common.logger_helper import init_logger

logger = init_logger()


def get_project_root() -> pathlib.Path:
    """
    Returns the root folder of the project, assuming 'voice_control' is part of the directory structure.

    Returns:
        pathlib.Path: The path to the root folder of the project.
    """

    project_root = pathlib.Path(__file__).parent.parent.parent.resolve()
    logger.trace(f"Project root: {project_root}")
    return project_root


def get_package_folder() -> pathlib.Path:
    """
    Returns the path to the 'voice_control' folder.

    Returns:
        pathlib.Path: The path to the 'voice_control' folder.
    """
    project_root = get_project_root()
    package_folder = project_root / "voice_control"
    logger.trace(f"Package folder: {relative_path(package_folder)}")
    return package_folder


def get_data_folder() -> pathlib.Path:
    """
    Returns the path to the 'data' folder inside the 'voice_control' folder.

    Returns:
        pathlib.Path: The path to the 'data' folder.
    """
    voice_control_folder = get_package_folder()
    data_folder = voice_control_folder / "data"
    create_folder_if_not_exists(data_folder)
    logger.trace(f"Data folder: {relative_path(data_folder)}")
    return data_folder


def get_recordings_folder() -> pathlib.Path:
    """
    Returns the path to the 'recordings' folder inside the 'voice_control' folder.

    Returns:
        pathlib.Path: The path to the 'recordings' folder.
    """
    package_root = get_package_folder()
    recordings_folder = package_root / "recordings"
    create_folder_if_not_exists(recordings_folder)
    logger.info(f"Recordings folder: {relative_path(recordings_folder)}")
    return recordings_folder


def get_context_file() -> pathlib.Path:
    """
    Returns the full path to the 'context.jsonl' file in the 'data' folder inside 'voice_control'.

    Returns:
        pathlib.Path: The path to the 'context.jsonl' file.
    """
    data_folder = get_data_folder()
    return data_folder / "context.jsonl"


def file_exists(file_path: pathlib.Path) -> bool:
    """
    Checks if a file exists at the specified path.

    Args:
        file_path (pathlib.Path): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """

    exists = os.path.exists(file_path)
    if exists:
        logger.debug(f"File exists: {file_path}")
    else:
        logger.debug(f"File does not exist: {file_path}")

    return exists


def create_folder_if_not_exists(folder_path: pathlib.Path):
    """
    Creates a folder at the specified path if it does not already exist.

    Args:
        folder_path (pathlib.Path): The path to the folder to create.
    """

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"Folder created: {folder_path}")
    else:
        logger.debug(f"Folder already exists: {folder_path}")


def list_files_in_folder(folder_path: pathlib.Path, file_types: Optional[list[str]] = None) -> list[pathlib.Path]:
    """
    Lists all files in the specified folder.

    Args:
        folder_path (pathlib.Path): The path to the folder to list files from.
        file_type (Optional[list[str]]): A list of file types to filter the files by. Defaults to None.

    Returns:
        list[pathlib.Path]: A list of paths to the files in the folder.
    """

    if file_types is None:
        file_types = [".*"]

    files = [f for f in folder_path.iterdir() if f.is_file() and any(f.name.endswith(file_type) for file_type in file_types)]

    logger.debug(f"Files in folder: {folder_path} - {files}")
    return files


def relative_path(file_path: pathlib.Path) -> pathlib.Path:
    """
    Returns the relative path of the file from the project root.

    Args:
        file_path (pathlib.Path): The path to the file.

    Returns:
        pathlib.Path: The relative path of the file from the project root.
    """

    project_root = get_project_root()
    relative_path = file_path.relative_to(project_root).as_posix()

    return f"./{relative_path}"
