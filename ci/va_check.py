# 🛤️ v3.34.0: the value-path bot on REAL OKX history (GitHub runner — public candles only: no keys, no orders, no notifications)
#   The engine's own rules (ci/va_sim.py — checked step by step against the engine itself) on hourly candles of 12 coins,
#   180-day windows starting every 15 days (≈2.5 years) ⇒ for every setting: result per 100 $ of the most capital it needed,
#   result per 300 $ budget, worst moment, trades, fees — next to plain DCA (same steps, same budget, never sells) and
#   buy-and-hold (the whole budget on day one). One setting changes at a time around the default, then a small grid.
#   python3 ci/va_check.py  ⇒ lines starting with HOLYVA
import os, sys, time, json, statistics as S
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_sim import va_sim, va_sim_price, dca_sim, hold_sim, roll_max
COINS = ["BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "BNB", "LTC", "LINK", "TRX", "AVAX", "DOT"]
HDR = {"User-Agent": "Mozilla/5.0 (HolyDashboard check)"}
YEARS = 2.5
WIN_D, EVERY_D = 180, 15


def candles(inst):
    """hourly candles (open · high · low · close), oldest first — OKX history-candles paged backwards (100 per call)"""
    rows, after = {}, None
    need = int(YEARS * 365 * 24)
    for _ in range(int(need / 100) + 5):
        u = f"https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar=1H&limit=100" + (f"&after={after}" if after else "")
        d = []
        for t in range(4):
            try:
                d = requests.get(u, headers=HDR, timeout=30).json().get("data") or []
                break
            except Exception:
                time.sleep(1 + t)
        if not d:
            break
        for r in d:
            rows[int(r[0])] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]))
        after = min(int(r[0]) for r in d)
        if len(rows) >= need:
            break
        time.sleep(0.11)
    ts = sorted(rows)
    out_t, out = [], []
    for t in ts:                                        # fill missing hours with the last close (OKX gaps are rare)
        if out_t and t - out_t[-1] > 3600 * 1000:
            k = out_t[-1]
            while t - k > 3600 * 1000:
                k += 3600 * 1000; out_t.append(k); out.append((out[-1][3],) * 4)
        out_t.append(t); out.append(rows[t])
    return out_t, out


DATA = {}
for c in COINS:
    try:
        t, ohlc = candles(c + "-USDT")
    except Exception as e:
        t, ohlc = [], []
    if len(ohlc) > 24 * 200:
        cl = [x[3] for x in ohlc]
        DATA[c] = (t, cl, roll_max(cl), [x[0] for x in ohlc], [x[1] for x in ohlc], [x[2] for x in ohlc])
print("HOLYVA hourly candles:", {c: len(v[1]) for c, v in DATA.items()},
      "· from", {c: time.strftime("%Y-%m-%d", time.gmtime(v[0][0] / 1000)) for c, v in DATA.items()}, flush=True)

BASE = dict(start=10, step=10, band=2, max_order=30, cap=300, floor=True, brake=15, every_h=24)


def windows(n):
    w, e = WIN_D * 24, EVERY_D * 24
    return [(i, i + w) for i in range(25, n - w, e)]


def run(p, label, per_coin=False):
    va_r, va_pl, dca_r, dca_pl, hold_r, hold_pl, beat, pos, worst, trades, fees, capf, real = [], [], [], [], [], [], [], [], [], [], [], [], []
    coin_rows = {}
    for c, (t, C, R) in ((k, v[:3]) for k, v in DATA.items()):
        for i0, i1 in windows(len(C)):
            v = va_sim(C, i0, i1, p, R=R)
            d = dca_sim(C, i0, i1, p["every_h"], p["start"], p["step"], p["cap"])
            h = hold_sim(C, i0, i1, p["cap"])
            pk = max(v["peak"], 1.0)
            va_r.append(v["pl"] / pk * 100); va_pl.append(v["pl"] * 300.0 / p["cap"])
            dca_r.append(d["ret"]); dca_pl.append(d["pl"] * 300.0 / p["cap"])
            hold_r.append(h["ret"]); hold_pl.append(h["pl"] * 300.0 / p["cap"])
            beat.append(v["pl"] > d["pl"]); pos.append(v["pl"] > 0)
            worst.append(v["pl_min"] / pk * 100); trades.append(v["trades"]); fees.append(v["fees"])
            capf.append(v["cap_full"] / max(1, v["steps"]) * 100); real.append(v["realized"])
            coin_rows.setdefault(c, []).append((v["pl"] / pk * 100, d["ret"], v["pl"] > d["pl"]))
    n = len(va_r)
    if not n:
        print(f"HOLYVA {label}: no data", flush=True); return None
    m = lambda a: S.mean(a)
    md = lambda a: S.median(a)
    print(f"HOLYVA {label} | {n} windows | VA: per100 med {md(va_r):+.1f} mean {m(va_r):+.1f} · per300$ mean {m(va_pl):+.1f}$ · positive {sum(pos) / n * 100:.0f}% · "
          f"worst moment mean {m(worst):.1f}% (min {min(worst):.1f}%) · trades {m(trades):.0f} · fees {m(fees):.2f}$ · realized {m(real):+.1f}$ · budget-full steps {m(capf):.0f}% | "
          f"DCA: per100 med {md(dca_r):+.1f} mean {m(dca_r):+.1f} · per300$ {m(dca_pl):+.1f}$ | HOLD: per100 med {md(hold_r):+.1f} · per300$ {m(hold_pl):+.1f}$ | "
          f"VA>DCA (dollars) {sum(beat) / n * 100:.0f}%", flush=True)
    if per_coin:
        for c, rr in coin_rows.items():
            print(f"HOLYVA   {c}: VA per100 med {md([x[0] for x in rr]):+.1f} · DCA med {md([x[1] for x in rr]):+.1f} · VA>DCA {sum(x[2] for x in rr) / len(rr) * 100:.0f}% ({len(rr)} windows)", flush=True)
    return {"va": md(va_r), "dca": md(dca_r), "beat": sum(beat) / n}


# round 1 (run 1, 2026-10-22): growing target ≈ DCA ≈ hold · fixed target (step 0) best (median +6.3 vs hold −4.5, VA>hold 60 %).
# round 2 (run 2, 2026-10-23): fixed 100 $ checked every 4 h, band 8 % best (median +7.1 · positive 57 % · VA>DCA 62 %) ⇒ v3.34.0 default.
# round 3 (v3.35.0): 📉📈 «by percentage» — a step at every level the price crosses (every drop% down / rise% up), no clock.
FIX4 = dict(start=100, step=0, band=8, max_order=60, cap=400, floor=True, brake=0, every_h=4)
_REF = {}


def run_pm(p, label, per_coin=False):
    """the «by percentage» mode on the same windows · next to buy-and-hold and to the time mode's best (fixed 100 $ · every 4 h · band 8 %)"""
    r, pos, worst, trades, fees, real, capf, hold_r, beat_t, beat_h, lv = [], [], [], [], [], [], [], [], [], [], []
    coin_rows = {}
    for c, (t, C, R, O, Hh, L) in DATA.items():
        for i0, i1 in windows(len(C)):
            v = va_sim_price(O, Hh, L, C, i0, i1, p)
            k = (c, i0)
            if k not in _REF:
                _REF[k] = va_sim(C, i0, i1, FIX4, R=R)
            ref = _REF[k]
            h = hold_sim(C, i0, i1, p["cap"])
            pk = max(v["peak"], 1.0)
            x = v["pl"] / pk * 100
            r.append(x); pos.append(v["pl"] > 0); worst.append(v["pl_min"] / pk * 100); trades.append(v["trades"]); fees.append(v["fees"])
            real.append(v["realized"]); capf.append(v["cap_full"]); hold_r.append(h["ret"]); lv.append(v["lvl"])
            beat_t.append(x > ref["pl"] / max(ref["peak"], 1.0) * 100); beat_h.append(x > h["ret"])
            coin_rows.setdefault(c, []).append(x)
    n = len(r)
    if not n:
        print(f"HOLYVA {label}: no data", flush=True); return None
    m, md = S.mean, S.median
    print(f"HOLYVA {label} | {n} windows | per100 med {md(r):+.1f} mean {m(r):+.1f} · positive {sum(pos) / n * 100:.0f}% · worst moment mean {m(worst):.1f}% "
          f"(min {min(worst):.1f}%) · trades {m(trades):.0f} · fees {m(fees):.2f}$ · realized {m(real):+.1f}$ · budget-full levels {m(capf):.1f} · "
          f"| HOLD per100 med {md(hold_r):+.1f} · beats hold {sum(beat_h) / n * 100:.0f}% · beats time-best {sum(beat_t) / n * 100:.0f}%", flush=True)
    if per_coin:
        print("HOLYVA   per coin med: " + " · ".join(f"{c} {md(v):+.1f}" for c, v in coin_rows.items()), flush=True)
    return md(r)


print("HOLYVA ── round 3 · by percentage (no clock)", flush=True)
FIXP = dict(start=100, step=0, drop=5, rise=5, max_order=100, cap=400, floor=True)
run_pm(FIXP, "PCT fixed 100 $ · 5 %", per_coin=True)
for x in (2, 3, 8, 10, 15):
    run_pm(dict(FIXP, drop=x, rise=x), f"pct fixed {x}%/{x}%")
for dd, uu in ((5, 8), (8, 5), (3, 6), (5, 10), (8, 12)):
    run_pm(dict(FIXP, drop=dd, rise=uu), f"pct fixed down {dd}% up {uu}%")
for x in (5, 8):
    run_pm(dict(FIXP, drop=x, rise=x, floor=False), f"pct fixed {x}% floor=False")
run_pm(dict(FIXP, cap=1e9), "pct fixed 5% cap=∞")
GROWP = dict(start=10, step=10, drop=5, rise=5, max_order=60, cap=300, floor=True)
run_pm(GROWP, "PCT grow 10+10 · 5 %", per_coin=True)
for x in (3, 8, 10, 15):
    run_pm(dict(GROWP, drop=x, rise=x), f"pct grow {x}%/{x}%")
for c in (150, 600):
    run_pm(dict(GROWP, cap=c), f"pct grow 5% cap={c}")
run_pm(dict(GROWP, step=5), "pct grow 10+5 · 5%")
print("HOLYVA done", flush=True)
