# 🔀 Holy ratio check 2 — the owner 27-11: «راح اعطيك مثال وسوي عليه فحص · Xrp مقابل eth · Xrp مقابل btc · Xrp مقابل xlm · Xrp مقابل سولانا ·
#   Xrp مقابل link · كل جهة ٢٠٠ دلار كيف راح يكون الربح»
#   The same rule as ci/ratio_check.py (a level every «step» of the ratio other ÷ XRP · one unit swapped through USDT per level · a close only with
#   profit after every fee · taker 0.10% + spread 0.02% on every leg · OKX's real lots and minimums) — start: 200$ of XRP + 200$ of the other coin.
#   Two ways of sharing the profit: «half» (half to each coin) and «xrp» (all of it to XRP — XRP plays the dollar's role).
#   New measures for the owner's condition «ما ينقص من العملتين»: share of the time each coin (and both) is at or above its start count · the
#   worst drop of each count · the end counts in coins and in % · the end value vs holding and vs a weekly 50/50 rebalance.
#   Fairness: on the 3 years of 1H, the same settings also run fresh on the first 2 years and on the last year alone.
#   REAL OKX public candles (no keys · no orders): 1H ~3 years · 15m ~1 year · 5m ~90 days.   python3 ci/ratio_check2.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R_ = tempfile.mkdtemp(prefix="ratio_")
shutil.copy(DASH, os.path.join(R_, "Holy_Dashboard.pyw"))
os.chdir(R_)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R_, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
T0 = time.time()
OUT = {"runs": []}


def P(*a):
    print("HOLYRATIO2", *a, flush=True)


DRY = os.environ.get("RATIO_DRY") == "1"
OTHERS = ["ETH-USDT", "XLM-USDT"] if DRY else ["ETH-USDT", "BTC-USDT", "XLM-USDT", "SOL-USDT", "LINK-USDT"]
FR = {"1H": (3600, 26280), "15m": (900, 35040), "5m": (300, 25920)}
if DRY:
    FR = {"1H": (3600, 3000)}


def fetch(sym, bar, n):
    """closed candles, oldest first, back page by page (100 each)"""
    if DRY:
        import random
        rnd = random.Random(hash(sym) % 1000)
        p, out, t = 1.0, [], int(time.time()) // FR[bar][0] * FR[bar][0] - n * FR[bar][0]
        base = random.Random(7)
        for i in range(n):
            r0 = base.gauss(0, 0.01)
            p *= math.exp(r0 * (1.4 if "XLM" in sym else 1.0) + rnd.gauss(0, 0.004))
            out.append([t + i * FR[bar][0], p, p, p, p, 1])
        return out
    rows = [c[:6] for c in m._fc_okx_rows(sym, bar, hist=False, limit=100) if c[6]]
    oldest = min((c[0] for c in rows), default=None)
    while oldest and len(rows) < n:
        pg = [c[:6] for c in m._fc_okx_rows(sym, bar, after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
        if not pg:
            break
        rows += pg
        oldest = min(c[0] for c in pg)
        time.sleep(0.12)
    return sorted({c[0]: c for c in rows}.values())[-n:]


def inst(sym):
    r = m._okx_pub(f"/api/v5/public/instruments?instType=SPOT&instId={sym}") if not DRY else None
    d = ((r or {}).get("data") or [{}])[0]
    return float(d.get("lotSz") or 0.000001), float(d.get("minSz") or 1.0)


def floor_lot(q, lot):
    return math.floor(q / lot + 1e-9) * lot


def ceil_lot(q, lot):
    return math.ceil(q / lot - 1e-9) * lot




def sim(T, PA, PB, step, frac, mx, fee, slip, la, lb, mina, minb, mode="half", cap=200.0):
    """A = XRP · B = the other · R = PB/PA · start: cap $ in each · a swap = frac × cap · mode «half» = profit half and half · «xrp» = all to XRP"""
    qa, qb, usd, fees = cap / PA[0], cap / PB[0], 0.0, 0.0
    qa0, qb0 = qa, qb
    ua, ub = frac * cap / PA[0], frac * cap / PB[0]
    R0, L = PB[0] / PA[0], 0
    up, dn = [], []                                         # up: sold B got A [qb_sold, qa_got] · dn: sold A got B [qa_sold, qb_got]
    cyc, pra, prb, mxu, mxd, skipped = 0, 0.0, 0.0, 0, 0, 0
    sa_dn = 1.0 if mode == "xrp" else 0.5                   # closing a «bought B» swap: the share of the profit that goes back to A
    sb_up = 0.0 if mode == "xrp" else 0.5                   # closing a «bought A» swap: the share of the profit that goes back to B
    ta = tb = tab = 0
    wa = wb = 0.0

    def sell_buy(q_sell, p_sell, lot_buy, p_buy):
        usd_in = q_sell * p_sell * (1 - slip)
        f1 = usd_in * fee
        usd_in -= f1
        y = floor_lot(usd_in / (p_buy * (1 + slip)), lot_buy)
        cost = y * p_buy * (1 + slip)
        f2 = y * fee
        return y - f2, usd_in - cost, f1 + f2 * p_buy

    for i in range(1, len(T)):
        pa, pb = PA[i], PB[i]
        R = pb / pa
        while R >= R0 * (1 + step) ** (L + 1):
            L += 1
            if dn:
                qa_sold, qb_got = dn[-1]
                qs = floor_lot(qb_got, lb)
                full, _d, _f = sell_buy(qs, pb, la, pa)
                prof = full - qa_sold
                if prof <= 0 or qs < minb:
                    skipped += 1
                    continue
                want = qa_sold + sa_dn * prof
                need_usd = want / (1 - fee) * pa * (1 + slip)
                qs2 = min(qs, ceil_lot(need_usd / ((1 - fee) * pb * (1 - slip)), lb))
                got, dust, f = sell_buy(qs2, pb, la, pa)
                qb -= qs2
                qa += got
                usd += dust
                fees += f
                pra += got - qa_sold
                prb += qb_got - qs2
                cyc += 1
                dn.pop()
            elif len(up) < mx:
                qs = floor_lot(min(ub, qb), lb)
                if qs < minb:
                    continue
                got, dust, f = sell_buy(qs, pb, la, pa)
                if got < mina:
                    continue
                qb -= qs
                qa += got
                usd += dust
                fees += f
                up.append([qs, got])
                mxu = max(mxu, len(up))
        while R <= R0 * (1 + step) ** (L - 1):
            L -= 1
            if up:
                qb_sold, qa_got = up[-1]
                qs = floor_lot(qa_got, la)
                full, _d, _f = sell_buy(qs, pa, lb, pb)
                prof = full - qb_sold
                if prof <= 0 or qs < mina:
                    skipped += 1
                    continue
                want = qb_sold + sb_up * prof
                need_usd = want / (1 - fee) * pb * (1 + slip)
                qs2 = min(qs, ceil_lot(need_usd / ((1 - fee) * pa * (1 - slip)), la))
                got, dust, f = sell_buy(qs2, pa, lb, pb)
                qa -= qs2
                qb += got
                usd += dust
                fees += f
                prb += got - qb_sold
                pra += qa_got - qs2
                cyc += 1
                up.pop()
            elif len(dn) < mx:
                qs = floor_lot(min(ua, qa), la)
                if qs < mina:
                    continue
                got, dust, f = sell_buy(qs, pa, lb, pb)
                if got < minb:
                    continue
                qa -= qs
                qb += got
                usd += dust
                fees += f
                dn.append([qs, got])
                mxd = max(mxd, len(dn))
        oka, okb = qa >= qa0 * (1 - 1e-9), qb >= qb0 * (1 - 1e-9)
        ta += oka
        tb += okb
        tab += oka and okb
        wa, wb = min(wa, qa / qa0 - 1), min(wb, qb / qb0 - 1)
    n = max(1, len(T) - 1)
    pa, pb = PA[-1], PB[-1]
    hold = qa0 * pa + qb0 * pb
    val = qa * pa + qb * pb + usd
    return {"qa0": qa0, "qb0": qb0, "qa": qa, "qb": qb, "usd": usd, "cyc": cyc, "pra": pra, "prb": prb, "open_up": len(up), "open_dn": len(dn),
            "mxu": mxu, "mxd": mxd, "hold": hold, "val": val, "fees": fees, "skipped": skipped,
            "t_a": ta / n, "t_b": tb / n, "t_ab": tab / n, "worst_a": wa, "worst_b": wb}


def rebal(PA, PB, every, fee, cap=1000.0):
    qa, qb = cap / PA[0], cap / PB[0]
    for i in range(every, len(PA), every):
        v = qa * PA[i] + qb * PB[i]
        ta = v / 2 / PA[i]
        d = (ta - qa) * PA[i]
        qa, qb = ta, (v / 2) / PB[i]
        v2 = qa * PA[i] + qb * PB[i] - abs(d) * fee * 2
        k = v2 / max(1e-12, qa * PA[i] + qb * PB[i])
        qa, qb = qa * k, qb * k
    return qa * PA[-1] + qb * PB[-1]


def stats(T, PA, PB, dt):
    ra = [math.log(PA[i] / PA[i - 1]) for i in range(1, len(PA))]
    rb = [math.log(PB[i] / PB[i - 1]) for i in range(1, len(PB))]
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((a - ma) * (b - mb) for a, b in zip(ra, rb)) / n
    va, vb = sum((a - ma) ** 2 for a in ra) / n, sum((b - mb) ** 2 for b in rb) / n
    R = [b / a for a, b in zip(PA, PB)]
    return {"corr": cov / math.sqrt(va * vb), "beta": cov / va, "vol_ratio": math.sqrt(vb / va), "r0": R[0], "r1": R[-1], "rmin": min(R), "rmax": max(R),
            "a_chg": PA[-1] / PA[0] - 1, "b_chg": PB[-1] / PB[0] - 1, "days": (T[-1] - T[0]) / 86400}



VAR = [(0.02, 0.10, 5), (0.03, 0.10, 5), (0.05, 0.10, 5), (0.03, 0.10, 2), (0.03, 0.05, 4)]
FEE, SLIP, CAP = 0.001, 0.0002, 200.0
CACHE = {}


def get(sym, bar, n):
    if (sym, bar) not in CACHE:
        CACHE[(sym, bar)] = fetch(sym, bar, n)
    return CACHE[(sym, bar)]


def line(tag, nA, nB, r, reb):
    da, db = r["qa"] - r["qa0"], r["qb"] - r["qb0"]
    return (f"{tag}: {nA} {r['qa0']:.6g} ⇒ {r['qa']:.6g} ({100 * da / r['qa0']:+.2f}%) · {nB} {r['qb0']:.6g} ⇒ {r['qb']:.6g} ({100 * db / r['qb0']:+.2f}%) · "
            f"realized {nA} {100 * r['pra'] / r['qa0']:+.2f}% {nB} {100 * r['prb'] / r['qb0']:+.2f}% · cycles {r['cyc']} · open ⬆{r['open_up']} ⬇{r['open_dn']} "
            f"(max ⬆{r['mxu']} ⬇{r['mxd']}) · time at/above start {nA} {100 * r['t_a']:.0f}% {nB} {100 * r['t_b']:.0f}% both {100 * r['t_ab']:.0f}% · "
            f"worst {nA} {100 * r['worst_a']:+.1f}% {nB} {100 * r['worst_b']:+.1f}% · $ left {r['usd']:.2f} · fees {r['fees']:.2f}$ · "
            f"value {r['val']:.2f}$ vs hold {r['hold']:.2f}$ ({100 * (r['val'] / r['hold'] - 1):+.2f}%) · weekly 50/50 {reb:.2f}$")


A = "XRP-USDT"
la, mina = inst(A)
P(f"lots {A}: lot {la} min {mina}")
for B in OTHERS:
    lb, minb = inst(B)
    nA, nB = A.split("-")[0], B.split("-")[0]
    P(f"pair {nA}/{nB} · lots {B}: lot {lb} min {minb}")
    for bar, (dt, n) in FR.items():
        t1 = time.time()
        ca, cb = get(A, bar, n), get(B, bar, n)
        tbm = {c[0]: c[4] for c in cb}
        rows = [(c[0], c[4], tbm[c[0]]) for c in ca if c[0] in tbm]
        if len(rows) < 500:
            P(f"{nA}/{nB} {bar}: too few candles ({len(rows)})")
            continue
        T, PA, PB = [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]
        st = stats(T, PA, PB, dt)
        P(f"== {nA}/{nB} {bar}: {len(rows)} candles · {st['days']:.0f} days ({time.strftime('%Y-%m-%d', time.gmtime(T[0]))} … "
          f"{time.strftime('%Y-%m-%d', time.gmtime(T[-1]))}) · {nA} {100 * st['a_chg']:+.1f}% · {nB} {100 * st['b_chg']:+.1f}% · "
          f"correlation {st['corr']:.2f} · {nB} moves ×{st['vol_ratio']:.2f} (beta {st['beta']:.2f}) · ratio {st['r0']:.6g} ⇒ {st['r1']:.6g} "
          f"(range {st['rmin']:.6g}–{st['rmax']:.6g}) · fetched in {time.time() - t1:.0f}s")
        parts = [("all", 0, len(T))]
        if bar == "1H" and not DRY:
            k = len(T) * 2 // 3
            parts += [("first 2 years", 0, k), ("last year", k, len(T))]
        for pn, i0, i1 in parts:
            t, pa_, pb_ = T[i0:i1], PA[i0:i1], PB[i0:i1]
            reb = rebal(pa_, pb_, max(1, int(7 * 86400 / dt)), FEE, cap=CAP)
            hold = CAP / pa_[0] * pa_[-1] + CAP / pb_[0] * pb_[-1]
            if pn != "all":
                P(f"-- {nA}/{nB} {bar} {pn}: {time.strftime('%Y-%m-%d', time.gmtime(t[0]))} … {time.strftime('%Y-%m-%d', time.gmtime(t[-1]))} · "
                  f"{nA} {100 * (pa_[-1] / pa_[0] - 1):+.1f}% · {nB} {100 * (pb_[-1] / pb_[0] - 1):+.1f}% · hold {hold:.2f}$ · weekly 50/50 {reb:.2f}$")
            for mode in ("half", "xrp"):
                for step, frac, mx in VAR:
                    if pn != "all" and (step, frac, mx) not in ((0.03, 0.10, 5), (0.03, 0.10, 2)):
                        continue
                    r = sim(t, pa_, pb_, step, frac, mx, FEE, SLIP, la, lb, mina, minb, mode=mode, cap=CAP)
                    OUT["runs"].append({"pair": f"{nA}/{nB}", "bar": bar, "part": pn, "mode": mode, "step": step, "frac": frac, "max": mx,
                                        **{k: round(v, 8) if isinstance(v, float) else v for k, v in r.items()}, "reb": round(reb, 4)})
                    tag = f"{nA}/{nB} {bar} [{pn}] profit {'half/half' if mode == 'half' else 'all to XRP'} · step {100 * step:.0f}% · swap {100 * frac:.0f}% · max {mx}"
                    P(line(tag, nA, nB, r, reb))
json.dump(OUT, open("/tmp/holyratio2.json", "w"), ensure_ascii=False)
P(f"DONE · {time.time() - T0:.0f}s")
