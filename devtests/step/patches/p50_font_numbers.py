# 🔤 patch 50 (dashboard · the chosen font on the numbers too) — the owner (13-11, a screenshot with a chosen font, after v3.36.36):
#   «مو كل الكتابة اتغيرت» — the words changed, the numbers (424.93 · 28.1278 · 0.8273 …) kept their fixed font (IBM Plex Mono).
#   Now the numbers follow the chosen font as well (--fm) · the default font («IBM Plex») keeps the old fixed numbers exactly as before ·
#   the columns stay aligned with equal-width digits (tabular-nums, unchanged) · the profit picture 🖼️ too.
#   python3 devtests/step/patches/p50_font_numbers.py Holy_Dashboard.pyw
import os, sys

CSS_A = "body{font-family:var(--ff,'IBM Plex Sans Arabic'),system-ui"
CSS_B = ".hwclone{overflow:hidden}"
FF = "var(--ff,'IBM Plex Sans Arabic')"
FM = "var(--fm,'IBM Plex Mono')"
INSIDE = [
    (f"font-family:'IBM Plex Mono',{FF},monospace", 8, f"font-family:{FM},{FF},monospace"),
    (f"font-family:'IBM Plex Mono',ui-monospace,{FF},monospace", 1, f"font-family:{FM},ui-monospace,{FF},monospace"),
    ("font:600 17px 'IBM Plex Mono',monospace", 1, f"font:600 17px {FM},monospace"),
    ("font:700 9px 'IBM Plex Mono',monospace", 1, f"font:700 9px {FM},monospace"),
    ("font:600 10.5px 'IBM Plex Mono',monospace", 1, f"font:600 10.5px {FM},monospace"),
]
R = [
    # the chosen font sets --fm too (the default «IBM Plex» = the old fixed numbers)
    ('''  document.documentElement.style.setProperty('--ff',f[1]==='system-ui'?'system-ui':"'"+f[1]+"'");''',
     '''  document.documentElement.style.setProperty('--ff',f[1]==='system-ui'?'system-ui':"'"+f[1]+"'");
  if(f[0]==='plex')document.documentElement.style.removeProperty('--fm');else document.documentElement.style.setProperty('--fm',f[1]==='system-ui'?'system-ui':"'"+f[1]+"'");   // 🔤 v3.36.37: الأرقام هم'''),
    ('''FM='"IBM Plex Mono",'+(_ff?_ff+',':'')+'"Segoe UI",monospace';''',
     '''FM=((getComputedStyle(document.documentElement).getPropertyValue('--fm')||'').trim()||'"IBM Plex Mono"')+','+(_ff?_ff+',':'')+'"Segoe UI",monospace';'''),
    # the chooser's note
    ('''<div class="snote">كل زر مكتوب بخطّه · الأرقام تبقى بخطّها الثابت.</div>''',
     '''<div class="snote">كل زر مكتوب بخطّه · الكلمات والأرقام كلها تأخذه («IBM Plex» = الأرقام بخطّها الثابت القديم).</div>'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    if s.count(CSS_A) != 1 or s.count(CSS_B) != 1:
        print(f"❌ stylesheet anchors: {s.count(CSS_A)} · {s.count(CSS_B)} — nothing written"); sys.exit(1)
    a = s.index(CSS_A); b = s.index(CSS_B)
    css = s[a:b]
    for t, n, r in INSIDE:
        if css.count(t) != n:
            print(f"❌ {t!r}: {css.count(t)} times in the stylesheet (want {n}) — nothing written"); sys.exit(1)
        css = css.replace(t, r)
    s = s[:a] + css + s[b:]
    for i, (x, y) in enumerate(R):
        if s.count(x) != 1:
            print(f"❌ replacement {i}: found {s.count(x)} times — nothing written: {x[:90]!r}"); sys.exit(1)
        s = s.replace(x, y)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {sum(n for _, n, _ in INSIDE)} number fonts + {len(R)} replacements · compiles · {p}")
