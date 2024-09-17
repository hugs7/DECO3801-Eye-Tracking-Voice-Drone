"""
Utils for gaze estimation
Modified by: Hugo Burton
Last Updated: 21/08/2024
"""

from common.logger_helper import init_logger
import pathlib
import operator
from omegaconf import DictConfig


logger = init_logger()


def get_ptgaze_model_dir() -> pathlib.Path:
    """
    Gets the directory to store the model files.

    Returns:
        pathlib.Path: The directory to store the model files
    """
    package_root = pathlib.Path(__file__).parent.parent.parent.resolve()
    model_dir = package_root / "data/models/"
    model_dir.mkdir(exist_ok=True, parents=True)
    return model_dir


def download_mpiigaze_model() -> pathlib.Path:
    """
    Downloads the pretrained MPIIGaze model.

    Returns:
        pathlib.Path: The path to the downloaded model
    """
    logger.debug("Called _download_mpiigaze_model()")
    model_dir = get_ptgaze_model_dir()
    output_dir = model_dir / "models/"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / "mpiigaze_resnet_preact.pth"
    if not output_path.exists():
        # Lazy import to avoid unnecessary dependency
        logger.info("Lazy loading torch.hub")
        import torch.hub

        url = "https://github.com/hysts/pytorch_mpiigaze_demo/releases/download/v0.1.0/mpiigaze_resnet_preact.pth"
        logger.debug("Downloading the pretrained model from '%s'", url)
        torch.hub.download_url_to_file(url, output_path.as_posix())
    else:
        logger.debug(f"The pretrained model {output_path} already exists.")
    return output_path


def _expanduser(path: str) -> str:
    """
    Expands a relative path to absolute posix paths.
    E.g. "~/path/to/file" -> "/home/user/path/to/file".

    Args:
        path (str): The path to expand as a string.

    Returns:
        str: The expanded path as a string.
    """
    if not path:
        return path
    return pathlib.Path(path).expanduser().as_posix()


def expanduser_all(config: DictConfig) -> None:
    """
    Expands the user in the paths in the config.

    Args:
        config (DictConfig): The config to expand the user in.
    """
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
    """
    Checks if the path exists and is a file.

    Args:
        config (DictConfig): The config to check the path in.
        key (str): The key to get the path from the config.
    """
    path_str = operator.attrgetter(key)(config)
    path = pathlib.Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"config.{key}: {path.as_posix()} not found.")
    if not path.is_file():
        raise ValueError(f"config.{key}: {path.as_posix()} is not a file.")


def check_path_all(config: DictConfig) -> None:
    """
    Checks if the paths in the config exist and are files.

    Args:
        config (DictConfig): The config to check the paths in.
    """
    _check_path(config, "gaze_estimator.checkpoint")
    _check_path(config, "gaze_estimator.camera_params")
    _check_path(config, "gaze_estimator.normalized_camera_params")
    if config.demo.image_path:
        _check_path(config, "demo.image_path")
    if config.demo.video_path:
        _check_path(config, "demo.video_path")
