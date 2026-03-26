"""Utility functions for plotting."""

import itertools
from typing import Any

import numpy
from bokeh.palettes import Category10
from numpy.typing import NDArray

from melopa import math


def palette_cycle() -> itertools.cycle:
    """Create a cycle of colors for plotting."""
    return itertools.cycle(Category10[10])


def signal_spectrum(
    signal: dict[str, Any], size: int = 65_536
) -> tuple[NDArray, NDArray]:
    """Extract frequency spectrum from signal dictionary."""
    if "f" in signal:
        y = signal.pop("f")
    else:
        y_ = signal.pop("y")
        y = math.decibel(numpy.fft.rfft(y_))

    if "x" in signal:
        x = signal.pop("x")
    else:
        length = 2 * (len(y) - 1)
        rate = signal.pop("rate")
        x = numpy.fft.rfftfreq(length, 1 / rate)

    return x.astype(numpy.float32), y.astype(numpy.float32)


def signal_waveform(
    signal: dict[str, Any], size: int = 65_536
) -> tuple[NDArray, NDArray]:
    """Extract waveform from signal dictionary."""
    y = signal.pop("y")
    if "x" in signal:
        x = signal.pop("x")
    else:
        rate = signal.pop("rate")
        x = numpy.linspace(0, len(y) / rate, len(y))

    return x.astype(numpy.float32), y.astype(numpy.float32)


def spectrum_ticks() -> tuple[list[float], list[str]]:
    """Generate frequency spectrum plot ticks as octaves centered at 440Hz."""
    ticks = 440 * 2.0 ** numpy.arange(-4, 6)
    labels = [f"{tick:g}" if tick < 1_000 else f"{tick / 1_000:g}k" for tick in ticks]
    return ticks.tolist(), labels
