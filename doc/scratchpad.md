---
title: Scratchpad
marimo-version: 0.20.2
width: medium
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "librosa~=0.11.0",
  #   "matplotlib~=3.10",
  #   "numpy~=2.2",
  #   "polars~=1.36",
  #   "plotly~=6.5",
  #   "scipy~=1.14",
  #   "soundfile~=0.13.0",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
---

```python {.marimo name="setup"}
import sys
if sys.platform == "emscripten":
    import micropip
    await micropip.install("/melopa/data/melopa-0.1.0-py3-none-any.whl")
import marimo as mo
import melopa
```
