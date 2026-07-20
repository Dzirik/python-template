"""
Smoke tests for PlotlyCandle (src/visualisations/plotly_candle.py).

Exercises the OHLC candle trace (using the fixed ATTR_HIGH="HIGH" column name) combined with
vertical_lines_positions, guarding the "vertical_line" colors key fix from Wave 1.
"""

from datetime import datetime

import plotly.graph_objs as go
from pandas import DataFrame

from src.visualisations.plotly_candle import PlotlyCandle
from src.visualisations.plotly_time_series_base import ATTR_CLOSE, ATTR_HIGH, ATTR_LOW, ATTR_OPEN


def _make_market_df(n: int = 5) -> DataFrame:
    """
    Builds a small OHLC DataFrame using the ATTR_* column names, indexed by consecutive days.

    :param n: int. Number of rows.
    :return: DataFrame. Columns OPEN/HIGH/LOW/CLOSE.
    """
    index = [datetime(2021, 1, i) for i in range(1, n + 1)]
    return DataFrame(
        {
            ATTR_OPEN: [10.0 + i for i in range(n)],
            ATTR_HIGH: [12.0 + i for i in range(n)],
            ATTR_LOW: [9.0 + i for i in range(n)],
            ATTR_CLOSE: [11.0 + i for i in range(n)],
        },
        index=index,
    )


class TestPlotlyCandle:
    """Tests for PlotlyCandle.plot."""

    def test_dashboard_returns_figure_with_candlestick_trace(self) -> None:
        """dashboard=True returns a go.Figure containing a Candlestick trace built from HIGH etc."""
        plotter = PlotlyCandle()
        fig = plotter.plot(df_market=_make_market_df(), dashboard=True)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Candlestick)

    def test_vertical_lines_positions_do_not_raise_key_error(self) -> None:
        """Combining a candle plot with vertical_lines_positions must not KeyError on colors."""
        plotter = PlotlyCandle()
        fig = plotter.plot(
            df_market=_make_market_df(),
            vertical_lines_positions=[1.0, 2.0],
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2
