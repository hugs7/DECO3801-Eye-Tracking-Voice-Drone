"""
Init module for the drone package.
06/09/2024
"""

from omegaconf import DictConfig, OmegaConf
import logging
from typing import Union

from .utils import file_handler as fh

from . import constants as c
from . import models

logger = logging.getLogger(__name__)


def init_config() -> DictConfig:
    """
    Config intialisation

    Returns:
        DictConfig: The drone config object
    """

    package_root = fh.get_package_folder()
    path = package_root / "configs/drone.yaml"

    logger.info(f"Loading config from {path}")
    config = OmegaConf.load(path)

    return config


def init() -> DictConfig:
    """
    Initialises the drone

    Returns:
        DictConfig: The drone config object
    """

    # === Config ===
    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    return config


def init_drone(config: OmegaConf) -> Union[models.TelloDrone, models.MavicDrone]:
    """
    Initialises the drone

    Returns:
        DictConfig: The drone config object
    """

    drone_type = config.drone_type

    match drone_type:
        case c.MAVIC:
            vehicle = models.MavicDrone(config.mavic)
        case c.TELLO:
            vehicle = models.TelloDrone(config.tello)
        case _:
            raise ValueError(f"Invalid drone type: {drone_type}")

    return vehicle
