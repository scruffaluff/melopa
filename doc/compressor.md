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
title: Compressor
width: medium
---

<!-- prettier-ignore-start -->

# Compressor

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import marimo as mo
import numpy
from numpy.typing import NDArray

import melopa
```

Dynamic range compressors decrease the amplitude variation in audio by
attenuating loud sounds and amplifying quiet sounds. A downward peak compressor
only attenuates loud sounds above a specific amplitude. It is controlled by the
following parameters which attached to their variable names.

- _Threshold (T)_ controls the minimum amplitude for compression to be applied.
  Any sample above the threshold is attenuated.
- _Ratio (R)_ controls the amount of compression to be applied for samples above
  the threshold.
- _Attack_ controls how quickly compression is applied after going above the
  threshold.
- _Release_ controls how quickly compression is stopped after going below the
  threshold.
- _Knee (K)_ softens the threshold transition by rounding its angle.
- _Gain (G)_ applies additional volume to the signal after compression and
  compensates for the reduction in signal amplitude.

The compression algorithm without the _attack_ or _release_ parameters is
described by the following formula[[1]](#1).

$$
f(x) = G \begin{cases}
x & \text{ when } x < T - \frac{K}{2} \\
x + \frac{(1 - R)(x - T + K/2)^2}{2KR} & \text{ when } T - \frac{K}{2} \leq x < T + \frac{K}{2} \\
T + (x - T)/R & \text{ when } x \geq T + \frac{K}{2} \\
\end{cases}
$$

The algorithm is implemented with the following editable code.

```python {.marimo}
code = f"""
def compress(
    signal: NDArray,
    gain: float = 1.0,
    knee: float = 0.0,
    ratio: float = 4.0,
    threshold: float = 0.8,
) -> NDArray:
    sign = numpy.sign(signal)
    amplitude = numpy.abs(signal)

    for index in range(len(amplitude)):
        value = amplitude[index] - threshold
        if value > knee / 2:
            amplitude[index] = threshold + value / ratio
        elif value > -knee / 2:
            smoothing = (value + knee / 2) ** 2 / (2 * knee * ratio)
            amplitude[index] += (1 - ratio) * smoothing

    return gain * sign * amplitude
""".strip()
editor = melopa.ui.editor(code)
```

```python {.marimo}
state, audio = melopa.source.ui("templeofhades-scratch_sample.wav")
gain_ui = mo.ui.slider(
    1, 10, 0.01, debounce=True, label="Gain", show_value=True, value=1.0
)
knee_ui = mo.ui.slider(
    0, 1, 0.01, debounce=True, label="Knee", show_value=True, value=0.0
)
ratio_ui = mo.ui.slider(
    1, 100, 0.1, debounce=True, label="Ratio", show_value=True, value=4.0
)
threshold_ui = mo.ui.slider(
    0, 1, 0.01, debounce=True, label="Threshold", show_value=True, value=0.8
)
plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Code": editor,
        "Parameter": mo.hstack(
            [gain_ui, knee_ui, ratio_ui, threshold_ui], gap=2, justify="start"
        ),
        "Signal": audio,
        "Plot": plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
source = state()
signal, rate = source.read()
exec(editor.value["editor"])
processed, output = melopa.ui.run(
    lambda: compress(
        signal, gain_ui.value, knee_ui.value, ratio_ui.value, threshold_ui.value
    )
)
output
```

```python {.marimo unparsable="true"}
melopa.plot.signal(
    [
        {"rate": rate, "y": signal, "legend_label": "original"},
        {"rate": rate, "y": processed, "legend_label": "compressed"},
    ],
    title=source.name(),
    **plot_ui.value,
)
```

We can listen to both versions of the signal below.

```python {.marimo}
mo.hstack(
    [
        mo.vstack([mo.md("### Original"), mo.audio(signal, rate)]),
        mo.vstack([mo.md("### Compressed"), mo.audio(processed, rate)]),
    ],
    gap=2,
    justify="start",
)
```

## References

<a id="1">[1]</a>
Giannoulis, Dimitrios & Massberg, Michael & Reiss, Joshua. (2012). [Digital Dynamic Range Compressor Design—A Tutorial and Analysis](https://www.researchgate.net/publication/277772168_Digital_Dynamic_Range_Compressor_Design-A_Tutorial_and_Analysis). AES: Journal of the Audio Engineering Society. 60.

<a id="2">[2]</a>
McCormack, Leo and Valimaki, Vesa and others. [FFT-based dynamic range compression](https://leomccormack.github.io/sparta-site/docs/help/related-publications/mccormack2017fft.pdf). 2017.

<!-- prettier-ignore-end -->
