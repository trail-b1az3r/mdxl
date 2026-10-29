# CTE — Concentrated Text Editor

CTE is a native Linux desktop editor for Markdown and MDXL (Markdown Extended Logic), built with a Qt Quick/QML interface and a Python backend. It is packaged for Arch Linux and pacman.

## Features

- **Edit and Render modes:** switch between the source editor and the MDXL HTML renderer.
- **Multiple pages:** open and edit multiple files in tabs, create new documents, save and save as.
- **Live counts:** word and character counts update immediately as the active document changes.
- **Installed fonts:** the system font picker changes the QML editor font and injects a matching font-family override into rendered MDXL. Code remains monospace for readability.
- **MDXL compatibility:** uses the repository renderer for MDXL tokens, GFM, Markdown Extra, formatted documents and code presentation.
- **Unsaved-change protection:** prompts before closing modified tabs or exiting.
- **Desktop integration:** .desktop launcher, scalable icon and file-manager path support.

## Build and install on Arch Linux

Once this version is merged into main, run:

    git clone https://github.com/trail-b1az3r/mdxl.git
    cd mdxl/cte
    makepkg -si

To build a package without installing it, run makepkg in the same directory. The generated package can then be installed with sudo pacman -U cte-mdxl-0.1.0-1-any.pkg.tar.zst.

The PKGBUILD declares PySide6, Qt 6 Declarative/Quick, Qt WebEngine and the Python renderer dependencies. Do not run CTE as root.

## Run

    cte
    cte ~/Documents/notes.mdxl

## Implementation notes

- cte/main.qml contains the desktop UI.
- cte/cte.py provides the QML-facing document model, file operations, word/character counts, installed-font enumeration, render HTML and status.
- mdxl_preview.py remains the canonical Markdown/MDXL renderer; the QML WebEngineView displays its output.
- Translation directives depend on an available/configured translation service. JavaScript examples remain inside MDXL's sandboxed renderer; the app does not grant them native-system access.
- The package and CI checks should be tested against a current Arch Linux desktop before any AUR publication.
