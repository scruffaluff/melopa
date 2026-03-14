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

Audio filters remove aspects of sound such as frequencies. Casual LTI filters
are well described by their Z-transform.

We'll start with a moving average filter.

```python {.marimo}
maf_code = f"""
def moving_average(signal: NDArray, length: int) -> NDArray:
    filter = numpy.ones(length) / length
    return numpy.convolve(filter, signal, mode="same")
""".strip()
maf_editor = melopa.ui.editor(maf_code)
```

```python {.marimo}
maf_state, maf_audio = melopa.source.ui("templeofhades-scratch_sample.wav")
maf_length_ui = mo.ui.slider(
    1, 100, 1, debounce=True, label="Length", show_value=True, value=8
)
mo.ui.tabs(
    {
        "Code": maf_editor,
        "Parameter": maf_length_ui,
        "Signal": maf_audio,
    },
    label="Controls",
)
```

```python {.marimo}
maf_source = maf_state()
maf_signal, maf_rate = maf_source.read()
exec(maf_editor.value["editor"])
maf_processed, maf_output = melopa.ui.run(
    lambda: moving_average(maf_signal, maf_length_ui.value)
)
maf_output
```

```python {.marimo}
maf_visual = melopa.plot.ui()
mo.right(maf_visual)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": maf_rate, "y": maf_signal, "legend_label": "original"},
        {"rate": maf_rate, "y": maf_processed, "legend_label": "filtered"},
    ],
    title=maf_source.name(),
    **maf_visual.value,
)
```

We can listen to both versions of the signal below.

```python {.marimo}
mo.hstack(
    [
        mo.vstack([mo.md("### Original"), mo.audio(maf_signal, maf_rate)]),
        mo.vstack([mo.md("### Filtered"), mo.audio(maf_processed, maf_rate)]),
    ],
    gap=2,
    justify="start",
)
```

## Finite Response

## Infinite Response

## Butterworth

- Has no gain ripple.

The following
interface provides controls for a Butterworth low-pass filter, which attenuates high
frequencies from a signal.

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

We can apply the low-pass filter to any sound and visualized its affects below.

```python {.marimo}
sample, rate_ = SourceFile("templeofhades-scratch_sample.wav").read()
sos = scipy.signal.butter(10, 1000, "lowpass", fs=rate, output="sos")
processed = scipy.signal.sosfilt(sos, sample)
```

```python {.marimo hide_code="true"}
visual = melopa.plot.ui()
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
