"""
Defines types for NormalisedLandmark
Defined here because it is not available in the mediapipe python package
"""


class NormalisedLandmark:
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        has_visibility: bool = False,
        visibility: float = 0.0,
        has_presence: bool = False,
        presence: float = 0.0,
        name: str = "",
    ):
        self.x = x
        self.y = y
        self.z = z
        self.has_visibility = has_visibility
        self.visibility = visibility
        self.has_presence = has_presence
        self.presence = presence
        self.name = name

    def __repr__(self):
        return f"NormalisedLandmark(name='{self.name}', x={self.x}, y={self.y}, z={self.z})"
