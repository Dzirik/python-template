"""
Two-dimensional histogram visualization module (density heatmaps for latent spaces).

Provides functionality for displaying density distributions across 2D latent spaces.
"""

from typing import Any

import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyHistogram2D(PlotlyBase):
    """
    Creates 2D histogram visualizations as heatmaps displaying density distributions.
    Especially beneficial for visualizing latent spaces.
    For usage examples refer to notebooks/documentation/visualisation_documentation.py.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

        self._default_colorscale = "Viridis"
        self._figure_size = {"autosize": False, "width": 800, "height": 800}

    # pylint: disable=arguments-differ
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def plot(
        self,
        hist: ndarray[Any, dtype[Any]],
        x_edges: ndarray[Any, dtype[Any]],
        y_edges: ndarray[Any, dtype[Any]],
        plot_title: str = "Latent Space Density",
        x_title: str = "Latent Dimension 1",
        y_title: str = "Latent Dimension 2",
        colorscale: str = "Viridis",
        show_colorbar: bool = True,
        square: bool = False,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Generates a 2D histogram (density heatmap) visualization or returns a figure object for Dash plotting.
        :param hist: ndarray[Any, dtype[Any]]. Two-dimensional histogram array containing bin counts.
        :param x_edges: ndarray[Any, dtype[Any]]. Bin edge values for the x-axis.
        :param y_edges: ndarray[Any, dtype[Any]]. Bin edge values for the y-axis.
        :param plot_title: str. Chart title. Defaults to "Latent Space Density".
        :param x_title: str. Label for the x-axis. Defaults to "Latent Dimension 1".
        :param y_title: str. Label for the y-axis. Defaults to "Latent Dimension 2".
        :param colorscale: str. Heatmap color palette. Available options: "Viridis", "Plasma",
                          "Inferno", "Magma", "Cividis", "Hot", "Blues", "Greens". Defaults to "Viridis".
        :param show_colorbar: bool. Whether to display the colorbar. Defaults to True.
        :param square: bool. Whether to create a square-shaped plot with equal aspect ratio. Defaults to True.
        :param dashboard: bool. Whether to use in a dash application.
        :return: Optional[go.Figure]. Returns None and displays the figure, or returns go.Figure
                for use with Dash and its dcc.Graph() component.
        """
        trace = go.Heatmap(
            z=hist.T,  # Transpose to match conventional orientation
            x=x_edges,
            y=y_edges,
            colorscale=colorscale,
            showscale=show_colorbar,
            colorbar={"title": {"text": "Density", "side": "right"}, "thickness": 15, "len": 0.8},
            hoverongaps=False,
            hovertemplate="<b>%{x:.3f}</b><br><b>%{y:.3f}</b><br>Count: %{z}<extra></extra>",
        )

        layout = {
            "title": {"text": plot_title, "x": 0.5, "xanchor": "center"},
            "xaxis": {
                "title": x_title,
                "showgrid": True,
                "zeroline": True,
                "showline": True,
                "gridcolor": hex_to_rgb(
                    self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"] * 0.5
                ),
                "linecolor": self._colors["line"][0],
            },
            "yaxis": {
                "title": y_title,
                "showgrid": True,
                "zeroline": True,
                "showline": True,
                "gridcolor": hex_to_rgb(
                    self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"] * 0.5
                ),
                "linecolor": self._colors["line"][0],
            },
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
            "margin": {"l": 80, "r": 50, "t": 80, "b": 80},
        }

        if square:
            yaxis = layout["yaxis"]
            assert isinstance(yaxis, dict)
            yaxis["scaleanchor"] = "x"
            yaxis["scaleratio"] = 1

        return self._plot_single_figure(trace=trace, layout=layout, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-locals
