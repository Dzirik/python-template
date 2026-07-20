"""
Smoke tests for PlotlyHistogram2D (src/visualisations/plotly_histogram_2d.py).
"""

import plotly.graph_objs as go
from numpy import histogram2d, random

from src.visualisations.plotly_histogram_2d import PlotlyHistogram2D


class TestPlotlyHistogram2D:
    """Tests for PlotlyHistogram2D.plot."""

    def test_dashboard_returns_figure_with_one_trace(self) -> None:
        """dashboard=True returns a go.Figure containing exactly one Heatmap-style density trace."""
        rng = random.default_rng(0)
        x = rng.standard_normal(200)
        y = rng.standard_normal(200)
        hist, x_edges, y_edges = histogram2d(x, y, bins=10)

        plotter = PlotlyHistogram2D()
        fig = plotter.plot(hist=hist, x_edges=x_edges, y_edges=y_edges, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Heatmap)

    def test_square_option_sets_scale_anchor(self) -> None:
        """square=True anchors the y-axis scale to the x-axis for an equal aspect ratio."""
        rng = random.default_rng(1)
        hist, x_edges, y_edges = histogram2d(rng.standard_normal(50), rng.standard_normal(50), bins=5)

        plotter = PlotlyHistogram2D()
        fig = plotter.plot(hist=hist, x_edges=x_edges, y_edges=y_edges, square=True, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert fig.layout.yaxis.scaleanchor == "x"
