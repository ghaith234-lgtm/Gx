# 🔬 v3.36.27 phase 1, third pass — the 🟢 bottom score built only from what the second pass found (REAL OKX prices · GitHub · public data ·
#   no keys · no orders · no notifications · every day sees only what came before it):
#   parts: a 7-day drop of more than 2× the coin's usual weekly move (z7) · RSI ≤ 25 / ≤ 30 · below the lower Bollinger band · a 3-day
#   drop of more than 2.5× (z3) · the daily indicators leaning strongly down — two weightings, levels 30…70
#   ⇒ 7 / 14 / 30 days later higher? median move · the drop before the rise · by calendar year · per coin · the last 40% of time ·
#   with Bitcoin above / below its 200-day average · without a confirmation, with the first daily close above the previous day's high
#   (≤ 5 days), with the first 4-hour close above its 20-candle average (≤ 3 days)
#   python3 ci/sig_check3.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG3
import bisect, importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
         "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "HBAR-USDT", "ICP-USDT", "INJ-USDT", "SHIB-USDT"]
if FAKE:
    COINS = COINS[:3]
R = tempfile.mkdtemp(prefix="sig3_real_")
json.dump({"port": 8096}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG3", *a, flush=True)


if FAKE:
    _SER = {}

    def _series(sym, bar):
        k = (sym, bar)
        if k not in _SER:
            dt = {"4H": 14400, "1Dutc": 86400}[bar]
            n = {"4H": 4500, "1Dutc": 2100}[bar]
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


T0 = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· fake" if FAKE else "· REAL OKX")
DATA = {}
for sym in COINS:
    try:
        d1, h4 = hist(sym, "1Dutc", 2000), hist(sym, "4H", 4400)
    except Exception as ex:
        P_(f"{sym}: fetch error {ex}"); continue
    if len(d1) >= 400:
        DATA[sym] = {"d1": d1, "h4": h4}
P_(f"fetched {len(DATA)} coins in {time.time() - T0:.0f}s")
btc = DATA.get("BTC-USDT", {}).get("d1") or []
btc_t = [r[0] for r in btc]
btc_c = [r[4] for r in btc]
btc_e = m._i2_ema(btc_c, 200) if len(btc_c) >= 200 else [None] * len(btc_c)

W_A = {"z7": 40, "rsi25": 30, "rsi30": 20, "bb": 10, "z3s": 10, "vsd": 10}      # (rsi25 replaces rsi30)
W_B = {"z7": 50, "rsi25": 30, "rsi30": 20, "bb": 20, "z3s": 0, "vsd": 0}
SEQ = {}
BASE = {}
for sym, Dd in DATA.items():
    d1, h4 = Dd["d1"], Dd["h4"]
    T, O, H, L, C, V = ([r[i] for r in d1] for i in range(6))
    S = m._i2_series(O, H, L, C, V)
    n = len(C)
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, n)]
    X = {"H": 7, "hn": "أسبوع", "fng": None, "fund": None}
    Pn = m._fc_pack(d1, d1, 86400, 86400)
    t4 = [r[0] for r in h4]; c4 = [r[4] for r in h4]; e4 = m._i2_ema(c4, 20) if len(c4) >= 20 else [None] * len(c4)
    seq = []
    for t in range(210, n - 31):
        o = (C[t + 7] / C[t] - 1, C[t + 14] / C[t] - 1, C[t + 30] / C[t] - 1, min(L[t + 1:t + 31]) / C[t] - 1)
        j = bisect.bisect_right(btc_t, T[t]) - 1
        breg = "btc_up" if (j >= 0 and btc_e[j] and btc_c[j] > btc_e[j]) else "btc_down"
        y = time.gmtime(T[t]).tm_year
        for rg in ("all", breg, f"y{y}") + (("last40",) if t / n >= 0.6 else ()):
            BASE.setdefault(rg, []).append(o)
        rs = lr[t - 59:t + 1]; rm = sum(rs) / 60; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 59) or 1e-9
        z3 = math.log(C[t] / C[t - 3]) / (sd * math.sqrt(3)); z7 = math.log(C[t] / C[t - 7]) / (sd * math.sqrt(7))
        w = C[t - 19:t + 1]; mu = sum(w) / 20; sdp = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
        rsi = S["rsi"][t]
        p = {"z7": z7 <= -2.0, "rsi25": rsi is not None and rsi <= 25, "rsi30": rsi is not None and 25 < rsi <= 30, "bb": C[t] < mu - 2 * sdp,
             "z3s": z3 <= -2.5}
        p["vsd"] = False
        if any(p.values()):                                       # (the daily lean only where something else fired — it is slow)
            sig, _ = m._fc_read(Pn, t, "w", X)
            p["vsd"] = m._fc_vote(sig)[3] == "sd"
        scA = sum(W_A[k] for k, on in p.items() if on)
        scB = sum(W_B[k] for k, on in p.items() if on)
        cf_d = next((e for e in range(t + 1, min(t + 6, n - 31)) if C[e] > H[e - 1]), None)
        cf_4 = None
        k0 = bisect.bisect_right(t4, T[t] + 86400 - 1)              # the first 4H candle after the signal day closed
        for k in range(k0, min(k0 + 18, len(c4))):
            if e4[k] and c4[k] > e4[k]:
                e = bisect.bisect_right(T, t4[k] + 4 * 3600 - 1) - 1  # enter at that day's close (no peeking: the day that holds the 4H close)
                cf_4 = e if t < e < n - 31 else None
                break
        seq.append((t, t / n, y, breg, scA, scB, o, cf_d, cf_4))
    SEQ[sym] = (C, L, seq)
P_(f"recorded in {time.time() - T0:.0f}s")


def outc(C, L, e):
    return (C[e + 7] / C[e] - 1, C[e + 14] / C[e] - 1, C[e + 30] / C[e] - 1, min(L[e + 1:e + 31]) / C[e] - 1)


def eline(v, b):
    if not v:
        return "—"
    f = lambda a, i: sum(1 for x in a if x[i] > 0) / len(a) * 100
    return (f"n {len(v):4d} · higher 7d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 14d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 30d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f}) · "
            f"median 14d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · drop first {med([x[3] for x in v]) * 100:.1f}% (normal {med([x[3] for x in b]) * 100:.1f}%)")


def events(wi, thr, conf):
    ev = []
    for sym, (C, L, seq) in SEQ.items():
        last = -99
        for t, frac, y, breg, scA, scB, o, cf_d, cf_4 in seq:
            sc = scA if wi == "A" else scB
            if sc >= thr:
                if t - last >= 10:
                    if conf == "none":
                        ev.append((sym, frac, y, breg, o))
                    else:
                        e = cf_d if conf == "day" else cf_4
                        if e is not None:
                            ev.append((sym, frac, y, breg, outc(C, L, e)))
                last = t
    return ev


for wi in ("A", "B"):
    P_(f"===== weighting {wi} {json.dumps(W_A if wi == 'A' else W_B)} · normal day: {eline(BASE['all'], BASE['all'])}")
    for thr in (30, 40, 50, 60, 70):
        for conf in ("none", "day", "4h"):
            ev = events(wi, thr, conf)
            if not ev:
                P_(f"  score ≥ {thr} · confirm {conf:4s} —"); continue
            P_(f"  score ≥ {thr} · confirm {conf:4s} all      {eline([e[4] for e in ev], BASE['all'])}")
            if conf == "none" or thr in (40, 50):
                l40 = [e[4] for e in ev if e[1] >= 0.6]
                P_(f"  score ≥ {thr} · confirm {conf:4s} last40%  {eline(l40, BASE['last40'])}")
                for rg in ("btc_up", "btc_down"):
                    P_(f"  score ≥ {thr} · confirm {conf:4s} {rg:8s} {eline([e[4] for e in ev if e[3] == rg], BASE[rg])}")
                cells = []
                for y in sorted({e[2] for e in ev}):
                    a = [e[4] for e in ev if e[2] == y]
                    b = BASE.get(f"y{y}") or []
                    if len(a) >= 8 and b:
                        cells.append(f"{y} {sum(1 for x in a if x[1] > 0) / len(a) * 100:.0f}% vs {sum(1 for x in b if x[1] > 0) / len(b) * 100:.0f}% ({len(a)})")
                P_(f"    by year 14d: " + " · ".join(cells))
                pos = tot = 0
                for sym in SEQ:
                    a = [e[4] for e in ev if e[0] == sym]
                    if len(a) >= 4:
                        tot += 1
                        pos += 1 if sum(1 for x in a if x[1] > 0) / len(a) > sum(1 for x in BASE["all"] if x[1] > 0) / len(BASE["all"]) else 0
                P_(f"    coins above the normal 14d rate: {pos}/{tot}")
P_(f"done in {time.time() - T0:.0f}s · notifications sent: {len(sent)}")
shutil.rmtree(R, ignore_errors=True)
