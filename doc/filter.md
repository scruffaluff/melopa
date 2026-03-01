---
title: Filters
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
```

Audio filters remove aspects of a sound such as frequencies.

A discrete time system is defined as $y[n] = T\{x[n]\}$ and is represented by
the flow chart below.

```python {.marimo}
mo.mermaid("""
stateDiagram
    direction LR
    x[n] --> y[n]: T{*}
""")
```

```python {.marimo}
cutoff = mo.ui.slider(steps=(440 * numpy.logspace(-4, 5, 100, base=2)).round(2), label="Cutoff", show_value=True)
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
melopa.plot.signal([{"x": freq, "f": decibels}], backend="matplotlib", kind="spectrum", y_range=(-100, 0))
```

```python {.marimo}

```
