# MDXL syntax and Markdown compatibility

MDXL combines its own expressive tokens with core Markdown, GitHub Flavored Markdown (GFM), Markdown Extra-style extensions, and a few PyMdown conveniences. Common Markdown remains valid, while MDXL adds optional styling.

## Heading syntax

| Source | Result |
|---|---|
| `-# Text` | MDXL micro-header, level 1 |
| `-## Text` | MDXL micro-header, level 2 |
| `-### Text` | MDXL micro-header, level 3 |
| `#### Text` | Ordinary Markdown level-four heading |
| `## A titled section {#custom-id}` | Markdown heading with a stable custom ID |

The three dash-prefixed headings are MDXL-specific. In particular, `####` remains an ordinary Markdown heading. Its four hashes are not consumed as a custom token.

## Core Markdown

The browser renderer supports headings, paragraphs, block quotes, ordered and unordered lists, nested lists, links, images, bold and italic emphasis, inline code, horizontal rules, fenced code blocks, and tables. Fences using backticks or tildes work.

```markdown
# Document title

A paragraph with **strong text**, *emphasis*, and inline code.

> A quotation can contain a short note.

1. First item
2. Second item

- A bullet
- Another bullet

[MDXL on GitHub](https://github.com/trail-b1az3r/mdxl)
```

## GitHub Flavored Markdown

### Tables and column alignment

Use pipes to separate cells. Colons in the divider row control alignment.

```markdown
| Feature | Default | Aligned |
| --- | :--- | ---: |
| Tables | supported | yes |
| MDXL tokens | optional | readable |
```

### Task lists

Task lists render as disabled checkboxes in the browser preview. They communicate status, but the preview does not act as an editable issue tracker.

```markdown
- [x] Restore the renderer
- [x] Add Markdown extensions
- [ ] Write a document
  - [ ] Review the examples
```

The terminal renderer prints a green checked marker for completed tasks and an unchecked marker for incomplete tasks.

### Strikethrough

Wrap text in double tildes:

```markdown
This was ~~replaced by a better approach~~.
```

### Bare URL and email autolinks

Plain URLs and email addresses become links in the browser preview. Angle-bracket autolinks also work.

```markdown
Visit https://github.com/trail-b1az3r/mdxl
Questions? writer@example.com
<https://example.com>
```

### GitHub-style alerts

Alert callouts use GitHub's familiar quote syntax and appear as styled callouts in the browser preview.

```markdown
> [!NOTE]
> A regular MDXL file remains a plain-text document.

> [!WARNING]
> Check the example before using it in a production workflow.
```

Supported alert types are NOTE, TIP, IMPORTANT, WARNING, and CAUTION. GitHub-specific mentions such as @username, repository issue references such as #123, and pull-request shortcuts are not resolved by this local renderer because they require repository context.

## Markdown Extra-style syntax

### Footnotes

Use a reference in the paragraph and define it elsewhere.

```markdown
MDXL can add a small note without interrupting the paragraph.[^syntax-note]

[^syntax-note]: Footnotes are collected at the bottom of the rendered document.
```

### Definition lists

Place a term on one line and indent its definition with a colon.

```markdown
MDXL
: A Markdown extension with additional text effects.
```

### Abbreviations

Define an abbreviation and matching uses are marked with a title.

```markdown
*[GFM]: GitHub Flavored Markdown

MDXL supports GFM syntax alongside its custom tokens.
```

### Attribute lists and custom heading IDs

Add an ID or class to a heading using braces.

```markdown
## Release notes {#release-notes}
### Internal details {.muted #internal-details}
```

Raw HTML tags in source documents are escaped for safety. Markdown Extra's Markdown-inside-raw-HTML mode is therefore intentionally unavailable; use ordinary Markdown blocks, definition lists, and attribute lists instead.

## Extended inline conveniences

The preview also supports small PyMdown-style inline additions and collapsible details.

| Syntax | Result |
|---|---|
| `==important==` | Inline highlight |
| `^2^` | Superscript |
| `^^new text^^` | Inserted text |
| Three question marks, a title, and an indented block | Collapsible details disclosure |

Example disclosure:

```markdown
??? note "Why use MDXL?"

    The source stays readable in a text editor, and the renderer adds visual structure.
```

MDXL's own highlight token //hl//text//hl// remains available too.

## MDXL inline tokens

| Source | Effect |
|---|---|
| /col//Text /col#RRGGBB// | Six-digit hex color |
| /rbw//Text//rbw// | Rainbow text |
| //hl//Text//hl// | Highlight |
| /red//Text/red// | Strikethrough-style redaction |
| //key//Ctrl+C//key// | Keyboard keycap |
| /bar//70// | Progress bar, clamped to 0–100 |
| ||||[Hidden text]|||| | Invisible ink in the browser preview |
| /!!!/Turn around/!!!/ | Upside-down Unicode approximation |
| [[==>>]], [[<<==]], [[<=>>]] | Directional arrows; click to cycle in preview |
| :check:, :rocket:, :warn:, :fire:, :star: | Supported shortcode replacements |

## Code blocks and safety

Standard three-backtick or tilde fences remain ordinary Markdown code blocks. Five backticks select MDXL's copyable-code presentation. Tokens inside fenced code are preserved and not reinterpreted.

```python
print("The preview displays this source; it never executes it.")
```

Raw HTML is escaped, and rendered Markdown is sanitized. Unsafe attributes and URL schemes are removed. The local preview is for reading documents, not executing embedded HTML or scripts.

## Renderer notes

- mdxl-preview supports the GFM and Markdown Extra-style features listed here.
- mdxl-cli styles MDXL tokens and provides terminal equivalents for GFM task markers and double-tilde strikethrough. Tables, footnotes, definitions, and other structural Markdown remain readable as plain source in the terminal.
- Kate uses mdxl.xml for MDXL highlighting and completions; it is not a full Markdown parser.
