"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Union, TypedDict, Optional

import constants
import list_helper
import dict_helper
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
        # === Eyes ===
        dict_helper.check_property_exists(landmark_mapping, "eyes", "landmark_mapping")

        for eye, eye_data in landmark_mapping["eyes"].items():
            dict_helper.check_property_exists(eye_data, "colour", f"eye class {eye}")
            dict_helper.check_property_exists(eye_data, "points", f"eye class {eye}")

            Colour.parse_colour(eye_data)

            # Check centre, right, top, left, bottom are present and unique
            eye_points = eye_data["points"]
            parsed_eye_points = []

            for expected_key in constants.EXPECTED_EYE_POINT_KEYS:
                dict_helper.check_property_exists(eye_points, expected_key, f"eye class {eye}")

                parsed_eye_points.append(eye_points[expected_key])

            # Check for duplicates
            duplicated_points = list_helper.find_duplicates_in_list(parsed_eye_points)
            if len(duplicated_points) > 0:
                raise ValueError(f"Duplicated points found in eye class {eye}: {duplicated_points}")

        # === Face ===
        dict_helper.check_property_exists(landmark_mapping, "face", "landmark_mapping")

        for face_part in landmark_mapping["face"]:
            dict_helper.check_property_exists(face_part, "name", f"face class {eye}")
            dict_helper.check_property_exists(face_part, "colour", f"face class {eye}")
            dict_helper.check_property_exists(face_part, "points", f"face class {eye}")

            Colour.parse_colour(eye_data)

            # Check points are a list of unique ints
            face_points = eye_data["points"]

            # Check for duplicates
            duplicated_points = list_helper.find_duplicates_in_list(face_points)
            if len(duplicated_points) > 0:
                raise ValueError(f"Duplicated points found in face class {eye}: {duplicated_points}")

        print("landmark_mapping")
        print(landmark_mapping)
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
