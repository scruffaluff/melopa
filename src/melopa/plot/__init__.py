"""Plotting interfaces."""

from enum import StrEnum
from typing import Any, NamedTuple, cast

import marimo
from marimo import Html

from melopa.plot import bokeh, matplotlib
from melopa.plot.bokeh import figure, gridplot

__all__ = ["bokeh", "figure", "gridplot", "matplotlib"]
__version__ = "0.1.0"


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


class Kind(Options):
    """Plot types."""

    Phase = "phase"
    Spectrogram = "spectrogram"
    Spectrum = "spectrum"
    Waveform = "waveform"


class Config(NamedTuple):
    """Plot settings."""

    backend: Backend = Backend.Bokeh
    kind: Kind = Kind.Waveform
    overlay: bool = True


def ui(
    backend: str = "Bokeh", kind: str = "Waveform", overlay: bool = True
) -> marimo.ui.batch:
    """Marimo element to select a signal plot settings."""
    backend_ = marimo.ui.dropdown(
        Backend.options(),
        allow_select_none=False,
        label="Backend",
        value=backend,
    )
    kind_ = marimo.ui.dropdown(
        Kind.options(),
        allow_select_none=False,
        label="Type",
        value=kind,
    )
    overlay_ = marimo.ui.switch(label="Overlay", value=overlay)
    return Html(
        """
<div style="display: flex; flex-direction: row; gap: 0.5rem;" >
    {backend}{kind}{overlay}
</div>
        """.strip()
    ).batch(
        backend=backend_,
        kind=kind_,
        overlay=overlay_,
    )


def signal(
    signals: list[dict],
    backend: str = "bokeh",
    kind: str = "waveform",
    normalize: bool = False,
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio signals.

    Raises:
        ValueError: If kind value is invalid.
    """
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]

    match kind.lower():
        case "phase":
            plot = module.phase(signals, overlay, **kwargs)
        case "spectrogram":
            plot = module.spectrogram(signals, normalize, **kwargs)
        case "spectrum":
            plot = module.spectrum(signals, normalize, overlay, **kwargs)
        case "waveform":
            plot = module.waveform(signals, normalize, overlay, **kwargs)
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)

    return cast("Html", plot)
