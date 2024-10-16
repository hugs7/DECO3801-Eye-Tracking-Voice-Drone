"""
Init module for the drone package.
06/09/2024
"""

from typing import Union, Optional
from threading import Event

from omegaconf import DictConfig, OmegaConf

from common.logger_helper import init_logger
from common import omegaconf_helper as oh

from .utils import file_handler as fh
from . import constants as c
from . import models

logger = init_logger()


def init_config() -> DictConfig:
    """
    Config intialisation

    Returns:
        DictConfig: The drone config object
    """
    logger.info("Initialising drone configuration...")

    configs_folder = fh.get_configs_folder()
    path = configs_folder / "drone.yaml"

    config = oh.load_or_create_config(path, c.DEFAULT_CONFIG)
    logger.info("Drone configuration initialised")
    return config


def init() -> DictConfig:
    """
    Initialises the drone module

    Returns:
        DictConfig: The drone config object
    """

    logger.info("Initialising drone module...")

    # === Config ===
    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    return config


def init_drone(config: OmegaConf, stop_event: Optional[Event] = None) -> Optional[Union[models.TelloDrone, models.MavicDrone]]:
    """
    Initialises the drone

    Returns:
        DictConfig: The drone config object
    """

    if not config.controller.connect_to_drone:
        logger.info("Running in GUI only mode. Not initialising drone.")
        return None

    logger.info("Initialising drone vehicle...")

    drone_type = config.drone_type

    match drone_type:
        case c.MAVIC:
            vehicle = models.MavicDrone(config.mavic)
        case c.TELLO:
            vehicle = models.TelloDrone(config.tello, stop_event)
        case _:
            raise ValueError(f"Invalid drone type: {drone_type}")

    return vehicle
