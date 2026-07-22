"""Tests for notebook examples."""

import numpy
from numpy import testing

from melopa import code


def test_resample() -> None:
    """Resampling interpolates new values between given values."""
    y = numpy.array([0, 1, 0, 1])
    actual = code.resample(y, 2)
    testing.assert_array_equal(actual, [0, 0.5, 1, 0.5, 0, 0.5, 1, 0.5])
