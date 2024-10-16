"""
Common file handler functions
"""

from typing import Optional
from pathlib import Path
import logging

# To fix later
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Returns the root folder of the project, assuming 'eye_tracking' is part of the directory structure.

    Returns:
        Path: The path to the root folder of the project.
    """

    project_root = Path(__file__).parent.parent.resolve()
    return project_root


def get_common_folder() -> Path:
    """
    Returns the path to the 'common' folder.

    Returns:
        Path: The path to the 'common' folder.
    """
    project_root = get_project_root()
    common_folder = project_root / "common"
    return common_folder


def get_file_extension(file_path: Path, remove_dot: bool = False) -> str:
    """
    Returns the file extension of the file at the specified path.

    Args:
        file_path (Path): The path to the file.
        remove_dot (bool): Whether to remove the dot from the file extension. Defaults to False.

    Returns:
        str: The file extension.
    """
    suffix = file_path.suffix

    if remove_dot:
        suffix = suffix[1:]

    return suffix


def file_exists(file_path: Path) -> bool:
    """
    Checks if a file exists at the specified path.

    Args:
        file_path (Path): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """

    exists = file_path.exists()
    if exists:
        logger.debug(f"File exists: {file_path}")
    else:
        logger.debug(f"File does not exist: {file_path}")

    return exists


def create_folder_if_not_exists(folder_path: Path):
    """
    Creates a folder at the specified path if it does not already exist.

    Args:
        folder_path (Path): The path to the folder to create.
    """

    if not folder_path.exists():
        folder_path.mkdir(parents=True)
        logger.info(f"Folder created: {folder_path}")
    else:
        logger.debug(f"Folder already exists: {folder_path}")


def list_files_in_folder(folder_path: Path, file_types: Optional[list[str]] = None) -> list[Path]:
    """
    Lists all files in the specified folder.

    Args:
        folder_path (Path): The path to the folder to list files from.
        file_type (Optional[list[str]]): A list of file types to filter the files by. Defaults to None.

    Returns:
        list[Path]: A list of paths to the files in the folder.
    """

    if file_types is None:
        file_types = [".*"]

    files = [f for f in folder_path.iterdir() if f.is_file() and any(f.name.endswith(file_type) for file_type in file_types)]

    logger.debug(f"Files in folder: {folder_path} - {files}")
    return files


def relative_path(file_path: Path) -> Path:
    """
    Returns the relative path of the file from the project root.

    Args:
        file_path (Path): The path to the file.

    Returns:
        Path: The relative path of the file from the project root.
    """

    project_root = get_project_root()
    relative_path = file_path.relative_to(project_root).as_posix()

    return f"./{relative_path}"
