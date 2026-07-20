"""
Smoke tests for PlotlyBarChart (src/visualisations/plotly_bar_chart.py).
"""

import plotly.graph_objs as go
from numpy import array

from src.visualisations.plotly_bar_chart import PlotlyBarChart


class TestPlotlyBarChart:
    """Tests for PlotlyBarChart.plot."""

    def test_dashboard_returns_figure_with_one_trace(self) -> None:
        """dashboard=True returns a go.Figure containing exactly one Bar trace."""
        plotter = PlotlyBarChart()
        fig = plotter.plot(
            array_ids=array(["a", "b", "c"]),
            array_values=array([3.0, 1.0, 2.0]),
            plot_title="Bar",
            name_ids="IDs",
            name_values="Values",
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Bar)
        assert fig.layout.title.text == "Bar"

    def test_order_by_captions_when_disabled(self) -> None:
        """order_by_values=False orders categories by ID rather than value."""
        plotter = PlotlyBarChart()
        fig = plotter.plot(
            array_ids=array(["a", "b", "c"]),
            array_values=array([3.0, 1.0, 2.0]),
            plot_title="Bar",
            name_ids="IDs",
            name_values="Values",
            order_by_values=False,
            reverse=False,
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert list(fig.layout.xaxis.categoryarray) == ["a", "b", "c"]
