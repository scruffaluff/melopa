"""Plotting routines with Bokeh."""

from pathlib import Path
from typing import Any

from bokeh import io, layouts, plotting
from bokeh.events import DocumentReady, RangesUpdate
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    FixedTicker,
    Legend,
    Pane,
    Range1d,
)

from melopa.plot import util


def add_downsample(
    plot: plotting.figure, source: ColumnDataSource, size: int = 65_536
) -> None:
    """Add JavaScript downsampling callbacks to Bokeh plot."""
    callback = CustomJS.from_file(
        Path(__file__).parents[1] / "downsample.mjs",
        size=size,
        source=source,
    )
    io.curdoc().js_on_event(DocumentReady, callback)
    plot.js_on_event(RangesUpdate, callback)


def figure(*args: Any, **kwargs: Any) -> plotting.figure:
    """Melopa wrapper for Bokeh figures."""
    figure_ = plotting.figure(
        *args,
        output_backend="webgl",
        sizing_mode="stretch_width",
        tools="fullscreen,pan,box_zoom,wheel_zoom,undo,redo,reset,save",
        **kwargs,
    )
    figure_.add_layout(Legend(click_policy="hide"))
    figure_.toolbar.logo = None
    return figure_


def phase(
    signals: list[dict], overlay: bool = True, size: int = 65_536, **kwargs: Any
) -> Pane:
    """Plot audio frequency phase with Bokeh."""
    plots = []
    palette = util.palette_cycle()
    ticks = util.spectrum_ticks()
    x_range, y_range = util.axis_ranges(kwargs, x_range=(20, 20_000))

    for signal in signals:
        color = signal.pop("color", next(palette))
        method = signal.pop("method", "line")
        x, y = util.signal_phase(signal)
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x, "y": y})

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
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                y_axis_label="Phase (rad)",
                **kwargs,
            )
            plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
            plots.append(plot)

        getattr(plot, method)(
            x="x",
            y="y",
            color=color,
            line_width=2,
            source=source,
            **signal,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range
    return layouts.gridplot(
        [plots],
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def spectrogram(signals: list[dict], **kwargs: Any) -> Pane:
    """Plot audio frequency time heatmap with Bokeh."""
    raise NotImplementedError


def spectrum(
    signals: list[dict], overlay: bool = True, size: int = 65_536, **kwargs: Any
) -> Pane:
    """Plot audio frequency spectrum with Bokeh."""
    plots = []
    palette = util.palette_cycle()
    ticks = util.spectrum_ticks()
    x_range, y_range = util.axis_ranges(kwargs, x_range=(20, 20_000))

    for signal in signals:
        color = signal.pop("color", next(palette))
        method = signal.pop("method", "line")
        x, y = util.signal_spectrum(signal)
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x, "y": y})

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
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                y_axis_label="Volume (dB)",
                **kwargs,
            )
            plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
            plots.append(plot)

        getattr(plot, method)(
            x="x",
            y="y",
            color=color,
            line_width=2,
            source=source,
            **signal,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range
    return layouts.gridplot(
        [plots],
        sizing_mode="stretch_width",
        toolbar_location="above",
    )


def waveform(
    signals: list[dict], overlay: bool = True, size: int = 65_536, **kwargs: Any
) -> Pane:
    """Plot audio waveform with Bokeh."""
    plots = []
    palette = util.palette_cycle()
    x_range, y_range = util.axis_ranges(kwargs, y_range=(-1.0, 1.0))

    for signal in signals:
        color = signal.pop("color", next(palette))
        method = signal.pop("method", "line")
        x, y = util.signal_waveform(signal)
        x_range += (x[0], x[-1])
        y_range += (y.min(), y.max())
        source = ColumnDataSource(data={"x": x, "y": y})

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
                x_axis_label="Time (s)",
                y_axis_label="Amplitude",
                **kwargs,
            )
            plots.append(plot)

        getattr(plot, method)(
            x="x",
            y="y",
            color=color,
            line_width=2,
            source=source,
            **signal,
        )
        add_downsample(plot, source, size)

    if x_range.valid():
        plots[0].x_range = Range1d(start=x_range.start, end=x_range.stop)
    if y_range.valid():
        plots[0].y_range = Range1d(start=y_range.start, end=y_range.stop)
    for plot in plots[1:]:
        plot.x_range = plots[0].x_range
        plot.y_range = plots[0].y_range
    return layouts.gridplot(
        [plots],
        sizing_mode="stretch_width",
        toolbar_location="above",
    )
