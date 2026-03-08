"""
Functions for visualisations.
"""

from datetime import datetime
from typing import Any

import numpy as np
from numpy import sin
from pandas import Series


def hex_to_rgb(color: str, opacity: float = 1) -> str:
    """
    Returns a color in format rgba (red, green, blue, alpha/opacity) for the color given in hex format (#rrggbb).
    :param color: str. Color in format #rrggbb.
    :param opacity: int. Opacity value in range [0, 1].
    :return: str. String in the format rgba.
    """
    color = color.lstrip("#")
    len_color = len(color)
    rgb = tuple(int(color[i : i + len_color // 3], 16) for i in range(0, len_color, len_color // 3))
    rgb_opacity = (*rgb, opacity)

    return "rgba" + str(rgb_opacity)


def create_time_series(seed_number: int = 3872, x_multiplier: float = 1, name: str | None = None) -> Series:
    """
    Generates a pandas time series, uses sin(x_multiplier * range(..)) plus some random part.
    :param seed_number: int. Seed for random part.
    :param x_multiplier: float. See the description above.
    :return: pd.Series.
    """
    n = 30

    datetime_index = [datetime(2020, 1, i) for i in range(1, n + 1, 1)]

    rng = np.random.default_rng(seed_number)
    data = [15 + 5 * sin(x_multiplier * x) + rng.standard_normal() for x in range(n)]

    return Series(data=data, index=datetime_index, name=name)


def get_colors_for_level(fill_color: str) -> dict[str, Any]:
    """
    Gets the colors for levels.
    :param fill_color: str. "green", "red", "blue", "purple"
    """
    color_dict = {"green": "#99AA38", "red": "#ED254E", "blue": "#1338BE", "purple": "#AF69EE", "": "#0f0f0f"}
    return {
        "line": ["#0f0f0f"],
        "fill": [color_dict[fill_color]],
        "paper_background": {"color": "#000000", "opacity": 0},
        "grid_background": {"color": "#858B97", "opacity": 0.4},
        "error": ["#ED254E", "#C81D25"],
        "dot": ["#99AA38", "#ED254E", "#ACD2ED"],
    }
