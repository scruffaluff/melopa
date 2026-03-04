"""Plotting routines with Bokeh."""

from typing import Any

from bokeh import layouts, plotting
from bokeh.models import FixedTicker, Legend, Pane, Range1d

from melopa.plot import util


def figure(*args: Any, **kwargs: Any) -> plotting.figure:
    """Melopa wrapper for Bokeh figures."""
    figure_ = plotting.figure(
        *args,
        output_backend="webgl",
        sizing_mode="stretch_width",
        tools="pan,box_zoom,wheel_zoom,save,reset,undo,redo",
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
        x, y = util.signal_spectrum(signal)
        color = signal.pop("color", next(palette))

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Frequency (Hz)",
                    x_axis_type="log",
                    x_range=Range1d(20, 20_000),
                    y_axis_label="Amplitude (dB)",
                    y_range=Range1d(-1, 1),
                    **kwargs,
                )
                plot.xaxis.ticker = FixedTicker(ticks=ticks[0])
                plots.append(plot)
        else:
            plot = figure(
                x_axis_label="Frequency (Hz)",
                x_axis_type="log",
                x_range=Range1d(20, 20_000),
                y_axis_label="Amplitude (dB)",
                y_range=Range1d(-1, 1),
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

        if plots:
            if overlay:
                plot = plots[0]
            else:
                plot = figure(
                    x_axis_label="Time (s)",
                    x_range=x_range,
                    y_axis_label="Amplitude",
                    y_range=Range1d(-1, 1),
                    **kwargs,
                )
                plots.append(plot)
        else:
            plot = figure(
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
    return layouts.row(plots, sizing_mode="stretch_width")
