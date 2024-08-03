"""
Initialises the eye_tracking package.
"""

import os
import file_helper

import constants
import list_helper
import dict_helper
import landmarks
from colours import ColourMap as CM, Colour


def parse_colour(obj: dict, colour_key: str = "colour") -> Colour:
    """
    Parses a colour name to a Colour object
    :param obj: The object to parse
    :param colour_key: The colour key. Default is "colour"
    :return None
    """

    colour_name = parse_colour(obj[colour_key])
    colour = CM.__dict__[colour_name]
    obj[colour_key] = colour


def eye_tracking_init() -> landmarks.LandmarkMapping:
    """
    Initialises the eye tracking package
    """

    LANDMARK_MAPPING_PATH = os.path.join(constants.MAPPINGS_FOLDER, "landmark_mapping.json")

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)

    # We need to parse colour names to Colour objects

    # === Eyes ===
    dict_helper.check_property_exists(landmark_mapping, "eyes", "landmark_mapping")

    for eye, eye_data in landmark_mapping["eyes"].items():
        dict_helper.check_property_exists(eye_data, "colour", f"eye class {eye}")

        parse_colour(eye_data)

        # Points
        dict_helper.check_property_exists(eye_data, "points", f"eye class {eye}")

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

    for eye, eye_data in landmark_mapping["face"].items():
        dict_helper.check_property_exists(eye_data, "colour", f"face class {eye}")

        parse_colour(eye_data)

        # Points
        dict_helper.check_property_exists(eye_data, "points", f"face class {eye}")

        # Check points are a list of unique ints
        face_points = eye_data["points"]

        # Check for duplicates
        duplicated_points = list_helper.find_duplicates_in_list(face_points)
        if len(duplicated_points) > 0:
            raise ValueError(f"Duplicated points found in face class {eye}: {duplicated_points}")

    print("landmark_mapping")
    print(landmark_mapping)

    return landmark_mapping
