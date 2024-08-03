"""
Defines some colours
"""

from typing import Tuple

import math_utils

MIN_COLOUR_VALUE = 0
MAX_COLOUR_VALUE = 255


class Colour:
    def __init__(self, name: str, red: int, green: int, blue: int) -> None:
        self.name = name

        self.red = red
        self.green = green
        self.blue = blue

        # Check values
        if not self._is_valid_colour_value(red):
            raise ValueError(f"Invalid red value {red}")

    def _is_valid_colour_value(self, value: int) -> bool:
        """
        Check if a colour value is valid
        :param value: The colour value
        :return: True if the value is valid, False otherwise
        """

        return math_utils.in_range(value, MIN_COLOUR_VALUE, MAX_COLOUR_VALUE)

    def get_colour(self) -> Tuple[int, int, int]:
        """
        Returns colour as rgb tuple
        :return Tuple[int, int, int]: The colour as an RGB tuple
        """

        return self.red, self.green, self.blue


class ColourMap:
    red = Colour("red", 0, 0, 255)
    green = Colour("green", 0, 255, 0)
    blue = Colour("blue", 255, 0, 0)
    yellow = Colour("yellow", 226, 235, 52)
    lime = Colour("lime", 153, 235, 52)
    light_green = Colour("light_green", 104, 235, 5)
    spring_green = Colour("spring_green", 52, 235, 76)
    forest_green = Colour("forest_green", 52, 235, 104)
    torquoise = Colour("torquoise", 52, 235, 174)
    cyan = Colour("cyan", 52, 229, 235)
    sky_blue = Colour("sky_blue", 52, 162, 235)
    cornflower_blue = Colour("cornflower_blue", 52, 116, 235)
    royal_blue = Colour("royal_blue", 52, 52, 235)
    navy_blue = Colour("navy_blue", 116, 52, 235)
    purple = Colour("purple", 162, 52, 235)
    magenta = Colour("magenta", 235, 52, 229)
    pink = Colour("pink", 235, 52, 162)
    coral = Colour("coral", 235, 52, 116)
    orange = Colour("orange", 235, 104, 52)
    brown = Colour("brown", 235, 162, 52)
    gold = Colour("gold", 235, 229, 52)
    white = Colour("white", 255, 255, 255)
    black = Colour("black", 0, 0, 0)
