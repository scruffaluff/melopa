---
title: Fourier
marimo-version: 0.20.2
width: medium
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "matplotlib~=3.8",
  #   "numpy~=2.2",
  #   "plotly~=6.5",
  #   "scipy~=1.14",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
---

# Fourier

```python {.marimo name="setup"}
import sys

if sys.platform == "emscripten":
    import micropip

    await micropip.install("/melopa/data/melopa-0.1.0-py3-none-any.whl")
from bokeh import plotting
import marimo as mo
import math
import numpy
from numpy.typing import NDArray
import scipy.signal
import melopa
```

The discrete Fourier transform converts a discrete time domain signal to its
frequency domain representation. For a signal $x[n]$ of length $N$ and sampling
period $T$, the transform is defined below with fundamental angular frequency
$w = \frac{2\pi}{NT}$.

<!-- prettier-ignore -->
$$ X[k] = \sum_{n=0}^{N-1} x[n] e^{-iwkn} $$

The sampling period $T$ of a signal is related to its sampling frequency by
$F = \frac{1}{T}$. The inverse transform is defined below.

<!-- prettier-ignore -->
$$ x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k] e^{iwkn} $$

To demonstrate this, we'll analyze a discrete sine wave of frequency 2Hz sampled
at 50Hz as plotted below.

```python {.marimo}
freq = 2
rate = 50
t = numpy.linspace(0, 1, rate)
x = numpy.sin(2 * numpy.pi * freq * rate * t)
```

```python {.marimo}
def dft(x: NDArray) -> NDArray:
    """Calculate the discrete Fourier transform of an array."""
    N = len(x)
    w = 2 * numpy.pi / N
    size = math.floor(N / 2 + 1)
    X = numpy.zeros(size, dtype=numpy.complex128)
    for k in range(size):
        X[k] = numpy.sum(x * numpy.exp(-1j * w * k * numpy.arange(N)))
    return X
```

```python {.marimo}
melopa.plot.signal([{"x": t, "y": x}])
```

```python {.marimo}
f = numpy.fft.rfftfreq(len(t), 1 / rate)
X = numpy.fft.rfft(x)
X = dft(x)

plot = plotting.figure(
    output_backend="webgl",
    sizing_mode="stretch_width",
    x_axis_label="Frequency (Hz)",
    y_axis_label="Amplitude",
)
plot.line(
    x=f,
    y=numpy.abs(X),
    line_width=2,
)
plot
```
