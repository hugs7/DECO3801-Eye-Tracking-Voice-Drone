import cv2
import yaml
from common.logger_helper import init_logger
import pathlib
import tempfile
from omegaconf import DictConfig

logger = init_logger()


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
        raise ValueError("Either demo.image_path or demo.video_path must be set.")

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
