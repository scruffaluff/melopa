"""Mathematical functions."""

import numpy
from numpy.typing import NDArray


def decibel(signal: NDArray) -> NDArray:
    """Convert signal to decibels.

    Avoids passing zeros to log10 by replacing them with the datatype epsilon.
    """
    epsilon = numpy.finfo(signal.dtype).eps
    amplitude = numpy.maximum(numpy.abs(signal), epsilon)
    return 20 * numpy.log10(amplitude)


def normalize(signal: NDArray) -> NDArray:
    """Scale signal to -1 and +1 range."""
    maximum = numpy.abs(signal).max()
    if maximum == 0:
        return signal
    return signal / maximum
