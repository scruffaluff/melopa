"""Plotting routines with Plotly."""

from typing import Any

import numpy
from plotly.graph_objects import Figure, Layout, Scattergl
from plotly.graph_objs.layout import Legend


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Plotly."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency spectrum with Plotly."""
    raise NotImplementedError


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:  # noqa: ARG001
    """Plot audio waveform with Plotly."""
    plot = Figure(
        layout=Layout(
            legend=Legend(orientation="h", y=-0.2, yanchor="top"),
            template="simple_white",
        ),
    )
    for signal in signals:
        rate = signal.pop("rate")
        y = signal.pop("y")
        x = numpy.linspace(0, len(y) / rate, len(y))

        plot.add_trace(
            Scattergl(x=x, y=y, mode="lines", name=signal.pop("legend_label", None))
        )

    return plot
