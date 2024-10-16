"""
Defines abstract class for drones
"""

from abc import ABC, abstractmethod
from typing import Tuple

import cv2


class Drone(ABC):
    @abstractmethod
    def connect(self):
        """
        Connects to the drone
        """
        pass

    @abstractmethod
    def read_camera(self) -> Tuple[bool, cv2.typing.MatLike]:
        """
        Reads the camera feed from the drone

        Returns:
            Tuple[bool, cv2.typing.MatLike]: A tuple containing a boolean indicating
             - ok: if the read was successful and the image read
             - img: the image read
        """
        pass

    # Controlling methods
    @abstractmethod
    def rotate_clockwise(self, degrees: int) -> None:
        """Rotate the drone clockwise by the specified number of degrees.

        Args:
            degrees (int): The number of degrees to rotate the drone.

        Returns:
            None
        """
        pass

    @abstractmethod
    def rotate_counter_clockwise(self, degrees: int) -> None:
        """Rotate the drone counterclockwise by the specified number of degrees.

        Args:
            degrees (int): The number of degrees to rotate the drone.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_up(self, cm: int) -> None:
        """Move the drone up by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone up.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_down(self, cm: int) -> None:
        """Move the drone down by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone down.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_left(self, cm: int) -> None:
        """Move the drone left by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone left.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_right(self, cm: int) -> None:
        """Move the drone right by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone right.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_forward(self, cm: int) -> None:
        """Move the drone forward by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone forward.

        Returns:
            None
        """
        pass

    @abstractmethod
    def move_backward(self, cm: int) -> None:
        """Move the drone backward by the specified magnitude.

        Args:
            cm (int): The number of cm to move the drone backward.

        Returns:
            None
        """
        pass

    @abstractmethod
    def takeoff(self) -> None:
        """Perform the takeoff operation for the drone.

        Returns:
            None
        """
        pass

    @abstractmethod
    def land(self) -> None:
        """Land the drone.

        Returns:
            None
        """
        pass

    # Polling methods
    @abstractmethod
    def get_height(self) -> int:
        """Get the altitude of the drone.

        Returns:
            int: The altitude of the drone.
        """
        pass
