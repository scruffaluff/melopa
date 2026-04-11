---
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "librosa~=0.11.0",
  #   "matplotlib~=3.8",
  #   "numpy~=2.2",
  #   "polars~=1.36",
  #   "scipy~=1.14",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
title: Scratchpad
marimo-version: 0.23.0
width: medium
---

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import bokeh
import marimo as mo
import numpy
import scipy

import melopa
```

```python {.marimo}
source = melopa.source.select("gowers-amen_break.wav")
signal, rate = source.read()
filter = scipy.signal.butter(4, 600, "highpass", fs=rate, output="sos")
processed = scipy.signal.sosfilt(filter, signal)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": rate, "y": signal, "legend_label": "original"},
        {"rate": rate, "y": processed, "legend_label": "processed"},
    ],
    backend="bokeh",
    kind="waveform",
    overlay=True,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": signal, "rate": rate, "name": "Original"},
    {"signal": processed, "rate": rate, "name": "Processed"},
])
```
