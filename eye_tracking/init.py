"""
Initialises the eye_tracking package.
"""

import os
import utils.file_helper as file_helper

import constants
import landmarks
from colours import ColourMap as CM, Colour


def eye_tracking_init() -> landmarks.FaceLandmarks:
    """
    Initialises the eye tracking package
    """

    LANDMARK_MAPPING_PATH = file_helper.resolve_path(os.path.join(constants.MAPPINGS_FOLDER, "landmark_mapping.json"))

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)
    lmks = landmarks.FaceLandmarks(landmark_mapping)

    return lmks
