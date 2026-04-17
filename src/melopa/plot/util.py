"""Utility functions for plotting."""

import dataclasses
import itertools
from typing import Any, Self

import numpy
from bokeh.palettes import Category10
from numpy.typing import NDArray
from scipy.signal import ShortTimeFFT

from melopa import math


@dataclasses.dataclass
class Range:
    """Plot axis range with support for expanding bounds."""

    start: float = numpy.inf
    stop: float = -numpy.inf
    fixed: bool = False

    def __iadd__(self, other: tuple[float, float]) -> Self:
        """Expand bounds if necessary."""
        if not self.fixed:
            self.start = min(other[0], self.start)
            self.stop = max(other[1], self.stop)
        return self

    def valid(self) -> bool:
        """Check if bounds are valid."""
        return self.start < self.stop


def axis_ranges(
    kwargs: dict[str, Any],
    x_range: tuple[float, float] | None = None,
    y_range: tuple[float, float] | None = None,
    z_range: tuple[float, float] | None = None,
) -> tuple[Range, Range, Range]:
    """Parse axis ranges from plot keyword arguments."""
    if "x_range" in kwargs:
        x_range_ = Range(kwargs["x_range"][0], kwargs["x_range"][1], True)
    elif x_range is None:
        x_range_ = Range()
    else:
        x_range_ = Range(x_range[0], x_range[1])

    if "y_range" in kwargs:
        y_range_ = Range(kwargs["y_range"][0], kwargs["y_range"][1], True)
    elif y_range is None:
        y_range_ = Range()
    else:
        y_range_ = Range(y_range[0], y_range[1])

    if "z_range" in kwargs:
        z_range_ = Range(kwargs["z_range"][0], kwargs["z_range"][1], True)
    elif z_range is None:
        z_range_ = Range()
    else:
        z_range_ = Range(z_range[0], z_range[1])
    return x_range_, y_range_, z_range_


def palette_cycle() -> itertools.cycle:
    """Create a cycle of colors for plotting."""
    return itertools.cycle(Category10[10])


def signal_phase(signal: dict[str, Any]) -> tuple[NDArray, NDArray]:
    """Extract frequency phase from signal dictionary."""
    if "f" in signal:
        y = signal.pop("f")
    else:
        y_ = signal.pop("y")
        y = numpy.unwrap(numpy.angle(numpy.fft.rfft(y_)))

    if "x" in signal:
        x = signal.pop("x")
    else:
        length = 2 * (len(y) - 1)
        rate = signal.pop("rate")
        x = numpy.fft.rfftfreq(length, 1 / rate)

    return x.astype(numpy.float32), y.astype(numpy.float32)


def signal_spectrogram(
    signal: dict[str, Any], normalize: bool = False
) -> tuple[NDArray, NDArray, NDArray]:
    """Extract time binned frequency spectrum from signal dictionary."""
    y_ = signal.pop("y")
    rate = signal.pop("rate")
    length = len(y_)

    transform = ShortTimeFFT.from_window(
        ("gaussian", 1e-2 * rate),
        fft_mode="onesided",
        fs=rate,
        noverlap=64,
        nperseg=512,
    )
    bounds = transform.extent(length, center_bins=True)

    z = transform.stft(y_)
    if normalize:
        z = math.normalize(z)
    x = numpy.linspace(bounds[0], bounds[1], num=z.shape[1], dtype=numpy.float32)
    y = numpy.linspace(bounds[2], bounds[3], num=z.shape[0], dtype=numpy.float32)
    return x, y, math.decibel(z).astype(numpy.float32)


def signal_spectrum(
    signal: dict[str, Any], normalize: bool = False
) -> tuple[NDArray, NDArray]:
    """Extract frequency spectrum from signal dictionary."""
    y = signal.pop("f") if "f" in signal else numpy.fft.rfft(signal.pop("y"))
    if "x" in signal:
        x = signal.pop("x")
    else:
        length = 2 * (len(y) - 1)
        rate = signal.pop("rate")
        x = numpy.fft.rfftfreq(length, 1 / rate)

    if normalize:
        y = math.normalize(y)
    return x.astype(numpy.float32), math.decibel(y).astype(numpy.float32)


def signal_waveform(
    signal: dict[str, Any], normalize: bool = False
) -> tuple[NDArray, NDArray]:
    """Extract waveform from signal dictionary."""
    y = signal.pop("y")
    if "x" in signal:
        x = signal.pop("x")
    else:
        rate = signal.pop("rate")
        x = numpy.linspace(0, len(y) / rate, len(y))

    if normalize:
        y = math.normalize(y)
    return x.astype(numpy.float32), y.astype(numpy.float32)


def spectrum_ticks() -> tuple[list[float], list[str]]:
    """Generate frequency spectrum plot ticks as octaves centered at 440Hz."""
    ticks = 440 * 2.0 ** numpy.arange(-4, 6)
    labels = [f"{tick:g}" if tick < 1_000 else f"{tick / 1_000:g}k" for tick in ticks]
    return ticks.tolist(), labels
