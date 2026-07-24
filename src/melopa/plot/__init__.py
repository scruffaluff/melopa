"""Plotting interfaces."""

from enum import StrEnum
from typing import Any, NamedTuple, cast

import marimo
from marimo import Html
from numpy.typing import ArrayLike

from melopa.plot import bokeh, matplotlib
from melopa.plot.bokeh import figure, gridplot
from melopa.plot.util import Signal

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


def line(
    *signals: ArrayLike,
    backend: str = "bokeh",
    overlay: bool = True,
    x: ArrayLike | None = None,
    **kwargs: Any,
) -> Html:
    """Plot audio waveform."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    plot = module.line(*signals, overlay=overlay, x=x, **kwargs)
    return cast("Html", plot)


def phase(
    *signals: Signal,
    backend: str = "bokeh",
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio phase."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    plot = module.phase(*signals, overlay=overlay, **kwargs)
    return cast("Html", plot)


def signal(
    *signals: Signal,
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
    match kind.lower():
        case "phase":
            plot = phase(*signals, backend=backend, overlay=overlay, **kwargs)
        case "spectrogram":
            plot = spectrogram(*signals, backend=backend, normalize=normalize, **kwargs)
        case "spectrum":
            plot = spectrum(
                *signals,
                backend=backend,
                normalize=normalize,
                overlay=overlay,
                **kwargs,
            )
        case "waveform":
            plot = waveform(
                *signals,
                backend=backend,
                normalize=normalize,
                overlay=overlay,
                **kwargs,
            )
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)

    return plot


def spectrogram(
    *signals: Signal,
    backend: str = "bokeh",
    normalize: bool = False,
    **kwargs: Any,
) -> Html:
    """Plot audio spectrogram."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    plot = module.spectrogram(*signals, normalize=normalize, **kwargs)
    return cast("Html", plot)


def spectrum(
    *signals: Signal,
    backend: str = "bokeh",
    normalize: bool = False,
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio spectrum."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    plot = module.spectrum(*signals, normalize=normalize, overlay=overlay, **kwargs)
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


def waveform(
    *signals: Signal,
    backend: str = "bokeh",
    normalize: bool = False,
    overlay: bool = True,
    **kwargs: Any,
) -> Html:
    """Plot audio waveform."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib}[backend.lower()]
    plot = module.waveform(*signals, normalize=normalize, overlay=overlay, **kwargs)
    return cast("Html", plot)
