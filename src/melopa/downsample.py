"""Downsampling algorithms for plotting."""

import numpy
from numpy.typing import NDArray


def decimate(array: NDArray, size: int) -> NDArray:
    """Downsample by selecting every nth point with rounding."""
    return numpy.linspace(0, len(array) - 1, size).round().astype(numpy.uint64)


def lttb(array: NDArray, size: int) -> NDArray:
    """Downsample using the largest triangle three buckets algorithm.

    Algorithm is described in section 4.2 of
    https://skemman.is/bitstream/1946/15343/3/SS_MSthesis.pdf and the reference
    implementation is at
    https://github.com/sveinn-steinarsson/flot-downsample/blob/master/jquery.flot.downsample.js.
    """
    length = len(array)
    indices = numpy.arange(length, dtype=numpy.uint64)
    # Skip if array is smaller than downsample limit.
    if size < 3 or size >= length:
        return indices

    data = (
        numpy.array([indices, array], dtype=array.dtype).T
        if len(array.shape) == 1
        else array
    )
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


def triangles_areas(left: NDArray, middles: NDArray, right: NDArray) -> NDArray:
    """Calculate areas of triangles from duples of vertex coordinates.

    Uses https://en.wikipedia.org/wiki/Area_of_a_triangle#Using_coordinates.
    """
    determinant = (left[0] - right[0]) * (middles[:, 1] - left[1]) - (
        left[0] - middles[:, 0]
    ) * (right[1] - left[1])
    return 0.5 * numpy.abs(determinant)
