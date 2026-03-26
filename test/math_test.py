"""Tests for plotting downsample algorithms."""

import numpy
from numpy import testing

from melopa import math


def test_lttb() -> None:
    """Test public."""
    y = numpy.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    actual = math.lttb(y, 4)
    testing.assert_array_equal(actual, [0, 1, 5, 9])
