import dataclasses
from typing import Optional
import cv2
import numpy as np
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclasses.dataclass()
class Camera:
    width: int = dataclasses.field(init=False)
    height: int = dataclasses.field(init=False)
    camera_matrix: np.ndarray = dataclasses.field(init=False)
    dist_coefficients: np.ndarray = dataclasses.field(init=False)

    camera_params_path: dataclasses.InitVar[str] = None

    def __post_init__(self, camera_params_path):
        """
        Initialises the camera object with the camera parameters
        Args:
            camera_params_path: Path to the camera parameters file
        """

        with open(camera_params_path) as f:
            data = yaml.safe_load(f)
        self.width = data["image_width"]
        self.height = data["image_height"]
        self.camera_matrix = np.array(
            data["camera_matrix"]["data"]).reshape(3, 3)
        self.dist_coefficients = np.array(
            data["distortion_coefficients"]["data"]).reshape(-1, 1)

    def project_points(self, points3d: np.ndarray, rvec: Optional[np.ndarray] = None, tvec: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Projects 3D world points (metres) to 2D image points (pixels)
        Args:
            points3d: 3D world points (metres)
            rvec: Rotation vector
            tvec: Translation vector
        :return: 2D image points (pixels)
        """
        assert points3d.shape[1] == 3
        if rvec is None:
            rvec = np.zeros(3, dtype=np.float32)
        if tvec is None:
            tvec = np.zeros(3, dtype=np.float32)
        points2d, _ = cv2.projectPoints(
            points3d, rvec, tvec, self.camera_matrix, self.dist_coefficients)
        return points2d.reshape(-1, 2)

    def project_point(self, point3d: np.ndarray, rvec: Optional[np.ndarray] = None, tvec: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Projects a 3D world point (metres) to a 2D image point (pixels)
        Args:
            point3d: 3D world point (metres)
            rvec: Rotation vector
            tvec: Translation vector
        :return: 2D image point (pixels)
        """
        assert point3d.shape == (3,)
        return self.project_points(point3d[np.newaxis], rvec, tvec)[0]
