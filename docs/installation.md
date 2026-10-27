# Installation and troubleshooting

## Requirements

- Python 3.9 or newer.
- A shell on Linux for the installer.
- Kate is optional and only required for native editor highlighting.

## Install

```bash
chmod +x install.sh
./install.sh
```

The installer places `mdxl-cli` and `mdxl-preview` under `~/.local/bin`, installs the **Markdown Extended Logic** Kate syntax definition, registers `*.mdxl` as `text/x-mdxl` in the user MIME database, and creates an isolated virtual environment for the browser renderer. It does not require administrator privileges. MIME registration is refreshed with `update-mime-database` when that command is installed.

The installer adds `~/.local/bin` to existing .profile, .bashrc, and .zshrc files if missing. Open a new terminal after installing or update PATH manually.

## Troubleshooting

### Preview reports that Markdown is missing

Re-run the installer, or install the dependency manually:

```bash
python3 -m pip install -r requirements-preview.txt
```

The installer installs this dependency in MDXL's private virtual environment, not system Python.

### Kate still treats .mdxl as plain text

Re-run `./install.sh`, then check that these two user-level files exist:

- `~/.local/share/org.kde.syntax-highlighting/syntax/mdxl.xml`
- `~/.local/share/mime/packages/mdxl.xml`

Check the registered MIME type with `xdg-mime query filetype your-file.mdxl`; it should report `text/x-mdxl`. If it reports something else, make sure `update-mime-database` (provided by `shared-mime-info`) is installed and rerun the installer. Restart Kate and reopen the document. You can also choose **Tools → Mode → Markup → Markdown Extended Logic** if Kate has not automatically switched the language mode.

### Browser does not open

```bash
mdxl-preview demo.mdxl --no-open --port 8420
```

The server binds only to `127.0.0.1`. If the starting port is occupied, it tries the next nine ports.

## Remove MDXL

Remove `~/.local/bin/mdxl-cli` and `~/.local/bin/mdxl-preview`, the directory `~/.local/share/mdxl`, `~/.local/share/org.kde.syntax-highlighting/syntax/mdxl.xml`, and `~/.local/share/mime/packages/mdxl.xml`. Then run `update-mime-database ~/.local/share/mime`. Remove the MDXL_PATH_SETUP block from shell startup files if you no longer need it.
