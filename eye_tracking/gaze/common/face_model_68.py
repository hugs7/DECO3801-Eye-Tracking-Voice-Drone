import numpy as np

from .face_model import FaceModel


class FaceModel68(FaceModel):
    """3D face model for Multi-PIE 68 points mark-up.

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

    def __init__(self):
        REYE_INDICES: np.ndarray = np.array([36, 39])
        LEYE_INDICES: np.ndarray = np.array([42, 45])
        MOUTH_INDICES: np.ndarray = np.array([48, 54])
        NOSE_INDICES: np.ndarray = np.array([31, 35])

        CHIN_INDEX: int = 8
        NOSE_INDEX: int = 30

        super().__init__(
            REYE_INDICES,
            LEYE_INDICES,
            MOUTH_INDICES,
            NOSE_INDICES,
            CHIN_INDEX,
            NOSE_INDEX,
        )
