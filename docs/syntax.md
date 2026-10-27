# MDXL syntax reference

## Headings

| Source | Meaning |
|---|---|
| `-# Text` | Micro-header level 1 |
| `-## Text` | Micro-header level 2 |
| `-### Text` | Micro-header level 3 |
| `#### Text` | Standard Markdown level-four heading |

The three dash-prefixed levels are deliberately compact. The fourth-level Markdown heading remains supported independently.

## Text effects

- `/col//Text /col#RRGGBB//`: true-color text.
- `/rbw//Text//rbw//`: per-character rainbow.
- `//hl//Text//hl//`: highlight.
- `/red//Text/red//`: strikethrough/redaction styling.
- `//key//Ctrl+C//key//`: keyboard keycap.
- `||||[Hidden text]||||`: invisible ink; the preview reveals it on hover or keyboard focus.
- `/!!!/Text/!!!/`: reverse and map supported glyphs to upside-down Unicode.

## Inline cues

- `/bar//70//`: progress bar; values outside 0–100 are clamped.
- `[[==>>]]`, `[[<<==]]`, `[[<=>>]]`: right, left, and bidirectional arrows. Click in the preview to cycle.
- `:check:`, `:rocket:`, `:warn:`: supported shortcode examples. Unknown shortcodes remain unchanged.

## Code blocks

Five backticks around a language-tagged block give it MDXL's dedicated code presentation:

`````python
print("Copyable example")
```

The preview offers a copy button. No code is executed automatically. Standard Markdown code fences remain supported.
