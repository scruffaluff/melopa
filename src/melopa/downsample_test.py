"""Tests for plotting downsample algorithms."""

import numpy
from numpy import testing

from melopa import downsample


def test_decimate_evenly_selects_array_elements() -> None:
    """Decimation selects every nth element with index rounding."""
    y = numpy.arange(16)
    actual = downsample.decimate(y, 5)
    testing.assert_array_equal(actual, [0, 4, 8, 11, 15])


def test_lttb_select_first_index() -> None:
    """LTTB selects first index for each bin on a straight line."""
    y = numpy.arange(10)
    actual = downsample.lttb(y, 4)
    testing.assert_array_equal(actual, [0, 1, 5, 9])


def test_lttb_select_single_peak() -> None:
    """LTTB selects single peak."""
    x = numpy.arange(5)
    y = numpy.array([0, 0, 1, 0, 0])
    array = numpy.array([x, y], dtype=y.dtype).T
    actual = downsample.lttb(array, 3)
    testing.assert_array_equal(actual, [0, 2, 4])
