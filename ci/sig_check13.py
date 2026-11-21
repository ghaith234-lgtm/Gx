# 🔬 Holy signals check, thirteenth pass — the indicator tables on the past (the owner 21-11: «جيد وسوي اختبار كيف يتنبء وتجي التنبيهات قبل
#    ما يتحرك السعر … التوليفات اختار فقط القوية ومثل ما قال جمناي وحسب الفحص … كل المؤشرات تسوي تنبيه وتختبر نفسها الجيد يصعد فوق والسيء
#    ينزل جوة»).
#    ① THE TABLES LIVE IN THE PAST: every row (1–70 · the dashboard's own SB_ROWS and scan code) predicts when it fires — its side for the next
#       candle of its frame (1H · 4H · 1D) — counted FROM ZERO from 12 months ago, per coin and «*» every coin together, exactly the board's
#       rule · what would have reached the owner under the inner filter (a row's own record so far: ≥ N different days and ≥ X%) · vs 50% and
#       vs the same walk on shuffled prices
#    ② STRONG COMBOS by Gemini's rule (one indicator per family · 2 or 3 together · agreeing, none against, the moment they start agreeing):
#       chosen on the history BEFORE each quarter only, then run on that quarter unseen · 4 quarters · vs shuffled · and Gemini's four by name
#       (صيد الاتجاه · اصطياد الانفجارات والارتدادات · فلتر السوق العرضي · قراءة الحيتان)
#    ③ LEAD TIME: for what would have reached the owner — how much the price moved its way in the candles BEFORE the alert vs AFTER it
#    Results: lines HOLYSIG13 + /tmp/holysig13.json. Public market data only — no keys, no orders, no notifications.
#    python3 ci/sig_check13.py Holy_Dashboard.pyw
import bisect, importlib.machinery, importlib.util, itertools, json, math, os, random, shutil, sys, tempfile, time
import numpy as np

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig13_")
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
OUT = {}


def P(*a):
    print("HOLYSIG13", *a, flush=True)


DRY = os.environ.get("SIG13_DRY") == "1"
EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
FRS = ("1H", "4H", "1D")
NUM = dict(m.SB_NUM)
FAM = {c: (m._sg_plain(c) or ("market",))[0] for c in NUM}
GEMINI = (("صيد الاتجاه", ("O-trend", "O-rsi", "O-cmf")),                 # EMA 50 + RSI + OBV (our money flow)
          ("اصطياد الانفجارات والارتدادات", ("18", "O-rsi", "32")),       # Bollinger + RSI + volume
          ("فلتر السوق العرضي", ("O-adx", "O-macd", "15")),               # ADX + MACD + ATR (Keltner on ATR)
          ("قراءة الحيتان", ("O-avwap", "O-vp", "P-tk")))                # VWAP + support/resistance + the futures (OI/funding not in history)
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· rows", len(NUM), "· frames", FRS)

# ── the prices (public) — the hour 15 months · 4 hours 2 years · the day 7 years
if DRY:
    COINS = COINS[:12]
    rnd0 = random.Random(3)
    now_ = int(time.time())
    cdb = {"c1": {}, "c4": {}, "c": {}}
    for sec, step, n in (("c1", 3600, 2400), ("c4", 14400, 1500), ("c", 86400, 900)):
        tend = now_ // step * step - step
        for j, s in enumerate(COINS):
            p, rows = 10.0 + j, []
            for i in range(n):
                r = rnd0.gauss(0.0001, 0.01 * (2 if sec == "c" else 1))
                o, c = p, p * math.exp(r)
                rows.append([tend - (n - 1 - i) * step, o, max(o, c) * 1.003, min(o, c) * 0.997, c, 1000 + rnd0.random() * 500])
                p = c
            cdb[sec][s] = {"d": rows}
    db, fdb = {}, {}
else:
    m.SG_N["1H"] = 11000
    cdb = {}
    m._sg_refresh(COINS, list(FRS), cdb)
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
P(f"prices fetched · {time.time() - T0:.0f}s · " + " · ".join(f"{fr} {sum(1 for e in (cdb.get(m.SG_BAR[fr][0]) or {}).values() if len(e.get('d') or []) > 400)} coins"
                                                          for fr in FRS))


def shuffled(db_, seed):
    rnd = random.Random(seed)
    out = {}
    for sec in ("c", "c4", "c1"):
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


def breadth_full(F, fr):
    """📊 the dashboard's rule (_sb_wide) on the whole history: 60% above their 50-candle mean ⇒ up · 40% ⇒ down · back only past the middle"""
    AB = {}
    for sym, (D, E) in F.items():
        C = D["C"]
        s = 0.0
        for i in range(D["n"]):
            s += C[i]
            if i >= 50:
                s -= C[i - 50]
            if i >= 49:
                AB.setdefault(D["T"][i], []).append(C[i] > s / 50.0)
    cur, ev = 0, {}
    for t in sorted(AB):
        a = AB[t]
        if len(a) < 10:
            continue
        sh = sum(a) / len(a)
        nxt = 1 if sh >= 0.6 else -1 if sh <= 0.4 else (0 if (cur > 0 and sh < 0.5) or (cur < 0 and sh > 0.5) else cur)
        if nxt and nxt != cur:
            ev[t] = nxt
        cur = nxt
    for sym, (D, E) in F.items():
        for i in range(210, D["n"]):
            s = ev.get(D["T"][i])
            if s:
                E.setdefault(("W-breadth", s), []).append(i)


def comp_full(F):
    if "BTC-USDT" not in F:
        return
    seq = m._sg_compass_states(F["BTC-USDT"][0], [D for D, E in F.values()])
    ch = {seq[k][0]: (1 if seq[k][2] == "up" else -1) for k in range(1, len(seq)) if seq[k][2] != seq[k - 1][2] and seq[k][2] in ("up", "down")}
    for sym, (D, E) in F.items():
        for i in range(210, D["n"]):
            s = ch.get(D["T"][i])
            if s:
                E.setdefault(("W-comp", s), []).append(i)


def prep(db_):
    """every coin × frame: the candles and the dashboard's own events (the scan's code on the whole history — causal: checked in check 12 ⓪)"""
    btc = {int(r[0]): float(r[4]) for r in ((db_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []}
    COIN = {fr: {} for fr in FRS}
    for sym in COINS:
        rd = ((db_.get("c") or {}).get(sym) or {}).get("d") or []
        if len(rd) < 300:
            continue
        ctx = m._sg_ctx(sym, rd, db, mkt, fng, btc)
        for fr in FRS:
            rows = ((db_.get(m.SG_BAR[fr][0]) or {}).get(sym) or {}).get("d") or []
            if len(rows) < 400:
                continue
            D, E = m._sg_events(rows, fr == "1D", ctx, dx=m.SG_SEC[fr])
            COIN[fr][sym] = (D, E)
    for fr in ("1H", "4H"):
        F = COIN[fr]
        if len(F) >= 10:
            CR, Z = m._sg_crash(F, k0=210)
            m._sb_surge(F, Z, 210)
    for fr in FRS:
        if len(COIN[fr]) >= 10:
            breadth_full(COIN[fr], fr)
    comp_full(COIN["1D"])
    return COIN


def arrays(COIN):
    """per frame · coin: the next candle's direction (+1 · −1 · 0) · the day of each candle · each row's firing (side per candle, the board's rule) ·
    each code's «active» window (fired within the frame's «together» candles) for the combos"""
    A = {}
    for fr, F in COIN.items():
        lk = m.SG_LK[fr]
        for sym, (D, E) in F.items():
            C = np.array(D["C"], dtype=float)
            nx = np.zeros(len(C), dtype=np.int8)
            nx[:-1] = np.sign(C[1:] - C[:-1]).astype(np.int8)
            T = np.array(D["T"], dtype=np.int64)
            act = {}
            fire = {}
            for (code, s), lst in E.items():
                if code not in NUM:
                    continue
                idx = np.array([i for i in lst if 0 <= i < len(C)], dtype=np.int64)
                if not len(idx):
                    continue
                ev = np.zeros(len(C), dtype=np.int32)
                ev[idx] = 1
                cs = np.cumsum(ev)
                w = cs.copy()
                w[lk:] -= cs[:-lk]
                act[(code, s)] = w > 0
                if code in m.SB_ONE and s != m.SB_ONE[code]:
                    continue
                f = fire.setdefault(code, np.zeros(len(C), dtype=np.int8))
                both = (f != 0) & (ev > 0) & (f != s)
                f[ev > 0] = s
                f[both] = 0                                           # both sides at once ⇒ no prediction
            A[(fr, sym)] = {"nx": nx, "T": T, "day": T // 86400, "C": C, "act": act, "fire": fire}
    return A


def wilson(w, n, z=1.96):
    if n <= 0:
        return 0.0
    p = w / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def zsc(w, n, p0=0.5):
    return (w - n * p0) / math.sqrt(n * p0 * (1 - p0)) if n else 0.0


# ── ① the tables live in the past (from zero) — and what the inner filter would have let through
FILT = [(nd, th) for nd in (15, 30, 50) for th in (0.55, 0.60, 0.65, 0.70)]


def board_walk(A, t_start, label, pooled=True):
    """chronological: every firing of every row (singles, then the given combos) on every coin and frame from t_start · the record grows from zero
    (✅ ❌ · different days) per coin and «*» · a firing «would notify» when the row's record BEFORE it passes the filter · its lead time"""
    evs = []
    for (fr, sym), a in A.items():
        T, nx, day, C = a["T"], a["nx"], a["day"], a["C"]
        for code, f in a["fire"].items():
            idx = np.nonzero((f != 0) & (T >= t_start))[0]
            for i in idx:
                if i + 1 >= len(C) or nx[i] == 0:
                    continue
                evs.append((int(T[i]) + m.SG_SEC[fr], fr, sym, code, int(f[i]), int(nx[i]) == int(f[i]), int(day[i]), int(i)))
    evs.sort(key=lambda e: e[0] - m.SG_SEC[e[1]])               # in the order they are DECIDED (the candle's close) …
    import heapq
    pend = []                                                   # … and a result counts only once its own candle closed (no peeking)
    rec_c, rec_a = {}, {}
    tot = {fr: [0, 0] for fr in FRS}
    rows = {}
    note = {(fr, k): [0, 0, [], []] for fr in FRS for k in FILT}
    note_c = {(fr, k): [0, 0] for fr in FRS for k in FILT}
    def settle(t_now):
        while pend and pend[0][0] <= t_now:
            td, fr_, sym_, code_, ok_, d_ = heapq.heappop(pend)
            for rec, key in ((rec_a, (code_, fr_)), (rec_c, (sym_, code_, fr_))):
                r = rec.setdefault(key, [0, 0, 0, -1])
                r[0 if ok_ else 1] += 1
                if d_ != r[3]:
                    r[2] += 1
                    r[3] = d_
    for tdone, fr, sym, code, s, ok, d, i in evs:
        settle(tdone - m.SG_SEC[fr])
        for rec, key, store in ((rec_a, (code, fr), note), (rec_c, (sym, code, fr), note_c)):
            r = rec.get(key)
            if r:
                n_ = r[0] + r[1]
                p = r[0] / n_
                for k in FILT:
                    if r[2] >= k[0] and p >= k[1]:
                        x = store[(fr, k)]
                        x[0 if ok else 1] += 1
                        if store is note and len(x) > 2:
                            C = A[(fr, sym)]["C"]
                            if i >= 3 and i + 3 < len(C):
                                x[2].append(s * (C[i] / C[i - 3] - 1.0))
                                x[3].append((s * (C[i + 1] / C[i] - 1.0), s * (C[i + 3] / C[i] - 1.0)))
        heapq.heappush(pend, (tdone, fr, sym, code, ok, d))
        tot[fr][0 if ok else 1] += 1
        rr = rows.setdefault((code, fr), [0, 0])
        rr[0 if ok else 1] += 1
    res = {"tot": tot, "note": {}, "rows": {}}
    for fr in FRS:
        w, l = tot[fr]
        P(f"{label} ① {fr}: every firing of every row on every coin — {100 * w / max(1, w + l):.1f}% right of {w + l} (the board's rule: the next candle's direction)")
        for k in FILT:
            for nm, store in (("«*» all coins", note), ("the coin's own", note_c)):
                x = store[(fr, k)]
                n_ = x[0] + x[1]
                if not n_:
                    continue
                line = f"{label} ① {fr} filter ≥{k[0]} days · ≥{int(k[1] * 100)}% on {nm} record: {100 * x[0] / n_:.1f}% right of {n_} · z {zsc(x[0], n_):+.1f}"
                if store is note and x[2]:
                    bf, a1, a3 = np.mean(x[2]), np.mean([y[0] for y in x[3]]), np.mean([y[1] for y in x[3]])
                    early = np.mean([1.0 if b > 2 * max(1e-9, abs(z3)) else 0.0 for b, (z1, z3) in zip(x[2], x[3])])
                    line += f" · ③ moved its way BEFORE (3 candles) {bf * 100:+.2f}% · AFTER 1 {a1 * 100:+.2f}% · AFTER 3 {a3 * 100:+.2f}% · most of the move before in {early * 100:.0f}%"
                    res["note"][f"{fr}|{k[0]}|{k[1]}"] = {"w": x[0], "n": n_, "before": round(float(bf), 5), "after1": round(float(a1), 5), "after3": round(float(a3), 5)}
                P(line)
        best = sorted(((w_ / max(1, w_ + l_), w_ + l_, c) for (c, f_), (w_, l_) in rows.items() if f_ == fr and w_ + l_ >= 200), reverse=True)
        P(f"{label} ① {fr} rows with ≥200 results, the best: " + " · ".join(f"{NUM[c]} {100 * p:.0f}% ({n_})" for p, n_, c in best[:8])
          + " | the worst: " + " · ".join(f"{NUM[c]} {100 * p:.0f}% ({n_})" for p, n_, c in best[-5:]))
        res["rows"][fr] = {str(NUM[c]): [round(p, 4), n_] for p, n_, c in best}
    return res


# ── ② combos: Gemini's rule (one per family) · chosen before each quarter · run on it unseen
def combo_list():
    by = {}
    for c in NUM:
        by.setdefault(FAM[c], []).append(c)
    fams = sorted(by)
    out = []
    for k in (2, 3):
        for fs in itertools.combinations(fams, k):
            for cs in itertools.product(*[by[f] for f in fs]):
                out.append(tuple(cs))
    return out


def frame_cat(A, fr):
    """every coin of a frame joined end to end (the combos are counted on one long array — the coins' borders kept apart)"""
    keys = sorted(k for k in A if k[0] == fr)
    if not keys:
        return None
    lens = [len(A[k]["C"]) for k in keys]
    n = sum(lens)
    start = np.zeros(n, dtype=bool)
    valid = np.ones(n, dtype=bool)
    o = 0
    for L_ in lens:
        start[o] = True
        valid[o + L_ - 1] = False                                  # the last candle has no next candle yet
        o += L_
    codes = {k2 for k in keys for k2 in A[k]["act"]}
    act = {}
    for cs in codes:
        act[cs] = np.concatenate([A[k]["act"].get(cs, np.zeros(len(A[k]["C"]), dtype=bool)) for k in keys])
    return {"act": act, "nx": np.concatenate([A[k]["nx"] for k in keys]), "T": np.concatenate([A[k]["T"] for k in keys]), "start": start, "valid": valid}


def combo_stats(A, combos, bounds):
    """for every combo × side × frame: ✅ ❌ and the different days between the bounds (pooled over coins) — the agreement rule of the board
    (every member fired its side within the frame's «together» candles · none the other side · the first candle they agree)"""
    st = {}
    nb = len(bounds) - 1
    for fr in FRS:
        Fc = frame_cat(A, fr)
        if Fc is None:
            continue
        act, nx, T, start, valid = Fc["act"], Fc["nx"], Fc["T"], Fc["start"], Fc["valid"]
        seg_all = np.searchsorted(bounds, T, side="right") - 1
        for cb in combos:
            for s in (1, -1):
                xs = [act.get((c, s)) for c in cb]
                if any(x is None for x in xs):
                    continue
                on = xs[0] & xs[1]
                for x in xs[2:]:
                    on &= x
                if not on.any():
                    continue
                for c in cb:
                    y = act.get((c, -s))
                    if y is not None:
                        on &= ~y
                edge = on.copy()
                edge[1:] &= ~(on[:-1] & ~start[1:])
                edge &= valid
                idx = np.nonzero(edge)[0]
                if not len(idx):
                    continue
                hit, seg, dd = nx[idx], seg_all[idx], T[idx] // 86400
                W = np.bincount(seg[hit == s], minlength=nb)[:nb]
                L = np.bincount(seg[hit == -s], minlength=nb)[:nb]
                ND = [int(len(np.unique(dd[seg == j]))) for j in range(nb)]
                st[(fr, cb, s)] = (W, L, ND)
        del Fc
    return st


def combo_walk(A, label, cuts, t_end, K=10):
    combos = combo_list()
    t_first = min(int(a["T"][0]) for a in A.values())
    bounds = np.array([t_first] + list(cuts) + [t_end + 1], dtype=np.int64)   # segment 0 = before the first quarter · 1..4 = the quarters
    t1 = time.time()
    st = combo_stats(A, combos, bounds)
    P(f"{label} ② {len(combos)} combos (one per family · 2 or 3) × 2 sides × 3 frames · {len(st)} ever fired · {time.time() - t1:.0f}s")
    res = {}
    for fr in FRS:
        agg = [0, 0]
        per_q = []
        for q in range(len(cuts)):
            cand = []
            for (f_, cb, s), (W, L, ND) in st.items():
                if f_ != fr:
                    continue
                w, l, nd = int(W[:q + 1].sum()), int(L[:q + 1].sum()), int(sum(ND[:q + 1]))
                n_ = w + l
                if n_ >= 50 and nd >= 30 and w / n_ >= 0.55 and wilson(w, n_) >= 0.5:
                    cand.append((wilson(w, n_), cb, s, w, n_))
            cand.sort(reverse=True)
            pick = cand[:K]
            tw = sum(int(st[(fr, cb, s)][0][q + 1]) for _, cb, s, _, _ in pick)
            tl = sum(int(st[(fr, cb, s)][1][q + 1]) for _, cb, s, _, _ in pick)
            agg[0] += tw; agg[1] += tl
            per_q.append((len(cand), len(pick), tw, tl))
        n_ = agg[0] + agg[1]
        beat = sum(1 for c_, p_, w_, l_ in per_q if w_ + l_ and w_ / (w_ + l_) > 0.5)
        P(f"{label} ② {fr}: the top {K} chosen on the past, run on each unseen quarter — {100 * agg[0] / max(1, n_):.1f}% right of {n_} · z {zsc(agg[0], n_):+.1f} · "
          f"above 50% in {beat}/{len(per_q)} quarters · " + " · ".join(f"q{q + 1}: {c_} passed, {100 * w_ / max(1, w_ + l_):.0f}% of {w_ + l_}" for q, (c_, p_, w_, l_) in enumerate(per_q)))
        res[fr] = {"w": agg[0], "n": n_, "beat": beat, "q": per_q}
    # the final choice on the whole history (what the dashboard would carry) — only if the procedure beat chance unseen
    final = []
    for fr in FRS:
        cand = []
        for (f_, cb, s), (W, L, ND) in st.items():
            if f_ != fr:
                continue
            w, l, nd = int(W.sum()), int(L.sum()), int(sum(ND))
            n_ = w + l
            # ~200,000 tests (33,029 combos × 2 sides × 3 frames): a lower bound at z 4.4 (≈ one false pick in 200,000 by luck) must stay above 50%
            if n_ >= 80 and nd >= 40 and wilson(w, n_, 4.4) >= 0.5 and int(W[-1]) + int(L[-1]) >= 10 and W[-1] / max(1, W[-1] + L[-1]) >= 0.5:
                cand.append((wilson(w, n_, 4.4), cb, s, w, n_))
        cand.sort(reverse=True)
        for lb, cb, s, w, n_ in cand[:K]:
            final.append({"fr": fr, "codes": list(cb), "side": s, "nums": [NUM[c] for c in cb], "w": w, "n": n_, "lb": round(lb, 4)})
            P(f"{label} ② final {fr} {'⬆️' if s > 0 else '⬇️'} {' + '.join(str(NUM[c]) for c in cb)} ({' + '.join(cb)}): {100 * w / n_:.1f}% of {n_} · strict lower bound {100 * lb:.1f}% · "
              f"the procedure unseen on {fr}: {100 * res[fr]['w'] / max(1, res[fr]['n']):.1f}% (z {zsc(res[fr]['w'], res[fr]['n']):+.1f})")
        if not cand:
            P(f"{label} ② final {fr}: no combo passes the strict bound (z 4.4) on the whole history")
    # Gemini's four by name (no choosing — as they are)
    gem = {}
    for nm, cb in GEMINI:
        miss = [c for c in cb if c not in NUM]
        s1 = combo_stats(A, [tuple(cb)], bounds)
        for fr in FRS:
            for s in (1, -1):
                x = s1.get((fr, tuple(cb), s))
                if not x:
                    P(f"{label} ② Gemini «{nm}» {fr} {'⬆️' if s > 0 else '⬇️'}: never fired" + (f" (missing {miss})" if miss else ""))
                    continue
                W, L, ND = x
                w, l = int(W[1:].sum()), int(L[1:].sum())
                n_ = w + l
                beat = sum(1 for j in range(1, len(W)) if W[j] + L[j] and W[j] / (W[j] + L[j]) > 0.5)
                P(f"{label} ② Gemini «{nm}» {fr} {'⬆️' if s > 0 else '⬇️'}: the last 12 months {100 * w / max(1, n_):.1f}% right of {n_} · z {zsc(w, n_):+.1f} · "
                  f"above 50% in {beat}/4 quarters · all history {100 * int(W.sum()) / max(1, int(W.sum() + L.sum())):.1f}% of {int(W.sum() + L.sum())}")
                gem[f"{nm}|{fr}|{s}"] = {"w": w, "n": n_, "beat": beat}
    return res, final, gem


COIN = prep(cdb)
P(f"events ready · {time.time() - T0:.0f}s · " + " · ".join(f"{fr} {len(COIN[fr])} coins" for fr in FRS))
A = arrays(COIN)
t_end = min(max(int(a["T"][-1]) for (f_, s), a in A.items() if f_ == fr) for fr in FRS if any(f_ == fr for f_, s in A))
CUTS = [t_end - (4 - q) * 91 * 86400 for q in range(4)]
if DRY:
    CUTS = [t_end - (4 - q) * 20 * 86400 for q in range(4)]
P("the 12 months from", time.strftime("%Y-%m-%d", time.gmtime(CUTS[0])), "· quarters", [time.strftime("%Y-%m-%d", time.gmtime(c)) for c in CUTS])
OUT["real_board"] = board_walk(A, CUTS[0], "REAL")
P(f"① done · {time.time() - T0:.0f}s")
cw, final, gem = combo_walk(A, "REAL", CUTS, t_end)
OUT["real_combo"], OUT["final"], OUT["gemini"] = cw, final, gem
P(f"② done · {time.time() - T0:.0f}s")
del A, COIN
COINS_ = prep(shuffled(cdb, 7))
A2 = arrays(COINS_)
OUT["shuf_board"] = board_walk(A2, CUTS[0], "SHUFFLED")
cw2, final2, gem2 = combo_walk(A2, "SHUFFLED", CUTS, t_end)
OUT["shuf_combo"] = cw2
json.dump(OUT, open("/tmp/holysig13.json", "w"), ensure_ascii=False, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
P(f"all done · {time.time() - T0:.0f}s")
