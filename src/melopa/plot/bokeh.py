"""Plotting routines with Bokeh."""

from typing import Any

from bokeh import layouts, plotting
from bokeh.models import ColumnDataSource, FixedTicker, Legend, Pane, Range1d

from melopa.plot import util


def figure(*args: Any, **kwargs: Any) -> plotting.figure:
    """Melopa wrapper for Bokeh figures."""
    figure_ = plotting.figure(
        *args,
        output_backend="webgl",
        sizing_mode="stretch_width",
        tools="fullscreen,pan,box_zoom,wheel_zoom,undo,redo,reset,save",
        **kwargs,
    )
    figure_.add_layout(Legend(click_policy="mute"))
    figure_.toolbar.logo = None
    return figure_


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio frequency time heatmap with Bokeh."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio frequency spectrum with Bokeh."""
    palette = util.palette_cycle()
    plots = []
    ticks = util.spectrum_ticks()

    for signal in signals:
        color = signal.pop("color", next(palette))
        method = signal.pop("method", "line")
        x, y = util.signal_spectrum(signal)
        source = ColumnDataSource(data={"x": x, "y": y})

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Frequency (Hz)",
                    x_axis_type="log",
                    x_range=Range1d(start=20, end=20_000, bounds="auto"),
                    y_axis_label="Amplitude (dB)",
                    **kwargs,
                )
                plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
                plots.append(plot)
        else:
            plot = figure(
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                x_range=Range1d(start=20, end=20_000, bounds="auto"),
                y_axis_label="Amplitude (dB)",
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
    return layouts.row(plots, sizing_mode="stretch_width")


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio waveform with Bokeh."""
    palette = util.palette_cycle()
    x_range_set = "x_range" in kwargs
    x_range = Range1d(*kwargs.pop("x_range", (0, 0)), bounds="auto")
    y_range = Range1d(*kwargs.pop("y_range", (-1, 1)), bounds="auto")
    plots = []

    for signal in signals:
        color = signal.pop("color", next(palette))
        method = signal.pop("method", "line")
        x, y = util.signal_waveform(signal)
        source = ColumnDataSource(data={"x": x, "y": y})
        if not x_range_set:
            x_range.start = min(x[0], x_range.start)
            x_range.end = max(x[-1], x_range.end)

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Time (s)",
                    x_range=x_range,
                    y_axis_label="Amplitude",
                    y_range=y_range,
                    **kwargs,
                )
                plots.append(plot)
        else:
            plot = figure(
                x_axis_label="Time (s)",
                x_range=x_range,
                y_axis_label="Amplitude",
                y_range=y_range,
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
    return layouts.row(plots, sizing_mode="stretch_width")
