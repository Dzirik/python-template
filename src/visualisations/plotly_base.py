"""
Base class for plotly visualisations, providing shared figure assembly, background layout, and sizing helpers.
"""

from abc import ABC, abstractmethod
from typing import Any

import plotly.graph_objs as go
import plotly.io as pio

from src.visualisations.colors import COLORS
from src.visualisations.visualisation_functions import hex_to_rgb

try:
    get_ipython()  # type: ignore[name-defined]
    pio.renderers.default = "notebook"
except NameError:
    pass

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
        :param colors: Dict[str, Any]. Check src/visualisations/colors.py for more details.
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
        """
        Assembles the figure and either returns it (for Dash) or shows it and returns None (standalone).
        :param trace: Union[List[Dict[str, Any]], Dict[str, Any]]. Plotly trace(s) for the figure.
        :param layout: Dict[str, Any]. Plotly layout for the figure.
        :param shapes: Optional[List[Any]]. Shapes (e.g. vertical lines) to add to the figure.
        :param dashboard: bool. If True, returns the go.Figure for embedding in a Dash dcc.Graph() component. If
            False, shows the figure and returns None.
        :return: Optional[go.Figure]. The go.Figure if dashboard is True, otherwise None (the figure is shown as a
            side effect).
        """
        fig = go.Figure(data=trace, layout=layout)

        if self._figure_size["autosize"]:
            fig.update_layout(autosize=True, height=self._figure_size["height"])
        else:
            fig.update_layout(autosize=False, width=self._figure_size["width"], height=self._figure_size["height"])

        if shapes is not None:
            for shape in shapes:
                fig.add_shape(shape)

        if dashboard:
            return fig

        fig.show()
        return None

    def _create_background_layout(self) -> dict[str, Any]:
        """
        Creates the paper/plot background color layout entries shared by all plotly visualisations.
        :return: Dict[str, Any]. Dictionary with "paper_bgcolor" and "plot_bgcolor" keys, ready to be merged into a
            plotly layout dict.
        """
        return {
            "paper_bgcolor": hex_to_rgb(
                self._colors["paper_background"]["color"], self._colors["paper_background"]["opacity"]
            ),
            "plot_bgcolor": hex_to_rgb(
                self._colors["grid_background"]["color"], self._colors["grid_background"]["opacity"]
            ),
        }

    def _create_vertical_lines(self, vertical_lines_positions: list[float] | None) -> list[Any] | None:
        """
        Creates vertical line shapes at the given x-axis positions, for overlaying markers on a plot.
        :param vertical_lines_positions: List[float] | None. X-axis coordinates to draw a vertical line at each.
            If None, no shapes are created.
        :return: Optional[List[Any]]. List of go.layout.Shape lines, or None if vertical_lines_positions is None.
        """
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
        :return: Optional[go.Figure]. If dashboard is True, returns the go.Figure to be plotted with Dash's
        dcc.Graph() component. If dashboard is False, shows the figure and returns None.
        """
