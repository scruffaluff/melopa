---
title: Compression
marimo-version: 0.20.2
width: medium
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "numpy~=2.2",
  #   "scipy~=1.14",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
---

# Compression

```python {.marimo name="setup"}
import sys
if sys.platform == "emscripten":
    import micropip
    await micropip.install("/melopa/data/melopa-0.1.0-py3-none-any.whl")
import marimo as mo
import numpy
from numpy.typing import NDArray
import melopa
from melopa.plot import Kind
```

Dynamic range compressors decrease an audio signal's dynamic range by
attenuating loud samples and amplifying quiet samples.

Compressor parameters:

- _Threshold_ is the minimum amplitude for compression to be applied.
- _Ratio_ is the amount of compression to be applied.
- _Attack_ is how quickly compression is applied.
- _Release_ is how quickly compression falls off.
- _Make gain_ is additional gain applied to the entire signal.
- _Knee width_ smooths the compression to ensure differentiability at the
  threshold.

The compression algorithm for this tutorial is implemented with the following
code.

```python {.marimo}
code = mo.ui.code_editor(
    value=f"""
def compress(
    signal: NDArray,
    knee_width: float = 0.0,
    make_gain: float = 0.0,
    ratio: float = {ratio.value},
    threshold: float = {threshold.value},
) -> NDArray:
    sign = numpy.sign(signal)
    amplitude = numpy.abs(signal)

    for index in range(len(signal)):
        value = amplitude[index] - threshold
        if value > knee_width / 2:
            amplitude[index] = value / ratio + threshold
        elif value > -knee_width / 2:
            smoothing = (value + knee_width / 2) ** 2 / (2 * knee_width)
            amplitude[index] += (1 / ratio - 1) * smoothing

    return sign * (amplitude + make_gain)
    """.strip(),
    language="python",
    debounce=True,
)
code
```

```python {.marimo}
state, audio = melopa.audio_selector("templeofhades-scratch_sample.wav")
ratio = mo.ui.slider(0, 100, 0.1, label="Ratio", show_value=True, value=4.0)
threshold = mo.ui.slider(0, 1, 0.01, label="Threshold", show_value=True, value=0.8)
visual = melopa.plot_selector()

mo.ui.tabs(
    {
        "File": audio,
        "Parameter": mo.hstack([ratio, threshold], gap=2, justify="start"),
        "Visual": visual,
    },
    label="Controls"
)
```

```python {.marimo}
source = state()
signal, rate = source.read()
exec(f"{code.value}\nprocessed = compress(signal)")
```

```python {.marimo}
plot = melopa.plot.signal([
    {"rate": rate, "y": signal, "legend_label": "original"},
    {"rate": rate, "y": processed, "legend_label": "compressed"},
    ],
    backend=visual.value["backend"].lower(),
    kind=Kind(visual.value["kind"].lower()),
    overlay=visual.value["overlay"],
    title=source.name(),
)
plot
```

We can listen to both versions of the signal below.

```python {.marimo}
mo.hstack([mo.vstack([mo.md("### Original"), mo.audio(signal, rate)]), mo.vstack([mo.md("### Compressed"), mo.audio(processed, rate)])], gap=2, justify="start")
```
