---
favicon: /melopa/favicon.svg
theme: default
title: About
titleTemplate: "%s | Melopa"
---

# Melopa

Melopa is the Scruffaluff wiki with tutorials, webapps, and workbooks.

---

# Why Slidev?

- **Markdown-based** — write slides in plain Markdown
- **Developer-friendly** — Vue components, code highlighting, monorepo support
- **Interactive** — embedded demos, presentor notes, remote control
- **Portable** — export to PDF, build to static HTML

---

# Layouts

::left::

# Text Content

Regular markdown content goes on the left side.

- Bullet points
- Code snippets
- Images

::right::

# Code Example

```ts
import { ref } from "vue";

const count = ref(0);
const double = computed(() => count.value * 2);
```

---

# Themes & Customization

This presentation uses the **default** theme, styled to match the site:

- Fira Sans for body text
- Fira Code for code
- Purple accent color

---

# Get Started

1. Add `slidev` to your devDependencies
2. Create a markdown file with frontmatter
3. Run `slidev` to start the dev server
4. Run `just build` to include in the site

---

# Thank You

Questions? Check the source on GitHub.
