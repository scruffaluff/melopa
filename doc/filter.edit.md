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
marimo-version: 0.21.0
title: Filter
width: medium
---

<!-- prettier-ignore-start -->

# Filter

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import marimo as mo
import numpy
from numpy.typing import NDArray
import scipy.signal

import melopa
from melopa.source import SourceFile
```

Audio filters are digital systems that modify features of sound. One common
example is a low-pass filter which removes a band of lower frequencies. A very
basic low-pass filter is a moving average system which is implemented below.

```python {.marimo}
maf_editor_ui = melopa.ui.editor("""
def moving_average(signal: NDArray, length: int) -> NDArray:
    filter = numpy.ones(length) / length
    return numpy.convolve(filter, signal, mode="same")
""")
maf_signal_state, maf_signal_ui = melopa.source.ui("claretcanelon-baby_parrot.wav")
maf_length_ui = mo.ui.slider(
    1, 100, 1, debounce=True, label="Length", show_value=True, value=8
)
maf_plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Code": maf_editor_ui,
        "Signal": maf_signal_ui,
        "Parameter": maf_length_ui,
        "Plot": maf_plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
maf_signal_source = maf_signal_state()
maf_signal, maf_rate = maf_signal_source.read()
exec(maf_editor_ui.value["editor"])
maf_processed, maf_output = melopa.ui.run(
    lambda: moving_average(maf_signal, maf_length_ui.value)
)
maf_output
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": maf_rate, "y": maf_signal, "legend_label": "original"},
        {"rate": maf_rate, "y": maf_processed, "legend_label": "filtered"},
    ],
    title=maf_signal_source.name(),
    **maf_plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": maf_signal, "rate": maf_rate, "name": "Original"},
    {"signal": maf_processed, "rate": maf_rate, "name": "Processed"},
])
```

The commonest class of audio filters are linear and time invariant (LTI)
filters. Linear filter, while time invariant filters are.

## Difference Equation

It is often useful to analyze the class of LTI filters that are also casual,
i.e. This filter is class is useful since their Z-transform can be expressed as
a ratio of polynomials.

$$ H(z) = \frac{\sum_{n=0}^{N} b_n z^{-n}}{\sum_{m=0}^{M} a_m z^{-m}} $$

For analytical convenience, these notebook assume that `a_0 = 1`. When
Z-transform is a ratio of polynomials, its system can be expressed by the
following difference equation.

$$ y[k] = -\sum_{m=1}^{M} a_m y[k-m] + \sum_{n=0}^{N} b_n x[k-n] $$

```python {.marimo}
de_rate = 48_000
de_b, de_a = scipy.signal.butter(4, 1_000, "lowpass", fs=de_rate)
de_matrix = melopa.ui.difference_matrix(de_b, de_a)
de_matrix
```

```python {.marimo}
de_freq, de_amp = scipy.signal.freqz(
    de_matrix.value[0], de_matrix.value[1], 1000, fs=de_rate
)
de_decibels = melopa.math.decibel(de_amp)
melopa.plot.signal(
    [{"x": de_freq, "f": de_decibels}],
    backend="matplotlib",
    kind="spectrum",
    y_range=(-50, 0),
)
```

## Finite Response

An finite impulse response (FIR) filter is an LTI filter whose output does not
depend on previous outputs. Thus, its Z-transform has no denominator polynomial
with form $H(z) = \sum_{n=0}^{N} b_n z^{-n}$ and its difference equation has
form $y[k] = \sum_{n=0}^{N} b_n x[k-n]$.

## Infinite Response

An infinite impulse response (IIR) filter, also called a recursive filter, is an
LTI filter whose output does depend on previous outputs. Thus, its Z-transform
has the full form
$H(z) = \frac{\sum_{n=0}^{N} b_n z^{-n}}{\sum_{m=0}^{M} a_m z^{-m}}$ and its
difference equation has form
$y[k] = -\sum_{m=1}^{M} a_m y[k-m] + \sum_{n=0}^{N} b_n x[k-n]$.

## Butterworth

- Has no gain ripple.

The following interface provides controls for a Butterworth low-pass filter,
which attenuates high frequencies from a signal.

```python {.marimo}
bw_cutoff_ui = mo.ui.slider(
    steps=(440 * numpy.logspace(-4, 5, 100, base=2)).round(2),
    label="Cutoff",
    show_value=True,
)
bw_order_ui = mo.ui.slider(1, 10, 1, label="Order", show_value=True, value=4)
mo.hstack([bw_cutoff_ui, bw_order_ui], justify="start")
```

```python {.marimo}
bw_rate = 40_000
bw_b, bw_a = scipy.signal.butter(
    bw_order_ui.value, bw_cutoff_ui.value, "lowpass", fs=rate
)
bw_freq, bw_amp = scipy.signal.freqz(bw_b, bw_a, 1_000, fs=bw_rate)
bw_decibels = melopa.math.decibel(bw_amp)
```

```python {.marimo}
melopa.plot.signal(
    [{"x": bw_freq, "f": bw_decibels}],
    backend="matplotlib",
    kind="spectrum",
    y_range=(-100, 0),
)
```

We can apply the low-pass filter to any sound and visualized its affects below.

```python {.marimo}
signal, rate = SourceFile("talitha5-cafe_ambience.wav").read()
sos = scipy.signal.butter(10, 1000, "lowpass", fs=rate, output="sos")
processed = scipy.signal.sosfilt(sos, signal)
```

```python {.marimo}
plot_ui = melopa.plot.ui()
mo.right(plot_ui)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": rate, "y": signal, "legend_label": "original"},
        {"rate": rate, "y": processed, "legend_label": "processed"},
    ],
    **plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": signal, "rate": rate, "name": "Original"},
    {"signal": processed, "rate": rate, "name": "Processed"},
])
```

## Biquad

A biquad filter is a second order recursive filter containing two poles and two
zeros. Thus, its transfer function is a ratio quadratic functions.

```python {.marimo unparsable="true"}
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

<!-- prettier-ignore-end -->
