"""
Defines the mapping for landmarks
"""

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

landmark_mapping = {
    "eyebrow": {
        "left": [70, 63, 105, 66, 65, 52, 53],
        "right": [336, 296, 334, 293, 300, 276, 283, 282, 295],
    },
    "lips": [39, 37, 267],
    "moustache": [],
}
