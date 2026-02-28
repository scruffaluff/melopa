"""Plotting routines with Matplotlib."""

from typing import Any

from matplotlib import pyplot
from matplotlib.figure import Figure

from melopa.plot import util


def spectrogram(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency time heatmap with Matplotlib."""
    raise NotImplementedError


def spectrum(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio frequency spectrum with Matplotlib."""
    palette = util.palette_cycle()
    figure, axes = pyplot.subplots(
        figsize=(12, 6), ncols=1 if overlay else len(signals)
    )
    figure.tight_layout()
    ticks = util.spectrum_ticks()

    for index, signal in enumerate(signals):
        x, y = util.signal_spectrum(signal)

        axis = axes if overlay else axes[index]
        axis.semilogx(x, y, color=next(palette), label=signal.pop("legend_label", None))
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Frequency (s)")
        axis.set_xlim(20, 20_000)
        axis.set_xticks(ticks[0])
        axis.set_xticklabels(ticks[1])
        if index == 0:
            axis.set_ylabel("Amplitude (dB)")
        axis.legend()
        axis.minorticks_off()
    return figure


def waveform(signals: list[dict], overlay: bool = True, **kwargs: Any) -> Figure:
    """Plot audio waveform with Matplotlib."""
    palette = util.palette_cycle()
    figure, axes = pyplot.subplots(
        figsize=(12, 6), ncols=1 if overlay else len(signals)
    )
    figure.tight_layout()

    for index, signal in enumerate(signals):
        x, y = util.signal_waveform(signal)

        axis = axes if overlay else axes[index]
        axis.plot(x, y, color=next(palette), label=signal.pop("legend_label", None))
        axis.set_title(kwargs.pop("title", None))
        axis.set_xlabel("Time (s)")
        if index == 0:
            axis.set_ylabel("Amplitude")
        axis.set_ylim(-1.0, 1.0)
        axis.legend()
    return figure
