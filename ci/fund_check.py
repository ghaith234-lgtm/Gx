# 💸 v3.36.29 — the owner (8-11): «ايهم يربح اكثر المراجحه التمويل ام البوتات الشبكية وهل فقط بالusdt ام عادي بالعملات تربح»
#   REAL OKX data (GitHub · public market data · no keys · no orders · no notifications), the last 3 months (OKX keeps 3 months of
#   funding history):
#   A. funding arbitrage per coin (coin spot + short perpetual of the same size): the funding the short received — USDT-margined
#      (X-USDT-SWAP, paid in USDT) and coin-margined (X-USD-SWAP, paid in the coin) · % of payments positive · the longest negative run ·
#      the worst week · the yield on the capital after the entry/exit fees, with the spot as the short's collateral (unified account) and
#      with half the money as margin (a plain account)
#   B. a ♾️ grid on the SAME 3 months of the same coins through the dashboard's own trial path on real candles (15-minute): trading profit ·
#      real profit · holding · bot vs holding — as % of the wallet
#   python3 ci/fund_check.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYFUND
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC", "ETH", "XRP", "SOL", "DOGE", "ADA", "LTC", "LINK", "TRX", "BCH"]
GRID = ["BTC", "ETH", "XRP", "SOL", "DOGE"]
if FAKE:
    COINS, GRID = ["BTC", "XRP"], ["XRP"]
FEE_T = 2 * 0.001 + 2 * 0.0005                    # taker: spot in/out 0.10% · perpetual in/out 0.05%
FEE_M = 2 * 0.0008 + 2 * 0.0002                   # maker: 0.08% · 0.02%
R = tempfile.mkdtemp(prefix="fund_real_")
json.dump({"port": 8098}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYFUND", *a, flush=True)


if FAKE:
    NOW = int(time.time())

    def _P(t):
        return 1.17 * (1 + 0.025 * math.sin(t / 21600.0) + 0.006 * math.sin(t / 1700.0))

    def _rows(sym, bar, after=None, hist=True, limit=100):
        sec, now = {"15m": 900}[bar], int(time.time())
        ts = (min(int(after // 1000) if after else now, now) - 1) // sec * sec
        out = []
        while len(out) < 100 and ts >= NOW - 200 * 86400:
            o, c = _P(ts), _P(ts + sec)
            out.append([ts, o, max(o, c) * 1.0015, min(o, c) * 0.9985, c, 1000.0, ts + sec <= now])
            ts -= sec
        return out

    def _pub(p):
        if "instruments" in p:
            return {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]}
        if "ticker" in p:
            return {"code": "0", "data": [{"last": str(_P(time.time()))}]}
        if "funding-rate-history" in p:
            aft = int(p.split("after=")[1].split("&")[0]) if "after=" in p else NOW * 1000
            out, t = [], (aft // 28800000) * 28800000
            if t == aft:
                t -= 28800000
            while len(out) < 100 and t > (NOW - 92 * 86400) * 1000:
                out.append({"fundingTime": str(t), "realizedRate": str(0.0001 * (1 + math.sin(t / 3e8)))})
                t -= 28800000
            return {"code": "0", "data": out}
        return None

    m._fc_okx_rows = _rows
    m._okx_pub = _pub
    m._okx_get = lambda *a, **k: None


def funding(inst):
    """every funding payment of the last 3 months (oldest first): [(ms, rate)]"""
    out, after = {}, None
    for _ in range(40):
        r = m._okx_pub(f"/api/v5/public/funding-rate-history?instId={inst}&limit=100" + (f"&after={after}" if after else ""))
        d = (r or {}).get("data") or []
        if not d:
            break
        for x in d:
            try:
                rt = x.get("realizedRate")
                rt = float(rt) if rt not in (None, "") else float(x.get("fundingRate") or 0)
                out[int(x["fundingTime"])] = rt
            except Exception:
                continue
        after = min(int(x["fundingTime"]) for x in d)
        time.sleep(0.25)
    return sorted(out.items())


# ── A. funding arbitrage
SUM = {}
for c in COINS:
    for kind, inst in (("USDT", f"{c}-USDT-SWAP"), ("coin", f"{c}-USD-SWAP")):
        f = funding(inst)
        if len(f) < 10:
            P_(f"A {inst}: no funding history ({len(f)})"); continue
        days = (f[-1][0] - f[0][0]) / 86400000.0 + 8 / 24.0
        tot = sum(r for _, r in f)
        pos = sum(1 for _, r in f if r > 0) / len(f) * 100
        run, worst_run, t_run0 = 0.0, 0.0, None
        for t, r in f:
            if r < 0:
                t_run0 = t if t_run0 is None else t_run0
                worst_run = max(worst_run, (t - t_run0) / 86400000.0 + 8 / 24.0)
            else:
                t_run0 = None
        wk = []
        for i in range(len(f)):
            j = i
            s = 0.0
            while j < len(f) and f[j][0] - f[i][0] < 7 * 86400000:
                s += f[j][1]; j += 1
            if f[-1][0] - f[i][0] >= 7 * 86400000:
                wk.append(s)
        months = {}
        for t, r in f:
            k = time.strftime("%Y-%m", time.gmtime(t / 1000))
            months[k] = months.get(k, 0.0) + r
        ann = tot / days * 365 * 100
        net_t, net_m = (tot - FEE_T) * 100, (tot - FEE_M) * 100
        SUM[(c, kind)] = {"days": days, "tot": tot * 100, "ann": ann, "net_t": net_t, "net_m": net_m}
        P_(f"A {inst} ({'paid in USDT' if kind == 'USDT' else 'paid in ' + c}): {len(f)} payments over {days:.0f} days · received {tot * 100:+.3f}% "
           f"(≈ {ann:+.1f}%/year) · positive {pos:.0f}% · longest negative run {worst_run:.1f} days · worst week {min(wk) * 100 if wk else 0:+.3f}% · "
           f"best 8h {max(r for _, r in f) * 100:+.4f}% · worst 8h {min(r for _, r in f) * 100:+.4f}% · by month "
           + " ".join(f"{k}:{v * 100:+.3f}%" for k, v in sorted(months.items()))
           + f" · AFTER FEES on the capital: unified account (spot = collateral) taker {net_t:+.3f}% / maker {net_m:+.3f}% · plain account (half as margin) "
             f"taker {net_t / 2:+.3f}% / maker {net_m / 2:+.3f}% for the {days:.0f} days")

# ── B. a ♾️ grid on the same 3 months (the dashboard's own trial path on real 15-minute candles)
GR = {}
for c in GRID:
    sym = f"{c}-USDT"
    try:
        live = float(((m._okx_pub(f"/api/v5/market/ticker?instId={sym}") or {}).get("data") or [{}])[0].get("last") or 0)
    except Exception:
        live = 0.0
    if live <= 0:
        P_(f"B {sym}: no price"); continue
    m.PX[sym] = live
    for gp in ("0.6", "1.2"):
        body = {"symbol": sym, "grid_pct": gp, "usd_value": "25", "min_price": repr(live * 0.4), "wallet": "main", "g_type": "grid"}
        pr = m.bt_prep({"kind": "grid", "body": body})
        if not pr.get("ok"):
            P_(f"B {sym} {gp}%: {pr.get('msg')}"); continue
        S = m.bt_start({"kind": "grid", "body": body, "period": "q3", "mood": "real", "paths": 1, "seed": "1", "p0": pr["p0"], "quote": pr["quote_def"],
                        "base": pr["base_def"], "maker": "0.08", "taker": "0.1", "slip": "0.05"})
        if not S.get("ok"):
            P_(f"B {sym} {gp}%: {S.get('msg')}"); continue
        a0, st = time.time(), {}
        while time.time() - a0 < 1800:
            st = m.bt_status({"id": S["id"]})
            if st.get("state") in ("done", "error", "stopped", "lost"):
                break
            time.sleep(1)
        if st.get("state") != "done" or not st.get("paths"):
            P_(f"B {sym} {gp}%: {st.get('state')} {st.get('err')}"); continue
        s = st["paths"][0]["sum"]
        v0 = s["q0"] + s["b0"] * s["p0"]
        tr = float(s["trade"]) / v0 * 100
        GR[(c, gp)] = {"trade": tr, "real": s["pnl_pct"], "hold": s["hold"] / v0 * 100, "vs": s["vs"] / v0 * 100}
        P_(f"B grid {gp}% {sym} {time.strftime('%m-%d', time.gmtime(s['t0']))}→{time.strftime('%m-%d', time.gmtime(s['t1']))}: price {s['p0']:.6g}→{s['p_end']:.6g} "
           f"({(s['p_end'] / s['p0'] - 1) * 100:+.1f}%) · wallet {v0:.0f}$ ({s['q0']:.0f}$ + {s['b0']:.6g} {c}) · trades {s['buys']}/{s['sells']} · "
           f"trading profit {float(s['trade']):+.2f}$ = {tr:+.2f}% · REAL {s['pnl']:+.2f}$ = {s['pnl_pct']:+.2f}% · holding {s['hold'] / v0 * 100:+.2f}% · "
           f"bot vs holding {s['vs'] / v0 * 100:+.2f}% · fees {s['fee_usd']:.2f}$ · lowest wallet {s['low']:.0f}$")

# ── side by side
for c in GRID:
    fu = SUM.get((c, "USDT")) or {}
    g6, g12 = GR.get((c, "0.6")) or {}, GR.get((c, "1.2")) or {}
    P_(f"VS {c}: funding arbitrage (unified · taker fees) {fu.get('net_t', float('nan')):+.2f}% in {fu.get('days', 0):.0f} days — no price risk · "
       f"grid 0.6%: trading {g6.get('trade', float('nan')):+.2f}% · real {g6.get('real', float('nan')):+.2f}% (holding {g6.get('hold', float('nan')):+.2f}%) · "
       f"grid 1.2%: trading {g12.get('trade', float('nan')):+.2f}% · real {g12.get('real', float('nan')):+.2f}%")
P_("RESULT done")
shutil.rmtree(R, ignore_errors=True)
