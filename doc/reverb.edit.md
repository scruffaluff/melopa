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

import melopa
```

Acoustic reverb is the persistence of sound through reflections from surfaces.

## Moorer Algorithm

We start our reverb analysis by implementing the algorithm from James Moorer in
his _About This Reverberation Business_ article. The algorithm logic is
encapsulated in the block diagram below.

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

<!-- prettier-ignore-end -->
