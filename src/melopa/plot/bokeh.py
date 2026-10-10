"""Plotting routines with Bokeh."""

# ruff: file-ignore[too-many-arguments]

from pathlib import Path
from typing import Any, cast

import numpy
import scipy.signal
from bokeh import io, layouts, palettes, plotting, transform
from bokeh.events import DocumentReady, RangesUpdate
from bokeh.models import (
    ColorBar,
    ColumnDataSource,
    CustomJS,
    DataRange1d,
    FixedTicker,
    Legend,
    LinearColorMapper,
    Pane,
    Range1d,
    UIElement,
)
from numpy.typing import NDArray

import melopa.math
import melopa.util
from melopa.plot import util
from melopa.plot.util import Scale, Signal, sigdata

PLOT_SIZE = 16_384


def add_downsample(
    plot: plotting.figure, source: ColumnDataSource, size: int = PLOT_SIZE
) -> None:
    """Add JavaScript downsampling callbacks to Bokeh plot."""
    callback = CustomJS.from_file(
        Path(__file__).parents[1] / "downsample.mjs",
        size=size,
        source=source,
    )
    io.curdoc().js_on_event(DocumentReady, callback)
    plot.js_on_event(RangesUpdate, callback)


def figure(*args: Any, title: str | None = None, **kwargs: Any) -> plotting.figure:
    """Melopa wrapper for Bokeh figures."""
    x_range = kwargs.pop("x_range", DataRange1d(range_padding=0))
    y_range = kwargs.pop("y_range", DataRange1d(range_padding=0))

    figure_ = plotting.figure(
        *args,
        output_backend="webgl",
        sizing_mode="stretch_width",
        toolbar_location="above",
        tools="fullscreen,pan,box_zoom,wheel_zoom,undo,redo,reset,save",
        title=title,
        x_range=x_range,
        y_range=y_range,
        **kwargs,
    )
    figure_.add_layout(Legend(click_policy="hide"))
    figure_.toolbar.logo = None
    return figure_


def frequency(
    *signals: Signal,
    depth: int = 3,
    overlay: bool = True,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    size: int = PLOT_SIZE,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Pane:
    """Plot audio frequency spectrum with Bokeh."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))
    title = melopa.util.popall(kwargs, ["title", "t"], None)
    plots: list[plotting.figure] = []
    ticks = util.spectrum_ticks()
    x_range, y_range, _ = util.axis_ranges(kwargs, x_range=(20, 20_000))

    for data in sigdata(signals, x=x, depth=depth):
        color = data["color"]
        label = data["label"]
        rate_ = rate or data.get("rate", len(data["y"]))
        y = scale(numpy.abs(numpy.fft.rfft(data["y"])))
        x_ = data.get("x", numpy.fft.rfftfreq(len(data["y"]), 1 / rate_))
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x_, "y": y})

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Frequency (Hz)",
                    x_axis_type="log",
                    **kwargs,
                )
                plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
                plots.append(plot)
        else:
            plot = figure(
                title=title,
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                y_axis_label=f"Level{scale.unit()}",
                **kwargs,
            )
            plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
            plots.append(plot)

        plot.line(
            x="x",
            y="y",
            color=color,
            label=label,
            line_width=2,
            source=source,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if len(plots) == 1:
        return plots[0]
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def grid(
    *signals: Signal,
    overlay: bool = True,
    plots: list[str] | None = None,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    size: int = PLOT_SIZE,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Pane:
    """Plot multiple graphs vertically in a grid.

    Raises:
        ValueError: For invalid plot type.
    """
    overlay = kwargs.pop("o", overlay)
    plots = plots or kwargs.pop("p", ["frequency", "phase"])
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))

    plot_panels: list[plotting.figure] = []
    for plot_name in plots:
        if "frequency".startswith(plot_name):
            panel = frequency(
                *signals,
                overlay=overlay,
                rate=rate,
                scale=scale,
                size=size,
                x=x,
                **kwargs,
            )
        elif "line".startswith(plot_name):
            panel = line(
                *signals,
                overlay=overlay,
                scale=scale,
                size=size,
                x=x,
                **kwargs,
            )
        elif "phase".startswith(plot_name):
            panel = phase(
                *signals,
                overlay=overlay,
                rate=rate,
                size=size,
                x=x,
                **kwargs,
            )
        elif "spectrogram".startswith(plot_name):
            panel = spectrogram(*signals, rate=rate, **kwargs)
        elif "waveform".startswith(plot_name):
            panel = waveform(
                *signals,
                overlay=overlay,
                rate=rate,
                scale=scale,
                size=size,
                x=x,
                **kwargs,
            )
        else:
            msg = f"Unknown plot type '{plot_name}'."
            raise ValueError(msg)

        if hasattr(panel, "children"):
            children = cast("list[plotting.figure]", panel.children)
            plot_panels.append(children[0])
        else:
            plot_panels.append(cast("plotting.figure", panel))

    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plot_panels]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def gridplot(plots: list[plotting.figure]) -> Pane:
    """Melopa wrapper for Bokeh gridplot."""
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def line(
    *signals: Signal,
    overlay: bool = True,
    scale: Scale = Scale.Linear,
    size: int = PLOT_SIZE,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Pane:
    """Plot line with Bokeh."""
    overlay = kwargs.pop("o", overlay)
    scale = Scale.from_prefix(kwargs.pop("s", scale))
    title = melopa.util.popall(kwargs, ["title", "t"], None)
    plots: list[plotting.figure] = []
    x_range, y_range, _ = util.axis_ranges(kwargs)

    for data in sigdata(signals, x=x, depth=3):
        color = data["color"]
        label = data["label"]
        y = scale(data["y"])
        x_ = data.pop("x", numpy.arange(len(data["y"])))
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x_, "y": y})

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(**kwargs)
                plots.append(plot)
        else:
            plot = figure(title=title, **kwargs)
            plots.append(plot)

        plot.line(
            x="x",
            y="y",
            color=color,
            label=label,
            line_width=2,
            source=source,
        )
        plot.y_axis_label = f"Value{scale.unit()}"
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if len(plots) == 1:
        return plots[0]
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def phase(
    *signals: Signal,
    overlay: bool = True,
    rate: int | None = None,
    size: int = PLOT_SIZE,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Pane:
    """Plot audio frequency phase with Bokeh."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)
    title = melopa.util.popall(kwargs, ["title", "t"], None)
    plots: list[plotting.figure] = []
    ticks = util.spectrum_ticks()
    x_range, y_range, _ = util.axis_ranges(kwargs, x_range=(20, 20_000))

    for data in sigdata(signals, x=x, depth=3):
        color = data["color"]
        label = data["label"]
        rate_ = rate or data.get("rate", len(data["y"]))
        y = numpy.unwrap(numpy.angle(numpy.fft.rfft(data["y"])))
        x_ = data.get("x", numpy.fft.rfftfreq(len(data["y"]), 1 / rate_))
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x_, "y": y})

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Frequency (Hz)",
                    x_axis_type="log",
                    **kwargs,
                )
                plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
                plots.append(plot)
        else:
            plot = figure(
                title=title,
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                y_axis_label="Phase (rad)",
                **kwargs,
            )
            plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
            plots.append(plot)

        plot.line(
            x="x",
            y="y",
            color=color,
            label=label,
            line_width=2,
            source=source,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if len(plots) == 1:
        return plots[0]
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def spectrogram(  # ruff: ignore[too-many-locals]
    *signals: Signal,
    depth: int = 3,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    **kwargs: Any,
) -> Pane:
    """Plot audio frequency time heatmap with Bokeh."""
    rate = kwargs.pop("r", rate)
    title = melopa.util.popall(kwargs, ["title", "t"], None)
    plots: list[plotting.figure] = []
    palette = palettes.viridis(6)
    ticks = util.spectrum_ticks()
    x_range, y_range, z_range = util.axis_ranges(kwargs, y_range=(20, 20_000))

    for data in sigdata(signals, depth=depth):
        rate_ = rate or data.get("rate", len(data["y"]))
        y_data = scale(data["y"])

        transform_ = scipy.signal.ShortTimeFFT.from_window(
            ("gaussian", 1e-2 * rate_),
            fft_mode="onesided",
            fs=rate_,
            noverlap=64,
            nperseg=512,
        )
        bounds = transform_.extent(len(y_data), center_bins=True)

        z_ = transform_.stft(y_data)
        x = numpy.linspace(bounds[0], bounds[1], num=z_.shape[1])
        y = numpy.linspace(bounds[2], bounds[3], num=z_.shape[0])
        z = melopa.math.decibel(numpy.abs(z_))
        x_range += (x.min(), x.max())
        y_range += (y.min(), y.max())
        z_range += (z.min(), z.max())
        colormap = transform.linear_cmap(
            field_name="z", palette=palette, low=numpy.min(z), high=numpy.max(z)
        )
        source = ColumnDataSource(
            data={
                "x": numpy.tile(x, len(y)),
                "y": numpy.repeat(y, len(x)),
                "z": z.ravel(),
            }
        )

        if plots:
            plot = figure(
                x_axis_label="Time (s)",
                y_axis_type="log",
                **kwargs,
            )
            plot.yaxis.ticker = FixedTicker(ticks=ticks[0])
            plot.grid.grid_line_width = 0
            plots.append(plot)
        else:
            plot = figure(
                title=title,
                x_axis_label="Time (s)",
                y_axis_label="Frequency (Hz)",
                y_axis_type="log",
                **kwargs,
            )
            plot.yaxis.ticker = FixedTicker(ticks=ticks[0])
            plot.grid.grid_line_width = 0
            plots.append(plot)

        plot.rect(
            x="x",
            y="y",
            fill_color=colormap,
            height=y[1] - y[0],
            source=source,
            width=x[1] - x[0],
        )

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range
    plots[-1].add_layout(
        ColorBar(
            color_mapper=LinearColorMapper(
                palette=palette,
                high=z_range.stop,
                low=z_range.start,
            ),
            title="Level (dB)",
        ),
        "right",
    )

    if len(plots) == 1:
        return plots[0]
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def waveform(
    *signals: Signal,
    depth: int = 3,
    overlay: bool = True,
    rate: int | None = None,
    scale: Scale = Scale.Linear,
    size: int = PLOT_SIZE,
    x: NDArray | None = None,
    **kwargs: Any,
) -> Pane:
    """Plot audio waveform with Bokeh."""
    overlay = kwargs.pop("o", overlay)
    rate = kwargs.pop("r", rate)
    scale = Scale.from_prefix(kwargs.pop("s", scale))
    title = melopa.util.popall(kwargs, ["title", "t"], None)
    plots: list[plotting.figure] = []
    x_range, y_range, _ = util.axis_ranges(kwargs, y_range=(-1, 1))

    for data in sigdata(signals, x=x, depth=depth):
        color = data["color"]
        label = data["label"]
        rate_ = rate or data.get("rate", len(data["y"]))
        x_ = data.get("x", numpy.linspace(0, len(data["y"]) / rate_, len(data["y"])))
        y = scale(data["y"])
        x_range += (x_[0], x_[-1])
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x_, "y": y})

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Time (s)",
                    **kwargs,
                )
                plots.append(plot)
        else:
            plot = figure(
                title=title,
                x_axis_label="Time (s)",
                y_axis_label=f"Amplitude{scale.unit()}",
                **kwargs,
            )
            plots.append(plot)

        plot.line(
            x="x",
            y="y",
            color=color,
            label=label,
            line_width=2,
            source=source,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range

    if len(plots) == 1:
        return plots[0]
    return layouts.gridplot(
        cast("list[list[UIElement | None]]", [plots]),
        sizing_mode="stretch_width",
        toolbar_location="above",
    )
