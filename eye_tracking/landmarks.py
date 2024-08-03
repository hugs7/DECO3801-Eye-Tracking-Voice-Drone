"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Tuple, Optional, TypedDict, Union

from colours import ColourMap as CM, Colour


class FaceLandmarkData(TypedDict):
    colour: Colour
    points: List[int]


class EyePoints(TypedDict):
    centre: int
    right: int
    top: int
    left: int
    button: int


class EyeLandmarkData(TypedDict):
    colour: Colour
    points: EyePoints


EyeLandmarkMapping = Dict[str, EyeLandmarkData]
FaceLandmarkMapping = Dict[str, FaceLandmarkData]
LandmarkMapping = Dict[str, Union[EyeLandmarkMapping, FaceLandmarkMapping]]


def classify_point(point_id: int):
    """
    Takes a point id and returns it's class (e.g. "lips")
    """

    for key, value in landmark_mapping.items():
        # Check value has a "points" key
        if "points" not in value:
            continue
        if point_id in value["points"]:
            return key

    return None


def check_for_duplicate_points():
    """
    Check for duplicate points in the landmark_mapping
    """

    points = []

    for key, value in landmark_mapping.items():
        if "points" not in value:
            continue
        for point in value["points"]:
            check_duplicates_in_list(value["points"], point)
            if point in points:
                print(f"Duplicate point found: {point}")
            else:
                points.append(point)


if __name__ == "__main__":
    check_for_duplicate_points()
