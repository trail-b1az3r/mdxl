#!/usr/bin/env python3
"""MDXL terminal renderer — ANSI colors and Unicode, with no HTML dependency."""
import argparse
import re
from pathlib import Path

RESET = "\033[0m"
UPSIDE_DOWN = str.maketrans({
    "a":"ɐ","b":"q","c":"ɔ","d":"p","e":"ǝ","f":"ɟ","g":"ƃ","h":"ɥ","i":"ᴉ","j":"ɾ","k":"ʞ","l":"l","m":"ɯ","n":"u","o":"o","p":"d","q":"b","r":"ɹ","s":"s","t":"ʇ","u":"n","v":"ʌ","w":"ʍ","x":"x","y":"ʎ","z":"z",
    "A":"∀","B":"ᙠ","C":"Ɔ","D":"ᗡ","E":"Ǝ","F":"Ⅎ","G":"⅁","H":"H","I":"I","J":"ſ","K":"ʞ","L":"˥","M":"W","N":"N","O":"O","P":"Ԁ","Q":"Ꝺ","R":"ɹ","S":"S","T":"┴","U":"∩","V":"Λ","W":"M","X":"X","Y":"⅄","Z":"Z",
    "0":"0","1":"Ɩ","2":"ᄅ","3":"Ɛ","4":"ㄣ","5":"ϛ","6":"9","7":"ㄥ","8":"8","9":"6",
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


def render_terminal(content):
    """Render supported MDXL tokens in a plain-text document."""
    fenced = []

    def hold_fence(match):
        fenced.append(match.group(0))
        return f"MDXLTERMINALFENCE{len(fenced) - 1}TOKEN"

    content = re.sub(
        r"(?ms)^[ \t]*((?:`{3,4}(?!`)|~{3,}))[^\n]*\n.*?^[ \t]*\1[ \t]*$".replace("`", chr(96)),
        hold_fence, content,
    )
    # Five-backtick MDXL blocks receive terminal emphasis and are never executed.
    content = re.sub(
        r"(?ms)^`{5}([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)^`{5}[ \t]*$".replace("`", chr(96)),
        lambda match: f"\033[33m{match.group(0)}{RESET}", content,
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
    content = re.sub(r"^-###\s(.*)$", rf"\033[2m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^-##\s(.*)$", rf"\033[2;1m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^-#\s(.*)$", rf"\033[1;4m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^####\s(.*)$", rf"\033[1;96m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^(#{1,6})\s(.*)$", rf"\033[1;97m\2{RESET}", content, flags=re.MULTILINE)
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
