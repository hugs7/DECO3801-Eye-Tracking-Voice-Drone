"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Union, TypedDict, Optional

from colours import ColourMap as CM, Colour


class FaceLandmarkData(TypedDict):
    colour: Colour
    points: List[int]


class EyePoints(TypedDict):
    centre: int
    right: int
    top: int
    left: int
    bottom: int


class EyeLandmarkData(TypedDict):
    colour: Colour
    points: EyePoints


EyeLandmarkMapping = Dict[str, EyeLandmarkData]
FaceLandmarkMapping = Dict[str, FaceLandmarkData]


class LandmarkMapping(TypedDict):
    eyes: EyeLandmarkMapping
    face: FaceLandmarkMapping


class FaceLandmarks:
    def __init__(self, landmark_mapping: LandmarkMapping):
        self.landmark_mapping = landmark_mapping

    def classify_point(self, point_id: int) -> Optional[str]:
        """
        Takes a point id and returns its class (e.g., "eyebrow_left")
        """
        for key, value in self.landmark_mapping.items():
            # Handle eye points separately
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if point_id in subvalue["points"].values():
                        return f"{key}_{subkey}"
            # Handle face points
            else:
                if point_id in value["points"]:
                    return key
        return None

    def check_for_duplicate_points(self):
        """
        Check for duplicate points in the landmark_mapping
        """
        points = set()
        duplicates = set()

        for key, value in self.landmark_mapping.items():
            # Handle eye points separately
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    for point in subvalue["points"].values():
                        if point in points:
                            duplicates.add(point)
                        else:
                            points.add(point)
            # Handle face points
            else:
                for point in value["points"]:
                    if point in points:
                        duplicates.add(point)
                    else:
                        points.add(point)

        if duplicates:
            print(f"Duplicate points found: {duplicates}")
        else:
            print("No duplicate points found")
