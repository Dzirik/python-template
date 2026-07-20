"""
Sanity tests for the COLORS palette used by all plotly-based plots.
"""

from src.visualisations.colors import COLORS


class TestColors:
    """Tests for the COLORS dictionary structure."""

    def test_required_keys_present(self) -> None:
        """COLORS must define every key consumed by PlotlyBase and its subclasses."""
        for key in ("line", "fill", "error", "dot", "paper_background", "grid_background", "vertical_line"):
            assert key in COLORS

    def test_vertical_line_key_is_non_empty_list(self) -> None:
        """The vertical_line key (Wave 1 fix) must be a non-empty list of colors, not missing."""
        assert isinstance(COLORS["vertical_line"], list)
        assert len(COLORS["vertical_line"]) > 0

    def test_background_entries_have_color_and_opacity(self) -> None:
        """paper_background and grid_background must each carry color + opacity."""
        for key in ("paper_background", "grid_background"):
            assert "color" in COLORS[key]
            assert "opacity" in COLORS[key]
