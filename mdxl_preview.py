#!/usr/bin/env python3
"""MDXL browser preview with live reload and standalone HTML export."""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import markdown
    import bleach
    from bleach.css_sanitizer import CSSSanitizer
except ImportError:
    sys.exit("The preview requires Markdown, PyMdown Extensions, and Bleach. Install requirements-preview.txt or run ./install.sh.")

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
RAINBOW = ["#ff5f57", "#ff9f43", "#ffd166", "#72d572", "#4db6ff", "#9b8cff", "#ff78c4"]
RELOAD_JS = """
<script>
(() => { let previous = null; window.setInterval(async () => {
  try { const response = await fetch('/__mtime', {cache:'no-store'}); const current = await response.text();
    if (previous !== null && current !== previous) window.location.reload(); previous = current;
  } catch (_) {}
}, 800); })();
</script>
"""
PREVIEW_CSS = """
<style>
:root{color-scheme:dark;--bg:#10120f;--line:#2b312a;--text:#e9eee5;--muted:#a2ad9b;--lime:#c0f477;--blue:#79c7ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(70rem 35rem at 80% -20%,#283820 0%,transparent 55%),var(--bg);color:var(--text);font:16px/1.7 ui-sans-serif,system-ui,-apple-system,sans-serif}
article{max-width:900px;margin:0 auto;padding:clamp(24px,5vw,64px)}h1,h2,h3,h4{line-height:1.2;letter-spacing:-.025em}h1{font-size:clamp(2.1rem,5vw,3.6rem)}h2{margin-top:2em}.mdxl-micro-1,.mdxl-micro-2,.mdxl-micro-3{margin:.7em 0}.mdxl-micro-1{font-size:.92em;color:var(--lime)}.mdxl-micro-2{font-size:.8em;color:var(--muted)}.mdxl-micro-3{font-size:.7em;color:var(--muted);font-weight:500}.mdxl-micro-plus-1{margin:.65em 0;font-size:.66em;letter-spacing:.09em;color:var(--blue);font-weight:750;text-transform:uppercase}.mdxl-micro-plus-2{margin:.55em 0;font-size:.56em;letter-spacing:.13em;color:#c9baff;font-weight:750;text-transform:uppercase}.mdxl-striped-through{position:relative;display:inline-block;text-decoration:line-through;text-decoration-color:var(--lime);text-decoration-thickness:.14em}.mdxl-striped-through::after{content:"";position:absolute;left:-.02em;right:-.02em;top:50%;height:.22em;transform:translateY(-50%);background:repeating-linear-gradient(135deg,#c0f477 0 2px,#20291a 2px 4px);pointer-events:none;mix-blend-mode:screen}h4{font-size:1.2rem;color:var(--blue)}
a{color:var(--lime)}blockquote{border-left:3px solid var(--lime);padding-left:1rem;color:var(--muted)}hr{border:0;border-top:1px solid var(--line)}img{max-width:100%}
pre,code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}code{background:#242a22;padding:.12em .32em;border-radius:5px}pre{overflow:auto;padding:1rem 1.25rem;border:1px solid var(--line);border-radius:14px;background:#0b0d0b;color:#dcebd3}pre code{padding:0;background:none}
table{border-collapse:collapse;width:100%;display:block;overflow:auto}th,td{border:1px solid var(--line);padding:.55rem .75rem;text-align:left}th{background:#20271c}tr:nth-child(even){background:#141812}
.mdxl-color{font-weight:650}.mdxl-highlight{background:#d7fb81;color:#17210e;border-radius:4px;padding:.05em .25em}.mdxl-redact{text-decoration:line-through;text-decoration-thickness:2px;color:#98a093}.mdxl-key{display:inline-block;border:1px solid #5c6758;border-bottom-width:3px;border-radius:6px;background:#232a20;padding:.05em .45em;font-size:.88em;font-weight:650;white-space:pre-wrap}
.mdxl-rainbow span{font-weight:750}.mdxl-progress{display:inline-flex;vertical-align:middle;width:180px;max-width:60vw;height:10px;border:1px solid #4b5743;border-radius:99px;background:#272d24;overflow:hidden;margin:0 .45rem}.mdxl-progress span{display:block;background:var(--lime);border-radius:inherit}.mdxl-progress-label{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.88em}
.invisible-ink{display:inline-block;padding:0 .35em;border-radius:4px;background:#252a22;cursor:help;outline-offset:3px}.ink-char{color:transparent;background:#252a22;border-radius:2px;transition:color .18s ease,background .18s ease}.invisible-ink:hover .ink-char,.invisible-ink:focus .ink-char{color:#edf8e6;background:transparent}
.upside-down{display:inline-block;unicode-bidi:plaintext}.arrow{border:0;background:transparent;color:var(--blue);font-size:1.2em;font-weight:700;cursor:pointer;padding:0 .15em;border-radius:5px}.arrow:hover{background:#24313b}.exec-block{margin:1.25rem 0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#0b0d0b}.exec-header{display:flex;justify-content:space-between;align-items:center;padding:.55rem .8rem;color:var(--muted);background:#1a2018;border-bottom:1px solid var(--line);font:600 .78rem ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em}.copy-code{border:1px solid #45513d;background:#252f20;color:var(--lime);padding:.35rem .65rem;border-radius:7px;cursor:pointer;font:inherit;text-transform:none;letter-spacing:0}.exec-block pre{margin:0;border:0;border-radius:0}
ul.task-list{list-style:none;padding-left:1.25rem}.task-list-item{list-style:none;margin-left:-1.25rem}.task-list-item input[type=checkbox]{margin:0 .55rem .15rem 0;accent-color:var(--lime);vertical-align:middle}del{text-decoration:line-through;text-decoration-thickness:2px;color:#a2ad9b}ins{color:var(--lime);text-decoration:underline;text-decoration-style:dotted}abbr[title]{text-decoration:underline dotted;cursor:help}dl{margin:1rem 0}dt{font-weight:750;color:#e5efd9;margin-top:.8rem}dd{margin:.25rem 0 .75rem 1.5rem;color:var(--muted)}.footnote-ref,.footnote-backref{color:var(--lime);font-size:.8em}.footnote{border-top:1px solid var(--line);margin-top:2rem;padding-top:1rem;font-size:.9em;color:var(--muted)}.admonition{margin:1.2rem 0;border:1px solid #46553a;border-left:4px solid var(--lime);border-radius:5px 16px 16px 5px;padding:.85rem 1.1rem;background:#c0f4770b}.admonition>.admonition-title{font-weight:750;color:var(--lime);margin-bottom:.45rem}.admonition.tip{border-left-color:#88d1ff;background:#88d1ff0b}.admonition.tip>.admonition-title{color:#88d1ff}.admonition.important{border-left-color:#b8a2ff;background:#b8a2ff0b}.admonition.important>.admonition-title{color:#b8a2ff}.admonition.warning,.admonition.caution{border-left-color:#ffb86b;background:#ffb86b0b}.admonition.warning>.admonition-title,.admonition.caution>.admonition-title{color:#ffb86b}details{border:1px solid var(--line);border-radius:12px;padding:.75rem 1rem;margin:1rem 0;background:#181d16}details>summary{cursor:pointer;color:var(--lime);font-weight:700}details[open]>summary{margin-bottom:.6rem}mark{background:#d7fb81;color:#17210e;border-radius:4px;padding:0 .2em}sup,sub{line-height:0}
.exec-actions{display:flex;gap:7px;align-items:center}.run-code{border:1px solid #536a42;border-radius:7px;background:#253421;color:var(--lime);padding:.35rem .65rem;cursor:pointer;font:inherit;text-transform:none;letter-spacing:0}.exec-output:empty{display:none}.exec-output{border-top:1px solid var(--line);padding:0;background:#090b09}.exec-output iframe{display:block;width:100%;min-height:90px;border:0;background:#0b0d0b;color:#e9eee5}.mdxl-translation,.mdxl-joke-translation{margin:1.1rem 0;padding:1rem 1.1rem;border:1px solid #394632;border-left:4px solid var(--blue);border-radius:5px 14px 14px 5px;background:#88d1ff08}.mdxl-translation-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;font-weight:800;color:var(--blue);margin-bottom:.55rem}.translation-source{margin:.25rem 0 .75rem;border-left-color:#4b6654;font-size:.92em}.translate-action{padding:.45rem .8rem;border:1px solid #4c6040;border-radius:999px;background:#20291b;color:var(--lime);cursor:pointer;font:inherit;font-size:.82rem}.translate-action:disabled{opacity:.55;cursor:wait}.translation-output{margin-top:.75rem;white-space:pre-wrap;overflow-wrap:anywhere}.translation-output:empty{display:none}.translation-output[data-error="true"]{color:#ffb86b}.mdxl-joke-translation{border-left-color:#c9baff;background:#c9baff08}.mdxl-joke-translation .mdxl-translation-label{color:#c9baff}.mdxl-format{margin:1.6rem 0;padding:clamp(1.4rem,4vw,3rem);border:1px solid #424a3c;border-radius:6px;background:#f6f3eb;color:#282a25;font-family:Georgia,"Times New Roman",serif;line-height:1.85;box-shadow:0 16px 40px #0002}.mdxl-format-label{font:800 .62rem/1.4 ui-sans-serif,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#5d6d4c;border-bottom:1px solid #dedbcf;padding-bottom:.6rem;margin-bottom:1.25rem}.mdxl-format-headers{margin-bottom:1.8rem}.mdxl-format-header{min-height:1.4em}.mdxl-format-header-1{font-weight:700}.mdxl-format-body p{margin:.7rem 0}.mdxl-format-body a{color:#354d70}.mdxl-format-apa .mdxl-format-headers{text-align:center}.mdxl-format-apa .mdxl-format-header-1{margin-bottom:.6rem}.mdxl-format-mla .mdxl-format-headers{text-align:left}.mdxl-format-mla .mdxl-format-header-1{font-weight:400}.mdxl-format-mla .mdxl-format-body h1,.mdxl-format-mla .mdxl-format-body h2{text-align:center;font-size:1.15em;font-weight:400}.mdxl-format-ieee .mdxl-format-header-1{color:#294e79}.mdxl-format-chicago .mdxl-format-header-1{text-align:center;margin-bottom:1rem}.mdxl-format-harvard .mdxl-format-header-1{font-style:italic}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
</style>
"""




# //autoT//text//target language aliases. Translation uses the locally configured
# LibreTranslate endpoint; only source text explicitly marked with autoT is sent.
TRANSLATION_ALIASES = {
    "en": ("en", "English"), "english": ("en", "English"),
    "es": ("es", "Spanish"), "spanish": ("es", "Spanish"), "sp": ("es", "Spanish"),
    "sps": ("es", "Spanish (Spain)"), "spm": ("es", "Spanish (Mexico)"), "spansh": ("es", "Spanish"),
    "fr": ("fr", "French"), "french": ("fr", "French"),
    "de": ("de", "German"), "german": ("de", "German"),
    "it": ("it", "Italian"), "italian": ("it", "Italian"),
    "pt": ("pt", "Portuguese"), "portuguese": ("pt", "Portuguese"),
    "ru": ("ru", "Russian"), "russian": ("ru", "Russian"),
    "zh": ("zh", "Mandarin Chinese"), "mandarin": ("zh", "Mandarin Chinese"), "chinese": ("zh", "Mandarin Chinese"),
    "yue": ("yue", "Cantonese"), "cantonese": ("yue", "Cantonese"),
    "pl": ("pl", "Polish"), "polish": ("pl", "Polish"),
    "ja": ("ja", "Japanese"), "japanese": ("ja", "Japanese"),
    "ko": ("ko", "Korean"), "korean": ("ko", "Korean"),
    "ar": ("ar", "Arabic"), "arabic": ("ar", "Arabic"),
    "hi": ("hi", "Hindi"), "hindi": ("hi", "Hindi"),
    "nl": ("nl", "Dutch"), "dutch": ("nl", "Dutch"),
    "auto": ("auto", "Random language: Russian, Mandarin, Cantonese, or Polish"),
}
JOKE_ALIASES = {
    "joke1": "Pirate English", "pirate": "Pirate English",
    "joke2": "Archaic English", "oldenglish": "Archaic English",
    "joke3": "Early Modern English", "earlymodern": "Early Modern English",
    "joke4": "Shakespearean English", "shakespeare": "Shakespearean English",
    "joke5": "Corporate jargon", "corporate": "Corporate jargon",
    "joke6": "Noir detective", "noir": "Noir detective",
    "joke7": "Gen Z slang", "genz": "Gen Z slang",
}
AUTO_TRANSLATE_ALIASES = sorted((*TRANSLATION_ALIASES, *JOKE_ALIASES), key=len, reverse=True)
AUTO_TRANSLATE_RE = re.compile(
    r"//autoT//(.*?)//(" + "|".join(map(re.escape, AUTO_TRANSLATE_ALIASES)) + r")(?![A-Za-z0-9_-])",
    re.IGNORECASE | re.DOTALL,
)
FORMAT_HEADER_RE = re.compile(
    r"^>>>[ \t]*\[([A-Za-z][A-Za-z0-9_-]*)\]((?:\([^)\n]*\)){0,4})[ \t]*(.*)$"
)
FORMAT_LABELS = {
    "apa": "APA", "apa7": "APA 7", "mla": "MLA", "mla9": "MLA 9",
    "chicago": "Chicago", "ieee": "IEEE", "harvard": "Harvard",
    "turabian": "Turabian", "ama": "AMA", "generic": "Formatted document",
}
TRANSLATE_LANGUAGES = {"en", "es", "fr", "de", "it", "pt", "ru", "zh", "yue", "pl", "ja", "ko", "ar", "hi", "nl"}
DEFAULT_TRANSLATE_ENDPOINT = "https://translate.argosopentech.com/translate"
MAX_TRANSLATION_CHARS = 4000


def _replace_style_words(text, replacements):
    keys = sorted(replacements, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, keys)) + r")\b", re.IGNORECASE)

    def replace(match):
        replacement = replacements[match.group(0).lower()]
        if match.group(0).isupper():
            return replacement.upper()
        if match.group(0).istitle():
            return replacement.title()
        return replacement

    return pattern.sub(replace, text)


def _render_joke_style(text, alias):
    styles = {
        "joke1": {
            "hello":"ahoy", "hi":"ahoy", "friend":"matey", "friends":"mateys",
            "you":"ye", "your":"yer", "are":"be", "is":"be", "the":"th'",
            "and":"an'", "money":"booty", "yes":"aye", "no":"nay", "very":"mighty",
            "my":"me", "old":"weathered", "good":"fine",
        },
        "pirate": {
            "hello":"ahoy", "hi":"ahoy", "friend":"matey", "friends":"mateys",
            "you":"ye", "your":"yer", "are":"be", "is":"be", "the":"th'",
            "and":"an'", "money":"booty", "yes":"aye", "no":"nay", "very":"mighty",
            "my":"me", "old":"weathered", "good":"fine",
        },
        "joke2": {
            "you":"thou", "your":"thy", "yours":"thine", "are":"art", "is":"is",
            "do":"dost", "does":"doth", "have":"hast", "has":"hath", "before":"ere",
            "hello":"good morrow", "yes":"verily", "no":"nay", "please":"prithee",
            "because":"forsooth", "my":"mine", "friend":"good fellow",
        },
        "oldenglish": {
            "you":"thou", "your":"thy", "yours":"thine", "are":"art", "do":"dost",
            "does":"doth", "have":"hast", "has":"hath", "before":"ere",
            "hello":"good morrow", "yes":"verily", "no":"nay", "please":"prithee",
            "because":"forsooth", "my":"mine", "friend":"good fellow",
        },
        "joke3": {
            "hello":"good day", "hi":"good day", "you":"you", "very":"exceedingly",
            "get":"obtain", "start":"commence", "end":"conclude", "help":"assist",
            "use":"utilize", "about":"concerning", "buy":"purchase", "show":"display",
            "ask":"inquire", "before":"prior to", "after":"subsequent to",
        },
        "earlymodern": {
            "hello":"good day", "hi":"good day", "very":"exceedingly", "get":"obtain",
            "start":"commence", "end":"conclude", "help":"assist", "use":"utilize",
            "about":"concerning", "buy":"purchase", "show":"display", "ask":"inquire",
            "before":"prior to", "after":"subsequent to",
        },
        "joke4": {
            "hello":"good morrow", "hi":"hail", "you":"thou", "your":"thy", "are":"art",
            "is":"doth stand", "yes":"aye", "no":"nay", "friend":"noble soul",
            "very":"most wondrously", "because":"forsooth", "before":"ere",
        },
        "shakespeare": {
            "hello":"good morrow", "hi":"hail", "you":"thou", "your":"thy", "are":"art",
            "is":"doth stand", "yes":"aye", "no":"nay", "friend":"noble soul",
            "very":"most wondrously", "because":"forsooth", "before":"ere",
        },
        "joke5": {
            "use":"leverage", "help":"provide enablement for", "start":"align on",
            "finish":"drive to completion", "problem":"opportunity", "idea":"strategic initiative",
            "change":"pivot", "meeting":"sync", "plan":"roadmap", "ask":"action item",
            "good":"high-impact", "important":"mission-critical",
        },
        "corporate": {
            "use":"leverage", "help":"provide enablement for", "start":"align on",
            "finish":"drive to completion", "problem":"opportunity", "idea":"strategic initiative",
            "change":"pivot", "meeting":"sync", "plan":"roadmap", "ask":"action item",
            "good":"high-impact", "important":"mission-critical",
        },
        "joke6": {
            "hello":"listen, pal", "friend":"client", "problem":"case", "money":"dough",
            "police":"the law", "look":"take a long, hard look", "night":"the mean streets",
            "rain":"the city's tears", "good":"on the level", "bad":"dirty",
        },
        "noir": {
            "hello":"listen, pal", "friend":"client", "problem":"case", "money":"dough",
            "police":"the law", "look":"take a long, hard look", "night":"the mean streets",
            "rain":"the city's tears", "good":"on the level", "bad":"dirty",
        },
        "joke7": {
            "very":"low-key", "good":"fire", "great":"goated", "bad":"mid",
            "friend":"bestie", "friends":"besties", "understand":"get it",
            "amazing":"iconic", "really":"literally", "cool":"chill", "no":"nah",
            "yes":"yeah", "problem":"drama",
        },
        "genz": {
            "very":"low-key", "good":"fire", "great":"goated", "bad":"mid",
            "friend":"bestie", "friends":"besties", "understand":"get it",
            "amazing":"iconic", "really":"literally", "cool":"chill", "no":"nah",
            "yes":"yeah", "problem":"drama",
        },
    }
    transformed = _replace_style_words(text, styles.get(alias, {}))
    prefixes = {
        "joke1":"Arrr! ", "pirate":"Arrr! ", "joke2":"Verily, ", "oldenglish":"Verily, ",
        "joke3":"In formal terms, ", "earlymodern":"In formal terms, ",
        "joke4":"Hark! ", "shakespeare":"Hark! ", "joke5":"For strategic alignment: ",
        "corporate":"For strategic alignment: ", "joke6":"It was a dark night. ",
        "noir":"It was a dark night. ", "joke7":"No cap: ", "genz":"No cap: ",
    }
    return prefixes.get(alias, "") + transformed


def _render_translation_directives(content, translation_blocks):
    def replace(match):
        source = match.group(1).strip()
        alias = match.group(2).lower()
        index = len(translation_blocks)
        if alias in JOKE_ALIASES:
            label = JOKE_ALIASES[alias]
            result = _render_joke_style(source, alias)
            block = (
                '<div class="mdxl-joke-translation"><div class="mdxl-translation-label">'
                + html.escape(label) + '</div><p>' + html.escape(result) + '</p></div>'
            )
        else:
            code, label = TRANSLATION_ALIASES[alias]
            variant = alias if alias in {"sps", "spm"} else ""
            source_html = html.escape(source)
            block = (
                '<div class="mdxl-translation" data-target="' + html.escape(code, quote=True)
                + '" data-label="' + html.escape(label, quote=True)
                + '" data-variant="' + html.escape(variant, quote=True)
                + '" data-auto="true"><div class="mdxl-translation-label">Auto-translate · '
                + html.escape(label) + '</div><blockquote class="translation-source">'
                + source_html + '</blockquote><button type="button" class="translate-action">Translate again</button>'
                + '<div class="translation-output" role="status" aria-live="polite"></div></div>'
            )
        translation_blocks.append(block)
        return "\n\nMDXLTRANSLATIONBLOCK" + str(index) + "TOKEN\n\n"

    return AUTO_TRANSLATE_RE.sub(replace, content)


def _render_formatted_document(format_name, header_text, body_source):
    headers = re.findall(r"\(([^)\n]*)\)", header_text)[:4]
    normalized = format_name.lower()
    label = FORMAT_LABELS.get(normalized, format_name.upper())
    # The custom document wrapper uses the regular Markdown engine for its body.
    body_source = re.sub(r"(?m)^([ \t]*)>>[ \t]?(.*)$", r"\1> > \2", body_source)
    body_source = expand_gfm_alerts(body_source)
    body_html = markdown.markdown(
        body_source,
        extensions=[
            "extra", "sane_lists", "nl2br", "admonition",
            "pymdownx.tasklist", "pymdownx.tilde", "pymdownx.magiclink",
            "pymdownx.caret", "pymdownx.mark", "pymdownx.details",
        ],
        extension_configs={
            "pymdownx.tasklist": {"clickable_checkbox": False},
            "pymdownx.tilde": {"subscript": False, "delete": True, "smart_delete": True},
            "pymdownx.magiclink": {"repo_url_shorthand": False, "social_url_shorthand": False},
        },
    ) if body_source.strip() else ""
    header_html = "".join(
        '<div class="mdxl-format-header mdxl-format-header-' + str(index + 1) + '">'
        + html.escape(value.strip()) + '</div>'
        for index, value in enumerate(headers) if value.strip()
    )
    safe_format = re.sub(r"[^a-z0-9_-]", "", normalized) or "custom"
    return (
        '<section class="mdxl-format mdxl-format-' + safe_format + '" data-format="' + safe_format + '">'
        '<div class="mdxl-format-label">' + html.escape(label) + ' format</div>'
        '<header class="mdxl-format-headers">' + header_html + '</header>'
        '<div class="mdxl-format-body">' + body_html + '</div></section>'
    )


def _extract_formatted_documents(content, formatted_blocks):
    lines = content.splitlines()
    output = []
    index = 0
    while index < len(lines):
        match = FORMAT_HEADER_RE.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue
        format_name, header_text, first_body_line = match.groups()
        body_lines = [first_body_line] if first_body_line.strip() else []
        index += 1
        while index < len(lines) and not FORMAT_HEADER_RE.match(lines[index]):
            body_lines.append(lines[index])
            index += 1
        formatted_blocks.append(_render_formatted_document(format_name, header_text, "\n".join(body_lines).strip()))
        output.append("\nMDXLFORMATBLOCK" + str(len(formatted_blocks) - 1) + "TOKEN\n")
    return "\n".join(output)


def _translate_with_provider(text, target):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("No text was provided for translation.")
    if len(text) > MAX_TRANSLATION_CHARS:
        raise ValueError("Translation text is limited to 4,000 characters per block.")
    if target not in TRANSLATE_LANGUAGES:
        raise ValueError("Unsupported target language code.")
    endpoint = os.environ.get("MDXL_TRANSLATE_ENDPOINT", DEFAULT_TRANSLATE_ENDPOINT).strip()
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("MDXL_TRANSLATE_ENDPOINT must be an absolute HTTP or HTTPS URL.")
    payload = {"q": text, "source": "auto", "target": target, "format": "text"}
    api_key = os.environ.get("MDXL_TRANSLATE_API_KEY", "").strip()
    if api_key:
        payload["api_key"] = api_key
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read(1_000_000).decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError("Translation service rejected the request (HTTP " + str(error.code) + ").") from error
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("Could not reach the translation service. Check the endpoint and network connection.") from error
    translated = data.get("translatedText") if isinstance(data, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        raise RuntimeError("Translation service returned no translated text. The selected language may not be available.")
    return translated





TRANSLATION_ALIASES = {
    "en": ("en", "English"), "english": ("en", "English"),
    "es": ("es", "Spanish"), "spanish": ("es", "Spanish"), "sp": ("es", "Spanish"),
    "sps": ("es", "Spanish (Spain)"), "spm": ("es", "Spanish (Mexico)"), "spansh": ("es", "Spanish"),
    "fr": ("fr", "French"), "french": ("fr", "French"),
    "de": ("de", "German"), "german": ("de", "German"),
    "it": ("it", "Italian"), "italian": ("it", "Italian"),
    "pt": ("pt", "Portuguese"), "portuguese": ("pt", "Portuguese"),
    "ru": ("ru", "Russian"), "russian": ("ru", "Russian"),
    "zh": ("zh", "Mandarin Chinese"), "mandarin": ("zh", "Mandarin Chinese"), "chinese": ("zh", "Mandarin Chinese"),
    "yue": ("yue", "Cantonese"), "cantonese": ("yue", "Cantonese"),
    "pl": ("pl", "Polish"), "polish": ("pl", "Polish"),
    "ja": ("ja", "Japanese"), "japanese": ("ja", "Japanese"),
    "ko": ("ko", "Korean"), "korean": ("ko", "Korean"),
    "ar": ("ar", "Arabic"), "arabic": ("ar", "Arabic"),
    "hi": ("hi", "Hindi"), "hindi": ("hi", "Hindi"),
    "nl": ("nl", "Dutch"), "dutch": ("nl", "Dutch"),
    "auto": ("auto", "Random language: Russian, Mandarin, Cantonese, or Polish"),
}
JOKE_ALIASES = {
    "joke1": "Pirate English", "pirate": "Pirate English",
    "joke2": "Archaic English style", "oldenglish": "Archaic English style",
    "joke3": "Early Modern English style", "earlymodern": "Early Modern English style",
    "joke4": "Shakespearean English style", "shakespeare": "Shakespearean English style",
    "joke5": "Corporate jargon", "corporate": "Corporate jargon",
    "joke6": "Noir detective style", "noir": "Noir detective style",
    "joke7": "Gen Z slang", "genz": "Gen Z slang",
}
AUTO_TRANSLATE_ALIASES = sorted((*TRANSLATION_ALIASES, *JOKE_ALIASES), key=len, reverse=True)
AUTO_TRANSLATE_RE = re.compile(
    r"//autoT//(.*?)//(" + "|".join(map(re.escape, AUTO_TRANSLATE_ALIASES)) + r")(?![A-Za-z0-9_-])",
    re.IGNORECASE | re.DOTALL,
)
FORMAT_HEADER_RE = re.compile(r"^>>>[ \t]*\[([A-Za-z][A-Za-z0-9_-]*)\]((?:\([^)\n]*\)){0,4})[ \t]*(.*)$")
FORMAT_LABELS = {
    "apa": "APA", "apa7": "APA 7", "mla": "MLA", "mla9": "MLA 9",
    "chicago": "Chicago", "ieee": "IEEE", "harvard": "Harvard",
    "turabian": "Turabian", "ama": "AMA", "generic": "Formatted document",
}
TRANSLATE_LANGUAGES = {"en", "es", "fr", "de", "it", "pt", "ru", "zh", "yue", "pl", "ja", "ko", "ar", "hi", "nl"}
DEFAULT_TRANSLATE_ENDPOINT = "https://translate.argosopentech.com/translate"
MAX_TRANSLATION_CHARS = 4000


def _replace_style_words(text, replacements):
    keys = sorted(replacements, key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, keys)) + r")\b", re.IGNORECASE)

    def replace(match):
        replacement = replacements[match.group(0).lower()]
        if match.group(0).isupper():
            return replacement.upper()
        if match.group(0).istitle():
            return replacement.title()
        return replacement

    return pattern.sub(replace, text)


def _render_joke_style(text, alias):
    styles = {
        "joke1": {"hello":"ahoy","hi":"ahoy","friend":"matey","friends":"mateys","you":"ye","your":"yer","are":"be","is":"be","the":"th'","and":"an'","money":"booty","yes":"aye","no":"nay","very":"mighty","my":"me","good":"fine"},
        "pirate": {"hello":"ahoy","hi":"ahoy","friend":"matey","friends":"mateys","you":"ye","your":"yer","are":"be","is":"be","the":"th'","and":"an'","money":"booty","yes":"aye","no":"nay","very":"mighty","my":"me","good":"fine"},
        "joke2": {"you":"thou","your":"thy","yours":"thine","are":"art","do":"dost","does":"doth","have":"hast","has":"hath","before":"ere","hello":"good morrow","yes":"verily","no":"nay","please":"prithee","because":"forsooth","my":"mine","friend":"good fellow"},
        "oldenglish": {"you":"thou","your":"thy","yours":"thine","are":"art","do":"dost","does":"doth","have":"hast","has":"hath","before":"ere","hello":"good morrow","yes":"verily","no":"nay","please":"prithee","because":"forsooth","my":"mine","friend":"good fellow"},
        "joke3": {"hello":"good day","hi":"good day","very":"exceedingly","get":"obtain","start":"commence","end":"conclude","help":"assist","use":"utilize","about":"concerning","buy":"purchase","show":"display","ask":"inquire","before":"prior to","after":"subsequent to"},
        "earlymodern": {"hello":"good day","hi":"good day","very":"exceedingly","get":"obtain","start":"commence","end":"conclude","help":"assist","use":"utilize","about":"concerning","buy":"purchase","show":"display","ask":"inquire","before":"prior to","after":"subsequent to"},
        "joke4": {"hello":"good morrow","hi":"hail","you":"thou","your":"thy","are":"art","is":"doth stand","yes":"aye","no":"nay","friend":"noble soul","very":"most wondrously","because":"forsooth","before":"ere"},
        "shakespeare": {"hello":"good morrow","hi":"hail","you":"thou","your":"thy","are":"art","is":"doth stand","yes":"aye","no":"nay","friend":"noble soul","very":"most wondrously","because":"forsooth","before":"ere"},
        "joke5": {"use":"leverage","help":"provide enablement for","start":"align on","finish":"drive to completion","problem":"opportunity","idea":"strategic initiative","change":"pivot","meeting":"sync","plan":"roadmap","ask":"action item","good":"high-impact","important":"mission-critical"},
        "corporate": {"use":"leverage","help":"provide enablement for","start":"align on","finish":"drive to completion","problem":"opportunity","idea":"strategic initiative","change":"pivot","meeting":"sync","plan":"roadmap","ask":"action item","good":"high-impact","important":"mission-critical"},
        "joke6": {"hello":"listen, pal","friend":"client","problem":"case","money":"dough","police":"the law","look":"take a long, hard look","night":"the mean streets","rain":"the city's tears","good":"on the level","bad":"dirty"},
        "noir": {"hello":"listen, pal","friend":"client","problem":"case","money":"dough","police":"the law","look":"take a long, hard look","night":"the mean streets","rain":"the city's tears","good":"on the level","bad":"dirty"},
        "joke7": {"very":"low-key","good":"fire","great":"goated","bad":"mid","friend":"bestie","friends":"besties","understand":"get it","amazing":"iconic","really":"literally","cool":"chill","no":"nah","yes":"yeah","problem":"drama"},
        "genz": {"very":"low-key","good":"fire","great":"goated","bad":"mid","friend":"bestie","friends":"besties","understand":"get it","amazing":"iconic","really":"literally","cool":"chill","no":"nah","yes":"yeah","problem":"drama"},
    }
    prefixes = {
        "joke1":"Arrr! ", "pirate":"Arrr! ", "joke2":"Verily, ", "oldenglish":"Verily, ",
        "joke3":"In formal terms, ", "earlymodern":"In formal terms, ", "joke4":"Hark! ",
        "shakespeare":"Hark! ", "joke5":"For strategic alignment: ", "corporate":"For strategic alignment: ",
        "joke6":"It was a dark night. ", "noir":"It was a dark night. ", "joke7":"No cap: ", "genz":"No cap: ",
    }
    return prefixes.get(alias, "") + _replace_style_words(text, styles.get(alias, {}))


def _render_translation_directives(content, translation_blocks):
    def replace(match):
        source = match.group(1).strip()
        alias = match.group(2).lower()
        index = len(translation_blocks)
        if alias in JOKE_ALIASES:
            block = (
                '<div class="mdxl-joke-translation"><div class="mdxl-translation-label">'
                + html.escape(JOKE_ALIASES[alias]) + '</div><p>'
                + html.escape(_render_joke_style(source, alias)) + '</p></div>'
            )
        else:
            code, label = TRANSLATION_ALIASES[alias]
            variant = alias if alias in {"sps", "spm"} else ""
            block = (
                '<div class="mdxl-translation" data-target="' + html.escape(code, quote=True)
                + '" data-label="' + html.escape(label, quote=True)
                + '" data-variant="' + html.escape(variant, quote=True)
                + '" data-auto="true"><div class="mdxl-translation-label">Auto-translate · '
                + html.escape(label) + '</div><blockquote class="translation-source">'
                + html.escape(source) + '</blockquote><button type="button" class="translate-action">Translate again</button>'
                + '<div class="translation-output" role="status" aria-live="polite"></div></div>'
            )
        translation_blocks.append(block)
        return "\n\nMDXLTRANSLATIONBLOCK" + str(index) + "TOKEN\n\n"
    return AUTO_TRANSLATE_RE.sub(replace, content)


def _render_formatted_document(format_name, header_text, body_source):
    headers = re.findall(r"\(([^)\n]*)\)", header_text)[:4]
    normalized = format_name.lower()
    label = FORMAT_LABELS.get(normalized, format_name.upper())
    body_source = re.sub(r"(?m)^([ \t]*)>>[ \t]?(.*)$", r"\1> > \2", body_source)
    body_source = expand_gfm_alerts(body_source)
    body_html = markdown.markdown(
        body_source,
        extensions=["extra", "sane_lists", "nl2br", "admonition", "pymdownx.tasklist",
                    "pymdownx.tilde", "pymdownx.magiclink", "pymdownx.caret", "pymdownx.mark", "pymdownx.details"],
        extension_configs={
            "pymdownx.tasklist": {"clickable_checkbox": False},
            "pymdownx.tilde": {"subscript": False, "delete": True, "smart_delete": True},
            "pymdownx.magiclink": {"repo_url_shorthand": False, "social_url_shorthand": False},
        },
    ) if body_source.strip() else ""
    header_html = "".join(
        '<div class="mdxl-format-header mdxl-format-header-' + str(index + 1) + '">'
        + html.escape(value.strip()) + '</div>'
        for index, value in enumerate(headers) if value.strip()
    )
    safe_format = re.sub(r"[^a-z0-9_-]", "", normalized) or "custom"
    return (
        '<section class="mdxl-format mdxl-format-' + safe_format + '" data-format="' + safe_format + '">'
        '<div class="mdxl-format-label">' + html.escape(label) + ' format</div>'
        '<header class="mdxl-format-headers">' + header_html + '</header>'
        '<div class="mdxl-format-body">' + body_html + '</div></section>'
    )


def _extract_formatted_documents(content, formatted_blocks):
    lines = content.splitlines()
    output = []
    index = 0
    while index < len(lines):
        match = FORMAT_HEADER_RE.match(lines[index])
        if not match:
            output.append(lines[index])
            index += 1
            continue
        format_name, header_text, first_body_line = match.groups()
        body_lines = [first_body_line] if first_body_line.strip() else []
        index += 1
        while index < len(lines) and not FORMAT_HEADER_RE.match(lines[index]):
            body_lines.append(lines[index])
            index += 1
        formatted_blocks.append(_render_formatted_document(format_name, header_text, "\n".join(body_lines).strip()))
        output.append("\nMDXLFORMATBLOCK" + str(len(formatted_blocks) - 1) + "TOKEN\n")
    return "\n".join(output)


def _translate_with_provider(text, target):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("No text was provided for translation.")
    if len(text) > MAX_TRANSLATION_CHARS:
        raise ValueError("Translation text is limited to 4,000 characters per block.")
    if target not in TRANSLATE_LANGUAGES:
        raise ValueError("Unsupported target language code.")
    endpoint = os.environ.get("MDXL_TRANSLATE_ENDPOINT", DEFAULT_TRANSLATE_ENDPOINT).strip()
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("MDXL_TRANSLATE_ENDPOINT must be an absolute HTTP or HTTPS URL.")
    payload = {"q": text, "source": "auto", "target": target, "format": "text"}
    api_key = os.environ.get("MDXL_TRANSLATE_API_KEY", "").strip()
    if api_key:
        payload["api_key"] = api_key
    request = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read(1_000_000).decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError("Translation service rejected the request (HTTP " + str(error.code) + ").") from error
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("Could not reach the translation service. Check the endpoint and network connection.") from error
    translated = data.get("translatedText") if isinstance(data, dict) else None
    if not isinstance(translated, str) or not translated.strip():
        raise RuntimeError("Translation service returned no translated text. The selected language may not be available.")
    return translated



def escape_source_html(content):
    """Escape raw HTML tags so source documents cannot add active browser markup."""
    return re.sub(r"</?([A-Za-z][A-Za-z0-9-]*)(\s[^<>]*?)?/?>", lambda match: html.escape(match.group(0)), content)



def expand_gfm_alerts(content):
    """Translate GitHub-style > [!NOTE] callouts into safe Markdown admonitions."""
    def convert(match):
        lines = [re.sub(r"^\s*>\s?", "", line) for line in match.group(0).splitlines()]
        if not lines:
            return match.group(0)
        marker = re.fullmatch(r"\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", lines[0].strip(), flags=re.IGNORECASE)
        if not marker:
            return match.group(0)
        kind = marker.group(1).lower()
        title = kind.title()
        body_lines = lines[1:]
        indented = "\n".join(("    " + line) if line.strip() else "" for line in body_lines)
        if not indented.strip():
            return f'!!! {kind} "{title}"\n'
        return f'!!! {kind} "{title}"\n{indented}\n'

    return re.sub(r"(?m)(?:^>[^\n]*(?:\n|$))+", convert, content)


def sanitize_rendered_html(fragment):
    """Allow Markdown output while stripping unsafe elements, attributes, and URL schemes."""
    allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS) | {
        "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span", "section",
        "article", "blockquote", "hr", "br", "pre", "code", "del", "ins",
        "mark", "kbd", "sup", "sub", "ul", "ol", "li", "input", "table",
        "thead", "tbody", "tr", "th", "td", "dl", "dt", "dd", "abbr",
        "details", "summary", "label", "button",
    }
    safe_names = {
        "class", "id", "title", "href", "src", "alt", "width", "height",
        "colspan", "rowspan", "align", "start", "type", "checked", "disabled",
        "rel", "open", "role", "tabindex", "scope", "for", "data-arrow",
    }

    def allow_attribute(tag, name, value):
        if name in safe_names or name.startswith(("aria-", "data-")):
            return True
        if name == "style":
            return tag in {"span", "p", "h1", "h2", "h3", "h4", "h5", "h6", "th", "td"}
        return False

    cleaner = bleach.Cleaner(
        tags=allowed_tags,
        attributes=allow_attribute,
        protocols={"http", "https", "mailto", "ftp"},
        strip=True,
        css_sanitizer=CSSSanitizer(allowed_css_properties=["color", "width", "text-align", "background-color"]),
    )
    return cleaner.clean(fragment)

def render_mdxl(content, live=False):
    """Render MDXL, GitHub Flavored Markdown, and Markdown Extra safely."""
    code_blocks = []
    exec_blocks = []
    translation_blocks = []
    formatted_blocks = []

    def add_exec_block(lang, source):
        language = (lang or "text").strip() or "text"
        runnable = language.lower() in {"js", "javascript", "ecmascript"}
        run_button = '<button type="button" class="run-code">Run JavaScript</button>' if runnable else ""
        rendered = (
            '<div class="exec-block"><div class="exec-header"><span>' + html.escape(language)
            + '</span><div class="exec-actions"><button type="button" class="copy-code">Copy code</button>'
            + run_button + '</div></div><pre><code>' + html.escape(source)
            + '</code></pre><div class="exec-output" aria-live="polite"></div></div>'
        )
        exec_blocks.append(rendered)
        return "\n\nMDXLEXECBLOCK" + str(len(exec_blocks) - 1) + "TOKEN\n\n"

    def process_exec(match):
        return add_exec_block(match.group(1), match.group(2))

    content = re.sub(
        r"(?ms)^\x60{5}([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)^\x60{5}[ \t]*$",
        process_exec, content,
    )

    # JavaScript fences get an explicit Run button; code only executes after a click.
    content = re.sub(
        r"(?ms)^[ \t]*(\x60{3,4})(?:javascript|js)(?:[ \t]+(?:run|exec))?[ \t]*\n(.*?)^[ \t]*\1[ \t]*$",
        lambda match: add_exec_block("javascript", match.group(2)),
        content, flags=re.IGNORECASE,
    )

    def hold_fence(match):
        code_blocks.append(match.group(0))
        return "\n\nMDXLRAWBLOCK" + str(len(code_blocks) - 1) + "TOKEN\n\n"

    content = re.sub(
        r"(?ms)^[ \t]*(\x60{3,4}(?!\x60)|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$",
        hold_fence, content,
    )
    # Escape raw HTML only after protecting fenced code, so code remains readable.
    content = escape_source_html(content)
    content = _render_translation_directives(content, translation_blocks)
    # Four tildes create MDXL's striped-through effect; code fences are protected above.
    content = re.sub(
        r"(?<!~)~~~~([^\n]+?)~~~~(?!~)",
        lambda match: '<span class="mdxl-striped-through">' + match.group(1) + "</span>",
        content,
    )

    def colored(match):
        return '<span class="mdxl-color" style="color:#' + match.group(2) + '">' + html.escape(match.group(1)) + "</span>"

    content = re.sub(r"/col//(.*?)/col#([0-9a-fA-F]{6})//", colored, content, flags=re.DOTALL)

    def rainbow(match):
        return '<span class="mdxl-rainbow">' + "".join(
            '<span style="color:' + RAINBOW[index % len(RAINBOW)] + '">' + html.escape(char) + "</span>"
            for index, char in enumerate(match.group(1))
        ) + "</span>"

    content = re.sub(r"/rbw//(.*?)/rbw//", rainbow, content, flags=re.DOTALL)
    content = re.sub(r"//hl//(.*?)//hl//", lambda m: '<mark class="mdxl-highlight">' + html.escape(m.group(1)) + "</mark>", content, flags=re.DOTALL)
    content = re.sub(r"/red//(.*?)/red//", lambda m: '<del class="mdxl-redact">' + html.escape(m.group(1)) + "</del>", content, flags=re.DOTALL)
    content = re.sub(r"//key//(.*?)//key//", lambda m: '<kbd class="mdxl-key">' + html.escape(m.group(1)) + "</kbd>", content, flags=re.DOTALL)

    def progress(match):
        percent = max(0, min(100, int(match.group(1))))
        return ('<span class="mdxl-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'
                + str(percent) + '"><span style="width:' + str(percent) + '%"></span></span>'
                + '<span class="mdxl-progress-label">' + str(percent) + "%</span>")

    content = re.sub(r"/bar//([0-9]{1,3})//", progress, content)

    def invisible_ink(match):
        chars = "".join('<span class="ink-char">' + html.escape(char) + "</span>" for char in match.group(1))
        return '<span class="invisible-ink" tabindex="0" aria-label="Hidden text; hover or focus to reveal">' + chars + "</span>"

    content = re.sub(r"\|\|\|\|\[(.*?)\]\|\|\|\|", invisible_ink, content, flags=re.DOTALL)

    def upside_down(match):
        lines = match.group(1).splitlines()
        text = "\n".join(line.translate(UPSIDE_DOWN)[::-1] for line in reversed(lines))
        return '<span class="upside-down">' + html.escape(text) + "</span>"

    content = re.sub(r"/!!!/(.*?)/!!!/", upside_down, content, flags=re.DOTALL)
    for token, markup in {
        "[[==>>]]": '<button type="button" class="arrow" data-arrow="right" aria-label="Cycle arrow">➜</button>',
        "[[<<==]]": '<button type="button" class="arrow" data-arrow="left" aria-label="Cycle arrow">⬅</button>',
        "[[<=>>]]": '<button type="button" class="arrow" data-arrow="both" aria-label="Cycle arrow">⇄</button>',
    }.items():
        content = content.replace(token, markup)
    content = re.sub(r":([a-z0-9_]+):", lambda match: EMOJI.get(match.group(0), match.group(0)), content)
    content = re.sub(r"^(-#)\s(.*)$", r'<h5 class="mdxl-micro-1">\2</h5>', content, flags=re.MULTILINE)
    content = re.sub(r"^(-##)\s(.*)$", r'<h5 class="mdxl-micro-2">\2</h5>', content, flags=re.MULTILINE)
    content = re.sub(r"^(-###)\s(.*)$", r'<h5 class="mdxl-micro-3">\2</h5>', content, flags=re.MULTILINE)
    content = re.sub(r"^(\+\+#)\s(.*)$", r'<h5 class="mdxl-micro-plus-2">\2</h5>', content, flags=re.MULTILINE)
    content = re.sub(r"^(\+#)\s(.*)$", r'<h5 class="mdxl-micro-plus-1">\2</h5>', content, flags=re.MULTILINE)
    content = _extract_formatted_documents(content, formatted_blocks)
    # The formatted-document parser runs first so >>> headers are not mistaken for quotes.
    content = re.sub(r"(?m)^([ \t]*)>>[ \t]?(.*)$", r"\1> > \2", content)

    content = expand_gfm_alerts(content)
    body = markdown.markdown(
        content,
        extensions=[
            "extra",                 # Markdown Extra: tables, footnotes, definitions, abbreviations, heading attributes
            "sane_lists",
            "nl2br",
            "admonition",            # also used for GitHub-style alert blocks
            "pymdownx.tasklist",     # GFM [ ] and [x] task lists
            "pymdownx.tilde",        # GFM ~~strikethrough~~; subscript deliberately disabled
            "pymdownx.magiclink",     # bare URL and email autolinks
            "pymdownx.caret",        # superscript and inserted text
            "pymdownx.mark",         # ==highlight==
            "pymdownx.details",      # collapsible details blocks
            "toc",
        ],
        extension_configs={
            "pymdownx.tasklist": {"clickable_checkbox": False},
            "pymdownx.tilde": {"subscript": False, "delete": True, "smart_delete": True},
            "pymdownx.magiclink": {"repo_url_shorthand": False, "social_url_shorthand": False},
            "toc": {"permalink": True},
        },
    )
    for index, block in enumerate(code_blocks):
        marker = "MDXLRAWBLOCK" + str(index) + "TOKEN"
        rendered = markdown.markdown(block, extensions=["extra", "sane_lists"])
        body = body.replace("<p>" + marker + "</p>", rendered).replace(marker, rendered)
    for index, rendered in enumerate(exec_blocks):
        marker = "MDXLEXECBLOCK" + str(index) + "TOKEN"
        body = body.replace("<p>" + marker + "</p>", rendered).replace(marker, rendered)
    for index, rendered in enumerate(formatted_blocks):
        marker = "MDXLFORMATBLOCK" + str(index) + "TOKEN"
        body = body.replace("<p>" + marker + "</p>", rendered).replace(marker, rendered)
    for index, rendered in enumerate(translation_blocks):
        marker = "MDXLTRANSLATIONBLOCK" + str(index) + "TOKEN"
        body = body.replace("<p>" + marker + "</p>", rendered).replace(marker, rendered)
    body = sanitize_rendered_html(body)

    script = """
<script>
async function translateBox(box) {
  const output = box.querySelector('.translation-output');
  const button = box.querySelector('.translate-action');
  if (!output || !button) return;
  let target = box.dataset.target;
  let label = box.dataset.label || target;
  if (target === 'auto') {
    const choices = [['ru','Russian'],['zh','Mandarin Chinese'],['yue','Cantonese'],['pl','Polish']];
    const selected = choices[Math.floor(Math.random() * choices.length)];
    target = selected[0]; label = selected[1];
    box.dataset.target = target;
    box.dataset.label = label;
    box.querySelector('.mdxl-translation-label').textContent = 'Auto-translate · ' + label;
  }
  button.disabled = true;
  button.textContent = 'Translating…';
  output.dataset.error = 'false';
  output.textContent = 'Translating to ' + label + '…';
  try {
    const response = await fetch('/__translate', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({text: box.querySelector('.translation-source').textContent, target})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Translation request failed.');
    let translated = data.translatedText;
    const variant = box.dataset.variant;
    const swaps = variant === 'sps'
      ? [[/\bcomputadora\b/gi,'ordenador'],[/\bcelular\b/gi,'móvil'],[/\bcarro\b/gi,'coche'],[/\bplaticar\b/gi,'charlar']]
      : variant === 'spm'
        ? [[/\bordenador\b/gi,'computadora'],[/\bmóvil\b/gi,'celular'],[/\bcoche\b/gi,'carro'],[/\bcharlar\b/gi,'platicar']]
        : [];
    for (const [pattern,replacement] of swaps) translated = translated.replace(pattern, replacement);
    output.textContent = translated;
  } catch (error) {
    output.dataset.error = 'true';
    output.textContent = error.message + ' Configure MDXL_TRANSLATE_ENDPOINT for a supported LibreTranslate server.';
  } finally {
    button.disabled = false;
    button.textContent = 'Translate again';
  }
}
function runJavaScript(block) {
  const source = block.querySelector('code').textContent;
  const output = block.querySelector('.exec-output');
  output.replaceChildren();
  const frame = document.createElement('iframe');
  frame.setAttribute('sandbox', 'allow-scripts');
  frame.setAttribute('referrerpolicy', 'no-referrer');
  frame.title = 'Sandboxed JavaScript output';
  const policy = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src data:; form-action 'none'; base-uri 'none'";
  const scriptClose = '<' + '/script>';
  const safeCode = source.replace(new RegExp('<' + '/script', 'gi'), '<\\/' + 'script');
  const bootstrap = "const out=document.getElementById('output');const format=v=>{if(typeof v==='string')return v;try{return JSON.stringify(v)}catch(e){return String(v)}};console.log=(...a)=>{out.textContent+=a.map(format).join(' ')+'\\n'};console.error=(...a)=>{out.textContent+='Error: '+a.map(format).join(' ')+'\\n'};window.onerror=(m)=>{out.textContent+='Error: '+m+'\\n'};";
  frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="' + policy + '"><style>body{margin:0;padding:12px;background:#0b0d0b;color:#e9eee5;font:13px/1.6 ui-monospace,monospace}pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;color:#c0f477}</style></head><body><pre id="output"></pre><script>' + bootstrap + scriptClose + '<script>' + safeCode + '\n' + scriptClose + '</body></html>';
  output.appendChild(frame);
  window.setTimeout(() => {
    if (frame.isConnected) frame.srcdoc = '<!doctype html><body style="color:#ffb86b;background:#0b0d0b;font:13px monospace;padding:12px">Execution stopped after 10 seconds.</body>';
  }, 10000);
}
document.addEventListener('click', async (event) => {
  const arrow = event.target.closest('[data-arrow]');
  if (arrow) {
    const cycle = {right:['left','⬅'], left:['both','⇄'], both:['right','➜']};
    const next = cycle[arrow.dataset.arrow]; arrow.dataset.arrow = next[0]; arrow.textContent = next[1]; return;
  }
  const translationButton = event.target.closest('.translate-action');
  if (translationButton) { await translateBox(translationButton.closest('.mdxl-translation')); return; }
  const runButton = event.target.closest('.run-code');
  if (runButton) { runJavaScript(runButton.closest('.exec-block')); return; }
  const button = event.target.closest('.copy-code');
  if (button) {
    try { await navigator.clipboard.writeText(button.closest('.exec-block').querySelector('code').textContent);
      button.textContent = 'Copied'; window.setTimeout(() => {button.textContent='Copy code';}, 1200);
    } catch (_) { button.textContent = 'Select code to copy'; }
  }
});
document.querySelectorAll('.mdxl-translation[data-auto="true"]').forEach(box => translateBox(box));
</script>
"""
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<meta name='color-scheme' content='dark'><title>MDXL Preview</title>" + PREVIEW_CSS
            + "</head><body><article>" + body + "</article>" + script + (RELOAD_JS if live else "") + "</body></html>")


class MDXLHandler(BaseHTTPRequestHandler):
    mdxl_path = None

    def _send(self, status, content_type, payload):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/__mtime":
            try: modified = str(os.path.getmtime(self.mdxl_path))
            except OSError: modified = "0"
            self._send(200, "text/plain; charset=utf-8", modified.encode())
        elif self.path in ("/", "/index.html"):
            try: source = Path(self.mdxl_path).read_text(encoding="utf-8")
            except OSError as error:
                self._send(500, "text/plain; charset=utf-8", str(error).encode())
                return
            self._send(200, "text/html; charset=utf-8", render_mdxl(source, live=True).encode())
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def do_POST(self):
        if self.path != "/__translate":
            self._send(404, "application/json; charset=utf-8", b'{"error":"Not found."}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 32_000:
                raise ValueError("Request size is invalid.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object.")
            translated = _translate_with_provider(payload.get("text"), payload.get("target"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            response = {"error": str(error)}
            self._send(400, "application/json; charset=utf-8", json.dumps(response).encode("utf-8"))
            return
        except RuntimeError as error:
            response = {"error": str(error)}
            self._send(502, "application/json; charset=utf-8", json.dumps(response).encode("utf-8"))
            return
        self._send(200, "application/json; charset=utf-8", json.dumps({"translatedText": translated}).encode("utf-8"))

    def log_message(self, *_args):
        return


def serve(file_path, port=8420, open_browser=True):
    MDXLHandler.mdxl_path = str(Path(file_path).resolve())
    first_port = port
    server = None
    for candidate in range(first_port, first_port + 10):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), MDXLHandler)
            port = candidate
            break
        except OSError:
            continue
    if server is None:
        raise SystemExit(f"No free port in range {first_port}-{first_port + 9}.")
    url = f"http://127.0.0.1:{port}/"
    print(f"MDXL preview: {url}\nWatching: {MDXLHandler.mdxl_path}\nPress Ctrl+C to stop.")
    if open_browser: threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nPreview stopped.")
    finally: server.server_close()


def main():
    parser = argparse.ArgumentParser(description="Render an MDXL document in a browser.")
    parser.add_argument("file", type=Path, help="Path to a .mdxl document")
    parser.add_argument("--stdout", action="store_true", help="Print rendered HTML to stdout")
    parser.add_argument("--live", action="store_true", help="Enable save-and-refresh polling")
    parser.add_argument("--export", nargs="?", const="AUTO", help="Export standalone HTML instead of serving")
    parser.add_argument("--port", type=int, default=8420, help="Starting local port (default: 8420)")
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser window")
    args = parser.parse_args()
    if not args.file.is_file(): parser.error(f"file not found: {args.file}")
    source = args.file.read_text(encoding="utf-8")
    if args.stdout:
        print(render_mdxl(source))
    elif args.export:
        output = Path(args.export) if args.export != "AUTO" else args.file.with_suffix(".html")
        output.write_text(render_mdxl(source), encoding="utf-8")
        print(f"Exported: {output}")
    else:
        serve(args.file, args.port, not args.no_open)


if __name__ == "__main__":
    main()
