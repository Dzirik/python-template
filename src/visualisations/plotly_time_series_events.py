"""
Visualizer
"""

from typing import Any

import plotly.graph_objs as go
from pandas import Series

from src.visualisations.plotly_time_series_base import PlotlyTimeSeriesBase


class PlotlyTimeSeriesEvents(PlotlyTimeSeriesBase):
    """
    Visualizes time series (one to multiple) in plotly. Possible to add couple of more time series aka events to be
    plotted as dots instead of lines (anomalies, buys, sells).
    """

    def __init__(self) -> None:
        PlotlyTimeSeriesBase.__init__(self, opacity=0.9)

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ
    def plot(
        self,
        series: list[Series],
        series_names: list[str] | None = None,
        series_obs_names: list[list[str]] | None = None,
        events: list[Series] | None = None,
        event_names: list[str] | None = None,
        event_obs_names: list[list[str]] | None = None,
        plot_title: str = "Title",
        y_title: str = "Y Axis Title",
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Creates an bar chart.
        :param series: List[Series]. List of time series to be plotted.
        :param series_names: Optional[List[str]]. List of names for time series. If none, default names are used.
        :param series_obs_names: Optional[List[List[str]]]. List of lists of names of observations for each
                                             time series.
        :param events: List[Series]. List of pandas series.
        :param event_names: Optional[List[str]]. List of names for len(series) time series. If None, automatic ones
                             are generated.
        :param event_obs_names: Optional[List[List[str]]]. List of lists of names of observations for each
                                             time series.
        :param plot_title: str. Title of the plot.
        :param y_title: Optional[str]. Y axis caption.
        :param dashboard: bool. If False, the method will create a plot. If True, it will return the figure dictionary
            for dash.
        :return: Optional[go.Figure]. Either it plots by using self._plot_single_figure (and thus it returns None) or
        returns the created go.Figure to be plotted with Dash's dcc.Graph() component.
        """
        traces: list[Any] = []
        traces = traces + self._create_time_series_traces(series, series_names, series_obs_names, fill_areas=False)
        if events is not None:
            traces = traces + self._create_event_traces(events, event_names, event_obs_names)
        layout = self._create_layout(plot_title, y_title)

        return self._plot_single_figure(trace=traces, layout=layout, dashboard=dashboard)

    # pylint: enable=too-many-arguments
    # pylint: enable=arguments-differ
