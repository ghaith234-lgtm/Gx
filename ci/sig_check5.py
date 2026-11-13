# 🔬 fifth pass — the owner (13-11): «للاثنين … اترك قاع الاربع ساعات · اختبر الجديد وحدث» — new signals measured on REAL OKX
#   prices before the alerts are built (4-hour candles ~2 years · 28 coins · the last 40% of time apart · per coin):
#   ① 🌊 the whole market crashing at once: share of coins whose 4-hour candle fell ≥ 2.5× their usual move in the SAME candle
#   ② 🔥 a 4-hour jump with huge volume (the mirror of the crash) ⇒ lower 1 / 3 / 7 days later?
#   ③ ₿ Bitcoin's own 4-hour crash with huge volume ⇒ the other coins 1 / 3 / 7 days later
#   ④ 💸 very negative funding (the short side paying — OKX keeps ~3 months) ⇒ the coin 1 / 3 / 7 days later
#   ⑤ 💥 the single-coin crash with huge volume again, with and without the market crashing with it (is its edge the market's?)
#   (the first pass's header follows, kept for its helpers)

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
R = tempfile.mkdtemp(prefix="sig5_real_")
json.dump({"port": 8111}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG5", *a, flush=True)


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



def mean(v):
    return sum(v) / len(v) if v else 0.0


T0 = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· fake" if FAKE else "· REAL OKX")
H4 = {}
for sym in COINS:
    try:
        h4 = hist(sym, "4H", 4400)
    except Exception as ex:
        P_(f"{sym}: fetch error {ex}"); continue
    if len(h4) >= 600:
        H4[sym] = h4
P_(f"fetched {len(H4)} coins in {time.time() - T0:.0f}s")

ROW = {}            # sym → {ts: (z, vr, o4 (1d, 3d, 7d, min7d), frac)}
for sym, h4 in H4.items():
    T4, O4, Hh, L4, C4, V4 = ([r[i] for r in h4] for i in range(6))
    n = len(C4)
    l4 = [0.0] + [math.log(C4[i] / C4[i - 1]) if C4[i] > 0 and C4[i - 1] > 0 else 0.0 for i in range(1, n)]
    d = {}
    for k in range(130, n - 43):
        rs = l4[k - 120:k]; rm = sum(rs) / 120; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 119) or 1e-9
        d[T4[k]] = (l4[k] / sd, V4[k] / (mean(V4[k - 30:k]) or 1e-9),
                    (C4[k + 6] / C4[k] - 1, C4[k + 18] / C4[k] - 1, C4[k + 42] / C4[k] - 1, min(L4[k + 1:k + 43]) / C4[k] - 1,
                     max(Hh[k + 1:k + 43]) / C4[k] - 1), k / n)
    ROW[sym] = d
ALLT = sorted(set().union(*[set(d) for d in ROW.values()])) if ROW else []
BASE = [r[2] for d in ROW.values() for r in d.values()]
BASE40 = [r[2] for d in ROW.values() for r in d.values() if r[3] >= 0.6]
P_(f"recorded in {time.time() - T0:.0f}s · {len(BASE)} coin-candles")


def line(v, b, down=False):
    if not v:
        return "—"
    s = (lambda x, i: x[i] < 0) if down else (lambda x, i: x[i] > 0)
    f = lambda a, i: sum(1 for x in a if s(x, i)) / len(a) * 100
    w = "LOWER" if down else "higher"
    return (f"n {len(v):5d} · {w} 1d {f(v, 0):.0f}% ({f(v, 0) - f(b, 0):+.0f}) · 3d {f(v, 1):.0f}% ({f(v, 1) - f(b, 1):+.0f}) · 7d {f(v, 2):.0f}% ({f(v, 2) - f(b, 2):+.0f}) · "
            f"median 1d {med([x[0] for x in v]) * 100:+.1f}% · 3d {med([x[1] for x in v]) * 100:+.1f}% (normal {med([x[1] for x in b]) * 100:+.1f}%) · "
            f"7d {med([x[2] for x in v]) * 100:+.1f}% (normal {med([x[2] for x in b]) * 100:+.1f}%) · "
            + (f"rise first {med([x[4] for x in v]) * 100:.1f}% (normal {med([x[4] for x in b]) * 100:.1f}%)" if down else
               f"drop first {med([x[3] for x in v]) * 100:.1f}% (normal {med([x[3] for x in b]) * 100:.1f}%)"))


def coins_ok(ev, down=False):
    nb = sum(1 for x in BASE if (x[1] < 0 if down else x[1] > 0)) / len(BASE)
    pos = tot = 0
    for sym in ROW:
        a = [e[1] for e in ev if e[0] == sym]
        if len(a) >= 3:
            tot += 1
            pos += 1 if sum(1 for x in a if (x[1] < 0 if down else x[1] > 0)) / len(a) > nb else 0
    return f"{pos}/{tot}"


# share of coins crashing in each candle
SHARE = {}
for t in ALLT:
    zs = [ROW[s][t][0] for s in ROW if t in ROW[s]]
    if len(zs) >= 15:
        SHARE[t] = (sum(1 for z in zs if z <= -2.5) / len(zs), len(zs))
P_(f"===== normal coin-candle: {line(BASE, BASE)}")
P_(f"===== normal (last 40%):  {line(BASE40, BASE40)}")

# ① the whole market crashing at once
P_("===== ① 🌊 the whole market crashing in the same 4-hour candle (share of coins falling ≥ 2.5× their usual move)")
for thr in (0.3, 0.5, 0.7):
    evt, last = [], -1e18
    for t in sorted(SHARE):
        if SHARE[t][0] >= thr:
            if t - last >= 86400:
                evt.append(t)
            last = t
    ev = [(s, ROW[s][t][2], ROW[s][t][3]) for t in evt for s in ROW if t in ROW[s]]
    P_(f"  ≥ {thr * 100:.0f}% of coins · {len(evt)} moments · every coin after      {line([e[1] for e in ev], BASE)}")
    P_(f"  ≥ {thr * 100:.0f}% of coins · last40%                              {line([e[1] for e in ev if e[2] >= 0.6], BASE40)}")
    P_(f"    coins above the normal 3d rate: {coins_ok(ev)} · moments: " + " ".join(time.strftime('%Y-%m-%d', time.gmtime(t)) for t in evt[-12:]))

# ② a 4-hour jump with huge volume
P_("===== ② 🔥 a 4-hour jump with huge volume (the mirror of the crash) ⇒ lower after?")
for zt, vt in ((2.5, 2), (3, 2), (3, 3), (4, 3), (5, 3)):
    ev = []
    for s, d in ROW.items():
        lk = -1e18
        for t in sorted(d):
            z, vr, o, f = d[t]
            if z >= zt and vr >= vt:
                if t - lk >= 86400:
                    ev.append((s, o, f))
                lk = t
    P_(f"  jump ≥ {zt}× · volume ≥ {vt}× all     {line([e[1] for e in ev], BASE, True)}")
    P_(f"  jump ≥ {zt}× · volume ≥ {vt}× last40% {line([e[1] for e in ev if e[2] >= 0.6], BASE40, True)}")
    P_(f"    coins above the normal 3d LOWER rate: {coins_ok(ev, True)}")

# ③ Bitcoin's crash ⇒ the other coins
P_("===== ③ ₿ Bitcoin's own 4-hour crash with huge volume ⇒ the OTHER coins after")
B = ROW.get("BTC-USDT") or {}
for zt, vt in ((-2.5, 2), (-3, 2), (-3, 3), (-4, 2)):
    evt, lk = [], -1e18
    for t in sorted(B):
        z, vr, o, f = B[t]
        if z <= zt and vr >= vt:
            if t - lk >= 86400:
                evt.append(t)
            lk = t
    ev = [(s, ROW[s][t][2], ROW[s][t][3]) for t in evt for s in ROW if s != "BTC-USDT" and t in ROW[s]]
    P_(f"  BTC drop ≤ {zt}× · volume ≥ {vt}× · {len(evt)} moments · other coins     {line([e[1] for e in ev], BASE)}")
    P_(f"  BTC drop ≤ {zt}× · volume ≥ {vt}× · last40%                    {line([e[1] for e in ev if e[2] >= 0.6], BASE40)}")

# ⑤ the single-coin crash, alone vs with the market
P_("===== ⑤ 💥 the single-coin crash with huge volume (≤ 3× · ≥ 3×) — alone vs while the market crashes with it")
for lbl, cond in (("any", lambda sh: True), ("ALONE (< 30% of coins crashing)", lambda sh: sh < 0.3), ("with the market (≥ 30%)", lambda sh: sh >= 0.3)):
    for zt in (-3, -4):
        ev = []
        for s, d in ROW.items():
            lk = -1e18
            for t in sorted(d):
                z, vr, o, f = d[t]
                if z <= zt and vr >= 3 and cond((SHARE.get(t) or (0, 0))[0]):
                    if t - lk >= 86400:
                        ev.append((s, o, f))
                    lk = t
        P_(f"  {lbl} · drop ≤ {zt}× all     {line([e[1] for e in ev], BASE)}")
        P_(f"  {lbl} · drop ≤ {zt}× last40% {line([e[1] for e in ev if e[2] >= 0.6], BASE40)} · coins {coins_ok(ev)}")

# ④ very negative funding
P_("===== ④ 💸 very negative funding (the short side paying · OKX keeps ~3 months)")
FE = {}
for sym in ROW:
    out, after = {}, None
    for _ in range(12):
        r = m._okx_pub(f"/api/v5/public/funding-rate-history?instId={sym.replace('-USDT', '-USDT-SWAP')}&limit=100" + (f"&after={after}" if after else ""))
        d = (r or {}).get("data") or []
        if not d:
            break
        for x in d:
            try:
                rt = x.get("realizedRate")
                out[int(x["fundingTime"]) // 1000] = float(rt) if rt not in (None, "") else float(x.get("fundingRate") or 0)
            except Exception:
                pass
        after = min(int(x["fundingTime"]) for x in d)
        if not FAKE:
            time.sleep(0.15)
    FE[sym] = out
P_(f"  funding payments: {sum(len(v) for v in FE.values())} over {len(FE)} coins")
for ft in (-0.0001, -0.0002, -0.0005):
    ev = []
    for sym, f in FE.items():
        d = ROW[sym]
        ts4 = sorted(d)
        lk = -1e18
        for ft_t in sorted(f):
            if f[ft_t] <= ft and ft_t - lk >= 86400:
                i = bisect.bisect_left(ts4, ft_t)
                if i < len(ts4) and ts4[i] - ft_t < 4 * 3600:
                    ev.append((sym, d[ts4[i]][2], d[ts4[i]][3]))
                    lk = ft_t
    rec = [r[2] for s, d in ROW.items() for t, r in d.items() if t >= time.time() - 95 * 86400]
    P_(f"  funding ≤ {ft * 100:.2f}% per payment   {line([e[1] for e in ev], rec)} · coins {len({e[0] for e in ev})}")
P_(f"done in {time.time() - T0:.0f}s · notifications sent: {len(sent)}")
shutil.rmtree(R, ignore_errors=True)
