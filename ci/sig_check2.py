# 🔬 v3.36.27 phase 1, second pass — what the first pass (sig_check.py) found, measured closer on REAL OKX prices (GitHub · public data · no
#   keys · no orders · no notifications), every past candle seeing only what came before it:
#   D 🔄 the bounce: on every horizon, by how strongly the indicators lean (strong down · down · flat · up · strong up) ⇒ how often the
#     price was higher at the end, and by how much, against the coin's normal candle — all of history · by calendar year · per coin
#   E 🟢 bottom candidates (daily, days to weeks): RSI · Bollinger · drawdown · short-term oversold (3/7-day move in the coin's own
#     volatility) · the daily indicators leaning strongly down · each one in an UPTREND (above the 200-day average) and in a downtrend ·
#     against the normal day of the same kind (all · uptrend · downtrend · the last 40% of time) · by calendar year
#   python3 ci/sig_check2.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG2
import bisect, importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
         "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "HBAR-USDT", "ICP-USDT", "INJ-USDT", "SHIB-USDT"]
if FAKE:
    COINS = COINS[:3]
R = tempfile.mkdtemp(prefix="sig2_real_")
json.dump({"port": 8097}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG2", *a, flush=True)


if FAKE:
    _SER = {}

    def _series(sym, bar):
        k = (sym, bar)
        if k not in _SER:
            dt = {"1H": 3600, "4H": 14400, "1Dutc": 86400}[bar]
            n = {"1H": 9000, "4H": 4500, "1Dutc": 2100}[bar]
            rnd = random.Random(hash(k) % 1000)
            t1 = int(time.time()) // dt * dt
            p, out = 1.0 + rnd.random(), []
            for i in range(n):
                o = p; p = max(1e-6, p * math.exp(rnd.gauss(0, 0.012 * math.sqrt(dt / 3600))))
                out.append([t1 - (n - 1 - i) * dt, o, max(o, p) * 1.003, min(o, p) * 0.997, p, 1000 * (1 + rnd.random())])
            _SER[k] = out
        return _SER[k]

    def _fake_pub(path):
        import urllib.parse as up
        q = dict(up.parse_qsl(path.split("?", 1)[1])) if "?" in path else {}
        if "candles" not in path:
            return None
        s = _series(q["instId"], q["bar"])
        after = int(q.get("after") or 0) // 1000
        rows = [r for r in s if (not after or r[0] < after)][-int(q.get("limit") or 100):]
        return {"code": "0", "data": [[str(r[0] * 1000), repr(r[1]), repr(r[2]), repr(r[3]), repr(r[4]), repr(r[5]), "0", "0", "1"] for r in reversed(rows)]}
    m._okx_pub = _fake_pub
    m._http_json = lambda *a, **k: None


def hist(sym, bar, maxn):
    rows = {}
    for c in m._fc_okx_rows(sym, bar, hist=False, limit=100):
        if c[6]:
            rows[c[0]] = c[:6]
    oldest = min(rows) if rows else None
    while oldest and len(rows) < maxn:
        pg = [c for c in m._fc_okx_rows(sym, bar, after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
        if not pg:
            break
        for c in pg:
            rows[c[0]] = c[:6]
        oldest = min(rows)
        if not FAKE:
            time.sleep(0.11)
    return [rows[k] for k in sorted(rows)][-maxn:]


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else 0.0


def yr(ts):
    return time.gmtime(ts).tm_year


T0 = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· fake" if FAKE else "· REAL OKX")
db = {}
fng = m._fc_fng(db) if not FAKE else None
DATA = {}
for sym in COINS:
    try:
        d1, h4 = hist(sym, "1Dutc", 2000), hist(sym, "4H", 4400)
    except Exception as ex:
        P_(f"{sym}: fetch error {ex}"); continue
    if len(d1) < 400:
        P_(f"{sym}: short ({len(d1)} days)"); continue
    DATA[sym] = {"d1": d1, "h4": h4}
P_(f"fetched {len(DATA)} coins in {time.time() - T0:.0f}s")

# ═════════════════════ D 🔄 the bounce by lean strength ═════════════════════
BK = (("sd", "strong down"), ("d", "down"), ("f", "flat"), ("u", "up"), ("su", "strong up"))
D = {}                      # k ⇒ {"all": [rets], bk: [(ret, year, sym)]}
VOTE_1D = {}                # sym ⇒ {day ts: vote key} (the week horizon reads daily candles — reused by E)
for sym, Dd in DATA.items():
    d1, h4 = Dd["d1"], Dd["h4"]
    g3, _ = m._fc_group(d1, None, 3, 0)
    gw, _ = m._fc_group(d1, None, 7, 3)
    tfr = {"4H": h4, "1D": d1, "3D": g3, "1W": gw}
    for k, nm, tf, H, dd in m.FC_H:
        rows = tfr[tf]
        if len(rows) < m.FC_MIN[tf] + H:
            continue
        X = {"H": H, "hn": nm, "fng": fng, "fund": None}
        Pn = m._fc_pack(rows, tfr[m.FC_TRD[k]], m.FC_TFS[tf], m.FC_TFS[m.FC_TRD[k]])
        C, T = Pn["D"]["c"], Pn["D"]["t"]
        e = D.setdefault(k, {"all": []})
        for t in range(m.FC_WARM[tf], len(rows)):
            sig, _ = m._fc_read(Pn, t, k, X)
            vk = m._fc_vote(sig)[3]
            if k == "w":
                VOTE_1D.setdefault(sym, {})[T[t]] = vk
            if t + H >= len(rows) or not C[t]:
                continue
            ret = C[t + H] / C[t] - 1.0
            e["all"].append((ret, yr(T[t]), sym))
            e.setdefault(vk, []).append((ret, yr(T[t]), sym))
P_(f"D recorded in {time.time() - T0:.0f}s")


def line(v, base):
    if not v:
        return "—"
    up = sum(1 for r in v if r[0] > 0) / len(v) * 100
    bu = sum(1 for r in base if r[0] > 0) / max(1, len(base)) * 100
    return (f"n {len(v):6d} · higher {up:.1f}% (normal {bu:.1f}%, {'+' if up >= bu else ''}{up - bu:.1f}) · mean {sum(r[0] for r in v) / len(v) * 100:+.2f}% "
            f"(normal {sum(r[0] for r in base) / max(1, len(base)) * 100:+.2f}%) · median {med([r[0] for r in v]) * 100:+.2f}%")


for k, nm, tf, H, dd in m.FC_H:
    e = D.get(k)
    if not e:
        continue
    P_(f"===== D 🔄 {k} {nm} ({tf} · {H} ahead) — after the indicators lean …")
    for bk, lbl in BK:
        P_(f"  {lbl:11s} {line(e.get(bk), e['all'])}")
    years = sorted({r[1] for r in e["all"]})
    for bk in ("sd", "su"):
        cells = []
        for y in years:
            v = [r for r in e.get(bk, []) if r[1] == y]
            b = [r for r in e["all"] if r[1] == y]
            if len(v) >= 20:
                up = sum(1 for r in v if r[0] > 0) / len(v) * 100
                bu = sum(1 for r in b if r[0] > 0) / len(b) * 100
                cells.append(f"{y} {up:.0f}% vs {bu:.0f}% ({len(v)})")
        P_(f"  by year after «{dict(BK)[bk]}»: " + " · ".join(cells))
        pos = tot = 0
        for sym in DATA:
            v = [r for r in e.get(bk, []) if r[2] == sym]
            b = [r for r in e["all"] if r[2] == sym]
            if len(v) >= 15 and b:
                tot += 1
                upv = sum(1 for r in v if r[0] > 0) / len(v)
                ub = sum(1 for r in b if r[0] > 0) / len(b)
                pos += 1 if ((upv > ub) if bk == "sd" else (upv < ub)) else 0
        P_(f"  coins where «{dict(BK)[bk]}» was followed by the opposite more than normal: {pos}/{tot}")

# ═════════════════════ E 🟢 bottom candidates (daily) ═════════════════════
CANDS = ["rsi30", "rsi25", "bb", "dd", "z3", "z3s", "z7", "vote_sd", "vote_sd_z3", "rsi30_bb"]
EV = {}                     # (cand, regime) ⇒ [(r7, r14, r30, mae, year, frac)]
BASE = {}                   # regime ⇒ same
for sym, Dd in DATA.items():
    d1 = Dd["d1"]
    T, O, H, L, C, V = ([r[i] for r in d1] for i in range(6))
    S = m._i2_series(O, H, L, C, V)
    n = len(C)
    e200 = m._i2_ema(C, 200)
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, n)]
    vt = VOTE_1D.get(sym, {})
    last = {}
    for t in range(210, n - 31):
        if not e200[t]:
            continue
        o = (C[t + 7] / C[t] - 1, C[t + 14] / C[t] - 1, C[t + 30] / C[t] - 1, min(L[t + 1:t + 31]) / C[t] - 1, yr(T[t]), t / n)
        reg = "up" if C[t] > e200[t] else "down"
        for rg in ("all", reg) + (("last40",) if t / n >= 0.6 else ()):
            BASE.setdefault(rg, []).append(o)
        rs = lr[t - 59:t + 1]; rm = sum(rs) / 60; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 59) or 1e-9
        z3 = math.log(C[t] / C[t - 3]) / (sd * math.sqrt(3)); z7 = math.log(C[t] / C[t - 7]) / (sd * math.sqrt(7))
        w = C[t - 19:t + 1]; mu = sum(w) / 20; sdp = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
        rsi = S["rsi"][t]
        hi90 = max(H[t - 89:t + 1])
        c = {"rsi30": rsi is not None and rsi <= 30, "rsi25": rsi is not None and rsi <= 25, "bb": C[t] < mu - 2 * sdp,
             "dd": (1 - C[t] / hi90) / (sd * math.sqrt(20)) >= 1.5, "z3": z3 <= -2.0, "z3s": z3 <= -2.5, "z7": z7 <= -2.0,
             "vote_sd": vt.get(T[t]) == "sd"}
        c["vote_sd_z3"] = c["vote_sd"] and z3 <= -1.5
        c["rsi30_bb"] = c["rsi30"] and c["bb"]
        for k_, on in c.items():
            if on:
                if t - last.get(k_, -99) >= 5:                      # an episode: the first day after 5 quiet days
                    for rg in ("all", reg) + (("last40",) if t / n >= 0.6 else ()):
                        EV.setdefault((k_, rg), []).append(o)
                last[k_] = t
P_(f"E recorded in {time.time() - T0:.0f}s")


def eline(v, b):
    if not v:
        return "—"
    f = lambda a, i: sum(1 for x in a if x[i] > 0) / len(a) * 100
    return (f"n {len(v):4d} · higher 7d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 14d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 30d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f})"
            f" · median 14d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · median drop first {med([x[3] for x in v]) * 100:.1f}%"
            f" (normal {med([x[3] for x in b]) * 100:.1f}%)")


P_(f"===== E 🟢 bottom candidates — daily · {len(DATA)} coins · (±) = points vs the normal day of the same kind")
for rg, lbl in (("all", "all days"), ("up", "UPTREND (above the 200-day average)"), ("down", "downtrend"), ("last40", "last 40% of time")):
    P_(f"  ── {lbl}: normal day {eline(BASE.get(rg, []), BASE.get(rg, []))}")
    for c in CANDS:
        P_(f"  {c:11s} {eline(EV.get((c, rg)), BASE.get(rg, []))}")
for c in CANDS:
    for rg in ("all", "up"):
        v = EV.get((c, rg)) or []
        cells = []
        for y in sorted({x[4] for x in v}):
            a = [x for x in v if x[4] == y]
            b = [x for x in BASE.get(rg, []) if x[4] == y]
            if len(a) >= 8 and b:
                cells.append(f"{y} {sum(1 for x in a if x[1] > 0) / len(a) * 100:.0f}% vs {sum(1 for x in b if x[1] > 0) / len(b) * 100:.0f}% ({len(a)})")
        P_(f"  by year {c} [{rg}] 14d: " + " · ".join(cells))
P_(f"done in {time.time() - T0:.0f}s · notifications sent: {len(sent)}")
shutil.rmtree(R, ignore_errors=True)
