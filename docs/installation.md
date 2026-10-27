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

The installer places mdxl-cli and mdxl-preview under `~/.local/bin`, copies the Kate syntax definition, and creates an isolated virtual environment for the browser renderer. It does not require administrator privileges.

The installer adds `~/.local/bin` to existing .profile, .bashrc, and .zshrc files if missing. Open a new terminal after installing or update PATH manually.

## Troubleshooting

### Preview reports that Markdown is missing

Re-run the installer, or install the dependency manually:

```bash
python3 -m pip install -r requirements-preview.txt
```

The installer installs this dependency in MDXL's private virtual environment, not system Python.

### Kate does not highlight .mdxl files

Confirm `~/.local/share/org.kde.syntax-highlighting/syntax/mdxl.xml` exists, then restart Kate.

### Browser does not open

```bash
mdxl-preview demo.mdxl --no-open --port 8420
```

The server binds only to `127.0.0.1`. If the starting port is occupied, it tries the next nine ports.

## Remove MDXL

Remove `~/.local/bin/mdxl-cli` and `~/.local/bin/mdxl-preview`, the directory `~/.local/share/mdxl`, and `mdxl.xml` from the Kate user syntax directory. Remove the MDXL_PATH_SETUP block from shell startup files if you no longer need it.
