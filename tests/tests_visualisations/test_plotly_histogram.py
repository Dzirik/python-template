"""
Smoke tests for PlotlyHistogram (src/visualisations/plotly_histogram.py).
"""

import plotly.graph_objs as go
from numpy import random

from src.visualisations.plotly_histogram import PlotlyHistogram


class TestPlotlyHistogram:
    """Tests for PlotlyHistogram.plot."""

    def test_dashboard_returns_figure_with_one_trace(self) -> None:
        """dashboard=True returns a go.Figure containing exactly one Histogram trace."""
        plotter = PlotlyHistogram()
        data = random.default_rng(0).standard_normal(100)
        fig = plotter.plot(data=data, plot_title="Hist", x_title="X", dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Histogram)

    def test_vertical_lines_positions_do_not_raise_key_error(self) -> None:
        """Combining a histogram with vertical_lines_positions must not KeyError on colors."""
        plotter = PlotlyHistogram()
        data = random.default_rng(0).standard_normal(100)
        fig = plotter.plot(
            data=data,
            plot_title="Hist",
            x_title="X",
            vertical_lines_positions=[0.0, 1.0],
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2
