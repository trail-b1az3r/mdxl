# CTE — Concentrated Text Editor

CTE is a native Linux desktop editor for Markdown and MDXL (Markdown Extended Logic), designed for Arch Linux and packaged with pacman using the included PKGBUILD.

## Highlights

- **Edit and Render modes:** switch between plain-source editing and MDXL's browser-based renderer.
- **Multiple pages:** open multiple files in tabs, move tabs, create untitled pages, and save each independently.
- **Installed fonts:** the font picker reads fonts installed on the system through Qt.
- **Material 3 Expressive-inspired design:** large rounded surfaces, expressive pill-shaped controls, strong active states, and a restrained dynamic-accent palette inspired by Google's Android design language.
- **MDXL rendering:** uses the repository's existing renderer for MDXL tokens, GFM, Markdown Extra, formatted documents, and code presentation.
- **Unsaved-change protection:** tab close and app exit ask whether to save, discard, or cancel.
- **Desktop integration:** .desktop launcher and scalable icon; accepts file paths from the file manager.

## Build and install on Arch Linux

From a checkout of this branch:

```bash
makepkg -si
```

Or build a package without installing it:

```bash
makepkg
sudo pacman -U cte-mdxl-0.1.0-1-any.pkg.tar.zst
```

Required dependencies are declared in the PKGBUILD and installed by pacman. Do not run the app as root.

## Run

```bash
cte
cte ~/Documents/notes.mdxl
```

## Notes

- Render mode uses Qt WebEngine. MDXL's renderer is reused so syntax behavior stays aligned with the command-line/browser preview.
- Translation directives require a configured/available translation service; the standalone browser preview remains the most reliable workflow for network-backed translation.
- JavaScript code blocks are displayed using MDXL's renderer. The app does not grant snippets native-system access.
- This is an initial app implementation. Test the package on a current Arch Linux installation before publishing it to the AUR.
