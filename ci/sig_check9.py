# 🔬 ninth pass — the owner (20-11): «سوي فحص جديد ابحث عن الثناىيات وفوق · انا ابحث على التركيبة النادرة هي». Every signal of ci/sig_check7.py
#   (the 36 systems · the old indicators · the market-wide readings — the same code, read from it) on REAL OKX prices, BOTH ways:
#   · BUY  (the price higher after) and SELL (lower after — the same systems on the mirrored price · the old ones' own SELL side)
#   · combinations of 2 · 3 · 4 · 5 · 6 signals fired within a few candles of each other on the same coin — searched step by step from the
#     best (a beam: the best pairs grow into triples, the best triples into fours …) on the first 60% of time only
#   · every chosen combination judged on the last 40% apart: how many cases · hit · against random · average move after
#   · 💎 the RARE ones on their own: few cases (≥ 6 while learning) but a very high hit — and what they did on the test
#   · judged after: 4-hour → 3 days (18 candles) · daily → 1 week (7 candles) · net after 0.2% fees
#   python3 ci/sig_check9.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG9
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "sig_check7.py"), encoding="utf-8").read()
_src = _src.split('P7("══ every system alone on the 4-hour and the daily')[0]
_src = _src.replace('print("HOLYSIG7"', 'print("HOLYSIG9"')
exec(compile(_src, "sig_check7_events", "exec"))


def P9(*a):
    print("HOLYSIG9", *a, flush=True)


HZN = {F4: 18, FD: 7}
LK = {F4: 3, FD: 2}
BEAM, TOPS = 60, 40
P9(f"events ready · {time.time() - T0:.0f}s")

# per coin · frame: the «active» sets (a signal fired within the last LK candles) · forward returns both ways · learn/test split
PRE = {}
for sym, (D4, E4, Dd, Ed, st) in COIN.items():
    for fr, D, E in ((F4, D4, E4), (FD, Dd, Ed)):
        h, lk = HZN[fr], LK[fr]
        act = {k: set(j for i in lst for j in range(i, min(D["n"], i + lk))) for k, lst in E.items() if lst}
        rl = {i: fwd(D["C"], i, h, 1) for i in range(210, D["n"])}
        rs = {i: fwd(D["C"], i, h, -1) for i in range(210, D["n"])}
        cut = next((i for i in range(D["n"]) if D["T"][i] >= st), D["n"])
        PRE[(sym, fr)] = (act, rl, rs, cut)
P9(f"prepared · {time.time() - T0:.0f}s")


def base(fr, side):
    l, t = [], []
    for sym in COIN:
        act, rl, rs, cut = PRE[(sym, fr)]
        r = rl if side > 0 else rs
        for i, x in r.items():
            if x is not None:
                (l if i < cut else t).append(x)
    return l, t


def evalc(fr, keys, side):
    """a combination (all its signals active together) — edge-triggered (the candle it starts) · (learn values, test values)"""
    l, t = [], []
    for sym in COIN:
        act, rl, rs, cut = PRE[(sym, fr)]
        sets = [act.get(k) for k in keys]
        if any(s is None for s in sets):
            continue
        inter = set.intersection(*sorted(sets, key=len))
        r = rl if side > 0 else rs
        last = -10 ** 9
        for i in sorted(inter):
            if i - 1 in inter or i - last < LK[fr]:
                continue
            last = i
            x = r.get(i)
            if x is not None:
                (l if i < cut else t).append(x)
    return l, t


def score(v, b):
    return (mean(v) - mean(b)) * math.sqrt(len(v)) if v else -9.0


REP = []
for fr in (FD, F4):
    for side in (1, -1):
        bl, bt = base(fr, side)
        lab = f"{'1D' if fr == FD else '4H'} {'BUY ' if side > 0 else 'SELL'}"
        singles = []
        for k in set(k for sym in COIN for k in PRE[(sym, fr)][0] if k[1] == side):
            l, t = evalc(fr, [k], side)
            if len(l) >= 6:
                singles.append((score(l, bl), k))
        singles.sort(reverse=True)
        top1 = [k for s, k in singles[:TOPS] if s > 0]
        P9(f"══ {lab} · judged after {HZN[fr]} candles · random: learn hit {hit(bl):.0f}% · test hit {hit(bt):.0f}% mean {pct(mean(bt))} · "
           f"{len(top1)} single signals beat random while learning ══")
        seen = set()
        allc = []
        cur = [(k,) for k in top1]
        for size in range(2, 7):
            cand = {}
            for c in cur:
                for k in top1:
                    if k in c:
                        continue
                    nc = tuple(sorted(c + (k,)))
                    if nc in seen:
                        continue
                    seen.add(nc)
                    l, t = evalc(fr, list(nc), side)
                    if len(l) >= 6 and mean(l) > mean(bl):
                        cand[nc] = (score(l, bl), l, t)
            best = sorted(cand.items(), key=lambda x: -x[1][0])[:BEAM]
            if not best:
                break
            cur = [c for c, _ in best]
            held = sum(1 for c, (s, l, t) in best[:20] if len(t) >= 3 and mean(t) > mean(bt))
            P9(f"{lab} · {size} together: {len(cand)} combinations beat random while learning · of the top 20: {held} still beat random on the test "
               f"(those with ≥ 3 test cases)")
            for c, (s, l, t) in best[:12]:
                ok_ = len(t) >= 3 and mean(t) > mean(bt)
                P9(f"{lab} {size}× " + " + ".join(k[0] for k in c) + f" · learn n {len(l)} hit {hit(l):.0f}% (rand {hit(bl):.0f}) · TEST n {len(t)} hit "
                   f"{hit(t):.0f}% (rand {hit(bt):.0f}) mean {pct(mean(t))} edge {pct(mean(t) - mean(bt))} {'✅' if ok_ else ('—' if len(t) < 3 else '❌')}")
            allc += [(fr, side, c, l, t) for c, (s, l, t) in cand.items()]
        # 💎 the rare ones: few cases while learning, a very high hit
        rare = [(hit(l), len(l), c, l, t) for f_, s_, c, l, t in allc if 6 <= len(l) <= 30 and hit(l) >= 75]
        rare.sort(key=lambda x: (-x[0], -x[1]))
        held = sum(1 for _, _, c, l, t in rare if len(t) >= 2 and hit(t) > hit(bt) and mean(t) > mean(bt))
        judged = sum(1 for _, _, c, l, t in rare if len(t) >= 2)
        P9(f"{lab} 💎 RARE (6–30 cases · hit ≥ 75% while learning): {len(rare)} found · judged on the test (≥ 2 cases): {judged} · still better "
           f"than random there: {held}")
        for hh, nn, c, l, t in rare[:15]:
            P9(f"{lab} 💎 {len(c)}× " + " + ".join(k[0] for k in c) + f" · learn {sum(1 for x in l if x > 0)}/{len(l)} ({hh:.0f}%) mean {pct(mean(l))} · "
               f"TEST {sum(1 for x in t if x > 0)}/{len(t)} ({hit(t):.0f}%) mean {pct(mean(t))}")
P9("names: " + " · ".join(f"{k}={v[0][:28]}" for k, v in sorted(SYS.items())))
P9(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
