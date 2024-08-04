"""
Module to help with eye tracking calibration
"""

from typing import Dict, List, Optional, Tuple, Union, TypedDict
from enum import Enum
import cv2

import draw
import landmarks
import constants
import coordinate
from custom_types.NormalisedLandmark import NormalisedLandmark
from colours import ColourMap as CM


class CalibrationStep(Enum):
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    MIDDLE_TOP = "middle-top"
    MIDDLE_BOTTOM = "middle-bottom"
    MIDDLE_LEFT = "middle-left"
    MIDDLE_RIGHT = "middle-right"


calibration_order = [
    CalibrationStep.CENTER,
    CalibrationStep.TOP_LEFT,
    CalibrationStep.TOP_RIGHT,
    CalibrationStep.BOTTOM_LEFT,
    CalibrationStep.BOTTOM_RIGHT,
    CalibrationStep.MIDDLE_TOP,
    CalibrationStep.MIDDLE_BOTTOM,
    CalibrationStep.MIDDLE_LEFT,
    CalibrationStep.MIDDLE_RIGHT,
]


def get_next_calibration_step(step: CalibrationStep) -> Optional[CalibrationStep]:
    """
    Get the next calibration step
    :param step: The current step
    :return: The next step
    """
    current_index = calibration_order.index(step)
    next_index = current_index + 1
    if next_index >= len(calibration_order):
        return None

    return calibration_order[next_index]


class EyeCalibrationData:
    def __init__(
        self,
        eye: Dict[str, List[Tuple[int, int]]],
        upper_eyelid: List[Tuple[int, Tuple[int, int]]],
        lower_eyelid: List[Tuple[int, Tuple[int, int]]],
    ):
        reference_point = upper_eyelid[0][1]

        self.eye = self._transform_coordinates(eye, reference_point)
        self.upper_eyelid = self._transform_list_of_tuples(upper_eyelid, reference_point)
        self.lower_eyelid = self._transform_list_of_tuples(lower_eyelid, reference_point)

    def _transform_coordinates(
        self, coordinates: Dict[str, List[Tuple[int, int]]], reference_point: Tuple[int, int]
    ) -> Dict[str, Tuple[int, int]]:
        """Transform coordinates by subtracting the reference point."""
        return {k: (v[0] - reference_point[0], v[1] - reference_point[1]) for k, v in coordinates.items()}

    def _transform_list_of_tuples(
        self, coordinates: List[Tuple[int, Tuple[int, int]]], reference_point: Tuple[int, int]
    ) -> List[Tuple[int, Tuple[int, int]]]:
        """Transform a list of tuples by subtracting the reference point."""
        return [(k, (v[0] - reference_point[0], v[1] - reference_point[1])) for k, v in coordinates]

    def __str__(self):
        return f"Eye: {self.eye}\n\tUpper eyelid: {self.upper_eyelid},\n\tLower eyelid: {self.lower_eyelid}"


class EyeCalibrationSideData(TypedDict):
    points: List[int]
    data: EyeCalibrationData


class EyePosition:
    def __init__(
        self,
        top: NormalisedLandmark,
        bottom: NormalisedLandmark,
        left: NormalisedLandmark,
        right: NormalisedLandmark,
        centre: NormalisedLandmark,
    ):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.centre = centre


class CalibrationData:
    def __init__(self, landmark_mapping: landmarks.Landmarks, frame_dim: coordinate.Coordinate2D):
        self.landmark_mapping = landmark_mapping
        self.frame_dim = frame_dim

        # Boolean for if user is looking straight ahead. User will need to
        # keep their head straight during calibration
        self.looking_straight: bool = True
        self.eye_calibration: Dict[CalibrationStep, Dict[str, EyeCalibrationSideData]] = {}
        self.step = calibration_order[0]

        self.eye_centre_reference: Dict[str, Dict[str, List[Tuple[int, Tuple[int, int]]]]] = {}

    def calculate_eye_centre_reference(self) -> Dict[str, Tuple[int, int]]:
        """
        Calculate a reference for the eye centre when the user is looking at the centre dot
        relative to the upper and lower eyelids. This will be our 3D reference point
        during solving the pnp gaze estimation problem
        :return: The reference point
        """

        eye_centre_reference_data = {}

        centre_step_data = self.eye_calibration[CalibrationStep.CENTER]
        if not centre_step_data:
            raise ValueError("No centre point found")

        # Remember, just look at centre calibration point for now
        for side, eye_side_cal_data in centre_step_data.items():
            eye_cal_data = eye_side_cal_data["data"]
            eye_data = eye_cal_data.eye
            upper_eyelid = eye_cal_data.upper_eyelid
            lower_eyelid = eye_cal_data.lower_eyelid

            eye_centre_point = eye_data.get("centre")

            side_ref_data = {}
            # Now, for each point in the upper and lower eyelids, calculate the
            # x and y distance to the centre of the eye
            side_ref_data["upper_eyelid"] = []
            for point in upper_eyelid:
                diff = coordinate.coord_difference(eye_centre_point, point[1])
                # Add z coordinate as 0
                diff = (diff[0], diff[1], 0)
                side_ref_data["upper_eyelid"].append((point[0], diff))

            side_ref_data["lower_eyelid"] = []
            for point in lower_eyelid:
                diff = coordinate.coord_difference(eye_centre_point, point[1])
                # Add z coordinate as 0
                diff = (diff[0], diff[1], 0)
                side_ref_data["lower_eyelid"].append((point[0], diff))

            eye_centre_reference_data[side] = side_ref_data

        self.eye_centre_reference = eye_centre_reference_data

    def __str__(self):
        string = "Calibration Data\n"

        for step, step_data in self.eye_calibration.items():
            string += f"Step: {step}\n"

            for side, eye_data in step_data.items():
                string += f"Side: {side}\n"

                string += f"{eye_data['data']}\n"

            string += "----------------\n"

        return string

    def set_calibration(self, side: str, eye_calibration_data: Dict[str, Union[List[int], int]], eye_point_ids: List[int]):
        """
        Set the calibration data for an eye
        :param side: The side of the eye
        :param data: The calibration data
        :return: None
        """

        eye = eye_calibration_data["eye"]
        upper_eyelid = eye_calibration_data["upper_eyelid"]
        lower_eyelid = eye_calibration_data["lower_eyelid"]

        eye_calibration_data = EyeCalibrationData(eye, upper_eyelid, lower_eyelid)

        # Add to the calibration data
        if not self.eye_calibration.get(self.step):
            self.eye_calibration[self.step] = {}

        eye_calibration_side_data: EyeCalibrationSideData = {"points": eye_point_ids, "data": eye_calibration_data}
        self.eye_calibration[self.step][side] = eye_calibration_side_data


def calibrate_init(landmark_mapping: landmarks.Landmarks, frame_dim: coordinate.Coordinate2D) -> CalibrationData:
    """
    Initialises the calibration. Creates a CalibrationData object for the calibration process
    :param landmark_mapping: The mapping of landmarks
    :param frame_dim: The dimensions of the frame
    :return: A new CalibrationData object
    """

    calibration_data = CalibrationData(landmark_mapping, frame_dim)
    return calibration_data


def perform_calibration(
    face_landmarks: List[NormalisedLandmark], calibration_data: CalibrationData, frame: cv2.VideoCapture, frame_dim: coordinate.Coordinate2D
) -> Tuple[bool, bool]:
    """
    Perform the calibration
    :param face_landmarks: The landmarks from the face mesh
    :param calibration_data: The calibration data
    :param frame: The frame to draw on
    :return: Tuple[bool, bool]: Whether calibrating and whether calibrated
    """

    draw.render_calibration_grid(frame, frame_dim, calibration_data.step)

    key = cv2.waitKey(1) & 0xFF
    if key != 255:
        print(f"Key: {key}")

    if key == ord(constants.BACKSPACE_KEY):
        # Continue with calibration
        next_step = get_next_calibration_step(calibration_data.step)
        if next_step is None:
            # Calculate reference points
            calibration_data.calculate_eye_centre_reference()

            print("Calibration complete")
            # Output calibration data

            return False, True
        else:
            # Capture data from the current step
            # We need to capture (for each eye) the top, bottom, left, right, and centre points
            # as well as the coordinates of the positions around the eye

            ref_regions = [
                "upper_eyelid",
                "lower_eyelid",
            ]

            for eye in ["left", "right"]:
                eye_point_ids: List[int] = []

                eye_calibration_data: Dict[str, Union[List[int], int]] = {}

                # Collect reference points (around eye)
                for ref_pos in ref_regions:
                    side_ref_pos = f"{ref_pos}_{eye}"
                    ref_landmark = calibration_data.landmark_mapping.get_part_by_name(side_ref_pos)
                    ref_points = ref_landmark.points
                    eye_calibration_data[ref_pos] = []
                    for landmark_id in ref_points:
                        eye_point_ids.append(landmark_id)
                        ref_landmark = landmarks.get_image_coord_of_landmark(face_landmarks, landmark_id, frame_dim)
                        ref_lmk_with_id = (landmark_id, ref_landmark)
                        eye_calibration_data[ref_pos].append(ref_lmk_with_id)

                eye_landmarks = calibration_data.landmark_mapping.get_part_by_name(eye)
                eye_points = eye_landmarks.points

                # Collect eye points
                eye_calibration_data["eye"] = {}
                for pos in ["top", "bottom", "left", "right", "centre"]:
                    pos_id = eye_points.get_side(pos)
                    eye_point_ids.append(pos_id)
                    landmark_coord = landmarks.get_image_coord_of_landmark(face_landmarks, pos_id, frame_dim)
                    eye_calibration_data["eye"][pos] = landmark_coord

                # Save to calibration data
                calibration_data.set_calibration(eye, eye_calibration_data, eye_point_ids)

            calibration_data.step = next_step
            print(f"Moving to next calibration step: {calibration_data.step}")

    elif key == ord("q") or key == ord(constants.ESCAPE_KEY):
        print("Calibration cancelled")
        calibration_data.step = CalibrationStep.CENTER
        calibration_data.looking_straight = True
        return False, False

    return True, False
