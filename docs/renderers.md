# Renderers and Markdown compatibility

## Browser preview

The mdxl-preview command renders MDXL plus extended Markdown in a local browser. Supported syntax includes:

- Core Markdown blocks, links, emphasis, lists, quotes, fenced code blocks, and tables.
- GFM task lists, strikethrough, bare URL/email autolinks, aligned tables, and GitHub-style alert callouts.
- Markdown Extra-style footnotes, definition lists, abbreviations, custom heading IDs, and attribute lists.
- Inline highlight, superscript, inserted text, and collapsible details.
- MDXL color, rainbow, keycap, progress, invisible-ink, arrow, shortcode, and heading tokens.

Five-backtick blocks become copyable code blocks. Source code is not executed. Raw HTML tags are escaped, and the rendered fragment is sanitized; unsafe attributes and URL schemes are removed.

## Terminal renderer

The mdxl-cli command maps MDXL tokens to ANSI colors and Unicode. It also renders GFM checklist markers and double-tilde strikethrough. Markdown tables, footnotes, definitions, and links remain readable source text rather than becoming a fully typeset terminal document.

## Export and live preview

mdxl-preview serves the file on 127.0.0.1 and refreshes when it changes. Export standalone HTML with:

```bash
mdxl-preview demo.mdxl --export
mdxl-preview demo.mdxl --export ./demo.html
```

Useful options include --port, --no-open, --stdout, and --live. The server binds to loopback only.

## Kate syntax

mdxl.xml declares the .mdxl extension, token highlighting, and completions. Kate uses the syntax definition, not the browser parser, so richer Markdown features may not receive the same in-editor rendering.
