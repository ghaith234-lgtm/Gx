# 🔬 Holy check 14 — the new analyst, rebuilt from scratch as a trader would (the owner 21-11: «كله اريدك تصيغه من جديد واتسوي عليه اختبار حتى
#    لو يطول ساعات … سويه انت كانما خبير تداول … اريد يقلي شديصير بالسوق بالحاضر وشراح يصير للسوق بشكل عام وبالعملات بشكل خاص»).
#    What can honestly be forecast, tested on years of real OKX prices with a walk-forward (every quarter learns only from the past before it,
#    then runs on that quarter unseen), against the base rate and against shuffled prices:
#    ① DIRECTION — P(up) over the next 4 hours (1H candles) · tomorrow (4H · 6 candles) · the week (1D · 7 candles), a coin and the market
#       (Bitcoin): one pooled logistic model on ~40 causal features (trend · momentum · volatility · volume · strength vs Bitcoin · the market's
#       state · the 70 signals) — accuracy · Brier skill vs the base rate · calibration (said 60% ⇒ was it 60%?) · the confident subset
#    ② STRONGER OR WEAKER THAN BITCOIN over the same horizons (relative strength)
#    ③ THE RANGE — the 10%–90% band of the next move from the coin's recent volatility: does it hold the price 80% of the time?
#    ④ LEAD TIME — for the confident forecasts: the move before vs after · ⑤ which features carry the weight
#    Results: HOLYSIG14 lines + /tmp/holysig14.json. Public market data only — no keys, no orders, no notifications.
#    python3 ci/sig_check14.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time
import numpy as np

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig14_")
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
DRY = os.environ.get("SIG14_DRY") == "1"


def P(*a):
    print("HOLYSIG14", *a, flush=True)


EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
HZ = {"1H": 4, "4H": 6, "1D": 7}                       # the next 4 hours · tomorrow · the week
HZN = {"1H": "the next 4 hours", "4H": "tomorrow", "1D": "the week"}
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· horizons", HZ)

# ── the prices (public)
if DRY:
    COINS = COINS[:14]
    rnd0 = random.Random(5)
    now_ = int(time.time())
    cdb = {"c1": {}, "c4": {}, "c": {}}
    mk = {sec: [rnd0.gauss(0, 0.006 * (1 if sec == "c1" else 2 if sec == "c4" else 4)) for _ in range(n)] for sec, n in (("c1", 3000), ("c4", 1600), ("c", 1200))}
    for sec, step, n in (("c1", 3600, 3000), ("c4", 14400, 1600), ("c", 86400, 1200)):
        tend = now_ // step * step - step
        for j, s in enumerate(COINS):
            p, rows = 10.0 + j, []
            for i in range(n):
                r = 0.7 * mk[sec][i] + rnd0.gauss(0.0, 0.005 * (1 if sec == "c1" else 2 if sec == "c4" else 4))
                o, c = p, p * math.exp(r)
                rows.append([tend - (n - 1 - i) * step, o, max(o, c) * 1.002, min(o, c) * 0.998, c, 1000 + rnd0.random() * 500])
                p = c
            cdb[sec][s] = {"d": rows}
    db, fdb = {}, {}
else:
    m.SG_N["1H"] = 11000
    cdb = {}
    m._sg_refresh(COINS, ["1H", "4H", "1D"], cdb)
    db, now = {}, time.time()
    for fn in ("_pro_vix", "_pro_dxy", "_pro_us10", "_pro_epu", "_pro_gpr", "_pro_tone"):
        try:
            getattr(m, fn)(db, now)
        except Exception as ex:
            P(fn, "error", ex)
    fdb = {}
    m._fc_fng(fdb)
mkt, fng = m._sg_mkt(db, fdb), m._sg_fng_raw(fdb)
P(f"prices fetched · {time.time() - T0:.0f}s · " + " · ".join(f"{fr} {sum(1 for e in (cdb.get(m.SG_BAR[fr][0]) or {}).values() if len(e.get('d') or []) > 600)} coins" for fr in HZ))


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


# ── causal features (everything at the close of candle t from candles ≤ t)
def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.empty_like(x)
    e = x[0]
    for i, v in enumerate(x):
        e = v if i == 0 else e + a * (v - e)
        out[i] = e
    return out


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up, dn = np.where(d > 0, d, 0.0), np.where(d < 0, -d, 0.0)
    au, ad = ema(up, 2 * n - 1), ema(dn, 2 * n - 1)
    return 100 - 100 / (1 + au / np.maximum(ad, 1e-12))


def roll_mean(x, n):
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out = np.full(len(x), np.nan)
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def roll_std(x, n):
    m1, m2 = roll_mean(x, n), roll_mean(x * x, n)
    return np.sqrt(np.maximum(m2 - m1 * m1, 0.0))


def roll_pct(x, n):
    """where x[t] sits among the last n values (0…1)"""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        out[i] = (w < x[i]).mean()
    return out


FEAT = ["r1", "r3", "r6", "r12", "r24", "r48", "e20", "e50", "e200", "s20", "s50", "rsi", "macd", "bbp", "vol", "volp", "atr", "vz", "rng",
        "rs12", "rs48", "b_r12", "b_r48", "b_e200", "breadth", "mvol", "fng", "hour_s", "hour_c", "sig_up", "sig_dn"]


def feats_coin(D, E, btc_c=None):
    C, H, L, V = np.array(D["C"]), np.array(D["H"]), np.array(D["L"]), np.array(D["V"])
    n = len(C)
    lr = np.diff(np.log(C), prepend=np.log(C[0]))
    sd = roll_std(lr, 48)
    sd = np.where(np.isnan(sd) | (sd <= 0), np.nanmedian(sd[sd > 0]) if np.any(sd > 0) else 0.01, sd)
    F = {}
    for k in (1, 3, 6, 12, 24, 48):
        r = np.full(n, np.nan)
        r[k:] = np.log(C[k:] / C[:-k])
        F[f"r{k}"] = r / (sd * math.sqrt(k))
    for k in (20, 50, 200):
        e = ema(C, k)
        F[f"e{k}"] = np.log(C / e) / (sd * math.sqrt(k / 4))
        if k in (20, 50):
            sl = np.full(n, np.nan)
            sl[5:] = np.log(e[5:] / e[:-5])
            F[f"s{k}"] = sl / (sd * math.sqrt(5))
    F["rsi"] = (rsi(C) - 50) / 20
    macd = ema(C, 12) - ema(C, 26)
    F["macd"] = (macd - ema(macd, 9)) / (C * sd)
    m20, s20 = roll_mean(C, 20), roll_std(C, 20)
    F["bbp"] = (C - m20) / np.maximum(2 * s20, 1e-12)
    F["vol"] = np.log(sd)
    F["volp"] = roll_pct(sd, 200) - 0.5
    tr = np.maximum(H - L, np.maximum(abs(H - np.roll(C, 1)), abs(L - np.roll(C, 1))))
    F["atr"] = np.log(np.maximum(ema(tr, 14) / C, 1e-9)) - np.log(sd)
    lv = np.log(np.maximum(V, 1e-9))
    F["vz"] = (lv - roll_mean(lv, 50)) / np.maximum(roll_std(lv, 50), 1e-6)
    hh, ll = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(20, n):
        hh[i], ll[i] = H[i - 20:i + 1].max(), L[i - 20:i + 1].min()
    F["rng"] = (C - ll) / np.maximum(hh - ll, 1e-12) - 0.5
    if btc_c is not None:
        bl = np.log(btc_c)
        for k in (12, 48):
            a = np.full(n, np.nan)
            a[k:] = np.log(C[k:] / C[:-k]) - (bl[k:] - bl[:-k])
            F[f"rs{k}"] = a / (sd * math.sqrt(k))
    else:
        F["rs12"] = np.zeros(n)
        F["rs48"] = np.zeros(n)
    up = np.zeros(n)
    dn = np.zeros(n)
    for (code, s), lst in E.items():
        if code not in m.SB_NUM:
            continue
        for i in lst:
            for j in range(i, min(n, i + 3)):
                if s > 0:
                    up[j] += 1
                else:
                    dn[j] += 1
    F["sig_up"], F["sig_dn"] = np.log1p(up), np.log1p(dn)
    T = np.array(D["T"])
    hr = (T % 86400) / 3600.0
    F["hour_s"], F["hour_c"] = np.sin(2 * math.pi * hr / 24), np.cos(2 * math.pi * hr / 24)
    return F, lr, sd


def build(db_, fr):
    """per frame: X (features) · y (up over the horizon) · yr (beat Bitcoin) · ret · sd · t · coin — rows with every feature known"""
    sec = m.SG_BAR[fr][0]
    h = HZ[fr]
    rows_btc = ((db_.get(sec) or {}).get("BTC-USDT") or {}).get("d") or []
    if len(rows_btc) < 400:
        return None
    btc = {int(r[0]): float(r[4]) for r in rows_btc}
    rd_btc = ((db_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    coins = {}
    for sym in COINS:
        rows = ((db_.get(sec) or {}).get(sym) or {}).get("d") or []
        if len(rows) < 600:
            continue
        rd = ((db_.get("c") or {}).get(sym) or {}).get("d") or []
        ctx = m._sg_ctx(sym, rd, db, mkt, fng, {int(r[0]): float(r[4]) for r in rd_btc})
        try:
            D, E = m._sg_events(rows, fr == "1D", ctx, dx=m.SG_SEC[fr])
        except Exception:
            D, E = m._sg_D(rows, fr == "1D"), {}
        bc = np.array([btc.get(t, np.nan) for t in D["T"]])
        if np.isnan(bc).mean() > 0.2:
            continue
        bc = np.where(np.isnan(bc), np.nanmean(bc), bc)
        F, lr, sd = feats_coin(D, E, bc if sym != "BTC-USDT" else None)
        coins[sym] = (D, F, lr, sd, bc)
    if "BTC-USDT" not in coins:
        return None
    # the market: Bitcoin's own trend + breadth (share of coins above their 50-candle mean) + the market's volatility
    Tb = coins["BTC-USDT"][0]["T"]
    FB = coins["BTC-USDT"][1]
    bmap = {t: i for i, t in enumerate(Tb)}
    ab = {}
    for sym, (D, F, lr, sd, bc) in coins.items():
        C = np.array(D["C"])
        m50 = roll_mean(C, 50)
        for i, t in enumerate(D["T"]):
            if not np.isnan(m50[i]):
                ab.setdefault(t, []).append(1.0 if C[i] > m50[i] else 0.0)
    br = {t: (np.mean(v) - 0.5) * 2 for t, v in ab.items() if len(v) >= 8}
    fv = {}
    if fng:
        ks, vs = fng
        for k_, v_ in zip(ks, vs):
            fv[int(k_) // 86400] = (float(v_) - 50) / 25
    X, Y, YR, RET, SD, TT, CO, I = [], [], [], [], [], [], [], []
    for sym, (D, F, lr, sd, bc) in coins.items():
        C = np.array(D["C"])
        n = len(C)
        T = D["T"]
        for i in range(210, n - h):
            bi = bmap.get(T[i])
            if bi is None:
                continue
            row = []
            okr = True
            for k in FEAT:
                if k.startswith("b_"):
                    v = FB[{"b_r12": "r12", "b_r48": "r48", "b_e200": "e200"}[k]][bi]
                elif k == "breadth":
                    v = br.get(T[i], np.nan)
                elif k == "mvol":
                    v = FB["vol"][bi]
                elif k == "fng":
                    v = fv.get((T[i] - 86400) // 86400, 0.0)            # yesterday's reading (published once a day)
                else:
                    v = F[k][i]
                if v is None or not np.isfinite(v):
                    okr = False
                    break
                row.append(float(max(-6.0, min(6.0, v))))
            if not okr:
                continue
            fwd = math.log(C[i + h] / C[i])
            bfwd = math.log(bc[i + h] / bc[i])
            X.append(row); Y.append(1 if fwd > 0 else 0); YR.append(1 if fwd - bfwd > 0 else 0)
            RET.append(fwd); SD.append(sd[i]); TT.append(T[i]); CO.append(sym); I.append(i)
    return {"X": np.array(X), "y": np.array(Y), "yr": np.array(YR), "ret": np.array(RET), "sd": np.array(SD), "t": np.array(TT), "coin": np.array(CO),
            "i": np.array(I), "coins": coins}


def fit_logit(X, y, l2=1.0, it=300, lr=0.5):
    mu, sg = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sg
    w = np.zeros(Z.shape[1])
    b = math.log((y.mean() + 1e-6) / (1 - y.mean() + 1e-6))
    n = len(y)
    for _ in range(it):
        p = 1 / (1 + np.exp(-(Z @ w + b)))
        g = Z.T @ (p - y) / n + l2 * w / n
        w -= lr * g
        b -= lr * float((p - y).mean())
    return {"mu": mu, "sg": sg, "w": w, "b": b}


def pred(md, X):
    Z = (X - md["mu"]) / md["sg"]
    return 1 / (1 + np.exp(-(Z @ md["w"] + md["b"])))


def calib(p, y, bins=(0, .40, .45, .48, .52, .55, .60, 1.01)):
    out = []
    for a, b in zip(bins[:-1], bins[1:]):
        k = (p >= a) & (p < b)
        if k.sum():
            out.append((f"{a:.2f}–{min(b, 1):.2f}", int(k.sum()), round(float(p[k].mean()), 3), round(float(y[k].mean()), 3)))
    return out


def evaluate(B, label, fr, quarters):
    """walk-forward: each quarter learns from everything before it (one pooled model for every coin) and runs on the quarter unseen"""
    X, y, yr, ret, sd, t, coin = B["X"], B["y"], B["yr"], B["ret"], B["sd"], B["t"], B["coin"]
    h = HZ[fr]
    gap = h * m.SG_SEC[fr]                                       # no training label may reach into the test quarter
    allp, ally, allp_r, ally_r, allbase, allbase_r, allret, allsd, allt, allc = [], [], [], [], [], [], [], [], [], []
    coef = []
    for q0, q1 in quarters:
        tr = t < q0 - gap
        te = (t >= q0) & (t < q1)
        if tr.sum() < 2000 or te.sum() < 200:
            continue
        md = fit_logit(X[tr], y[tr].astype(float))
        mr = fit_logit(X[tr], yr[tr].astype(float))
        coef.append(md["w"])
        p, pr = pred(md, X[te]), pred(mr, X[te])
        allp.append(p); ally.append(y[te]); allp_r.append(pr); ally_r.append(yr[te])
        allbase.append(np.full(te.sum(), y[tr].mean())); allbase_r.append(np.full(te.sum(), yr[tr].mean()))
        allret.append(ret[te]); allsd.append(sd[te]); allt.append(t[te]); allc.append(coin[te])
    if not allp:
        P(f"{label} {fr}: not enough data")
        return None
    p, Y, pr, YR = np.concatenate(allp), np.concatenate(ally), np.concatenate(allp_r), np.concatenate(ally_r)
    base, base_r = np.concatenate(allbase), np.concatenate(allbase_r)
    ret_, sd_, t_, c_ = np.concatenate(allret), np.concatenate(allsd), np.concatenate(allt), np.concatenate(allc)
    res = {}
    blk = max(h * m.SG_SEC[fr], 7 * 86400)                       # independent periods: a week or the horizon (the coins move together · the labels overlap)

    def boot(pp, yy, bb, tt, n_b=400):
        """90% interval of the accuracy and the Brier skill over independent time blocks (resampled) — luck shows as an interval across 50% / 0"""
        g = (tt // blk).astype(np.int64)
        ub, inv = np.unique(g, return_inverse=True)
        cr = np.bincount(inv, weights=((pp > 0.5) == (yy == 1)).astype(float))
        nn = np.bincount(inv).astype(float)
        e1 = np.bincount(inv, weights=(pp - yy) ** 2)
        e0 = np.bincount(inv, weights=(bb - yy) ** 2)
        rg = np.random.default_rng(7)
        A, Sk = [], []
        for _ in range(n_b):
            ix = rg.integers(0, len(ub), len(ub))
            A.append(cr[ix].sum() / nn[ix].sum())
            Sk.append(1 - e1[ix].sum() / max(1e-12, e0[ix].sum()))
        return len(ub), np.quantile(A, [0.05, 0.95]), np.quantile(Sk, [0.05, 0.95])
    for nm, pp, yy, bb in (("direction", p, Y, base), ("vs Bitcoin", pr, YR, base_r)):
        tt_ = t_
        if nm == "vs Bitcoin":
            k = c_ != "BTC-USDT"
            pp, yy, bb, tt_ = pp[k], yy[k], bb[k], t_[k]
        acc = float(((pp > 0.5) == (yy == 1)).mean())
        bs, bs0 = float(((pp - yy) ** 2).mean()), float(((bb - yy) ** 2).mean())
        nb_, ci_a, ci_s = boot(pp, yy, bb, tt_)
        conf = {}
        for d in (0.03, 0.05, 0.08, 0.12):
            k = np.abs(pp - 0.5) >= d
            if k.sum() >= 30:
                conf[d] = (int(k.sum()), round(float(((pp[k] > 0.5) == (yy[k] == 1)).mean()), 4), round(float(k.mean()), 4))
        res[nm] = {"acc": round(acc, 4), "skill": round(1 - bs / bs0, 4), "n": int(len(yy)), "up": round(float(yy.mean()), 4), "conf": conf, "calib": calib(pp, yy),
                   "blocks": nb_, "ci_acc": [round(float(x), 4) for x in ci_a], "ci_skill": [round(float(x), 4) for x in ci_s]}
        P(f"{label} {fr} ({HZN[fr]}) {nm}: right {100 * acc:.1f}% of {len(yy)} (ups {100 * yy.mean():.1f}%) · 90% over {nb_} independent periods "
          f"{100 * ci_a[0]:.1f}–{100 * ci_a[1]:.1f}% · Brier skill vs the base rate {100 * (1 - bs / bs0):+.2f}% ({100 * ci_s[0]:+.1f} … {100 * ci_s[1]:+.1f}) · "
          + " · ".join(f"|p−½|≥{d}: {100 * v[1]:.1f}% of {v[0]} ({100 * v[2]:.0f}% of the time)" for d, v in conf.items()))
        P(f"{label} {fr} {nm} calibration (said → was): " + " · ".join(f"{a}: {100 * pm:.0f}%→{100 * ob:.0f}% (n {nn})" for a, nn, pm, ob in res[nm]["calib"]))
    kb = c_ == "BTC-USDT"
    if kb.sum() >= 50:
        acc_b = float(((p[kb] > 0.5) == (Y[kb] == 1)).mean())
        bs, bs0 = float(((p[kb] - Y[kb]) ** 2).mean()), float(((base[kb] - Y[kb]) ** 2).mean())
        P(f"{label} {fr} the market (Bitcoin) direction: right {100 * acc_b:.1f}% of {int(kb.sum())} · skill {100 * (1 - bs / bs0):+.2f}%")
        res["btc"] = {"acc": round(acc_b, 4), "skill": round(1 - bs / bs0, 4), "n": int(kb.sum())}
    # ③ the range: 10%–90% of the next move from the recent volatility (normal) — and from the past's own quantiles of move/σ
    z = ret_ / (sd_ * math.sqrt(h))
    cov_n = float(((z > -1.2816) & (z < 1.2816)).mean())
    lo_q, hi_q = np.quantile(z[: max(1, len(z) // 4)], [0.10, 0.90])
    cov_e = float(((z[len(z) // 4:] > lo_q) & (z[len(z) // 4:] < hi_q)).mean())
    P(f"{label} {fr} ③ the 10–90% range: with the normal curve it held the price {100 * cov_n:.1f}% of the time (target 80%) · with the quantiles learned from "
      f"the first quarter ({lo_q:+.2f}σ … {hi_q:+.2f}σ) {100 * cov_e:.1f}% on the rest · typical band ±{100 * float(np.median(sd_) * math.sqrt(h) * 1.28):.2f}%")
    res["range"] = {"normal": round(cov_n, 4), "learned": round(cov_e, 4), "q": [round(float(lo_q), 3), round(float(hi_q), 3)]}
    # ④ lead time for the confident forecasts: the move its way before (the last horizon) vs after
    k = np.abs(p - 0.5) >= 0.05
    if k.sum() >= 30:
        s = np.where(p[k] > 0.5, 1.0, -1.0)
        coins = B["coins"]
        before = []
        for tt, cc, ss in zip(t_[k], c_[k], s):
            D = coins[cc][0]
            ii = D["T"].index(int(tt)) if int(tt) in D["T"] else -1
            if ii >= h:
                before.append(ss * math.log(D["C"][ii] / D["C"][ii - h]))
        after = s * ret_[k]
        P(f"{label} {fr} ④ the confident forecasts ({int(k.sum())}): moved their way BEFORE {100 * float(np.mean(before)) if before else 0:+.2f}% · AFTER {100 * float(np.mean(after)):+.2f}% "
          f"(the average move over {HZN[fr]})")
        res["lead"] = {"before": round(float(np.mean(before)) if before else 0, 5), "after": round(float(np.mean(after)), 5), "n": int(k.sum())}
    if coef:
        w = np.mean(coef, 0)
        top = sorted(zip(FEAT, w), key=lambda x: -abs(x[1]))[:10]
        P(f"{label} {fr} ⑤ the weights (standardized · + = up): " + " · ".join(f"{a} {b:+.3f}" for a, b in top))
        res["w"] = {a: round(float(b), 4) for a, b in zip(FEAT, w)}
    return res


def run(db_, label):
    out = {}
    for fr in ("4H", "1D", "1H"):
        t1 = time.time()
        B = build(db_, fr)
        if B is None or not len(B["y"]):
            P(f"{label} {fr}: no data")
            continue
        t_end = int(B["t"].max())
        span = 91 * 86400 if not DRY else 25 * 86400
        nq = 8 if fr != "1H" else 3
        quarters = [(t_end - (nq - q) * span, t_end - (nq - q - 1) * span) for q in range(nq)]
        P(f"{label} {fr}: {len(B['y'])} rows · {len(B['coins'])} coins · {nq} quarters unseen from {time.strftime('%Y-%m-%d', time.gmtime(quarters[0][0]))} · {time.time() - t1:.0f}s")
        out[fr] = evaluate(B, label, fr, quarters)
        del B
    return out


OUT["real"] = run(cdb, "REAL")
P(f"real done · {time.time() - T0:.0f}s")
OUT["shuffled"] = run(shuffled(cdb, 11), "SHUFFLED")
json.dump(OUT, open("/tmp/holysig14.json", "w"), ensure_ascii=False, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
P(f"all done · {time.time() - T0:.0f}s")
