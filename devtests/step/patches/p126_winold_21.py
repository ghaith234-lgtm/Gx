# 💻 patch 126 (dashboard v3.36.72 · the Windows program 2.1 inside). With 2.1 in the dashboard, a 2.0 program that fell back to the Edge
#   window (no WebView2 on that computer) saw «2.1 جاهز — نزّله» — but 2.1 needs WebView2 too: downloading it would change nothing. The bar
#   offers the download only to a 1.x program (the old title-bar window) · from 2.0 on, without WebView2, it still says to install WebView2
#   (devtests/ui_winold.py ②) · a 2.0 program running normally learns about 2.1 in ⚙️ ⇐ 💻 («توجد نسخة أحدث»)
#   python3 devtests/step/patches/p126_winold_21.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""  const old=cur<nv,b=document.createElement('div');""",
     """  const old=cur<2&&cur<nv/* 💻 v3.36.72: التنزيل لبرنامج 1.x فقط — 2.0 فما فوق بلا WebView2 ⇒ تنصيبه */,b=document.createElement('div');"""),
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
    print(f"✅ {len(R)} replacement · 💻 the old-program bar knows 2.1 · compiles · {p}")
