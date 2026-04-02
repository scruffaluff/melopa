"""Plotting routines with Matplotlib."""

from typing import Any

import matplotlib
from matplotlib import pyplot
from matplotlib.figure import Figure

from melopa.plot import util

# Disable Matplotlib font cache logs. Based on
# https://github.com/matplotlib/matplotlib/issues/23326#issuecomment-1164772708.
matplotlib.set_loglevel("critical")


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Matplotlib."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency spectrum with Matplotlib."""
    palette = util.palette_cycle()
    legend = False
    figure, axes = subplots(ncols=1 if overlay else len(signals))
    ticks = util.spectrum_ticks()
    x_range = kwargs.pop("x_range", (20, 20_000))
    y_range = kwargs.pop("y_range", None)

    for index, signal in enumerate(signals):
        label = signal.pop("legend_label", None)
        legend = legend or (label is not None)
        x, y = util.signal_spectrum(signal)

        axis = axes if overlay else axes[index]
        axis.semilogx(x, y, color=next(palette), label=signal.pop("legend_label", None))
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Frequency (Hz)")
        axis.set_xlim(*x_range)
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        if index == 0:
            axis.set_ylabel("Amplitude (dB)")
        if y_range is not None:
            axis.set_ylim(*y_range)
        if legend:
            axis.legend()
        axis.minorticks_off()
    figure.tight_layout()
    return figure


def subplots(*args: Any, **kwargs: Any) -> tuple[Figure, Any]:
    """Melopa wrapper for Matplotlib subplots."""
    return pyplot.subplots(*args, figsize=(12, 6), **kwargs)


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio waveform with Matplotlib."""
    palette = util.palette_cycle()
    legend = False
    figure, axes = subplots(ncols=1 if overlay else len(signals))

    for index, signal in enumerate(signals):
        label = signal.pop("legend_label", None)
        legend = legend or (label is not None)
        x, y = util.signal_waveform(signal)

        axis = axes if overlay else axes[index]
        axis.plot(x, y, color=next(palette), label=label)
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Time (s)")
        if index == 0:
            axis.set_ylabel("Amplitude")
        axis.set_ylim(-1.0, 1.0)
        if legend:
            axis.legend()
    figure.tight_layout()
    return figure
