# Renderers and editor support

## Terminal renderer

`mdxl-cli <document.mdxl>` turns recognized tokens into ANSI colors and Unicode glyphs. It has no third-party dependencies and never executes code.

## Browser preview

`mdxl-preview <document.mdxl>` serves a local preview on `127.0.0.1` and refreshes on save. Available options include `--port`, `--no-open`, `--stdout`, and `--export`.

Export a static copy:

```bash
mdxl-preview demo.mdxl --export
mdxl-preview demo.mdxl --export ./demo.html
```

Five-backtick code blocks become copyable blocks; they are not executed. Source HTML tags are escaped to prevent them becoming active markup in the preview.

## Kate syntax

mdxl.xml declares the .mdxl extension, token highlighting, and completions for MDXL syntax. Run the installer and restart Kate to activate it.

## Documentation site

The website is a Vite + React app built with HeroUI. Actions tests the Python renderer, builds the static site, and deploys it to GitHub Pages when changes reach main. Site source lives in website/.
