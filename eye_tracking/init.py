"""
Initialises the eye_tracking package.
"""

import os
import file_helper
from constants import MAPPINGS_FOLDER


def eye_tracking_init():
    """
    Initialises the eye tracking package
    """

    LANDMARK_MAPPING_PATH = os.path.join(MAPPINGS_FOLDER, "landmark_mapping.json")

    landmark_mapping = file_helper.load_json(LANDMARK_MAPPING_PATH)
