"""
Multi-series bar chart visualization module

Creates bar chart visualizations with multiple data series sharing the same categories/indices.
Provides support for both grouped and stacked bar chart layouts.
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyBarChartMulti(PlotlyBase):
    """
    Creates visualizations with multiple bar chart series sharing identical categories. For usage examples refer to
    notebooks/documentation/visualisation_documentation.py.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

    # pylint: disable=too-many-arguments
    # pylint: disable=arguments-differ
    # pylint: disable=too-many-locals
    def plot(
        self,
        array_ids: ndarray[Any, dtype[Any]],
        array_values_list: list[ndarray[Any, dtype[Any]]],
        series_names: list[str],
        plot_title: str = "",
        name_ids: str = "",
        name_values: str = "",
        order_by_values: bool = True,
        reverse: bool = True,
        order_by_series: int = 0,
        bar_mode: str = "group",
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Generates a bar chart visualization with multiple data series sharing identical categories.
        :param array_ids: ndarray[Any, dtype[Any]]. One-dimensional array containing category IDs/names.
        :param array_values_list: List[ndarray[Any, dtype[Any]]]. Collection of 1D arrays where each array holds
                                 values for a single series. Each array must match array_ids in length.
        :param series_names: List[str]. Labels for each data series. Length must match array_values_list.
        :param plot_title: str. Chart title. Defaults to empty string.
        :param name_ids: str. Label for categories on x-axis. Defaults to empty string.
        :param name_values: str. Label for values on y-axis. Defaults to empty string.
        :param order_by_values: bool. Whether to sort by values (True) or category names (False).
        :param reverse: bool. Whether to reverse the sort order.
        :param order_by_series: int. Series index to use for sorting when order_by_values=True.
                               Defaults to 0 (first series).
        :param bar_mode: str. Display mode for bars: "group" (side-by-side) or "stack" (stacked). Defaults to "group".
        :param dashboard: bool. Whether to use in a dash application.
        :return: Optional[go.Figure]. Returns None and displays the figure, or returns go.Figure
                for use with Dash and its dcc.Graph() component.
        """
        if len(array_values_list) != len(series_names):
            raise ValueError("array_values_list and series_names must have the same length")

        for i, values in enumerate(array_values_list):
            if len(values) != len(array_ids):
                raise ValueError(f"Series {i} length ({len(values)}) doesn't match array_ids length ({len(array_ids)})")

        if order_by_series >= len(array_values_list):
            raise ValueError(
                f"order_by_series ({order_by_series}) must be less than number of series ({len(array_values_list)})"
            )

        traces = []
        opacity = self._other_params.get("opacity") or self._opacity
        for i, (values, series_name) in enumerate(zip(array_values_list, series_names, strict=True)):
            trace = go.Bar(
                x=array_ids,
                y=values,
                name=series_name,
                marker_color=hex_to_rgb(color=self._colors["fill"][i % len(self._colors["fill"])], opacity=opacity),
                marker_line_color=self._colors["line"][i % len(self._colors["line"])],
                marker_line_width=1.5,
            )
            traces.append(trace)

        if order_by_values:
            ordering_values = array_values_list[order_by_series]
            category_array = [x for _, x in sorted(zip(ordering_values, array_ids, strict=True), reverse=reverse)]
        else:
            category_array = [x for x, _ in sorted(zip(array_ids, array_values_list[0], strict=True), reverse=reverse)]

        layout = {
            "xaxis_title": name_ids,
            "yaxis_title": name_values,
            "xaxis": {"type": "category", "categoryorder": "array", "categoryarray": category_array},
            "title": plot_title,
            "barmode": bar_mode,
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
            "legend": {"orientation": "v", "yanchor": "top", "y": 1, "xanchor": "left", "x": 1.02},
        }

        return self._plot_single_figure(trace=traces, layout=layout, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-locals
