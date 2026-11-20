# 📉 patch 109 (dashboard v3.36.64 · the bar's DCA button). The owner (20-11): «نشر dca , اكتب فقط dca» ⇒ «📉 نشر DCA» → «📉 DCA»
#   (like «➕ شبكة» · «⚡ DCA+» beside it) — the same button, the same window
#   python3 devtests/step/patches/p109_dca_label.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""rgb(var(--amber3-rgb)/.9))">📉 نشر DCA</button>""", """rgb(var(--amber3-rgb)/.9))">📉 DCA</button>"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · 📉 the bar's button reads «📉 DCA» · compiles · {p}")
