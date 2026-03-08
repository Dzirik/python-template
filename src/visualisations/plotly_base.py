"""
Visualizer
"""

from abc import ABC, abstractmethod
from typing import Any

import plotly.graph_objs as go
import plotly.offline as py

from src.constants.global_constants import COLORS

# Type alias for the colors dictionary structure
ColorsDict = dict[str, Any]


class PlotlyBase(ABC):
    """
    Base class for plotly visualisations.
    """

    _colors: ColorsDict

    def __init__(self) -> None:
        self._opacity = 0.25
        self._colors = COLORS
        self._hist_func: str
        self._figure_size = {"autosize": True, "width": 1000, "height": 750}
        self._other_params: dict[str, Any] = {"axis_font_size": None, "opacity": 0.25}

    def set_other_params(self, params: dict[str, Any]) -> None:
        """
        Sets the additional parameters for the plotly visualisations.
        :param params: Dict[str, Any]. Dictionary with params to be changed.
        """
        for key, value in params.items():
            self._other_params[key] = value

    def set_colors(self, colors: ColorsDict) -> None:
        """
        Sets the colors for the plot.
        :param colors: Dict[str, Any]. Check src/constants/global_constants.py for more details.
            {
                "line": ["#0f0f0f", "#011936", "#2F3E46", "#354F52"],
                "fill": ["#087E8B", "#99AA38", "#F58A07", "#F7F5FB", "#FFBB00"],
                "error": ["#ED254E", "#C81D25"],
                "dot": ["#99AA38", "#ED254E", "#ACD2ED"],
                "paper_background": {"color": "#000000", "opacity": 0},
                "grid_background": {"color": "#858B97", "opacity": 0.4}
            }
        """
        self._colors = colors

    def _plot_single_figure(
        self,
        trace: list[dict[str, Any]] | dict[str, Any],
        layout: dict[str, Any],
        shapes: list[Any] | None = None,
        dashboard: bool = False,
    ) -> go.Figure | None:
        fig = go.Figure(data=trace, layout=layout)

        if not self._figure_size["autosize"]:
            fig.update_layout(autosize=self._figure_size["autosize"])
            fig.update_layout(width=self._figure_size["width"])
            fig.update_layout(height=self._figure_size["height"])

        if shapes is not None:
            for shape in shapes:
                fig.add_shape(shape)

        if dashboard:
            return fig

        py.iplot(fig)
        return None

    def _create_vertical_lines(self, vertical_lines_positions: list[float] | None) -> list[Any] | None:
        if vertical_lines_positions is None:
            return None

        lines = []
        for i, line_x_coordinates in enumerate(vertical_lines_positions):
            # "dash": "solid", "dash" - - -, "dot"
            line = go.layout.Shape(
                type="line",
                xref="x",
                yref="paper",
                x0=line_x_coordinates,
                y0=0,
                x1=line_x_coordinates,
                y1=1,
                line={
                    "dash": "dash",
                    "color": self._colors["vertical_line"][i % len(self._colors["vertical_line"])],
                    "width": 1.5,
                },
            )
            lines.append(line)
        return lines

    def set_histogram(self, hist_func: str = "count") -> None:
        """
        Sets parameters of lower importance.
        :param hist_func: str. Grouping function name for the histogram ("count", "sum", "avg", "min", "max").
        """
        self._hist_func = hist_func

    def customize_size(self, autosize: bool = False, width: int = 1000, height: int = 750) -> None:
        """
        Customizes setting for figure size.
        :param autosize: bool. If autosize or not.
        :param width: int.
        :param height: int.
        """
        self._figure_size = {"autosize": autosize, "width": width, "height": height}

    @staticmethod
    def _create_captions(n: int, base_caption: str) -> list[str]:
        """
        Creates captions "<base_caption> i" for i in n_hat eg. 1-n.
        :param n: int. Number captions to be created.
        :return: List[str]. List of captions.
        """
        return [base_caption + " " + str(i + 1) for i in range(n)]

    @abstractmethod
    def plot(self, *args: Any, **kwargs: Any) -> go.Figure | None:
        """
        Plots the figure.
        :param args: Positional arguments for the plot (subclass-specific).
        :param kwargs: Keyword arguments for the plot (subclass-specific).
        :return: Optional[go.Figure]. Either it plots by using self._plot_single_figure (and thus it returns None) or
        returns the created go.Figure to be plotted with Dash's dcc.Graph() component.
        """
