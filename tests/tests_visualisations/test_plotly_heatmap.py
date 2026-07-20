"""
Smoke tests for PlotlyHeatmap (src/visualisations/plotly_heatmap.py).
"""

import plotly.graph_objs as go
from numpy import array
from pandas import DataFrame

from src.visualisations.plotly_heatmap import PlotlyHeatmap


class TestPlotlyHeatmap:
    """Tests for PlotlyHeatmap.plot."""

    def test_dashboard_returns_figure_with_heatmap_trace_from_ndarray(self) -> None:
        """dashboard=True with a plain ndarray returns a go.Figure with one Heatmap trace."""
        plotter = PlotlyHeatmap()
        data = array([[1.0, 0.5], [0.5, 1.0]])
        fig = plotter.plot(data=data, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Heatmap)

    def test_dataframe_input_uses_columns_and_index_as_labels(self) -> None:
        """A DataFrame input derives x/y labels from its columns/index when not given explicitly."""
        plotter = PlotlyHeatmap()
        df = DataFrame([[1.0, 0.2], [0.2, 1.0]], columns=["a", "b"], index=["x", "y"])
        fig = plotter.plot(data=df, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert list(fig.data[0].x) == ["a", "b"]
        assert list(fig.data[0].y) == ["x", "y"]


class TestPlotlyHeatmapCorrelationMatrix:
    """Tests for PlotlyHeatmap.plot_correlation_matrix."""

    def test_dashboard_returns_figure(self) -> None:
        """plot_correlation_matrix delegates to plot and returns a go.Figure when dashboard=True."""
        plotter = PlotlyHeatmap()
        corr = DataFrame([[1.0, 0.3], [0.3, 1.0]], columns=["a", "b"], index=["a", "b"])
        fig = plotter.plot_correlation_matrix(corr_matrix=corr, dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
