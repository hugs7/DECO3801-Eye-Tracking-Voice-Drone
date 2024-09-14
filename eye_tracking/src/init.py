"""
Initialises the eye_tracking package.
Author: Hugo Burton
Last Updated: 21/08/2024
"""

import pathlib
from omegaconf import DictConfig, OmegaConf

from common.logger_helper import init_logger

from .utils.model import (
    check_path_all,
    download_mpiigaze_model,
    expanduser_all,
)
from .utils.camera import generate_dummy_camera_params


logger = init_logger()


def init_ptgaze_config() -> DictConfig:
    """
    Custom config initialiser for ptgaze
    :return DictConfig: The ptgaze config
    """

    package_root = pathlib.Path(__file__).parent.parent.resolve()
    path = package_root / "configs/mpiigaze.yaml"

    logger.info(f"Loading config from {path}")
    config = OmegaConf.load(path)
    config.PACKAGE_ROOT = package_root.as_posix()
    logger.info(f"Pacakge root: {config.PACKAGE_ROOT}")

    return config


def init_ptgaze() -> DictConfig:
    """
    Initialises ptgaze for eye tracking
    :return DictConfig: The ptgaze config
    """

    config = init_ptgaze_config()

    expanduser_all(config)
    if config.gaze_estimator.use_dummy_camera_params:
        generate_dummy_camera_params(config)

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    download_mpiigaze_model()

    check_path_all(config)

    return config
