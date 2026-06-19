---
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.9",
  #   "matplotlib~=3.10",
  #   "numpy~=2.4",
  #   "scipy~=1.17",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
marimo-version: 0.23.10
title: Signal
width: medium
---

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

A digital audio signal is a representation of sound as a sequence of numbers
denoted as $x[n]$. Digital audio signals can be generated from continuous analog
signals by discretely recording them at a sampling frequency $F$. We can view
a comparison between analog and digital signals in the sine and impulse plots
below.

```python {.marimo}
def _():
    freq = 2
    time_c = numpy.linspace(-1, 1, 257)
    sine_c = numpy.sin(2 * numpy.pi * 2 * 257 * time_c)
    delta_c = numpy.zeros(len(time_c))
    delta_c[128] = 1

    time_d = numpy.linspace(-1, 1, 33)
    sine_d = numpy.sin(2 * numpy.pi * 2 * 33 * time_d)
    delta_d = numpy.zeros(len(time_d))
    delta_d[16] = 1

    return melopa.plot.gridplot([
        melopa.plot.signal(
            [
                {"x": time_c, "y": sine_c, "legend_label": "Continuous"},
                {
                    "x": time_d,
                    "y": sine_d,
                    "legend_label": "Discrete",
                    "method": "scatter",
                },
            ],
            title="Sine",
            y_range=(-1.1, 1.1),
        ),
        melopa.plot.signal(
            [
                {"x": time_c, "y": delta_c, "legend_label": "Continuous"},
                {
                    "x": time_d,
                    "y": delta_d,
                    "legend_label": "Discrete",
                    "method": "scatter",
                },
            ],
            title="Impulse",
            y_range=(-1.1, 1.1),
        ),
    ])


_()
```

## System

A digital system $T$ is a function that maps an input signal $x[n]$ to an output
signal $y[n]$. The system equation is conventionally written as $y[n] = T(x[n])$ and described in a block diagram as follows.

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

The class of linear and time invariant (LTI) systems are often used in digital audio
processing for their properties. Each LTI system $T$ in this class can be
written as a convolution of its impulse response $h[n]$, i.e. its output to
the impulse signal, as follows.

$$ T(x[n]) = \sum_{k=-\infty}^{\infty} x[n] h[n-k] = x[n] * h[n] $$

## Fourier Transform

A transform maps signals from one domain to another domain. One of the most
useful transforms is the
[discrete Fourier transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform),
which converts a discrete signal from the time domain to the frequency domain.

For a signal $x[n]$ of length $N$, the following equations describe the
relationships between $x[n]$ and its Fourier transform $X[k]$.

$$
X[k] = \sum_{n=0}^{N-1} x[n] e^{-iakn}
\newline
x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k] e^{iakn}
$$

To demonstrate the transform, we'll implement it in code as the `dft` function
below and plot it for sine waves.

```python {.marimo}
editor_ui = melopa.ui.editor(melopa.code.dft)
freq_ui = mo.ui.slider(0, 20, 1, label="Frequency", show_value=True, value=2)
mo.vstack([freq_ui, editor_ui])
```

```python {.marimo}
exec(editor_ui.value["editor"])
rate = 1_000
time = numpy.linspace(0, 1, rate)
waveform = numpy.sin(2 * numpy.pi * freq_ui.value * rate * time)
freq = numpy.fft.rfftfreq(len(time), 1 / rate)
spectrum, output = melopa.ui.run(lambda: dft(waveform))
output
```

```python {.marimo}
waveform_plot = melopa.plot.signal([{"x": time, "y": waveform}], title="Sine Signal")
spectrum_plot = melopa.plot.figure(
    title="Fourier Transform",
    x_axis_label="Frequency (Hz)",
    y_axis_label="Amplitude",
)
spectrum_plot.line(x=freq[:20], y=numpy.abs(spectrum)[:20])
melopa.plot.gridplot([waveform_plot, spectrum_plot])
```

The Fourier transform has the convolution property that $y[n] = x[n] * h[n]$ if
and only if $Y[k] = X[k] H[k]$.

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

The Z-transform has the convolution property that $y[n] = x[n] * h[n]$ if and
only if $Y(z) = X(z) H(z)$. As a result, an LTI system can be fully described by
its transfer function $H(z) = \frac{Y(z)}{X(z)}$. If the LTI system is
additionally casual, then the transfer function becomes a fraction of
polynomials in the following order.

$$ H(z) = \frac{\sum_{n=0}^{N} b_k z^{-n}}{\sum_{m=0}^{N} a_k z^{-m}} $$

The zeros of the system are the roots of the numerator and the poles of the
system are the roots of the denominator.

## Short Time Fourier Transform

The discrete Fourier transform decomposes the entire signal into frequency
components. If we want to analyze the change in frequency components over time,
then we can use the [discrete short-time Fourier
transform](https://en.wikipedia.org/wiki/Short-time_Fourier_transform#Discrete-time_STFT)
(STFT). The STFT divides the Fourier transform input into time segments by using
a window function $w[m]$. The Guassian windo

$$ w[n] = e^{0.5 (\frac{n - N/2}{\sigma N / 2})^2} $$

The STFT

$$
X[m, k] = \sum_{n=0}^{N-1} x[n] w[n-m] e^{-iakn}
\newline
x[n] = \frac{1}{w[n-m] * N} \sum_{k=0}^{N-1} X[m, k] e^{iakn}
$$

## Bilinear Transform

## Next

Follow the next notebook <a href="/melopa/filter.html">Filters</a>.

## References

<a id="1">[1]</a> Oppenheim, Alan V., and Roland W. Schafer.
[Discrete-Time Signal Processing](https://books.google.com/books/about/Discrete_time_Signal_Processing.html).
Third edition, Pearson New international edition, Pearson, 2014. Always
Learning.
