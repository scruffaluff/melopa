"""Plotting interfaces."""

from enum import StrEnum
from typing import Any

from melopa.plot import bokeh, matplotlib, plotly


class Kind(StrEnum):
    """Plot types."""

    Spectrogram = "spectrogram"
    Spectrum = "spectrum"
    Waveform = "waveform"

    @classmethod
    def options(cls) -> list[str]:
        """List all options."""
        return [kind.value for kind in cls]


def signal(
    signals: list[dict],
    backend: str = "bokeh",
    kind: Kind = Kind.Waveform,
    **kwargs: Any,
) -> Any:  # noqa: ANN401
    """Plot audio signals."""
    module = {"bokeh": bokeh, "matplotlib": matplotlib, "plotly": plotly}[backend]

    match kind:
        case Kind.Spectrogram:
            return module.spectrogram(signals, **kwargs)
        case Kind.Spectrum:
            return module.spectrum(signals, **kwargs)
        case Kind.Waveform:
            return module.waveform(signals, **kwargs)
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)
