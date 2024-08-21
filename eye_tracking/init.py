"""
Initialises the eye_tracking package.
"""

import os
from typing import Dict
import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh

import constants
import coordinate
import landmarks
import utils.file_helper as file_helper
import controller


# Pt gaze imports
import pathlib
from omegaconf import DictConfig, OmegaConf
import logging
from gaze.utils import (
    check_path_all,
    download_dlib_pretrained_model,
    download_ethxgaze_model,
    download_mpiifacegaze_model,
    download_mpiigaze_model,
    expanduser_all,
    generate_dummy_camera_params,
)
from omegaconf import DictConfig, OmegaConf


logger = logging.getLogger(__name__)


def init_ptgaze_config(mode: str) -> DictConfig:
    """
    Custom config initialiser for ptgaze
    """

    package_root = pathlib.Path(__file__).parent.resolve()
    ptgaze_package_root = package_root / "gaze"
    if mode == "mpiigaze":
        path = ptgaze_package_root / "data/configs/mpiigaze.yaml"
    elif mode == "mpiifacegaze":
        path = ptgaze_package_root / "data/configs/mpiifacegaze.yaml"
    elif mode == "eth-xgaze":
        path = ptgaze_package_root / "data/configs/eth-xgaze.yaml"
    else:
        raise ValueError(f"Incorrect mode selected: {mode}")

    logger.info(f"Loading config from {path}")
    config = OmegaConf.load(path)
    config.PACKAGE_ROOT = ptgaze_package_root.as_posix()
    logger.info(f"Pacakge root: {config.PACKAGE_ROOT}")

    return config


def init_ptgaze() -> DictConfig:
    """
    Initialises ptgaze for eye tracking
    :return DictConfig: The ptgaze config
    """

    config = init_ptgaze_config("mpiigaze")

    expanduser_all(config)
    if config.gaze_estimator.use_dummy_camera_params:
        generate_dummy_camera_params(config)

    OmegaConf.set_readonly(config, True)
    logger.info(OmegaConf.to_yaml(config))

    if config.face_detector.mode == "dlib":
        download_dlib_pretrained_model()

    if config.mode == "MPIIGaze":
        download_mpiigaze_model()
    elif config.mode == "MPIIFaceGaze":
        download_mpiifacegaze_model()
    elif config.mode == "ETH-XGaze":
        download_ethxgaze_model()

    check_path_all(config)

    return config
