"""Plotting routines with Bokeh."""

from typing import Any

import numpy
from bokeh import layouts, plotting
from bokeh.models import FixedTicker, Pane, Range1d

from melopa.plot import util


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio frequency time heatmap with Bokeh."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio frequency spectrum with Bokeh."""
    palette = util.palette_cycle()
    plots = []
    ticks = util.spectrum_ticks()

    for signal in signals:
        x, y = util.signal_spectrum(signal)
        color = signal.pop("color", next(palette))

        if kwargs.pop("smooth", False):
            y = numpy.convolve(y, numpy.ones(16) / 16, mode="same")
        if overlay:
            if plots:
                plot = plots[0]
            else:
                plot = plotting.figure(
                    output_backend="webgl",
                    sizing_mode="stretch_width",
                    x_axis_label="Frequency (Hz)",
                    x_axis_type="log",
                    x_range=Range1d(20, 20_000),
                    y_axis_label="Amplitude (dB)",
                    **kwargs,
                )
                plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
                plots.append(plot)
        else:
            plot = plotting.figure(
                output_backend="webgl",
                sizing_mode="stretch_width",
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                x_range=Range1d(20, 20_000),
                y_axis_label="Amplitude (dB)",
                **kwargs,
            )
            plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
            plots.append(plot)

        plot.line(
            x=x,
            y=y,
            color=color,
            line_width=2,
            **signal,
        )
        if overlay and len(signals) > 1:
            plot.legend.click_policy = "mute"
        plot.toolbar.logo = None
    return layouts.row(plots, sizing_mode="stretch_width")


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Pane:
    """Plot audio waveform with Bokeh."""
    palette = util.palette_cycle()
    x_range = Range1d(0, 0)
    plots = []

    for signal in signals:
        x, y = util.signal_waveform(signal)
        x_range.end = max(x[-1], x_range.end)
        color = signal.pop("color", next(palette))

        if overlay:
            if plots:
                plot = plots[0]
            else:
                plot = plotting.figure(
                    output_backend="webgl",
                    sizing_mode="stretch_width",
                    x_axis_label="Time (s)",
                    x_range=x_range,
                    y_axis_label="Amplitude",
                    y_range=Range1d(-1, 1),
                    tools="pan,box_zoom,wheel_zoom,save,reset,undo,redo",
                    **kwargs,
                )
                plots.append(plot)
        else:
            if plots:
                # Share pan tools over both plots.
                plot = plotting.figure(
                    output_backend="webgl",
                    sizing_mode="stretch_width",
                    x_axis_label="Time (s)",
                    x_range=plots[0].x_range,
                    y_range=plots[0].y_range,
                    tools="pan,box_zoom,wheel_zoom,save,reset,undo,redo",
                    **kwargs,
                )
            else:
                plot = plotting.figure(
                    output_backend="webgl",
                    sizing_mode="stretch_width",
                    x_axis_label="Time (s)",
                    x_range=x_range,
                    y_axis_label="Amplitude",
                    y_range=Range1d(-1, 1),
                    **kwargs,
                )
            plots.append(plot)

        plot.line(
            x=x,
            y=y,
            color=color,
            line_width=2,
            **signal,
        )
        if overlay and len(signals) > 1:
            plot.legend.click_policy = "mute"
        plot.toolbar.logo = None
    return layouts.row(plots, sizing_mode="stretch_width")
