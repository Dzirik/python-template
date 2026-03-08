"""
Visualizer
"""

from typing import Any

import plotly.graph_objs as go
from pandas import Series

from src.visualisations.plotly_time_series_base import PlotlyTimeSeriesBase


class PlotlyTimeSeries(PlotlyTimeSeriesBase):
    """
    Visualizes time series in plotly. Enables multiple TS, error marks.
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
        anomalies: list[int] | None = None,
        anomalies_obs_names: list[str] | None = None,
        plot_title: str = "Title",
        y_title: str = "Y Axis Title",
        fill_areas: bool = False,
        dashboard: bool = False,
        vertical_lines_positions: list[float] | None = None,
    ) -> go.Figure | None:
        """
        Creates an bar chart.
        :param series: List[Series]. List of time series to be plotted.
        :param series_names: Optional[List[str]]. List of names for time series. If none, default names are used.
        :param series_obs_names: Optional[List[List[str]]]. List of lists of names of observations for each
                                             time series.
        :param anomalies: Optional[List[int]]. List of indices of anomalies to be plotted from the first time series.
                          Default is None.
        :param anomalies_obs_names: Optional[List[str]]. Captions for anomalies.
        :param plot_title: str. Title of the plot.
        :param y_title: Optional[str]. Y axis caption.
        :param fill_areas: bool. If True if will fill the areas between time series.
        :param dashboard: bool. If False, the method will create a plot. If True, it will return the figure dictionary
            for dash.
        :return: Optional[go.Figure]. Either it plots by using self._plot_single_figure (and thus it returns None) or
        returns the created go.Figure to be plotted with Dash's dcc.Graph() component.
        """
        traces: list[Any] = []
        traces = traces + self._create_time_series_traces(series, series_names, series_obs_names, fill_areas)
        if anomalies is not None:
            traces = traces + self._create_anomalies_from_index_trace(series[0], anomalies, anomalies_obs_names)
        layout = self._create_layout(plot_title, y_title)
        lines = self._create_vertical_lines(vertical_lines_positions)

        return self._plot_single_figure(trace=traces, layout=layout, shapes=lines, dashboard=dashboard)

    # pylint: enable=too-many-arguments
    # pylint: enable=arguments-differ
