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
title: Beamforming
width: medium
---

# Beamforming

```python {.marimo name="setup"}
import marimo as mo
```

Beamforming uses microphone arrays to perform spatial filtering of sound. It
uses the phase and amplitude of signals from multiple microphones to focus on
sound from a specific angle.
