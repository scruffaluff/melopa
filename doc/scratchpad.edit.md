---
header: |-
  # /// script
  # dependencies = [
  #   "bokeh~=3.6",
  #   "librosa~=0.11.0",
  #   "matplotlib~=3.8",
  #   "numpy~=2.2",
  #   "polars~=1.36",
  #   "scipy~=1.14",
  # ]
  # requires-python = ">=3.12.0,<4.0.0"
  #
  # [tool.uv.sources]
  # melopa = { editable = true, path = "src/melopa" }
  # ///
title: Scratchpad
marimo-version: 0.22.0
width: medium
---

```python {.marimo name="setup"}
import sys

await __import__("micropip").install(
    "/melopa/data/melopa-0.1.0-py3-none-any.whl"
) if sys.platform == "emscripten" else None

import bokeh
import marimo as mo
import numpy
import scipy

import melopa
```
