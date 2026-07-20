"""
Smoke tests for PlotlyHistogramDistplot (src/visualisations/plotly_histogram_distplot.py).
"""

import plotly.graph_objs as go
from numpy import random

from src.visualisations.plotly_histogram_distplot import PlotlyHistogramDistplot


class TestPlotlyHistogramDistplot:
    """Tests for PlotlyHistogramDistplot.plot."""

    def test_dashboard_returns_figure_with_traces_per_group(self) -> None:
        """dashboard=True returns a go.Figure; create_distplot emits a distribution + rug trace per group."""
        rng = random.default_rng(0)
        data = [rng.standard_normal(50), rng.standard_normal(50)]
        plotter = PlotlyHistogramDistplot()
        fig = plotter.plot(
            data=data,
            plot_title="Distplot",
            x_title="X",
            group_labels=["g1", "g2"],
            bin_size=None,
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        # create_distplot emits at least one trace (curve/histogram) per group.
        assert len(fig.data) >= 2
        assert fig.layout.title.text == "Distplot"

    def test_vertical_lines_positions_do_not_raise_key_error(self) -> None:
        """Combining a distplot with vertical_lines_positions must not KeyError on colors."""
        rng = random.default_rng(1)
        data = [rng.standard_normal(50), rng.standard_normal(50)]
        plotter = PlotlyHistogramDistplot()
        fig = plotter.plot(
            data=data,
            plot_title="Distplot",
            x_title="X",
            group_labels=["g1", "g2"],
            bin_size=[0.5, 0.5],
            vertical_lines_positions=[0.0, 1.0],
            dashboard=True,
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) == 2
