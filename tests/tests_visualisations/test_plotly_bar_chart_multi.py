"""
Smoke tests for PlotlyBarChartMulti (src/visualisations/plotly_bar_chart_multi.py).
"""

import plotly.graph_objs as go
import pytest
from numpy import array

from src.visualisations.plotly_bar_chart_multi import PlotlyBarChartMulti


class TestPlotlyBarChartMulti:
    """Tests for PlotlyBarChartMulti.plot."""

    def test_dashboard_returns_figure_with_one_trace_per_series(self) -> None:
        """dashboard=True returns a go.Figure with one Bar trace per series."""
        plotter = PlotlyBarChartMulti()
        fig = plotter.plot(
            array_ids=array(["a", "b", "c"]),
            array_values_list=[array([1.0, 2.0, 3.0]), array([3.0, 2.0, 1.0])],
            series_names=["s1", "s2"],
            plot_title="Multi Bar",
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert all(isinstance(trace, go.Bar) for trace in fig.data)
        assert fig.layout.barmode == "group"

    def test_stack_bar_mode(self) -> None:
        """bar_mode="stack" is forwarded to the figure layout."""
        plotter = PlotlyBarChartMulti()
        fig = plotter.plot(
            array_ids=array(["a", "b"]),
            array_values_list=[array([1.0, 2.0]), array([2.0, 1.0])],
            series_names=["s1", "s2"],
            bar_mode="stack",
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert fig.layout.barmode == "stack"

    def test_mismatched_series_names_length_raises(self) -> None:
        """A mismatch between array_values_list and series_names lengths raises ValueError."""
        plotter = PlotlyBarChartMulti()
        with pytest.raises(ValueError, match="same length"):
            plotter.plot(
                array_ids=array(["a", "b"]),
                array_values_list=[array([1.0, 2.0])],
                series_names=["s1", "s2"],
                dashboard=True,
            )
