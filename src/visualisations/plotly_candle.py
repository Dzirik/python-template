"""
Visualizer
Customize markers: https://plotly.com/python/marker-style/
"""

from typing import Any

import plotly.graph_objs as go
from pandas import DataFrame, Series

from src.visualisations.plotly_time_series_base import PlotlyTimeSeriesBase


class PlotlyCandle(PlotlyTimeSeriesBase):
    """
    Plot candles optionally with time series and markers for occasions.
    """

    def __init__(self) -> None:
        PlotlyTimeSeriesBase.__init__(self, opacity=1)

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ
    def plot(
        self,
        df_market: DataFrame,
        series: list[Series] | None = None,
        series_names: list[str] | None = None,
        series_obs_names: list[list[str]] | None = None,
        events: list[Series] | None = None,
        event_names: list[str] | None = None,
        event_obs_names: list[list[str]] | None = None,
        vertical_lines_positions: list[float] | None = None,
        plot_title: str = "Title",
        y_title: str = "Y Axis Title",
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Creates a candle plot out of df_market, adds one or more time series, add one or more event series.
        :param df_market: DataFrame. Data frame with index datetimeindex and four columns ATTR_OPEN, ATTR_HIGH,
                          ATTR_LOW, ATTR_CLOSE.
        :param series: List[Series]. List of time series to be plotted.
        :param series_names: Optional[List[str]]. List of names for time series. If none, default names are used.
        :param series_obs_names: Optional[List[List[str]]]. List of lists of names of observations for each
                                             time series.
        :param events: List[Series]. List of pandas series.
        :param event_names: Optional[List[str]]. List of names for len(series) time series. If None, automatic ones
                             are generated.
        :param event_obs_names: Optional[List[List[str]]]. List of lists of names of observations for each
                                             time series.
        :param vertical_lines_positions: List[float]. If not None, a list of x-axis coordinates for plotting a vertical
               line there.
        :param plot_title: str. Title of the plot.
        :param y_title: Optional[str]. Y axis caption.
        :param dashboard: bool. If False, the method will create a plot. If True, it will return the figure dictionary
            for dash.
        :return: Optional[go.Figure]. Either it plots by using self._plot_single_figure (and thus it returns None) or
        returns the created go.Figure to be plotted with Dash's dcc.Graph() component.
        """
        traces: list[Any] = []
        traces = traces + self._create_candle_trace(df_market)
        if series is not None:
            traces = traces + self._create_time_series_traces(series, series_names, series_obs_names)
        if events is not None:
            traces = traces + self._create_event_traces(events, event_names, event_obs_names)
        layout = self._create_layout(plot_title, y_title)
        lines = self._create_vertical_lines(vertical_lines_positions)

        return self._plot_single_figure(trace=traces, layout=layout, shapes=lines, dashboard=dashboard)
