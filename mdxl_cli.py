#!/usr/bin/env python3
"""MDXL terminal renderer — ANSI colors and Unicode, with no HTML dependency."""
import argparse
import json
import os
import random
import re
import urllib.error
import urllib.parse
import urllib.request
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




TRANSLATION_TARGETS = {
    "en": ("en","English"), "english": ("en","English"),
    "es": ("es","Spanish"), "spanish": ("es","Spanish"), "sp": ("es","Spanish"),
    "sps": ("es","Spanish (Spain)"), "spm": ("es","Spanish (Mexico)"), "spansh": ("es","Spanish"),
    "fr": ("fr","French"), "french": ("fr","French"),
    "de": ("de","German"), "german": ("de","German"),
    "it": ("it","Italian"), "italian": ("it","Italian"),
    "pt": ("pt","Portuguese"), "portuguese": ("pt","Portuguese"),
    "ru": ("ru","Russian"), "russian": ("ru","Russian"),
    "zh": ("zh","Mandarin Chinese"), "mandarin": ("zh","Mandarin Chinese"), "chinese": ("zh","Mandarin Chinese"),
    "yue": ("yue","Cantonese"), "cantonese": ("yue","Cantonese"),
    "pl": ("pl","Polish"), "polish": ("pl","Polish"),
    "ja": ("ja","Japanese"), "japanese": ("ja","Japanese"),
    "ko": ("ko","Korean"), "korean": ("ko","Korean"),
    "ar": ("ar","Arabic"), "arabic": ("ar","Arabic"),
    "hi": ("hi","Hindi"), "hindi": ("hi","Hindi"),
    "nl": ("nl","Dutch"), "dutch": ("nl","Dutch"),
    "auto": ("auto","Random language"),
}
JOKE_NAMES = {
    "joke1":"Pirate English","pirate":"Pirate English",
    "joke2":"Archaic English style","oldenglish":"Archaic English style",
    "joke3":"Early Modern English style","earlymodern":"Early Modern English style",
    "joke4":"Shakespearean English style","shakespeare":"Shakespearean English style",
    "joke5":"Corporate jargon","corporate":"Corporate jargon",
    "joke6":"Noir detective style","noir":"Noir detective style",
    "joke7":"Gen Z slang","genz":"Gen Z slang",
}
TRANSLATION_RE = re.compile(
    r"//autoT//(.*?)//(" + "|".join(map(re.escape, sorted((*TRANSLATION_TARGETS, *JOKE_NAMES), key=len, reverse=True))) + r")(?![A-Za-z0-9_-])",
    re.IGNORECASE | re.DOTALL,
)
TRANSLATE_ENDPOINT = "https://translate.argosopentech.com/translate"


def _joke_translation(text, alias):
    styles = {
        "joke1":{"hello":"ahoy","hi":"ahoy","friend":"matey","friends":"mateys","you":"ye","your":"yer","are":"be","is":"be","the":"th'","and":"an'","money":"booty","yes":"aye","no":"nay","very":"mighty","good":"fine"},
        "pirate":{"hello":"ahoy","hi":"ahoy","friend":"matey","friends":"mateys","you":"ye","your":"yer","are":"be","is":"be","the":"th'","and":"an'","money":"booty","yes":"aye","no":"nay","very":"mighty","good":"fine"},
        "joke2":{"you":"thou","your":"thy","yours":"thine","are":"art","do":"dost","does":"doth","have":"hast","has":"hath","before":"ere","hello":"good morrow","yes":"verily","no":"nay","please":"prithee","because":"forsooth"},
        "oldenglish":{"you":"thou","your":"thy","yours":"thine","are":"art","do":"dost","does":"doth","have":"hast","has":"hath","before":"ere","hello":"good morrow","yes":"verily","no":"nay","please":"prithee","because":"forsooth"},
        "joke3":{"hello":"good day","hi":"good day","very":"exceedingly","get":"obtain","start":"commence","end":"conclude","help":"assist","use":"utilize","about":"concerning","buy":"purchase","show":"display","ask":"inquire","before":"prior to"},
        "earlymodern":{"hello":"good day","hi":"good day","very":"exceedingly","get":"obtain","start":"commence","end":"conclude","help":"assist","use":"utilize","about":"concerning","buy":"purchase","show":"display","ask":"inquire","before":"prior to"},
        "joke4":{"hello":"good morrow","hi":"hail","you":"thou","your":"thy","are":"art","yes":"aye","no":"nay","friend":"noble soul","because":"forsooth"},
        "shakespeare":{"hello":"good morrow","hi":"hail","you":"thou","your":"thy","are":"art","yes":"aye","no":"nay","friend":"noble soul","because":"forsooth"},
        "joke5":{"use":"leverage","help":"provide enablement for","start":"align on","finish":"drive to completion","problem":"opportunity","idea":"strategic initiative","change":"pivot","meeting":"sync","plan":"roadmap","ask":"action item"},
        "corporate":{"use":"leverage","help":"provide enablement for","start":"align on","finish":"drive to completion","problem":"opportunity","idea":"strategic initiative","change":"pivot","meeting":"sync","plan":"roadmap","ask":"action item"},
        "joke6":{"hello":"listen, pal","friend":"client","problem":"case","money":"dough","police":"the law","night":"the mean streets","good":"on the level","bad":"dirty"},
        "noir":{"hello":"listen, pal","friend":"client","problem":"case","money":"dough","police":"the law","night":"the mean streets","good":"on the level","bad":"dirty"},
        "joke7":{"very":"low-key","good":"fire","great":"goated","bad":"mid","friend":"bestie","friends":"besties","amazing":"iconic","really":"literally","cool":"chill","no":"nah","yes":"yeah"},
        "genz":{"very":"low-key","good":"fire","great":"goated","bad":"mid","friend":"bestie","friends":"besties","amazing":"iconic","really":"literally","cool":"chill","no":"nah","yes":"yeah"},
    }
    replacements = styles.get(alias, {})
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, sorted(replacements, key=len, reverse=True))) + r")\b", re.IGNORECASE) if replacements else None
    if pattern:
        def replace(match):
            value = replacements[match.group(0).lower()]
            return value.upper() if match.group(0).isupper() else value.title() if match.group(0).istitle() else value
        text = pattern.sub(replace, text)
    prefixes = {
        "joke1":"Arrr! ","pirate":"Arrr! ","joke2":"Verily, ","oldenglish":"Verily, ",
        "joke3":"In formal terms, ","earlymodern":"In formal terms, ","joke4":"Hark! ","shakespeare":"Hark! ",
        "joke5":"For strategic alignment: ","corporate":"For strategic alignment: ",
        "joke6":"It was a dark night. ","noir":"It was a dark night. ","joke7":"No cap: ","genz":"No cap: ",
    }
    return prefixes.get(alias, "") + text


def _online_translation(text, target, variant=""):
    code, label = TRANSLATION_TARGETS[target]
    if code == "auto":
        code, label = random.choice([("ru","Russian"),("zh","Mandarin Chinese"),("yue","Cantonese"),("pl","Polish")])
    if len(text) > 4000:
        raise ValueError("translation blocks are limited to 4,000 characters")
    endpoint = os.environ.get("MDXL_TRANSLATE_ENDPOINT", TRANSLATE_ENDPOINT).strip()
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("MDXL_TRANSLATE_ENDPOINT must be an HTTP or HTTPS URL")
    payload = {"q": text, "source": "auto", "target": code, "format": "text"}
    api_key = os.environ.get("MDXL_TRANSLATE_API_KEY", "").strip()
    if api_key:
        payload["api_key"] = api_key
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type":"application/json","Accept":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read(1_000_000).decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("translation service unavailable") from error
    translated = data.get("translatedText") if isinstance(data, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        raise RuntimeError("translation service returned no text")
    if variant == "sps":
        translated = re.sub(r"\bcomputadora\b","ordenador",translated,flags=re.IGNORECASE)
        translated = re.sub(r"\bcelular\b","móvil",translated,flags=re.IGNORECASE)
        translated = re.sub(r"\bcarro\b","coche",translated,flags=re.IGNORECASE)
    elif variant == "spm":
        translated = re.sub(r"\bordenador\b","computadora",translated,flags=re.IGNORECASE)
        translated = re.sub(r"\bmóvil\b","celular",translated,flags=re.IGNORECASE)
        translated = re.sub(r"\bcoche\b","carro",translated,flags=re.IGNORECASE)
    return label, translated


def _render_translations(content):
    def replace(match):
        source = match.group(1).strip()
        alias = match.group(2).lower()
        if alias in JOKE_NAMES:
            text = _joke_translation(source, alias)
            return f"\033[1;35m[{JOKE_NAMES[alias]}]\033[0m {text}"
        try:
            label, text = _online_translation(source, alias, alias if alias in {"sps","spm"} else "")
            return f"\033[1;36m[{label}]\033[0m {text}"
        except (ValueError, RuntimeError) as error:
            return f"\033[33m[translation unavailable: {error}]\033[0m {source}"
    return TRANSLATION_RE.sub(replace, content)


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
    content = _render_translations(content)
    # Plain terminal equivalents for common GFM inline and checklist syntax.
    content = re.sub(
        r"(?m)^(\s*(?:[-+*]|\d+[.)])\s+)\[([ xX])\]\s+",
        lambda m: m.group(1) + (f"\033[92m[x]{RESET}" if m.group(2).strip() else "[ ]") + " ",
        content,
    )
    # Four tildes use an alternating-color strikethrough as a terminal-safe striped approximation.
    content = re.sub(
        r"(?<!~)~~~~([^\n]+?)~~~~(?!~)",
        lambda m: "".join(f"\033[9;{36 if i % 2 == 0 else 35}m{char}{RESET}" for i, char in enumerate(m.group(1))),
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
    content = re.sub(r"^\+\+#\s(.*)$", rf"\033[2;35m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"^\+#\s(.*)$", rf"\033[1;35m\1{RESET}", content, flags=re.MULTILINE)
    content = re.sub(r"(?m)^([ \t]*)>>[ \t]?(.*)$", r"\1│   │ \2", content)
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
