"""
Initialisation module
"""

import file_handler
from omegaconf import DictConfig, OmegaConf
import logging

logger = logging.getLogger(__name__)


def init_config() -> DictConfig:
    """
    Initializes the configuration for the voice control program.
    :return: The configuration object.
    """

    package_root = file_handler.get_package_folder()
    config_path = package_root / "configs/config.yaml"
    if not file_handler.file_exists(config_path):
        raise FileNotFoundError("Configuration file not found.")

    logger.info(f"Loading config from {config_path}")
    config = OmegaConf.load(config_path)
    config.PACKAGE_ROOT = package_root.as_posix()
    logger.info(f"Pacakge root: {config.PACKAGE_ROOT}")

    return config
