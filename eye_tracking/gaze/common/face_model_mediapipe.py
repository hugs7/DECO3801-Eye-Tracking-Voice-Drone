"""
MediaPipe 3D face model for 468 points mark-up.
Author: Hugo Burton
Last Updated: 21/08/2024
"""

import numpy as np

from .face_model import FaceModel


class FaceModelMediaPipe(FaceModel):
    """3D face model for MediaPipe 468 points mark-up.

    In the camera coordinate system, the X axis points to the right from
    camera, the Y axis points down, and the Z axis points forward.

    The face model is facing the camera. Here, the Z axis is
    perpendicular to the plane passing through the three midpoints of
    the eyes and mouth, the X axis is parallel to the line passing
    through the midpoints of both eyes, and the origin is at the tip of
    the nose.

    The units of the coordinate system are meters and the distance
    between outer eye corners of the model is set to 90mm.

    The model coordinate system is defined as the camera coordinate
    system rotated 180 degrees around the Y axis.
    """

    def __init__(self) -> None:
        REYE_INDICES: np.ndarray = np.array([33, 133])
        LEYE_INDICES: np.ndarray = np.array([362, 263])
        MOUTH_INDICES: np.ndarray = np.array([78, 308])
        NOSE_INDICES: np.ndarray = np.array([240, 460])

        CHIN_INDEX: int = 199
        NOSE_INDEX: int = 1

        super().__init__(
            REYE_INDICES,
            LEYE_INDICES,
            MOUTH_INDICES,
            NOSE_INDICES,
            CHIN_INDEX,
            NOSE_INDEX,
        )
