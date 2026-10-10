"""General utilities."""

import contextlib
import functools
import importlib
import inspect
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import marimo
from marimo._runtime.context.types import (  # ruff:ignore[import-private-name]
    ContextNotInitializedError,
)


def config_marimo() -> None:
    """Apply custom Marimo settings for WASM.

    Several Marimo settings from marimo.toml and pyproject.toml are not saved
    in WASM builds.
    """
    try:
        marimo_config = marimo._runtime.context.get_context().marimo_config  # ruff:ignore[private-member-access]  # ty:ignore[possibly-missing-submodule]
    except ContextNotInitializedError:
        return
    marimo_config["runtime"]["output_max_bytes"] = 1000000000


@functools.cache
def in_marimo() -> bool:
    """Check if running inside a Marimo notebook."""
    if "marimo" not in sys.modules:
        return False
    return importlib.import_module("marimo").running_in_notebook()


def popall(obj: Any, keys: str | Iterable[str], default: Any) -> Any:  # ruff: ignore[any-type]
    """Pop possible keys from object until successful."""
    if isinstance(keys, str):
        return obj.pop(keys, default)
    for key in keys:
        with contextlib.suppress(KeyError):
            return obj.pop(key)
    return default


def repo_path() -> Path:
    """Get repository path."""
    if "MELOPA_REPO" in os.environ:
        return Path(os.environ["MELOPA_REPO"])
    return Path(__file__).parents[2]


def varname(var: Any, default: str = "", depth: int = 2) -> str:  # ruff: ignore[any-type]
    """Trace variable name in calling scope."""
    frame = inspect.currentframe()
    if frame is None:
        return default

    for _ in range(depth):
        frame = frame.f_back
        if frame is None:
            return default
    vars_ = frame.f_locals.items()
    try:
        return next(name for name, value in vars_ if value is var)
    except StopIteration:
        return default
