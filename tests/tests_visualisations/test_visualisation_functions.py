"""
Tests for the pure helper functions in src/visualisations/visualisation_functions.py.
"""

from pandas import Series

from src.visualisations.visualisation_functions import create_time_series, get_colors_for_level, hex_to_rgb


class TestHexToRgb:
    """Tests for hex_to_rgb."""

    def test_black_full_opacity(self) -> None:
        """#000000 with opacity 1 converts to rgba(0, 0, 0, 1)."""
        assert hex_to_rgb("#000000", 1) == "rgba(0, 0, 0, 1)"

    def test_white_default_opacity(self) -> None:
        """#ffffff with the default opacity (1) converts to rgba(255, 255, 255, 1)."""
        assert hex_to_rgb("#ffffff") == "rgba(255, 255, 255, 1)"

    def test_arbitrary_color_with_partial_opacity(self) -> None:
        """A mid-range hex color with fractional opacity is converted component-wise."""
        assert hex_to_rgb("#087E8B", 0.25) == "rgba(8, 126, 139, 0.25)"


class TestCreateTimeSeries:
    """Tests for create_time_series."""

    def test_returns_series_of_expected_length(self) -> None:
        """The generated series has 30 points (fixed n in the implementation)."""
        series = create_time_series()
        assert isinstance(series, Series)
        assert len(series) == 30

    def test_name_is_propagated(self) -> None:
        """The optional name parameter is set on the returned Series."""
        series = create_time_series(name="my_series")
        assert series.name == "my_series"

    def test_seed_is_deterministic(self) -> None:
        """Same seed_number produces identical data."""
        series_a = create_time_series(seed_number=42)
        series_b = create_time_series(seed_number=42)
        assert (series_a.to_numpy() == series_b.to_numpy()).all()


class TestGetColorsForLevel:
    """Tests for get_colors_for_level."""

    def test_known_color_key_resolves(self) -> None:
        """A known color name resolves to the matching fill hex code."""
        colors = get_colors_for_level("green")
        assert colors["fill"] == ["#99AA38"]

    def test_result_includes_vertical_line_key(self) -> None:
        """
        The returned dict must include vertical_line (Wave 1 fix) so combining with
        vertical_lines_positions never raises KeyError.
        """
        colors = get_colors_for_level("red")
        assert "vertical_line" in colors
        assert isinstance(colors["vertical_line"], list)
        assert len(colors["vertical_line"]) > 0

    def test_empty_string_key_resolves_to_default(self) -> None:
        """An empty fill_color string resolves to the default color entry."""
        colors = get_colors_for_level("")
        assert colors["fill"] == ["#0f0f0f"]
