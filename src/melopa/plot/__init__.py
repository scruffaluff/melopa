"""Plotting interfaces."""

from enum import StrEnum
from typing import Any, NamedTuple, cast

import marimo
from marimo import Html

from melopa.plot import bokeh, matplotlib, plotly


class Options(StrEnum):
    """Interface for selection options."""

    @classmethod
    def options(cls) -> list[str]:
        """List all options."""
        return [kind.value for kind in cls]


class Backend(Options):
    """Plot backends."""

    Bokeh = "Bokeh"
    Matplotlib = "Matplotlib"
    Plotly = "Plotly"


class Kind(Options):
    """Plot types."""

    Spectrogram = "Spectrogram"
    Spectrum = "Spectrum"
    Waveform = "Waveform"


class Config(NamedTuple):
    """Plot settings."""

    backend: Backend = Backend.Bokeh
    kind: Kind = Kind.Waveform
    overlay: bool = True


def component() -> marimo.ui.batch:
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
    config: marimo.ui.batch | None = None,
    **kwargs: Any,
) -> Html:
    """Plot audio signals."""
    if config is None:
        config_ = Config()
    elif isinstance(config, Config):
        config_ = config
    else:
        config_ = Config(**cast("dict", config.value))
    module = {"Bokeh": bokeh, "Matplotlib": matplotlib, "Plotly": plotly}[
        config_.backend
    ]

    match config_.kind:
        case Kind.Spectrogram:
            return module.spectrogram(signals, config_.overlay, **kwargs)
        case Kind.Spectrum:
            return module.spectrum(signals, config_.overlay, **kwargs)
        case Kind.Waveform:
            return module.waveform(signals, config_.overlay, **kwargs)
        case _:
            message = f"Invalid choice '{config.kind_}' for PlotKind."
            raise ValueError(message)
