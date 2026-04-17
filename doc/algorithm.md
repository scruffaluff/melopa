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
marimo-version: 0.23.1
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

Resampling changes the sampling frequency of an audio signal. One method to
resample a signal is by trimming or zero-padding its Fourier transform. Playing
a resampled signal with the original sampling frequency changes the speed of the
signal.

```python {.marimo}
code = f"""
def resample(signal: NDArray, ratio: float) -> NDArray:
    size_in = len(signal)
    size_out = int(ratio * size_in + 0.5)
    bins = min(size_in, size_out) // 2 + 1
    freq = numpy.fft.rfft(signal)[:bins]
    return numpy.fft.irfft(size_out * freq / size_in, n=size_out)
"""
```

```python {.marimo}
editor_ui = melopa.ui.editor(code)
signal_state, signal_ui = melopa.source.ui("templeofhades-scratch_sample.wav")
ratio_ui = mo.ui.slider(
    0.1, 6, 0.1, debounce=True, label="Ratio", show_value=True, value=1
)
plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Code": editor_ui,
        "Signal": signal_ui,
        "Parameter": mo.hstack([ratio_ui], gap=2, justify="start"),
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
