"""
Defines abstract class for drones
"""

from abc import ABC, abstractmethod
from typing import Tuple
import cv2


class Drone(ABC):
    @abstractmethod
    def _connect(self):
        pass

    @abstractmethod
    def read_camera(self):
        pass

    def resize_frame(self, frame: cv2.typing.MatLike, output_dim: Tuple[int, int]) -> cv2.typing.MatLike:
        return cv2.resize(frame, output_dim)

    # Controlling methods
    @abstractmethod
    def rotate_clockwise(self, degrees: int) -> None:
        """
        Rotates the drone clockwise by the specified number of degrees
        :param degrees: The number of degrees to rotate the drone
        :return: None
        """
        pass

    @abstractmethod
    def rotate_counter_clockwise(self, degrees: int) -> None:
        """
        Rotates the drone counter clockwise by the specified number of degrees
        ::param cm: The number of cm to move the drone
        :return: None
        """
        pass

    @abstractmethod
    def move_up(self, cm: int) -> None:
        """
        Moves the drone up by the specified magnitude.
        ::param cm: The number of cm to move the drone up
        :return: None
        """
        pass

    @abstractmethod
    def move_down(self, cm: int) -> None:
        """
        Moves the drone down by the specified magnitude.
        ::param cm: The number of cm to move the drone down
        :return: None
        """
        pass

    @abstractmethod
    def move_left(self, cm: int) -> None:
        """
        Moves the drone left by the specified magnitude.
        ::param cm: The number of cm to move the drone left
        :return: None
        """
        pass

    @abstractmethod
    def move_right(self, cm: int) -> None:
        """
        Moves the drone right by the specified magnitude.
        ::param cm: The number of cm to move the drone right
        :return: None
        """
        pass

    @abstractmethod
    def move_forward(self, cm: int) -> None:
        """
        Moves the drone forward by the specified magnitude.
        ::param cm: The number of cm to move the drone forward
        :return: None
        """
        pass

    @abstractmethod
    def move_backward(self, cm: int) -> None:
        """
        Moves the drone backward by the specified magnitude.
        ::param cm: The number of cm to move the drone backward
        :return: None
        """
        pass

    @abstractmethod
    def takeoff(self) -> None:
        """
        Performs the takeoff operation for the drone
        :return: None
        """
        pass

    @abstractmethod
    def land(self) -> None:
        """
        Lands the drone
        :return: None
        """
        pass

    # Polling methods
    @abstractmethod
    def get_altitude(self) -> int:
        """
        Gets the altitude of the drone
        :return: The altitude of the drone
        """
        pass
