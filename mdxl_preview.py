#!/usr/bin/env python3
"""MDXL Engine with Kate In-App Support (--stdout) and Live Browser (--live)"""
import re, sys, os, html, argparse, threading, webbrowser
import markdown
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

RELOAD_JS = """
<script>
(function(){ let last=null; setInterval(async()=>{ try{ const r=await fetch('/__mtime'); const t=await r.text(); if(last===null){last=t;} else if(t!==last){location.reload();} }catch(e){} }, 800); })();
</script>
"""

def render_mdxl(content, live=False):
    exec_counter = 0
    def process_invisible_ink(match):
        text = match.group(1)
        letters = "".join(f'<span class="ink-char" style="transition-delay: {i*50}ms">{html.escape(c)}</span>' for i, c in enumerate(text))
        return f'<span class="invisible-ink">{letters}</span>'
    content = re.sub(r'\|\|\|\|\[(.*?)\]\|\|\|\|', process_invisible_ink, content)

    content = re.sub(r'/!!!/(.*?)/!!!/', lambda m: f'<span class="upside-down">{m.group(1)}</span>', content, flags=re.DOTALL)
    content = re.sub(r'/col//(.*?)/col#([0-9a-fA-F]{6})//', lambda m: f'<span style="color: #{m.group(2)}">{html.escape(m.group(1))}</span>', content, flags=re.DOTALL)

    content = content.replace('[[==>>]]', '<span class="arrow right" onclick="flipArrow(this)" style="cursor:pointer;">➜</span>')
    content = content.replace('[[<<==]]', '<span class="arrow left" onclick="flipArrow(this)" style="cursor:pointer;">⬅</span>')
    content = content.replace('[[<=>>]]', '<span class="arrow both" onclick="flipArrow(this)" style="cursor:pointer;">⇄</span>')

    content = re.sub(r'^(-#)\s(.*)$', r'<h1 class="mdxl-h1">\2</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^(-##)\s(.*)$', r'<h2 class="mdxl-h2">\2</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^(-###)\s(.*)$', r'<h3 class="mdxl-h3">\2</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^(####)\s(.*)$', r'<h4 class="mdxl-h4">\2</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^>> (.*)$', r'> > \1', content, flags=re.MULTILINE)

    def process_exec(match):
        nonlocal exec_counter; exec_counter += 1
        lang = match.group(1).strip() if match.group(1) else "text"
        code = html.escape(match.group(2))
        cid = f"exec_code_{exec_counter}"
        return (f'<div class="exec-block"><div class="exec-header">{lang} '
                f'<button onclick="runCode(this, \'{lang}\', \'{cid}\')">Run</button></div>'
                f'<pre><code id="{cid}" class="language-{lang}">{code}</code></pre></div>')
    content = re.sub(r'^`````([a-zA-Z]+)?\n(.*?)^`````', process_exec, content, flags=re.MULTILINE|re.DOTALL)

    body = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])
    css = """
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #222; }
        .mdxl-h4 { font-size: 1.2em; color: #555; margin: .5em 0; }
        .mdxl-h1 { font-size: .9em; color: #777; margin: .2em 0; }
        .mdxl-h2 { font-size: .7em; color: #999; margin: .1em 0; }
        .mdxl-h3 { font-size: .5em; color: #aaa; margin: .1em 0; }
        .upside-down { display: inline-block; transform: rotate(180deg); }
        .arrow { font-weight: bold; color: #007bff; font-size: 1.2em; user-select: none; }
        .invisible-ink { background: #333; padding: 0 4px; border-radius: 4px; cursor: pointer; display: inline-block; }
        .ink-char { transition: color .2s ease, background .2s ease; color: transparent; background: #333; padding: 0 1px; border-radius: 2px; }
        .invisible-ink:hover .ink-char { color: #000; background: transparent; }
        .exec-block { border: 1px solid #ddd; border-radius: 6px; margin: 15px 0; overflow: hidden; }
        .exec-header { background: #f5f5f5; padding: 8px 12px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
        .exec-header button { background: #28a745; color: white; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; }
        pre { margin: 0; padding: 15px; background: #2d2d2d; color: #f8f8f2; overflow-x: auto; }
        table { border-collapse: collapse; margin: 12px 0; } th, td { border: 1px solid #bbb; padding: 6px 12px; } th { background: #eee; }
    </style>"""
    js = """
    <script>
    function flipArrow(el){ if (el.innerHTML.includes('➜')) { el.innerHTML='⬅'; el.classList.replace('right','left'); } else if (el.innerHTML.includes('⬅')) { el.innerHTML='⇄'; el.classList.replace('left','both'); } else { el.innerHTML='➜'; el.classList.replace('both','right'); } }
    function runCode(btn, lang, codeId){ const code = document.getElementById(codeId).innerText; if (lang === 'python') { alert("Executing Python locally...\\n\\n" + code); btn.innerText = "Executed"; } else if (lang === 'bash' || lang === 'fish') { alert("Executing " + lang + " locally...\\n\\n" + code); btn.innerText = "Executed"; } else { alert("Language not supported."); } }
    </script>"""
    if live: js += RELOAD_JS
    return f"<html><head><meta charset='utf-8'><title>MDXL</title>{css}</head><body>{body}{js}</body></html>"

class MDXLHandler(BaseHTTPRequestHandler):
    mdxl_path = None
    def _send(self, code, ctype, payload):
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(payload)
    def do_GET(self):
        if self.path == '/__mtime':
            try: m = str(os.path.getmtime(self.mdxl_path))
            except OSError: m = '0'
            self._send(200, 'text/plain', m.encode())
        elif self.path in ('/', '/index.html'):
            with open(self.mdxl_path, encoding='utf-8') as f: self._send(200, 'text/html; charset=utf-8', render_mdxl(f.read(), live=True).encode('utf-8'))
        else: self._send(404, 'text/plain', b'Not found')
    def log_message(self, *a): pass

def serve(mdxl_path, port, open_browser):
    MDXLHandler.mdxl_path = os.path.abspath(mdxl_path)
    httpd = None
    for p in range(port, port + 10):
        try: httpd = ThreadingHTTPServer(('127.0.0.1', p), MDXLHandler); port = p; break
        except OSError: continue
    url = f'http://127.0.0.1:{port}/'
    print(f'MDXL live preview → {url}')
    if open_browser: threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try: httpd.serve_forever()
    except KeyboardInterrupt: print('\nStopped.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--stdout', action='store_true', help='Print HTML to stdout (for Kate Tool View)')
    ap.add_argument('--live', action='store_true', help='Start local server with auto-reload')
    ap.add_argument('--export', nargs='?', const='AUTO', help='Write static .html file')
    ap.add_argument('--port', type=int, default=8420)
    args = ap.parse_args()

    if not os.path.exists(args.file): sys.exit(f'FileNotFoundError: {args.file}')
    with open(args.file, encoding='utf-8') as f: content = f.read()

    if args.stdout:
        print(render_mdxl(content))
    elif args.live:
        serve(args.file, args.port, True)
    elif args.export:
        out = args.export if args.export != 'AUTO' else os.path.splitext(args.file)[0] + '.html'
        with open(out, 'w', encoding='utf-8') as f: f.write(render_mdxl(content))
        print(f'Generated: {out}')
    else:
        serve(args.file, args.port, True)
