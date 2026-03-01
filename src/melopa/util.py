"""General utilities."""

import os
from pathlib import Path


def repo_path() -> Path:
    """Get repository path."""
    if "MELOPA_REPO" in os.environ:
        return Path(os.environ["MELOPA_REPO"])
    return Path(__file__).parents[2]
