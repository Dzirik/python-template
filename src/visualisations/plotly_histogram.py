"""
Visualizer

Links:
https://community.plotly.com/t/drawing-vertical-line-on-histogram-in-subplot-but-yref-paper-is-not-working/31581/2
https://plotly.com/python/shapes/
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyHistogram(PlotlyBase):
    """
    Visualizes the array data as a histogram. For usage please see
    notebooks/documentation/visualisation_documentation.py.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

        self.set_histogram()

    # pylint: disable=arguments-differ
    # pylint: disable=too-many-arguments
    def plot(
        self,
        data: ndarray[Any, dtype[Any]],
        plot_title: str,
        x_title: str,
        n_bins: int = 0,
        x_axis_min_max: tuple[float] | None = None,
        vertical_lines_positions: list[float] | None = None,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Plots the figure or returns object to be plotted in Dash.
        :param data: ndarray[Any, dtype[Any]]. 1D array of the data.
        :param plot_title: str. Title of the plot.
        :param x_title: Description of the x-axis.
        :param n_bins: int. Number of n_bins to create. If 0, automatic n_bins selection is applied.
        :param x_axis_min_max: Optional[Tuple[float]]. If None, the x-axis limits are set automatically, otherwise based
               on first (min) and second (max) values of this tuple.
        :param vertical_lines_positions: List[float]. If not None, a list of x-axis coordinates for plotting a vertical
               line there.
        :param dashboard: bool. If use in dash application or not.
        :return: Optional[go.Figure]. If None, then plots the figure. Otherwise, it creates go.Figure to be plotted with
        Dash and its dcc.Graph() component.
        """
        start = data.min()
        end = data.max()
        size = float(abs(start - end) / n_bins) if n_bins != 0 else 0.0

        trace = go.Histogram(
            x=data,
            xbins={"start": start, "end": end, "size": size},
            histfunc=self._hist_func,
            marker_color=hex_to_rgb(color=self._colors["fill"][0], opacity=self._opacity),
            marker_line_color=self._colors["line"][3],
            marker_line_width=1.5,
        )

        layout = {
            "xaxis_title": x_title,
            "yaxis_title": self._hist_func.capitalize(),
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

        return self._plot_single_figure(trace=trace, layout=layout, shapes=lines, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
