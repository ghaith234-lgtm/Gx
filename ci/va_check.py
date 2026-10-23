# 🛤️ v3.34.0: the value-path bot on REAL OKX history (GitHub runner — public candles only: no keys, no orders, no notifications)
#   The engine's own rules (ci/va_sim.py — checked step by step against the engine itself) on hourly candles of 12 coins,
#   180-day windows starting every 15 days (≈2.5 years) ⇒ for every setting: result per 100 $ of the most capital it needed,
#   result per 300 $ budget, worst moment, trades, fees — next to plain DCA (same steps, same budget, never sells) and
#   buy-and-hold (the whole budget on day one). One setting changes at a time around the default, then a small grid.
#   python3 ci/va_check.py  ⇒ lines starting with HOLYVA
import os, sys, time, json, statistics as S
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_sim import va_sim, dca_sim, hold_sim, roll_max
COINS = ["BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "BNB", "LTC", "LINK", "TRX", "AVAX", "DOT"]
HDR = {"User-Agent": "Mozilla/5.0 (HolyDashboard check)"}
YEARS = 2.5
WIN_D, EVERY_D = 180, 15


def candles(inst):
    """hourly closes, oldest first — OKX history-candles paged backwards (100 per call)"""
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
            rows[int(r[0])] = float(r[4])
        after = min(int(r[0]) for r in d)
        if len(rows) >= need:
            break
        time.sleep(0.11)
    ts = sorted(rows)
    out_t, out_c = [], []
    for t in ts:                                        # fill missing hours with the last close (OKX gaps are rare)
        if out_t and t - out_t[-1] > 3600 * 1000:
            k = out_t[-1]
            while t - k > 3600 * 1000:
                k += 3600 * 1000; out_t.append(k); out_c.append(out_c[-1])
        out_t.append(t); out_c.append(rows[t])
    return out_t, out_c


DATA = {}
for c in COINS:
    try:
        t, cl = candles(c + "-USDT")
    except Exception as e:
        t, cl = [], []
    if len(cl) > 24 * 200:
        DATA[c] = (t, cl, roll_max(cl))
print("HOLYVA hourly candles:", {c: len(v[1]) for c, v in DATA.items()},
      "· from", {c: time.strftime("%Y-%m-%d", time.gmtime(v[0][0] / 1000)) for c, v in DATA.items()}, flush=True)

BASE = dict(start=10, step=10, band=2, max_order=30, cap=300, floor=True, brake=15, every_h=24)


def windows(n):
    w, e = WIN_D * 24, EVERY_D * 24
    return [(i, i + w) for i in range(25, n - w, e)]


def run(p, label, per_coin=False):
    va_r, va_pl, dca_r, dca_pl, hold_r, hold_pl, beat, pos, worst, trades, fees, capf, real = [], [], [], [], [], [], [], [], [], [], [], [], []
    coin_rows = {}
    for c, (t, C, R) in DATA.items():
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


# round 1 (run 1, 2026-10-22): growing target ≈ DCA ≈ hold · fixed target (step 0) best (median +6.3 vs hold −4.5, VA>hold 60 %) ·
#   band, floor, brake, max order barely matter (brake slightly worse). Round 2: tune the fixed target · growing target with slow steps.
FIX = dict(start=100, step=0, band=4, max_order=60, cap=400, floor=True, brake=0, every_h=24)
print("HOLYVA ── round 2 · fixed target 100 $ (step 0)", FIX, flush=True)
run(FIX, "FIXED default", per_coin=True)
for e in (4, 12, 24, 72):
    for b in (2, 4, 8):
        for f in (True, False):
            run(dict(FIX, every_h=e, band=b, floor=f), f"fixed every_h={e} band={b} floor={f}")
for c in (200, 1e9):
    run(dict(FIX, cap=c), f"fixed cap={c}")
for mo in (30, 1e9):
    run(dict(FIX, max_order=mo), f"fixed max_order={mo}")
run(dict(FIX, brake=15), "fixed brake=15")
G = dict(start=10, step=10, band=4, max_order=30, cap=300, floor=True, brake=0, every_h=168)
print("HOLYVA ── round 2 · growing target, slow steps", G, flush=True)
run(G, "GROW weekly", per_coin=True)
for e in (72, 168):
    for c in (300, 600, 1e9):
        run(dict(G, every_h=e, cap=c), f"grow every_h={e} cap={c}")
print("HOLYVA done", flush=True)
