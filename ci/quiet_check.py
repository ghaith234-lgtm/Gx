# 😴 the owner (10-11): «اغلب الاوقات السوق ميت هل راح يفيدني السكالبينج هذا» — the 🪜 graded grid on quiet vs busy days.
#   REAL OKX public data (GitHub · no keys · no orders): the last 90 days of XRP-USDT on 5-minute candles (each walked open/low/high/close)
#   · the REAL 🪜 engine in the trial box with the owner's two settings (3 sells · first 0.3% · then 0.2%): A 25$ · buys every 0.6% ·
#   B 12.5$ · buys every 0.3% · every day sorted by its own range (high−low) · per kind of day: how many days, sells per day, the engine's
#   booked profit per day · the whole period: trades, trading profit, real profit, holding
#   python3 ci/quiet_check.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYQUIET
import importlib.machinery, importlib.util, json, math, os, shutil, statistics, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
DAYS = 5 if FAKE else 90
R = tempfile.mkdtemp(prefix="quiet_")
json.dump({"port": 8108}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "K", "sec": "S", "pass": "P"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
P_ = lambda *a: print("HOLYQUIET", *a, flush=True)
SYM = "XRP-USDT"
if FAKE:
    NOW = int(time.time())

    def _P(t):
        return 1.10 * (1 + 0.01 * math.sin(t / 9000.0) + 0.004 * math.sin(t / 1300.0))

    def _rows(sym, bar, after=None, hist=True, limit=100):
        sec, now = 300, int(time.time())
        ts = (min(int(after // 1000) if after else now, now) - 1) // sec * sec
        out = []
        while len(out) < 100 and ts >= NOW - 30 * 86400:
            o, c = _P(ts), _P(ts + sec)
            out.append([ts, o, max(o, c) * 1.0008, min(o, c) * 0.9992, c, 1000.0, ts + sec <= now])
            ts -= sec
        return out
    m._fc_okx_rows = _rows
    m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "1"}]} if "instruments" in p else None)
m._okx_get = lambda *a, **k: None
spec = m._bt_spec(SYM)
P_(f"spec {spec}")
sec = 300
t1 = int(time.time()) // sec * sec
t0 = t1 - DAYS * 86400
rows = m._bt_hist(SYM, "5m", sec, t0, t1)
W = {"o": [r_[1] for r_ in rows], "h": [r_[2] for r_ in rows], "l": [r_[3] for r_ in rows], "c": [r_[4] for r_ in rows]}
px = m._bt_ohlc(W)
p0 = px[0]
P_(f"{len(rows)} five-minute candles · {time.strftime('%Y-%m-%d', time.gmtime(t0))} → {time.strftime('%Y-%m-%d', time.gmtime(t1))} · XRP {p0:.4f} → {W['c'][-1]:.4f} · "
   f"low {min(W['l']):.4f} high {max(W['h']):.4f}")
per_day = int(86400 / sec)
rng = []
for d in range(len(rows) // per_day):
    hs, ls = W["h"][d * per_day:(d + 1) * per_day], W["l"][d * per_day:(d + 1) * per_day]
    rng.append((max(hs) - min(ls)) / min(ls) * 100)
BK = [(0, 2, "dead (<2%)"), (2, 3, "quiet (2–3%)"), (3, 5, "normal (3–5%)"), (5, 8, "busy (5–8%)"), (8, 999, "wild (>8%)")]
P_("days by their range: " + " · ".join(f"{lb} {sum(1 for x in rng if a <= x < b)}" for a, b, lb in BK) + f" · median range {statistics.median(rng):.2f}%")
KEEP = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
dt = sec / 4.0
HI = max(W["h"]) * 1.02                          # the levels above cover the whole period (the bot never leaves its range)
for nm, q, g in (("A 25$ · buys every 0.6%", "25", "0.6"), ("B 12.5$ · buys every 0.3%", "12.5", "0.3")):
    up = int(math.ceil(math.log(HI / p0) / math.log(1 + float(g) / 100)))
    body = {"symbol": SYM, "usd_value": q, "step_parts": "3", "step_first_pct": "0.3", "step_sell_pct": "0.2", "grid_pct": g, "up_groups": str(up),
            "min_price": repr(round(p0 * 0.75, 4)), "forced_base": "", "wallet": "main", "auto": False}
    m.PX[SYM] = p0
    cfg, err = m._bt_dry_cfg("grid_step", body, SYM, spec, p0)
    for k, v in KEEP.items():
        setattr(m, k, v)
    if not cfg:
        P_(f"{nm}: {err}"); continue
    q0, b0 = m._bt_wallet_def("grid_step", None, body, p0, spec)
    a0 = time.time()
    r = m._bt_run("grid_step", cfg, SYM, px, dt, q0, b0, spec)
    S = m._bt_summary("grid_step", r, q0, b0, p0, dt)
    pe = float(r["curve"][-1][1])
    pnl = r["ex"].bal[r["ex"].quote] + r["ex"].bal[r["ex"].base] * pe - (q0 + b0 * p0)
    sells_d = [0] * len(rng)
    for f in r["ex"].fills:
        d = int((f[0] - m._BT_T0) / 86400)
        if f[1] == "sell" and 0 <= d < len(rng):
            sells_d[d] += 1
    prof_d = [0.0] * len(rng)
    for i, v in r["pops"]:
        d = int(i * dt / 86400)
        if 0 <= d < len(rng):
            prof_d[d] += v
    tot = sum(prof_d) or 1e-9
    P_(f"{nm}: {up} levels above (to {HI:.3f}) · wallet {q0:.0f}$ + {b0:.1f} XRP · {S['buys']} buys / {S['sells']} sells · trading profit {float(S['trade']):+.2f}$ "
       f"(≈ {float(S['trade']) / DAYS * 30:+.2f}$ a month) · real {pnl:+.2f}$ · holding {b0 * (pe - p0):+.2f}$ · most dollars in use {S['used_max']:.0f}$ · "
       f"fees {S['fee_usd']:.2f}$ · {time.time() - a0:.0f}s")
    for a, b, lb in BK:
        ix = [d for d, x in enumerate(rng) if a <= x < b]
        if not ix:
            continue
        P_(f"   {nm} · {lb}: {len(ix)} days ({sum(1 for d in ix if not sells_d[d])} without a sell) · sells/day {statistics.mean(sells_d[d] for d in ix):.1f} · profit/day {statistics.mean(prof_d[d] for d in ix):+.3f}$ "
           f"(median {statistics.median(prof_d[d] for d in ix):+.3f}$) · {sum(prof_d[d] for d in ix) / tot * 100:.0f}% of the profit")
P_("RESULT done")
shutil.rmtree(R, ignore_errors=True)
