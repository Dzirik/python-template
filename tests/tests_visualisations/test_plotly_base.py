"""
Smoke tests for PlotlyBase (src/visualisations/plotly_base.py) via a minimal concrete subclass.

PlotlyBase is an ABC (abstract plot()), so a trivial concrete subclass is used to exercise its
shared machinery: figure assembly, background layout, vertical line shapes (including the
Wave 1 "vertical_line" key fix), sizing, and captions.
"""

from typing import Any

import plotly.graph_objs as go
import pytest

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import get_colors_for_level


class _MinimalPlot(PlotlyBase):
    """Minimal concrete PlotlyBase subclass used only to exercise shared base behavior."""

    def plot(self, *_args: Any, **kwargs: Any) -> go.Figure | None:
        """
        Builds a trivial single-trace figure using the base class's plumbing.

        :param _args: Any. Unused positional arguments.
        :param kwargs: Any. Accepts "vertical_lines_positions" and "dashboard".
        :return: Optional[go.Figure]. See PlotlyBase.plot.
        """
        vertical_lines_positions = kwargs.get("vertical_lines_positions")
        dashboard = kwargs.get("dashboard", False)
        trace = go.Scatter(x=[1, 2, 3], y=[4, 5, 6])
        layout = {"title": "Minimal", **self._create_background_layout()}
        shapes = self._create_vertical_lines(vertical_lines_positions)
        return self._plot_single_figure(trace=trace, layout=layout, shapes=shapes, dashboard=dashboard)


class TestPlotSingleFigure:
    """Tests for PlotlyBase._plot_single_figure via _MinimalPlot.plot."""

    def test_dashboard_true_returns_figure(self) -> None:
        """dashboard=True returns a go.Figure with the expected number of traces."""
        fig = _MinimalPlot().plot(dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1

    def test_dashboard_false_shows_and_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """dashboard=False calls fig.show() and returns None (no real rendering)."""
        monkeypatch.setattr(go.Figure, "show", lambda *_args, **_kwargs: None)
        result = _MinimalPlot().plot(dashboard=False)
        assert result is None

    def test_autosize_layout_applied(self) -> None:
        """Default autosize sizing sets autosize=True and the configured height."""
        fig = _MinimalPlot().plot(dashboard=True)
        assert isinstance(fig, go.Figure)
        assert fig.layout.autosize is True

    def test_fixed_size_layout_applied(self) -> None:
        """customize_size(autosize=False, ...) sets explicit width/height on the figure."""
        plotter = _MinimalPlot()
        plotter.customize_size(autosize=False, width=640, height=480)
        fig = plotter.plot(dashboard=True)
        assert isinstance(fig, go.Figure)
        assert fig.layout.autosize is False
        assert fig.layout.width == 640
        assert fig.layout.height == 480


class TestVerticalLines:
    """Tests for PlotlyBase._create_vertical_lines, including the vertical_line key fix."""

    def test_none_positions_produce_no_shapes(self) -> None:
        """vertical_lines_positions=None → no shapes added, figure builds fine."""
        fig = _MinimalPlot().plot(dashboard=True, vertical_lines_positions=None)
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 0

    def test_positions_add_shapes_without_key_error(self) -> None:
        """vertical_lines_positions with default colors does not raise KeyError."""
        fig = _MinimalPlot().plot(dashboard=True, vertical_lines_positions=[1.5, 2.5])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2

    def test_positions_with_get_colors_for_level_do_not_raise_key_error(self) -> None:
        """Combining set_colors(get_colors_for_level(...)) with vertical_lines_positions must not KeyError."""
        plotter = _MinimalPlot()
        plotter.set_colors(get_colors_for_level("blue"))
        fig = plotter.plot(dashboard=True, vertical_lines_positions=[0.0, 1.0, 2.0])
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 3


class TestCreateCaptions:
    """Tests for PlotlyBase._create_captions."""

    def test_generates_expected_captions(self) -> None:
        """Captions are "<base> i" for i in 1..n."""
        assert PlotlyBase._create_captions(3, "Line") == ["Line 1", "Line 2", "Line 3"]

    def test_zero_captions(self) -> None:
        """n=0 produces an empty list."""
        assert PlotlyBase._create_captions(0, "Line") == []


class TestSetOtherParams:
    """Tests for PlotlyBase.set_other_params."""

    def test_overrides_merge_into_existing_dict(self) -> None:
        """set_other_params merges new keys/values without dropping existing ones."""
        plotter = _MinimalPlot()
        plotter.set_other_params({"axis_font_size": 14})
        assert plotter._other_params["axis_font_size"] == 14
        assert "opacity" in plotter._other_params
