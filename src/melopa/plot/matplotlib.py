"""Plotting routines with Matplotlib."""

from typing import Any

import matplotlib
import numpy
from matplotlib import pyplot
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

from melopa.plot import util
from melopa.plot.util import Signal

# Disable Matplotlib font cache logs. Based on
# https://github.com/matplotlib/matplotlib/issues/23326#issuecomment-1164772708.
matplotlib.set_loglevel("CRITICAL")


def line(
    *signals: ArrayLike, overlay: bool = True, x: ArrayLike | None = None, **kwargs: Any
) -> Figure:
    """Plot line with Matplotlib."""
    palette = util.palette_cycle()
    x_range, y_range, _ = util.axis_ranges(kwargs)

    figure, axes = subplots(ncols=1 if overlay else len(signals), squeeze=False)
    axes = axes[0]

    for index, signal in enumerate(signals):
        color = next(palette)
        y = numpy.asarray(signal)
        x = numpy.arange(len(y))
        x_range += (x[0], x[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x, y, color=color)
        axis.set_title(kwargs.pop("title", None))

    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)
    return figure


def phase(*signals: Signal, overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency phase with Matplotlib."""
    palette = util.palette_cycle()
    x_range, y_range, _ = util.axis_ranges(kwargs, x_range=(20, 20_000))

    figure, axes = subplots(ncols=1 if overlay else len(signals), squeeze=False)
    axes = axes[0]
    axes[0].set_ylabel("Phase (rad)")
    ticks = util.spectrum_ticks()

    for index, signal in enumerate(signals):
        if isinstance(signal, dict):
            color = signal.pop("color", next(palette))
            label = signal.pop("legend_label", None)
        else:
            color = next(palette)
            label = None

        x, y = util.signal_phase(signal)
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x, y, color=color, label=label)
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Frequency (Hz)")
        axis.set_xscale("log")
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        if label:
            axis.legend()
        axis.minorticks_off()

    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)
    return figure


def spectrogram(*signals: Signal, normalize: bool = False, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Matplotlib."""
    ticks = util.spectrum_ticks()
    x_range, y_range, _ = util.axis_ranges(kwargs, y_range=(20, 20_000))

    figure, axes = subplots(ncols=len(signals))
    axes[0].set_ylabel("Frequency (Hz)")

    for index, signal in enumerate(signals):
        x, y, z = util.signal_spectrogram(signal, normalize)
        x_range += (x.min(), x.max())

        axis = axes[index]
        mesh = axis.pcolormesh(
            x,
            y,
            z,
            antialiased=True,
            cmap="viridis",
            shading="auto",
        )
        axis.set_xlabel("Time (s)")
        axis.set_yscale("log")
        axis.set_yticks(ticks[0])
        axis.set_yticklabels(ticks[1])

    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)
    figure.colorbar(mesh, ax=axes, label="Volume (dB)")
    return figure


def spectrum(
    *signals: Signal, normalize: bool = False, overlay: bool = True, **kwargs: Any
) -> Figure:
    """Plot audio frequency spectrum with Matplotlib."""
    palette = util.palette_cycle()
    ticks = util.spectrum_ticks()
    x_range, y_range, _ = util.axis_ranges(kwargs, x_range=(20, 20_000))

    figure, axes = subplots(ncols=1 if overlay else len(signals), squeeze=False)
    axes = axes[0]
    axes[0].set_ylabel("Volume (dB)")

    for index, signal in enumerate(signals):
        if isinstance(signal, dict):
            color = signal.pop("color", next(palette))
            label = signal.pop("legend_label", None)
        else:
            color = next(palette)
            label = None

        x, y = util.signal_spectrum(signal, normalize)
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x, y, color=color, label=label)
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Frequency (Hz)")
        axis.set_xscale("log")
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        if label:
            axis.legend()
        axis.minorticks_off()

    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)
    return figure


def subplots(*args: Any, **kwargs: Any) -> tuple[Figure, Any]:
    """Melopa wrapper for Matplotlib subplots."""
    return pyplot.subplots(*args, figsize=(12, 6), layout="compressed", **kwargs)


def waveform(
    *signals: Signal, normalize: bool = False, overlay: bool = True, **kwargs: Any
) -> Figure:
    """Plot audio waveform with Matplotlib."""
    palette = util.palette_cycle()
    x_range, y_range, _ = util.axis_ranges(kwargs, y_range=(-1.0, 1.0))

    figure, axes = subplots(ncols=1 if overlay else len(signals), squeeze=False)
    axes = axes[0]
    axes[0].set_ylabel("Amplitude")

    for index, signal in enumerate(signals):
        if isinstance(signal, dict):
            color = signal.pop("color", next(palette))
            label = signal.pop("legend_label", None)
        else:
            color = next(palette)
            label = None

        x, y = util.signal_waveform(signal, normalize)
        x_range += (x[0], x[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x, y, color=color, label=label)
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Time (s)")
        if label:
            axis.legend()

    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)
    return figure
