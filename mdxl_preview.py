#!/usr/bin/env python3
"""MDXL browser preview with live reload and standalone HTML export."""
import argparse
import html
import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("The preview requires Python Markdown. Install requirements-preview.txt or run ./install.sh.")

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
article{max-width:900px;margin:0 auto;padding:clamp(24px,5vw,64px)}h1,h2,h3,h4{line-height:1.2;letter-spacing:-.025em}h1{font-size:clamp(2.1rem,5vw,3.6rem)}h2{margin-top:2em}.mdxl-micro-1,.mdxl-micro-2,.mdxl-micro-3{margin:.7em 0}.mdxl-micro-1{font-size:.92em;color:var(--lime)}.mdxl-micro-2{font-size:.8em;color:var(--muted)}.mdxl-micro-3{font-size:.7em;color:var(--muted);font-weight:500}h4{font-size:1.2rem;color:var(--blue)}
a{color:var(--lime)}blockquote{border-left:3px solid var(--lime);padding-left:1rem;color:var(--muted)}hr{border:0;border-top:1px solid var(--line)}img{max-width:100%}
pre,code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}code{background:#242a22;padding:.12em .32em;border-radius:5px}pre{overflow:auto;padding:1rem 1.25rem;border:1px solid var(--line);border-radius:14px;background:#0b0d0b;color:#dcebd3}pre code{padding:0;background:none}
table{border-collapse:collapse;width:100%;display:block;overflow:auto}th,td{border:1px solid var(--line);padding:.55rem .75rem;text-align:left}th{background:#20271c}tr:nth-child(even){background:#141812}
.mdxl-color{font-weight:650}.mdxl-highlight{background:#d7fb81;color:#17210e;border-radius:4px;padding:.05em .25em}.mdxl-redact{text-decoration:line-through;text-decoration-thickness:2px;color:#98a093}.mdxl-key{display:inline-block;border:1px solid #5c6758;border-bottom-width:3px;border-radius:6px;background:#232a20;padding:.05em .45em;font-size:.88em;font-weight:650;white-space:pre-wrap}
.mdxl-rainbow span{font-weight:750}.mdxl-progress{display:inline-flex;vertical-align:middle;width:180px;max-width:60vw;height:10px;border:1px solid #4b5743;border-radius:99px;background:#272d24;overflow:hidden;margin:0 .45rem}.mdxl-progress span{display:block;background:var(--lime);border-radius:inherit}.mdxl-progress-label{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.88em}
.invisible-ink{display:inline-block;padding:0 .35em;border-radius:4px;background:#252a22;cursor:help;outline-offset:3px}.ink-char{color:transparent;background:#252a22;border-radius:2px;transition:color .18s ease,background .18s ease}.invisible-ink:hover .ink-char,.invisible-ink:focus .ink-char{color:#edf8e6;background:transparent}
.upside-down{display:inline-block;unicode-bidi:plaintext}.arrow{border:0;background:transparent;color:var(--blue);font-size:1.2em;font-weight:700;cursor:pointer;padding:0 .15em;border-radius:5px}.arrow:hover{background:#24313b}.exec-block{margin:1.25rem 0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#0b0d0b}.exec-header{display:flex;justify-content:space-between;align-items:center;padding:.55rem .8rem;color:var(--muted);background:#1a2018;border-bottom:1px solid var(--line);font:600 .78rem ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em}.copy-code{border:1px solid #45513d;background:#252f20;color:var(--lime);padding:.35rem .65rem;border-radius:7px;cursor:pointer;font:inherit;text-transform:none;letter-spacing:0}.exec-block pre{margin:0;border:0;border-radius:0}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
</style>
"""


def escape_source_html(content):
    """Escape raw HTML tags so source documents cannot add active browser markup."""
    return re.sub(r"</?([A-Za-z][A-Za-z0-9-]*)(\s[^<>]*?)?/?>", lambda match: html.escape(match.group(0)), content)


def render_mdxl(content, live=False):
    """Render MDXL syntax and Markdown into a self-contained HTML document."""
    content = escape_source_html(content)
    code_blocks = []

    def process_exec(match):
        lang = (match.group(1) or "text").strip() or "text"
        return ('<div class="exec-block"><div class="exec-header"><span>' + html.escape(lang)
                + '</span><button type="button" class="copy-code">Copy code</button></div><pre><code>'
                + html.escape(match.group(2)) + '</code></pre></div>')

    content = re.sub(
        r"(?ms)^`{5}([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)^`{5}[ \t]*$".replace("`", chr(96)),
        process_exec, content,
    )

    def hold_fence(match):
        code_blocks.append(match.group(0))
        return "\n\nMDXLRAWBLOCK" + str(len(code_blocks) - 1) + "TOKEN\n\n"

    content = re.sub(
        r"(?ms)^[ \t]*(`{3,4}(?!`)|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$".replace("`", chr(96)),
        hold_fence, content,
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

    body = markdown.markdown(content, extensions=["fenced_code", "tables", "nl2br", "sane_lists"])
    for index, block in enumerate(code_blocks):
        marker = "MDXLRAWBLOCK" + str(index) + "TOKEN"
        rendered = markdown.markdown(block, extensions=["fenced_code"])
        body = body.replace("<p>" + marker + "</p>", rendered).replace(marker, rendered)

    script = """
<script>
document.addEventListener('click', async (event) => {
  const arrow = event.target.closest('[data-arrow]');
  if (arrow) {
    const cycle = {right:['left','⬅'], left:['both','⇄'], both:['right','➜']};
    const next = cycle[arrow.dataset.arrow]; arrow.dataset.arrow = next[0]; arrow.textContent = next[1]; return;
  }
  const button = event.target.closest('.copy-code');
  if (button) {
    try { await navigator.clipboard.writeText(button.closest('.exec-block').querySelector('code').textContent);
      button.textContent = 'Copied'; window.setTimeout(() => {button.textContent='Copy code';}, 1200);
    } catch (_) { button.textContent = 'Select code to copy'; }
  }
});
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
