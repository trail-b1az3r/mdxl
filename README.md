# MDXL

**Markdown Extended Logic** adds expressive syntax to Markdown while keeping documents readable as plain text. Render the same .mdxl file in your terminal, preview it locally in a browser, or edit it in Kate with native syntax highlighting and completions.

[![Actions](https://github.com/trail-b1az3r/mdxl/actions/workflows/pages.yml/badge.svg)](https://github.com/trail-b1az3r/mdxl/actions/workflows/pages.yml)
[![MIT](https://img.shields.io/badge/license-MIT-9ee37d.svg)](LICENSE)

**[Open the docs and syntax showcase](https://trail-b1az3r.github.io/mdxl/)** · [Repository](https://github.com/trail-b1az3r/mdxl)

## Features

- True-color and rainbow text, highlights, redaction, keyboard keycaps, invisible ink, and upside-down text.
- Progress bars, interactive arrow glyphs, shortcode replacements, and copyable code blocks.
- Common Markdown plus GFM task lists, strikethrough, autolinks, aligned tables, and alert callouts.
- Markdown Extra-style footnotes, definition lists, abbreviations, heading IDs, and attribute lists; plus highlight, superscript, insertion, and collapsible details.
- Three micro-header levels (`-#`, `-##`, `-###`) plus the `####` subheading.
- Terminal rendering with mdxl-cli and browser rendering with mdxl-preview.
- Kate syntax highlighting and completion suggestions.
- JavaScript code fences have an explicit Run JavaScript button and execute only after a click inside a sandboxed iframe; other languages remain copy-only. Marked `//autoT//...//target` text is automatically translated in the preview through the configured translation service. APA/MLA-style document blocks can provide up to four optional headers.

## Install

On Linux, from a clone or downloaded repository:

```bash
chmod +x install.sh
./install.sh
```

The installer installs both commands under `~/.local/bin`, registers the `text/x-mdxl` MIME type for `*.mdxl`, installs Kate's Markdown Extended Logic syntax definition, and creates a private virtual environment for the preview dependency. It does not use administrator privileges or modify system Python packages. Restart Kate and reopen existing `.mdxl` files after installation.

## Use

```bash
mdxl-cli demo.mdxl
mdxl-preview demo.mdxl
mdxl-preview demo.mdxl --export
mdxl-preview demo.mdxl --export ./demo.html
```

mdxl-preview opens a local preview and refreshes when the document changes. Useful options include --port 8420, --no-open, --stdout, and --export [path]. For manual setup of the preview dependency, run python3 -m pip install -r requirements-preview.txt.

## Syntax quick reference

MDXL builds on [GitHub Flavored Markdown](https://github.github.com/gfm/) and [Markdown Extra-style extensions](https://python-markdown.github.io/extensions/extra/). See the [complete syntax guide](https://trail-b1az3r.github.io/mdxl/syntax/) for examples and compatibility notes.

| Syntax | Effect |
| --- | --- |
| `-# Heading`, `-## Heading`, `-### Heading` | Three micro-header levels |
| `+# Heading`, `++# Heading` | Two additional compact heading levels |
| `>> Nested quote` | Quote inside another quotation |
| `~~~~Striped-through~~~~` | Striped strike-band effect |
| ` ```js ... ``` ` | Click-to-run JavaScript in a sandboxed preview |
| `//autoT//Hola//en` | Translate marked text into English |
| `>>>[APA](Title)(Author)(Course)(Date)` | Format a document block with optional headers |
| `#### Subheading` | Markdown level-four heading |
| `/col//Signal /col#B7F77A//` | Hex true color |
| `/rbw//Spectrum//rbw//` | Rainbow text |
| `//hl//Important//hl//` | Highlight |
| `/red//Deprecated/red//` | Strikethrough styling |
| `//key//Ctrl+C//key//` | Keycap |
| `/bar//70//` | Progress bar (0–100) |
| `||||[Hidden note]||||` | Invisible ink |
| `/!!!/Hello world/!!!/` | Upside-down text |
| `[[==>>]]`, `[[<<==]]`, `[[<=>>]]` | Directional arrows |
| `:check:`, `:rocket:` | Shortcodes |

## Docs and development

**[Open the full MDXL site](https://trail-b1az3r.github.io/mdxl/)**

- [Getting started guide](https://trail-b1az3r.github.io/mdxl/guide/)
- [Interactive syntax reference](https://trail-b1az3r.github.io/mdxl/syntax/)
- [Extended Markdown and GFM compatibility](https://trail-b1az3r.github.io/mdxl/markdown/)
- [Installation and troubleshooting](https://trail-b1az3r.github.io/mdxl/installation/)
- [Terminal, browser, and Kate renderers](https://trail-b1az3r.github.io/mdxl/renderers/)
- [Practical examples](https://trail-b1az3r.github.io/mdxl/examples/)
- [Project principles and contributing](https://trail-b1az3r.github.io/mdxl/about/)
- [Markdown syntax guide in the repository](docs/syntax.md)
- [Example document](demo.mdxl)

```bash
python3 -m pip install -r requirements-preview.txt
python3 -m unittest discover -s tests
cd website
npm install
npm run dev
npm run build
```

The GitHub Actions workflow tests the Python renderers and builds the Vite docs. Pushes to main deploy the site. In repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** if needed.

## License

[MIT](LICENSE).
