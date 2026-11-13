# 🔤 patch 47 (dashboard · the chosen font everywhere) — the owner (13-11): «هناك بعض الخطوط الي في الواجهة وداخل الكروت لم تتغير».
#   Found (devtests/ui_skins.js scan · every visible text with the font «أميري»): the words that sit inside a number's box
#   («10.2 يوم · منذ 11-03» · «4 شراء · 4 بيع» · «بلا حدود» · «لا شراء بعد» · «· نسبتك 0.1%» · «وصل ✓» · the report text …) took the
#   numbers' font (IBM Plex Mono — it has no Arabic letters) ⇒ the phone drew their Arabic with its own system font, whatever was chosen.
#   Now every monospace stack of the dashboard falls back to the chosen font (--ff) before the generic one: the digits keep their fixed
#   font, the Arabic letters next to them take the chosen one · the profit picture (🖼️) is drawn with the chosen font too.
#   python3 devtests/step/patches/p47_font_all.py Holy_Dashboard.pyw
import os, sys

CSS_A = "body{font-family:var(--ff,'IBM Plex Sans Arabic'),system-ui"   # the dashboard's own stylesheet (not the exported report page)
CSS_B = ".hwclone{overflow:hidden}"
FF = "var(--ff,'IBM Plex Sans Arabic')"
INSIDE = [   # (text, how many times inside the dashboard's stylesheet, replacement)
    ("font-family:'IBM Plex Mono',monospace", 8, f"font-family:'IBM Plex Mono',{FF},monospace"),
    ("font-family:'IBM Plex Mono',ui-monospace,monospace", 1, f"font-family:'IBM Plex Mono',ui-monospace,{FF},monospace"),
    ("font-family:ui-monospace,Menlo,Consolas,monospace", 2, f"font-family:ui-monospace,Menlo,Consolas,{FF},monospace"),
]
R = [
    ('''  const W=1080,PAD=64,IW=W-2*PAD,FA='"IBM Plex Sans Arabic","Segoe UI",Tahoma,sans-serif',FM='"IBM Plex Mono","Segoe UI",monospace';''',
     '''  const _ff=(getComputedStyle(document.documentElement).getPropertyValue('--ff')||'').trim();   // 🔤 v3.36.36: الخط المختار
  const W=1080,PAD=64,IW=W-2*PAD,FA=(_ff&&_ff!=="'IBM Plex Sans Arabic'"?_ff+',':'')+'"IBM Plex Sans Arabic","Segoe UI",Tahoma,sans-serif',FM='"IBM Plex Mono",'+(_ff?_ff+',':'')+'"Segoe UI",monospace';'''),
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
    print(f"✅ {sum(n for _, n, _ in INSIDE)} font stacks + {len(R)} replacement · compiles · {p}")
