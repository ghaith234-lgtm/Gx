# 🔬 eighth pass — the owner (20-11): «حتى التجميع وينبهني اذا سوق راح يصعد · وهم شي تعرف ممكن اشارتين او اكثر ممكن يعطن نتيجه افضل
#   اقصد المستوى الثاني ، والثالث النهائي» + the compass («اريد اعرف السوق يصعد او ينزل»). Every signal of ci/sig_check7.py (the 36
#   systems · the old indicators · the market-wide readings — the same code, read from it), on REAL OKX prices:
#   ① PAIRS and TRIPLES: two (three) BUY signals within a few candles of each other on the same coin — chosen on the first 60% of time
#     only (≥ 40 cases · better than random), then judged on the last 40% apart · how many of the chosen still beat random there
#     (if most fail, they were luck) · the same pair on the 4-hour confirmed by the daily (the «final»)
#   ② 🧲 accumulation / distribution judged after 1 · 2 · 4 weeks (its own time — it shows over weeks, not days)
#   ③ 🧭 the compass: the market's state (Bitcoin vs its 200-day average · share of the coins above their 50-day average) ⇒ what a BUY on
#     any coin gave over the next 3 days · 1 week · 2 weeks in each state · and the BUY signals inside each state
#   python3 ci/sig_check8.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG8
import itertools, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "sig_check7.py"), encoding="utf-8").read()
_src = _src.split('P7("══ every system alone on the 4-hour and the daily')[0]       # fetch · events · weights — up to the reports
_src = _src.replace('print("HOLYSIG7"', 'print("HOLYSIG8"')
exec(compile(_src, "sig_check7_events", "exec"))


def P8(*a):
    print("HOLYSIG8", *a, flush=True)


P8(f"events ready · {time.time() - T0:.0f}s")
LK = {F4: 3, FD: 2}          # two signals «together» = within this many candles of each other


def base_rets(fr, h, test):
    out = []
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        D = D4 if fr == F4 else Dd
        for i in range(210, D["n"]):
            if (D["T"][i] >= st) == test:
                x = fwd(D["C"], i, h, 1)
                if x is not None:
                    out.append(x)
    return out


def combo_events(D, E, keys, look):
    """the candles where every signal in keys fired within `look` candles (the last of them fires now) — BUY side"""
    lists = [E.get(k) or [] for k in keys]
    if any(not l for l in lists):
        return []
    sets = [set(l) for l in lists]
    out, lastc = [], -10 ** 9
    for i in sorted(set().union(*sets)):
        if all(any(j in s for j in range(i - look + 1, i + 1)) for s in sets) and i - lastc >= look:
            out.append(i); lastc = i
    return out


def judge_combo(fr, keys, h, test, look):
    v = []
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        D, E = (D4, E4) if fr == F4 else (Dd, Ed)
        for i in combo_events(D, E, keys, look):
            if (D["T"][i] >= st) == test:
                x = fwd(D["C"], i, h, 1)
                if x is not None:
                    v.append(x)
    return v


# ── ① pairs and triples (BUY) ──
for fr, h in ((FD, 3), (F4, 18)):
    bl, bt = base_rets(fr, h, False), base_rets(fr, h, True)
    ml, mt = mean(bl), mean(bt)
    single = {}
    for code in SYS:
        k = (code, 1)
        v = judge_combo(fr, [k], h, False, 1)
        if len(v) >= 40 and mean(v) > ml:
            single[k] = (mean(v) - ml, len(v))
    cand = sorted(single, key=lambda k: -single[k][0])[:28]          # the best single BUY signals while learning
    P8(f"══ {fr} · judged after {h} candles · {len(single)} single BUY signals beat random while learning · trying pairs of the top {len(cand)} ══")
    pairs = []
    for a, b in itertools.combinations(cand, 2):
        v = judge_combo(fr, [a, b], h, False, LK[fr])
        if len(v) >= 40 and mean(v) > ml:
            pairs.append((mean(v) - ml, len(v), (a, b)))
    pairs.sort(reverse=True)
    top = pairs[:20]
    held = 0
    for e, n, ks in top:
        vt = judge_combo(fr, list(ks), h, True, LK[fr])
        et = mean(vt) - mt if vt else 0.0
        held += 1 if vt and len(vt) >= 15 and et > 0 else 0
        P8(f"{fr} PAIR {' + '.join(k[0] for k in ks):18s} {' + '.join(SYS[k[0]][0][:22] for k in ks)[:48]:48s} learn n {n} edge {pct(e)} → "
           f"TEST n {len(vt)} hit {hit(vt):.0f}% (rand {hit(bt):.0f}) edge {pct(et)} {'✅' if vt and len(vt) >= 15 and et > 0 else '❌'}")
    P8(f"{fr} PAIRS: {held} of the top {len(top)} (chosen on the learning part) still beat random on the test")
    tri = []
    for e, n, (a, b) in pairs[:12]:
        for c in cand:
            if c in (a, b):
                continue
            v = judge_combo(fr, [a, b, c], h, False, LK[fr])
            if len(v) >= 30 and mean(v) > ml:
                tri.append((mean(v) - ml, len(v), tuple(sorted((a, b, c)))))
    tri = sorted(set(tri), reverse=True)[:15]
    held = 0
    for e, n, ks in tri:
        vt = judge_combo(fr, list(ks), h, True, LK[fr])
        et = mean(vt) - mt if vt else 0.0
        held += 1 if vt and len(vt) >= 10 and et > 0 else 0
        P8(f"{fr} TRIPLE {' + '.join(k[0] for k in ks):24s} learn n {n} edge {pct(e)} → TEST n {len(vt)} hit {hit(vt):.0f}% (rand {hit(bt):.0f}) "
           f"edge {pct(et)} {'✅' if vt and len(vt) >= 10 and et > 0 else '❌'}")
    P8(f"{fr} TRIPLES: {held} of the top {len(tri)} still beat random on the test")
    if fr == F4:
        continue
    # the «final»: a daily pair also confirmed on the 4-hour (any of its two signals fired on the 4-hour within 3 candles before the daily close)
    held = 0
    for e, n, ks in top[:10]:
        for test in (False, True):
            v = []
            for sym, (D4, E4, Dd, Ed, st) in COIN.items():
                for i in combo_events(Dd, Ed, list(ks), LK[FD]):
                    if (Dd["T"][i] >= st) != test:
                        continue
                    tcl = Dd["T"][i] + 86400
                    j4 = bisect.bisect_right(D4["T"], tcl - 14400) - 1
                    if j4 < 0:
                        continue
                    if any(any(j4 - 2 <= x <= j4 for x in (E4.get(k) or [])) for k in ks):
                        x = fwd(Dd["C"], i, 3, 1)
                        if x is not None:
                            v.append(x)
            if not test:
                el = mean(v) - ml if v else 0.0; nl = len(v)
            else:
                et = mean(v) - mt if v else 0.0
                held += 1 if len(v) >= 10 and et > 0 else 0
                P8(f"FINAL daily pair {' + '.join(k[0] for k in ks):18s} + the 4-hour agrees: learn n {nl} edge {pct(el)} → TEST n {len(v)} hit {hit(v):.0f}% "
                   f"edge {pct(et)} {'✅' if len(v) >= 10 and et > 0 else '❌'}")
    P8(f"FINAL: {held} of 10 still beat random on the test")

# ── ② 🧲 accumulation / distribution over weeks ──
P8("══ 🧲 accumulation / distribution — judged after 1 · 2 · 4 weeks (daily · all of the time) ══")
for k in (("X-ad", 1), ("X-ad", -1), ("X-adt", 1), ("X-adt", -1)):
    seg = []
    for h in (7, 14, 28):
        for test in (False, True):
            v, b = [], []
            for sym, (D4, E4, Dd, Ed, st) in COIN.items():
                for i in (Ed.get(k) or []):
                    if (Dd["T"][i] >= st) == test:
                        x = fwd(Dd["C"], i, h, k[1])
                        if x is not None:
                            v.append(x)
                for i in range(210, Dd["n"]):
                    if (Dd["T"][i] >= st) == test:
                        x = fwd(Dd["C"], i, h, k[1])
                        if x is not None:
                            b.append(x)
            seg.append(f"{h // 7}w {'test' if test else 'learn'} n {len(v)} hit {hit(v):.0f}% (rand {hit(b):.0f}) edge {pct(mean(v) - mean(b))}")
    P8(f"{k[0]} {'BUY ' if k[1] > 0 else 'SELL'} ({SYS[k[0]][0]}): " + " · ".join(seg))

# ── ③ 🧭 the compass ──
P8("══ 🧭 the compass: Bitcoin vs its 200-day average · share of the coins above their 50-day average (daily) ══")
btc = COIN.get("BTC-USDT")
if btc:
    Dd = btc[2]
    b200 = sma(Dd["C"], 200)
    BT = {Dd["T"][i]: (Dd["C"][i] > b200[i]) for i in range(Dd["n"]) if b200[i] is not None}
    ABOVE = {}
    for sym, (D4, E4, Dc, Ec, st) in COIN.items():
        s50 = sma(Dc["C"], 50)
        for i in range(Dc["n"]):
            if s50[i] is not None:
                ABOVE.setdefault(Dc["T"][i], []).append(Dc["C"][i] > s50[i])
    def state(t):
        if t not in BT or len(ABOVE.get(t) or []) < 10:
            return None
        sh = sum(ABOVE[t]) / len(ABOVE[t])
        return "up" if BT[t] and sh >= 0.6 else "down" if (not BT[t]) and sh <= 0.4 else "flat"
    for h in (3, 7, 14):
        res = {"up": [], "flat": [], "down": []}
        sigs = {"up": [], "flat": [], "down": []}
        days = {"up": 0, "flat": 0, "down": 0}
        for sym, (D4, E4, Dc, Ec, st) in COIN.items():
            buyset = set(i for (code, side), lst in Ec.items() if side > 0 and code in ("35", "09", "27", "17", "38", "O-verdict", "F-vote", "X-adt") for i in lst)
            for i in range(210, Dc["n"]):
                s = state(Dc["T"][i])
                if not s:
                    continue
                x = fwd(Dc["C"], i, h, 1)
                if x is None:
                    continue
                res[s].append(x)
                if sym == "BTC-USDT":
                    days[s] += 1
                if i in buyset:
                    sigs[s].append(x)
        P8(f"after {h} days: " + " ‖ ".join(f"{s.upper()} ({days[s]} days): any buy hit {hit(res[s]):.0f}% mean {pct(mean(res[s]))} · "
                                          f"with a good BUY signal n {len(sigs[s])} hit {hit(sigs[s]):.0f}% mean {pct(mean(sigs[s]))}" for s in ("up", "flat", "down")))
    # how long a state lasts and whether its change is a warning
    seq = [(t, state(t)) for t in sorted(BT)]
    seq = [(t, s) for t, s in seq if s]
    runs, cur, n0 = [], None, 0
    for t, s in seq:
        if s != cur:
            if cur:
                runs.append((cur, n0))
            cur, n0 = s, 0
        n0 += 1
    P8("state runs (days): " + " · ".join(f"{s}: median {med([n for k, n in runs if k == s]) if [n for k, n in runs if k == s] else 0} "
                                          f"(n {len([1 for k, n in runs if k == s])})" for s in ("up", "flat", "down")))
    P8(f"today: {seq[-1][1] if seq else '—'} (since {sum(1 for _ in itertools.takewhile(lambda x: x[1] == seq[-1][1], reversed(seq))) if seq else 0} days)")
P8(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
