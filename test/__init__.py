"""template-python testing package."""

import tomllib
from pathlib import Path

import melopa

REPO_PATH = Path(__file__).parents[1]


def test_version() -> None:
    """Check that all the version tags are in sync."""
    path = REPO_PATH / "pyproject.toml"
    with path.open("rb") as file:
        expected = tomllib.load(file)["project"]["version"]

    actual = melopa.__version__
    assert actual == expected
