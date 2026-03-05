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
title: Filters
width: medium
---

<!-- prettier-ignore-start -->

# Filters

```python {.marimo name="setup"}
import sys

if sys.platform == "emscripten":
    import micropip

    await micropip.install("/melopa/data/melopa-0.1.0-py3-none-any.whl")
import marimo as mo
import numpy
from numpy.typing import NDArray
import scipy.signal
import melopa
from melopa.source import SourceFile
```

Audio filters remove aspects of a sound such as frequencies.

A discrete time system is defined as $y[n] = T\{x[n]\}$ as shown in the block
diagram below.

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

```python {.marimo}
cutoff = mo.ui.slider(
    steps=(440 * numpy.logspace(-4, 5, 100, base=2)).round(2),
    label="Cutoff",
    show_value=True,
)
order = mo.ui.slider(1, 10, 1, label="Order", show_value=True, value=4)
mo.hstack([cutoff, order], justify="start")
```

```python {.marimo}
rate = 40_000
b, a = scipy.signal.butter(order.value, cutoff.value, "lowpass", fs=rate)
freq, amp = scipy.signal.freqz(b, a, 1_000, fs=rate)
decibels = melopa.math.decibel(amp)
```

```python {.marimo}
melopa.plot.signal(
    [{"x": freq, "f": decibels}],
    backend="matplotlib",
    kind="spectrum",
    y_range=(-100, 0),
)
```

```python {.marimo}
sample, rate_ = SourceFile("templeofhades-scratch_sample.wav").read()
sos = scipy.signal.butter(10, 1000, "lowpass", fs=rate, output="sos")
processed = scipy.signal.sosfilt(sos, sample)
```

```python {.marimo hide_code="true"}
visual = melopa.plot.component()
mo.right(visual)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": rate_, "y": sample, "legend_label": "original"},
        {"rate": rate_, "y": processed, "legend_label": "processed"},
    ],
    **visual.value,
)
```

```python {.marimo}
mo.hstack(
    [
        mo.vstack([mo.md("### Original"), mo.audio(sample, rate)]),
        mo.vstack([mo.md("### Processed"), mo.audio(processed, rate)]),
    ],
    gap=2,
    justify="start",
)
```

<!-- prettier-ignore-end -->
