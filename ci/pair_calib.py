# 🔀 «شبكة عملتين» — how do XRP and SUI · SOL · ASTER · XLM really move (REAL OKX public candles · no keys · no orders · no wallet)?
#   The numbers a random market needs to look like the real one: every coin's price counted in XRP (the ratio) and XRP in dollars —
#   the size of a move over 1 minute · 15 minutes · 1 hour · 4 hours · 1 day · 1 week · 30 days · fat tails · calm/wild spells ·
#   how the moves go together · and how many 1.5% round trips a ratio really made per day (1-minute closes for 30 days ·
#   15-minute closes for a year · daily closes for 3 years). OKX's lot/tick/min for each coin.
#   python3 ci/pair_calib.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R_ = tempfile.mkdtemp(prefix="pairc_")
shutil.copy(DASH, os.path.join(R_, "Holy_Dashboard.pyw"))
os.chdir(R_)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R_, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
T0 = time.time()
COINS = ["XRP", "SUI", "SOL", "ASTER", "XLM"]
FR = {"1m": (60, 43200), "15m": (900, 35040), "1Dutc": (86400, 1100)}


def Pr(*a):
    print("HPC", *a, flush=True)


DRY = os.environ.get("PAIRC_DRY") == "1"
if DRY:
    FR = {"1m": (60, 3000), "15m": (900, 2000), "1Dutc": (86400, 400)}


def fetch(sym, bar, n):
    if DRY:                                          # (a local run: a synthetic walk — the CI run reads OKX)
        import random
        rnd, base = random.Random(len(sym) * 31 + len(bar)), random.Random(len(bar))
        p, out, t, dt = 1.0, [], 1_760_000_000, FR[bar][0]
        for i in range(n):
            p *= math.exp(base.gauss(0, 0.004) + rnd.gauss(0, 0.003))
            out.append([t + i * dt, p, p, p, p, 1])
        return out
    rows = [c[:6] for c in m._fc_okx_rows(sym, bar, hist=False, limit=100) if c[6]]
    oldest = min((c[0] for c in rows), default=None)
    while oldest and len(rows) < n:
        pg = []
        for _ in range(4):
            pg = [c[:6] for c in m._fc_okx_rows(sym, bar, after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
            if pg:
                break
            time.sleep(1.0)
        if not pg:
            break
        rows += pg
        oldest = min(c[0] for c in pg)
        time.sleep(0.11)
    return sorted({c[0]: c for c in rows}.values())[-n:]


def spec(sym):
    if DRY:
        return {}
    r = m._okx_pub(f"/api/v5/public/instruments?instType=SPOT&instId={sym}")
    d = ((r or {}).get("data") or [{}])[0]
    return {"tick": d.get("tickSz"), "lot": d.get("lotSz"), "min": d.get("minSz"), "state": d.get("state"), "list": d.get("listTime")}


def std(x):
    n = len(x)
    if n < 3:
        return None
    mu = sum(x) / n
    return math.sqrt(sum((v - mu) ** 2 for v in x) / (n - 1))


def kurt(x):
    n = len(x)
    if n < 10:
        return None
    mu = sum(x) / n
    v = sum((a - mu) ** 2 for a in x) / n
    return sum((a - mu) ** 4 for a in x) / n / v / v if v > 0 else None


def corr(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / sa / sb if sa > 0 and sb > 0 else None


def ac(x, lag=1):
    return corr(x[:-lag], x[lag:]) if len(x) > lag + 3 else None


def rets(lp, k):
    """non-overlapping log returns over k bars"""
    return [lp[i + k] - lp[i] for i in range(0, len(lp) - k, k)]


def trips(lp, g):
    """the engine's ladder on a ratio path: levels every g from the start · a level above the start holds coins from the start ·
    a buy when the ratio drops through a level · a sale one level up · ⇒ sales"""
    lg = math.log(1 + g)
    held = set(range(0, 100000))                   # «as if bought» from the start up (level j buys at R0(1+g)^j · sells one level up)
    L = 0
    n = 0
    base = lp[0]
    for v in lp[1:]:
        k = math.floor((v - base) / lg + 1e-12)
        while L < k:                               # up through level L+1: level L sells
            if L in held:
                held.discard(L)
                n += 1
            L += 1
        while L > k:                               # down through level L: level L buys
            held.add(L)
            L -= 1
    return n


OUT = {"coins": COINS, "spec": {}, "bars": {}}
for c in COINS:
    OUT["spec"][c] = spec(f"{c}-USDT")
Pr("spec", json.dumps(OUT["spec"]))
for bar, (dt, n) in FR.items():
    data = {}
    for c in COINS:
        rows = fetch(f"{c}-USDT", bar, n)
        data[c] = {r[0]: r[4] for r in rows}
        Pr(f"{bar} {c}: {len(rows)} candles · from {time.strftime('%Y-%m-%d', time.gmtime(rows[0][0])) if rows else '-'} · {time.time() - T0:.0f}s")
    res = {}
    tx = sorted(data["XRP"])
    lx = [math.log(data["XRP"][t]) for t in tx]
    ks = {"1m": [1, 15, 60, 240, 1440], "15m": [1, 4, 16, 96, 672, 2880], "1Dutc": [1, 7, 30, 90, 365]}[bar]
    per_day = 86400 / dt
    res["XRP"] = {"n": len(lx), "days": round(len(lx) / per_day, 1), "chg": round(math.exp(lx[-1] - lx[0]) - 1, 4),
                  "sd": {k: std(rets(lx, k)) for k in ks}, "kurt1": kurt(rets(lx, 1)), "kurtd": kurt(rets(lx, int(per_day))) if per_day > 1 else kurt(rets(lx, 1)),
                  "ac1": ac(rets(lx, 1)), "acabs": ac([abs(v) for v in rets(lx, max(1, int(per_day)))])}
    RR = {}
    for c in COINS[1:]:
        tt = [t for t in tx if t in data[c]]
        if len(tt) < 50:
            continue
        lr = [math.log(data[c][t] / data["XRP"][t]) for t in tt]
        lc = [math.log(data[c][t]) for t in tt]
        lxx = [math.log(data["XRP"][t]) for t in tt]
        RR[c] = (tt, lr, lc, lxx)
        days = len(tt) / per_day
        hi, lo = max(lr), min(lr)
        res[c] = {"n": len(lr), "days": round(days, 1), "ratio_chg": round(math.exp(lr[-1] - lr[0]) - 1, 4),
                  "usd_chg": round(math.exp(lc[-1] - lc[0]) - 1, 4), "ratio_hi": round(math.exp(hi - lr[0]) - 1, 4), "ratio_lo": round(math.exp(lo - lr[0]) - 1, 4),
                  "sd": {k: std(rets(lr, k)) for k in ks}, "sd_usd": {k: std(rets(lc, k)) for k in ks},
                  "kurt1": kurt(rets(lr, 1)), "ac1": ac(rets(lr, 1)), "ac2": ac(rets(lr, 1), 2),
                  "acabs": ac([abs(v) for v in rets(lr, max(1, int(per_day)))]),
                  "corr_usd_xrp": corr(rets(lc, 1), rets(lxx, 1)), "corr_ratio_xrp": corr(rets(lr, 1), rets(lxx, 1)),
                  "corr_usd_xrp_d": corr(rets(lc, max(1, int(per_day))), rets(lxx, max(1, int(per_day)))),
                  "corr_ratio_xrp_d": corr(rets(lr, max(1, int(per_day))), rets(lxx, max(1, int(per_day)))),
                  "trips15": trips(lr, 0.015), "trips15_per_day": round(trips(lr, 0.015) / days, 3),
                  "trips20_per_day": round(trips(lr, 0.02) / days, 3)}
    cc = {}
    for a in RR:
        for b in RR:
            if a < b:
                ta = set(RR[a][0]) & set(RR[b][0])
                ia = [i for i, t in enumerate(RR[a][0]) if t in ta]
                ib = [i for i, t in enumerate(RR[b][0]) if t in ta]
                la = [RR[a][1][i] for i in ia]
                lb = [RR[b][1][i] for i in ib]
                k = max(1, int(per_day))
                cc[f"{a}/{b}"] = (corr(rets(la, 1), rets(lb, 1)), corr(rets(la, k), rets(lb, k)))
    res["ratio_corr"] = cc
    OUT["bars"][bar] = res
    Pr(bar, json.dumps(res, separators=(",", ":")))
json.dump(OUT, open("/tmp/holypairc.json", "w"))
Pr(f"DONE · {time.time() - T0:.0f}s")
