"""
Initialisation module
"""

import os
import logging

from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf
import openai

from common.logger_helper import init_logger

from . import constants as c
from . import file_handler

logger = init_logger(logging.DEBUG)


def init_config() -> DictConfig:
    """
    Initialises the configuration for the voice control program.

    Returns:
        The configuration object.
    """

    package_root = file_handler.get_package_folder()
    config_path = package_root / "configs/config.yaml"
    logger.debug(f"Config path: {file_handler.relative_path(config_path)}")
    if not file_handler.file_exists(config_path):
        raise FileNotFoundError("Configuration file not found.")

    logger.info(f"Loading config from {file_handler.relative_path(config_path)}")
    config = OmegaConf.load(config_path)
    config.PACKAGE_ROOT = package_root.as_posix()
    logger.debug(f"Pacakge root: {config.PACKAGE_ROOT}")

    return config


def load_environment_variables():
    """
    Loads environment variables from the .env file.
    """

    load_dotenv()
    init_openai()


def init_openai():
    """
    Retrieves the OpenAI API key from the environment variables and sets it in the OpenAI API.

    Raises:
        Exception: If the OpenAI API key is not found in the environment variables.
    """

    api_key = os.getenv(c.OPENAI_API_KEY_CONFIG_KEY)
    if api_key is None:
        raise Exception(f"Please assign a valid OpenAI API key to the environment variable {c.OPENAI_API_KEY_CONFIG_KEY}.")

    openai.api_key = api_key


def init() -> DictConfig:
    """
    Initialises the voice control program.

    Returns:
        The configuration object.
    """

    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    load_environment_variables()

    return config
