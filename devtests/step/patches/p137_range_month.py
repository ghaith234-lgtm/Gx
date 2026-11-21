# p137 — v3.36.76 🔮 the range for the month and the three months (check 15: close-to-close on 90 daily candles held 82.2% and 80.7% of the time
#   for the next month and the next three months on 38 real coins · Garman–Klass / Parkinson were wider and held 83–87% — no gain, not used)
#   · AN_HZ + «1m» (the next month) and «3m» (the next three months) · AN_WIN: their volatility from the last 90 daily candles (the rest 48)
#   · issued on the daily close of the 1st of the month (three months: January · April · July · October) · graded at their end as the others
#   · they appear wherever the horizons are listed: 📈 (Bitcoin · each coin · 📜 the record) and 🔮
#   python3 devtests/step/patches/p137_range_month.py Holy_Dashboard.pyw
import sys, os

R = [
    ('AN_HZ = (("4h", "c1", 4, 3600, "الساعات الأربع القادمة"), ("1d", "c4", 6, 14400, "غداً"), ("1w", "c", 7, 86400, "الأسبوع القادم"))\n',
     'AN_HZ = (("4h", "c1", 4, 3600, "الساعات الأربع القادمة"), ("1d", "c4", 6, 14400, "غداً"), ("1w", "c", 7, 86400, "الأسبوع القادم"),\n'
     '         ("1m", "c", 30, 86400, "الشهر القادم"), ("3m", "c", 90, 86400, "الأشهر الثلاثة القادمة"))     # 🔮 v3.36.76: الشهر والأشهر الثلاثة (فحص 15)\n'
     'AN_WIN = {"1m": 90, "3m": 90}                    # تذبذبهما من آخر 90 شمعة يومية (الباقي 48) — فحص 15: 82.2% · 80.7%\n'),
    ('''        if len(rows) < 60 or not px:
            continue
        C = [float(r[4]) for r in rows[-49:]]
''', '''        win = AN_WIN.get(k, 48)
        if len(rows) < max(60, win + 1) or not px:
            continue
        C = [float(r[4]) for r in rows[-(win + 1):]]
'''),
    ('''    want = {"4h": "4H" in frs, "1d": "1D" in frs, "1w": "1D" in frs and datetime.utcfromtimestamp(now).weekday() == 0}
''', '''    d0 = datetime.utcfromtimestamp(now)
    want = {"4h": "4H" in frs, "1d": "1D" in frs, "1w": "1D" in frs and d0.weekday() == 0,
            "1m": "1D" in frs and d0.day == 1, "3m": "1D" in frs and d0.day == 1 and d0.month in (1, 4, 7, 10)}     # 🔮 v3.36.76
'''),
    ('''            h = {"4h": 4 * 3600, "1d": 86400, "1w": 7 * 86400}[k]
''', '''            h = {"4h": 4 * 3600, "1d": 86400, "1w": 7 * 86400, "1m": 30 * 86400, "3m": 90 * 86400}.get(k)
            if not h:
                continue
'''),
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
    print(f"✅ {len(R)} replacements · 🔮 the month and the three months · compiles · {p}")
