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

```python {.marimo}
rate = 40_000
b, a = scipy.signal.butter(4, 480, "lowpass", fs=rate)
freq, amp = scipy.signal.freqz(b, a, 1_000, fs=rate)
decibels = melopa.math.decibel(amp)
```

```python {.marimo}
melopa.plot.signal([{"x": freq, "f": decibels}], kind="spectrum")
```

```python {.marimo}

```
