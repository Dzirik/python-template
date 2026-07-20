"""
Smoke tests for PlotlyTimeSeriesEvents (src/visualisations/plotly_time_series_events.py).
"""

from datetime import datetime

import plotly.graph_objs as go
from numpy import random
from pandas import Series

from src.visualisations.plotly_time_series_events import PlotlyTimeSeriesEvents


def _make_series(n: int = 10) -> Series:
    """
    Builds a small deterministic pandas Series with a DatetimeIndex.

    :param n: int. Number of points.
    :return: Series. Series indexed by consecutive days in January 2021.
    """
    rng = random.default_rng(3)
    index = [datetime(2021, 1, i) for i in range(1, n + 1)]
    return Series(data=rng.standard_normal(n), index=index)


class TestPlotlyTimeSeriesEvents:
    """Tests for PlotlyTimeSeriesEvents.plot."""

    def test_dashboard_returns_figure_with_one_trace(self) -> None:
        """dashboard=True with a single series and no events returns a go.Figure with one trace."""
        plotter = PlotlyTimeSeriesEvents()
        fig = plotter.plot(series=[_make_series()], dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Scatter)

    def test_events_add_extra_marker_traces(self) -> None:
        """Passing events adds an additional discrete-marker trace for each event series."""
        plotter = PlotlyTimeSeriesEvents()
        fig = plotter.plot(series=[_make_series()], events=[_make_series(n=4)], dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        assert fig.data[-1].mode == "markers"
