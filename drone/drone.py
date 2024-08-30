"""
Defines abstract class for drones
"""

from abc import ABC, abstractmethod


class Drone(ABC):
    @abstractmethod
    def connect(self):
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
