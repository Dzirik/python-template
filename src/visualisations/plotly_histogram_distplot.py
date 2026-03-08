"""
Visualizer

The visualisation normalizes the histograms, so if the number of observations is different, it does not work.
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray
from plotly.figure_factory import create_distplot

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyHistogramDistplot(PlotlyBase):
    """
    Visualizes multiple histograms in one plot, based on distplot plot, scales the distributions, so not very useful
    for data sets with different sizes of observations.
    """

    _DEFAULT_BIN_SIZE = 0.25

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ
    def plot(
        self,
        data: list[ndarray[Any, dtype[Any]]],
        plot_title: str,
        x_title: str,
        group_labels: list[str],
        bin_size: list[float] | None,
        x_axis_min_max: tuple[float] | None = None,
        vertical_lines_positions: list[float] | None = None,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Creates multi histogram based on distplot.
        :param data: List[ndarray[Any, dtype[Any]]]. List of arrays of possibly different length containing data for
                                                     each plot.
        :param plot_title: str. Title of the plot.
        :param x_title: Description of the x-axis.
        :param group_labels: List[str]. List of names of each data list. Length has to be the same as of data list.
        :param bin_size: List[float]. List of bin sized for each data set. Length has to be the same as of data list.
        :param vertical_lines_positions: List[float]. If not None, a list of x-axis coordinates for plotting a vertical
               line there.
        :param dashboard: bool. If use in dash application or not.
        :return: Optional[go.Figure]. If None, then plots the figure. Otherwise, it creates go.Figure to be plotted with
        Dash and its dcc.Graph() component.
        """
        if bin_size is None:
            bin_size = [self._DEFAULT_BIN_SIZE] * len(data)

        colors = [self._colors["fill"][i % len(self._colors["line"])] for i in range(len(data))]
        figure = create_distplot(hist_data=data, group_labels=group_labels, bin_size=bin_size, colors=colors)
        figure.update_layout(title_text=plot_title)
        figure.update_layout(xaxis_title=x_title)
        figure.update_layout(xaxis_range=x_axis_min_max)
        figure.update_layout(
            paper_bgcolor=hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            )
        )
        figure.update_layout(
            plot_bgcolor=hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            )
        )

        trace = list(figure.data)
        layout = figure.layout
        lines = self._create_vertical_lines(vertical_lines_positions)

        return self._plot_single_figure(trace=trace, layout=layout, shapes=lines, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
