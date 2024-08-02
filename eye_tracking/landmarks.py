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

face_landmarks = [i for i in range(0, 468)]


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
    "upper_eyelid_left": {
        "colour": CM.royal_blue,
        "points": [157, 158, 159, 470, 247, 113, 30, 29, 27, 28, 56, 190, 160, 161, 146, 33, 130, 246],
    },
    "lower_eyelid_left": {
        "colour": CM.royal_blue,
        "points": [25, 110, 24, 472, 23, 145, 153, 22, 26, 154, 112, 173, 343, 144, 163, 226, 7],
    },
    "under_eye_left": {
        "colour": CM.cornflower_blue,
        "points": [31, 111, 228, 229, 230, 231, 232, 233, 244, 120, 121, 128, 245, 100, 47, 114, 188],
    },
    "under_eye_ight": {"colour": CM.cornflower_blue, "points": [357, 350, 277, 349, 329, 348, 347, 449, 450, 451, 452, 253, 254, 339, 448]},
    "eyesocket_outside_left": {"colour": CM.coral, "points": [124, 35, 111, 46]},
    "above_eye_left": {"colour": CM.white, "points": [225, 224, 223, 222, 221, 189]},
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
    "nose_lower": {
        "colour": CM.yellow,
        "points": [
            142,
            126,
            217,
            174,
            196,
            197,
            419,
            399,
            437,
            335,
            371,
            209,
            198,
            236,
            3,
            195,
            248,
            456,
            420,
            49,
            131,
            134,
            51,
            5,
            281,
            363,
            360,
            115,
            220,
            45,
            4,
            275,
            440,
            344,
            279,
            44,
            1,
            429,
        ],
    },
    "nostrils": {},
    "tear_trough_left": {"colour": CM.cornflower_blue, "points": [243, 155, 133]},
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
            182,
            96,
            57,
            36,
        ],
    },
    "cheek_right": {
        "colour": CM.magenta,
        "points": [
            365,
            397,
            288,
            355,
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
    "philtrum": {"colour": CM.gold, "points": [167, 164, 393]},
    "upper_lip": {"colour": CM.forest_green, "points": [186, 92, 391, 322, 410, 287]},
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


def check_duplicates_in_list(lst: List[int], num_to_check: int):
    """
    Check if a number is in a list more than once
    """

    if lst.count(num_to_check) > 1:
        print(f"Duplicate point found: {num_to_check}")


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
