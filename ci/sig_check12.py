# 🔬 twelfth pass — the owner (21-11): «اريدك اتسوي فحص قوي اتقوي التنبؤ … الفحص لتنبؤ اختبره على البيانات القديمة».
#   THE ANALYST LIVES IN THE PAST (walk-forward): the dashboard's own code builds its proven groups (v3.36.69+ _sg_search) from the history
#   BEFORE a date only, then runs on the next 3 months it never saw exactly as it runs live (a group fires when all its signals agree and
#   none of the other side is on · judged by its own target/stop) — moved forward 3 months at a time, 4 times · 40 coins · REAL OKX prices.
#   Every message is counted once (one coin · side · frame per day for «غداً» / per 3 days for the month), at the owner's thresholds.
#   What may make the prediction stronger — each on the same unseen months, each beside «random» and beside SHUFFLED prices (luck):
#   ① BASE · ② the market's state (buy only when the compass is up · sell only when it is down) · ③ the two frames agree (a 4-hour fire
#   only with the daily trend on its side) · ④ the target/stop distance ×0.75 · ×1 · ×1.5 · ⑤ the 4-hour horizon (judged after 4 hours)
#   · ⑥ the same walk on shuffled prices (what luck alone gives)
#   python3 ci/sig_check12.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYSIG12
import bisect, importlib.machinery, importlib.util, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig12_")
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
    print("HOLYSIG12", *a, flush=True)


EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
THRS = (50, 55, 60, 65)
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· horizons", m.SG_HZ)
cdb = {}
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


def shuffled(db_, seed):
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


def prep(db_):
    btc = {int(r[0]): float(r[4]) for r in ((db_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []}
    COIN = {}
    for sym in COINS:
        rd = ((db_.get("c") or {}).get(sym) or {}).get("d") or []
        r4 = ((db_.get("c4") or {}).get(sym) or {}).get("d") or []
        if len(r4) < m.SG_MIN["4H"] or len(rd) < m.SG_MIN["1D"]:
            continue
        ctx = m._sg_ctx(sym, rd, db, mkt, fng, btc)
        D4, E4 = m._sg_events(r4, False, ctx)
        Dd, Ed = m._sg_events(rd, True, ctx)
        COIN[sym] = (D4, E4, Dd, Ed, D4["T"][int(D4["n"] * 0.6)])
    m._sg_crash({s: (v[0], v[1]) for s, v in COIN.items()})
    return COIN


def cut(COIN, t_cut):
    """the history before t_cut only (every signal is computed from the past, so a cut series is what the dashboard saw that day)"""
    out = {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        parts = []
        for D, E in ((D4, E4), (Dd, Ed)):
            k = bisect.bisect_left(D["T"], t_cut)
            D2 = {kk: (vv[:k] if isinstance(vv, list) else vv) for kk, vv in D.items()}
            D2["n"] = k
            E2 = {key: [i for i in lst if i < k] for key, lst in E.items()}
            parts.append((D2, {a: b for a, b in E2.items() if b}))
        if parts[0][0]["n"] >= m.SG_MIN["4H"] and parts[1][0]["n"] >= m.SG_MIN["1D"]:
            out[sym] = (parts[0][0], parts[0][1], parts[1][0], parts[1][1], st)
    return out


def compass_map(COIN):
    btc = COIN.get("BTC-USDT")
    if not btc:
        return {}
    seq = m._sg_compass_states(btc[2], [v[2] for v in COIN.values()])
    return {t: s for t, raw, s, *_ in seq}


def daily_trend(COIN):
    """per coin: day → +1 if the daily close is above its 50-day average, −1 below (the frame-agreement filter)"""
    out = {}
    for sym, v in COIN.items():
        Dd = v[2]
        C = Dd["C"]
        d = {}
        s = 0.0
        for i in range(Dd["n"]):
            s += C[i]
            if i >= 50:
                s -= C[i - 50]
            if i >= 49:
                d[Dd["T"][i]] = 1 if C[i] > s / 50.0 else -1
        out[sym] = (sorted(d), d)
    return out


def is_mkt(e):
    return len(e["k"]) == 1 and e["k"][0].startswith(("W-", "M-"))


def simulate(COIN, cat, t0, t1, comp, trend, q, ks=(1.0,)):
    """the analyst running live over [t0, t1): a group fires on the candle its signals all become active together (none of the other side
    on · a market reading alone without that filter) · it passes as the dashboard passes it (proven in the 4 periods · ≥ 15 cases · its
    accuracy ≥ the owner's % · better than random) · one message per coin · side · frame per day («غداً») / per 3 days (the month) ·
    a market reading alone (🌊 😨 🗞️) is ONE message for the whole market (judged by the average coin) · random entries on the same candles"""
    ents = {"4H": [], "1D": []}
    base = cat.get("base") or {}
    for e in cat["e"]:
        b = base.get(f"{e['f']}|{e['s']}") or {}
        if e.get("c4") and e["nt"] and (e.get("nd") or 0 if is_mkt(e) else e["nt"]) >= 15:
            acc = e["wt"] / e["nt"] * 100.0
            ents[e["f"]].append((e, acc, acc > float(b.get("ht") or 0) and e["mt"] > float(b.get("mt") or 0), is_mkt(e), int(e["nt"]), int(e.get("nd") or 0)))
    msgs, rnd, mk = [], {}, {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        tk, td = trend.get(sym, ([], {}))
        for fr, D, E in (("4H", D4, E4), ("1D", Dd, Ed)):
            h, lk = m.SG_HZ[fr], m.SG_LK[fr]
            T = D["T"]
            i0, i1 = bisect.bisect_left(T, t0), bisect.bisect_left(T, t1)
            if i1 - i0 < 2:
                continue
            A = [set() for _ in range(i1 - i0 + 1)]
            for (code, side), lst in E.items():
                for i in lst:
                    for j in range(max(i, i0 - 1), min(i + lk, i1)):
                        A[j - i0 + 1].add(f"{code}:{side}")
            opp = [(any(a.endswith(":-1") and not a.startswith("W-crash:") for a in s_), any(a.endswith(":1") and not a.startswith("W-crash:") for a in s_)) for s_ in A]
            sg = m._sg_sig(D["C"], h)
            last = {}
            gap = 86400 if fr == "4H" else 3 * 86400
            for i in range(i0, i1):
                if i + h >= D["n"]:
                    break
                for side in (1, -1):
                    for k in ks:
                        x = m._sg_out(D["H"], D["L"], D["C"], i, h, side, sg[i] * k)
                        if x is not None:
                            rnd.setdefault((fr, side, k, q), []).append(x)
                a1, a0 = A[i - i0 + 1], A[i - i0]
                o1, o0 = opp[i - i0 + 1], opp[i - i0]
                fired = {}
                for e, acc, brnd, mw, nt_, nd_ in ents[fr]:
                    keys = [f"{kk}:{e['s']}" for kk in e["k"]]
                    if not all(kk in a1 for kk in keys) or (not mw and (o1[0] if e["s"] > 0 else o1[1])):
                        continue
                    if all(kk in a0 for kk in keys) and (mw or not (o0[0] if e["s"] > 0 else o0[1])):
                        continue
                    key = (e["s"], mw)
                    if acc > fired.get(key, (-1, 0))[0]:
                        fired[key] = (acc, brnd, nt_, nd_)
                day = T[i] // 86400 * 86400
                cs = comp.get(day) or comp.get(day - 86400)
                j = bisect.bisect_right(tk, T[i] - 86400) - 1
                tr = td.get(tk[j]) if j >= 0 else None
                for (side, mw), (acc, brnd, nt_, nd_) in fired.items():
                    xs = {k: m._sg_out(D["H"], D["L"], D["C"], i, h, side, sg[i] * k) for k in ks}
                    if mw:
                        mk.setdefault((fr, side, T[i]), {"acc": acc, "rnd": brnd, "cs": cs, "xs": []})["xs"].append(xs)
                        continue
                    kk = (sym, fr, side)
                    if T[i] - last.get(kk, -10 ** 12) < gap:
                        continue
                    last[kk] = T[i]
                    msgs.append({"fr": fr, "side": side, "acc": acc, "rnd": brnd, "cs": cs, "tr": tr, "x": xs, "t": T[i], "sym": sym, "q": q, "mw": False,
                                 "n": nt_, "nd": nd_})
    lastm = {}
    for (fr, side, t), v in sorted(mk.items(), key=lambda z: z[0][2]):
        gap = 86400 if fr == "4H" else 3 * 86400
        if t - lastm.get((fr, side), -10 ** 12) < gap or len(v["xs"]) < 5:
            continue
        lastm[(fr, side)] = t
        xs = {k: mean([x[k] for x in v["xs"] if x.get(k) is not None]) if any(x.get(k) is not None for x in v["xs"]) else None for k in ks}
        msgs.append({"fr": fr, "side": side, "acc": v["acc"], "rnd": v["rnd"], "cs": v["cs"], "tr": None, "x": xs, "t": t, "sym": "*", "q": q, "mw": True})
    return msgs, rnd


def hit(v):
    return sum(1 for x in v if x > 0) / len(v) * 100.0 if v else 0.0


def mean(v):
    return sum(v) / len(v) if v else 0.0


def zsc(v, r):
    """how far the messages' hit rate is above random's, in standard errors (≥ 2 ⇒ unlikely to be luck)"""
    if not v or not r:
        return 0.0
    p = hit(r) / 100.0
    se = math.sqrt(max(p * (1 - p), 1e-6) / len(v))
    return (hit(v) / 100.0 - p) / se


def walk(COIN_full, label, ks=(1.0,), cuts=None):
    """4 windows of 3 months · groups rebuilt before each from the past only · all messages gathered"""
    comp, trend = compass_map(COIN_full), daily_trend(COIN_full)
    allm, allr = [], {}
    for q, c0 in enumerate(cuts):
        t1 = time.time()
        part = cut(COIN_full, c0)
        if len(part) < 5:
            P(f"{label} · window from {time.strftime('%Y-%m-%d', time.gmtime(c0))}: only {len(part)} coins have enough history before it — skipped")
            continue
        cat = m._sg_search(part)
        nc4 = sum(1 for e in cat["e"] if e.get("c4"))
        msgs, rnd = simulate(COIN_full, cat, c0, c0 + 91 * 86400, comp, trend, q, ks)
        allm += msgs
        for k, v in rnd.items():
            allr.setdefault(k, []).extend(v)
        P(f"{label} · window {q + 1} from {time.strftime('%Y-%m-%d', time.gmtime(c0))}: {len(part)} coins · {nc4} proven groups built from the past · "
          f"{len(msgs)} messages in the next 3 months · {time.time() - t1:.0f}s")
    return allm, allr


def rget(rnd, fr, side, k, q=None):
    return [x for (f, s, kk, qq), v in rnd.items() if f == fr and s == side and kk == k and (q is None or qq == q) for x in v]


def report(label, msgs, rnd, ks=(1.0,), frs=("4H", "1D")):
    weeks = 4 * 13
    for fr in frs:
        nm = ("tomorrow" if m.SG_HZ["4H"] == 6 else f"{m.SG_HZ['4H'] * 4} hours") if fr == "4H" else "next month"
        for side in (1, -1):
            sd = "BUY " if side > 0 else "SELL"
            r = rget(rnd, fr, side, 1.0)
            for thr in THRS:
                mm = [x for x in msgs if x["fr"] == fr and x["side"] == side and x["acc"] >= thr and x["rnd"] and not x["mw"]]
                v = [x["x"][1.0] for x in mm if x["x"].get(1.0) is not None]
                want = "up" if side > 0 else "down"
                rg = [x["x"][1.0] for x in mm if x["x"].get(1.0) is not None and x["cs"] == want]
                tf = [x["x"][1.0] for x in mm if x["x"].get(1.0) is not None and x["tr"] == side]
                both = [x["x"][1.0] for x in mm if x["x"].get(1.0) is not None and x["cs"] == want and x["tr"] == side]
                days = len({x["t"] // 86400 for x in mm})
                wins = []
                for q in range(4):
                    vq = [x["x"][1.0] for x in mm if x["q"] == q and x["x"].get(1.0) is not None]
                    rq = rget(rnd, fr, side, 1.0, q)
                    wins.append(f"{hit(vq):.0f}/{hit(rq):.0f}" if vq else "—")
                beat = sum(1 for q in range(4) if [x for x in mm if x["q"] == q] and
                           hit([x["x"][1.0] for x in mm if x["q"] == q and x["x"].get(1.0) is not None]) > hit(rget(rnd, fr, side, 1.0, q)))
                line = (f"{label} {nm} {sd} ≥{thr}%: ① {hit(v):.0f}% right n{len(v)} on {days} days ({len(v) / weeks:.1f}/week) avg {mean(v) * 100:+.2f}% · "
                        f"random {hit(r):.0f}% {mean(r) * 100:+.2f}% · z {zsc(v, r):+.1f} · windows {' '.join(wins)} (beat random in {beat}/4) · "
                        f"② market state {hit(rg):.0f}% n{len(rg)} z {zsc(rg, r):+.1f} · ③ frames agree {hit(tf):.0f}% n{len(tf)} z {zsc(tf, r):+.1f} · "
                        f"②+③ {hit(both):.0f}% n{len(both)} z {zsc(both, r):+.1f}")
                if len(ks) > 1:
                    line += " · ④ target/stop " + " ".join(
                        f"×{k}: {hit([x['x'][k] for x in mm if x['x'].get(k) is not None]):.0f}%/{mean([x['x'][k] for x in mm if x['x'].get(k) is not None]) * 100:+.2f}%"
                        f" (rnd {hit(rget(rnd, fr, side, k)):.0f}%/{mean(rget(rnd, fr, side, k)) * 100:+.2f}%)" for k in ks)
                P(line)
            for thr in (50, 60):
                mw = [x for x in msgs if x["fr"] == fr and x["side"] == side and x["acc"] >= thr and x["rnd"] and x["mw"]]
                v = [x["x"][1.0] for x in mw if x["x"].get(1.0) is not None]
                if mw:
                    P(f"{label} {nm} {sd} ≥{thr}% MARKET READINGS (one message for the whole market · the average coin): {hit(v):.0f}% right n{len(v)} "
                      f"avg {mean(v) * 100:+.2f}% · random {hit(r):.0f}% {mean(r) * 100:+.2f}%")


def report_filters(label, msgs, rnd):
    """🔢 the owner (21-11): «اكو فلترين عددي ونسبي — انصحني ياهو الي يعطي نتيجة افضل»: the same unseen months, each message kept only if
    its group had ≥ N cases (and ≥ N different days) in the history it was built on and its accuracy ≥ the % — which pair is truest?"""
    for fr in ("4H", "1D"):
        nm = "tomorrow" if fr == "4H" else "next month"
        for side in (1, -1):
            r = rget(rnd, fr, side, 1.0)
            for by in ("cases", "days"):
                for mn in (15, 30, 50, 100):
                    for thr in (50, 55, 60, 65):
                        mm = [x for x in msgs if x["fr"] == fr and x["side"] == side and not x["mw"] and x["rnd"] and x["acc"] >= thr
                              and (x["n"] if by == "cases" else x["nd"]) >= mn and x["x"].get(1.0) is not None]
                        v = [x["x"][1.0] for x in mm]
                        beat = sum(1 for q in range(4) if [x for x in mm if x["q"] == q] and hit([x["x"][1.0] for x in mm if x["q"] == q]) > hit(rget(rnd, fr, side, 1.0, q)))
                        P(f"{label} FILTER {nm} {'BUY ' if side > 0 else 'SELL'} ≥{mn} {by} · ≥{thr}%: {hit(v):.0f}% right n{len(v)} ({len(v) / 52:.1f}/week) avg "
                          f"{mean(v) * 100:+.2f}% · random {hit(r):.0f}% · z {zsc(v, r):+.1f} · beat random in {beat}/4 windows")


def causal(COIN_raw_db, syms, cuts):
    """⓪ the signals use the past only: events computed on the history cut at a date = the same events in the full history before it"""
    btc = {int(r[0]): float(r[4]) for r in ((COIN_raw_db.get("c") or {}).get("BTC-USDT") or {}).get("d") or []}
    bad, n = {}, 0
    for sym in syms:
        rd = ((COIN_raw_db.get("c") or {}).get(sym) or {}).get("d") or []
        r4 = ((COIN_raw_db.get("c4") or {}).get(sym) or {}).get("d") or []
        if not rd or not r4:
            continue
        ctx = m._sg_ctx(sym, rd, db, mkt, fng, btc)
        full = {False: m._sg_events(r4, False, ctx)[1], True: m._sg_events(rd, True, ctx)[1]}
        for c0 in cuts:
            rdc = [r for r in rd if int(r[0]) < c0]
            r4c = [r for r in r4 if int(r[0]) < c0]
            ctxc = m._sg_ctx(sym, rdc, db, mkt, fng, btc)
            for daily, rows in ((False, r4c), (True, rdc)):
                k = len(rows)
                E2 = m._sg_events(rows, daily, ctxc)[1]
                for key in set(full[daily]) | set(E2):
                    n += 1
                    a = [i for i in full[daily].get(key, []) if i < k - 1]
                    b = [i for i in E2.get(key, []) if i < k - 1]
                    if a != b:
                        bad.setdefault(("1D" if daily else "4H", key[0]), 0)
                        bad[("1D" if daily else "4H", key[0])] += 1
    return bad, n


COIN = prep(cdb)
btc4 = COIN["BTC-USDT"][0]["T"]
t_end = btc4[-1] - 91 * 86400 // 13           # the last week's outcomes are not known yet
CUTS = [t_end - (4 - q) * 91 * 86400 for q in range(4)]
P(f"events ready · {len(COIN)} coins · windows from " + " · ".join(time.strftime("%Y-%m-%d", time.gmtime(c)) for c in CUTS) + f" · {time.time() - T0:.0f}s")
bad, nchk = causal(cdb, ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LINK-USDT"], CUTS[1:3])
P(f"⓪ the signals look at the past only: {nchk} signal lists compared (cut history vs full history before the cut) · "
  + ("all identical ✓" if not bad else "DIFFERENT: " + " · ".join(f"{fr} {c} ×{v}" for (fr, c), v in sorted(bad.items()))))
KS = (0.75, 1.0, 1.5)
msgs, rnd = walk(COIN, "REAL", KS, CUTS)
report("REAL", msgs, rnd, KS)
report_filters("REAL", msgs, rnd)
P(f"① – ④ done · {time.time() - T0:.0f}s")

# ⑤ the 4-hour horizon: the same walk with the 4-hour frame judged after ONE candle
m.SG_HZ["4H"] = 1
msgs4, rnd4 = walk(COIN, "4H-HORIZON", (1.0,), CUTS)
report("4H-HORIZON", msgs4, rnd4, (1.0,), ("4H",))
m.SG_HZ["4H"] = 6
P(f"⑤ done · {time.time() - T0:.0f}s")

# ⑥ luck: the same walk on shuffled prices
COINS_ = prep(shuffled(cdb, 7))
msgsS, rndS = walk(COINS_, "SHUFFLED", (1.0,), CUTS)
report("SHUFFLED", msgsS, rndS, (1.0,))
report_filters("SHUFFLED", msgsS, rndS)
P(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
