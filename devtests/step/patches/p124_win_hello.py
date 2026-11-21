# 💻 patch 124 (dashboard v3.36.72 · the Windows program's «hello»). The Windows check of the program 2.1 (GitHub run 44890440235): the page
#   told the program where it drew — ☐ ✕ only after a resize — the first try (1.5 s after the start) found the brand still hidden under the
#   opening splash (it ends at 3.6 s) and gave up · the page now tries again at 4.2 s and 8 s (the «hello» only feeds the program's log and
#   the Windows check · nothing for the customer changes)
#   python3 devtests/step/patches/p124_win_hello.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""  winCmd('state');setTimeout(winHello,1500);addEventListener('resize',()=>{clearTimeout(ht);ht=setTimeout(winHello,600)})}""",
     """  winCmd('state');[1500,4200,8000].forEach(t=>setTimeout(winHello,t));addEventListener('resize',()=>{clearTimeout(ht);ht=setTimeout(winHello,600)})}"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · 💻 the program's «hello» tried again after the splash · compiles · {p}")
