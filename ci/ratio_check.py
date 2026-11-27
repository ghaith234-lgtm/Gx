# 🔀 Holy ratio check — a bot that trades BETWEEN two coins through the dollar (the owner 27-11: «بوت تداول بين العملات … xrp و xlm … العملتين
#   يزداد كميتهم ويكون الوسيط بينهم الدولار محسوب جميع العمولات … كلما يزيد الفرق يتبادل … الربح يعطي للعملتين … سوي فحص … واخرج لي بالجدول
#   كم الارباح للعملتين»)
#   The rule (exactly the example given to the owner): the ratio R = XLM price ÷ XRP price · a level every «step» from the start ·
#   R up one level ⇒ (close an open «XLM bought» swap with profit, else) sell one unit of XLM for XRP through USDT · R down one level ⇒ the mirror ·
#   a close happens only when it gives back MORE than was sold (after every fee) and the profit is split half and half between the two coins ·
#   at most «max_open» swaps open on each side · every trade pays the taker fee + a spread slip · sizes rounded to OKX's lot and refused under
#   its minimum · the dollar left over from rounding is kept and counted.
#   REAL OKX public candles (no keys · no orders): 1H for ~3 years · 15m for ~1 year · 5m for the last ~90 days · the instruments' real lots.
#   For every step / size / max: XRP gained · XLM gained (count and %) · completed cycles · open swaps left · the end value vs simply holding
#   (and vs a weekly 50/50 rebalance) · the fees paid. Also the two coins' relation (correlation · XLM's beta vs XRP · where the ratio went).
#   Results: lines HOLYRATIO + /tmp/holyratio.json.   python3 ci/ratio_check.py Holy_Dashboard.pyw
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
    print("HOLYRATIO", *a, flush=True)


DRY = os.environ.get("RATIO_DRY") == "1"
PAIRS = [("XRP-USDT", "XLM-USDT")] + ([] if DRY else [("XRP-USDT", "ADA-USDT"), ("XLM-USDT", "HBAR-USDT")])
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


def sim(T, PA, PB, step, frac, mx, fee, slip, la, lb, mina, minb, split=0.5, cap=1000.0):
    """A = the first coin (XRP) · B = the second (XLM) · R = PB/PA · start: cap $ in each · a swap = frac × cap of value"""
    qa, qb, usd, fees = cap / PA[0], cap / PB[0], 0.0, 0.0
    qa0, qb0 = qa, qb
    ua, ub = frac * cap / PA[0], frac * cap / PB[0]
    R0, L = PB[0] / PA[0], 0
    up, dn = [], []                                         # up: sold B got A [qb_sold, qa_got] · dn: sold A got B [qa_sold, qb_got]
    cyc, pra, prb, mxu, mxd, skipped = 0, 0.0, 0.0, 0, 0, 0

    def sell_buy(q_sell, p_sell, lot_buy, p_buy):
        """sell q_sell of X at p_sell (minus slip, fee in $) ⇒ buy Y at p_buy (plus slip) with all of it, fee in Y ⇒ (Y got, $ dust, fee $)"""
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
        while R >= R0 * (1 + step) ** (L + 1):              # XLM stronger by one more level
            L += 1
            if dn:                                          # close a «bought XLM» swap: sell its XLM back to XRP (only with profit)
                qa_sold, qb_got = dn[-1]
                qs = floor_lot(qb_got, lb)
                full, _d, _f = sell_buy(qs, pb, la, pa)
                prof = full - qa_sold
                if prof <= 0 or qs < minb:
                    skipped += 1
                    continue
                want = qa_sold + split * prof                # XRP back + half the profit · the rest of the profit stays in XLM
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
            elif len(up) < mx:                              # open: sell one unit of XLM for XRP
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
        while R <= R0 * (1 + step) ** (L - 1):              # XLM weaker by one more level
            L -= 1
            if up:                                          # close a «sold XLM» swap: buy the XLM back with its XRP (only with profit)
                qb_sold, qa_got = up[-1]
                qs = floor_lot(qa_got, la)
                full, _d, _f = sell_buy(qs, pa, lb, pb)
                prof = full - qb_sold
                if prof <= 0 or qs < mina:
                    skipped += 1
                    continue
                want = qb_sold + split * prof
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
            elif len(dn) < mx:                              # open: sell one unit of XRP for XLM
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
    pa, pb = PA[-1], PB[-1]
    hold = qa0 * pa + qb0 * pb
    val = qa * pa + qb * pb + usd
    return {"qa0": qa0, "qb0": qb0, "qa": qa, "qb": qb, "usd": usd, "cyc": cyc, "pra": pra, "prb": prb, "open_up": len(up), "open_dn": len(dn),
            "mxu": mxu, "mxd": mxd, "hold": hold, "val": val, "fees": fees, "skipped": skipped}


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


VAR = [(s, f, mx) for s in (0.008, 0.01, 0.015, 0.02, 0.03, 0.04) for f, mx in ((0.05, 10), (0.10, 5))] + [(0.02, 0.05, 20), (0.015, 0.03, 20)]
FEES = (("taker 0.10% + spread 0.02%", 0.001, 0.0002), ("maker 0.08%", 0.0008, 0.0))
for A, B in PAIRS:
    la, mina = inst(A)
    lb, minb = inst(B)
    P(f"pair {A.split('-')[0]}/{B.split('-')[0]} · lots {A}: lot {la} min {mina} · {B}: lot {lb} min {minb}")
    for bar, (dt, n) in FR.items():
        if A != "XRP-USDT" or B != "XLM-USDT":
            if bar != "1H":
                continue
        t1 = time.time()
        ca, cb = fetch(A, bar, n), fetch(B, bar, n)
        tb = {c[0]: c[4] for c in cb}
        rows = [(c[0], c[4], tb[c[0]]) for c in ca if c[0] in tb]
        if len(rows) < 500:
            P(f"{A}/{B} {bar}: too few candles ({len(rows)})")
            continue
        T, PA, PB = [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]
        st = stats(T, PA, PB, dt)
        P(f"== {A.split('-')[0]}/{B.split('-')[0]} {bar}: {len(rows)} candles · {st['days']:.0f} days ({time.strftime('%Y-%m-%d', time.gmtime(T[0]))} … "
          f"{time.strftime('%Y-%m-%d', time.gmtime(T[-1]))}) · {A.split('-')[0]} {100 * st['a_chg']:+.1f}% · {B.split('-')[0]} {100 * st['b_chg']:+.1f}% · "
          f"correlation {st['corr']:.2f} · {B.split('-')[0]} moves ×{st['vol_ratio']:.2f} (beta {st['beta']:.2f}) · ratio {st['r0']:.4f} ⇒ {st['r1']:.4f} "
          f"(range {st['rmin']:.4f}–{st['rmax']:.4f}) · fetched in {time.time() - t1:.0f}s")
        reb = rebal(PA, PB, max(1, int(7 * 86400 / dt)), 0.001)
        for fn, fee, slip in FEES:
            for step, frac, mx in VAR:
                r = sim(T, PA, PB, step, frac, mx, fee, slip, la, lb, mina, minb)
                da, db = r["qa"] - r["qa0"], r["qb"] - r["qb0"]
                rec = {"pair": f"{A}/{B}", "bar": bar, "fee": fn, "step": step, "frac": frac, "max": mx, **{k: round(v, 6) if isinstance(v, float) else v for k, v in r.items()},
                       "reb": round(reb, 4), **{k: round(v, 6) for k, v in st.items()}}
                OUT["runs"].append(rec)
                P(f"{A.split('-')[0]}/{B.split('-')[0]} {bar} [{fn}] step {100 * step:.1f}% · swap {100 * frac:.0f}% · max {mx}: "
                  f"{A.split('-')[0]} {da:+.2f} ({100 * da / r['qa0']:+.2f}%) · {B.split('-')[0]} {db:+.2f} ({100 * db / r['qb0']:+.2f}%) · "
                  f"cycles {r['cyc']} · realized {A.split('-')[0]} {r['pra']:+.2f} {B.split('-')[0]} {r['prb']:+.2f} · open now ⬆{r['open_up']} ⬇{r['open_dn']} "
                  f"(max ⬆{r['mxu']} ⬇{r['mxd']}) · $ left {r['usd']:.2f} · fees {r['fees']:.2f}$ · value {r['val']:.0f}$ vs hold {r['hold']:.0f}$ "
                  f"({100 * (r['val'] / r['hold'] - 1):+.2f}%) · weekly 50/50 {reb:.0f}$")
json.dump(OUT, open("/tmp/holyratio.json", "w"), ensure_ascii=False)
P(f"DONE · {time.time() - T0:.0f}s")
