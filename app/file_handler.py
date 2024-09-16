"""
File handler module for app
"""

from pathlib import Path

from common.file_handler import get_project_root


def get_app_folder() -> Path:
    """
    Get the path to the app folder.

    Returns:
        Path to the app folder
    """

    project_root = get_project_root()
    app_folder = project_root / "app"

    return app_folder


def get_configs_folder() -> Path:
    """
    Get the path to the configs folder.

    Returns:
        Path to the configs folder
    """

    app_folder = get_app_folder()
    configs_folder = app_folder / "configs"

    return configs_folder
