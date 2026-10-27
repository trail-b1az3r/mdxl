# MDXL

**Markdown Extended Logic** adds expressive syntax to Markdown while keeping documents readable as plain text. Render the same .mdxl file in your terminal, preview it locally in a browser, or edit it in Kate with native syntax highlighting and completions.

[![Actions](https://github.com/trail-b1az3r/mdxl/actions/workflows/pages.yml/badge.svg)](https://github.com/trail-b1az3r/mdxl/actions/workflows/pages.yml)
[![MIT](https://img.shields.io/badge/license-MIT-9ee37d.svg)](LICENSE)

**[Open the docs and syntax showcase](https://trail-b1az3r.github.io/mdxl/)** · [Repository](https://github.com/trail-b1az3r/mdxl)

## Features

- True-color and rainbow text, highlights, redaction, keyboard keycaps, invisible ink, and upside-down text.
- Progress bars, interactive arrow glyphs, and shortcode replacements.
- Three micro-header levels (`-#`, `-##`, `-###`) plus the `####` subheading.
- Terminal rendering with mdxl-cli and browser rendering with mdxl-preview.
- Kate syntax highlighting and completion suggestions.
- Five-backtick code blocks are copyable in the preview. Code is never executed automatically.

## Install

On Linux, from a clone or downloaded repository:

```bash
chmod +x install.sh
./install.sh
```

The installer installs both commands under `~/.local/bin`, adds Kate syntax, and creates a private virtual environment for the preview dependency. It does not use administrator privileges or modify system Python packages. Restart Kate and open a new terminal after installation.

## Use

```bash
mdxl-cli demo.mdxl
mdxl-preview demo.mdxl
mdxl-preview demo.mdxl --export
mdxl-preview demo.mdxl --export ./demo.html
```

mdxl-preview opens a local preview and refreshes when the document changes. Useful options include --port 8420, --no-open, --stdout, and --export [path]. For manual setup of the preview dependency, run python3 -m pip install -r requirements-preview.txt.

## Syntax quick reference

| Syntax | Effect |
| --- | --- |
| `-# Heading`, `-## Heading`, `-### Heading` | Three micro-header levels |
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

- [Syntax reference](docs/syntax.md)
- [Installation and troubleshooting](docs/installation.md)
- [Renderers and editor support](docs/renderers.md)
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
