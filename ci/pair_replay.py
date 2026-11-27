# 🔀 «شبكة عملتين» on REAL 1-minute OKX prices (the owner 27-11: «عندك مشكلة انت في الربح في المسافات القصيرة ، كذلك الربح هو مو
#   اتجاه واحد هو تذبذب»). XRP main with SUI · SOL · ASTER · XLM · step 1.5% · every buy 5 XRP · profit to XRP / half and half.
#   ① the last real year minute by minute (the same moves, started from today's prices) · ② the same year read every 15 minutes
#   and every hour (what the short swings add) · ③ 200 random years built from real two-week pieces of the last year (all coins
#   together — the real swings, in a new order). The engine = ci/pair_model.py (matches the real engine exactly).
#   A generic ladder (no wallet here): 400 levels below · above up to OKX's minimum order. Printed: what each bot changes —
#   sales · profit · its XRP · its coin · vs holding (in XRP). Public data only (no keys · no orders).
#   python3 ci/pair_replay.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pair_model import PairModel

DASH = os.path.abspath(sys.argv[1])
R_ = tempfile.mkdtemp(prefix="pairr_")
shutil.copy(DASH, os.path.join(R_, "Holy_Dashboard.pyw"))
os.chdir(R_)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R_, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
T0 = time.time()
COINS = ["XRP", "SUI", "SOL", "ASTER", "XLM"]
OT = COINS[1:]
DAYS = int(os.environ.get("REPLAY_DAYS") or 365)
NBOOT = int(os.environ.get("REPLAY_BOOT") or 200)
BLOCK_D = 14
G, MV, DN = 0.015, 5.0, 400
MODES = ("main", "half")
DRY = os.environ.get("REPLAY_DRY") == "1"
LOCK = threading.Lock()


def Pr(*a):
    with LOCK:
        print("HPR", *a, flush=True)


def fetch(sym, n):
    """1-minute closes, oldest first · back page by page (100 each) · patient with the rate limit"""
    if DRY:
        rnd = np.random.default_rng(abs(hash(sym)) % 1000)
        t = 1_760_000_000
        p = {"XRP": 0.95, "SUI": 0.67, "SOL": 72.0, "ASTER": 0.5, "XLM": 0.127}[sym.split("-")[0]]
        lp = np.log(p) + np.cumsum(rnd.normal(0, 0.001, n))
        return [[t + 60 * i, float(np.exp(v))] for i, v in enumerate(lp)]
    rows = {}
    for c in m._fc_okx_rows(sym, "1m", hist=False, limit=100):
        if c[6]:
            rows[c[0]] = c[4]
    oldest = min(rows) if rows else None
    last_log = time.time()
    while oldest and len(rows) < n:
        pg = []
        for k in range(10):
            pg = [c for c in m._fc_okx_rows(sym, "1m", after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
            if pg:
                break
            time.sleep(1.0 + k)
        if not pg:
            break
        for c in pg:
            rows[c[0]] = c[4]
        oldest = min(c[0] for c in pg)
        if time.time() - last_log > 300:
            last_log = time.time()
            Pr(f"{sym}: {len(rows)} minutes · {time.time() - T0:.0f}s")
        time.sleep(0.55)
    return sorted(rows.items())[-n:]


def spec(sym):
    if DRY:
        return {"XRP": (0.0001, 0.000001, 1.0), "SUI": (0.0001, 0.0001, 1.0), "SOL": (0.01, 0.000001, 0.01), "ASTER": (0.0001, 0.001, 1.0),
                "XLM": (0.00001, 0.000001, 10.0)}[sym.split("-")[0]]
    r = m._okx_pub(f"/api/v5/public/instruments?instType=SPOT&instId={sym}")
    d = ((r or {}).get("data") or [{}])[0]
    return float(d.get("tickSz") or 0.0001), float(d.get("lotSz") or 0.000001), float(d.get("minSz") or 1)


N = DAYS * 1440 + 1
SPEC = {c: spec(f"{c}-USDT") for c in COINS}
Pr("spec", json.dumps(SPEC))
with ThreadPoolExecutor(5) as ex:
    raw = dict(zip(COINS, ex.map(lambda c: fetch(f"{c}-USDT", N), COINS)))
for c in COINS:
    Pr(f"{c}: {len(raw[c])} minutes · from {time.strftime('%Y-%m-%d %H:%M', time.gmtime(raw[c][0][0])) if raw[c] else '-'} · {time.time() - T0:.0f}s")
t_lo = max(raw[c][0][0] for c in COINS)
t_hi = min(raw[c][-1][0] for c in COINS)
TT = np.arange(t_lo, t_hi + 1, 60)
PX = {}
for c in COINS:
    ts = np.array([r[0] for r in raw[c]])
    ps = np.array([r[1] for r in raw[c]])
    idx = np.searchsorted(ts, TT, side="right") - 1          # the last close at or before each minute (a quiet minute keeps its price)
    PX[c] = ps[np.clip(idx, 0, len(ps) - 1)]
NM = len(TT)
Pr(f"aligned {NM} minutes ({NM / 1440:.1f} days) · gaps filled {sum(int(NM - len(raw[c])) for c in COINS)}")
LX = np.log(PX["XRP"])
LR = {c: np.log(PX[c]) - LX for c in OT}                     # the ratio in XRP (log)
P_TODAY = {c: float(PX[c][-1]) for c in COINS}


def up_levels(c, r0):
    """the calculator's levels above: until one level is under 1.5 × OKX's minimum (generic — no wallet)"""
    up = 0
    while up < 2000 - DN:
        q = MV / (r0 * (1 + G) ** up)
        if q < 1.5 * SPEC[c][2]:
            break
        up += 1
    return up


def run_bot(c, mode, lx, lr):
    """one bot on a path of log prices (XRP in $ · the coin in XRP) started from today's prices ⇒ what it changed"""
    pm = P_TODAY["XRP"] * np.exp(lx - lx[0])
    po = P_TODAY[c] * np.exp(lr - lr[0] + lx - lx[0])
    tm, to = SPEC["XRP"][0], SPEC[c][0]
    PM = (np.round(pm / tm) * tm).tolist()
    PO = (np.round(po / to) * to).tolist()
    r0 = PO[0] / PM[0]
    up = up_levels(c, r0)
    M = PairModel(r0, G, MV, DN, up, mode, SPEC[c], SPEC["XRP"])
    M.run(PM[1:], PO[1:])
    rend = PO[-1] / PM[-1]
    dx, dc = M.w_main - M.main_start, M.w_other - M.other_start
    vs_hold = dx + dc * rend + M.w_usd / PM[-1]               # in XRP, at the end prices
    lr_rel = lr - lr[0]
    return {"sales": M.sales, "profit": M.total_profit, "kept": M.profit_other, "dx": dx, "dc": dc, "usd": M.w_usd, "vs_hold": vs_hold,
            "up": up, "r_chg": math.exp(float(lr_rel[-1])) - 1, "r_hi": math.exp(float(lr_rel.max())) - 1, "r_lo": math.exp(float(lr_rel.min())) - 1,
            "x_chg": math.exp(float(lx[-1] - lx[0])) - 1, "fees": M.fees_usd}


OUT = {"spec": SPEC, "today": P_TODAY, "minutes": NM, "from": int(TT[0]), "to": int(TT[-1]), "real": {}, "boot": {}}
# ① + ② the real year · minute / 15 minutes / hour
for every, lab in ((1, "1m"), (15, "15m"), (60, "1h")):
    for c in OT:
        for mode in (MODES if every == 1 else ("main",)):
            r = run_bot(c, mode, LX[::every], LR[c][::every])
            OUT["real"][f"{lab}:{c}:{mode}"] = r
            Pr(f"REAL {lab} {c}/XRP {mode}: {r['sales']} sales · profit {r['profit']:.3f} XRP" + (f" + {r['kept']:.6g} {c}" if r['kept'] else "")
               + f" · bot XRP {r['dx']:+.3f} · bot {c} {r['dc']:+.6g} · vs holding {r['vs_hold']:+.3f} XRP · ratio {r['r_chg'] * 100:+.1f}% "
               f"(high {r['r_hi'] * 100:+.1f}% · low {r['r_lo'] * 100:+.1f}%) · XRP $ {r['x_chg'] * 100:+.1f}% · up levels {r['up']} · fees {r['fees']:.2f}$")
# ③ random years from real two-week pieces (every coin together)
B = BLOCK_D * 1440
dX = np.diff(LX)
dR = {c: np.diff(LR[c]) for c in OT}
Y = 365 * 1440
rng = np.random.default_rng(20261127)
agg = {mode: {"sx": [], "vs": [], "allup": 0, "dc": {c: [] for c in OT}, "pr": {c: [] for c in OT}, "kp": {c: [] for c in OT},
              "sa": {c: [] for c in OT}, "rc": {c: [] for c in OT}} for mode in MODES}
xchg = []
tb = time.time()
for y in range(NBOOT):
    starts = rng.integers(0, len(dX) - B, size=Y // B + 1)
    sel = np.concatenate([np.arange(s, s + B) for s in starts])[:Y]
    lx = np.concatenate([[0.0], np.cumsum(dX[sel])])
    lrs = {c: np.concatenate([[0.0], np.cumsum(dR[c][sel])]) for c in OT}
    xchg.append(math.exp(lx[-1]) - 1)
    for mode in MODES:
        a = agg[mode]
        sx, vs, ok = 0.0, 0.0, True
        for c in OT:
            r = run_bot(c, mode, lx, lrs[c])
            sx += r["dx"]
            vs += r["vs_hold"]
            a["dc"][c].append(r["dc"])
            a["pr"][c].append(r["profit"])
            a["kp"][c].append(r["kept"])
            a["sa"][c].append(r["sales"])
            a["rc"][c].append(r["r_chg"])
            ok = ok and r["dc"] > 0
        a["sx"].append(sx)
        a["vs"].append(vs)
        a["allup"] += int(ok and sx > 0)
    if y % 20 == 19:
        Pr(f"random years {y + 1}/{NBOOT} · {time.time() - tb:.0f}s")


def pc(a):
    a = np.array(a)
    return [round(float(np.percentile(a, p)), 6) for p in (10, 25, 50, 75, 90)] + [round(float(np.mean(a)), 6)]


for mode in MODES:
    a = agg[mode]
    s = {"bots_xrp_change_p10_25_50_75_90_mean": pc(a["sx"]), "vs_hold_xrp": pc(a["vs"]), "vs_hold_better_share": float(np.mean(np.array(a["vs"]) > 0)),
         "all_up_share": a["allup"] / NBOOT, "xrp_usd_change": pc(xchg), "per_coin": {}}
    for c in OT:
        s["per_coin"][c] = {"coin_change": pc(a["dc"][c]), "profit_xrp": pc(a["pr"][c]), "kept_coin": pc(a["kp"][c]), "sales": pc(a["sa"][c]),
                            "ratio_change": pc(a["rc"][c]), "coin_up_share": float(np.mean(np.array(a["dc"][c]) > 0))}
    OUT["boot"][mode] = s
    Pr(f"BOOT {mode} " + json.dumps(s, separators=(",", ":")))
    Pr(f"BOOT {mode} per-year bots XRP change " + json.dumps([round(x, 2) for x in a["sx"]], separators=(",", ":")))
    Pr(f"BOOT {mode} per-year vs holding (XRP) " + json.dumps([round(x, 2) for x in a["vs"]], separators=(",", ":")))
json.dump(OUT, open("/tmp/holypairr.json", "w"))
Pr(f"DONE · {time.time() - T0:.0f}s")
