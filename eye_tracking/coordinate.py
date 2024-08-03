"""
Defines a class for a coordinate system
"""

import cv2.typing as cv_t

from typing import Tuple


class Coordinate:
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
