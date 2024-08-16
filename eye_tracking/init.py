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
import argparse
from omegaconf import DictConfig, OmegaConf
import logging

from gaze.demo import Demo

import gaze.main as ptgaze_main

from gaze.utils import (
    check_path_all,
    download_dlib_pretrained_model,
    download_ethxgaze_model,
    download_mpiifacegaze_model,
    download_mpiigaze_model,
    expanduser_all,
    generate_dummy_camera_params,
)

import pathlib
import warnings

import torch
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


def init_ptgaze():
    """
    Initialises ptgaze for eye tracking
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

    demo = Demo(config)
    demo.run()


def init_landmark_mapping() -> landmarks.Landmarks:
    """
    Initialises the mapping for landmarks on the face
    """

    LANDMARK_MAPPING_PATH = file_helper.resolve_path(os.path.join(constants.MAPPINGS_FOLDER, "landmark_mapping.json"))

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)
    lmks = landmarks.Landmarks(landmark_mapping)

    return lmks


def init_window(window_width: int, window_height: int, landmark_visibility: Dict[str, bool]) -> coordinate.Coordinate2D:
    """
    Initialises the window for the eye tracking application
    :param window_width: The width of the window
    :param window_height: The height of the window
    :param landmark_visibility: The visibility of the landmarks
    :return coordinate.Coordinate: The upscaled dimensions
    """

    # Rescale window to fill scren better
    feed_ratio = window_width / window_height
    upscaled_window_width = 2400
    upscaled_window_height = int(upscaled_window_width / feed_ratio)
    upscaled_dim = coordinate.Coordinate2D(upscaled_window_width, upscaled_window_height)

    # Set the desired window size
    cv2.namedWindow(constants.EYE_TRACKING_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(constants.EYE_TRACKING_WINDOW_NAME, window_width, window_height)

    mouse_params = {
        "landmark_visibility": landmark_visibility,
        "upscaled_dim": upscaled_dim,
    }
    cv2.setMouseCallback(constants.EYE_TRACKING_WINDOW_NAME, controller.mouse_callback, mouse_params)

    return upscaled_dim


def camera_init() -> cv2.VideoCapture:
    """
    Initialises the camera
    :return cv2.VideoCapture: The camera object
    """
    cam = cv2.VideoCapture(0)
    return cam


def init_face_mesh() -> FaceMesh:
    """
    Initialises the face mesh detector
    :return FaceMesh: The face mesh detector
    """
    face_mesh = FaceMesh(refine_landmarks=True, max_num_faces=1)
    return face_mesh


def init_landmark_visibility() -> Dict[str, bool]:
    """
    Initialises the visibility of the landmarks
    :return Dict[str, bool]: The visibility of the landmarks
    """

    return {
        "left": True,  # Left eye
        "right": True,  # Right eye
        "eyebrow_left": False,
        "eyebrow_right": False,
        "upper_eyelid_left": True,
        "upper_eyelid_right": True,
        "lower_eyelid_left": True,
        "lower_eyelid_right": True,
        "under_eye_left": False,
        "under_eye_right": False,
        "eyesocket_outside_left": False,
        "eyesocket_outside_right": False,
        "above_eye_left": False,
        "above_eye_right": False,
        "lips": False,
        "nose_bridge": False,
        "nose_lower": False,
        "nostrils": False,
        "tear_trough_left": False,
        "tear_trough_right": False,
        "chin": False,
        "cheek_left": False,
        "cheek_right": False,
        "ear_left": False,
        "ear_right": False,
        "temporal_left": False,
        "temporal_right": False,
        "philtrum": False,
        "upper_lip": False,
        "forehead": False,
    }
