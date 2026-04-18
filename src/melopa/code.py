"""Source code for notebook examples."""

# ruff: noqa: D103

import numpy
from numpy.typing import NDArray


def resample(signal: NDArray, ratio: float) -> NDArray:
    size_in = len(signal)
    size_out = int(ratio * size_in + 0.5)
    size = min(size_in, size_out)
    bins = size // 2 + 1
    freq = numpy.fft.rfft(signal)[:bins]
    # Scale highest frequency if input length is even.
    if size % 2 == 0:
        freq[bins - 1] = (
            2 * freq[bins - 1] if size_out < size_in else 0.5 * freq[bins - 1]
        )
    return numpy.fft.irfft(size_out * freq / size_in, n=size_out)
