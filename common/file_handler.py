"""
Common file handler functions
"""

import os
import pathlib


def get_project_root() -> pathlib.Path:
    """
    Returns the root folder of the project, assuming 'eye_tracking' is part of the directory structure.

    Returns:
        pathlib.Path: The path to the root folder of the project.
    """

    project_root = pathlib.Path(__file__).parent.parent.resolve()
    return project_root


def get_common_folder() -> pathlib.Path:
    """
    Returns the path to the 'common' folder.

    Returns:
        pathlib.Path: The path to the 'common' folder.
    """
    project_root = get_project_root()
    common_folder = project_root / "common"
    return common_folder
