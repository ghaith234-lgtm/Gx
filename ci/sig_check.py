# 🔬 v3.36.27 phase 1 — the owner (8-11): «التوقعات والمؤشرات سويهم اقوى عبر الاختبارات حقيقية … مؤشر القاع حتى اعرف متى اشتري …
#   اريد المؤشر الي يكون صادق او الافضل خليه بالبداية … من يجيني اشعار له قيمه»
#   REAL OKX prices on the GitHub runner (public market data · no keys · no orders · no notifications) — the dashboard's own code, every
#   past candle sees only what came before it:
#   A 🔮 every horizon (day 4H · week 1D · month 3D · 3 months 1W): each reading and the vote — right% vs chance (the same up/down mix of
#     calls) · all of history and walk-forward (each coin: the first 60% of its time learns, the last 40% is judged) · combiners judged
#     on the 40%: the vote · its opposite · weights learned per coin · weights learned on all coins · the best single · by market regime
#   B 📊 hourly (a year of 1H): each reading 4 h ahead · the weighted average · the turn alert exactly as ina_tick fires it (mid and
#     quiet) 4 h and 24 h ahead · the squeeze release
#   C 🟢 bottom research (daily): components and combinations ⇒ 7 / 14 / 30 days later higher? · how deep it went first · how near the
#     real 30-day low — against the coin's normal day · thresholds learned on the first 60% of time, judged on the last 40%
#   python3 ci/sig_check.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG   (--fake: synthetic prices, to dry-run offline)
import bisect, importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
         "TON-USDT", "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT"]
if FAKE:
    COINS = COINS[:3]
R = tempfile.mkdtemp(prefix="sig_real_")
json.dump({"port": 8098}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG", *a, flush=True)


if FAKE:                                                   # 🧪 offline dry-run only: a random walk served like OKX's public candles
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
                r = rnd.gauss(0, 0.012 * math.sqrt(dt / 3600))
                o = p; p = max(1e-6, p * math.exp(r))
                hi, lo = max(o, p) * (1 + abs(rnd.gauss(0, 0.004))), min(o, p) * (1 - abs(rnd.gauss(0, 0.004)))
                out.append([t1 - (n - 1 - i) * dt, o, hi, lo, p, 1000 * (1 + rnd.random())])
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
    """closed candles, oldest first (recent page + history pages backwards)"""
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


# ── scoring helpers ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def tally(recs, fn):
    """recs: [(ret, ...)] · fn(rec) ⇒ signed call (|v| ≥ 0.15 counts) ⇒ [hits, expected-by-chance, calls]"""
    if not recs:
        return [0, 0.0, 0]
    u = sum(1 for r in recs if r[0] > 0) / len(recs)
    h = ex = c = 0
    for r in recs:
        v = fn(r)
        if v is None or abs(v) < 0.15:
            continue
        c += 1
        if v > 0:
            ex += u; h += 1 if r[0] > 0 else 0
        else:
            ex += 1 - u; h += 1 if r[0] < 0 else 0
    return [h, ex, c]


def add(a, b):
    a[0] += b[0]; a[1] += b[1]; a[2] += b[2]
    return a


def fmt(t, H=1):
    h, ex, c = t
    if not c:
        return "—"
    e = (h - ex) / c * 100
    z = (h - ex) / math.sqrt(max(1e-9, c * 0.25)) / math.sqrt(max(1, H))          # overlap-adjusted (H-candle windows overlap)
    return f"{h / c * 100:.1f}% vs {ex / c * 100:.1f}% ({'+' if e >= 0 else ''}{e:.1f} · z {z:+.1f}) of {c}"


def edge(t):
    return (t[0] - t[1]) / t[2] if t[2] else 0.0


T_START = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· fake" if FAKE else "· REAL OKX")
db = {}
fng = m._fc_fng(db) if not FAKE else None
P_("fear & greed history:", len(fng[0]) if fng else 0, "days")
DATA = {}
for sym in COINS:
    w0 = time.time()
    try:
        d1 = hist(sym, "1Dutc", 2000)
        h4 = hist(sym, "4H", 4400)
        h1 = hist(sym, "1H", 8800)
        fund = m._fc_fund(sym, db) if not FAKE else None
    except Exception as ex:
        P_(f"{sym}: fetch error {type(ex).__name__}: {ex}"); continue
    DATA[sym] = {"d1": d1, "h4": h4, "h1": h1, "fund": fund}
    P_(f"{sym}: 1D {len(d1)} · 4H {len(h4)} · 1H {len(h1)} · funding {len(fund[0]) if fund else 0} · {time.time() - w0:.0f}s")

# ═════════════════════════════════════════ A 🔮 the forecast, every horizon ═════════════════════════════════════════
KEYS_I = [x[0] for x in m._IND2_K] + [x[0] for x in m._FC_X]
TREND_K = {"avwap", "pa", "trend", "st", "macd", "nw", "adx"}
REC = {}                                                   # (k) ⇒ {sym: [(ret, t, {key: s}, adx)]}
for sym, Dd in DATA.items():
    d1, h4 = Dd["d1"], Dd["h4"]
    if len(d1) < 300:
        continue
    g3, _ = m._fc_group(d1, None, 3, 0)
    gw, _ = m._fc_group(d1, None, 7, 3)
    tfr = {"4H": h4, "1D": d1, "3D": g3, "1W": gw}
    for k, nm, tf, H, dd in m.FC_H:
        rows = tfr[tf]
        if len(rows) < m.FC_MIN[tf] + H:
            continue
        trows = tfr[m.FC_TRD[k]]
        X = {"H": H, "hn": nm, "fng": fng, "fund": Dd["fund"]}
        Pn = m._fc_pack(rows, trows, m.FC_TFS[tf], m.FC_TFS[m.FC_TRD[k]])
        C = Pn["D"]["c"]
        out = []
        for t in range(m.FC_WARM[tf], len(rows) - H):
            if not C[t]:
                continue
            ret = C[t + H] / C[t] - 1.0
            if abs(ret) < m.FC_MOVE:
                continue
            sig, _ = m._fc_read(Pn, t, k, X)
            s = {kk: v[0] for kk, v in sig.items()}
            up, dn, n_, vk, _ = m._fc_vote(sig)
            s["vote"] = 1.0 if vk in ("su", "u") else -1.0 if vk in ("sd", "d") else 0.0
            out.append((ret, Pn["D"]["t"][t], s, Pn["S"]["adx"][t]))
        REC.setdefault(k, {})[sym] = out
P_(f"A recorded in {time.time() - T_START:.0f}s")


def learn_w(recs_by_coin, keys):
    """signed weights from edge (contrarian allowed) — only readings with ≥ 30 calls and |edge| ≥ 3 points"""
    w = {}
    for kk in keys:
        t = [0, 0.0, 0]
        for recs in recs_by_coin:
            add(t, tally(recs, lambda r, kk=kk: r[2].get(kk)))
        e = edge(t)
        if t[2] >= 30 and abs(e) >= 0.03:
            w[kk] = e
    return w


def wscore(r, w):
    if not w:
        return None
    num = sum(w[k] * r[2].get(k, 0.0) for k in w)
    den = sum(abs(w[k]) for k in w)
    v = num / den if den else 0.0
    return 1.0 if v >= 0.05 else -1.0 if v <= -0.05 else 0.0


SUMMARY = {}
for k, nm, tf, H, dd in m.FC_H:
    per = REC.get(k) or {}
    if not per:
        continue
    P_(f"===== A 🔮 {k} {nm} ({tf} candles · {H} ahead) · {len(per)} coins · {sum(len(v) for v in per.values())} candles")
    split = {s: (v[:int(len(v) * 0.6)], v[int(len(v) * 0.6):]) for s, v in per.items()}
    rows = []
    for kk in KEYS_I + ["vote"]:
        ta, tr, te = [0, 0.0, 0], [0, 0.0, 0], [0, 0.0, 0]
        pos = 0
        for s, v in per.items():
            fn = (lambda r, kk=kk: r[2].get(kk))
            add(ta, tally(v, fn)); add(tr, tally(split[s][0], fn))
            x = tally(split[s][1], fn); add(te, x)
            pos += 1 if x[2] and x[0] > x[1] else 0
        if ta[2]:
            rows.append((edge(te), kk, ta, tr, te, pos))
    for e_, kk, ta, tr, te, pos in sorted(rows, reverse=True):
        P_(f"  {kk:6s} all {fmt(ta, H)} | learn {fmt(tr, H)} | JUDGE {fmt(te, H)} · coins up {pos}/{len(per)}")
    SUMMARY[k] = {kk: (edge(te), te[2]) for _, kk, _, _, te, _ in rows}
    wall = learn_w([split[s][0] for s in per], KEYS_I)
    trs = {}
    for kk in KEYS_I:
        t = [0, 0.0, 0]
        for s in per:
            add(t, tally(split[s][0], lambda r, kk=kk: r[2].get(kk)))
        if t[2] >= 100:
            trs[kk] = edge(t)
    b1 = max(trs.items(), key=lambda x: abs(x[1])) if trs else None
    comb = {"vote": lambda r, w=None: r[2].get("vote"), "contra": lambda r, w=None: -r[2].get("vote", 0.0),
            "w_all": lambda r, w=None: wscore(r, wall),
            "best1": (lambda r, w=None: (r[2].get(b1[0], 0.0) * (1 if b1[1] > 0 else -1))) if b1 else (lambda r, w=None: None),
            "vote_trend": lambda r, w=None: r[2].get("vote") if (r[3] or 0) >= 25 else None,
            "contra_range": lambda r, w=None: -r[2].get("vote", 0.0) if (r[3] or 0) < 20 else None}
    res = {c: [0, 0.0, 0] for c in comb}
    res["w_coin"] = [0, 0.0, 0]
    posc = {c: 0 for c in res}
    for s in per:
        tr_, te_ = split[s]
        wc = learn_w([tr_], KEYS_I)
        for c, fn in comb.items():
            x = tally(te_, fn); add(res[c], x); posc[c] += 1 if x[2] and x[0] > x[1] else 0
        x = tally(te_, lambda r, wc=wc: wscore(r, wc)); add(res["w_coin"], x); posc["w_coin"] += 1 if x[2] and x[0] > x[1] else 0
    P_(f"  combiners judged on the unseen 40% (learned on the first 60%): weights(all coins) {json.dumps({a: round(b, 3) for a, b in wall.items()})} · best single {b1}")
    for c in res:
        P_(f"  ▶ {c:12s} {fmt(res[c], H)} · coins up {posc[c]}/{len(per)}")

# ═════════════════════════════════════════ B 📊 hourly readings and the alerts ═════════════════════════════════════════
BW = {k: w for k, _, _, w, _ in m._IND2_K}
B_IND = {kk: [[0, 0.0, 0], [0, 0.0, 0]] for kk in [x[0] for x in m._IND2_K] + ["avg"]}       # 4h · 24h
ALERT = {s: [[0, 0.0, 0], [0, 0.0, 0], 0] for s in ("mid", "low")}
SQ = {"n": 0, "dir4": [0, 0.0, 0], "dir24": [0, 0.0, 0], "mv": 0.0, "mv_all": 0.0, "n_all": 0}
for sym, Dd in DATA.items():
    c1, c4 = Dd["h1"], Dd["h4"]
    if len(c1) < 600 or len(c4) < 250:
        continue
    D = {"t": [x[0] for x in c1], "o": [x[1] for x in c1], "h": [x[2] for x in c1], "l": [x[3] for x in c1], "c": [x[4] for x in c1], "v": [x[5] for x in c1]}
    S = m._i2_series(D["o"], D["h"], D["l"], D["c"], D["v"])
    cl4, t4 = [x[4] for x in c4], [x[0] for x in c4]

    def _idx(ts, t4=t4):
        j = bisect.bisect_right(t4, ts - 4 * 3600 + 3600) - 1
        return j if j >= 0 else None
    T4 = {"e50": m._i2_ema(cl4, 50), "e200": m._i2_ema(cl4, 200), "idx": _idx}
    C = D["c"]
    sqs = m._fc_sq(D, S)
    recs4, recs24, arec = [], [], []
    st = {"mid": {"dir": None, "ts": {}}, "low": {"dir": None, "ts": {}}}
    run = 0
    for t in range(220, len(C) - 25):
        sg, lv = m._i2_signals(D, S, t, T4, None, None, None)
        sc = m._i2_combine(sg, BW) * 100
        s = {kk: v[0] for kk, v in sg.items()}
        s["avg"] = 1.0 if sc >= 15 else -1.0 if sc <= -15 else 0.0
        r4, r24 = C[t + 4] / C[t] - 1.0, C[t + 24] / C[t] - 1.0
        if abs(r4) >= m.IND2_MIN_MOVE:
            recs4.append((r4, t, s))
        if abs(r24) >= m.IND2_MIN_MOVE:
            recs24.append((r24, t, s))
        nz = [(kk, v) for kk, v in s.items() if kk != "avg" and abs(v) >= 0.15]
        agree = sum(BW.get(kk, 0) for kk, v in nz if (v > 0) == (sc > 0)) if sc else 0.0
        tw = sum(BW.get(kk, 0) for kk, _ in nz) or 1.0
        conf = (agree / tw * 100) if abs(sc) >= 15 else None
        if conf is not None and lv.get("adx") is not None and lv["adx"] < 20:
            conf *= 0.85
        for sens in ("mid", "low"):
            S_ = m.INA_SENS[sens]
            L = st[sens]
            d = "up" if sc >= S_["turn"] else ("dn" if sc <= -S_["turn"] else None)
            if abs(sc) < S_["turn"] * 0.5:
                L["dir"] = None
            if d and L["dir"] != d and (conf is None or conf >= S_["conf"]) and t - L["ts"].get(d, -99) >= 3:
                L["dir"] = d; L["ts"][d] = t
                arec.append((sens, 1.0 if d == "up" else -1.0, r4, r24))
        if sqs[t]:
            run += 1
        else:
            if run >= m.INA_SQ_MIN:
                m20 = sum(C[t - 19:t + 1]) / 20.0
                dv = 1.0 if C[t] >= m20 else -1.0
                SQ["n"] += 1
                add(SQ["dir4"], [1 if dv * r4 > 0 else 0, 0.5, 1]); add(SQ["dir24"], [1 if dv * r24 > 0 else 0, 0.5, 1])
                SQ["mv"] += abs(r24)
            run = 0
        SQ["mv_all"] += abs(r24); SQ["n_all"] += 1
    for kk in B_IND:
        add(B_IND[kk][0], tally(recs4, lambda r, kk=kk: r[2].get(kk)))
        add(B_IND[kk][1], tally(recs24, lambda r, kk=kk: r[2].get(kk)))
    u4 = sum(1 for r in recs4 if r[0] > 0) / max(1, len(recs4))
    u24 = sum(1 for r in recs24 if r[0] > 0) / max(1, len(recs24))
    for sens, dv, r4, r24 in arec:
        A = ALERT[sens]; A[2] += 1
        add(A[0], [1 if dv * r4 > 0 else 0, u4 if dv > 0 else 1 - u4, 1])
        add(A[1], [1 if dv * r24 > 0 else 0, u24 if dv > 0 else 1 - u24, 1])
P_(f"===== B 📊 hourly (a year of 1H · {len(DATA)} coins) — each reading 4 h and 24 h ahead · right% vs chance")
for kk, (a4, a24) in sorted(B_IND.items(), key=lambda x: -edge(x[1][0])):
    P_(f"  {kk:6s} 4h {fmt(a4, 4)} | 24h {fmt(a24, 24)}")
for sens, (a4, a24, n) in ALERT.items():
    P_(f"  🔔 turn alert ({sens}: turn {m.INA_SENS[sens]['turn']} · conf {m.INA_SENS[sens]['conf']}) fired {n}× · 4h {fmt(a4, 4)} | 24h {fmt(a24, 24)}"
       f" · per coin per month ≈ {n / max(1, len(DATA)) / 12:.1f}")
P_(f"  ⚡ squeeze release {SQ['n']}× · direction 4h {fmt(SQ['dir4'], 4)} · 24h {fmt(SQ['dir24'], 24)} · 24h move ×{(SQ['mv'] / max(1, SQ['n'])) / (SQ['mv_all'] / max(1, SQ['n_all'])):.2f} of normal")
P_(f"B done in {time.time() - T_START:.0f}s")

# ═════════════════════════════════════════ C 🟢 bottom research (daily) ═════════════════════════════════════════
COMP = ["dd", "bb", "rsi30", "rsi25", "div", "cap", "acc", "ext", "fng20", "fund_neg"]
EV = {}           # component/combo ⇒ list of (sym, t_frac, r7, r14, r30, mae30, near)
BASE = {"n": 0, "r14p": 0, "r14": [], "mae": [], "near": 0, "r7p": 0, "r30p": 0}
SEQ = {}          # sym ⇒ (C, H, L, [(t, frac, score 0–100, outcomes)])


def outcomes(C, L, e):
    if e + 30 >= len(C):
        return None
    c0 = C[e]
    lo = min(L[e + 1:e + 31])
    return (C[e + 7] / c0 - 1, C[e + 14] / c0 - 1, C[e + 30] / c0 - 1, lo / c0 - 1, c0 <= 1.05 * min(lo, L[e]))


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else 0.0


fng_t, fng_v = (fng[0], fng[1]) if fng else ([], [])
for sym, Dd in DATA.items():
    d1 = Dd["d1"]
    if len(d1) < 400:
        continue
    T, O, H, L, C, V = ([r[i] for r in d1] for i in range(6))
    S = m._i2_series(O, H, L, C, V)
    ad = m._xc_ad(T, H, L, C, V)
    n = len(C)
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, n)]
    e50 = m._i2_ema(C, 50)
    ft, fv = Dd["fund"] if Dd["fund"] else ([], [])
    last_on = {c: -99 for c in COMP}
    seq = []
    for t in range(100, n - 31):
        o = outcomes(C, L, t)
        if not o:
            continue
        BASE["n"] += 1; BASE["r7p"] += o[0] > 0; BASE["r14p"] += o[1] > 0; BASE["r30p"] += o[2] > 0
        BASE["r14"].append(o[1]); BASE["mae"].append(o[3]); BASE["near"] += o[4]
        w = C[t - 19:t + 1]; mu = sum(w) / 20; sd = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
        hi90 = max(H[t - 89:t + 1]); dd = 1 - C[t] / hi90
        rs = lr[t - 59:t + 1]; rm = sum(rs) / 60; rsd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 59) or 1e-9
        rsi, atr = S["rsi"][t], S["atr"][t]
        vavg = sum(V[t - 20:t]) / 20
        comp = {"dd": dd / (rsd * math.sqrt(20)) >= 1.5, "bb": C[t] < mu - 2 * sd, "rsi30": rsi is not None and rsi <= 30,
                "rsi25": rsi is not None and rsi <= 25, "ext": bool(atr and e50[t] and C[t] < e50[t] - 3 * atr)}
        lo_new = min(range(t - 5, t + 1), key=lambda i: L[i]); lo_old = min(range(t - 30, t - 5), key=lambda i: L[i])
        comp["div"] = bool(L[lo_new] < L[lo_old] and S["rsi"][lo_new] is not None and S["rsi"][lo_old] is not None
                           and S["rsi"][lo_old] <= 35 and S["rsi"][lo_new] >= S["rsi"][lo_old] + 3)
        rg = H[t] - L[t]
        comp["cap"] = bool(vavg and V[t] >= 2.5 * vavg and rg > 0 and (C[t] - L[t]) / rg >= 0.5 and C[t] < mu)
        a = m._xc_ad_at(t, ad, C)
        comp["acc"] = bool(a and a[0] == "acc" and a[2] < 0)
        if fng_t:
            v = m._fc_at(fng_t, fng_v, T[t] + 86400)
            comp["fng20"] = v is not None and v <= 20
        if ft:
            j = bisect.bisect_right(ft, T[t] + 86400 - 1)
            comp["fund_neg"] = bool(j >= 3 and T[t] + 86400 - ft[j - 1] < 2 * 86400 and sum(fv[j - 3:j]) / 3 < 0)
        frac = t / n
        for c, on in comp.items():
            if on and t - last_on[c] >= 10:
                EV.setdefault(c, []).append((sym, frac) + o)
            if on:
                last_on[c] = t
        score = (2 * comp["dd"] + 1.5 * comp["bb"] + 1.5 * comp["rsi30"] + 1 * comp["rsi25"] + 2 * comp["div"] + 1.5 * comp["cap"] + 1 * comp["acc"]
                 + 1 * comp["ext"] + 1 * comp.get("fng20", False) + 0.5 * comp.get("fund_neg", False))
        seq.append((t, frac, round(score / 13.0 * 100), o))
    SEQ[sym] = (C, H, L, seq)


def confirm(C, H, L, t):
    """✅ the first close above the previous day's high within 7 days ⇒ outcomes from that close"""
    for e in range(t + 1, min(t + 8, len(C) - 31)):
        if C[e] > H[e - 1]:
            return outcomes(C, L, e)
    return None


def episodes(thr):
    ev, evc = [], []
    for sym, (C, H, L, seq) in SEQ.items():
        last = -99
        for t, frac, sc, o in seq:
            if sc >= thr:
                if t - last >= 10:
                    ev.append((sym, frac) + o)
                    cf = confirm(C, H, L, t)
                    if cf:
                        evc.append((sym, frac) + cf)
                last = t
    return ev, evc


def show(lbl, ev):
    if not ev:
        P_(f"  {lbl:18s} —"); return
    n = len(ev)
    r7 = sum(1 for e in ev if e[2] > 0) / n * 100; r14 = sum(1 for e in ev if e[3] > 0) / n * 100; r30 = sum(1 for e in ev if e[4] > 0) / n * 100
    P_(f"  {lbl:18s} n {n:4d} · higher after 7d {r7:.0f}% · 14d {r14:.0f}% · 30d {r30:.0f}% · median 14d {med([e[3] for e in ev]) * 100:+.1f}% · "
       f"median drop first {med([e[5] for e in ev]) * 100:.1f}% · near the 30-day low {sum(1 for e in ev if e[6]) / n * 100:.0f}%")


bn = max(1, BASE["n"])
P_(f"===== C 🟢 bottom research — daily · {len(DATA)} coins · every day vs the coin's normal day")
P_(f"  normal day        n {BASE['n']} · higher after 7d {BASE['r7p'] / bn * 100:.0f}% · 14d {BASE['r14p'] / bn * 100:.0f}% · 30d {BASE['r30p'] / bn * 100:.0f}% · "
   f"median 14d {med(BASE['r14']) * 100:+.1f}% · median drop first {med(BASE['mae']) * 100:.1f}% · near the 30-day low {BASE['near'] / bn * 100:.0f}%")
for c in COMP:
    show(c, EV.get(c))
for c in COMP:
    show(c + " (last 40%)", [e for e in EV.get(c, []) if e[1] >= 0.6])
P_("  ── the combined score (episodes: first day at/above the level after 10 quiet days) · and with the confirmation (first close above the previous high, ≤ 7 days)")
for thr in (25, 35, 45, 55, 65):
    ev, evc = episodes(thr)
    show(f"score ≥ {thr}", ev)
    show(f"score ≥ {thr} (40%)", [e for e in ev if e[1] >= 0.6])
    show(f"score ≥ {thr} ✅", evc)
    show(f"score ≥ {thr} ✅ 40%", [e for e in evc if e[1] >= 0.6])
P_(f"C done in {time.time() - T_START:.0f}s")
P_("notifications sent:", len(sent))
P_("done")
shutil.rmtree(R, ignore_errors=True)
