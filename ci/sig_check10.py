# 🔬 tenth pass — the owner (20-11): «افحص» — the geopolitical-risk (GPR) and policy-uncertainty (EPU) readings looked too good in check 9
#   (sell combinations up to 29/29) but those indexes are PUBLISHED LATE: a back-test that reads the value of day t on day t sees it before
#   anyone could. Here every macro reading (GPR · EPU · VIX · the dollar · US 10-year · news tone · fear & greed) is moved later by
#   0 · 1 · 3 · 7 · 14 days (the value of day t usable only from day t + lag) and judged again — alone and in the pairs check 9 found
#   (BUY and SELL · daily → 1 week · 4-hour → 3 days · the first 60% learn / the last 40% test · net after fees · vs random)
#   python3 ci/sig_check10.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG10
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "sig_check7.py"), encoding="utf-8").read()
_src = _src.split('P7("══ every system alone on the 4-hour and the daily')[0]
_src = _src.replace('print("HOLYSIG7"', 'print("HOLYSIG10"')
exec(compile(_src, "sig_check7_events", "exec"))


def PX10(*a):
    print("HOLYSIG10", *a, flush=True)


HZN = {F4: 18, FD: 7}
LK = {F4: 3, FD: 2}
PAIRS = [("20", "M-gpr"), ("F-nw", "M-gpr"), ("30", "M-gpr"), ("M-gpr", "X-rs"), ("F-vote", "M-gpr"), ("M-gpr", "O-verdict"), ("23", "M-gpr"),
         ("M-gpr", "X-adt"), ("35", "M-epu"), ("29", "M-epu"), ("M-epu", "O-vp"), ("32", "M-epu"), ("M-dxy", "M-gpr")]
MK = [k for k in MKT]
PX10(f"macro series: {', '.join(f'{k} {len(MKT[k][1])}' for k in MK)}")


_MC = {}


def macro_events(D, dx, lag):
    ck = (id(D), lag)
    if ck in _MC:
        return _MC[ck]
    ev = {}
    for k, (ks, vs) in MKT.items():
        sf = _FNG if k == "fng" else (lambda vs_, j, k=k: m._mac_sig(k, vs_, j)[0])
        ev.update(series_events(D, dx, "M-" + k, [x + lag * 86400 for x in ks], vs, sf))
    _MC[ck] = ev
    return ev


def judge(fr, keys, side, lag):
    l, t, bl, bt = [], [], [], []
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        D, E = (D4, E4) if fr == F4 else (Dd, Ed)
        dx = 14400 if fr == F4 else 86400
        E2 = dict(E)
        E2.update(macro_events(D, dx, lag))
        lk, h = LK[fr], HZN[fr]
        sets = []
        for k in keys:
            lst = E2.get((k, side)) or []
            sets.append(set(j for i in lst for j in range(i, min(D["n"], i + lk))))
        cut = next((i for i in range(D["n"]) if D["T"][i] >= st), D["n"])
        for i in range(210, D["n"]):
            x = fwd(D["C"], i, h, side)
            if x is not None:
                (bl if i < cut else bt).append(x)
        if any(not s for s in sets):
            continue
        inter = set.intersection(*sets)
        last = -10 ** 9
        for i in sorted(inter):
            if i - 1 in inter or i - last < lk:
                continue
            last = i
            x = fwd(D["C"], i, h, side)
            if x is not None:
                (l if i < cut else t).append(x)
    return l, t, bl, bt


for fr in (FD, F4):
    for side in (1, -1):
        lab = f"{'1D' if fr == FD else '4H'} {'BUY ' if side > 0 else 'SELL'}"
        PX10(f"══ {lab} ══")
        for keys in [(f"M-{k}",) for k in MK] + PAIRS:
            seg = []
            for lag in (0, 1, 3, 7, 14):
                l, t, bl, bt = judge(fr, list(keys), side, lag)
                seg.append(f"lag {lag:2d}d: learn {hit(l):.0f}% n {len(l)} · test {hit(t):.0f}% n {len(t)} (rand {hit(bt):.0f}) edge {pct(mean(t) - mean(bt)) if t else '—'}")
            PX10(f"{lab} {' + '.join(keys):18s} " + " ‖ ".join(seg))
PX10(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
