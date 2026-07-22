"""Custom Marimo UI components."""

import inspect
import traceback
from collections.abc import Callable, Iterable
from types import FunctionType
from typing import Any, cast

import marimo
import numpy
from marimo import Html
from numpy.typing import NDArray


def audio_list(audios: Iterable[dict[str, Any]]) -> Html:
    """Create a list of audio playback elements."""
    items = []
    for audio in audios:
        item = marimo.audio(audio["signal"], audio["rate"])
        if "name" in audio:
            items.append(marimo.vstack([marimo.md(f"### {audio['name']}"), item]))
        else:
            items.append(item)
    return marimo.hstack(items, gap=2, justify="start", wrap=True)


def difference_matrix(
    numerator: NDArray, denominator: NDArray, length: int = 0
) -> Html:
    """Create a Marimo matrix for difference equations."""
    size = length or max(len(numerator), len(denominator))
    matrix = numpy.array([
        numpy.concat([numerator, numpy.zeros(size - len(numerator))]),
        numpy.concat([denominator, numpy.zeros(size - len(denominator))]),
    ])
    return marimo.ui.matrix(matrix, debounce=True, row_labels=["b", "a"])


def editor(*codes: str | FunctionType) -> Html:
    """Create a Marimo code editor."""
    texts = []
    for code in codes:
        if isinstance(code, FunctionType):
            texts.append(inspect.getsource(code).strip())
        else:
            texts.append(code.strip())
    text = "\n\n".join(texts)
    editor_ = marimo.ui.code_editor(text, debounce=True)
    return Html("<div>{editor}</div>").batch(editor=editor_)


def run[T](func: Callable[[], T]) -> tuple[T, Html | None]:
    """Execute Python function and wrap its output in Marimo callouts."""
    styles = {"margin": "0rem", "margin-bottom": "0rem"}
    with marimo.capture_stderr() as stderr_, marimo.capture_stdout() as stdout_:
        try:
            result = func()
        except Exception:  # ruff:ignore[blind-except]
            return cast("T", None), marimo.callout(
                Html(f'<pre style="overflow: auto;">{traceback.format_exc()}</pre>'),
                kind="danger",
            ).style(styles)

    outputs = []
    stderr = stderr_.getvalue()
    stdout = stdout_.getvalue()
    if stderr:
        outputs.append(marimo.callout(stderr, kind="danger").style(styles))
    if stdout:
        outputs.append(marimo.callout(stdout, kind="neutral").style(styles))
    return result, marimo.vstack(outputs) if outputs else None
