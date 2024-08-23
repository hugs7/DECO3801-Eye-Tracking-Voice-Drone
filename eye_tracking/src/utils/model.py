"""
Utils for gaze estimation
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

import logging
import pathlib
import torch.hub
import operator
from omegaconf import DictConfig


logger = logging.getLogger(__name__)


def get_ptgaze_model_dir() -> pathlib.Path:
<<<<<<< HEAD
    package_root = pathlib.Path(__file__).parent.parent.parent.resolve()
=======
    package_root = pathlib.Path(__file__).parent.parent.resolve()
>>>>>>> dd828f6 (Refactor everything)
    model_dir = package_root / "data/models/"
    model_dir.mkdir(exist_ok=True, parents=True)
    return model_dir


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


def _expanduser(path: str) -> str:
    if not path:
        return path
    return pathlib.Path(path).expanduser().as_posix()


def expanduser_all(config: DictConfig) -> None:
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
    _check_path(config, "gaze_estimator.checkpoint")
    _check_path(config, "gaze_estimator.camera_params")
    _check_path(config, "gaze_estimator.normalized_camera_params")
    if config.demo.image_path:
        _check_path(config, "demo.image_path")
    if config.demo.video_path:
        _check_path(config, "demo.video_path")
