---
marimo-version: 0.20.2
title: Reverberation
width: medium
---

<!-- prettier-ignore-start -->

# Reverberation

```python {.marimo name="setup"}
import marimo as mo
import melopa
```

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
