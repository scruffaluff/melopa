---
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
marimo-version: 0.20.2
title: Transforms
width: medium
---

<!-- prettier-ignore-start -->

# Transforms

```python {.marimo name="setup"}
import sys

if sys.platform == "emscripten":
    import micropip

    await micropip.install("/melopa/data/melopa-0.1.0-py3-none-any.whl")
import bokeh
import marimo as mo
import math
import numpy
from numpy.typing import NDArray
import melopa
```

Mathematical transforms map signals from one domain to another domain. One of
the most useful transforms is the [discrete Fourier
transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform), which
converts a discrete signals from the time domain to the frequency domain.

Let's consider a signal $x[n]$ of length $N$ and sampling period $T$. The signal
has sampling frequency $\frac{1}{T}$ and angular frequency $w =
\frac{2\pi}{NT}$. The following equations describe the relationships between
signal $x[n]$ and its Fourier transform $X[k]$.

$$
X[k] = \sum_{n=0}^{N-1} x[n] e^{-iwkn}
\newline
x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k] e^{iwkn}
$$

To demonstrate the transform, we'll implement it in code as the `dtf` function
below and plot it for sine waves.

```python {.marimo}
code_comp = mo.ui.code_editor(
    """
def dft(x: NDArray) -> NDArray:
    N = len(x)
    w = 2 * numpy.pi / N
    size = math.floor(N / 2 + 1)
    X = numpy.zeros(size, dtype=numpy.complex128)
    for k in range(size):
        X[k] = numpy.sum(x * numpy.exp(-1j * w * k * numpy.arange(N)))
    return X
    """.strip()
)
code_comp
```

```python {.marimo}
freq_comp = mo.ui.slider(0, 100, 1, label="Frequency", show_value=True, value=2)
rate_comp = mo.ui.slider(0, 100, 1, label="Rate", show_value=True, value=50)
mo.hstack([freq_comp, rate_comp], gap=2, justify="start")
```

```python {.marimo}
exec(code_comp.value)

time = numpy.linspace(0, 1, rate_comp.value)
waveform = numpy.sin(2 * numpy.pi * freq_comp.value * rate_comp.value * time)
freq = numpy.fft.rfftfreq(len(time), 1 / rate_comp.value)
spectrum = dft(waveform)
```

```python {.marimo}
waveform_plot = melopa.plot.signal([{"x": time, "y": waveform}], title="Sine Signal")
spectrum_plot = melopa.plot.figure(
    title="Fourier Transform",
    x_axis_label="Frequency (Hz)",
    y_axis_label="Amplitude",
)
spectrum_plot.line(x=freq, y=numpy.abs(spectrum))
bokeh.layouts.row([waveform_plot, spectrum_plot], sizing_mode="stretch_width")
```

The Fourier transform can be extended to the
[Z-transform](https://en.wikipedia.org/wiki/Z-transform). The following
equations describe the relationships between signal $x[n]$ and its Z-transform
$X(z)$.

$$
X(z) = \sum_{n=-\infty}^{\infty} x[n] z^{-n}
\newline
x[n] = \frac{1}{2\pi j} \oint X(z) z^{n-1} dz
$$

The discrete Fourier transform is the restriction of the z-transform to the unit
circle, i.e. where $z = e^{jw}$.

The closed form of the z-transform is blah. The zeros are the roots of the
numerator and the poles are the roots of the denominator.

<!-- prettier-ignore-end -->
