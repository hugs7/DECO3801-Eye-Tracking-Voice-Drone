"""
Defines abstract class for drones
"""

from abc import ABC, abstractmethod
from typing import Tuple
import cv2


class Drone(ABC):
    @abstractmethod
    def __connect(self):
        pass

    @abstractmethod
    def read_camera(self):
        pass

    @abstractmethod
    def takeoff(self):
        pass

    @abstractmethod
    def land(self):
        pass

    def resize_frame(self, frame: cv2.typing.MatLike, output_dim: Tuple[int, int]) -> cv2.typing.MatLike:
        return cv2.resize(frame, output_dim)
