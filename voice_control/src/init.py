"""
Initialisation module
"""

import openai
from omegaconf import DictConfig, OmegaConf
import logging
import os
from dotenv import load_dotenv

import constants as c
import file_handler

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


def load_environment_variables():
    """
    Loads environment variables from the .env file.
    """

    load_dotenv()


def init_openai():
    """
    Retrieves the OpenAI API key from the environment variables and sets it in the OpenAI API.

    Raises:
        Exception: If the OpenAI API key is not found in the environment variables.
    """

    api_key = os.getenv(c.OPENAI_API_KEY_CONFIG_KEY)
    if api_key is None:
        raise Exception(
            f"Please assign a valid OpenAI API key to the environment variable {c.OPENAI_API_KEY_CONFIG_KEY}.")

    openai.api_key = api_key


def init() -> DictConfig:
    """
    Initialises the voice control program.
    :return: The configuration object.
    """

    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    load_environment_variables()
    init_openai()

    return config