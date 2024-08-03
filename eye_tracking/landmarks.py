"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Tuple, Union, TypedDict, Optional

import numpy as np

import constants
from colours import Colour
import coordinate

import utils.list_helper as list_helper
import utils.dict_helper as dict_helper

from custom_types.NormalisedLandmark import NormalisedLandmark


class EyePoints:
    def __init__(self, centre: int, right: int, top: int, left: int, bottom: int):
        self.centre = centre
        self.right = right
        self.top = top
        self.left = left
        self.bottom = bottom

    def get_side(self, side: str):
        if side == "right":
            return self.right
        elif side == "top":
            return self.top
        elif side == "left":
            return self.left
        elif side == "bottom":
            return self.bottom
        elif side == "centre":
            return self.centre
        else:
            raise ValueError(f"Invalid side: {side}")


class EyeLandmarks:
    def __init__(self, name: str, colour: Colour, points: EyePoints):
        self.name = name
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
        eyes = []
        for eye_data in eyes_data:
            dict_helper.check_property_exists(eye_data, "name", "eye class")
            dict_helper.check_property_exists(eye_data, "colour", "eye class")
            dict_helper.check_property_exists(eye_data, "points", "eye class")

            eye_name = eye_data["name"]
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
            eye_landmarks = EyeLandmarks(eye_name, colour=eye_colour, points=eye_points)

            # Check for duplicates
            parsed_eye_points = [eye_points.centre, eye_points.right, eye_points.top, eye_points.left, eye_points.bottom]
            duplicated_points = list_helper.find_duplicates_in_list(parsed_eye_points)
            if duplicated_points:
                raise ValueError(f"Duplicated points found in eye class {eye_name}: {duplicated_points}")

            overlap = seen_points.intersection(parsed_eye_points)
            if overlap:
                raise ValueError(f"Duplicate points found in eye class {eye_name}: {overlap}")

            seen_points.update(parsed_eye_points)
            eyes.append(eye_landmarks)

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
        for eye_data in self.eyes:
            if point_id in vars(eye_data.points).values():
                return eye_data

        # Search in face landmarks
        for face_part in self.face:
            if point_id in face_part.points:
                return face_part

        return None

    def get_part_by_name(self, part_name: str) -> Optional[Union[EyeLandmarks, FacePart]]:
        """
        Get a part by its name
        :param part_name: The name of the part
        :return: The part or None if not found
        """

        # Search in eye landmarks
        for eye_data in self.eyes:
            if eye_data.name == part_name:
                return eye_data

        # Search in face landmarks
        for face_part in self.face:
            if face_part.name == part_name:
                return face_part

        return None


def normalise_landmark(landmark, frame_dim: coordinate.Coordinate3D) -> coordinate.Coordinate3D:
    """
    Normalise a landmark to the width and height of the frame
    :param landmark: The landmark to normalise
    :param frame_dim: The dimensions of the frame
    :return Coordinate: The normalised landmark
    """

    x = int(landmark.x * frame_dim.x)
    y = int(landmark.y * frame_dim.y)
    z = int(landmark.z * frame_dim.z)

    return coordinate.Coordinate3D(x, y, z)


def get_image_coord_of_landmark(face_landmarks: List[NormalisedLandmark], landmark_id: int, frame_dim: np.ndarray) -> Tuple[int, int]:
    """
    Get the image coordinates of a landmark
    :param face_landmarks: The face landmarks
    :param landmark_id: The landmark id
    :param frame_dim: The dimensions of the frame
    :return Tuple[int, int]: The image coordinates
    """

    lmk_pick = face_landmarks[landmark_id]
    normalised_landmark = normalise_landmark(lmk_pick, frame_dim)

    return normalised_landmark.to_tuple()
