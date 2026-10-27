#!/bin/bash

echo "======================================="
echo "  MDXL (Markdown XL) Installer"
echo "======================================="

# 1. Install Kate Syntax Definition
KATE_SYNTAX_DIR="$HOME/.local/share/org.kde.syntax-highlighting/syntax"
mkdir -p "$KATE_SYNTAX_DIR"
cp mdxl.xml "$KATE_SYNTAX_DIR/"
echo "[✓] Installed Kate syntax to $KATE_SYNTAX_DIR"

# 2. Install Python Preview Script
mkdir -p "$HOME/.local/bin"
cp mdxl_preview.py "$HOME/.local/bin/mdxl-preview"
chmod +x "$HOME/.local/bin/mdxl-preview"
echo "[✓] Installed preview tool to $HOME/.local/bin/mdxl-preview"

# 2. Install Terminal CLI
mkdir -p "$HOME/.local/bin"
cp mdxl_cli.py "$HOME/.local/bin/mdxl-cli"
chmod +x "$HOME/.local/bin/mdxl-cli"
echo "[✓] Installed terminal renderer to $HOME/.local/bin/mdxl-cli"

# 3. Install Python Dependencies
echo "[ ] Installing Python 'markdown' package..."
pip install markdown --user --quiet --break-system-packages
echo "[✓] Python dependencies installed"

# 4. Add to PATH if missing
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding $HOME/.local/bin to PATH in .bashrc and .zshrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi
echo ""
echo "======================================="
echo "  Installation Complete!"
echo "======================================="
echo "1. Restart Kate to apply native highlighting and autocomplete."
echo "2. Run: mdxl-cli <file.mdxl> to view it in the terminal."
