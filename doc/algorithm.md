---
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "matplotlib~=3.8",
  #   "numpy~=2.2",
  #   "scipy~=1.14",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
marimo-version: 0.23.7
title: Algorithm
width: medium
---

# Algorithm

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import marimo as mo
import numpy
import scipy
from numpy.typing import NDArray

import melopa
```

## Resample

Resampling is the process of changing the sample rate of an existing signal. We
can resample in the time domain by periodically removing or inserting
interpolated samples and then applying lowpass filters to prevent aliasing.
However, it more trivial to resample in the frequency domain. By removing the
upper frequencies of the Fourier transform we decrease the sample rate.
Similarly by zero padding after the upper frequencies, we increase the sampling
rate. Playing back the resampled signal at the original sample rate will change
the speed of the signal as shown below.

```python {.marimo}
editor_ui = melopa.ui.editor(melopa.code.resample)
signal_state, signal_ui = melopa.source.ui("templeofhades-scratch_sample.wav")
ratio_ui = mo.ui.slider(
    debounce=True,
    label="Ratio",
    show_value=True,
    steps=numpy.round(numpy.logspace(-1, 1, 33), 2),
    value=1,
)
plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Code": editor_ui,
        "Signal": signal_ui,
        "Parameter": mo.hstack([ratio_ui], gap=2, justify="start", wrap=True),
        "Plot": plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
signal_source = signal_state()
signal, rate = signal_source.read()
exec(editor_ui.value["editor"])
processed, output = melopa.ui.run(lambda: resample(signal, ratio_ui.value))
output
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": rate, "y": signal, "legend_label": "original"},
        {"rate": rate, "y": processed, "legend_label": "processed"},
    ],
    title=signal_source.name(),
    **plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": signal, "rate": rate, "name": "Original"},
    {"signal": processed, "rate": rate, "name": "Processed"},
])
```

## References
