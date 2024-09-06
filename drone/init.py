"""
Init module for the drone package.
06/09/2024
"""

import pathlib
from omegaconf import DictConfig, OmegaConf
import logging
from omegaconf import DictConfig, OmegaConf
from typing import Union

import models

logger = logging.getLogger(__name__)


def init_config() -> DictConfig:
    """
    Config intialisation
    """

    package_root = pathlib.Path(__file__).parent.resolve()
    path = package_root / "configs/mpiigaze.yaml"

    logger.info(f"Loading config from {path}")
    config = OmegaConf.load(path)
    config.PACKAGE_ROOT = package_root.as_posix()
    logger.info(f"Pacakge root: {config.PACKAGE_ROOT}")

    return config


def init(drone_type) -> Union[models.MavicDrone, models.TelloDrone]:
    """
    Initialises the drone
    """

    # === Config ===
    config = init_config()

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    # download_mpiigaze_model()

    # check_path_all(config)

    return config

    match drone_type:
        case c.MAVIC:
            vehicle = mavic.MavicDrone(c.MAVIC_IP, c.MAVIC_PORT)
        case c.TELLO:
            vehicle = tello.TelloDrone()
        case _:
            raise ValueError(f"Invalid drone type: {drone_type}")

    return vehicle
