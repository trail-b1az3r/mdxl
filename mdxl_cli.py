#!/usr/bin/env python3
"""MDXL Pure Terminal Renderer v2 — ANSI + Unicode only. Zero HTML."""
import re, sys

RESET = "\033[0m"

UPSIDE_DOWN = str.maketrans({
    'a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ','i':'ᴉ','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d','q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x','y':'ʎ','z':'z',
    'A':'∀','B':'ᙠ','C':'Ɔ','D':'ᗡ','E':'Ǝ','F':'Ⅎ','G':'⅁','H':'H','I':'I','J':'ſ','K':'ʞ','L':'˥','M':'W','N':'N','O':'O','P':'Ԁ','Q':'Ꝺ','R':'ɹ','S':'S','T':'┴','U':'∩','V':'Λ','W':'M','X':'X','Y':'⅄','Z':'Z',
    '0':'0','1':'Ɩ','2':'ᄅ','3':'Ɛ','4':'ㄣ','5':'ϛ','6':'9','7':'ㄥ','8':'8','9':'6',
    '.':'˙', ',':'\'', '!':'¡', '?':'¿', '\'':',', '"':'„', '`':',', '&':'⅋',
    '[':']', ']':'[', '(':')', ')':'(', '{':'}', '}':'{', '<':'>', '>':'<', '*':'⁎', '_':'‾',
})

EMOJI = {
    ':fire:':'🔥', ':check:':'✅', ':x:':'❌', ':warn:':'⚠️', ':skull:':'💀',
    ':heart:':'❤️', ':star:':'⭐', ':rocket:':'🚀', ':eyes:':'👀', ':think:':'🤔',
    ':party:':'🎉', ':bug:':'🐛', ':lock:':'🔒', ':bulb:':'💡', ':coffee:':'☕',
}

RAINBOW = [(255,0,0),(255,127,0),(255,200,0),(0,180,0),(0,120,255),(120,0,255),(210,0,180)]

def _rainbow(m):
    return "".join(f"\033[38;2;{RAINBOW[i % 7][0]};{RAINBOW[i % 7][1]};{RAINBOW[i % 7][2]}m{ch}{RESET}"
                   for i, ch in enumerate(m.group(1)))

def _bar(m):
    pct = max(0, min(100, int(m.group(1))))
    filled = pct // 10
    return f"\033[92m{'█'*filled}\033[90m{'░'*(10-filled)}{RESET} {pct}%"

def render_terminal(content):
    # Executable code blocks -> yellow
    content = re.sub(r'^`````([a-zA-Z]+)?\n(.*?)^`````', lambda m: f"\033[33m{m.group(0)}{RESET}", content, flags=re.MULTILINE|re.DOTALL)
    # /col// text /col#RRGGBB// -> ANSI TrueColor
    def _col(m):
        h = m.group(2)
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"\033[38;2;{r};{g};{b}m{m.group(1)}{RESET}"
    content = re.sub(r'/col//(.*?)/col#([0-9a-fA-F]{6})//', _col, content, flags=re.DOTALL)
    # NEW: rainbow
    content = re.sub(r'/rbw//(.*?)/rbw//', _rainbow, content, flags=re.DOTALL)
    # NEW: highlighter
    content = re.sub(r'//hl//(.*?)//hl//', lambda m: f"\033[43;30m{m.group(1)}{RESET}", content, flags=re.DOTALL)
    # NEW: redacted strikethrough
    content = re.sub(r'/red//(.*?)/red//', lambda m: f"\033[9m{m.group(1)}{RESET}", content, flags=re.DOTALL)
    # NEW: keycaps
    content = re.sub(r'//key//(.*?)//key//', lambda m: f"\033[7m {m.group(1)} {RESET}", content, flags=re.DOTALL)
    # NEW: progress bars
    content = re.sub(r'/bar//([0-9]{1,3})//', _bar, content)
    # Upside down
    def _flip(m):
        lines = m.group(1).split('\n')
        return '\n'.join(l.translate(UPSIDE_DOWN)[::-1] for l in lines)[::-1]
    content = re.sub(r'/!!!/(.*?)/!!!/', _flip, content, flags=re.DOTALL)
    # Invisible ink (black on black)
    content = re.sub(r'\|\|\|\|\[(.*?)\]\|\|\|\|', lambda m: f"\033[30;40m{m.group(1)}{RESET}", content)
    # Arrows
    content = content.replace('[[==>>]]', '\033[1;34m➜\033[0m')
    content = content.replace('[[<<==]]', '\033[1;34m⬅\033[0m')
    content = content.replace('[[<=>>]]', '\033[1;34m⇄\033[0m')
    # NEW: emoji shortcodes
    content = re.sub(r':([a-z0-9_]+):', lambda m: EMOJI.get(m.group(0), m.group(0)), content)
    # Micro headers + standard headers
    content = re.sub(r'^-###\s(.*)$', rf'\033[2m\1{RESET}', content, flags=re.MULTILINE)
    content = re.sub(r'^-##\s(.*)$',  rf'\033[2;1m\1{RESET}', content, flags=re.MULTILINE)
    content = re.sub(r'^-#\s(.*)$',   rf'\033[1;4m\1{RESET}', content, flags=re.MULTILINE)
    content = re.sub(r'^(#{1,6})\s(.*)$', rf'\033[1;97m\2{RESET}', content, flags=re.MULTILINE)
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mdxl-cli <file.mdxl>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        print(render_terminal(f.read()))#!/usr/bin/env python3
        """MDXL Pure Terminal Renderer v2 — ANSI + Unicode only. Zero HTML."""
        import re, sys
        
        RESET = "\033[0m"
        
        UPSIDE_DOWN = str.maketrans(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?\'"`&[](){}<>*_',
            'ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀qƆpƎℲפHIſʞWNOԀbɹS┴∩ΛMXZ0ƖƐㄣϛ9ㄥ86˙\'¡¿,,„⅋][)(}{><⁎‾'
        )
        
        EMOJI = {
            ':fire:':'🔥', ':check:':'✅', ':x:':'❌', ':warn:':'⚠️', ':skull:':'💀',
            ':heart:':'❤️', ':star:':'⭐', ':rocket:':'🚀', ':eyes:':'👀', ':think:':'🤔',
            ':party:':'🎉', ':bug:':'🐛', ':lock:':'🔒', ':bulb:':'💡', ':coffee:':'☕',
        }
        
        RAINBOW = [(255,0,0),(255,127,0),(255,200,0),(0,180,0),(0,120,255),(120,0,255),(210,0,180)]
        
        def _rainbow(m):
            return "".join(f"\033[38;2;{RAINBOW[i % 7][0]};{RAINBOW[i % 7][1]};{RAINBOW[i % 7][2]}m{ch}{RESET}"
                           for i, ch in enumerate(m.group(1)))
        
        def _bar(m):
            pct = max(0, min(100, int(m.group(1))))
            filled = pct // 10
            return f"\033[92m{'█'*filled}\033[90m{'░'*(10-filled)}{RESET} {pct}%"
        
        def render_terminal(content):
            # Executable code blocks -> yellow
            content = re.sub(r'^`````([a-zA-Z]+)?\n(.*?)^`````', lambda m: f"\033[33m{m.group(0)}{RESET}", content, flags=re.MULTILINE|re.DOTALL)
            # /col// text /col#RRGGBB// -> ANSI TrueColor
            def _col(m):
                h = m.group(2)
                r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
                return f"\033[38;2;{r};{g};{b}m{m.group(1)}{RESET}"
            content = re.sub(r'/col//(.*?)/col#([0-9a-fA-F]{6})//', _col, content, flags=re.DOTALL)
            # NEW: rainbow
            content = re.sub(r'/rbw//(.*?)/rbw//', _rainbow, content, flags=re.DOTALL)
            # NEW: highlighter
            content = re.sub(r'//hl//(.*?)//hl//', lambda m: f"\033[43;30m{m.group(1)}{RESET}", content, flags=re.DOTALL)
            # NEW: redacted strikethrough
            content = re.sub(r'/red//(.*?)/red//', lambda m: f"\033[9m{m.group(1)}{RESET}", content, flags=re.DOTALL)
            # NEW: keycaps
            content = re.sub(r'//key//(.*?)//key//', lambda m: f"\033[7m {m.group(1)} {RESET}", content, flags=re.DOTALL)
            # NEW: progress bars
            content = re.sub(r'/bar//([0-9]{1,3})//', _bar, content)
            # Upside down
            def _flip(m):
                lines = m.group(1).split('\n')
                return '\n'.join(l.translate(UPSIDE_DOWN)[::-1] for l in lines)[::-1]
            content = re.sub(r'/!!!/(.*?)/!!!/', _flip, content, flags=re.DOTALL)
            # Invisible ink (black on black)
            content = re.sub(r'\|\|\|\|\[(.*?)\]\|\|\|\|', lambda m: f"\033[30;40m{m.group(1)}{RESET}", content)
            # Arrows
            content = content.replace('[[==>>]]', '\033[1;34m➜\033[0m')
            content = content.replace('[[<<==]]', '\033[1;34m⬅\033[0m')
            content = content.replace('[[<=>>]]', '\033[1;34m⇄\033[0m')
            # NEW: emoji shortcodes
            content = re.sub(r':([a-z0-9_]+):', lambda m: EMOJI.get(m.group(0), m.group(0)), content)
            # Micro headers + standard headers
            content = re.sub(r'^-###\s(.*)$', rf'\033[2m\1{RESET}', content, flags=re.MULTILINE)
            content = re.sub(r'^-##\s(.*)$',  rf'\033[2;1m\1{RESET}', content, flags=re.MULTILINE)
            content = re.sub(r'^-#\s(.*)$',   rf'\033[1;4m\1{RESET}', content, flags=re.MULTILINE)
            content = re.sub(r'^(#{1,6})\s(.*)$', rf'\033[1;97m\2{RESET}', content, flags=re.MULTILINE)
            return content
        
        if __name__ == "__main__":
            if len(sys.argv) < 2:
                print("Usage: mdxl-cli <file.mdxl>")
                sys.exit(1)
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                print(render_terminal(f.read()))
