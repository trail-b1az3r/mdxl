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

The mdxl-cli command maps MDXL tokens to ANSI colors and Unicode. It renders GFM checklist markers and double-tilde strikethrough, formats aligned GFM tables as bordered terminal grids, and turns GFM alert blockquotes into color-labeled callouts. Footnotes, definitions, and links remain readable source text rather than becoming a fully typeset terminal document.

## Executable code, translation, and formatted documents

JavaScript code fences receive an explicit Run button. Execution is user-triggered and occurs in a sandboxed iframe with network access disabled; MDXL does not auto-run code when opening a document. Other languages are displayed and copied as source only. The CLI never executes code.

`//autoT//...//target` marks text for source-language detection and translation to a target alias. The browser preview automatically submits only explicitly marked spans to its translation endpoint. The terminal renderer also submits explicitly marked translation spans when `mdxl-cli` processes the file. The default is a community-hosted LibreTranslate endpoint; set `MDXL_TRANSLATE_ENDPOINT` and optionally `MDXL_TRANSLATE_API_KEY` before starting `mdxl-preview` to use a different or self-hosted service. Regional Spanish aliases use Spanish translation plus a best-effort vocabulary adjustment. Joke aliases are local word substitutions, not machine translations.

`>>>[APA](Title)(Author)(Course)(Date)` starts a format-styled document block. Its body continues until the next `>>>[...]` format header or end-of-file. The built-in styles are visual templates rather than a full academic citation engine.

## Export and live preview

mdxl-preview serves the file on 127.0.0.1 and refreshes when it changes. Export standalone HTML with:

```bash
mdxl-preview demo.mdxl --export
mdxl-preview demo.mdxl --export ./demo.html
```

Useful options include --port, --no-open, --stdout, and --live. The server binds to loopback only.

## Kate syntax

The `mdxl.xml` definition is named **Markdown Extended Logic**, registers `*.mdxl` as `text/x-mdxl`, and adds highlighting and completions for MDXL-specific tokens and Extended Markdown markers. It imports Kate's bundled Markdown grammar for standard Markdown and GFM syntax, including headings, lists, inline emphasis, links and images, tables, block quotes, horizontal rules, fenced code blocks, and language-specific code highlighting where the bundled grammar supports it. Kate provides syntax highlighting, not the browser's rendered visual effects; for example, it highlights `/rbw//text//rbw//` as MDXL syntax instead of displaying each letter in rainbow colors.
