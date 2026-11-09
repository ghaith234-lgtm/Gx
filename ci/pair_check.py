# 🔀 the owner (9-11): «اريد مثلا sol مع xrp» — a grid between two coins. REAL OKX public data (GitHub · no keys · no orders):
#   ① is there a direct SOL-XRP / XRP-SOL spot pair? (else each swap goes through USDT: two trades, double fee) · the direct pairs of each
#   ② the SOL/XRP ratio vs XRP-USDT and SOL-USDT alone, last year (1H closes) and last 3 months (15m closes): how many completed grid
#      cycles (a step down then back up) at 1% · 1.5% · 2% · 3% · the gain per order after fees (via USDT: 4 trades · direct: 2) ·
#      where the ratio ended vs its start (the drift that leaves you holding the weaker coin)
#   python3 ci/pair_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYPAIR
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="pair_")
json.dump({"port": 8103}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
P_ = lambda *a: print("HOLYPAIR", *a, flush=True)

for inst in ("SOL-XRP", "XRP-SOL", "XRP-BTC", "SOL-BTC", "XRP-ETH", "SOL-ETH"):
    r = m._okx_pub(f"/api/v5/public/instruments?instType=SPOT&instId={inst}")
    d = (r or {}).get("data") or []
    P_(f"pair {inst}: {'EXISTS ' + json.dumps({k: d[0].get(k) for k in ('state', 'minSz', 'tickSz')}) if d else 'none'} (code {(r or {}).get('code')})")
allsp = ((m._okx_pub("/api/v5/public/instruments?instType=SPOT") or {}).get("data")) or []
for c in ("XRP", "SOL"):
    P_(f"direct pairs of {c}: {sorted(x['instId'] for x in allsp if x.get('baseCcy') == c or x.get('quoteCcy') == c)}")


def cycles(series, step):
    lv0 = math.floor(math.log(series[0]) / math.log(1 + step))
    cur, open_, done = lv0, 0, 0
    for v in series[1:]:
        lv = math.floor(math.log(v) / math.log(1 + step))
        while lv < cur:
            cur -= 1; open_ += 1
        while lv > cur:
            cur += 1
            if open_ > 0:
                open_ -= 1; done += 1
    return done, open_


now = int(time.time())
for lbl, bar, sec, days in (("last year · 1H closes", "1H", 3600, 365), ("last 3 months · 15m closes", "15m", 900, 91)):
    t1 = now // sec * sec
    t0 = t1 - days * 86400
    S = {r_[0]: r_[4] for r_ in m._bt_hist("SOL-USDT", bar, sec, t0, t1)}
    X = {r_[0]: r_[4] for r_ in m._bt_hist("XRP-USDT", bar, sec, t0, t1)}
    ts = sorted(set(S) & set(X))
    ser = {"SOL/XRP ratio (via USDT)": [S[t] / X[t] for t in ts], "XRP-USDT": [X[t] for t in ts], "SOL-USDT": [S[t] for t in ts]}
    P_(f"{lbl}: {len(ts)} candles")
    for nm, s in ser.items():
        fee = 0.0032 if "ratio" in nm else 0.0016
        row = []
        for st in (0.01, 0.015, 0.02, 0.03):
            d, o = cycles(s, st)
            row.append(f"{st * 100:g}%: {d} cycles · {d * (st - fee) * 100:+.1f}% per order (fee {fee * 100:.2f}%/cycle) · {o} still open")
        P_(f"  {nm}: start {s[0]:.6g} end {s[-1]:.6g} ({(s[-1] / s[0] - 1) * 100:+.1f}%) · low {min(s):.6g} high {max(s):.6g} · " + " | ".join(row))
P_("RESULT done")
shutil.rmtree(R, ignore_errors=True)
