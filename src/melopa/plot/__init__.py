"""Plotting interfaces."""

from enum import StrEnum
from typing import Any

from melopa.plot import bokeh, plotly


class Kind(StrEnum):
    """Plot types."""

    Frequency = "frequency"
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
    module = {"bokeh": bokeh, "plotly": plotly}[backend]

    match kind:
        case Kind.Frequency:
            return module.frequency(signals, **kwargs)
        case Kind.Waveform:
            return module.waveform(signals, **kwargs)
        case _:
            message = f"Invalid choice '{kind}' for PlotKind."
            raise ValueError(message)
