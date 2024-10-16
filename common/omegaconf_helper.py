"""
OmegaConf helper functions
"""

from typing import Optional, Any, Dict
import sys
from pathlib import Path

from omegaconf import OmegaConf

from . import file_handler as fh
from .logger_helper import init_logger

logger = init_logger()


def safe_get(conf: OmegaConf, attr: str) -> any:
    """
    Get attribute value from OmegaConf object with None if attribute is not found.

    Args:
        conf: OmegaConf object
        attr: Attribute to access in dot notation

    Returns:
        Attribute value or None if not found
    """
    try:
        return OmegaConf.select(conf, attr, default=None)
    except AttributeError:
        return None


def conf_key_from_value(conf: OmegaConf, *values: Any) -> Optional[str]:
    """
    Finds key in OmegaConf from value

    Args:
        conf [Omegaconf]: Omegaconfig to find key from by value
        values [Any]: Values to find in the OmegaConf

    Returns:
        [Optional[str]]: The key of the value or None if not found.
    """
    dict = OmegaConf.to_container(conf)

    for key, dict_value in dict.items():
        if dict_value in values:
            return key


def initialise_config(config_dict: Dict, config_path: Path) -> OmegaConf:
    """
    Initialises the configuration file with default values, excluding paths.

    Args:
        config_dict (Dict): The configuration dictionary.
        config_path (str): The path to the configuration file.

    Returns:
        OmegaConf: The OmegaConf object of the configuration
    """

    default_config = OmegaConf.create(config_dict)

    logger.info(f"Initialising config file at {config_path}")
    parent = config_path.parent
    fh.create_folder_if_not_exists(parent)
    OmegaConf.save(default_config, config_path)
    logger.info("Config file initialised.")

    return default_config


def load_or_create_config(config_path: Path, default_config: Dict) -> OmegaConf:
    """
    Load the configuration file if it exists, otherwise create it with default values.

    Args:
        config_path (Path): The path to the configuration file.
        default_config (Dict): The default configuration settings.

    Returns:
        OmegaConf: The OmegaConf object of the configuration
    """

    if config_path.is_file():
        logger.info("Loading config from %s", config_path)
        config = OmegaConf.load(config_path)
    else:
        logger.info("Config file not found at %s. Initialising with default values.", config_path)
        config = initialise_config(default_config, config_path)

    return config
