"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Union, TypedDict, Optional

import constants
from colours import Colour
import coordinate

import utils.list_helper as list_helper
import utils.dict_helper as dict_helper


class EyePoints:
    def __init__(self, centre: int, right: int, top: int, left: int, bottom: int):
        self.centre = centre
        self.right = right
        self.top = top
        self.left = left
        self.bottom = bottom


class EyeLandmarks:
    def __init__(self, colour: Colour, points: EyePoints):
        self.colour = colour
        self.points = points


class FacePart:
    def __init__(self, name: str, colour: Colour, points: List[int]):
        self.name = name
        self.colour = colour
        self.points = points


class LandmarkMapping(TypedDict):
    eyes: Dict[str, EyeLandmarks]
    face: List[FacePart]


class Landmarks:
    def __init__(self, landmark_mapping_data: Dict[str, Dict[str, Union[Dict, List]]]):
        seen_points = set()

        # === Eyes ===
        if "eyes" not in landmark_mapping_data:
            raise ValueError("landmark_mapping must have an 'eyes' property")

        eyes_data = landmark_mapping_data["eyes"]
        eyes = {}
        for eye_name, eye_data in eyes_data.items():
            dict_helper.check_property_exists(eye_data, "colour", "eye class")
            dict_helper.check_property_exists(eye_data, "points", "eye class")

            eye_colour = Colour.parse_colour(eye_data)
            eye_points_data = eye_data["points"]

            for expected_key in ["centre", "right", "top", "left", "bottom"]:
                dict_helper.check_property_exists(eye_points_data, expected_key, "eye class")

            eye_points = EyePoints(
                centre=eye_points_data["centre"],
                right=eye_points_data["right"],
                top=eye_points_data["top"],
                left=eye_points_data["left"],
                bottom=eye_points_data["bottom"],
            )
            eye_landmarks = EyeLandmarks(colour=eye_colour, points=eye_points)

            # Check for duplicates
            parsed_eye_points = [eye_points.centre, eye_points.right, eye_points.top, eye_points.left, eye_points.bottom]
            duplicated_points = list_helper.find_duplicates_in_list(parsed_eye_points)
            if duplicated_points:
                raise ValueError(f"Duplicated points found in eye class {eye_name}: {duplicated_points}")

            overlap = seen_points.intersection(parsed_eye_points)
            if overlap:
                raise ValueError(f"Duplicate points found in eye class {eye_name}: {overlap}")

            seen_points.update(parsed_eye_points)
            eyes[eye_name] = eye_landmarks

        # === Face ===
        if "face" not in landmark_mapping_data:
            raise ValueError("landmark_mapping must have a 'face' property")

        face_data = landmark_mapping_data["face"]
        face = []
        for face_part_data in face_data:
            dict_helper.check_property_exists(face_part_data, "name", "face part")
            dict_helper.check_property_exists(face_part_data, "colour", "face part")
            dict_helper.check_property_exists(face_part_data, "points", "face part")

            face_part_colour = Colour.parse_colour(face_part_data)
            face_part = FacePart(
                name=face_part_data["name"],
                colour=face_part_colour,
                points=face_part_data["points"],
            )

            # Check for duplicates
            duplicated_points = list_helper.find_duplicates_in_list(face_part.points)
            if duplicated_points:
                raise ValueError(f"Duplicated points found in face part {face_part.name}: {duplicated_points}")

            overlap = seen_points.intersection(face_part.points)
            if overlap:
                raise ValueError(f"Duplicate points found in face part {face_part.name}: {overlap}")

            seen_points.update(face_part.points)
            face.append(face_part)

        self.eyes = eyes
        self.face = face
        self.landmark_mapping: LandmarkMapping = {"eyes": eyes, "face": face}

    def classify_point(self, point_id: int) -> Optional[Union[EyeLandmarks, FacePart]]:
        """
        Takes a point id and returns its class (e.g., "eyebrow_left")
        :param point_id: The point id
        :return: The class of the point or None if not found
        """

        # Search in eye landmarks
        for eye, eye_data in self.eyes.items():
            if point_id in vars(eye_data.points).values():
                return eye_data

        # Search in face landmarks
        for face_part in self.face:
            if point_id in face_part.points:
                return face_part

        return None


def normalise_landmark(landmark, frame_dim: coordinate.Coordinate) -> coordinate.Coordinate:
    """
    Normalise a landmark to the width and height of the frame
    :param landmark: The landmark to normalise
    :param frame_dim: The dimensions of the frame
    :return Coordinate: The normalised landmark
    """

    x = int(landmark.x * frame_dim.x)
    y = int(landmark.y * frame_dim.y)

    return coordinate.Coordinate(x, y)
