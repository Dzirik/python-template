"""
Visualizer

Visualizes multiple histograms.

https://stackoverflow.com/questions/40629949/python-plotly-multiple-histogram-with-mean-line
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyHistogramMulti(PlotlyBase):
    """
    Visualizes multiple histograms.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)
        self._opacity = 0.3

        self.set_histogram()

    # pylint: disable=arguments-differ
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def plot(
        self,
        data: list[ndarray[Any, dtype[Any]]],
        plot_title: str,
        x_title: str,
        group_labels: list[str],
        n_bins: int = 0,
        x_axis_min_max: tuple[float] | None = None,
        vertical_lines_positions: list[float] | None = None,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Plots multiple histograms.
        :param data: List[ndarray[Any, dtype[Any]]]. List of arrays of possibly different length containing data for
                     each plot.
        :param plot_title: str. Title of the plot.
        :param x_title: Description of the x-axis.
        :param group_labels: List[str]. List of names of each data list. Length has to be the same as of data list.
        :param n_bins: int. Number of n_bins to create. If 0, automatic n_bins selection is applied.
        :param x_axis_min_max: Optional[Tuple[float]]. If None, the x-axis limits are set automatically, otherwise based
               on first (min) and second (max) values of this tuple.
        :param vertical_lines_positions: List[float]. If not None, a list of x-axis coordinates for plotting a vertical
               line there.
        :param dashboard: bool. If use in dash application or not.
        :return: Optional[go.Figure]. If None, then plots the figure. Otherwise, it creates go.Figure to be plotted with
        Dash and its dcc.Graph() component.
        """
        traces = []
        for i, single_data in enumerate(data):
            start = single_data.min()
            end = single_data.max()
            size = float(abs(start - end) / n_bins) if n_bins != 0 else 0.0
            trace = go.Histogram(
                x=single_data,
                xbins={"start": start, "end": end, "size": size},
                histfunc=self._hist_func,
                marker_color=hex_to_rgb(
                    color=self._colors["fill"][i % len(self._colors["fill"])], opacity=self._opacity
                ),
                marker_line_color=self._colors["line"][3],
                marker_line_width=1.5,
                name=group_labels[i],
            )
            traces.append(trace)

        layout = {
            "xaxis_title": x_title,
            "yaxis_title": self._hist_func.capitalize(),
            "barmode": "overlay",
            "title": plot_title,
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
            "xaxis_range": x_axis_min_max,
        }

        lines = self._create_vertical_lines(vertical_lines_positions)

        return self._plot_single_figure(trace=traces, layout=layout, shapes=lines, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-locals
