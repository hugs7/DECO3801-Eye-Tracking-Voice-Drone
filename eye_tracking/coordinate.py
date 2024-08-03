"""
Defines a class for a coordinate system
"""

from typing import Tuple


class Coordinate:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def get_coordinates(self) -> Tuple[float, float]:
        """
        Returns the coordinates as a tuple
        :return Tuple[float, float]: The coordinates as a tuple
        """
        return self.x, self.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
