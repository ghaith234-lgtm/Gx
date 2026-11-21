# p133 — v3.36.76 📍 «منطقة أكثر تداول» from the hour (Gemini's point, checked: it was 30 daily closes in 24 boxes)
#   · the last 30 days of hourly candles (720): each candle's typical price (high + low + close) / 3 weighted by its volume, in 40 boxes over
#     the month's low … high ⇒ the busiest box · fewer than 240 hourly candles ⇒ the old daily way
#   python3 devtests/step/patches/p133_poc_hourly.py Holy_Dashboard.pyw
import sys, os

R = [
    ("def _an_levels(H, L, C, V, px=None, look=30):\n",
     "def _an_levels(H, L, C, V, px=None, look=30, h1=None):\n"),
    ("""    lo, hi = min(L[-look:]), max(H[-look:])
    poc = None
    if hi > lo:
        bins = [0.0] * 24
""",
     """    lo, hi = min(L[-look:]), max(H[-look:])
    poc = None
    hh = [r for r in (h1 or [])[-look * 24:] if float(r[2]) >= float(r[3]) > 0]
    if len(hh) >= 240:                               # 📍 v3.36.76: من شموع الساعة — السعر النموذجي (أعلى + أدنى + إغلاق) / 3 × الحجم
        lo2, hi2 = min(float(r[3]) for r in hh), max(float(r[2]) for r in hh)
        if hi2 > lo2:
            bins = [0.0] * 40
            for r in hh:
                tp = (float(r[2]) + float(r[3]) + float(r[4])) / 3.0
                bins[min(39, int((tp - lo2) / (hi2 - lo2) * 40))] += float(r[5])
            b = max(range(40), key=lambda j: bins[j])
            poc = lo2 + (b + 0.5) * (hi2 - lo2) / 40
    elif hi > lo:                                    # (أقل من 240 شمعة ساعة ⇒ الطريقة اليومية)
        bins = [0.0] * 24
"""),
    ("    lv = _an_levels(H, L, C, V, px)\n", "    lv = _an_levels(H, L, C, V, px, h1=h1)\n"),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 📍 the busiest area from the hourly candles · compiles · {p}")
