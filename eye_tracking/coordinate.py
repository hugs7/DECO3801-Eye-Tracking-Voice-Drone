"""
Defines a class for a coordinate system
"""

import cv2.typing as cv_t

from typing import Tuple


class Coordinate2D:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_tuple(self) -> Tuple[float, float]:
        """
        Returns the coordinates as a tuple
        :return Tuple[float, float]: The coordinates as a tuple
        """
        return self.x, self.y

    def to_point(self) -> cv_t.Point:
        """
        Returns the coordinates as a tuple of integers
        :return Tuple[int, int]: The coordinates as a tuple of integers
        """
        point = (int(self.x), int(self.y))
        return point

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class Coordinate3D:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def to_tuple(self) -> Tuple[float, float, float]:
        """
        Returns the coordinates as a tuple
        :return Tuple[float, float, float]: The coordinates as a tuple
        """
        return self.x, self.y, self.z

    def to_point(self) -> cv_t.Point3f:
        """
        Returns the coordinates as a tuple of integers
        :return Tuple[int, int, int]: The coordinates as a tuple of integers
        """
        point = (int(self.x), int(self.y), int(self.z))

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


def coord_difference(point_a: Tuple[int, int], point_b: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calculate the difference between two points
    :param point_a: The first point
    :param point_b: The second point
    :return: Tuple[int, int]: The x and y difference
    """

    x_diff = point_b[0] - point_a[0]
    y_diff = point_b[1] - point_a[1]

    return x_diff, y_diff
