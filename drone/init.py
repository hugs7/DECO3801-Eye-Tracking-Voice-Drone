"""
Init module for the drone package.
06/09/2024
"""

import pathlib
from omegaconf import DictConfig, OmegaConf
import logging
from typing import Union
import models
import constants as c

logger = logging.getLogger(__name__)


def init_config() -> DictConfig:
    """
    Config intialisation
    """

    package_root = pathlib.Path(__file__).parent.resolve()
    path = package_root / "configs/drone_config.yaml"

    logger.info(f"Loading config from {path}")
    config = OmegaConf.load(path)

    return config


def init() -> DictConfig:
    """
    Initialises the drone
    :return: The drone object
    """

    # === Config ===
    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    return config


def init_drone(config: OmegaConf) -> Union[models.TelloDrone, models.MavicDrone]:
    """
    Initialises the drone
    :return: The drone object
    """

    drone_type = config.drone_type

    match drone_type:
        case c.MAVIC:
            vehicle = models.MavicDrone(c.MAVIC_IP, c.MAVIC_PORT)
        case c.TELLO:
            vehicle = models.TelloDrone()
        case _:
            raise ValueError(f"Invalid drone type: {drone_type}")

    return vehicle
