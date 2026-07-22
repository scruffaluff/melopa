"""General utilities."""

import os
from pathlib import Path

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


def repo_path() -> Path:
    """Get repository path."""
    if "MELOPA_REPO" in os.environ:
        return Path(os.environ["MELOPA_REPO"])
    return Path(__file__).parents[2]
