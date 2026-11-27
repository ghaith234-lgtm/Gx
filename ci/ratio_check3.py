# 🔀 Holy ratio check 3 — the owner 27-11: «افضل تبقى عملة اتصير مثل الدولار وعملة تداول … الوسيط يصير الدولار محسوب كل العمولات ·
#   الخزنة العملة الرئيسية انا اختارها · خليه مفتوح حسب العملة والنسب · جرب xrp عملة رىيسية وxlm ثانوية · اذا خلينه الxrp عملة رئيسية (وممكن
#   العكس) كانما هي واحد دولار تبقى ثابته · اي اعداد جرب بس اهم شي محسوب كل شيء · العمولة ٠.١ · اريد اعرف كم اربح باليوم · ممكن اخلي بوتين
#   متعاكسين واحد يجمع xrp واحد يجمع xlm · افحصه وكذلك شوف الارباح»
#   The bot = ♾️ on the price of XLM counted in XRP (R = XLM ÷ XRP): a level every «step» from the start · R down one level ⇒ (close an open
#   «XLM bought earlier above» swap with profit, else) spend one order of XRP on XLM · R up one level ⇒ the mirror · every swap = sell → USDT → buy
#   at the same moment (2 market orders · 0.10% each + 0.02% spread) · a close only when it gives back MORE than it paid after every fee ·
#   OKX's real lot and minimum · the dollar dust kept and counted.
#   Choices (all open): start = all XRP · half and half · all XLM — profit = all to XRP · all to XLM · half and half · «own side» (two opposite bots:
#   the XRP side collects XRP, the XLM side collects XLM) — step 2/3/5% · order 10$/20$ (fixed coins at the start price) · floor = the most one side
#   can spend: 100$ · 200$ · all — start money 400$.
#   Measures: both coin counts · realized profit · profit PER DAY ($ at that day's price · XRP · XLM) · share of days with profit · month by month ·
#   the wallet counted in XRP and in XLM · the worst dip of the wallet in XRP · vs holding the start mix · rolling starts (every 14 days for 90 days ·
#   every 30 days for 180 days) — REAL OKX public candles (no keys · no orders): 1H 3 years · 15m 1 year · 5m 90 days.
#   python3 ci/ratio_check3.py Holy_Dashboard.pyw
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
    print("HR3", *a, flush=True)


DRY = os.environ.get("RATIO_DRY") == "1"
A, B = "XRP-USDT", "XLM-USDT"
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





FEE, SLIP, CAP = 0.001, 0.0002, 400.0
STARTS = {"half": (0.5, 0.5), "allXRP": (1.0, 0.0), "allXLM": (0.0, 1.0)}
MODES = {"toXRP": (1.0, 0.0), "toXLM": (0.0, 1.0), "half": (0.5, 0.5), "own": (1.0, 1.0)}   # (share to XRP on an XRP-side close · share to XLM on an XLM-side close)
MODES_OF = {"half": ("own", "half", "toXRP", "toXLM"), "allXRP": ("toXRP", "toXLM"), "allXLM": ("toXLM", "toXRP")}


def sim(T, PA, PB, step, order, floor, start, mode, la, lb, mina, minb, daily=False):
    """A = XRP · B = XLM · R = PB/PA · start money CAP split by «start» · one order = «order» $ in coins at the start price ·
    floor = the most $ (at the start price) one side may have out · mode = who gets the profit"""
    fa, fb = STARTS[start]
    qa, qb, usd, fees = CAP * fa / PA[0], CAP * fb / PB[0], 0.0, 0.0
    qa0, qb0 = qa, qb
    ua, ub = order / PA[0], order / PB[0]
    mx = 10 ** 9 if floor is None else max(1, int(round(floor / order)))
    sa_dn, sb_up = MODES[mode]
    R0, L = PB[0] / PA[0], 0
    up, dn = [], []                                   # up: sold XLM got XRP (the XLM side) · dn: sold XRP got XLM (the XRP side)
    cyc, pra, prb, mxu, mxd, skipped = 0, 0.0, 0.0, 0, 0, 0
    W0 = qa + qb * R0
    wmin = 0.0
    day = {}                                          # day ⇒ [realized $, realized XRP, realized XLM]
    wday = {}                                         # day ⇒ wallet in XRP at the day's last candle

    def sell_buy(q_sell, p_sell, lot_buy, p_buy):
        usd_in = q_sell * p_sell * (1 - SLIP)
        f1 = usd_in * FEE
        usd_in -= f1
        y = floor_lot(usd_in / (p_buy * (1 + SLIP)), lot_buy)
        cost = y * p_buy * (1 + SLIP)
        f2 = y * FEE
        return y - f2, usd_in - cost, f1 + f2 * p_buy

    for i in range(1, len(T)):
        pa, pb = PA[i], PB[i]
        R = pb / pa
        d = T[i] // 86400
        while R >= R0 * (1 + step) ** (L + 1):        # XLM dearer by one level
            L += 1
            if dn:                                    # the XRP side: sell back the XLM it bought lower
                qa_sold, qb_got = dn[-1]
                qs = floor_lot(qb_got, lb)
                full, _d, _f = sell_buy(qs, pb, la, pa)
                prof = full - qa_sold
                if prof <= 0 or qs < minb:
                    skipped += 1
                    continue
                want = qa_sold + sa_dn * prof
                need_usd = want / (1 - FEE) * pa * (1 + SLIP)
                qs2 = min(qs, ceil_lot(need_usd / ((1 - FEE) * pb * (1 - SLIP)), lb))
                got, dust, f = sell_buy(qs2, pb, la, pa)
                qb -= qs2
                qa += got
                usd += dust
                fees += f
                ga, gb = got - qa_sold, qb_got - qs2
                pra += ga
                prb += gb
                if daily:
                    x = day.setdefault(d, [0.0, 0.0, 0.0])
                    x[0] += ga * pa + gb * pb
                    x[1] += ga
                    x[2] += gb
                cyc += 1
                dn.pop()
            elif len(up) < mx:                        # the XLM side: spend one order of XLM on XRP
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
        while R <= R0 * (1 + step) ** (L - 1):        # XLM cheaper by one level
            L -= 1
            if up:                                    # the XLM side: buy back the XLM it sold higher
                qb_sold, qa_got = up[-1]
                qs = floor_lot(qa_got, la)
                full, _d, _f = sell_buy(qs, pa, lb, pb)
                prof = full - qb_sold
                if prof <= 0 or qs < mina:
                    skipped += 1
                    continue
                want = qb_sold + sb_up * prof
                need_usd = want / (1 - FEE) * pb * (1 + SLIP)
                qs2 = min(qs, ceil_lot(need_usd / ((1 - FEE) * pa * (1 - SLIP)), la))
                got, dust, f = sell_buy(qs2, pa, lb, pb)
                qa -= qs2
                qb += got
                usd += dust
                fees += f
                gb, ga = got - qb_sold, qa_got - qs2
                prb += gb
                pra += ga
                if daily:
                    x = day.setdefault(d, [0.0, 0.0, 0.0])
                    x[0] += ga * pa + gb * pb
                    x[1] += ga
                    x[2] += gb
                cyc += 1
                up.pop()
            elif len(dn) < mx:                        # the XRP side: spend one order of XRP on XLM
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
        W = qa + qb * R + usd / pa
        wmin = min(wmin, W / W0 - 1)
        if daily:
            wday[d] = W
    pa, pb = PA[-1], PB[-1]
    R1 = pb / pa
    W1 = qa + qb * R1 + usd / pa
    hold = qa0 * pa + qb0 * pb
    val = qa * pa + qb * pb + usd
    days = max(1.0, (T[-1] - T[0]) / 86400)
    rusd = sum(x[0] for x in day.values()) if daily else None
    out = {"qa0": qa0, "qb0": qb0, "qa": qa, "qb": qb, "usd": usd, "cyc": cyc, "pra": pra, "prb": prb, "open_up": len(up), "open_dn": len(dn),
           "mxu": mxu, "mxd": mxd, "hold": hold, "val": val, "fees": fees, "skipped": skipped, "days": days,
           "w_xrp": W1 / W0 - 1, "w_xlm": (W1 / R1) / (W0 / R0) - 1, "w_min": wmin}
    if daily:
        d0, d1 = T[0] // 86400, T[-1] // 86400
        n = d1 - d0 + 1
        out["usd_day"] = rusd / days
        out["xrp_day"] = pra / days
        out["xlm_day"] = prb / days
        out["days_profit"] = sum(1 for x in day.values() if x[0] > 0) / n
        out["best_day"] = max((x[0] for x in day.values()), default=0.0)
        mon = {}
        for dd, x in day.items():
            k = time.strftime("%Y-%m", time.gmtime(dd * 86400))
            mon[k] = mon.get(k, 0.0) + x[0]
        out["months"] = mon
        ks = sorted(wday)
        out["w_worst_day"] = min((wday[ks[j]] / wday[ks[j - 1]] - 1 for j in range(1, len(ks))), default=0.0)
    return out

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



STEPS, ORDERS, FLOORS = (0.02, 0.03, 0.05), (10.0, 20.0), (100.0, 200.0, None)


def fl(f):
    return "all" if f is None else f"{f:.0f}$"


def line(tag, r):
    return (f"{tag} | XRP {r['qa0']:.6g} ⇒ {r['qa']:.6g} · XLM {r['qb0']:.6g} ⇒ {r['qb']:.6g} · realized XRP {r['pra']:+.4f} XLM {r['prb']:+.4f} · "
            f"cycles {r['cyc']} · open ⬆{r['open_up']} ⬇{r['open_dn']} (max ⬆{r['mxu']} ⬇{r['mxd']}) · per day {r['usd_day']:.4f}$ "
            f"(XRP {r['xrp_day']:.5f} · XLM {r['xlm_day']:.5f}) · days with profit {100 * r['days_profit']:.0f}% · best day {r['best_day']:.2f}$ · "
            f"wallet in XRP {100 * r['w_xrp']:+.2f}% · in XLM {100 * r['w_xlm']:+.2f}% · worst dip in XRP {100 * r['w_min']:+.1f}% · worst day {100 * r['w_worst_day']:+.2f}% · "
            f"$ {CAP:.0f} ⇒ {r['val']:.2f} vs hold {r['hold']:.2f} ({100 * (r['val'] / r['hold'] - 1):+.2f}%) · fees {r['fees']:.2f}$ · skipped {r['skipped']}")


HEAD = [("half", "own", 0.03, 20.0, 200.0), ("allXRP", "toXRP", 0.03, 20.0, 200.0), ("allXLM", "toXLM", 0.03, 20.0, 200.0),
        ("half", "own", 0.02, 20.0, 200.0), ("half", "own", 0.05, 20.0, 200.0), ("allXRP", "toXRP", 0.05, 20.0, 200.0), ("allXLM", "toXLM", 0.05, 20.0, 200.0)]
la, mina = inst(A)
lb, minb = inst(B)
nA, nB = A.split("-")[0], B.split("-")[0]
P(f"lots {A}: lot {la} min {mina} · {B}: lot {lb} min {minb} · fee {100 * FEE:.2f}% every order + spread {100 * SLIP:.2f}% · start {CAP:.0f}$")
for bar, (dt, n) in FR.items():
    t1 = time.time()
    ca, cb = fetch(A, bar, n), fetch(B, bar, n)
    tbm = {c[0]: c[4] for c in cb}
    rows = [(c[0], c[4], tbm[c[0]]) for c in ca if c[0] in tbm]
    if len(rows) < 500:
        P(f"{bar}: too few candles ({len(rows)})")
        continue
    T, PA, PB = [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows]
    st = stats(T, PA, PB, dt)
    P(f"== {bar}: {len(rows)} candles · {st['days']:.0f} days ({time.strftime('%Y-%m-%d', time.gmtime(T[0]))} … {time.strftime('%Y-%m-%d', time.gmtime(T[-1]))}) · "
      f"{nA} {PA[0]:.4f}$ ⇒ {PA[-1]:.4f}$ ({100 * st['a_chg']:+.1f}%) · {nB} {PB[0]:.4f}$ ⇒ {PB[-1]:.4f}$ ({100 * st['b_chg']:+.1f}%) · "
      f"1 XLM = {st['r0']:.5f} ⇒ {st['r1']:.5f} XRP (range {st['rmin']:.5f}–{st['rmax']:.5f}) · correlation {st['corr']:.2f} · fetched in {time.time() - t1:.0f}s")
    for start, modes in MODES_OF.items():
        for mode in modes:
            for step in STEPS:
                for order in ORDERS:
                    for floor in FLOORS:
                        r = sim(T, PA, PB, step, order, floor, start, mode, la, lb, mina, minb, daily=True)
                        mon = r.pop("months")
                        OUT["runs"].append({"bar": bar, "part": "all", "start": start, "mode": mode, "step": step, "order": order, "floor": floor,
                                            **{k: round(v, 8) if isinstance(v, float) else v for k, v in r.items()}})
                        P(line(f"{bar} [all] start {start} · profit {mode} · step {100 * step:.0f}% · order {order:.0f}$ · floor {fl(floor)}", r))
                        if (start, mode, step, order, floor) in HEAD:
                            P(f"{bar} months · start {start} · profit {mode} · step {100 * step:.0f}% · order {order:.0f}$ · floor {fl(floor)} · realized $ per month: "
                              + " · ".join(f"{k} {v:.2f}" for k, v in sorted(mon.items())))
    if bar == "1H" and not DRY:
        k = len(T) * 2 // 3
        for pn, i0, i1 in (("first 2 years", 0, k), ("last year", k, len(T))):
            P(f"-- 1H {pn}: {time.strftime('%Y-%m-%d', time.gmtime(T[i0]))} … {time.strftime('%Y-%m-%d', time.gmtime(T[i1 - 1]))} · "
              f"{nA} {100 * (PA[i1 - 1] / PA[i0] - 1):+.1f}% · {nB} {100 * (PB[i1 - 1] / PB[i0] - 1):+.1f}%")
            for start, mode, step, order, floor in HEAD:
                r = sim(T[i0:i1], PA[i0:i1], PB[i0:i1], step, order, floor, start, mode, la, lb, mina, minb, daily=True)
                r.pop("months")
                P(line(f"1H [{pn}] start {start} · profit {mode} · step {100 * step:.0f}% · order {order:.0f}$ · floor {fl(floor)}", r))
    # rolling starts: a fresh bot every «every» days, running «run» days
    every, run = ((30, 180) if bar == "1H" else (14, 90) if bar == "15m" else (7, 30))
    per = int(86400 / dt)
    for start, mode, step, order, floor in HEAD:
        res = []
        i = 0
        while i + run * per <= len(T):
            r = sim(T[i:i + run * per], PA[i:i + run * per], PB[i:i + run * per], step, order, floor, start, mode, la, lb, mina, minb, daily=True)
            res.append(r)
            i += every * per
        if not res:
            continue

        def q(key, f=lambda v: v):
            v = sorted(f(x) for x in res)
            return v[0], v[len(v) // 2], v[-1]
        ud = q("usd_day", lambda x: x["usd_day"])
        wx = q("w_xrp", lambda x: x["w_xrp"])
        wl = q("w_xlm", lambda x: x["w_xlm"])
        vh = q("vh", lambda x: x["val"] / x["hold"] - 1)
        cx = q("cx", lambda x: (x["qa"] / x["qa0"] - 1) if x["qa0"] else 0.0)
        cl = q("cl", lambda x: (x["qb"] / x["qb0"] - 1) if x["qb0"] else 0.0)
        P(f"{bar} rolling · start {start} · profit {mode} · step {100 * step:.0f}% · order {order:.0f}$ · floor {fl(floor)} · {len(res)} bots of {run} days (a new one every {every} days) · "
          f"per day $ worst {ud[0]:.4f} · middle {ud[1]:.4f} · best {ud[2]:.4f} · wallet in XRP worst {100 * wx[0]:+.1f}% · middle {100 * wx[1]:+.1f}% · best {100 * wx[2]:+.1f}% · "
          f"in XLM worst {100 * wl[0]:+.1f}% · middle {100 * wl[1]:+.1f}% · best {100 * wl[2]:+.1f}% · vs hold worst {100 * vh[0]:+.1f}% · middle {100 * vh[1]:+.1f}% · best {100 * vh[2]:+.1f}% · "
          f"XRP count worst {100 * cx[0]:+.1f}% middle {100 * cx[1]:+.1f}% · XLM count worst {100 * cl[0]:+.1f}% middle {100 * cl[1]:+.1f}% · "
          f"wallet in XRP ≥ start in {100 * sum(1 for x in res if x['w_xrp'] >= 0) / len(res):.0f}% of the bots")
json.dump(OUT, open("/tmp/holyratio3.json", "w"), ensure_ascii=False)
P(f"DONE · {time.time() - T0:.0f}s")
