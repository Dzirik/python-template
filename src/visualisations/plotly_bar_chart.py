"""
Bar chart visualisation module.

Ordering: https://stackoverflow.com/questions/40149556/ordering-in-r-plotly-barchart
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyBarChart(PlotlyBase):
    """
    Visualizes two arrays, ids and values, as a bar chart. For usage please see
    notebooks/documentation/visualisation_documentation.py.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

    def plot(
        self,
        array_ids: ndarray[Any, dtype[Any]],
        array_values: ndarray[Any, dtype[Any]],
        plot_title: str,
        name_ids: str,
        name_values: str,
        order_by_values: bool = True,
        reverse: bool = True,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Sorts the data based on values and plots the figure or returns object to be plotted in Dash.
        :param array_ids: ndarray[Any, dtype[Any]]. 1D array of the data IDs.
        :param array_values: ndarray[Any, dtype[Any]]. 1D array of the data values.
        :param plot_title: str. Title of the plot.
        :param name_ids: str. Name of the IDs for caption.
        :param name_values: str. Name of the values for captions.
        :param order_by_values: bool. If order by values (True) or by captions (False)
        :param reverse: bool. If reverse the ordering.
        :param dashboard: bool. If True, returns the go.Figure to be plotted with Dash's dcc.Graph() component. If
            False, shows the figure and returns None.
        :return: Optional[go.Figure]. The go.Figure if dashboard is True, otherwise None (the figure is shown as a
            side effect).
        """
        trace = go.Bar(
            x=array_ids,
            y=array_values,
            marker_color=hex_to_rgb(color=self._colors["fill"][3], opacity=self._opacity),
            marker_line_color=self._colors["line"][2],
            marker_line_width=1.5,
        )

        if order_by_values:
            category_array = [x for _, x in sorted(zip(array_values, array_ids, strict=True), reverse=reverse)]
        else:
            category_array = [x for x, _ in sorted(zip(array_ids, array_values, strict=True), reverse=reverse)]

        layout = {
            "xaxis_title": name_ids,
            "yaxis_title": name_values,
            "xaxis": {"type": "category", "categoryorder": "array", "categoryarray": category_array},
            "title": plot_title,
            **self._create_background_layout(),
        }

        return self._plot_single_figure(trace=trace, layout=layout, dashboard=dashboard)
