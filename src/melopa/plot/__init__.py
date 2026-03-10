"""Plotting interfaces."""

from enum import StrEnum
from typing import Any, NamedTuple

import marimo
from marimo import Html

from melopa.plot import bokeh, matplotlib, plotly
from melopa.plot.bokeh import figure

__all__ = ["bokeh", "figure", "matplotlib", "plotly"]


class Options(StrEnum):
    """Interface for selection options."""

    @classmethod
    def options(cls) -> list[str]:
        """List all options."""
        return [kind.value.capitalize() for kind in cls]


class Backend(Options):
    """Plot backends."""

    Bokeh = "bokeh"
    Matplotlib = "matplotlib"
    Plotly = "plotly"


class Kind(Options):
    """Plot types."""

    Spectrogram = "spectrogram"
    Spectrum = "spectrum"
    Waveform = "waveform"


class Config(NamedTuple):
    """Plot settings."""

    backend: Backend = Backend.Bokeh
    kind: Kind = Kind.Waveform
    overlay: bool = True


def ui() -> marimo.ui.batch:
    """Marimo element to select a signal plot settings."""
    backend = marimo.ui.dropdown(
        Backend.options(),
        allow_select_none=False,
        label="Backend",
        value="Bokeh",
    )
    kind = marimo.ui.dropdown(
        Kind.options(),
        allow_select_none=False,
        label="Type",
        value="Waveform",
    )
    overlay = marimo.ui.switch(label="Overlay", value=True)
    return Html("<div>{backend}{kind}{overlay}</div>").batch(
        backend=backend,  # ty:ignore[invalid-argument-type]
        kind=kind,  # ty:ignore[invalid-argument-type]
        overlay=overlay,  # ty:ignore[invalid-argument-type]
    )


def signal(
    signals: list[dict],
    backend: str = "bokeh",
    kind: str = "waveform",
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio signals."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib, "plotly": plotly}[
        backend.lower()
    ]

    match kind.lower():
        case "spectrogram":
            return module.spectrogram(signals, overlay, **kwargs)
        case "spectrum":
            return module.spectrum(signals, overlay, **kwargs)
        case "waveform":
            return module.waveform(signals, overlay, **kwargs)
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)
