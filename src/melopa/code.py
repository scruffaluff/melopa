"""Source code for notebook examples."""

# ruff: noqa: D103, N806, PLR0913

import numpy
from numpy.typing import NDArray

import melopa


def compress(
    signal: NDArray,
    attack: int = 0,
    knee: float = 0.0,
    ratio: float = 4.0,
    release: int = 0,
    threshold: float = 0.8,
) -> NDArray:
    volume = melopa.math.decibel(signal)
    reduction = gain_compute(volume, knee, ratio, threshold)
    level = level_detect(reduction, attack, release)
    return numpy.power(10, level / 20) * signal


def dft(x: NDArray) -> NDArray:
    N = len(x)
    a = 2 * numpy.pi / N
    size = N // 2 + 1
    X = numpy.zeros(size, dtype=numpy.complex128)
    for k in range(size):
        X[k] = numpy.sum(x * numpy.exp(-1j * a * k * numpy.arange(N)))
    return X


def gain_compute(
    signal: NDArray,
    knee: float = 0.0,
    ratio: float = 4.0,
    threshold: float = 0.8,
) -> NDArray:
    length = len(signal)
    gain = numpy.copy(signal)
    for index in range(length):
        value = signal[index] - threshold
        if value > knee / 2:
            gain[index] = threshold + value / ratio
        elif value > -knee / 2:
            smoothing = (value + knee / 2) ** 2 / (2 * knee * ratio)
            gain[index] += (1 - ratio) * smoothing
    return gain - signal


def level_detect(signal: NDArray, attack: int, release: int) -> NDArray:
    attack_ = 0 if attack == 0 else numpy.exp(-1 / attack)
    release_ = 0 if release == 0 else numpy.exp(-1 / release)
    length = len(signal)
    level = numpy.zeros(length)
    level[0] = signal[0]
    for index in range(1, length):
        if signal[index] > level[index - 1]:
            level[index] = attack_ * level[index - 1] + (1 - attack_) * signal[index]
        else:
            level[index] = release_ * level[index - 1] + (1 - release_) * signal[index]
    return level


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
