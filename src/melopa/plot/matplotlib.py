"""Plotting routines with Matplotlib."""

# ruff: file-ignore[too-many-arguments]

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

import numpy
import scipy.signal
from marimo import Html
from matplotlib import pyplot

import melopa.util
from melopa import math
from melopa.plot import util
from melopa.plot.util import Range, Scale, Signal, sigdata

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from numpy.typing import NDArray

type AxesList = Sequence[Axes]
type Plot = AxesList | Sequence[AxesList] | Html


def frequency(
    *signals: Signal,
    axes: AxesList | None = None,
    depth: int = 3,
    figsize: tuple[float, float] | None = None,
    overlay: bool = True,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Plot:
    """Plot audio frequency spectrum."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))

    if axes is None:
        axes = subplots(
            figsize=figsize,
            ncols=1 if overlay else len(signals),
            squeeze=False,
            title=melopa.util.popall(kwargs, ["title", "t"], None),
        )[1][0]
    axes[0].set_ylabel(f"Level{scale.unit()}")
    ticks = util.spectrum_ticks()
    x_range, y_range = Range(20, 20_000, True), Range()
    datas = sigdata(signals, x=x, depth=depth)

    for index, data in enumerate(datas):
        if "f" in data:
            y = data["f"]
            length = len(y)
        else:
            y = scale(numpy.abs(numpy.fft.rfft(data["y"])))
            length = len(data["y"])
        rate_ = rate or data.get("rate", length)
        x_ = data.get("x", numpy.fft.rfftfreq(length, 1 / rate_))
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x_, y, color=data["color"], label=data["label"])
        axis.set_xlabel("Frequency (Hz)")
        axis.set_xscale("log")
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        axis.set_yscale(scale.axis())
        axis.legend(loc="upper right")
        axis.minorticks_off()

    set_ranges(axes, x_range, y_range)
    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0].figure)
    return axes


def grid(
    *signals: Signal,
    figsize: tuple[float, float] | None = None,
    overlay: bool = True,
    plots: list[str] | None = None,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Plot:
    """Plot multiple graphs vertically in a grid.

    Raises:
        ValueError: For invalid plot type.
    """
    overlay = kwargs.pop("o", overlay)
    plots = plots or kwargs.pop("p", ["frequency", "phase"])
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))

    axes = subplots(
        figsize=figsize,
        nrows=len(plots),
        ncols=1 if overlay else len(signals),
        squeeze=False,
        title=melopa.util.popall(kwargs, ["title", "t"], None),
    )[1]
    for idx, plot in enumerate(plots):
        if "line".startswith(plot):
            line(
                *signals,
                axes=axes[idx],
                depth=4,
                figsize=figsize,
                overlay=overlay,
                scale=scale,
                show=False,
                x=x,
                **kwargs,
            )
        elif "frequency".startswith(plot):
            frequency(
                *signals,
                axes=axes[idx],
                depth=4,
                figsize=figsize,
                overlay=overlay,
                rate=rate,
                scale=scale,
                show=False,
                x=x,
                **kwargs,
            )
        elif "phase".startswith(plot):
            phase(
                *signals,
                axes=axes[idx],
                depth=4,
                figsize=figsize,
                overlay=overlay,
                rate=rate,
                show=False,
                x=x,
                **kwargs,
            )
        elif "spectrogram".startswith(plot):
            spectrogram(
                *signals,
                axes=axes[idx],
                depth=4,
                figsize=figsize,
                rate=rate,
                show=False,
                **kwargs,
            )
        elif "waveform".startswith(plot):
            waveform(
                *signals,
                axes=axes[idx],
                depth=4,
                figsize=figsize,
                overlay=overlay,
                rate=rate,
                scale=scale,
                show=False,
                x=x,
                **kwargs,
            )
        else:
            msg = f"Unknown plot type '{plot}'."
            raise ValueError(msg)

    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0][0].figure)
    return axes


def line(
    *signals: Signal,
    axes: AxesList | None = None,
    depth: int = 3,
    figsize: tuple[float, float] | None = None,
    overlay: bool = True,
    scale: Scale = Scale.Linear,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Plot:
    """Plot line."""
    overlay = kwargs.pop("o", overlay)
    scale = Scale.from_prefix(kwargs.pop("s", scale))

    if axes is None:
        axes = subplots(
            figsize=figsize,
            ncols=1 if overlay else len(signals),
            squeeze=False,
            title=melopa.util.popall(kwargs, ["title", "t"], None),
        )[1][0]
    x_range, y_range = Range(), Range()
    datas = sigdata(signals, x=x, depth=depth)

    for index, data in enumerate(datas):
        x_ = data.pop("x", numpy.arange(len(data["y"])))
        y = scale(data["y"])
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x_, data["y"], color=data["color"], label=data["label"])
        axis.set_yscale(scale.axis())
        axis.legend(loc="upper right")

    set_ranges(axes, x_range, y_range)
    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0].figure)
    return axes


def phase(
    *signals: Signal,
    axes: AxesList | None = None,
    depth: int = 3,
    figsize: tuple[float, float] | None = None,
    overlay: bool = True,
    rate: int | None = None,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Plot:
    """Plot audio frequency phase."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)

    if axes is None:
        axes = subplots(
            figsize=figsize,
            ncols=1 if overlay else len(signals),
            squeeze=False,
            title=melopa.util.popall(kwargs, ["title", "t"], None),
        )[1][0]
    axes[0].set_ylabel("Phase (rad)")
    ticks = util.spectrum_ticks()
    x_range, y_range = Range(20, 20_000, True), Range()
    datas = sigdata(signals, x=x, depth=depth)

    for index, data in enumerate(datas):
        rate_ = rate or data.pop("rate", len(data["y"]))
        y = numpy.unwrap(numpy.angle(numpy.fft.rfft(data["y"])))
        x_ = data.pop("x", numpy.fft.rfftfreq(len(data["y"]), 1 / rate_))
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x_, y, color=data["color"], label=data["label"])
        axis.legend(loc="upper right")
        axis.set_xlabel("Frequency (Hz)")
        axis.set_xscale("log")
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        axis.minorticks_off()

    set_ranges(axes, x_range, y_range)
    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0].figure)
    return axes


def set_ranges(axes: AxesList, x_range: Range, y_range: Range) -> None:
    """Set ranges for axes if valid."""
    for axis in axes:
        if x_range.valid():
            axis.set_xlim(x_range.start, x_range.stop)
        if y_range.valid():
            axis.set_ylim(y_range.start, y_range.stop)


def signal(
    *signals: Signal,
    figsize: tuple[float, float] | None = None,
    kind: str = "waveform",
    normalize: bool = False,
    overlay: bool = True,
    **kwargs: Any,
) -> Plot:
    """Plot audio signals.

    Raises:
        ValueError: If kind value is invalid.
    """
    match kind.lower():
        case "frequency":
            plot = frequency(
                *signals,
                figsize=figsize,
                normalize=normalize,
                overlay=overlay,
                **kwargs,
            )
        case "phase":
            plot = phase(*signals, figsize=figsize, overlay=overlay, **kwargs)
        case "spectrogram":
            plot = spectrogram(*signals, figsize=figsize, normalize=normalize, **kwargs)
        case "waveform":
            plot = waveform(
                *signals,
                figsize=figsize,
                normalize=normalize,
                overlay=overlay,
                **kwargs,
            )
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)

    return plot


def spectrogram(  # ruff: ignore[too-many-locals]
    *signals: Signal,
    axes: AxesList | None = None,
    depth: int = 3,
    figsize: tuple[float, float] | None = None,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    **kwargs: Any,
) -> Plot:
    """Plot audio frequency time heatmap with Matplotlib."""
    rate = kwargs.pop("r", rate)

    if axes is None:
        axes = subplots(
            figsize=figsize,
            ncols=1,
            squeeze=False,
            title=melopa.util.popall(kwargs, ["title", "t"], None),
        )[1][0]
    axis = axes[0]
    axis.set_ylabel("Frequency (Hz)")
    ticks = util.spectrum_ticks()
    x_range, y_range = Range(), Range(20, 20_000, True)
    datas = sigdata(signals, depth=depth)

    for data in datas:
        rate_ = rate or data.pop("rate", len(data["y"]))
        transform = scipy.signal.ShortTimeFFT.from_window(
            ("gaussian", 1e-2 * rate_),
            fft_mode="onesided",
            fs=rate_,
            noverlap=64,
            nperseg=512,
        )
        bounds = transform.extent(len(scale(data["y"])), center_bins=True)

        z_ = transform.stft(scale(data["y"]))
        x = numpy.linspace(bounds[0], bounds[1], num=z_.shape[1])
        y = numpy.linspace(bounds[2], bounds[3], num=z_.shape[0])
        z = math.decibel(numpy.abs(z_))
        x_range += (x.min(), x.max())
        y_range += (y.min(), y.max())

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

    set_ranges(axes, x_range, y_range)
    axis.figure.colorbar(mesh, ax=axes, label="Level (dB)")
    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0].figure)
    return axes


def subplots(
    *args: Any,
    figsize: tuple[float, float] | None = None,
    title: str | None = None,
    **kwargs: Any,
) -> tuple[Figure, Sequence[AxesList]]:
    """Wrapper for Matplotlib subplots."""
    figsize = figsize or (10, 5)
    figure, axes = pyplot.subplots(
        *args, figsize=figsize, layout="compressed", **kwargs
    )
    if title is not None:
        figure.suptitle(title)
    return figure, axes


def waveform(
    *signals: Signal,
    axes: AxesList | None = None,
    depth: int = 3,
    figsize: tuple[float, float] | None = None,
    overlay: bool = True,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Plot:
    """Plot audio waveform."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))

    if axes is None:
        axes = subplots(
            figsize=figsize,
            ncols=1 if overlay else len(signals),
            squeeze=False,
            title=melopa.util.popall(kwargs, ["title", "t"], None),
        )[1][0]
    axes[0].set_ylabel(f"Amplitude{scale.unit()}")
    x_range, y_range = Range(), Range(-1, 1, True)
    datas = sigdata(signals, x=x, depth=depth)

    for index, data in enumerate(datas):
        rate_ = rate or data.pop("rate", len(data["y"]))
        x_ = data.pop("x", numpy.linspace(0, len(data["y"]) / rate_, len(data["y"])))
        y = scale(data["y"])
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())

        axis = axes[0 if overlay else index]
        axis.plot(x_, y, color=data["color"], label=data["label"])
        axis.set_xlabel("Time (s)")
        axis.set_yscale(scale.axis())
        axis.legend(loc="upper right")

    set_ranges(axes, x_range, y_range)
    if melopa.util.in_marimo():
        marimo = importlib.import_module("marimo")
        return marimo.mpl.interactive(axes[0].figure)
    return axes
