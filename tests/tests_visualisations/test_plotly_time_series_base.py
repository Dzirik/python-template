"""
Smoke tests for PlotlyTimeSeriesBase (src/visualisations/plotly_time_series_base.py) via a
minimal concrete subclass, and for the ATTR_* column-name constants used by candle plots.
"""

from datetime import datetime
from typing import Any

import plotly.graph_objs as go
from numpy import random
from pandas import DataFrame, Series

from src.visualisations.plotly_time_series_base import (
    ATTR_CLOSE,
    ATTR_HIGH,
    ATTR_LOW,
    ATTR_OPEN,
    PlotlyTimeSeriesBase,
)


class _MinimalTimeSeriesPlot(PlotlyTimeSeriesBase):
    """Minimal concrete PlotlyTimeSeriesBase subclass used only to exercise shared behavior."""

    def __init__(self) -> None:
        PlotlyTimeSeriesBase.__init__(self, opacity=0.9)

    def plot(self, *_args: Any, **_kwargs: Any) -> go.Figure | None:
        """
        Not exercised directly in these tests; the base-class helper methods are called
        individually instead.

        :param _args: Any. Unused.
        :param _kwargs: Any. Unused.
        :return: None.
        """
        return None


def _make_series(n: int = 10, name: str | None = None) -> Series:
    """
    Builds a small deterministic pandas Series with a DatetimeIndex.

    :param n: int. Number of points.
    :param name: Optional[str]. Series name.
    :return: Series. Series indexed by consecutive days in January 2021.
    """
    rng = random.default_rng(1)
    index = [datetime(2021, 1, i) for i in range(1, n + 1)]
    return Series(data=rng.standard_normal(n), index=index, name=name)


class TestCreateTimeSeriesTraces:
    """Tests for _create_time_series_traces."""

    def test_default_names_generated(self) -> None:
        """When series_names is None, auto-generated "Time Series i" captions are used."""
        plotter = _MinimalTimeSeriesPlot()
        traces = plotter._create_time_series_traces([_make_series(), _make_series()])
        assert len(traces) == 2
        assert traces[0].name == "Time Series 1"
        assert traces[1].name == "Time Series 2"

    def test_fill_areas_sets_tonexty_from_second_trace(self) -> None:
        """fill_areas=True fills from the second trace onward, not the first."""
        plotter = _MinimalTimeSeriesPlot()
        traces = plotter._create_time_series_traces([_make_series(), _make_series()], fill_areas=True)
        assert traces[0].fill is None
        assert traces[1].fill == "tonexty"


class TestCreateEventTraces:
    """Tests for _create_event_traces."""

    def test_produces_marker_traces(self) -> None:
        """Event traces are rendered as discrete markers, not lines."""
        plotter = _MinimalTimeSeriesPlot()
        traces = plotter._create_event_traces([_make_series(n=5)])
        assert len(traces) == 1
        assert traces[0].mode == "markers"


class TestCreateLayout:
    """Tests for _create_layout."""

    def test_layout_contains_title_and_axis_titles(self) -> None:
        """The layout dict carries the requested plot title and y-axis title."""
        plotter = _MinimalTimeSeriesPlot()
        layout = plotter._create_layout(plot_title="My Title", y_title="My Y")
        assert layout["title"] == "My Title"
        assert layout["yaxis_title"] == "My Y"
        assert layout["xaxis_title"] == "Date & Time"


class TestCreateAnomaliesFromIndexTrace:
    """Tests for _create_anomalies_from_index_trace."""

    def test_selects_expected_points(self) -> None:
        """The anomaly trace picks exactly the rows at the given integer positions."""
        plotter = _MinimalTimeSeriesPlot()
        ts = _make_series(n=10)
        traces = plotter._create_anomalies_from_index_trace(ts, anomalies=[0, 3])
        assert len(traces) == 1
        assert len(traces[0].x) == 2
        assert traces[0].mode == "markers"


class TestCreateCandleTrace:
    """Tests for _create_candle_trace and the ATTR_* column name constants."""

    def test_high_column_name_is_fixed_spelling(self) -> None:
        """The Wave 1 fix: ATTR_HIGH must be the correctly spelled "HIGH", not "HIGHT"."""
        assert ATTR_HIGH == "HIGH"

    def test_candle_trace_uses_ohlc_columns(self) -> None:
        """A Candlestick trace is produced from a DataFrame with OPEN/HIGH/LOW/CLOSE columns."""
        index = [datetime(2021, 1, i) for i in range(1, 6)]
        df_market = DataFrame(
            {
                ATTR_OPEN: [10.0, 11.0, 10.5, 11.5, 12.0],
                ATTR_HIGH: [12.0, 12.5, 11.5, 12.5, 13.0],
                ATTR_LOW: [9.5, 10.5, 10.0, 11.0, 11.5],
                ATTR_CLOSE: [11.0, 10.5, 11.0, 12.0, 12.5],
            },
            index=index,
        )
        traces = PlotlyTimeSeriesBase._create_candle_trace(df_market)
        assert len(traces) == 1
        assert isinstance(traces[0], go.Candlestick)
