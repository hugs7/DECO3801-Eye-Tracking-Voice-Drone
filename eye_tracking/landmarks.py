"""
Defines the mapping for landmarks
02/08/2024
"""

from typing import Dict, List, Tuple, Optional, TypedDict

from colours import ColourMap as CM

total_landmarks = 478

eye_landmarks = {
    "left": {
        "top": 469,
        "bottom": 470,
        "left": 471,
        "right": 472,
    },
    "right": {
        "top": 473,
        "bottom": 474,
        "left": 475,
        "right": 476,
    },
}

face_landmarks = [i for i in range(0, 478)]


class LandmarkData(TypedDict, total=False):
    colour: Tuple[int, int, int]
    points: List[int]


LandmarkMapping = Dict[str, LandmarkData]

landmark_mapping = {
    "eyebrow_left": {
        "colour": CM.lime,
        "points": [70, 63, 105, 66, 65, 52, 53, 107, 55],
    },
    "eyebrow_right": {
        "colour": CM.lime,
        "points": [336, 296, 334, 293, 300, 276, 283, 282, 295],
    },
    "lips": {"colour": CM.yellow, "points": [39, 37, 267]},
    "moustache": {},
    "nose_bridge": {
        "colour": CM.sky_blue,
        "points": [
            9,
            8,
            193,
            168,
            41,
            122,
            6,
            351,
        ],
    },
    "tear_trough_left": {"colour": CM.cornflower_blue, "points": []},
    "tear_trough_right": {"colour": CM.cornflower_blue, "points": []},
    "chin": {
        "colour": CM.coral,
        "points": [
            194,
            201,
            200,
            204,
            421,
            418,
            424,
            422,
            211,
            32,
            208,
            199,
            428,
            262,
            431,
            430,
            170,
            140,
            171,
            175,
            396,
            369,
            309,
            395,
            394,
            150,
            149,
            176,
            148,
            152,
            377,
            400,
            378,
            379,
        ],
    },
    "cheek_left": {
        "colour": CM.magenta,
        "points": [
            227,
            116,
            207,
            117,
            203,
            118,
            119,
            137,
            123,
            50,
            58,
            216,
            172,
            136,
            101,
            177,
            147,
            187,
            205,
            206,
            165,
            215,
            213,
            192,
            214,
            138,
            135,
            212,
            210,
            202,
            169,
        ],
    },
    "cheek_right": {
        "colour": CM.magenta,
        "points": [
            365,
            397,
            288,
            364,
            366,
            367,
            435,
            401,
            466,
            447,
            434,
            416,
            433,
            432,
            436,
            427,
            411,
            376,
            352,
            345,
            280,
            425,
            427,
            423,
            266,
            330,
            426,
        ],
    },
    "ear_left": {"colour": CM.torquoise, "points": [234, 93, 132]},
    "ear_right": {"colour": CM.torquoise, "points": [361, 323, 454]},
    "temporal_left": {"colour": CM.gold, "points": [21, 71, 162, 139, 156, 127, 34, 143]},
    "temporal_right": {"colour": CM.gold, "points": [372, 264, 356, 383, 368, 389, 301, 251]},
    "philtrum": {"colour": CM.gold, "points": [167]},
    "forehead": {
        "colour": CM.forest_green,
        "points": [54, 68, 103, 104, 67, 69, 109, 108, 10, 151, 338, 337, 297, 299, 332, 333, 284, 298],
    },
}


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
            if point in points:
                print(f"Duplicate point found: {point}")
            else:
                points.append(point)
