"""
File handling functions for the drone module.
"""

from pathlib import Path

from common.logger_helper import init_logger
from common import file_handler as cfu


logger = init_logger()


def get_package_folder() -> Path:
    """
    Returns the path to the 'drone' folder.

    Returns:
        Path: The path to the 'drone' folder.
    """
    project_root = cfu.get_project_root()
    package_folder = project_root / "drone"
    logger.trace(f"Package folder: {cfu.relative_path(package_folder)}")
    return package_folder


def get_configs_folder() -> Path:
    """
    Returns the path to the 'configs' folder inside the 'drone' folder.

    Returns:
        path: The path to the 'configs' folder.
    """

    drone_folder = get_package_folder()
    configs_folder = drone_folder / "configs"
    cfu.create_folder_if_not_exists(configs_folder)
    logger.trace(f"Configs folder: {cfu.relative_path(configs_folder)}")
    return configs_folder


def get_assets_folder() -> Path:
    """
    Returns the path to the 'data' folder inside the 'drone' folder.

    Returns:
        Path: The path to the 'data' folder.
    """
    drone_folder = get_package_folder()
    data_folder = drone_folder / "assets"
    cfu.create_folder_if_not_exists(data_folder)
    logger.trace(f"Data folder: {cfu.relative_path(data_folder)}")
    return data_folder
