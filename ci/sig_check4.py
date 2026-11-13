# 🔬 the owner (13-11): «المؤشرات تنطي اشعارات لكن جدا ضعيفة … شنو مؤشرات نگدر انضيفها قوية» ⇒ «سوي اختبارات للمؤشرات الجديدة» —
#   four candidates measured on REAL OKX prices (GitHub · public data · no keys · no orders · no notifications · every candle sees only
#   what came before it · the last 40% of time judged apart · by year · per coin · with Bitcoin above / below its 200-day average):
#   ① 🔺 a TOP score (the mirror of the 🟢 bottom): a 7-day rise of more than 2× the coin's usual weekly move · RSI ≥ 75 / ≥ 70 · above
#      the upper Bollinger band ⇒ lower 7 / 14 / 30 days later? median move · how much higher it went first
#   ② 🌤️ «grid weather»: how choppy the last 14 days were (efficiency = net move ÷ the sum of all moves) ⇒ does the next week stay
#      choppy? grid cycles of 1% in the next 7 days (4-hour closes) · the week's net move · weeks moving more than 10%
#   ③ 💥 a 4-hour crash with huge volume (the candle's drop vs the coin's usual 4-hour move · volume vs its 30-candle average) ⇒ higher
#      1 / 3 / 7 days later? median move · the drop first
#   ④ 🟢 the bottom score (as in the dashboard) with and without a volume blow-off in the last 3 days
#   python3 ci/sig_check4.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG4
import bisect, importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
         "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "HBAR-USDT", "ICP-USDT", "INJ-USDT", "SHIB-USDT"]
if FAKE:
    COINS = COINS[:3]
R = tempfile.mkdtemp(prefix="sig4_real_")
json.dump({"port": 8110}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG4", *a, flush=True)


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
                out.append([t1 - (n - 1 - i) * dt, o, max(o, p) * 1.003, min(o, p) * 0.997, p, 1000 * (1 + rnd.random() * (6 if rnd.random() < 0.02 else 1))])
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


def mean(v):
    return sum(v) / len(v) if v else 0.0


def cycles(series, step):
    """a real grid: a buy needs a whole step under the last trade, its sell a whole step above that buy"""
    if len(series) < 2:
        return 0
    k = math.log(1 + step)
    a = round(math.log(series[0]) / k)
    open_, done = 0, 0
    for v in series[1:]:
        x = math.log(v) / k
        while x <= a - 1:
            a -= 1; open_ += 1
        while x >= a + 1:
            a += 1
            if open_ > 0:
                open_ -= 1; done += 1
    return done


T0 = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· fake" if FAKE else "· REAL OKX")
DATA = {}
for sym in COINS:
    try:
        d1, h4 = hist(sym, "1Dutc", 2000), hist(sym, "4H", 4400)
    except Exception as ex:
        P_(f"{sym}: fetch error {ex}"); continue
    if len(d1) >= 400 and len(h4) >= 600:
        DATA[sym] = {"d1": d1, "h4": h4}
P_(f"fetched {len(DATA)} coins in {time.time() - T0:.0f}s")
btc = DATA.get("BTC-USDT", {}).get("d1") or []
btc_t = [r[0] for r in btc]
btc_c = [r[4] for r in btc]
btc_e = m._i2_ema(btc_c, 200) if len(btc_c) >= 200 else [None] * len(btc_c)
W_BOT = {"z7": 50, "rsi25": 30, "rsi30": 20, "bb": 20}                 # the dashboard's bottom (BOT_W)
W_TOP = {"z7": 50, "rsi75": 30, "rsi70": 20, "bb": 20}                 # its mirror

DAY, BASE, H4EV, H4BASE = {}, {}, [], {}
for sym, Dd in DATA.items():
    d1, h4 = Dd["d1"], Dd["h4"]
    T, O, H, L, C, V = ([r[i] for r in d1] for i in range(6))
    S = m._i2_series(O, H, L, C, V)
    n = len(C)
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, n)]
    t4 = [r[0] for r in h4]; c4 = [r[4] for r in h4]
    rows = []
    for t in range(210, n - 31):
        o = (C[t + 7] / C[t] - 1, C[t + 14] / C[t] - 1, C[t + 30] / C[t] - 1, min(L[t + 1:t + 31]) / C[t] - 1, max(H[t + 1:t + 31]) / C[t] - 1)
        j = bisect.bisect_right(btc_t, T[t]) - 1
        breg = "btc_up" if (j >= 0 and btc_e[j] and btc_c[j] > btc_e[j]) else "btc_down"
        y = time.gmtime(T[t]).tm_year
        frac = t / n
        for rg in ("all", breg, f"y{y}") + (("last40",) if frac >= 0.6 else ()):
            BASE.setdefault(rg, []).append(o)
        rs = lr[t - 59:t + 1]; rm = sum(rs) / 60; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 59) or 1e-9
        z7 = math.log(C[t] / C[t - 7]) / (sd * math.sqrt(7))
        w = C[t - 19:t + 1]; mu = sum(w) / 20; sdp = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
        rsi = S["rsi"][t]
        pb = {"z7": z7 <= -2.0, "rsi25": rsi is not None and rsi <= 25, "rsi30": rsi is not None and 25 < rsi <= 30, "bb": C[t] < mu - 2 * sdp}
        pt = {"z7": z7 >= 2.0, "rsi75": rsi is not None and rsi >= 75, "rsi70": rsi is not None and 70 <= rsi < 75, "bb": C[t] > mu + 2 * sdp}
        bot = sum(W_BOT[k] for k, on in pb.items() if on)
        top = sum(W_TOP[k] for k, on in pt.items() if on)
        va = mean(V[t - 22:t - 2]) or 1e-9
        vcap = max(V[t - 2:t + 1]) / va >= 2.5
        moves = sum(abs(C[i] - C[i - 1]) for i in range(t - 13, t + 1)) or 1e-12
        er14 = abs(C[t] - C[t - 14]) / moves
        k0 = bisect.bisect_right(t4, T[t] + 86400 - 1)
        fut4 = c4[k0:k0 + 42]
        fcyc = cycles(fut4, 0.01) if len(fut4) >= 40 else None
        fmv = sum(abs(C[i] - C[i - 1]) for i in range(t + 1, t + 8)) or 1e-12
        fer7 = abs(C[t + 7] - C[t]) / fmv
        rows.append((t, frac, y, breg, top, bot, vcap, o, er14, fcyc, abs(o[0]), fer7))
    DAY[sym] = rows
    # ③ 4-hour crash with huge volume
    T4, O4, H4_, L4, C4, V4 = ([r[i] for r in h4] for i in range(6))
    m4 = len(C4)
    l4 = [0.0] + [math.log(C4[i] / C4[i - 1]) if C4[i] > 0 and C4[i - 1] > 0 else 0.0 for i in range(1, m4)]
    last = {}
    for k in range(130, m4 - 43):
        o4 = (C4[k + 6] / C4[k] - 1, C4[k + 18] / C4[k] - 1, C4[k + 42] / C4[k] - 1, min(L4[k + 1:k + 43]) / C4[k] - 1)
        f4 = k / m4
        for rg in ("all",) + (("last40",) if f4 >= 0.6 else ()):
            H4BASE.setdefault(rg, []).append(o4)
        rs = l4[k - 120:k]; rm = sum(rs) / 120; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 119) or 1e-9
        z = l4[k] / sd
        vr = V4[k] / (mean(V4[k - 30:k]) or 1e-9)
        if z <= -2.5 and vr >= 2:
            H4EV.append((sym, k, f4, z, vr, o4))
P_(f"recorded in {time.time() - T0:.0f}s · daily rows {sum(len(v) for v in DAY.values())} · 4H crash candidates {len(H4EV)}")


def eline(v, b, down=False):
    if not v:
        return "—"
    if down:
        f = lambda a, i: sum(1 for x in a if x[i] < 0) / len(a) * 100
        return (f"n {len(v):4d} · LOWER 7d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 14d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 30d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f}) · "
                f"median 14d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · rise first {med([x[4] for x in v]) * 100:.1f}% (normal {med([x[4] for x in b]) * 100:.1f}%)")
    f = lambda a, i: sum(1 for x in a if x[i] > 0) / len(a) * 100
    return (f"n {len(v):4d} · higher 7d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 14d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 30d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f}) · "
            f"median 14d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · drop first {med([x[3] for x in v]) * 100:.1f}% (normal {med([x[3] for x in b]) * 100:.1f}%)")


def day_events(pick, gap=10):
    ev = []
    for sym, rows in DAY.items():
        lastt = -99
        for r in rows:
            if pick(r):
                if r[0] - lastt >= gap:
                    ev.append((sym,) + r)
                lastt = r[0]
    return ev


def report(name, ev, down):
    P_(f"  {name} all      {eline([e[8] for e in ev], BASE['all'], down)}")
    P_(f"  {name} last40%  {eline([e[8] for e in ev if e[2] >= 0.6], BASE['last40'], down)}")
    for rg in ("btc_up", "btc_down"):
        P_(f"  {name} {rg:8s} {eline([e[8] for e in ev if e[4] == rg], BASE[rg], down)}")
    i = 1
    sgn = (lambda x: x[i] < 0) if down else (lambda x: x[i] > 0)
    cells = []
    for y in sorted({e[3] for e in ev}):
        a = [e[8] for e in ev if e[3] == y]
        b = BASE.get(f"y{y}") or []
        if len(a) >= 8 and b:
            cells.append(f"{y} {sum(1 for x in a if sgn(x)) / len(a) * 100:.0f}% vs {sum(1 for x in b if sgn(x)) / len(b) * 100:.0f}% ({len(a)})")
    P_(f"    by year 14d {'lower' if down else 'higher'}: " + " · ".join(cells))
    pos = tot = 0
    nb = sum(1 for x in BASE["all"] if sgn(x)) / len(BASE["all"])
    for sym in DAY:
        a = [e[8] for e in ev if e[0] == sym]
        if len(a) >= 4:
            tot += 1
            pos += 1 if sum(1 for x in a if sgn(x)) / len(a) > nb else 0
    P_(f"    coins above the normal 14d rate: {pos}/{tot}")


# ── ① the top score
P_(f"===== ① 🔺 TOP score {json.dumps(W_TOP)} · normal day: {eline(BASE['all'], BASE['all'], True)}")
for thr in (30, 50, 60, 70):
    report(f"top ≥ {thr}", day_events(lambda r, thr=thr: r[4] >= thr), True)

# ── ② grid weather
allr = [r for rows in DAY.values() for r in rows if r[9] is not None]
for lbl, rr in (("all time", allr), ("last 40% of time", [r for r in allr if r[1] >= 0.6])):
    qs = sorted(r[8] for r in rr)
    cut = [qs[int(len(qs) * f)] for f in (0.2, 0.4, 0.6, 0.8)] if qs else []
    P_(f"===== ② 🌤️ grid weather · {lbl} · {len(rr)} days · choppiness of the last 14 days (efficiency: 0 = all back and forth · 1 = one straight line) in fifths")
    for qi in range(5):
        lo = cut[qi - 1] if qi > 0 else -1
        hi = cut[qi] if qi < 4 else 9
        a = [r for r in rr if lo < r[8] <= hi]
        if not a:
            continue
        P_(f"  fifth {qi + 1} (efficiency {lo if qi else 0:.2f}–{hi if qi < 4 else 1:.2f}): next 7 days · 1% grid cycles {mean([r[9] for r in a]):.1f} "
           f"(median {med([r[9] for r in a]):.0f}) · |net move| median {med([r[10] for r in a]) * 100:.1f}% · weeks moving > 10%: "
           f"{sum(1 for r in a if r[10] > 0.10) / len(a) * 100:.0f}% · next week's efficiency {mean([r[11] for r in a]):.2f} · n {len(a)}")

# ── ③ 4-hour crash with huge volume
def h4line(v, b):
    if not v:
        return "—"
    f = lambda a, i: sum(1 for x in a if x[i] > 0) / len(a) * 100
    return (f"n {len(v):4d} · higher 1d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 3d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 7d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f}) · "
            f"median 3d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · median 7d {med([x[2] for x in v]) * 100:+.1f}% "
            f"(normal {med([x[2] for x in b]) * 100:+.1f}%) · drop first {med([x[3] for x in v]) * 100:.1f}% (normal {med([x[3] for x in b]) * 100:.1f}%)")


P_(f"===== ③ 💥 4-hour crash with huge volume · normal 4H candle: {h4line(H4BASE['all'], H4BASE['all'])}")
for zt, vt in ((-2.5, 2), (-3, 2), (-3, 3), (-4, 3), (-5, 3)):
    ev, lastk = [], {}
    for sym, k, f4, z, vr, o4 in H4EV:
        if z <= zt and vr >= vt:
            if k - lastk.get(sym, -99) >= 6:
                ev.append((sym, f4, o4))
            lastk[sym] = k
    P_(f"  drop ≤ {zt}× usual · volume ≥ {vt}× all     {h4line([e[2] for e in ev], H4BASE['all'])}")
    P_(f"  drop ≤ {zt}× usual · volume ≥ {vt}× last40% {h4line([e[2] for e in ev if e[1] >= 0.6], H4BASE['last40'])}")
    pos = tot = 0
    nb = sum(1 for x in H4BASE["all"] if x[1] > 0) / len(H4BASE["all"])
    for sym in DATA:
        a = [e[2] for e in ev if e[0] == sym]
        if len(a) >= 3:
            tot += 1
            pos += 1 if sum(1 for x in a if x[1] > 0) / len(a) > nb else 0
    P_(f"    coins above the normal 3d rate: {pos}/{tot}")

# ── ④ the bottom with / without a volume blow-off
P_(f"===== ④ 🟢 bottom score (the dashboard's) with / without a volume blow-off (≥ 2.5× the 20-day average in the last 3 days)")
for thr in (50, 60):
    for lbl, f in (("any", lambda r: True), ("WITH volume", lambda r: r[6]), ("without", lambda r: not r[6])):
        ev = day_events(lambda r, thr=thr, f=f: r[5] >= thr and f(r))
        P_(f"  bottom ≥ {thr} · {lbl:11s} all     {eline([e[8] for e in ev], BASE['all'])}")
        P_(f"  bottom ≥ {thr} · {lbl:11s} last40% {eline([e[8] for e in ev if e[2] >= 0.6], BASE['last40'])}")
P_(f"done in {time.time() - T0:.0f}s · notifications sent: {len(sent)}")
shutil.rmtree(R, ignore_errors=True)
