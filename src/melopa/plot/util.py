"""Utility functions for plotting."""

import dataclasses
import itertools
from collections.abc import Iterable
from enum import Enum
from typing import Any, Self, Union, cast

import numpy
from numpy.typing import NDArray

import melopa.util
from melopa import math

type Signal = NDArray | tuple[NDArray, NDArray] | dict[str, Any]


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


class Scale(Enum):
    """Signal amplitude scale."""

    Decibel = "decibel"
    FullScale = "fullscale"
    Linear = "linear"
    Normalized = "normalized"

    def __call__(self, array: NDArray) -> NDArray:
        """Transform array to scale."""
        if self == Scale.Decibel:
            return math.decibel(array)
        if self == Scale.FullScale:
            return math.decibel(math.normalize(array))
        if self == Scale.Normalized:
            return math.normalize(array)
        return array

    def __str__(self) -> str:
        """Get string representation."""
        return self.value

    def axis(self) -> str:
        """Get axis scale."""
        return {
            Scale.Decibel: "log",
            Scale.FullScale: "log",
            Scale.Linear: "linear",
            Scale.Normalized: "linear",
        }[self]

    @classmethod
    def from_prefix(cls, value: Union[str, "Scale"]) -> "Scale":
        """Create Scale instance from value prefix.

        Raises:
            ValueError: For invalid value.
        """
        if isinstance(value, Scale):
            return value

        value_ = value.lower()
        if "decibel".startswith(value_) or value_ == "db":
            return cls.Decibel
        if "fullscale".startswith(value_) or value_ == "dbfs":
            return cls.FullScale
        if "linear".startswith(value_):
            return cls.Linear
        if "normalized".startswith(value_):
            return cls.Normalized
        msg = f"Invalid scale value '{value}'"
        raise ValueError(msg)

    def unit(self) -> str:
        """Get plot axis label unit."""
        return {
            Scale.Decibel: " (dB)",
            Scale.FullScale: " (dBFS)",
            Scale.Linear: "",
            Scale.Normalized: "",
        }[self]


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
    """Create a cycle of colors for plotting.

    Based on D3's Category10 palette,
    https://d3js.org/d3-scale-chromatic/categorical#schemeCategory10.
    """
    return itertools.cycle((
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ))


def sigdata(
    signals: Iterable[Signal],
    x: NDArray | None = None,
    depth: int = 3,
) -> list[dict[str, Any]]:
    """Convert signal into standardized format."""
    palette = palette_cycle()

    datas = []
    for index, signal in enumerate(signals):
        if isinstance(signal, dict):
            signal = cast("dict[str, Any]", signal)
            if "f" in signal:
                values = {"f": math.mono(numpy.asarray(signal.pop("f")))}
            else:
                values = {"y": math.mono(numpy.asarray(signal.pop("y")))}
            x_ = signal.pop("x", x)
            color = melopa.util.popall(signal, ["color", "c"], next(palette))
            label = melopa.util.popall(
                signal,
                ["label", "l"],
                melopa.util.varname(signal, str(index), depth=depth),
            )
            data = {
                **signal,
                **values,
                "color": color,
                "label": label,
            }
            if x_ is not None:
                data["x"] = math.mono(numpy.asarray(x_))
        elif isinstance(signal, tuple):
            signal = cast("tuple[NDArray, NDArray]", signal)
            x_, y = signal
            data = {
                "x": math.mono(numpy.asarray(x_)),
                "y": math.mono(numpy.asarray(y)),
                "color": next(palette),
                "label": melopa.util.varname(signal, str(index), depth=depth),
            }
        else:
            y = math.mono(numpy.asarray(signal))
            data = {
                "y": y,
                "color": next(palette),
                "label": melopa.util.varname(signal, str(index), depth=depth),
            }
            if x is not None:
                data["x"] = math.mono(numpy.asarray(x))
        datas.append(data)
    return datas


def spectrum_ticks() -> tuple[list[float], list[str]]:
    """Generate frequency spectrum plot ticks as octaves centered at 440Hz."""
    ticks = 440 * 2.0 ** numpy.arange(-4, 6)
    labels = [f"{tick:g}" if tick < 1_000 else f"{tick / 1_000:g}k" for tick in ticks]
    return ticks.tolist(), labels
