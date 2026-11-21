# 🔬 Holy signals check, fifteenth pass — the daily tendency and the range, with the dashboard's OWN code (v3.36.76 · p131)
#    The owner (21-11): «نعم اريد إضافة ميل يومي ضعيف … بناء 🔮 التوقعات على نفس الأساس» · Gemini's ideas (decay 0.96 · promote ≥ 60% /
#    demote < 52% · one or two per family · regime by Hurst · Garman–Klass for the range) — each one measured here before it is built.
#    ① THE TENDENCY (m.td_prep + m.td_walk — the very functions the dashboard runs): every coin's whole daily history · the pooled record
#       grows from zero in time order · the champions are picked only from what was known that day · each variant of the rule (days ·
#       promote · demote · decay · family cap · agreeing champions · raw or Wilson) — PICKED on the two years before the last two, then
#       judged on the last two (unseen) · vs the same coin-days' baseline · weekly-block bootstrap · vs the same walk on shuffled prices ·
#       by agreement · by side · per year · by the market's regime (Bitcoin's Kaufman efficiency · Hurst)
#    ② THE RANGE 10–90%: close-to-close (the dashboard's _an_sd) vs Parkinson vs Garman–Klass · 48 or 90 candles · for the next 4 hours ·
#       tomorrow · the week · the month · three months — coverage (target 80%) and width
#    ③ THE TABLES' GRADING: how many daily firings moved less than 0.2% (no longer counted from v3.36.76) and the accuracy with and without
#    Results: lines HOLYSIG15 + /tmp/holysig15.json. Public market data only — no keys, no orders, no notifications.
#    python3 ci/sig_check15.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig15_")
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
OUT = {"version": m.APP_VERSION, "default": m.TD_P}
DAY = 86400


def P(*a):
    print("HOLYSIG15", *a, flush=True)


DRY = os.environ.get("SIG15_DRY") == "1"
EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· default rule", m.TD_P)

# ── the prices (public): the day ~7 years · 4 hours ~2 years · the hour ~1 year
if DRY:
    COINS = COINS[:12]
    rnd0 = random.Random(3)
    now_ = int(time.time())
    cdb = {"c1": {}, "c4": {}, "c": {}}
    for sec, step, n in (("c1", 3600, 2000), ("c4", 14400, 1500), ("c", DAY, 1500)):
        tend = now_ // step * step - step
        for j, s in enumerate(COINS):
            p, rows = 10.0 + j, []
            for i in range(n):
                r = rnd0.gauss(0.0002, 0.01 * (3 if sec == "c" else 1))
                o, c = p, p * math.exp(r)
                rows.append([tend - (n - 1 - i) * step, o, max(o, c) * (1 + abs(rnd0.gauss(0, 0.004))), min(o, c) * (1 - abs(rnd0.gauss(0, 0.004))), c,
                             1000 + rnd0.random() * 500])
                p = c
            cdb[sec][s] = {"d": rows}
    db, fdb = {}, {}
else:
    m.SG_N["1H"] = 9000
    cdb = {}
    m._sg_refresh(COINS, ["1H", "4H", "1D"], cdb)
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
P(f"prices fetched · {time.time() - T0:.0f}s · " + " · ".join(f"{sec} {sum(1 for e in (cdb.get(sec) or {}).values() if len(e.get('d') or []) > 300)} coins"
                                                          for sec in ("c1", "c4", "c")))


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


def zb(w, n, pb):
    return (w - n * pb) / math.sqrt(n * pb * (1 - pb)) if n and 0 < pb < 1 else 0.0


def boot(rows, k=2000, seed=7):
    """weekly blocks: resample whole weeks (a market-wide day hits many coins at once — the weeks are the independent pieces)"""
    by = {}
    for t, win in rows:
        by.setdefault(t // (7 * DAY), []).append(win)
    wk = list(by.values())
    if len(wk) < 10:
        return None
    rnd = random.Random(seed)
    acc = []
    for _ in range(k):
        s = n = 0
        for _j in range(len(wk)):
            x = wk[rnd.randrange(len(wk))]
            s += sum(x)
            n += len(x)
        acc.append(s / max(1, n))
    acc.sort()
    return round(100 * acc[int(0.025 * k)], 1), round(100 * acc[int(0.975 * k)], 1)


# ── ① the tendency
t1 = time.time()
F = m.td_prep(cdb, COINS, db, fdb)
TL = max(D["T"][D["n"] - 1] for D, E in F.values())
TEST0 = TL - 730 * DAY
SEL0 = TEST0 - 730 * DAY
P(f"① events on the whole daily history: {len(F)} coins · {time.time() - t1:.0f}s · selection {time.strftime('%Y-%m-%d', time.gmtime(SEL0))} … "
  f"test from {time.strftime('%Y-%m-%d', time.gmtime(TEST0))} to {time.strftime('%Y-%m-%d', time.gmtime(TL))}")
UPMOVE = {}                                                    # (sym, day t) ⇒ the next day's move (for the baseline)
for sym, (D, E) in F.items():
    for i in range(D["n"] - 1):
        if D["C"][i]:
            UPMOVE[(sym, D["T"][i])] = D["C"][i + 1] / D["C"][i] - 1.0


def judge(W, t_from, t_to):
    rows = [(t, sd, res, cs, sym) for t, sym, sd, res, cs in W["tend"] if t_from <= t < t_to and res in (0, 1)]
    n = len(rows)
    w = sum(r[2] for r in rows)
    q = sum(1 for r in rows if r[1] > 0) / n if n else 0.0
    mvs = [UPMOVE.get((r[4], r[0]), 0.0) for r in rows]
    u = sum(1 for x in mvs if x > 0) / n if n else 0.0
    pb = q * u + (1 - q) * (1 - u) if n else 0.5                  # the same coin-days, the side picked at random with the same up share
    return {"w": w, "n": n, "acc": round(100.0 * w / n, 2) if n else None, "pb": round(100 * pb, 2), "z": round(zb(w, n, 0.5), 2),
            "zb": round(zb(w, n, pb), 2), "rows": rows}


GRID = []
for mode in ("raw",):
    for dmin in (30, 50, 80):
        for up in (0.56, 0.58, 0.60, 0.62):
            for dn in (0.52, None):
                for dec in (1.0, 0.99, 0.96):
                    for cap in (2, 9):
                        for k in (1, 2):
                            GRID.append({"mode": mode, "dmin": dmin, "up": up, "dn": dn if dn is not None else up, "dec": dec, "cap": cap, "k": k})
for dmin in (15, 30):
    for up in (0.52, 0.55, 0.58):
        GRID.append({"mode": "wlb", "dmin": dmin, "up": up, "dn": 0.52, "dec": 1.0, "cap": 2, "k": 1})
if DRY:
    GRID = GRID[::40] + [dict(m.TD_P)]
res1 = []
for j, g in enumerate(GRID):
    W = m.td_walk(F, g)
    s, t = judge(W, SEL0, TEST0), judge(W, TEST0, TL + DAY)
    res1.append((g, s, t))
    if j % 25 == 0:
        P(f"① variants {j + 1}/{len(GRID)} · {time.time() - t1:.0f}s")
W0 = m.td_walk(F, None)
s0, t0_ = judge(W0, SEL0, TEST0), judge(W0, TEST0, TL + DAY)


def show(nm, g, s, t):
    b = boot([(r[0], r[2]) for r in t["rows"]])
    P(f"① {nm} {json.dumps(g, ensure_ascii=False)} — PICK period {s['acc']}% of {s['n']} (baseline {s['pb']}% · z vs baseline {s['zb']:+.1f}) · "
      f"TEST (unseen) {t['acc']}% of {t['n']} (baseline {t['pb']}% · z {t['z']:+.1f} vs 50% · {t['zb']:+.1f} vs baseline) · weekly bootstrap {b}")
    return {"g": g, "sel": {k: v for k, v in s.items() if k != "rows"}, "test": {k: v for k, v in t.items() if k != "rows"}, "boot": b}


OUT["default"] = show("the default (pre-registered)", m.TD_P, s0, t0_)
ok_ = [r for r in res1 if r[1]["n"] >= 300]
pick = max(ok_, key=lambda r: r[1]["zb"]) if ok_ else None
if pick:
    OUT["pick"] = show("the PICK (best on the pick period only)", *pick)
top = sorted(ok_, key=lambda r: -r[1]["zb"])[:10]
for g, s, t in top:
    P(f"① top-10 on the pick period: {json.dumps(g)} pick {s['acc']}% ({s['n']}) z {s['zb']:+.1f} ⇒ test {t['acc']}% ({t['n']}) baseline {t['pb']}% z {t['zb']:+.1f}")
for key in ("dec", "dmin", "up", "cap", "k"):
    agg = {}
    for g, s, t in res1:
        if g["mode"] != "raw":
            continue
        a = agg.setdefault(g[key], [0, 0, 0.0])
        a[0] += t["w"]
        a[1] += t["n"]
        a[2] += t["pb"] * t["n"]
    P(f"① on TEST, all variants pooled by {key}: " + " · ".join(f"{v}: {100 * a[0] / max(1, a[1]):.1f}% (baseline {a[2] / max(1, a[1]):.1f}%)"
                                                              for v, a in sorted(agg.items())))
hy = [(g, t) for g, s, t in res1 if g["mode"] == "raw" and g["dec"] == 1.0 and g["cap"] == 2 and g["k"] == 1 and g["dmin"] == 50]
P("① hysteresis (promote ≥ up · demote < 52% vs no gap) on TEST: " + " · ".join(f"up {g['up']} dn {g['dn']}: {t['acc']}% of {t['n']}" for g, t in hy))
wl = [(g, t) for g, s, t in res1 if g["mode"] == "wlb"]
P("① Wilson promotion (Gemini: ≥ N results · lower bound ≥ X) on TEST: " + " · ".join(f"n≥{g['dmin']} lb≥{g['up']}: {t['acc']}% of {t['n']}" for g, t in wl))
# by agreement · side · year
for nm, keyf in (("agreeing champions", lambda r: min(3, len(r[3]))), ("side", lambda r: "up" if r[1] > 0 else "down"),
                 ("year", lambda r: time.strftime("%Y", time.gmtime(r[0])))):
    agg = {}
    for r in judge(W0, 0, TL + DAY)["rows"]:
        a = agg.setdefault(keyf(r), [0, 0])
        a[0] += r[2]
        a[1] += 1
    P(f"① the default by {nm} (whole history): " + " · ".join(f"{k}: {100 * a[0] / a[1]:.1f}% of {a[1]}" for k, a in sorted(agg.items())))
# the regime (Bitcoin): Kaufman efficiency 20 days · Hurst 100 days (rescaled range)
bd = F.get("BTC-USDT")
REG = {}
if bd:
    C = bd[0]["C"]
    T = bd[0]["T"]

    def hurst(x):
        r = [math.log(x[i] / x[i - 1]) for i in range(1, len(x)) if x[i - 1] > 0 and x[i] > 0]
        out = []
        for n in (8, 16, 32, 64):
            rs = []
            for a in range(0, len(r) - n + 1, n):
                seg = r[a:a + n]
                mu = sum(seg) / n
                cum, mx, mn = 0.0, -1e9, 1e9
                for v in seg:
                    cum += v - mu
                    mx, mn = max(mx, cum), min(mn, cum)
                sd = math.sqrt(sum((v - mu) ** 2 for v in seg) / n)
                if sd > 0:
                    rs.append((mx - mn) / sd)
            if rs:
                out.append((math.log(n), math.log(sum(rs) / len(rs))))
        if len(out) < 3:
            return None
        mx_ = sum(a for a, b in out) / len(out)
        my_ = sum(b for a, b in out) / len(out)
        return sum((a - mx_) * (b - my_) for a, b in out) / sum((a - mx_) ** 2 for a, b in out)
    for i in range(130, len(C)):
        er = abs(C[i] - C[i - 20]) / max(1e-12, sum(abs(C[j] - C[j - 1]) for j in range(i - 19, i + 1)))
        REG[T[i]] = (er, hurst(C[i - 129:i + 1]))
    for nm, f in (("Kaufman efficiency (20 days) > 0.3 = trending", lambda er, h: "trending" if er > 0.3 else "ranging"),
                  ("Hurst (130 days) > 0.55 trending · < 0.45 ranging", lambda er, h: "?" if h is None else "trending" if h > 0.55 else "ranging" if h < 0.45 else "middle")):
        agg = {}
        for r in judge(W0, SEL0, TL + DAY)["rows"]:
            x = REG.get(r[0])
            if not x:
                continue
            a = agg.setdefault(f(*x), [0, 0])
            a[0] += r[2]
            a[1] += 1
        P(f"① the default by the market's regime — {nm} (last 4 years): " + " · ".join(f"{k}: {100 * a[0] / a[1]:.1f}% of {a[1]}" for k, a in sorted(agg.items())))
        OUT.setdefault("regime", {})[nm] = {k: [a[0], a[1]] for k, a in agg.items()}
# shuffled prices — the same walk
OUT["shuffled"] = []
for seed in (11, 12, 13):                                      # the null: the same walk on shuffled prices (3 shuffles)
    Fs = m.td_prep(shuffled(cdb, seed), COINS, db, fdb)
    Ws = m.td_walk(Fs, None)
    ss, ts, wh = judge(Ws, SEL0, TEST0), judge(Ws, TEST0, TL + DAY), judge(Ws, 0, TL + DAY)
    P(f"① SHUFFLED prices #{seed}, the default rule: whole history {wh['acc']}% of {wh['n']} · pick period {ss['acc']}% of {ss['n']} · "
      f"test {ts['acc']}% of {ts['n']} (baseline {ts['pb']}%)")
    OUT["shuffled"].append({k: {x: y for x, y in v.items() if x != "rows"} for k, v in (("all", wh), ("sel", ss), ("test", ts))})
OUT["champions_now"] = [[c, m.SB_NUM.get(c), m.SB_NM.get(c)] for c in W0["champ"]]
P("① champions today (default rule): " + " · ".join(f"{m.SB_NUM.get(c)} {m.SB_NM.get(c)}" for c in W0["champ"]))

# ── ② the range
t2 = time.time()


def sig_cc(rows):
    C = [float(r[4]) for r in rows]
    return m._an_sd(m._an_lr(C))


def sig_pk(rows):
    v = [math.log(float(r[2]) / float(r[3])) ** 2 for r in rows[1:] if float(r[3]) > 0 and float(r[2]) >= float(r[3])]
    return math.sqrt(sum(v) / len(v) / (4 * math.log(2))) if v else 0.0


def sig_gk(rows):
    v = []
    for r in rows[1:]:
        o, h, l, c = float(r[1]), float(r[2]), float(r[3]), float(r[4])
        if min(o, h, l, c) <= 0:
            continue
        v.append(0.5 * math.log(h / l) ** 2 - (2 * math.log(2) - 1) * math.log(c / o) ** 2)
    return math.sqrt(max(0.0, sum(v) / len(v))) if v else 0.0


HZ = (("4h", "c1", 4), ("1d", "c4", 6), ("1w", "c", 7), ("1m", "c", 30), ("3m", "c", 90))
RG = {}
for k, sec, h in HZ:
    for est_nm, est in (("cc", sig_cc), ("pk", sig_pk), ("gk", sig_gk)):
        for win in ((48, 90) if sec == "c" else (48,)):
            ins = tot = 0
            wsum = 0.0
            blocks = {}
            for sym, e in (cdb.get(sec) or {}).items():
                rows = e.get("d") or []
                if len(rows) < win + h + 50:
                    continue
                t_lim = rows[-1][0] - 730 * DAY
                step = max(1, h // 2)
                for i in range(win, len(rows) - h, step):
                    if rows[i][0] < t_lim:
                        continue
                    sd = est(rows[i - win:i + 1])
                    if sd <= 0:
                        continue
                    px = float(rows[i][4])
                    w = m.AN_Z * sd * math.sqrt(h)
                    end = float(rows[i + h][4])
                    hit = px * math.exp(-w) <= end <= px * math.exp(w)
                    ins += hit
                    tot += 1
                    wsum += (math.exp(w) - 1) * 100
                    blocks.setdefault(rows[i][0] // (7 * DAY), []).append(1 if hit else 0)
            if tot:
                b = boot([(wk * 7 * DAY, x) for wk, xs in blocks.items() for x in xs], k=500)
                RG[f"{k}|{est_nm}|{win}"] = {"in": round(100 * ins / tot, 2), "n": tot, "w": round(wsum / tot, 2), "boot": b}
                P(f"② range {k} · {est_nm} {win} candles: the price ended inside {100 * ins / tot:.1f}% of {tot} (target 80%) · width ±{wsum / tot:.2f}% · bootstrap {b}")
OUT["range"] = RG
P(f"② done · {time.time() - t2:.0f}s")

# ── ③ the tables' grading (daily, every coin): moves under 0.2%
small = tot = right_all = right_big = n_big = 0
for sym, (D, E) in F.items():
    fi = m._td_fires(D, E)
    C = D["C"]
    for i, fires in fi.items():
        if i + 1 >= D["n"] or not C[i]:
            continue
        r_ = C[i + 1] / C[i] - 1.0
        for c, s in fires.items():
            tot += 1
            ok = r_ * s > 0
            right_all += ok
            if abs(r_) < 0.002:
                small += 1
            else:
                n_big += 1
                right_big += ok
if tot:
    P(f"③ daily firings: {tot} · moved less than 0.2%: {100 * small / tot:.1f}% · right counting everything {100 * right_all / tot:.1f}% · "
      f"right without the small moves {100 * right_big / max(1, n_big):.1f}%")
    OUT["grading"] = {"tot": tot, "small": small, "acc_all": round(100 * right_all / tot, 2), "acc_big": round(100 * right_big / max(1, n_big), 2)}
json.dump(OUT, open("/tmp/holysig15.json", "w"), ensure_ascii=False, indent=1, default=str)
P(f"done · {time.time() - T0:.0f}s")
