"""
Utils for gaze estimation
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

import bz2
import logging
import operator
import pathlib
import tempfile
from typing import Tuple
import numpy as np

import cv2
import torch.hub
import yaml
from omegaconf import DictConfig

from gaze.common.face_model import FaceModel
from gaze.common.face_model_68 import FaceModel68
from gaze.common.face_model_mediapipe import FaceModelMediaPipe

logger = logging.getLogger(__name__)


def get_3d_face_model(config: DictConfig) -> FaceModel:
    if config.face_detector.mode == "mediapipe":
        return FaceModelMediaPipe()
    else:
        return FaceModel68()


def get_ptgaze_model_dir() -> pathlib.Path:
    package_root = pathlib.Path(__file__).parent.resolve()
    model_dir = package_root / "data/models/"
    model_dir.mkdir(exist_ok=True, parents=True)
    return model_dir


def download_dlib_pretrained_model() -> None:
    logger.debug("Called download_dlib_pretrained_model()")

    model_dir = get_ptgaze_model_dir()
    dlib_model_dir = model_dir / "dlib"
    dlib_model_dir.mkdir(exist_ok=True, parents=True)
    dlib_model_path = dlib_model_dir / "shape_predictor_68_face_landmarks.dat"
    logger.debug(f"Update config.face_detector.dlib_model_path to {dlib_model_path.as_posix()}")

    if dlib_model_path.exists():
        logger.debug(f"dlib pretrained model {dlib_model_path.as_posix()} already exists.")
        return

    logger.debug("Download the dlib pretrained model")
    bz2_path = dlib_model_path.as_posix() + ".bz2"
    torch.hub.download_url_to_file("http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2", bz2_path)
    with bz2.BZ2File(bz2_path, "rb") as f_in, open(dlib_model_path, "wb") as f_out:
        data = f_in.read()
        f_out.write(data)


def download_mpiigaze_model() -> pathlib.Path:
    logger.debug("Called _download_mpiigaze_model()")
    model_dir = get_ptgaze_model_dir()
    output_dir = model_dir / "models/"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / "mpiigaze_resnet_preact.pth"
    if not output_path.exists():
        logger.debug("Download the pretrained model")
        torch.hub.download_url_to_file(
            "https://github.com/hysts/pytorch_mpiigaze_demo/releases/download/v0.1.0/mpiigaze_resnet_preact.pth", output_path.as_posix()
        )
    else:
        logger.debug(f"The pretrained model {output_path} already exists.")
    return output_path


def generate_dummy_camera_params(config: DictConfig) -> None:
    logger.debug("Called _generate_dummy_camera_params()")
    if config.demo.image_path:
        path = pathlib.Path(config.demo.image_path).expanduser()
        image = cv2.imread(path.as_posix())
        h, w = image.shape[:2]
    elif config.demo.video_path:
        logger.debug(f"Open video {config.demo.video_path}")
        path = pathlib.Path(config.demo.video_path).expanduser().as_posix()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"{config.demo.video_path} is not opened.")
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap.release()
    else:
        raise ValueError
    logger.debug(f"Frame size is ({w}, {h})")
    logger.debug(f"Close video {config.demo.video_path}")
    out_file = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
    logger.debug(f"Create a dummy camera param file {out_file.name}")
    dic = {
        "image_width": w,
        "image_height": h,
        "camera_matrix": {"rows": 3, "cols": 3, "data": [w, 0.0, w // 2, 0.0, w, h // 2, 0.0, 0.0, 1.0]},
        "distortion_coefficients": {"rows": 1, "cols": 5, "data": [0.0, 0.0, 0.0, 0.0, 0.0]},
    }
    with open(out_file.name, "w") as f:
        yaml.safe_dump(dic, f)
    config.gaze_estimator.camera_params = out_file.name
    logger.debug(f"Update config.gaze_estimator.camera_params to {out_file.name}")


def _expanduser(path: str) -> str:
    if not path:
        return path
    return pathlib.Path(path).expanduser().as_posix()


def expanduser_all(config: DictConfig) -> None:
    if hasattr(config.face_detector, "dlib_model_path"):
        config.face_detector.dlib_model_path = _expanduser(config.face_detector.dlib_model_path)
    config.gaze_estimator.checkpoint = _expanduser(config.gaze_estimator.checkpoint)
    config.gaze_estimator.camera_params = _expanduser(config.gaze_estimator.camera_params)
    config.gaze_estimator.normalized_camera_params = _expanduser(config.gaze_estimator.normalized_camera_params)
    if hasattr(config.demo, "image_path"):
        config.demo.image_path = _expanduser(config.demo.image_path)
    if hasattr(config.demo, "video_path"):
        config.demo.video_path = _expanduser(config.demo.video_path)
    if hasattr(config.demo, "output_dir"):
        config.demo.output_dir = _expanduser(config.demo.output_dir)


def _check_path(config: DictConfig, key: str) -> None:
    path_str = operator.attrgetter(key)(config)
    path = pathlib.Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"config.{key}: {path.as_posix()} not found.")
    if not path.is_file():
        raise ValueError(f"config.{key}: {path.as_posix()} is not a file.")


def check_path_all(config: DictConfig) -> None:
    if config.face_detector.mode == "dlib":
        _check_path(config, "face_detector.dlib_model_path")
    _check_path(config, "gaze_estimator.checkpoint")
    _check_path(config, "gaze_estimator.camera_params")
    _check_path(config, "gaze_estimator.normalized_camera_params")
    if config.demo.image_path:
        _check_path(config, "demo.image_path")
    if config.demo.video_path:
        _check_path(config, "demo.video_path")


def upscale(frame: cv2.VideoCapture, upscaled_dim: Tuple[int, int]) -> cv2.VideoCapture:
    """
    Upscale the frame
    :param frame: The frame to upscale
    :param upscaled_dim: The dimensions to upscale to (width, height)
    :return cv2.VideoCapture: The upscaled frame
    """

    upscaled_frame = cv2.resize(frame, upscaled_dim)

    return upscaled_frame


def flip_image(image: np.ndarray) -> np.ndarray:
    """
    Flip the image
    :param image: The image to flip
    :return np.ndarray: The flipped image
    """

    return image[:, ::-1]


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp the value between the min and max values
    :param value: The value to clamp
    :param min_value: The minimum value
    :param max_value: The maximum value
    :return float: The clamped value
    """

    return max(min(value, max_value), min_value)
