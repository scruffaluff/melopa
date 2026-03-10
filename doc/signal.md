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
marimo-version: 0.20.4
title: Signal
width: medium
---

<!-- prettier-ignore-start -->

# Signal

```python {.marimo name="setup"}
import math
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import bokeh
import marimo as mo
import numpy
from numpy.typing import NDArray

import melopa
```

A digital audio signal is a representation of sound as a time series sequence of
numbers denoted as $x[n]$. Digital audio signals can be translated into analog
signal with an associated sampling frequency $F$. We can view the comparison
between for analog and digital for the sine and impulse signals below.

```python {.marimo}
def _():
    freq = 2
    rate = 50
    time = numpy.linspace(0, 1, rate)
    sine = numpy.sin(2 * numpy.pi * 2 * rate * time)
    delta = numpy.zeros(len(time))
    delta[0] = 1
    return bokeh.layouts.row(
        [
            melopa.plot.signal(
                [
                    {"x": time, "y": sine, "legend_label": "Continuous"},
                    {
                        "x": time,
                        "y": sine,
                        "legend_label": "Discrete",
                        "method": "scatter",
                    },
                ],
                title="Sine",
            ),
            melopa.plot.signal(
                [
                    {"x": time, "y": delta, "legend_label": "Continuous"},
                    {
                        "x": time,
                        "y": delta,
                        "legend_label": "Discrete",
                        "method": "scatter",
                    },
                ],
                title="Impulse",
            ),
        ],
        sizing_mode="stretch_width",
    )


_()
```

## System

A digital system $T$ is a function that maps an input signal $x[n]$ to an output
signal $y[n]$ $y[n] = T\{x[n]\}$ as shown in the block diagram below.

```python {.marimo}
mo.mermaid("""
---
config:
    theme: neutral
---

stateDiagram
    direction LR
    x[n] --> y[n]: T{*}
""")
```

The class of linear and time invariant (LTI) systems are often used in audio
processing for their properties. Each LTI system $T$ in this class can be
rewritten as a convolution of its impulse response $h[n]$, i.e. its output to the
impulse signal, as follows.

$$ T(x[n]) = \sum_{k=-\infty}^{\infty} x[n] h[n-k] = x[n] * h[n] $$

## Fourier Transform

A transform maps signals from one domain to another domain. One of
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

The Fourier transform has the convolution property that $y[n] = x[n] * h[n]$ if and only if $Y[k] = X[k] H[k]$.
<!---->
## Z-Transform

The Fourier transform can be extended to the
[Z-transform](https://en.wikipedia.org/wiki/Z-transform) by allowing for any
complex number $z$ instead of only complex numbers on the unit circle $e^{iw}$.
The following equations describe the relationships between signal $x[n]$ and its
Z-transform $X(z)$.

$$
X(z) = \sum_{n=-\infty}^{\infty} x[n] z^{-n}
\newline
x[n] = \frac{1}{2\pi j} \oint X(z) z^{n-1} dz
$$

The Z-transform has the convolution property that $y[n] = x[n] * h[n]$ if and only if $Y(z) = X(z) H(z)$. As a result, an LTI system can be fully described by its transfer function $H(z) = \frac{Y(z)}{X(z)}$. If the LTI system is additionally casual, then the transfer function becomes a fraction of polynomials in the following order.

$$ H(z) = \frac{\sum_{n=0}^{N} b_k z^{-n}}{\sum_{m=0}^{N} a_k z^{-m}} $$

The zeros of the system are the roots of the numerator and the poles of the system are the roots of the denominator.

<!-- prettier-ignore-end -->

```python {.marimo}

```
