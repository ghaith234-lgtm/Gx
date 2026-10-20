# 🏦🗞️📐 v3.33.0: measure the new indicators on REAL history (GitHub runner — public data, no keys, no orders, no notifications)
#   The dashboard's own code (`_pro_ls_sig` · `_pro_tk_sig` · `_pro_pc_sig` · `_pro_mv_sig` · `_mac_sig` · `_pro_grade` · `_pro_volx` · `_dta_read` · `_dxy_of`)
#   on: OKX long/short accounts (since 2024, 20 coins) · taker volume · option put/call · Deribit DVOL (since 2021) · CoinMetrics MVRV
#   (since 2019) · CBOE VIX · ECB rates ⇒ DXY · US Treasury 10y · EPU · GPR — each graded vs CHANCE on later prices (no look-ahead).
#   + FOMC decision days (federalreserve.gov) ⇒ BTC move vs a normal day · + the indicator formulas vs TA-Lib on real candles.
#   python3 ci/x33_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYX
import os, sys, json, time, math, re, shutil, tempfile, importlib.machinery, importlib.util, calendar
import requests
DASH = os.path.abspath(sys.argv[1])
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "BNB", "LTC", "LINK", "TRX", "AVAX", "DOT", "BCH", "ETC", "XLM", "ATOM", "FIL", "UNI", "NEAR", "AAVE"]
R = tempfile.mkdtemp(prefix="x33_real_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
print("HOLYX dashboard", m.APP_VERSION, flush=True)
H = {"User-Agent": "Mozilla/5.0 (HolyDashboard check)"}
DAY = 86400
G = lambda u, t=40: requests.get(u, headers=H, timeout=t)


def show(tag, g):
    if not g or g.get("g") == "short":
        print(f"HOLYX {tag}: ⏳ short sample ({(g or {}).get('n', 0)} calls)", flush=True); return
    print(f"HOLYX {tag}: hit {g['hit']}% vs chance {g['ch']}% (edge {g['edge']:+}) · {g['n']} calls · ~{g['neff']} independent · badge {g['g']}", flush=True)


def pool(gs):
    """يجمع درجات عدة عملات: الإصابة والصدفة موزونة بعدد المرات"""
    gs = [g for g in gs if g and g.get("n") and g.get("hit") is not None]
    n = sum(g["n"] for g in gs)
    if not n:
        return None
    return {"hit": round(sum(g["hit"] * g["n"] for g in gs) / n, 1), "ch": round(sum(g["ch"] * g["n"] for g in gs) / n, 1), "n": n, "coins": len(gs)}


db = {}
CL = {}
for c in COINS:
    try:
        d1, l1 = m.fc_candles(c + "-USDT", db)
        CL[c] = {int(r[0]) // DAY * DAY: float(r[4]) for r in d1}
    except Exception as e:
        CL[c] = {}
print("HOLYX daily candles:", {c: len(v) for c, v in CL.items()}, flush=True)
BTC = CL["BTC"]

# ── ⚖️ long/short accounts (contract, paged: deepest history) ──
gs = []
for c in COINS:
    rows, end = [], None
    for _ in range(14):
        try:
            d = G(f"https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio-contract?instId={c}-USDT-SWAP&period=1D&limit=100" + (f"&end={end}" if end else "")).json().get("data") or []
        except Exception:
            d = []
        d = [x for x in d if float(x[1] or 0) > 0]
        if not d:
            break
        rows += d; end = int(d[-1][0]) - 1
        time.sleep(0.25)
    ser = sorted({int(x[0]) // 1000 // DAY * DAY: float(x[1]) for x in rows}.items())
    if len(ser) < 60 or not CL.get(c):
        continue
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    g = m._pro_grade(ks, [m._pro_ls_sig(vs, i)[0] for i in range(len(vs))], CL[c], m.PRO_H["ls"])
    gs.append(g)
    show(f"⚖️ long/short {c} ({len(vs)} days)", g)
print("HOLYX ⚖️ long/short POOLED (20 coins, crowding read contrarian, judged after 3 days):", pool(gs), flush=True)

# ── 🐂 taker buy share (contracts, ~72 days) ──
gs = []
for c in COINS:
    try:
        d = G(f"https://www.okx.com/api/v5/rubik/stat/taker-volume?ccy={c}&instType=CONTRACTS&period=1D").json().get("data") or []
    except Exception:
        d = []
    ser = sorted({int(x[0]) // 1000 // DAY * DAY: [float(x[1]), float(x[2])] for x in d if float(x[1]) + float(x[2]) > 0}.items())
    if len(ser) < 20 or not CL.get(c):
        continue
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    gs.append(m._pro_grade(ks, [m._pro_tk_sig(vs, i)[0] for i in range(len(vs))], CL[c], m.PRO_H["tk"]))
    time.sleep(0.25)
print("HOLYX 🐂 taker POOLED:", pool(gs), flush=True)

# ── 🎲 put/call (72 days) ──
for c in ("BTC", "ETH"):
    d = G(f"https://www.okx.com/api/v5/rubik/stat/option/open-interest-volume-ratio?ccy={c}&period=1D").json().get("data") or []
    ser = sorted({int(x[0]) // 1000 // DAY * DAY: [float(x[1]), float(x[2])] for x in d}.items())
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    show(f"🎲 put/call {c} ({len(vs)} days)", m._pro_grade(ks, [m._pro_pc_sig(vs, i)[0] for i in range(len(vs))], CL[c], m.PRO_H["pc"]))

# ── 🌡️ DVOL (since 2021): does unusual calm precede bigger moves? ──
for c in ("BTC", "ETH"):
    end, rows = int(time.time() * 1000), []
    for _ in range(10):
        j = G(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={c}&start_timestamp=1609459200000&end_timestamp={end}&resolution=1D").json()["result"]
        rows += j.get("data") or []
        if not j.get("continuation") or not j.get("data"):
            break
        end = int(j["continuation"]); time.sleep(0.4)
    ser = sorted({int(x[0]) // 1000 // DAY * DAY: float(x[4]) for x in rows}.items())
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    fl = [(m._pro_pct(vs[max(0, i - 364):i + 1], vs[i]) or 1) <= 0.15 if i >= 60 else False for i in range(len(vs))]
    hi = [(m._pro_pct(vs[max(0, i - 364):i + 1], vs[i]) or 0) >= 0.85 if i >= 60 else False for i in range(len(vs))]
    print(f"HOLYX 🌡️ DVOL {c} ({len(vs)} days): 7-day move after unusual CALM ×{m._pro_volx(ks, fl, CL[c], 7)} · after unusual FEAR ×{m._pro_volx(ks, hi, CL[c], 7)} (vs a normal week)", flush=True)

# ── 🔗 MVRV per coin (since 2019, judged after 30 days) ──
gs = []
for c in COINS:
    j = G(f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={c.lower()}&metrics=CapMVRVCur&frequency=1d&page_size=10000&start_time=2019-01-01").json()
    d = j.get("data") or []
    ser = sorted({calendar.timegm(time.strptime(x["time"][:10], "%Y-%m-%d")): float(x["CapMVRVCur"]) for x in d}.items())
    if len(ser) < 200 or time.time() - ser[-1][0] > 10 * DAY or not CL.get(c):
        continue
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    g = m._pro_grade(ks, [m._pro_mv_sig(v) for v in vs], CL[c], m.PRO_H["mv"])
    gs.append(g); show(f"🔗 MVRV {c} ({len(vs)} days)", g)
    time.sleep(0.5)
print("HOLYX 🔗 MVRV POOLED:", pool(gs), flush=True)

# ── 🗞️ macro on BTC (7 days later) ──
def mdy(t):
    mm, dd, yy = t.split("/"); return calendar.timegm((int(yy), int(mm), int(dd), 0, 0, 0))
MAC = {}
t = G("https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv").text.splitlines()[1:]
MAC["vix"] = sorted((mdy(x.split(",")[0]), float(x.split(",")[4])) for x in t if x.count(",") >= 4)
rows = []
for yy in range(2019, time.gmtime().tm_year + 1):
    L = G(f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{yy}/all?type=daily_treasury_yield_curve&field_tdr_date_value={yy}&page&_format=csv").text.splitlines()
    hd = [h.strip().strip('"') for h in L[0].split(",")]
    ix = hd.index("10 Yr")
    rows += [(mdy(x.split(",")[0]), float(x.split(",")[ix])) for x in L[1:] if x.split(",")[ix].strip()]
    time.sleep(0.4)
MAC["us10"] = sorted(rows)
j = G("https://api.frankfurter.app/2019-01-01..?from=USD&to=EUR,JPY,GBP,CAD,SEK,CHF").json()
MAC["dxy"] = sorted((calendar.timegm(time.strptime(k, "%Y-%m-%d")), m._dxy_of(r)) for k, r in j["rates"].items())
t = G("https://www.policyuncertainty.com/media/All_Daily_Policy_Data.csv").text.splitlines()[1:]
MAC["epu"] = sorted((calendar.timegm((int(x.split(",")[2]), int(x.split(",")[1]), int(x.split(",")[0]), 0, 0, 0)), float(x.split(",")[3])) for x in t if x.count(",") >= 3)
d = m._dta_read(G("https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.dta", 60).content, ("date", "GPRD"))
b0 = calendar.timegm((1960, 1, 1, 0, 0, 0))
MAC["gpr"] = sorted((b0 + int(dd) * DAY, float(v)) for dd, v in zip(d["date"], d["GPRD"]) if dd is not None and v is not None)
print("HOLYX macro sources:", {k: f"{len(v)} days {time.strftime('%Y-%m-%d', time.gmtime(v[0][0]))}→{time.strftime('%Y-%m-%d', time.gmtime(v[-1][0]))}" for k, v in MAC.items()}, flush=True)
print(f"HOLYX 💱 DXY today (ECB formula): {MAC['dxy'][-1][1]:.2f}", flush=True)
for k, ser in MAC.items():
    ser = [(a, b) for a, b in ser if a >= calendar.timegm((2019, 1, 1, 0, 0, 0))]
    ks, vs = [a for a, _ in ser], [b for _, b in ser]
    show(f"🗞️ {k} on BTC (7 days later, {len(vs)} days)", m._pro_grade(ks, [m._mac_sig(k, vs, i)[0] for i in range(len(vs))], BTC, m.PRO_H[k]))

# ── 📅 FOMC decision days: BTC move that day vs a normal day ──
try:
    fom = set()
    for url in ["https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"] + [f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm" for y in range(2019, 2021)]:
        h = G(url).text
        for blk in re.findall(r'(\d{4}) FOMC Meetings(.*?)(?=\d{4} FOMC Meetings|$)', h, re.S):
            yy = int(blk[0])
            for mon, days_ in re.findall(r'fomc-meeting__month[^>]*>\s*<strong>([A-Za-z/]+)</strong>.*?fomc-meeting__date[^>]*>([0-9\-]+)', blk[1], re.S):
                mon = mon.split("/")[-1]
                dd = int(days_.split("-")[-1])
                try:
                    fom.add(calendar.timegm(time.strptime(f"{yy} {mon[:3]} {dd}", "%Y %b %d")))
                except Exception:
                    pass
        time.sleep(0.5)
    fom = sorted(x for x in fom if x < time.time() - DAY)
    al, on = [], []
    for k in sorted(BTC):
        c0, c1 = BTC.get(k), BTC.get(k + DAY)
        if c0 and c1:
            mv = abs(c1 / c0 - 1)
            al.append(mv)
            if k in fom:
                on.append(mv)
    print(f"HOLYX 📅 FOMC days found {len(fom)} · BTC 24h move on decision day ×{(sum(on) / len(on)) / (sum(al) / len(al)):.2f} of a normal day ({len(on)} days)" if on else f"HOLYX 📅 FOMC days parsed: {len(fom)} (none matched candles)", flush=True)
except Exception as e:
    print(f"HOLYX 📅 FOMC: error {type(e).__name__}: {e}", flush=True)

# ── 🌋 what really precedes BIG moves (size, not direction): squeeze · VIX jump · DVOL level ──
def volx(ts, flags, closes, H):
    return m._pro_volx(ts, flags, closes, H)
for tf, H, lab in (("1D", 7, "daily · next 7 days"),):
    pool_on, pool_al = [], []
    for c in COINS:
        rows = m.fc_candles(c + "-USDT", db)[0]
        if len(rows) < 300:
            continue
        D = {"t": [int(r[0]) for r in rows], "o": [r[1] for r in rows], "h": [r[2] for r in rows], "l": [r[3] for r in rows], "c": [r[4] for r in rows], "v": [r[5] for r in rows]}
        S = m._i2_series(D["o"], D["h"], D["l"], D["c"], D["v"])
        sq = m._fc_sq(D, S)
        C = D["c"]
        for t in range(30, len(C) - H):
            mv = abs(C[t + H] / C[t] - 1)
            pool_al.append(mv)
            if sq[t]:
                pool_on.append(mv)
    print(f"HOLYX ⚡ squeeze ({lab}, 20 coins): move after squeeze ×{(sum(pool_on) / len(pool_on)) / (sum(pool_al) / len(pool_al)):.2f} of normal ({len(pool_on)} squeeze days)", flush=True)
vks = [a for a, _ in MAC["vix"] if a >= calendar.timegm((2019, 1, 1, 0, 0, 0))]
vvs = [b for a, b in MAC["vix"] if a >= calendar.timegm((2019, 1, 1, 0, 0, 0))]
jump = [i >= 5 and vvs[i] / vvs[i - 5] - 1 >= 0.25 for i in range(len(vvs))]
print(f"HOLYX 😱 VIX jump ≥25% in 5 days ⇒ BTC 7-day move ×{volx(vks, jump, BTC, 7)}", flush=True)
for c in ("BTC",):
    end, rows = int(time.time() * 1000), []
    for _ in range(10):
        j = G(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={c}&start_timestamp=1609459200000&end_timestamp={end}&resolution=1D").json()["result"]
        rows += j.get("data") or []
        if not j.get("continuation") or not j.get("data"):
            break
        end = int(j["continuation"]); time.sleep(0.4)
    ser = sorted({int(x[0]) // 1000 // DAY * DAY: float(x[4]) for x in rows}.items())
    ks, vs = [k for k, _ in ser], [v for _, v in ser]
    q = sorted(vs)
    lo, hi = q[len(q) // 5], q[4 * len(q) // 5]
    print(f"HOLYX 🌡️ DVOL {c} absolute level: top-fifth days ⇒ 7-day move ×{volx(ks, [v >= hi for v in vs], CL[c], 7)} · bottom-fifth ×{volx(ks, [v <= lo for v in vs], CL[c], 7)} (implied vol as a SIZE forecast)", flush=True)
    real = []
    for k, v in zip(ks, vs):
        c0, c1 = CL[c].get(k), CL[c].get(k + 30 * DAY)
        if c0 and c1:
            real.append((v / math.sqrt(365 / 30), abs(math.log(c1 / c0)) * 100))
    inside = sum(1 for a, b in real if b <= a) / len(real) * 100 if real else None
    print(f"HOLYX 🌡️ DVOL {c}: the 30-day move stayed inside ±DVOL·√(30/365) in {inside:.0f}% of {len(real)} days (a 1-σ band ≈ 68% if DVOL is right)", flush=True)

# ── 📐 formulas vs TA-Lib on REAL candles (BTC daily) ──
try:
    import numpy as np, talib
    rows = m.fc_candles("BTC-USDT", db)[0][-700:]
    O, Hh, L, C, V = ([float(r[i]) for r in rows] for i in (1, 2, 3, 4, 5))
    S = m._i2_series(O, Hh, L, C, V)
    o, h, l, c = (np.array(x) for x in (O, Hh, L, C))
    W = 260
    def mx(a, b, rel=False):
        d = [abs(x - y) / (abs(y) if rel else 1) for x, y in zip(a[W:], b[W:]) if x is not None and not math.isnan(y)]
        return max(d) if d else float("nan")
    res = {"RSI14": mx(S["rsi"], talib.RSI(c, 14)), "ATR14": mx(S["atr"], talib.ATR(h, l, c, 14), True), "MACD hist": mx(S["hist"], talib.MACD(c, 12, 26, 9)[2]),
           "ADX14": mx(S["adx"], talib.ADX(h, l, c, 14)), "+DI": mx(S["pdi"], talib.PLUS_DI(h, l, c, 14)), "-DI": mx(S["ndi"], talib.MINUS_DI(h, l, c, 14)),
           "EMA200": mx(m._i2_ema(C, 200), talib.EMA(c, 200), True)}
    print("HOLYX 📐 vs TA-Lib on real BTC candles (max difference after warm-up):", {k: f"{v:.2g}" for k, v in res.items()}, "⇒", "ALL MATCH" if all(v < 1e-6 for v in res.values()) else "DIFFERENCES", flush=True)
except Exception as e:
    print(f"HOLYX 📐 TA-Lib check skipped: {type(e).__name__}: {e}", flush=True)
print("HOLYX done", flush=True)
