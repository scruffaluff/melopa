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
marimo-version: 0.23.14
title: Modulation
width: medium
---

# Modulation

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
from melopa.source import SourceConstant, SourceSawtooth, SourceSine
```

Audio modulation is the process of varying a property of a signal, called the
carrier, by another signal, called the modulator.

## Amplitude Modulation

Amplitude modulation modifies the instantaneous amplitude of the carrier signal
using the amplitude from the modulator signal. It is described by the following
equation where $c[n]$ is the carrier signal and $m[n]$ is the modulator signal.

$$ y[n] = m[n] c[n] $$

A common application of amplitude modulation is the ADSR envelope. Its name is
an acronym for its parameters of attack, decay, sustain, and release.

- Attack is the time ratio to increase from zero to peak amplitude.
- Decay is the time ratio to decrease from peak to sustain amplitude.
- Sustain is the amplitude level maintained between the decay and release
  phases.
- Release is the time ratio to decrease from sustain to zero amplitude.

An ADSR envelope is applied to a sawtooth wave in the section below.

```python {.marimo}
adsr_attack_ui = mo.ui.slider(
    0,
    1,
    0.01,
    debounce=True,
    label="Attack",
    show_value=True,
    value=0.1,
)
adsr_decay_ui = mo.ui.slider(
    0,
    1,
    0.01,
    debounce=True,
    label="Decay",
    show_value=True,
    value=0.2,
)
adsr_sustain_ui = mo.ui.slider(
    0,
    1,
    0.01,
    debounce=True,
    label="Sustain",
    show_value=True,
    value=0.5,
)
adsr_release_ui = mo.ui.slider(
    0,
    1,
    0.01,
    debounce=True,
    label="Release",
    show_value=True,
    value=0.1,
)
adsr_plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Parameter": mo.hstack(
            [adsr_attack_ui, adsr_decay_ui, adsr_sustain_ui, adsr_release_ui],
            gap=2,
            justify="start",
            wrap=True,
        ),
        "Plot": adsr_plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
adsr_source = SourceSawtooth(110)
adsr_signal, adsr_rate = adsr_source.read()
adsr_processed = melopa.modulate.adsr(
    adsr_signal,
    adsr_attack_ui.value,
    adsr_decay_ui.value,
    adsr_sustain_ui.value,
    adsr_release_ui.value,
)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": adsr_rate, "y": adsr_processed, "legend_label": "modulated"},
    ],
    title=adsr_source.name(),
    **adsr_plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": adsr_signal, "rate": adsr_rate, "name": "Original"},
    {"signal": adsr_processed, "rate": adsr_rate, "name": "Modulated"},
])
```

## Frequency Modulation

Frequency modulation modifies the instantaneous frequency of the carrier signal
using the amplitude from the modulator signal. If the carrier wave is a sine
signal with frequency $f$ and $m[n]$ is the modulator signal, then the following
equation and its live demo describes an implementation of frequency modulation.

$$ y[n] = \sin(2 \pi f n + m[n]) $$

```python {.marimo}
fm_mod_ui = melopa.source.ui_synth("sine")
fm_amp_ui = mo.ui.slider(
    debounce=True,
    label="Amplitude",
    show_value=True,
    steps=[0, *numpy.round(numpy.logspace(-4, 5, 28, base=2), 2)],
    value=1.0,
)
fm_freq_car_ui = mo.ui.slider(
    debounce=True,
    label="Carrier Frequency",
    show_value=True,
    steps=numpy.round(440 * numpy.logspace(-3, 4, 15, base=2), 2),
    value=110.0,
)
fm_freq_mod_ui = mo.ui.slider(
    debounce=True,
    label="Modulator Frequency",
    steps=numpy.round(numpy.logspace(0, 2, 32, base=10), 2),
    value=8.0,
)
fm_plot_ui = melopa.plot.ui()

mo.ui.tabs(
    {
        "Modulator": fm_mod_ui,
        "Parameter": mo.hstack(
            [fm_amp_ui, fm_freq_car_ui, fm_freq_mod_ui],
            gap=2,
            justify="start",
            wrap=True,
        ),
        "Plot": fm_plot_ui,
    },
    label="Controls",
)
```

```python {.marimo}
fm_mod_source = fm_mod_ui.value(freq=fm_freq_mod_ui.value)
fm_mod, fm_rate = fm_mod_source.read()
fm_time = numpy.linspace(0, 1, len(fm_mod))
fm_signal = numpy.sin(2 * numpy.pi * fm_freq_car_ui.value * fm_time)
fm_processed = melopa.math.normalize(
    numpy.sin(2 * numpy.pi * fm_freq_car_ui.value * fm_time + fm_amp_ui.value * fm_mod)
)
```

```python {.marimo}
melopa.plot.signal(
    [
        {"rate": fm_rate, "y": fm_processed, "legend_label": "modulated"},
    ],
    title="Sine",
    **fm_plot_ui.value,
)
```

```python {.marimo}
melopa.ui.audio_list([
    {"signal": fm_signal, "rate": adsr_rate, "name": "Carrier"},
    {"signal": fm_processed, "rate": fm_rate, "name": "Modulated"},
])
```
