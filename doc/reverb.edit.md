---
marimo-version: 0.21.0
title: Reverb
width: medium
---

<!-- prettier-ignore-start -->
<!-- Check if the lack of dependency specification in the header causes slower
WASM loads. -->

# Reverb

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import marimo as mo
import numpy
import scipy

import melopa
```

Acoustic reverb is the effect of sound bouncing off surfaces and reflecting back
into the original sound. When sound encounters a surface, some of it is absorbed
while the rest echos back as a reflection. When a large number of reflections
combine with the original sound it is perceived as reverb instead of an echo.

Reverberation time is the number of seconds it takes for the reverberation of a
sound to drop by 60 decibels from its initial value.

## Moorer Algorithm

We start our reverb analysis by implementing an algorithm by James Moorer[1].
His algorithm splits reverberation into distincter early reflections and less
distinct late reflections. The early reflections are modeled by a series of
delays and the late reflections are modeled by a comb filter. These reflections
are then added back into the signal.

The algorithm logic is encapsulated in the block diagram below.

```python {.marimo}
mo.mermaid("""
---
config:
  theme: neutral
title: Moorer Reverb
---

graph LR
    H0:::hidden -- x[n] --- H1:::hidden

    subgraph Early Reflections
        H1 --> Delay("$$ Z^{-mN} $$")
        H1 --- H2:::hidden
        Delay --- H2
    end

    H2 --> Add(("+"))
    Add --- H3:::hidden

    subgraph Late Reflections
        H3 --- H4:::hidden
        H3 --> Comb("`Comb Filter\n$$ Z^{-1} $$`")
        Comb --- H4
    end

    H4 -- y[n] --> H5:::hidden
""")
```

```python {.marimo}
code = f"""
def allpass(signal: NDArray, delay: int, gain: float) -> NDArray:
    B = numpy.zeros(delay)
    B[0] = gain
    B[delay - 1] = 1
    A = numpy.zeros(delay)
    A[0] = 1
    A[delay - 1] = gain
    processed = numpy.zeros(signal.shape)
    processed = scipy.signal.lfilter(B, A, signal)
    return processed


def comb(signal: NDArray, delay: int, gain: float) -> NDArray:
    B = numpy.zeros(delay)
    B[delay - 1] = 1
    A = numpy.zeros(delay)
    A[0] = 1
    A[delay - 1] = -gain
    processed = numpy.zeros(signal.shape)
    processed = scipy.signal.lfilter(B, A, signal)
    return processed


def comb_with_lp(signal: NDArray, delay, g: float, g1: float) -> NDArray:
    g2 = g * (1 - g1)
    B = numpy.zeros(delay + 1)
    B[delay - 1] = 1
    B[delay] = -g1
    A = numpy.zeros(delay)
    A[0] = 1
    A[1] = -g1
    A[delay - 1] = -g2
    processed = numpy.zeros(signal.shape)
    processed = scipy.signal.lfilter(B, A, signal)
    return processed


def delay(signal: NDArray, delay: int, gain: float = 1) -> NDArray:
    return gain * numpy.concatenate((numpy.zeros(delay), signal))


def reverb(signal: NDArray, wet: float = 0.5) -> NDArray:
    dry = 1 - wet

    delays = [2205, 2469, 2690, 2998, 3175, 3439]
    delays_early = [877, 1561, 1715, 1825, 3082, 3510]
    gains_early = [1.02, 0.818, 0.635, 0.719, 0.267, 0.242]
    g1_list = [0.41, 0.43, 0.45, 0.47, 0.48, 0.50]
    g = 0.9
    rev_to_er_delay = 1800
    allpass_delay = 286
    allpass_g = 0.7

    early_reflections = numpy.zeros(signal.size)
    combs_out = numpy.zeros(signal.size)

    for i in range(6):
        early_reflections = (
            early_reflections
            + delay(signal, delays_early[i], gains_early[i])[: signal.size]
        )
        combs_out = combs_out + comb_with_lp(signal, delays[i], g, g1_list[i])

    reverb = allpass(combs_out, allpass_delay, allpass_g)
    early_reflections = numpy.concatenate(
        (early_reflections, numpy.zeros(rev_to_er_delay))
    )

    reverb = delay(reverb, rev_to_er_delay)
    reverb_out = early_reflections + reverb
    return wet * reverb_out + dry * numpy.concatenate((signal, numpy.zeros(rev_to_er_delay)))
"""
```

```python {.marimo}
editor_ui = melopa.ui.editor(code)
signal_state, signal_ui = melopa.source.ui("templeofhades-scratch_sample.wav")
wet_ui = mo.ui.slider(
    0, 1, 0.01, debounce=True, label="Wet", show_value=True, value=0.5
)
plot_ui = melopa.plot.ui()
mo.ui.tabs(
    {
        "Code": editor_ui,
        "Signal": signal_ui,
        "Parameter": mo.hstack([wet_ui], gap=2, justify="start"),
        "Plot": plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
signal_source = signal_state()
signal, rate = signal_source.read()
exec(editor_ui.value["editor"])
processed, output = melopa.ui.run(lambda: reverb(signal, wet=wet_ui.value))
output
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": rate, "y": signal, "legend_label": "original"},
        {"rate": rate, "y": processed, "legend_label": "reverbed"},
    ],
    title=signal_source.name(),
    **plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": signal, "rate": rate, "name": "Original"},
    {"signal": processed, "rate": rate, "name": "Reverbed"},
])
```

## References

<a id="1">[1]</a>
Moorer, James A. [About This Reverberation Business.](https://www.researchgate.net/publication/239735102_About_This_Reverberation_Business) Computer Music Journal, vol. 3, no. 2, June 1979, p. 13. DOI.org (Crossref), https://doi.org/10.2307/3680280.

<!-- prettier-ignore-end -->
