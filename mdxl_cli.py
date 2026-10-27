#!/usr/bin/env python3
"""MDXL terminal renderer — ANSI colors and Unicode, with no HTML dependency."""
import argparse
import re
from pathlib import Path

RESET = "\033[0m"
UPSIDE_DOWN = str.maketrans({
    "a":"ɐ","b":"q","c":"ɔ","d":"p","e":"ǝ","f":"ɟ","g":"ƃ","h":"ɥ","i":"ᴉ","j":"ɾ","k":"ʞ","l":"l","m":"ɯ","n":"u","o":"o","p":"d","q":"b","r":"ɹ","s":"s","t":"ʇ","u":"n","v":"ʌ","w":"ʍ","x":"x","y":"ʎ","z":"z",
    "A":"∀","B":"ᙠ","C":"Ɔ","D":"ᗡ","E":"Ǝ","F":"Ⅎ","G":"⅁","H":"H","I":"I","J":"ſ","K":"ʞ","L":"L","M":"W","N":"N","O":"O","P":"Ԁ","Q":"Ꝺ","R":"ɹ","S":"S","T":"┴","U":"∩","V":"Λ","W":"M","X":"X","Y":"⅄","Z":"Z",
    "0":"0","1":"Ɩ","2":"S","3":"Ɛ","4":"h","5":"ϛ","6":"9","7":"L","8":"8","9":"6",
    ".":"˙",",":"'","!":"¡","?":"¿","'":",",'"':"„","\u0060":",","&":"⅋",
    "[":"]","]":"[","(":")",")":"(","{":"}","}":"{","<":">",">":"<","*":"⁎","_":"‾",
})
EMOJI = {
    ":fire:":"🔥", ":check:":"✅", ":x:":"❌", ":warn:":"⚠️", ":skull:":"💀",
    ":heart:":"❤️", ":star:":"⭐", ":rocket:":"🚀", ":eyes:":"👀", ":think:":"🤔",
    ":party:":"🎉", ":bug:":"🐛", ":lock:":"🔒", ":bulb:":"💡", ":coffee:":"☕",
}
RAINBOW = [(255,0,0),(255,127,0),(255,200,0),(0,180,0),(0,120,255),(120,0,255),(210,0,180)]


def _rainbow(match):
    return "".join(
        f"\033[38;2;{r};{g};{b}m{char}{RESET}"
        for i, char in enumerate(match.group(1))
        for r, g, b in [RAINBOW[i % len(RAINBOW)]]
    )


def _bar(match):
    percent = max(0, min(100, int(match.group(1))))
    filled = percent // 10
    return f"\033[92m{'█' * filled}\033[90m{'░' * (10 - filled)}{RESET} {percent}%"


def _flip(match):
    lines = match.group(1).splitlines()
    return "\n".join(line.translate(UPSIDE_DOWN)[::-1] for line in reversed(lines))


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
ALERT_COLORS = {
    "NOTE": "\033[1;36m",
    "TIP": "\033[1;32m",
    "IMPORTANT": "\033[1;35m",
    "WARNING": "\033[1;33m",
    "CAUTION": "\033[1;31m",
}


def _visible_length(value):
    """Return a terminal string's length without counting ANSI control codes."""
    return len(ANSI_ESCAPE_RE.sub("", value))


def _split_table_row(line):
    """Split a Markdown table row while respecting escaped and code-span pipes."""
    source = line.strip()
    if source.startswith("|"):
        source = source[1:]
    if source.endswith("|") and not source.endswith(r"\|"):
        source = source[:-1]

    cells = []
    current = []
    in_code = False
    index = 0
    while index < len(source):
        char = source[index]
        if char == "\\" and index + 1 < len(source) and source[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if char == "\x60":
            in_code = not in_code
            current.append(char)
        elif char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def _render_gfm_tables(content):
    """Render simple GFM tables as aligned, bordered terminal text."""
    lines = content.splitlines()
    output = []
    index = 0
    trailing_newline = content.endswith(("\n", "\r"))

    while index < len(lines):
        if index + 1 >= len(lines) or "|" not in lines[index] or "|" not in lines[index + 1]:
            output.append(lines[index])
            index += 1
            continue

        headers = _split_table_row(lines[index])
        separators = _split_table_row(lines[index + 1])
        if (
            len(headers) < 2
            or len(headers) != len(separators)
            or not all(TABLE_SEPARATOR_RE.fullmatch(cell) for cell in separators)
        ):
            output.append(lines[index])
            index += 1
            continue

        alignments = []
        for cell in separators:
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append("center")
            elif cell.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")

        rows = []
        cursor = index + 2
        while cursor < len(lines) and "|" in lines[cursor]:
            row = _split_table_row(lines[cursor])
            if len(row) != len(headers):
                break
            rows.append(row)
            cursor += 1

        all_rows = [headers, *rows]
        widths = [
            max(_visible_length(row[column]) for row in all_rows)
            for column in range(len(headers))
        ]

        def border(fill):
            return "+" + "+".join(fill * (width + 2) for width in widths) + "+"

        def render_row(row):
            cells = []
            for column, cell in enumerate(row):
                padding = max(0, widths[column] - _visible_length(cell))
                alignment = alignments[column]
                if alignment == "right":
                    cell = (" " * padding) + cell
                elif alignment == "center":
                    left = padding // 2
                    cell = (" " * left) + cell + (" " * (padding - left))
                else:
                    cell = cell + (" " * padding)
                cells.append(" " + cell + " ")
            return "|" + "|".join(cells) + "|"

        output.append(border("-"))
        output.append(render_row(headers))
        output.append(border("="))
        output.extend(render_row(row) for row in rows)
        output.append(border("-"))
        index = cursor

    rendered = "\n".join(output)
    return rendered + ("\n" if trailing_newline else "")


def _render_gfm_alerts(content):
    """Turn GFM alert blockquotes into compact, color-labeled terminal callouts."""
    lines = content.splitlines()
    output = []
    index = 0
    trailing_newline = content.endswith(("\n", "\r"))
    alert_pattern = re.compile(r"^>[ \t]*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*$", re.IGNORECASE)

    while index < len(lines):
        match = alert_pattern.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue

        kind = match.group(1).upper()
        index += 1
        body = []
        while index < len(lines) and re.match(r"^>[ \t]?", lines[index]):
            body.append(re.sub(r"^>[ \t]?", "", lines[index], count=1))
            index += 1

        color = ALERT_COLORS[kind]
        label = f"{color}{kind}:{RESET}"
        if body:
            rendered_body = [label + " " + body[0]]
            rendered_body.extend("    " + line for line in body[1:])
            output.extend(rendered_body)
        else:
            output.append(label)

    rendered = "\n".join(output)
    return rendered + ("\n" if trailing_newline else "")


def render_terminal(content):
    """Render supported MDXL tokens in a plain-text document."""
    fenced = []
    mdxl_code_blocks = []

    def hold_fence(match):
        fenced.append(match.group(0))
        return f"MDXLTERMINALFENCE{len(fenced) - 1}TOKEN"

    content = re.sub(
        r"(?ms)^[ \t]*((?:`{3,4}(?!`)|~{3,}))[^\n]*\n.*?^[ \t]*\1[ \t]*$".replace("`", chr(96)),
        hold_fence, content,
    )
    # Keep five-backtick code literal until the rest of the renderer has finished.
    def hold_mdxl_code(match):
        mdxl_code_blocks.append(match.group(0))
        return f"MDXLTERMINALMDXLBLOCK{len(mdxl_code_blocks) - 1}TOKEN"

    content = re.sub(
        r"(?ms)^`{5}([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)^`{5}[ \t]*$".replace("`", chr(96)),
        hold_mdxl_code, content,
    )

    def color(match):
        text, hex_value = match.group(1), match.group(2)
        red, green, blue = (int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
        return f"\033[38;2;{red};{green};{blue}m{text}{RESET}"

    content = re.sub(r"/col//(.*?)/col#([0-9a-fA-F]{6})//", color, content, flags=re.DOTALL)
    content = re.sub(r"/rbw//(.*?)/rbw//", _rainbow, content, flags=re.DOTALL)
    content = re.sub(r"//hl//(.*?)//hl//", lambda m: f"\033[43;30m{m.group(1)}{RESET}", content, flags=re.DOTALL)
    content = re.sub(r"/red//(.*?)/red//", lambda m: f"\033[9m{m.group(1)}{RESET}", content, flags=re.DOTALL)
    content = re.sub(r"//key//(.*?)//key//", lambda m: f"\033[7m {m.group(1)} {RESET}", content, flags=re.DOTALL)
    content = re.sub(r"/bar//([0-9]{1,3})//", _bar, content)
    content = re.sub(r"/!!!/(.*?)/!!!/", _flip, content, flags=re.DOTALL)
    content = re.sub(r"\|\|\|\|\[(.*?)\]\|\|\|\|", lambda m: f"\033[30;40m{m.group(1)}{RESET}", content)
    content = content.replace("[[==>>]]", "\033[1;34m➜\033[0m")
    content = content.replace("[[<<==]]", "\033[1;34m⬅\033[0m")
    content = content.replace("[[<=>>]]", "\033[1;34m⇄\033[0m")
    content = re.sub(r":([a-z0-9_]+):", lambda m: EMOJI.get(m.group(0), m.group(0)), content)
    # Plain terminal equivalents for common GFM inline and checklist syntax.
    content = re.sub(
        r"(?m)^(\s*(?:[-+*]|\d+[.)])\s+)\[([ xX])\]\s+",
        lambda m: m.group(1) + (f"\033[92m[x]{RESET}" if m.group(2).strip() else "[ ]") + " ",
        content,
    )
    content = re.sub(
        r"(?<!~)~~(.+?)~~(?!~)",
        lambda m: f"\033[9m{m.group(1)}{RESET}",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(r"^-###\s(.*)$", rf"\033[2m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^-##\s(.*)$", rf"\033[2;1m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^-#\s(.*)$", rf"\033[1;4m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^####\s(.*)$", rf"\033[1;96m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^(#{1,6})\s(.*)$", rf"\033[1;97m\2{RESET}", content, flags=re.MULTILINE)
    content = _render_gfm_alerts(content)
    content = _render_gfm_tables(content)
    for index, block in enumerate(mdxl_code_blocks):
        content = content.replace(f"MDXLTERMINALMDXLBLOCK{index}TOKEN", f"\033[33m{block}{RESET}")
    for index, block in enumerate(fenced):
        content = content.replace(f"MDXLTERMINALFENCE{index}TOKEN", block)
    return content


def main():
    parser = argparse.ArgumentParser(description="Render MDXL syntax in the terminal.")
    parser.add_argument("file", type=Path, help="Path to a .mdxl document")
    parser.add_argument("--version", action="version", version="mdxl-cli 0.2.0")
    args = parser.parse_args()
    try:
        content = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(str(exc))
    print(render_terminal(content))


if __name__ == "__main__":
    main()
