"""Plotting interfaces."""

import functools
from enum import StrEnum
from typing import Any, NamedTuple, cast

import marimo
from marimo import Html

from melopa.plot import bokeh, matplotlib
from melopa.plot.bokeh import figure, gridplot
from melopa.plot.util import Signal

__all__ = ["bokeh", "figure", "gridplot", "matplotlib"]


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

    Frequency = "frequency"
    Grid = "grid"
    Line = "line"
    Phase = "phase"
    Spectrogram = "spectrogram"
    Waveform = "waveform"


class Config(NamedTuple):
    """Plot settings."""

    backend: Backend = Backend.Bokeh
    kind: Kind = Kind.Waveform
    overlay: bool = True


def signal(
    *signals: Signal,
    backend: str = "bokeh",
    depth: int = 4,
    kind: str = "waveform",
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio signals.

    Raises:
        ValueError: If kind value is invalid.
    """
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    match kind.lower():
        case "frequency":
            plot = module.frequency(
                *signals,
                depth=depth,
                overlay=overlay,
                **kwargs,
            )
        case "grid":
            plot = module.grid(*signals, depth=depth + 1, overlay=overlay, **kwargs)
        case "line":
            plot = module.line(*signals, depth=depth, overlay=overlay, **kwargs)
        case "phase":
            plot = module.phase(*signals, depth=depth, overlay=overlay, **kwargs)
        case "spectrogram":
            plot = module.spectrogram(*signals, depth=depth, **kwargs)
        case "waveform":
            plot = module.waveform(
                *signals,
                depth=depth,
                overlay=overlay,
                **kwargs,
            )
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)

    return cast("Html", plot)


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


frequency = functools.partial(signal, kind=Kind.Frequency)
grid = functools.partial(signal, kind=Kind.Grid)
line = functools.partial(signal, kind=Kind.Line)
phase = functools.partial(signal, kind=Kind.Phase)
spectrogram = functools.partial(signal, kind=Kind.Spectrogram)
waveform = functools.partial(signal, kind=Kind.Waveform)
