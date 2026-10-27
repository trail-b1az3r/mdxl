# MDXL (Markdown Extended Logic)

**MDXL** (`.mdxl`) is a hyper-extended markdown specification designed to push the boundaries of plain-text documents natively. It builds upon GitHub Flavored Markdown (GFM) and introduces a suite of visual and executable custom syntaxes that render **natively in text editors and terminals** without relying on HTML, webviews, or browsers.

## 🚀 Zero-HTML Features

### 1. True Terminal Colors & Native Editor Highlighting
- **Syntax:** `/col// Text /col#RRGGBB//`
- **Terminal:** Renders using ANSI TrueColor escape codes.
- **Kate:** Natively highlights the tags and text using KSyntaxHighlighting.

### 2. Native Invisible Ink
- **Syntax:** `||||[Secret Text]||||`
- **Terminal:** Renders as black text on a black background. Highlight it with your mouse to reveal it.
- **Kate:** Natively masks the text by matching the foreground color to the background color.

### 3. Upside Down Text
- **Syntax:** `/!!!/ Text /!!!/`
- **Terminal:** Physically maps characters to their upside-down Unicode equivalents and reverses the string.

### 4. Micro-Headers
- `-# Super Small` (Dim/Bold)
- `-## Even Smaller` 
- `-### Smallest` 

### 5. Interactive Arrows
- `[[==>>]]` (Right), `[[<<==]]` (Left), `[[<=>>]]` (Both)
- Renders as bold Unicode arrows (`➜`, `⬅`, `⇄`) in both the terminal and editor.

### 6. Executable Code Blocks
- Use 5 backticks (```` ````` ````) to denote code meant for local execution (Python stdlib, Bash, Fish).

## 📦 Installation

```bash
chmod +x install.sh
./install.sh
```

## 🛠️ Usage

### 1. Native Terminal Rendering
View your document directly in the terminal with full ANSI color and Unicode flipping support:
```bash
mdxl-cli document.mdxl
```

### 2. Native Editor Support (Kate)
1. Restart Kate after running the install script.
2. Open any `.mdxl` file.
3. Kate will natively highlight the syntax, mask the invisible ink, and provide autocomplete popups for all MDXL tags as you type.

## 📄 Syntax Reference

| Syntax | Terminal Result | Kate Native Result |
| :--- | :--- | :--- |
| `-# Text` | Dim/Bold Text | Gray Bold Text |
| `/col// Text /col#FF0000//` | True Red Text | Highlighted Tags |
| `||||[Secret]||||` | Black-on-Black (Hidden) | Gray-on-Gray (Masked) |
| `/!!!/ Text /!!!/` | Flipped Unicode Text | Italic Magenta Text |
| `[[==>>]]` | Blue `➜` | Blue `➜` |

## 📝 License
[MIT](https://choosealicense.com/licenses/mit/)
