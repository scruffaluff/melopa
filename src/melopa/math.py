"""Mathematical functions."""

import numpy
from numpy.typing import NDArray


def loudness(signal: NDArray) -> NDArray:
    """Convert signal to decibels."""
    return 20 * numpy.log10(numpy.abs(signal))


def normalize(signal: NDArray) -> NDArray:
    """Scale signal -1 and +1 range."""
    return signal / numpy.abs(signal).max()
