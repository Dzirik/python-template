"""
Smoke tests for PlotlyTimeSeries (src/visualisations/plotly_time_series.py).
"""

from datetime import datetime

import plotly.graph_objs as go
from numpy import random
from pandas import Series

from src.visualisations.plotly_time_series import PlotlyTimeSeries


def _make_series(n: int = 10) -> Series:
    """
    Builds a small deterministic pandas Series with a DatetimeIndex.

    :param n: int. Number of points.
    :return: Series. Series indexed by consecutive days in January 2021.
    """
    rng = random.default_rng(2)
    index = [datetime(2021, 1, i) for i in range(1, n + 1)]
    return Series(data=rng.standard_normal(n), index=index)


class TestPlotlyTimeSeries:
    """Tests for PlotlyTimeSeries.plot."""

    def test_dashboard_returns_figure_with_one_trace(self) -> None:
        """dashboard=True with a single series returns a go.Figure with one Scatter trace."""
        plotter = PlotlyTimeSeries()
        fig = plotter.plot(series=[_make_series()], dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Scatter)

    def test_anomalies_add_an_extra_trace(self) -> None:
        """Passing anomalies adds one additional marker trace on top of the series traces."""
        plotter = PlotlyTimeSeries()
        fig = plotter.plot(series=[_make_series()], anomalies=[0, 2], dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert fig.data[-1].mode == "markers"

    def test_vertical_lines_positions_do_not_raise_key_error(self) -> None:
        """Combining a time series plot with vertical_lines_positions must not KeyError on colors."""
        plotter = PlotlyTimeSeries()
        fig = plotter.plot(series=[_make_series()], vertical_lines_positions=[1.0, 2.0], dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2
