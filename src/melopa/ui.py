"""Custom Marimo editor component."""

import traceback
from collections.abc import Callable
from typing import cast

import marimo
from marimo import Html


def editor(code: str) -> Html:
    """Create a Marimo code editor."""
    get_code, set_code = marimo.state(code)
    editor_ = marimo.ui.code_editor(get_code(), debounce=True, on_change=exec)
    button = marimo.ui.button(
        on_click=lambda _: set_code(code), label=f"{marimo.icon('lucide:undo-2')}"
    )
    return Html("<div>{button}{editor}</div>").batch(
        button=button,
        editor=editor_,  # ty:ignore[invalid-argument-type]
    )


def run[T](func: Callable[[], T]) -> tuple[T, Html | None]:
    """Execute Python function and wrap its output in Marimo callouts."""
    styles = {"margin": "0rem", "margin-bottom": "0rem"}
    with marimo.capture_stderr() as stderr_, marimo.capture_stdout() as stdout_:
        try:
            result = func()
        except Exception:  # noqa: BLE001
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
