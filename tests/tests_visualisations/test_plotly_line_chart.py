"""
Smoke tests for PlotlyLineChart (src/visualisations/plotly_line_chart.py).
"""

import plotly.graph_objs as go
from numpy import array

from src.visualisations.plotly_line_chart import PlotlyLineChart


class TestPlotlyLineChart:
    """Tests for PlotlyLineChart.plot."""

    def test_dashboard_returns_figure_with_one_trace_per_line(self) -> None:
        """dashboard=True returns a go.Figure with one Scatter trace per (x, y) tuple."""
        plotter = PlotlyLineChart()
        lines = [(array([1, 2, 3]), array([1.0, 2.0, 3.0])), (array([1, 2, 3]), array([3.0, 2.0, 1.0]))]
        fig = plotter.plot(lines=lines, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert all(isinstance(trace, go.Scatter) for trace in fig.data)

    def test_default_line_names_generated(self) -> None:
        """When line_names is None, auto-generated "Line i" captions are used."""
        plotter = PlotlyLineChart()
        lines = [(array([1, 2]), array([1.0, 2.0]))]
        fig = plotter.plot(lines=lines, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert fig.data[0].name == "Line 1"
