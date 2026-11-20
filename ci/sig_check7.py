# 🔬 seventh pass — the owner (20-11): «انا اريد كل اشارات اتضيفها · واريد الاشارات الي اذا تتقارب مع بعض مستوى ثاني تحقق · والمستوى الثالث
#   النهائي · المؤشرات الاشعارا فريم 4 ساعات واليومي · والتوقعات اريدها مضبوطه». The three levels measured on REAL OKX prices exactly as
#   they would run (the 36 systems of ci/sig_check6.py — the same code, read from it):
#   · LEVEL 1 — every system on the 4-hour and the daily candles: BUY / SELL / nothing (a signal lives a few candles: 4H 3 · 1D 2)
#   · LEVEL 2 — the families (trend · momentum · volatility · pattern/levels · volume) on ONE frame: ≥ K families say the same, none the other
#   · LEVEL 3 — the final: LEVEL 2 the same way on the 4-hour AND on the last closed daily candle
#   · each system's weight = its edge on the first 60% of time only (0 if it did not help) · everything judged on the last 40% apart
#   · judged after 1 day · 3 days · 7 days (4-hour closes) · net after 0.2% fees · against ANY 4-hour candle of the same coins and time
#   · the forecast's «صدق %» checked: the hit rate the learning part promises vs what the test part gave (calibration)
#   · the OLD indicators too (the owner: «هل مشمول المؤشرات القديمة؟»): the 10 readings of 📊 (Volume Profile · VWAP · order flow · price
#     action · EMA 50/200 · Supertrend · MACD · RSI · ADX · CMF) and the 📊 verdict — the dashboard's own _i2_signals / _i2_combine on the same
#     candles (a reading becomes a signal when it turns ≥ +0.5 / ≤ −0.5 · the verdict at ±15) — and 🟢 the bottom (daily · its own _bot_at)
#   python3 ci/sig_check7.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG7
import bisect, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "sig_check6.py"), encoding="utf-8").read().split("\nT0 = time.time()")[0]
exec(compile(_src, "sig_check6_systems", "exec"))                 # the indicators · the 36 systems · fetching · mirror · fwd


def hit(v):
    return sum(1 for x in v if x > 0) / len(v) * 100 if v else 0.0


def pct(x):
    return f"{x * 100:+.2f}%"


def P7(*a):
    print("HOLYSIG7", *a, flush=True)


F4, FD = "4H", "1Dutc"
N4, ND = (900 if FAKE else 4400), (500 if FAKE else 1100)
LOOK = {F4: 3, FD: 2}
HZ = (6, 18, 42)                     # 1 day · 3 days · 7 days of 4-hour candles
FAMS = ("trend", "momentum", "volatility", "pattern", "volume")
T0 = time.time()
P7("dashboard", m.APP_VERSION, "· coins", len(COINS), "· systems", len(SYS), "· fake" if FAKE else "· REAL OKX")


OLD_FAM = {"vp": "pattern", "avwap": "pattern", "pa": "pattern", "of": "volume", "cmf": "volume", "trend": "trend", "st": "trend", "adx": "trend",
           "macd": "momentum", "rsi": "momentum"}
for _k, _nm, _ic, _w, _d in m._IND2_K:
    SYS["O-" + _k] = ("OLD " + _ic + " " + _nm, OLD_FAM.get(_k, "trend"), None)
SYS["O-verdict"] = ("OLD 📊 the verdict (all ten)", "trend", None)
SYS["O-bottom"] = ("OLD 🟢 the bottom (daily)", "volatility", None)


def old_events(D, daily):
    """the dashboard's own readings on these candles ⇒ BUY when a reading turns ≥ +0.5 · SELL ≤ −0.5 (the verdict ±15 · the bottom ≥ 50)"""
    O, H, L, C, V = D["O"], D["H"], D["L"], D["C"], D["V"]
    S2 = m._i2_series(O, H, L, C, V)
    DD = {"o": O, "h": H, "l": L, "c": C, "v": V, "t": D["T"]}
    base = {k: w for k, _, _, w, _ in m._IND2_K}
    prev, ev = {}, {}
    for t in range(210, D["n"]):
        try:
            sg, _ = m._i2_signals(DD, S2, t)
        except Exception:
            continue
        cur = {("O-" + k): (1 if v >= 0.5 else -1 if v <= -0.5 else 0) for k, (v, _) in sg.items()}
        sc = m._i2_combine(sg, base) * 100
        cur["O-verdict"] = 1 if sc >= 15 else -1 if sc <= -15 else 0
        if daily:
            a = m._bot_at(C, S2["rsi"], t)
            cur["O-bottom"] = 1 if a and a[0] >= 50 else 0
        for k, v in cur.items():
            if v and v != prev.get(k, 0):
                ev.setdefault((k, v), []).append(t)
        prev = cur
    return ev


def frame(rows, blk):
    D = {"T": [int(r[0]) for r in rows], "O": [float(r[1]) for r in rows], "H": [float(r[2]) for r in rows], "L": [float(r[3]) for r in rows],
         "C": [float(r[4]) for r in rows], "V": [float(r[5]) for r in rows], "n": len(rows), "blk": blk}
    S1, Dm = build(D), mirror(D)
    Sm = build(Dm)
    ev = {}
    try:
        for k, lst in old_events(D, blk == 5).items():
            ev[k] = lst
    except Exception as ex:
        P7(f"old indicators error: {type(ex).__name__} {ex}")
    for code, (name, fam, fn) in SYS.items():
        if fn is None:
            continue
        for side, DD, SS in ((1, D, S1), (-1, Dm, Sm)):
            try:
                ev[(code, side)] = sorted(i for i in fn(DD, SS) if i >= 210)
            except Exception as ex:
                P7(f"error {code}: {type(ex).__name__} {ex}"); ev[(code, side)] = []
    return D, ev


COIN = {}
for sym in COINS:
    try:
        r4, rd = hist(sym, F4, N4), hist(sym, FD, ND)
    except Exception as ex:
        P7(f"{sym}: fetch error {ex}"); continue
    if len(r4) < 700 or len(rd) < 300:
        continue
    D4, E4 = frame(r4, 6)
    Dd, Ed = frame(rd, 5)
    split_t = D4["T"][int(D4["n"] * 0.6)]                      # one moment splits both frames: before = learn · after = test
    COIN[sym] = (D4, E4, Dd, Ed, split_t)
P7(f"{len(COIN)} coins · {time.time() - T0:.0f}s")


# ── the weights: each system's edge (per frame · per side) on the learning part only ──
def edge_w(fr, h):
    W = {}
    base = {1: [], -1: []}
    acc = {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        D, E = (D4, E4) if fr == F4 else (Dd, Ed)
        C, T = D["C"], D["T"]
        for side in (1, -1):
            for i in range(210, D["n"]):
                if T[i] >= st:
                    break
                x = fwd(C, i, h, side)
                if x is not None:
                    base[side].append(x)
        for k, lst in E.items():
            for i in lst:
                if T[i] >= st:
                    break
                x = fwd(C, i, h, k[1])
                if x is not None:
                    acc.setdefault(k, []).append(x)
    for k, v in acc.items():
        e = mean(v) - mean(base[k[1]])
        W[k] = max(0.0, e) * 100 if len(v) >= 30 else 0.0
    return W


W = {F4: edge_w(F4, 6), FD: edge_w(FD, 1)}
for fr in (F4, FD):
    good = sorted(((w, k) for k, w in W[fr].items() if w > 0), reverse=True)
    P7(f"{fr}: {len(good)} system-sides helped while learning: " + " · ".join(f"{k[0]}{'↑' if k[1] > 0 else '↓'} {w:.2f}" for w, k in good[:24]))


def state_series(D, E, Wf, look):
    """per candle: {family: weighted vote} from the systems that fired in the last `look` candles (latest event per system-side)"""
    n = D["n"]
    last = {k: -10 ** 9 for k in E}
    ptr = {k: 0 for k in E}
    out = [None] * n
    for i in range(n):
        for k, lst in E.items():
            while ptr[k] < len(lst) and lst[ptr[k]] <= i:
                last[k] = lst[ptr[k]]; ptr[k] += 1
        fam, score, l1 = {}, 0.0, [0, 0]
        for k, t in last.items():
            if i - t < look:
                l1[0 if k[1] > 0 else 1] += 1
                w = Wf.get(k, 0.0)
                if w > 0:
                    f = SYS[k[0]][1]
                    fam[f] = fam.get(f, 0.0) + k[1] * w
                    score += k[1] * w
        out[i] = (fam, score, l1)
    return out


def lvl2(st, K):
    fam = st[0]
    up = sum(1 for v in fam.values() if v > 0); dn = sum(1 for v in fam.values() if v < 0)
    return 1 if up >= K and dn == 0 else (-1 if dn >= K and up == 0 else 0)


SER = {}
for sym, (D4, E4, Dd, Ed, st) in COIN.items():
    SER[sym] = (state_series(D4, E4, W[F4], LOOK[F4]), state_series(Dd, Ed, W[FD], LOOK[FD]))
P7(f"states built · {time.time() - T0:.0f}s")


def daily_at(Dd, t4):
    """the last daily candle CLOSED when the 4-hour candle opened at t4 closes"""
    j = bisect.bisect_right(Dd["T"], t4 + 14400 - 86400) - 1
    return j


def judge(name, picks, test=True):
    """picks: {sym: [(i4, side)]} on the 4-hour candles — edge-triggered events · prints the line"""
    res = {h: [] for h in HZ}
    base = {h: {1: [], -1: []} for h in HZ}
    nco = 0
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        C, T = D4["C"], D4["T"]
        lst = [(i, s) for i, s in picks.get(sym, []) if (T[i] >= st) == test]
        nco += 1 if lst else 0
        for hi, h in enumerate(HZ):
            for i, s in lst:
                x = fwd(C, i, h, s)
                if x is not None:
                    res[h].append((s, x))
            for i in range(210, D4["n"]):
                if (T[i] >= st) != test:
                    continue
                for s in (1, -1):
                    x = fwd(C, i, h, s)
                    if x is not None:
                        base[h][s].append(x)
    parts = []
    for s, lab in ((1, "BUY"), (-1, "SELL")):
        segs = []
        for h in HZ:
            v = [x for ss, x in res[h] if ss == s]
            b = base[h][s]
            segs.append(f"{h // 6}d hit {hit(v):.0f}% (rand {hit(b):.0f}) edge {pct(mean(v) - mean(b))}")
        n_ = len([1 for ss, x in res[HZ[1]] if ss == s])
        parts.append(f"{lab} n {n_}: " + " · ".join(segs))
    P7(f"{name} [{'TEST' if test else 'learn'} · {nco} coins] " + " ‖ ".join(parts))
    return res


def edges(series, cond):
    """edge-triggered: the candle where cond(i) becomes non-zero (or flips)"""
    out, prev = [], 0
    for i in range(len(series)):
        c = cond(i)
        if c and c != prev:
            out.append((i, c))
        prev = c
    return out


P7("══ every system alone on the 4-hour and the daily (TEST · 3 days · net after fees · vs any candle) — the old ones first ══")
for fr, hh in ((F4, 18), (FD, 3)):
    bs = {1: [], -1: []}; acc = {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        D, E = (D4, E4) if fr == F4 else (Dd, Ed)
        C, T = D["C"], D["T"]
        for side in (1, -1):
            for i in range(210, D["n"]):
                if T[i] >= st:
                    x = fwd(C, i, hh, side)
                    if x is not None:
                        bs[side].append(x)
        for k, lst in E.items():
            for i in lst:
                if T[i] >= st:
                    x = fwd(C, i, hh, k[1])
                    if x is not None:
                        acc.setdefault(k, []).append(x)
    rows = []
    for k, v in acc.items():
        e = mean(v) - mean(bs[k[1]])
        rows.append((0 if k[0].startswith("O-") else 1, -e, f"{fr} {'BUY ' if k[1] > 0 else 'SELL'} {k[0]:9s} {SYS[k[0]][0][:36]:36s} n {len(v):5d} · hit {hit(v):5.1f}% "
                     f"(rand {hit(bs[k[1]]):.1f}) · edge {pct(e)} · weight {W[fr].get(k, 0):.2f} {'✅' if e > 0 and W[fr].get(k, 0) > 0 and len(v) >= 30 else '—'}"))
    for _, _, ln in sorted(rows):
        P7(ln)

P7("══ LEVEL 1 — every system alone (4-hour · judged after 1 · 3 · 7 days) ══")
L1 = {}
for sym, (D4, E4, Dd, Ed, st) in COIN.items():
    L1[sym] = [(i, k[1]) for k, lst in E4.items() for i in lst]
judge("L1 all systems pooled (4H)", L1)
L1w = {sym: [(i, k[1]) for k, lst in E4.items() if W[F4].get(k, 0) > 0 for i in lst] for sym, (D4, E4, Dd, Ed, st) in COIN.items()}
judge("L1 only the systems that helped while learning (4H)", L1w)

P7("══ LEVEL 2 — families agree on one frame ══")
for K in (2, 3, 4):
    pk4, pkd = {}, {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        s4, sd = SER[sym]
        pk4[sym] = edges(s4, lambda i: lvl2(s4[i], K) if s4[i] else 0)
        ev = []
        for i in range(D4["n"]):                             # the daily level 2 as seen at each 4-hour candle
            j = daily_at(Dd, D4["T"][i])
            ev.append(lvl2(sd[j], K) if j >= 0 and sd[j] else 0)
        pkd[sym] = edges(ev, lambda i: ev[i])
    judge(f"L2 ≥{K} families · 4H", pk4)
    judge(f"L2 ≥{K} families · daily", pkd)

P7("══ LEVEL 3 — the final: level 2 the same way on the 4-hour AND the daily ══")
CAL = {}
for K in (2, 3):
    for thr in (0.0, 0.5, 1.0):
        pk = {}
        for sym, (D4, E4, Dd, Ed, st) in COIN.items():
            s4, sd = SER[sym]
            ev = []
            for i in range(D4["n"]):
                j = daily_at(Dd, D4["T"][i])
                a = lvl2(s4[i], K) if s4[i] else 0
                b = lvl2(sd[j], K) if j >= 0 and sd[j] else 0
                sc = (s4[i][1] if s4[i] else 0.0) + (sd[j][1] if j >= 0 and sd[j] else 0.0)
                ev.append(a if a and a == b and a * sc >= thr else 0)
            pk[sym] = edges(ev, lambda i: ev[i])
        lr = judge(f"L3 ≥{K} families both frames · score ≥ {thr}", pk, test=False)
        te = judge(f"L3 ≥{K} families both frames · score ≥ {thr}", pk, test=True)
        for s in (1, -1):
            a = [x for ss, x in lr[HZ[1]] if ss == s]; b = [x for ss, x in te[HZ[1]] if ss == s]
            CAL[(K, thr, s)] = (hit(a), len(a), hit(b), len(b))
P7("══ the forecast's «صدق %» — what the learning part promises vs what the test gave (3 days) ══")
for (K, thr, s), (ha, na, hb, nb) in sorted(CAL.items()):
    P7(f"L3 ≥{K} · score ≥ {thr} · {'BUY ' if s > 0 else 'SELL'}: learned {ha:.0f}% (n {na}) → test {hb:.0f}% (n {nb}) · gap {hb - ha:+.0f} points")

P7("══ the last 8 final signals of the test (L3 ≥3 · score ≥ 0.5) ══")
lastev = []
for sym, (D4, E4, Dd, Ed, st) in COIN.items():
    s4, sd = SER[sym]
    ev = []
    for i in range(D4["n"]):
        j = daily_at(Dd, D4["T"][i])
        a = lvl2(s4[i], 3) if s4[i] else 0
        b = lvl2(sd[j], 3) if j >= 0 and sd[j] else 0
        sc = (s4[i][1] if s4[i] else 0.0) + (sd[j][1] if j >= 0 and sd[j] else 0.0)
        ev.append(a if a and a == b and a * sc >= 0.5 else 0)
    for i, s in edges(ev, lambda i: ev[i]):
        if D4["T"][i] >= st:
            x = fwd(D4["C"], i, 18, s)
            lastev.append((D4["T"][i], sym, s, x))
for t, sym, s, x in sorted(lastev)[-8:]:
    P7(f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(t))} UTC · {sym} · {'BUY' if s > 0 else 'SELL'} · 3 days later net {pct(x) if x is not None else '—'}")
P7(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
