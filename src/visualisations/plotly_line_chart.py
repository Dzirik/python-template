"""
Visualizer
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyLineChart(PlotlyBase):
    """
    Class for line visualisations.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)
        self._opacity = 0.9

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ
    def plot(
        self,
        lines: list[tuple[ndarray[Any, dtype[Any]], ndarray[Any, dtype[Any]]]],
        line_names: list[str] | None = None,
        plot_title: str = "Title",
        x_title: str = "X Axis Title",
        y_title: str = "Y Axis Title",
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Creates line visualisation.
        :param lines: List[Tuple[array, array]]. List of tuples consisting of x values and y values.
        :param line_names: Optional[List[str]]. List of names for lines. If none, default names are used.
        :param plot_title: str. Title of the plot.
        :param x_title: str. X axis caption.
        :param y_title: Optional[str]. Y axis caption.
        :param dashboard: bool. If False, the method will create a plot. If True, it will return the figure dictionary
            for dash.
        :return: Optional[go.Figure]. If None, then plots the figure. Otherwise, it creates go.Figure to be plotted with
        Dash and its dcc.Graph() component.
        """
        if line_names is None:
            line_names = self._create_captions(len(lines), "Line")
        traces = []
        for i, (x, y) in enumerate(lines):
            trace = go.Scatter(
                x=x,
                y=y,
                name=line_names[i],
                line={"color": self._colors["fill"][i % len(self._colors["fill"])]},
                opacity=self._opacity,
                mode="lines+markers",
                fillcolor=hex_to_rgb(self._colors["line"][i % len(self._colors["line"])], 0.1),
            )
            traces.append(trace)
        layout = {
            "yaxis_title": y_title,
            "xaxis_title": x_title,
            "title": plot_title,
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
        }
        return self._plot_single_figure(trace=traces, layout=layout, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
