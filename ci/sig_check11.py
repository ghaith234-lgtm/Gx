# 🔬 eleventh pass — the owner (20-11): «سوي فحص للمؤشرات كم قلنا عندما يجتمع مؤشرين او اكثر ممكن يعطينا دقه اكبر ، بس لازم المؤشرات
#   داىما متفقين يعني مو الاختيار عشواىي». Everything through the dashboard's OWN signal code (the same events the 🎯 catalog uses · the
#   macro readings moved later by their publication delay), 28 coins, REAL OKX prices, judged after 4 hours · 1 day · 1 month (net of 0.2%):
#   ① AGREEMENT: k signals (2 … 8) say the SAME direction at the same time and NONE says the opposite ⇒ what followed · the same with k
#      different FAMILIES (trend · momentum · volatility · pattern · volume · market) ⇒ does more agreement give more accuracy?
#   ② NOT CHANCE: the whole history cut into 4 equal periods · an agreement or a combination counts only if it beats random in EVERY
#      period on its own (with enough cases and different days) — not one lucky stretch
#   ③ SPECIFIC combinations (2 · 3 · 4 signals, all the same direction, no opposite one active): chosen on periods 1–3 only (each beating
#      random in all three) ⇒ judged on period 4 that they never saw · combinations that fire on the very same candles counted once
#      · THE YARDSTICK: the same hunt run again on SHUFFLED prices (each coin's real candles in a random order — same sizes, same
#        volatility, nothing to predict) ⇒ what «held» there is what luck alone gives · real only matters if it clearly beats that
#   ④ THE MARKET AS A WHOLE: the compass · the market-wide crash · fear & greed · the macro readings ⇒ the market's average
#      after 4 hours · 1 day · 1 month, period by period
#   · the owner again (20-11): «مؤشرات ثلاثه او اكثر او اقل محددة دائما اذا اتفقت طلع توقعها صحيح · بدون اسبوع خلي الشهر التالي» ⇒ the
#     horizons are 4 hours · tomorrow · NEXT MONTH (the week is gone) · the daily history goes back as far as the exchange has it (~7 years)
#     so a month has enough separate cases · cases are counted as INDEPENDENT only once per window of the horizon (a month = one per 30 days)
#     · ⑤ what is happening NOW on the exchange (accumulation · distribution · aggressive buying/selling · crowding) ⇒ what followed
#   python3 ci/sig_check11.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYSIG11
import importlib.machinery, importlib.util, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig11_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
T0 = time.time()


def P(*a):
    print("HOLYSIG11", *a, flush=True)


L = m._sg_lib()
FEE = 0.002
COINS = list(m.MKT_COINS)
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· macro delays", m.SG_MLAG)
# ── the data, through the dashboard's own fetchers ──
cdb = {}
m.SG_N["1D"] = 2600                      # 📅 the daily history as far back as the exchange has it (~7 years) — for the month
m._sg_refresh(COINS, ["4H", "1D"], cdb)
db, now = {}, time.time()
for fn in ("_pro_vix", "_pro_dxy", "_pro_us10", "_pro_epu", "_pro_gpr", "_pro_tone"):
    try:
        getattr(m, fn)(db, now)
    except Exception as ex:
        P(fn, "error", ex)
try:
    m._pro_ls(db, now, [c.split("-")[0] for c in COINS]); m._pro_tk(db, now, [c.split("-")[0] for c in COINS])
except Exception as ex:
    P("pro error", ex)
fdb = {}
m._fc_fng(fdb)
mkt, fng = m._sg_mkt(db, fdb), m._sg_fng_raw(fdb)
P(f"prices fetched · {time.time() - T0:.0f}s")
META = m._sg_meta()
FAM = lambda code: META.get(code, ("other",))[0]
LK = {"4H": 3, "1D": 2}
HZ = [("4H", 1, "4 hours"), ("4H", 6, "1 day"), ("1D", 1, "1 day (daily)"), ("1D", 30, "1 month (daily)")]
SEC = {"4H": 14400, "1D": 86400}


def bk(fr, h, ts):
    """independent cases: at most one per window of the horizon (a day for 4 hours and a day · 30 days for a month)"""
    return ts // max(86400, h * SEC[fr])


def fwd(C, i, h, side):
    if i + h >= len(C):
        return None
    return (C[i + h] / C[i] - 1 if side > 0 else C[i] / C[i + h] - 1) - FEE


def mean(v):
    return sum(v) / len(v) if v else 0.0


def hit(v):
    return sum(1 for x in v if x > 0) / len(v) * 100 if v else 0.0


def shuffled(db_, seed):
    """each coin's real candles in a random order (each candle keeps its own move · its open gap · its wicks · its volume) ⇒ the same
    sizes and volatility, nothing that can be predicted"""
    rnd = random.Random(seed)
    out = {}
    for sec in ("c", "c4"):
        out[sec] = {}
        for sym, e in (db_.get(sec) or {}).items():
            rows = e.get("d") or []
            if len(rows) < 3:
                continue
            parts = [(r[1] / rows[k - 1][4], r[2] / r[4], r[3] / r[4], r[4] / rows[k - 1][4], r[5]) for k, r in enumerate(rows) if k > 0]
            rnd.shuffle(parts)
            c, new = rows[0][4], [list(rows[0][:6])]
            for k, (o, h, l, cc, v) in enumerate(parts, 1):
                o_, c_ = c * o, c * cc
                new.append([rows[k][0], o_, max(c_ * h, o_, c_), min(c_ * l, o_, c_), c_, v])
                c = c_
            out[sec][sym] = {"d": new}
    return out


def per(X, fr, ts):
    b = X["BND"][fr]
    return 0 if ts < b[1] else 1 if ts < b[2] else 2 if ts < b[3] else 3


def prep(db_):
    """the dashboard's own events for every coin and frame ⇒ everything the checks need"""
    btc = {int(r[0]): float(r[4]) for r in ((db_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []}
    F = {}
    for sym in COINS:
        rd = ((db_.get("c") or {}).get(sym) or {}).get("d") or []
        r4 = ((db_.get("c4") or {}).get(sym) or {}).get("d") or []
        if len(rd) < 300 or len(r4) < 700:
            continue
        ctx = m._sg_ctx(sym, rd, db, mkt, fng, btc)
        F[(sym, "4H")] = m._sg_events(r4, False, ctx)
        F[(sym, "1D")] = m._sg_events(rd, True, ctx)
    m._sg_crash({s: F[(s, "4H")] for s, fr in F if fr == "4H"})
    X = {"F": F, "SYMS": sorted({s for s, f in F})}
    # periods: 4 equal stretches of time per frame (the same cut for every coin)
    X["BND"] = {}
    for fr in ("4H", "1D"):
        t0 = min(F[(s, fr)][0]["T"][210] for s in X["SYMS"])
        t1 = max(F[(s, fr)][0]["T"][-1] for s in X["SYMS"])
        X["BND"][fr] = [t0 + (t1 - t0) * k / 4 for k in range(5)]
    # per coin · frame: the active signals of each side at every candle (a signal stays «on» for LK candles, as in the catalog)
    ACT, AS, OPP = {}, {}, {}
    for (sym, fr), (D, E) in F.items():
        n = D["n"]
        a = {1: [[] for _ in range(n)], -1: [[] for _ in range(n)]}
        for (code, side), lst in E.items():
            for i in lst:
                for j in range(i, min(n, i + LK[fr])):
                    a[side][j].append(code)
        ACT[(sym, fr)] = a
        for side in (1, -1):
            d = {}
            for i, lst in enumerate(a[side]):
                for c in lst:
                    d.setdefault(c, set()).add(i)
            AS[(sym, fr, side)] = d
            OPP[(sym, fr, side)] = {i for i, lst in enumerate(a[side]) if lst}
    X.update(ACT=ACT, AS=AS, OPP=OPP)
    BASE = {}
    for fr, h, nm in HZ:
        for side in (1, -1):
            bp = [[] for _ in range(4)]
            for sym in X["SYMS"]:
                D = F[(sym, fr)][0]
                for i in range(210, D["n"]):
                    x = fwd(D["C"], i, h, side)
                    if x is not None:
                        bp[per(X, fr, D["T"][i])].append(x)
            BASE[(fr, h, side)] = bp
    X["BASE"] = BASE
    return X


def judge(X, fr, h, side, cond):
    """edge-triggered: the candle where cond becomes true ⇒ returns per period + the days"""
    out = [[] for _ in range(4)]
    days = [set() for _ in range(4)]
    for sym in X["SYMS"]:
        D = X["F"][(sym, fr)][0]
        a = X["ACT"][(sym, fr)]
        prev = False
        for i in range(210, D["n"]):
            c = cond(a[side][i], a[-side][i])
            if c and not prev:
                x = fwd(D["C"], i, h, side)
                if x is not None:
                    p = per(X, fr, D["T"][i])
                    out[p].append(x)
                    days[p].add(bk(fr, h, D["T"][i]))
            prev = c
    return out, days


def line(X, fr, h, side, out, days, min_n=10):
    bp = X["BASE"][(fr, h, side)]
    allv = [x for v in out for x in v]
    allb = [x for v in bp for x in v]
    wins = sum(1 for k in range(4) if len(out[k]) >= min_n and len(days[k]) >= 3 and hit(out[k]) > hit(bp[k]) and mean(out[k]) > mean(bp[k]))
    seg = " | ".join(f"P{k + 1} {hit(out[k]):.0f}% n{len(out[k])} d{len(days[k])} (rand {hit(bp[k]):.0f})" for k in range(4))
    return (f"n {len(allv)} days {sum(len(d) for d in days)} hit {hit(allv):.0f}% (rand {hit(allb):.0f}) edge {(mean(allv) - mean(allb)) * 100:+.2f}% · "
            f"beats random in {wins}/4 periods{' ✅ CONSISTENT' if wins == 4 else ''} · {seg}"), wins


def evalc(X, fr, h, side, keys, strict=True):
    """a combination: all its signals active together on the same side (and none of the other side) ⇒ the first candle of each time"""
    out = [[] for _ in range(4)]
    days = [set() for _ in range(4)]
    cases = []
    for sym in X["SYMS"]:
        D = X["F"][(sym, fr)][0]
        d = X["AS"][(sym, fr, side)]
        if any(c not in d for c in keys):
            continue
        S = set.intersection(*sorted((d[c] for c in keys), key=len))
        if strict:
            S = S - X["OPP"][(sym, fr, -side)]
        for i in sorted(S):
            if i >= 210 and (i - 1) not in S:
                x = fwd(D["C"], i, h, side)
                if x is not None:
                    p = per(X, fr, D["T"][i])
                    out[p].append(x)
                    days[p].add(bk(fr, h, D["T"][i]))
                    cases.append((sym, i))
    return out, days, frozenset(cases)


def ok3(X, fr, h, side, out, days, min_n=6):
    bp = X["BASE"][(fr, h, side)]
    return all(len(out[k]) >= min_n and len(days[k]) >= 3 and hit(out[k]) > hit(bp[k]) and mean(out[k]) > mean(bp[k]) for k in range(3))


def score3(X, fr, h, side, out):
    bp = X["BASE"][(fr, h, side)]
    return min((mean(out[k]) - mean(bp[k])) * math.sqrt(len(out[k])) for k in range(3))


def hunt(X, fr, h, side):
    """③ beam search on periods 1–3 only ⇒ the combinations consistent in each of them (identical firing counted once)"""
    codes = sorted({c for sym in X["SYMS"] for (c, s), lst in X["F"][(sym, fr)][1].items() if s == side and len(lst) >= 3})
    sc = []
    for c in codes:
        out, days, _ = evalc(X, fr, h, side, [c])
        if sum(len(v) for v in out[:3]) >= 30 and all(out[k] for k in range(3)):
            sc.append((score3(X, fr, h, side, out), c))
    sc.sort(reverse=True)
    top = [c for s, c in sc[:30]]
    found, seen, beam = [], set(), [(c,) for c in top]
    for size in (2, 3, 4):
        cand = {}
        for b in beam:
            for c in top:
                if c in b:
                    continue
                nc = tuple(sorted(b + (c,)))
                if nc in cand:
                    continue
                out, days, cs = evalc(X, fr, h, side, nc)
                if ok3(X, fr, h, side, out, days):
                    cand[nc] = (score3(X, fr, h, side, out), out, days, cs)
        best = sorted(cand.items(), key=lambda x: -x[1][0])[:25]
        beam = [c for c, _ in best]
        for c, (s, out, days, cs) in best:
            if cs not in seen:                       # the same candles as a smaller one ⇒ not a new combination
                seen.add(cs)
                found.append((size, c, out, days))
        if not best:
            break
    bp = X["BASE"][(fr, h, side)]
    judged = [x for x in found if len(x[2][3]) >= 10 and len(x[3][3]) >= 5]
    held = [x for x in judged if hit(x[2][3]) > hit(bp[3]) and mean(x[2][3]) > mean(bp[3])]
    return found, judged, held


T1 = time.time()
X = prep(cdb)
P(f"events ready · {len(X['SYMS'])} coins · {time.time() - T1:.0f}s")

# ── ① agreement: k signals the same way · none the other way ──
def agree(X, show):
    res = []
    for fr, h, nm in HZ:
        for side in (1, -1):
            sd = "BUY " if side > 0 else "SELL"
            if show:
                P(f"══ ① {nm} · {sd} · k signals agree, none against ══")
            for kind, ks in (("signals", (2, 3, 4, 5, 6, 8)), ("families", (2, 3, 4, 5))):
                for k in ks:
                    if kind == "signals":
                        out, days = judge(X, fr, h, side, lambda s, o, k=k: len(set(s)) >= k and not o)
                    else:
                        out, days = judge(X, fr, h, side, lambda s, o, k=k: len({FAM(c) for c in s}) >= k and not o)
                    txt, w = line(X, fr, h, side, out, days)
                    res.append((f"{nm} {sd} {k}+ {kind}", w))
                    if show:
                        P(f"{nm} {sd} {k}+ {kind}: " + txt)
    return res


AG_REAL = agree(X, True)
P(f"① done · {time.time() - T0:.0f}s")

# ── ③ specific combinations on REAL prices: chosen on periods 1–3 · judged on period 4 ──
H3 = (("4H", 1, "4 hours"), ("4H", 6, "1 day"), ("1D", 1, "1 day (daily)"), ("1D", 30, "1 month (daily)"))
REAL = {}
for fr, h, nm in H3:
    for side in (1, -1):
        sd = "BUY " if side > 0 else "SELL"
        found, judged, held = hunt(X, fr, h, side)
        REAL[(fr, h, side)] = (len(found), len(judged), len(held))
        bp = X["BASE"][(fr, h, side)]
        bands = [sum(1 for x in held if lo <= hit(x[2][3]) < hi) for lo, hi in ((0, 55), (55, 60), (60, 70), (70, 101))]
        P(f"══ ③ REAL {nm} · {sd} · combinations consistent in periods 1–3: {len(found)} · judged on period 4 (≥10 cases · ≥5 separate): "
          f"{len(judged)} · still better than random there: {len(held)} (random P4 {hit(bp[3]):.0f}%) · their P4 accuracy: under 55% {bands[0]} · "
          f"55–60% {bands[1]} · 60–70% {bands[2]} · 70%+ {bands[3]} ══")
        for size, c, out, days in sorted(judged, key=lambda x: -hit(x[2][3]))[:12]:
            names = " + ".join(m._sg_name(k, side) for k in c)
            ok = hit(out[3]) > hit(bp[3]) and mean(out[3]) > mean(bp[3])
            ev4 = all(len(out[k]) >= 5 and hit(out[k]) > hit(bp[k]) and mean(out[k]) > mean(bp[k]) for k in range(4))
            allv = [x for v in out for x in v]
            P(f"{nm} {sd} {size}× P1-3 " + " · ".join(f"{hit(out[k]):.0f}%/{len(out[k])}" for k in range(3))
              + f" → P4 {hit(out[3]):.0f}% n{len(out[3])} sep{len(days[3])} (rand {hit(bp[3]):.0f}) edge {(mean(out[3]) - mean(bp[3])) * 100:+.2f}% "
              + ("✅" if ok else "❌") + f" · all periods {hit(allv):.0f}% n{len(allv)}" + (" 🟢 EVERY PERIOD" if ev4 else "") + f" · {names}")
P(f"③ real done · {time.time() - T0:.0f}s")

# ── ④ the market as a whole (real prices) ──
IDX = {(s, fr): {t: i for i, t in enumerate(X["F"][(s, fr)][0]["T"])} for s, fr in X["F"]}


def mkt_avg(fr, ts, h):
    v = []
    for sym in X["SYMS"]:
        D = X["F"][(sym, fr)][0]
        j = IDX[(sym, fr)].get(ts)
        if j is not None:
            x = fwd(D["C"], j, h, 1)
            if x is not None:
                v.append(x + FEE)
    return mean(v) if len(v) >= 10 else None


seq = m._sg_compass_states(X["F"][("BTC-USDT", "1D")][0], [X["F"][(s, "1D")][0] for s in X["SYMS"]])
for h, nm in ((1, "1 day"), (30, "1 month")):
    res = {}
    for t, raw, s, *_ in seq:
        x = mkt_avg("1D", t, h)
        if x is not None:
            res.setdefault(s, [[] for _ in range(4)])[per(X, "1D", t)].append(x)
    allx = [[] for _ in range(4)]
    for s, v in res.items():
        for k in range(4):
            allx[k] += v[k]
    for s in ("up", "flat", "down"):
        v = res.get(s) or [[] for _ in range(4)]
        P(f"④ compass {s.upper():4s} → the market's average after {nm}: " + " | ".join(
            f"P{k + 1} up {hit(v[k]):.0f}% mean {mean(v[k]) * 100:+.2f}% n{len(v[k])} (all days {hit(allx[k]):.0f}% {mean(allx[k]) * 100:+.2f}%)" for k in range(4)))
for code, fr in (("W-crash", "4H"), ("M-fng", "1D"), ("M-vix", "1D"), ("M-dxy", "1D"), ("M-us10", "1D"), ("M-epu", "1D"), ("M-gpr", "1D")):
    for side in (1, -1):
        Fb = X["F"][("BTC-USDT", fr)]
        ts_ = sorted({Fb[0]["T"][i] for i in (Fb[1].get((code, side)) or [])})
        if not ts_:
            continue
        segs = []
        for h, nm in ((1 if fr == "1D" else 6, "1d"), (30 if fr == "1D" else 180, "1m")) + (((1, "4h"),) if fr == "4H" else ()):
            per_v = [[] for _ in range(4)]
            for t in ts_:
                x = mkt_avg(fr, t, h)
                if x is not None:
                    per_v[per(X, fr, t)].append(x if side > 0 else -x)
            segs.append(f"{nm}: " + " ".join(f"P{k + 1} {hit(per_v[k]):.0f}%/{len(per_v[k])}" for k in range(4)))
        P(f"④ {code} {'BUY ' if side > 0 else 'SELL'} ({len(ts_)} events) the market's average in its direction · " + " ‖ ".join(segs))
P(f"④ done · {time.time() - T0:.0f}s")

# ── ⑤ what is happening NOW on the exchange, per coin ⇒ what followed for that coin ──
for code, fr in (("X-ad", "1D"), ("X-ad", "4H"), ("X-adt", "1D"), ("X-adt", "4H"), ("P-tk", "1D"), ("P-ls", "1D"), ("X-rs", "1D")):
    for side in (1, -1):
        for h, nm in (((1, "4 hours"), (6, "1 day")) if fr == "4H" else ((1, "1 day"), (30, "1 month"))):
            out, days, _ = evalc(X, fr, h, side, [code], strict=False)
            if sum(len(v) for v in out) < 5:
                continue
            P(f"⑤ {fr} {m._sg_name(code, side)} → after {nm}: " + line(X, fr, h, side, out, days)[0])
P(f"⑤ done · {time.time() - T0:.0f}s")

# ── the yardstick: everything again on shuffled prices (6 different orders) — what luck alone gives ──
NULL = {k: [] for k in REAL}
AG_NULL = []
for seed in range(11, 17):
    T1 = time.time()
    Y = prep(shuffled(cdb, seed))
    AG_NULL.append(agree(Y, False))
    for fr, h, nm in H3:
        for side in (1, -1):
            found, judged, held = hunt(Y, fr, h, side)
            NULL[(fr, h, side)].append((len(found), len(judged), len(held)))
    P(f"shuffled #{seed - 10} done in {time.time() - T1:.0f}s · agreement lines consistent in all 4 periods there: "
      f"{sum(1 for _, w in AG_NULL[-1] if w == 4)} of {len(AG_NULL[-1])}")
    del Y
P(f"⚖️ ① agreement lines consistent in all 4 periods · REAL {sum(1 for _, w in AG_REAL if w == 4)} of {len(AG_REAL)}: "
  + (" · ".join(lb for lb, w in AG_REAL if w == 4) or "none") + " ‖ SHUFFLED (luck alone) per order: " + " · ".join(str(sum(1 for _, w in g if w == 4)) for g in AG_NULL))
P(f"⚖️ ① agreement lines beating random in ≥3 of 4 periods · REAL {sum(1 for _, w in AG_REAL if w >= 3)} ‖ SHUFFLED: "
  + " · ".join(str(sum(1 for _, w in g if w >= 3)) for g in AG_NULL))
for fr, h, nm in H3:
    for side in (1, -1):
        r = REAL[(fr, h, side)]
        nl = NULL[(fr, h, side)]
        pc = sorted(c / b * 100 for a_, b, c in nl if b)
        P(f"⚖️ ③ {nm} {'BUY ' if side > 0 else 'SELL'} · REAL: consistent in P1-3 {r[0]} · judged {r[1]} · held in P4 {r[2]}"
          + (f" ({r[2] / r[1] * 100:.0f}%)" if r[1] else "") + " ‖ SHUFFLED (luck alone) found/judged/held: "
          + " · ".join(f"{a_}/{b}/{c}" for a_, b, c in nl)
          + (f" · held % from {pc[0]:.0f} to {pc[-1]:.0f} (middle {pc[len(pc) // 2]:.0f})" if pc else ""))
P(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
