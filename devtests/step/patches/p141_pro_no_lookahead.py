# p141 — v3.36.77 ⚖️ a daily derivatives reading is used only after ITS day has closed (found by check 16)
#   Check 16 (real prices): «🏦 العقود والمحترفون» on the 1-hour frame was right 76% — too good: the OKX daily readings (long/short accounts ·
#   taker volume · put/call · MVRV) are keyed by the START of their day but describe the whole day, and an hourly candle inside that day was
#   already reading them. Now every derivatives series is shifted by a day minus a second: the daily candle that closes the day still reads
#   its own day (unchanged), an hourly or 4-hour candle reads the day before (no peeking). The market series already carry their own lag.
#   python3 devtests/step/patches/p141_pro_no_lookahead.py Holy_Dashboard.pyw
import sys, os

R = [
    ('SG_MLAG = {"fng": 0, "vix": 1, "dxy": 1, "us10": 1, "epu": 2, "gpr": 8, "tone": 1}',
     'SG_MLAG = {"fng": 0, "vix": 1, "dxy": 1, "us10": 1, "epu": 2, "gpr": 8, "tone": 1}\n'
     'SG_PLAG = 86400 - 1                         # ⚖️ v3.36.77: قراءة العقود اليومية (مفتاحها بداية يومها) تُقرأ بعد إغلاق يومها فقط (الفحص 16)'),
    ('''            ks, vs = _pro_sorted(e_)
            if len(vs) >= 30:
                pro[k] = (ks, vs)
    return {"sym": sym, "drows": drows, "fng": fng, "btc": btc, "mkt": mkt, "pro": pro}''',
     '''            ks, vs = _pro_sorted(e_)
            if len(vs) >= 30:
                pro[k] = ([x + SG_PLAG for x in ks], vs)
    return {"sym": sym, "drows": drows, "fng": fng, "btc": btc, "mkt": mkt, "pro": pro}'''),
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
    print(f"✅ {len(R)} replacements · a daily derivatives reading waits for its day to close · {p}")
