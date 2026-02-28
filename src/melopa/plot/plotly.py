"""Plotting routines with Plotly."""

from typing import Any

import numpy
from plotly import subplots
from plotly.graph_objects import Figure, Scattergl
from plotly.graph_objs.layout import Legend

from melopa.plot import util


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Plotly."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency spectrum with Plotly."""
    palette = util.palette_cycle()
    ticks = util.spectrum_ticks()
    plot = subplots.make_subplots(
        cols=1 if overlay else len(signals), shared_yaxes=True
    )
    plot.update_layout(
        legend=Legend(orientation="h", x=1, y=1.1, xanchor="right", yanchor="top"),
        template="simple_white",
        yaxis_title="Amplitude (dB)",
        title=kwargs.pop("title", None),
    )
    plot.update_xaxes(
        range=[numpy.log10(20), numpy.log10(20_000)],
        tickvals=ticks[0],
        ticktext=ticks[1],
        title="Frequency (Hz)",
        type="log",
    )

    for index, signal in enumerate(signals):
        x, y = util.signal_spectrum(signal)

        plot.add_trace(
            Scattergl(
                x=x,
                y=y,
                hoverinfo="none",
                line={"color": next(palette)},
                mode="lines",
                name=signal.pop("legend_label", None),
            ),
            col=1 if overlay else index + 1,
            row=1,
        )
    return plot


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio waveform with Plotly."""
    palette = util.palette_cycle()
    plot = subplots.make_subplots(
        cols=1 if overlay else len(signals), shared_yaxes=True
    )
    plot.update_layout(
        legend=Legend(orientation="h", x=1, y=1.1, xanchor="right", yanchor="top"),
        template="simple_white",
        xaxis_title="Time (s)",
        yaxis_range=[-1, 1],
        yaxis_title="Amplitude",
        title=kwargs.pop("title", None),
    )
    plot.update_xaxes(
        title="Time (s)",
    )

    for index, signal in enumerate(signals):
        x, y = util.signal_waveform(signal)

        plot.add_trace(
            Scattergl(
                x=x,
                y=y,
                hoverinfo="none",
                line={"color": next(palette)},
                mode="lines",
                name=signal.pop("legend_label", None),
            ),
            col=1 if overlay else index + 1,
            row=1,
        )
    return plot
