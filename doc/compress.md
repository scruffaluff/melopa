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
marimo-version: 0.24.0
title: Compression
width: medium
---

# Compression

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

Dynamic range compressors narrow the volume bandwidth in audio by attenuating
loud sounds or amplifying quiet sounds. A compressor that only attenuates loud
sounds is called a downward peak compressor. The compressor calculates the
current volume of the signal and then uses the following parameters.

- _Threshold (T)_ controls the minimum amplitude for compression to be applied.
  Any sample above the threshold is attenuated.
- _Ratio (R)_ controls the amount of compression in decibels to be applied for
  samples above the threshold.
- _Attack (A)_ controls how quickly compression is applied after going above the
  threshold.
- _Release (L)_ controls how quickly compression is stopped after going below the
  threshold.
- _Knee (K)_ softens the threshold transition by rounding its edge.
- _Gain (G)_ applies additional volume to the signal after compression and
  compensates for the reduction in signal amplitude.

The compression algorithm is commonly split into two routines, level detection
and gain computer. The level detector routine measures the volume of the signal to
find when the threshold has been crossed.

The gain computer routine determines how to scale the signal after the level
detector finds a threshold crossing. Its algorithm is described by the following
formula [[1]](#r1).

$$
f(x) = \begin{cases}
x & \text{ when } x < T - \frac{K}{2} \\
x + \frac{(1 - R)(x - T + K/2)^2}{2KR} & \text{ when } T - \frac{K}{2} \leq x < T + \frac{K}{2} \\
T + (x - T)/R & \text{ when } x \geq T + \frac{K}{2} \\
\end{cases}
$$

The algorithm is implemented with the following editable code.

```python {.marimo}
editor_ui = melopa.ui.editor(
    melopa.code.compress, melopa.code.gain_compute, melopa.code.level_detect
)
signal_state, signal_ui = melopa.source.ui("templeofhades-scratch_sample.wav")
attack_ui = mo.ui.slider(
    0, 100, 1, debounce=True, label="Attack", show_value=True, value=0
)
knee_ui = mo.ui.slider(
    0, 1, 0.01, debounce=True, label="Knee", show_value=True, value=0.0
)
ratio_ui = mo.ui.slider(
    debounce=True,
    label="Ratio",
    show_value=True,
    steps=numpy.round(numpy.logspace(0, 4, 33, base=2), 2),
    value=4.0,
)
release_ui = mo.ui.slider(
    0, 100, 1, debounce=True, label="Release", show_value=True, value=0
)
threshold_ui = mo.ui.slider(
    debounce=True,
    label="Threshold",
    show_value=True,
    steps=[0, *-numpy.round(numpy.logspace(-2, 6, 33, base=2), 2)],
    value=-8,
)
plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Code": editor_ui,
        "Signal": signal_ui,
        "Parameter": mo.hstack(
            [attack_ui, knee_ui, ratio_ui, release_ui, threshold_ui],
            gap=2,
            justify="start",
            wrap=True,
        ),
        "Plot": plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
signal_source = signal_state()
signal, rate = signal_source.read()
exec(editor_ui.value["editor"])
processed, output = melopa.ui.run(
    lambda: compress(
        signal,
        attack=rate * attack_ui.value / 1_000,
        knee=knee_ui.value,
        ratio=ratio_ui.value,
        release=rate * release_ui.value / 1_000,
        threshold=threshold_ui.value,
    )
)
output
```

```python {.marimo}
volume = melopa.math.decibel(signal)
reduction = gain_compute(volume, knee_ui.value, ratio_ui.value, threshold_ui.value)
level = level_detect(reduction, attack_ui.value, release_ui.value)
melopa.plot.signal(
    {
        "rate": rate,
        "y": numpy.power(10, reduction / 20),
        "legend_label": "reduction",
    },
    {
        "rate": rate,
        "y": numpy.power(10, level / 20),
        "legend_label": "level",
    },
    title=signal_source.name(),
    **plot_ui.value,
)
```

```python {.marimo}
melopa.plot.signal(
    {"rate": rate, "y": signal, "legend_label": "original"},
    {"rate": rate, "y": processed, "legend_label": "compressed"},
    title=signal_source.name(),
    **plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": signal, "rate": rate, "name": "Original"},
    {"signal": processed, "rate": rate, "name": "Compressed"},
])
```

## References

<span id="r1">[1]</span> Giannoulis, Dimitrios & Massberg, Michael & Reiss, Joshua.
(2012).
[Digital Dynamic Range Compressor Design—A Tutorial and Analysis](https://www.researchgate.net/publication/277772168_Digital_Dynamic_Range_Compressor_Design-A_Tutorial_and_Analysis).
AES: Journal of the Audio Engineering Society. 60.

<span id="r2">[2]</span> McCormack, Leo and Valimaki, Vesa and others.
[FFT-based dynamic range compression](https://leomccormack.github.io/sparta-site/docs/help/related-publications/mccormack2017fft.pdf). 2017.
