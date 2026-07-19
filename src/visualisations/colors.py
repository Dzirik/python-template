"""
Visualisation palette used by plotly-based plots.
"""

COLORS = {
    "line": ["#0f0f0f", "#011936", "#2F3E46", "#354F52"],  # black, oxford  blue, charcoal, dask slate gray
    "fill": ["#087E8B", "#99AA38", "#F58A07", "#F7F5FB", "#FFBB00"],  # metallic seaweed (B), citron (G), dark orange,
    # ghost white, sunflower
    "error": ["#ED254E", "#C81D25"],  # red crayola, lava
    "dot": ["#99AA38", "#ED254E", "#ACD2ED"],  # green "#99AA38", yello "#F9DC5C", blue, grass "#3F681C",
    # red crayola "#ED254E"
    "paper_background": {"color": "#000000", "opacity": 0},  # outside of the plot, black with 0 opacity
    "grid_background": {"color": "#858B97", "opacity": 0.4},
    "vertical_line": ["#000000"],
    # "vertical_line": ["#000000"]
}
