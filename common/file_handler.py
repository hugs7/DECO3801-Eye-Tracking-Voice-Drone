"""
Common file handler functions
"""

from pathlib import Path


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
        pathlib.Path: The path to the 'common' folder.
    """
    project_root = get_project_root()
    common_folder = project_root / "common"
    return common_folder
