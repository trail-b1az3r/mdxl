#!/bin/bash
echo "======================================="
echo "  MDXL Pure Text Installer (v2)"
echo "======================================="

CLI_HEAD=$(head -c 5 mdxl_cli.py 2>/dev/null)
XML_HEAD=$(head -c 5 mdxl.xml 2>/dev/null)

# Auto-fix swapped file contents
if [ "$CLI_HEAD" = "<?xml" ] && [ "$XML_HEAD" = "#!/us" -o "$XML_HEAD" = "impor" ]; then
    echo "[!] Detected swapped contents between mdxl.xml and mdxl_cli.py — swapping back."
    mv mdxl_cli.py .mdxl_swap.tmp && mv mdxl.xml mdxl_cli.py && mv .mdxl_swap.tmp mdxl.xml
    CLI_HEAD=$(head -c 5 mdxl_cli.py); XML_HEAD=$(head -c 5 mdxl.xml)
fi

# Refuse to install garbage
if [ "$CLI_HEAD" = "<?xml" ]; then
    echo "[✗] mdxl_cli.py contains XML! Re-save the Python script as mdxl_cli.py and re-run."; exit 1
fi
if [ "$XML_HEAD" != "<?xml" ]; then
    echo "[✗] mdxl.xml does not start with an XML declaration! Re-save it and re-run."; exit 1
fi

KATE_SYNTAX_DIR="$HOME/.local/share/org.kde.syntax-highlighting/syntax"
mkdir -p "$KATE_SYNTAX_DIR"
cp mdxl.xml "$KATE_SYNTAX_DIR/"
echo "[✓] Kate native syntax installed"

mkdir -p "$HOME/.local/bin"
cp mdxl_cli.py "$HOME/.local/bin/mdxl-cli"
chmod +x "$HOME/.local/bin/mdxl-cli"

# Post-install sanity check
if ! head -1 "$HOME/.local/bin/mdxl-cli" | grep -q python3; then
    echo "[✗] Sanity check failed: installed mdxl-cli is not Python."; exit 1
fi
python3 -m py_compile "$HOME/.local/bin/mdxl-cli" 2>/dev/null && echo "[✓] mdxl-cli compiles cleanly"

echo ""
echo "======================================="
echo "  Installation Complete!"
echo "======================================="
echo "1. Restart Kate for highlighting + autocomplete."
echo "2. Run: mdxl-cli <file.mdxl>"
