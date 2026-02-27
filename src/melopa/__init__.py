"""Personal collection of notebooks."""

import marimo
from marimo import Html
from marimo._runtime.state import State

from melopa import source
from melopa.plot import Kind
from melopa.source import Source, SourceFile, SourceInput

__version__ = "0.1.0"


def audio_selector(default: str) -> tuple[State[Source], Html]:
    """Marimo input element to select an audio signal."""
    get_file, set_file = marimo.state(source.select(default))
    select = marimo.ui.dropdown(
        SourceFile.list(),
        allow_select_none=True,
        label="Select File",
        on_change=lambda name: set_file(SourceFile(name)),
        value=None,
    )
    synth = marimo.ui.dropdown(
        source.synths(),
        allow_select_none=True,
        label="Synth Generator",
        on_change=lambda name: set_file(source.select(name)),
        value=None,
    )
    upload = marimo.ui.file(
        filetypes=[".wav"],
        kind="button",
        label="Upload File",
        on_change=lambda input_: set_file(SourceInput(input_)),
    )
    return get_file, marimo.ui.batch(
        marimo.md("{select} {synth} {upload}"),
        {"select": select, "synth": synth, "upload": upload},
    )


def plot_selector() -> Html:
    """Marimo input element to select a signal plot."""
    backend = marimo.ui.dropdown(
        ["Bokeh", "Matplotlib", "Plotly"],
        allow_select_none=False,
        label="Backend",
        value="Bokeh",
    )
    kind = marimo.ui.dropdown(
        [option.capitalize() for option in Kind.options()],
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
