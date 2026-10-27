#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
DATA_DIR="$HOME/.local/share/mdxl"
KATE_DIR="$HOME/.local/share/org.kde.syntax-highlighting/syntax"
MIME_PACKAGE_DIR="$HOME/.local/share/mime/packages"
VENV_DIR="$DATA_DIR/venv"

printf '\nMDXL installer\n===============\n'
command -v python3 >/dev/null 2>&1 || { echo "Error: Python 3 is required." >&2; exit 1; }
for file in mdxl_cli.py mdxl_preview.py mdxl.xml requirements-preview.txt data/mime/packages/mdxl.xml; do
    [[ -f "$SCRIPT_DIR/$file" ]] || { echo "Error: expected $file beside install.sh." >&2; exit 1; }
done

python3 -m py_compile "$SCRIPT_DIR/mdxl_cli.py" "$SCRIPT_DIR/mdxl_preview.py"
python3 - "$SCRIPT_DIR/mdxl.xml" "$SCRIPT_DIR/data/mime/packages/mdxl.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
for path in sys.argv[1:]:
    ET.parse(path)
PY
mkdir -p "$BIN_DIR" "$DATA_DIR" "$KATE_DIR" "$MIME_PACKAGE_DIR"
install -m 755 "$SCRIPT_DIR/mdxl_cli.py" "$BIN_DIR/mdxl-cli"
install -m 644 "$SCRIPT_DIR/mdxl_preview.py" "$DATA_DIR/mdxl_preview.py"
install -m 644 "$SCRIPT_DIR/requirements-preview.txt" "$DATA_DIR/requirements-preview.txt"
install -m 644 "$SCRIPT_DIR/mdxl.xml" "$KATE_DIR/mdxl.xml"
install -m 644 "$SCRIPT_DIR/data/mime/packages/mdxl.xml" "$MIME_PACKAGE_DIR/mdxl.xml"
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database "$HOME/.local/share/mime"
else
    printf 'Warning: update-mime-database is unavailable; install shared-mime-info and rerun install.sh to register the .mdxl file type.\n' >&2
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
elif command -v kbuildsycoca5 >/dev/null 2>&1; then
    kbuildsycoca5 --noincremental >/dev/null 2>&1 || true
fi
if [[ ! -x "$VENV_DIR/bin/python" ]]; then python3 -m venv "$VENV_DIR"; fi
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$DATA_DIR/requirements-preview.txt"

cat > "$BIN_DIR/mdxl-preview" <<'WRAPPER'
#!/usr/bin/env sh
exec "$HOME/.local/share/mdxl/venv/bin/python" "$HOME/.local/share/mdxl/mdxl_preview.py" "$@"
WRAPPER
chmod 755 "$BIN_DIR/mdxl-preview"

for startup in "$HOME/.profile" "$HOME/.bashrc" "$HOME/.zshrc"; do
    [[ -e "$startup" ]] || continue
    if ! grep -q 'MDXL_PATH_SETUP' "$startup"; then
        printf '\n# MDXL_PATH_SETUP\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$startup"
    fi
done
printf '\nInstallation complete.\n'
printf 'Terminal renderer: %s/mdxl-cli\nBrowser preview: %s/mdxl-preview\nKate syntax: %s/mdxl.xml\nMIME registration: %s/mdxl.xml\nFile type: text/x-mdxl (Markdown Extended Logic document)\n' "$BIN_DIR" "$BIN_DIR" "$KATE_DIR" "$MIME_PACKAGE_DIR"
printf 'Restart Kate and open a new terminal (or source your shell profile). If an already-open file still has generic highlighting, close and reopen it, or select Markdown Extended Logic under Tools > Mode.\n'
