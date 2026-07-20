"""
Smoke tests for PlotlyHistogramMulti (src/visualisations/plotly_histogram_multi.py).
"""

import plotly.graph_objs as go
from numpy import random

from src.visualisations.plotly_histogram_multi import PlotlyHistogramMulti


class TestPlotlyHistogramMulti:
    """Tests for PlotlyHistogramMulti.plot."""

    def test_dashboard_returns_figure_with_one_trace_per_group(self) -> None:
        """dashboard=True returns a go.Figure with one overlaid Histogram trace per data group."""
        rng = random.default_rng(0)
        data = [rng.standard_normal(60), rng.standard_normal(60)]
        plotter = PlotlyHistogramMulti()
        fig = plotter.plot(
            data=data,
            plot_title="Multi Hist",
            x_title="X",
            group_labels=["g1", "g2"],
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert all(isinstance(trace, go.Histogram) for trace in fig.data)
        assert fig.layout.barmode == "overlay"

    def test_vertical_lines_positions_do_not_raise_key_error(self) -> None:
        """Combining a multi-histogram with vertical_lines_positions must not KeyError on colors."""
        rng = random.default_rng(1)
        data = [rng.standard_normal(60), rng.standard_normal(60)]
        plotter = PlotlyHistogramMulti()
        fig = plotter.plot(
            data=data,
            plot_title="Multi Hist",
            x_title="X",
            group_labels=["g1", "g2"],
            vertical_lines_positions=[0.0, 1.0],
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2
