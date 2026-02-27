"""Plotting routines with Matplotlib."""

from typing import Any

import numpy
from matplotlib import pyplot
from matplotlib.figure import Figure


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Matplotlib."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency spectrum with Matplotlib."""
    raise NotImplementedError


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:  # noqa: ARG001
    """Plot audio waveform with Matplotlib."""
    figure, axis = pyplot.subplots(figsize=(12, 6))
    figure.tight_layout()

    for signal in signals:
        rate = signal.pop("rate")
        y = signal.pop("y")
        x = numpy.linspace(0, len(y) / rate, len(y))
        axis.plot(x, y, label=signal.pop("legend_label", None))

    axis.legend()
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Amplitude")
    axis.set_ylim(-1.0, 1.0)
    axis.set_title(kwargs.pop("title", None))
    return figure
