"""Mathematical functions."""

import numpy
from numpy.typing import NDArray


def decibel(signal: NDArray) -> NDArray:
    """Convert signal to decibels."""
    return 20 * numpy.log10(numpy.abs(signal))


def lttb(array: NDArray, size: int) -> NDArray:
    """Downsample using the largest triangle three buckets algorithm."""
    length = len(array)
    indices = numpy.arange(length, dtype=numpy.uint64)
    if size < 3 or size >= length:
        return indices

    data = numpy.array([indices, array], dtype=array.dtype).T
    bins = [data[:1], *numpy.array_split(data[1:-1], size - 2), data[-2:]]
    output = numpy.zeros((size, 2), dtype=numpy.uint64)
    output[0] = data[0]
    output[-1] = data[-1]

    for index, bin_ in enumerate(bins[1:-1]):
        left = output[index]
        right = numpy.mean(bins[index + 2], axis=0)
        areas = triangles_areas(left, bin_, right)
        numpy.argmax(areas)
        output[index + 1] = bin_[numpy.argmax(areas)]

    return output[:, 0]


def normalize(signal: NDArray) -> NDArray:
    """Scale signal -1 and +1 range."""
    return signal / numpy.abs(signal).max()


def triangles_areas(left: NDArray, middles: NDArray, right: NDArray) -> NDArray:
    """Calculate areas of triangles from duples of vertex coordinates.

    Uses https://en.wikipedia.org/wiki/Area_of_a_triangle#Using_coordinates.
    """
    determinant = (
        left[0] * (middles[:, 1] - right[1])
        + middles[:, 0] * (right[1] - left[1])
        + right[0] * (left[1] - middles[:, 1])
    )
    return 0.5 * numpy.abs(determinant)
