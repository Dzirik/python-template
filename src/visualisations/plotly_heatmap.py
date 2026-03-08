"""
Heatmap visualization module, especially beneficial for displaying correlation matrices.

Based on matplotlib/seaborn heatmap capabilities implemented using Plotly.
"""

from typing import Any

import pandas as pd
import plotly.graph_objs as go
from numpy import dtype, ndarray

from src.visualisations.plotly_base import PlotlyBase
from src.visualisations.visualisation_functions import hex_to_rgb


class PlotlyHeatmap(PlotlyBase):
    """
    Creates heatmap visualizations from 2D data. Especially beneficial for correlation matrices.
    For usage examples refer to notebooks/documentation/visualisation_documentation.py.
    """

    def __init__(self) -> None:
        PlotlyBase.__init__(self)

        # Default colorscale mappings similar to matplotlib/seaborn
        self._colorscale_mappings = {
            "coolwarm": "RdBu_r",  # Red for high (1), blue for low (0) - matches matplotlib coolwarm
            "RdBu": "RdBu",  # Red min, blue max
            "viridis": "Viridis",  # Blue min, yellow max
            "plasma": "Plasma",  # High values yellow
            "YlGnBu": "YlGnBu",  # Blue max, yellow rest
            "cubehelix": "Viridis",  # Color blind friendly alternative
            "bwr": "RdBu_r",  # Red max, blue min (reversed)
            "seismic": "RdBu",  # Strong contrast
        }

    # pylint: disable=arguments-differ
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def plot(
        self,
        data: pd.DataFrame | ndarray[Any, dtype[Any]],
        plot_title: str = "Heatmap",
        x_labels: list[str] | None = None,
        y_labels: list[str] | None = None,
        colorscale: str = "coolwarm",
        show_values: bool = True,
        value_format: str = ".2f",
        line_width: float = 0.5,
        colorbar_shrink: float = 0.8,
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Generates a heatmap visualization or returns a figure object for Dash plotting.
        :param data: Union[pd.DataFrame, ndarray]. Two-dimensional data for heatmap visualization.
        :param plot_title: str. Chart title. Defaults to "Heatmap".
        :param x_labels: Optional[List[str]]. X-axis labels. When None and data is DataFrame, column names are used.
        :param y_labels: Optional[List[str]]. Y-axis labels. When None and data is DataFrame, index names are used.
        :param colorscale: str. Heatmap color palette. Available options: "coolwarm", "RdBu", "viridis",
                          "plasma", "YlGnBu", "cubehelix", "bwr", "seismic". Defaults to "coolwarm".
        :param show_values: bool. Whether to display values within each cell. Defaults to True.
        :param value_format: str. Formatting string for displayed values. Defaults to ".2f".
        :param line_width: float. Thickness of lines separating cells. Defaults to 0.5.
        :param colorbar_shrink: float. Scaling factor for colorbar size. Defaults to 0.8.
        :param dashboard: bool. Whether to use in a dash application.
        :return: Optional[go.Figure]. Returns None and displays the figure, or returns go.Figure
                for use with Dash and its dcc.Graph() component.
        """
        if isinstance(data, pd.DataFrame):
            z_data = data.to_numpy()
            if x_labels is None:
                x_labels = list(data.columns)
            if y_labels is None:
                y_labels = list(data.index)
        else:
            z_data = data
            if x_labels is None:
                x_labels = [f"Col {i}" for i in range(z_data.shape[1])]
            if y_labels is None:
                y_labels = [f"Row {i}" for i in range(z_data.shape[0])]

        plotly_colorscale = self._colorscale_mappings.get(colorscale, "RdBu")

        text_data = None
        if show_values:
            text_data = [[f"{val:{value_format}}" for val in row] for row in z_data]

        trace = go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale=plotly_colorscale,
            text=text_data,
            texttemplate="%{text}" if show_values else None,
            textfont={"size": 10, "color": "white"},
            showscale=True,
            colorbar={"len": colorbar_shrink, "thickness": 15, "title": {"text": "", "side": "right"}},
            hoverongaps=False,
            hovertemplate="<b>%{y}</b><br><b>%{x}</b><br>Value: %{z}<extra></extra>",
        )

        layout = {
            "title": {"text": plot_title, "x": 0.5, "xanchor": "center"},
            "xaxis": {
                "title": "",
                "side": "bottom",
                "tickangle": -45 if len(x_labels) > 10 else 0,
                "showgrid": False,
                "zeroline": False,
                "showline": True,
                "linewidth": line_width,
                "linecolor": self._colors["line"][0],
            },
            "yaxis": {
                "title": "",
                "autorange": "reversed",  # To match seaborn/matplotlib convention
                "showgrid": False,
                "zeroline": False,
                "showline": True,
                "linewidth": line_width,
                "linecolor": self._colors["line"][0],
            },
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
            "margin": {"l": 100, "r": 50, "t": 80, "b": 100},
        }

        return self._plot_single_figure(trace=trace, layout=layout, dashboard=dashboard)

    # pylint: enable=arguments-differ
    # pylint: enable=too-many-arguments
    # pylint: enable=too-many-locals

    def plot_correlation_matrix(
        self,
        corr_matrix: pd.DataFrame | ndarray[Any, dtype[Any]],
        title: str = "Correlation Matrix",
        colorscale: str = "coolwarm",
        dashboard: bool = False,
    ) -> go.Figure | None:
        """
        Helper method designed specifically for visualizing correlation matrices.
        :param corr_matrix: Union[pd.DataFrame, ndarray]. Correlation matrix for visualization.
        :param title: str. Chart title. Defaults to "Correlation Matrix".
        :param colorscale: str. Heatmap color palette. Defaults to "coolwarm".
        :param dashboard: bool. Whether to use in a dash application.
        :return: Optional[go.Figure]. Returns None and displays the figure, or returns go.Figure
                for use with Dash and its dcc.Graph() component.
        """
        return self.plot(
            data=corr_matrix,
            plot_title=title,
            colorscale=colorscale,
            show_values=True,
            value_format=".2f",
            line_width=0.5,
            colorbar_shrink=0.8,
            dashboard=dashboard,
        )
