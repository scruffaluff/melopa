"""Signal processing modulation functions."""

import numpy
from numpy.typing import NDArray


def adsr(
    signal: NDArray,
    attack: float = 0.1,
    decay: float = 0.3,
    sustain: float = 0.5,
    release: float = 0.1,
) -> NDArray:
    """Apply an attack, decay, sustain, and release envelope to a signal."""
    length = len(signal)
    lengths = numpy.array([
        round(attack * length),
        round(decay * length),
        0,
        round(release * length),
    ])
    lengths[2] = length - numpy.sum(lengths)

    envelope = numpy.concatenate([
        numpy.linspace(0, 1, lengths[0]),
        numpy.linspace(1, sustain, lengths[1]),
        sustain * numpy.ones(lengths[2]),
        numpy.linspace(sustain, 0, lengths[3]),
    ])
    return envelope * signal
