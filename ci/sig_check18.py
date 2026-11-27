# 🔬 Holy signals check, eighteenth pass — WHAT GIVES THE RIGHT SIGNAL (v3.36.78 · p144: the engine's options), with the dashboard's own code
#    The owner (27-11): «افحص ولا تتقيد اهم شي يعطيني الاشارة الصحيحه» — after Gemini's review (one candle only · no risk measure · combos by
#    chance · old history = new · cross-group helpers). Each option of gp_walk is run on the same real prices and events:
#    · h — grade over more candles of the frame (1H: 1 · 4 · 12 · 4H: 1 · 3 · 6 · 1D: 1 · 3 · 7)
#    · win — only recent results count (1H: 30 · 60 days · 4H and 1D: 180 · 365 days)
#    · combo — none · all pairs (today) · strict pairs (each member alone ≥ its usual)
#    · help — 🤝 market-state helpers (the compass · most coins up · Bitcoin's trend · a big-volume candle)
#    · grade — «tp»: a target the size of the usual move × √h touched before the same stop
#    · and a few combinations
#    For every variant: what would have been sent (all · 1st half · 2nd half · last quarter) vs its usual · the PUSH record (the groups whose
#    own record passed the 📲 gate on the 1st half ⇒ their 2nd half, unseen) · the path of the calls (the move at the end · the worst move
#    against before it · how often it went 2% against first) · per group · per-group picking (pick the best variant on the 1st half ⇒ judge it on
#    the 2nd) · SHUFFLED prices for the default and the best variants.
#    Results: lines HOLYSIG18 + /tmp/holysig18.json. Public data only — no keys, no orders, no notifications.
#    python3 ci/sig_check18.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig18_")
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
DAY = 86400
DRY = os.environ.get("SIG18_DRY") == "1"
OUT = {"version": m.APP_VERSION, "rule": m.GP_P, "hist": m.GP_HIST, "frames": {}}


def P(*a):
    print("HOLYSIG18", *a, flush=True)


EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
VAR = {
    "1H": [("default", {}), ("h4", {"h": 4}), ("h12", {"h": 12}), ("win30", {"win": 30}), ("win60", {"win": 60}), ("nocombo", {"combo": 0}),
           ("strict", {"combo": 2}), ("help", {"help": 1}), ("tp", {"grade": "tp"}), ("tp h4", {"grade": "tp", "h": 4}),
           ("help strict", {"help": 1, "combo": 2}), ("help h4", {"help": 1, "h": 4}), ("help strict tp h4", {"help": 1, "combo": 2, "grade": "tp", "h": 4})],
    "4H": [("default", {}), ("h3", {"h": 3}), ("h6", {"h": 6}), ("win180", {"win": 180}), ("win365", {"win": 365}), ("nocombo", {"combo": 0}),
           ("strict", {"combo": 2}), ("help", {"help": 1}), ("tp", {"grade": "tp"}), ("tp h3", {"grade": "tp", "h": 3}),
           ("help strict", {"help": 1, "combo": 2}), ("help h3", {"help": 1, "h": 3}), ("help strict tp h3", {"help": 1, "combo": 2, "grade": "tp", "h": 3}),
           ("help strict win365", {"help": 1, "combo": 2, "win": 365})],
    "1D": [("default", {}), ("h3", {"h": 3}), ("h7", {"h": 7}), ("win180", {"win": 180}), ("win365", {"win": 365}), ("nocombo", {"combo": 0}),
           ("strict", {"combo": 2}), ("help", {"help": 1}), ("tp", {"grade": "tp"}), ("tp h3", {"grade": "tp", "h": 3}),
           ("help strict", {"help": 1, "combo": 2}), ("help h3", {"help": 1, "h": 3}), ("help strict tp h3", {"help": 1, "combo": 2, "grade": "tp", "h": 3}),
           ("help strict win365", {"help": 1, "combo": 2, "win": 365})],
}
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· default rule", m.GP_P, "· history", m.GP_HIST)

# ── the prices and readings (public)
if DRY:
    COINS = COINS[:12]
    rnd0 = random.Random(3)
    now_ = int(time.time())
    cdb = {"c1": {}, "c4": {}, "c": {}}
    for sec, step, n in (("c1", 3600, 900), ("c4", 14400, 900), ("c", DAY, 900)):
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
    m.GP_HIST.update({"1H": 700, "4H": 700, "1D": 800})
    VAR = {fr: v[:3] + v[7:9] for fr, v in VAR.items()}
else:
    m.SG_N["1H"], m.SG_N["4H"] = m.GP_HIST["1H"], m.GP_HIST["4H"]
    cdb = {}
    m._sg_refresh(COINS, ["1H", "4H", "1D"], cdb)
    db, now = {}, time.time()
    ccys = [c.split("-")[0] for c in COINS]
    for fn, args in (("_pro_vix", ()), ("_pro_dxy", ()), ("_pro_us10", ()), ("_pro_epu", ()), ("_pro_gpr", ()), ("_pro_tone", ()), ("_pro_ls", (ccys,)),
                     ("_pro_tk", (ccys,)), ("_pro_pc", ()), ("_pro_mv", (["BTC"],)), ("_pro_oi", (ccys,)), ("_pro_top", (ccys,)), ("_pro_fund", (ccys,)),
                     ("_pro_cbp", ()), ("_pro_stb", ()), ("_pro_cal", ())):
        try:
            getattr(m, fn)(db, now, *args)
        except Exception as ex:
            P(fn, "error", type(ex).__name__, ex)
    fdb = {}
    try:
        m._fc_fng(fdb)
    except Exception as ex:
        P("fng error", ex)
P(f"data · {time.time() - T0:.0f}s · " + " · ".join(f"{sec} {sum(1 for e in (cdb.get(sec) or {}).values() if len(e.get('d') or []) > 300)} coins" for sec in ("c1", "c4", "c")))


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


def events(cdb_, fr):
    mkt, fng = m._sg_mkt(db, fdb, cdb_), m._sg_fng_raw(fdb)
    bd = ((cdb_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    btcd = {int(r[0]): float(r[4]) for r in bd}
    sec_ = m.SG_BAR[fr][0]
    F = {}
    for sym in COINS:
        rd = ((cdb_.get("c") or {}).get(sym) or {}).get("d") or []
        rows = (((cdb_.get(sec_) or {}).get(sym) or {}).get("d") or [])[-m.GP_HIST[fr]:]
        if len(rows) < 300 or len(rd) < 220:
            continue
        F[sym] = m._sg_events(rows, fr == "1D", m._sg_ctx(sym, rd, db, mkt, fng, btcd), t0=210, dx=m.SG_SEC[fr])
    if "BTC-USDT" not in F:
        return None, None, None
    m._gp_wide({fr: F}, full=True)
    Db = F["BTC-USDT"][0]
    return F, {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}, m._gp_states(F, fr, cdb_)


def zs(w, n, b):
    pb = b / n if n else 0.5
    return (w - b) / math.sqrt(n * pb * (1 - pb)) if n and 0 < pb < 1 else 0.0


def fmt(sc):
    w, n, b = sc[:3]
    return f"{100 * w / n:.1f}% of {n} (usual {100 * b / n:.1f}% · lift {100 * (w - b) / n:+.1f} · z {zs(w, n, b):+.1f})" if n else "— (none)"


def add(a, b):
    for j in range(3):
        a[j] += b[j]


def pst(x):
    return f"path n {x[0]} · end {x[1]:+.2f}% · worst against {x[2]:+.2f}% · best with {x[3]:+.2f}% · went −2% first {x[4]:.0f}%" if x[0] else "path —"


def run(F, B, St, fr, p):
    """one variant on one frame: the coin and the market walks ⇒ per group: sent (all · halves · last quarter) · gate · path"""
    res = {}
    for sec in ("coin", "mkt"):
        FF = F if sec == "coin" else {"BTC-USDT": F["BTC-USDT"]}
        W = m.gp_walk(FF, sec, fr, B=B, p=p, S=St)
        tl = W["t"]
        for g, S_ in W["sent"].items():
            t1 = S_[0][0] if S_ else tl
            mid, q4 = t1 + (tl - t1) // 2, tl - (tl - t1) // 4
            pa = W["path"][g]
            h1 = m.gp_score(S_, 0, mid)
            res[g] = {"all": m.gp_score(S_), "h1": h1, "h2": m.gp_score(S_, mid), "q4": m.gp_score(S_, q4),
                      "gate": h1[1] >= 30 and h1[0] / h1[1] >= h1[2] / h1[1] + m.GP_SAY,
                      "px2": m.gp_pathst(pa, S_, mid), "pxa": m.gp_pathst(pa), "ch": W["champ"][g], "job": m.GP_GROUPS[g]["job"]}
    return res


def pooled(res, key, only=None):
    a = [0, 0, 0.0]
    for g, x in res.items():
        if only is None or only(g, x):
            add(a, x[key])
    return a


def pxpool(res, only=None):
    n = s1 = s2 = s3 = s4 = 0.0
    for g, x in res.items():
        if (only is None or only(g, x)) and x["px2"][0]:
            k = x["px2"][0]
            n += k
            s1 += x["px2"][1] * k
            s2 += x["px2"][2] * k
            s3 += x["px2"][3] * k
            s4 += x["px2"][4] * k
    return [int(n), s1 / n, s2 / n, s3 / n, s4 / n] if n else [0, 0, 0, 0, 0]


for fr in m.GP_FR:
    t1 = time.time()
    F, B, St = events(cdb, fr)
    if not F:
        P(f"{fr}: no Bitcoin — skipped")
        continue
    P(f"{fr}: events for {len(F)} coins · states {({k: len(v) for k, v in St.items()})} · {time.time() - t1:.0f}s")
    RES = {}
    for vn, vp in VAR[fr]:
        t2 = time.time()
        res = run(F, B, St, fr, vp)
        RES[vn] = res
        push = pooled(res, "h2", lambda g, x: x["gate"])
        P(f"① {fr} [{vn}] ALL {fmt(pooled(res, 'all'))} · 2nd half {fmt(pooled(res, 'h2'))} · last quarter {fmt(pooled(res, 'q4'))} · {time.time() - t2:.0f}s")
        P(f"①   {fr} [{vn}] 📲 PUSH (gate on the 1st half ⇒ 2nd half): {fmt(push)} · groups {[g for g, x in res.items() if x['gate']]} · "
          f"{pst(pxpool(res, lambda g, x: x['gate'] and x['job'] == 'dir'))}")
        P(f"①   {fr} [{vn}] direction groups 2nd half: {fmt(pooled(res, 'h2', lambda g, x: x['job'] == 'dir'))} · {pst(pxpool(res, lambda g, x: x['job'] == 'dir'))}")
    groups = sorted(next(iter(RES.values())).keys())
    for g in groups:
        P(f"② {fr} {m.GP_GROUPS[g]['ic']} {g}: " + " ‖ ".join(f"{vn} {fmt(RES[vn][g]['h2']).split(' (')[0]} (lift {100 * (RES[vn][g]['h2'][0] - RES[vn][g]['h2'][2]) / max(1, RES[vn][g]['h2'][1]):+.1f})"
                                                              for vn, _ in VAR[fr]))
    # per-group picking: the best variant on the 1st half (≥ 30 calls, lift) ⇒ its 2nd half
    pick, pickd = [0, 0, 0.0], {}
    for g in groups:
        cands = [(vn, RES[vn][g]) for vn, _ in VAR[fr] if RES[vn][g]["h1"][1] >= 30]
        if not cands:
            continue
        vn, x = max(cands, key=lambda c: (c[1]["h1"][0] - c[1]["h1"][2]) / c[1]["h1"][1])
        pickd[g] = vn
        if (x["h1"][0] - x["h1"][2]) / x["h1"][1] >= m.GP_SAY:
            add(pick, x["h2"])
    P(f"③ {fr} per-group PICK on the 1st half ⇒ 2nd half (only the picks that pass the gate): {fmt(pick)} · picks {pickd}")
    best = sorted(((vn, pooled(RES[vn], 'h2', lambda g, x: x['gate'])) for vn, _ in VAR[fr]), key=lambda v: -(v[1][0] - v[1][2]) / max(1, v[1][1]))[:2]
    OUT["frames"][fr] = {vn: {g: {k: v for k, v in x.items()} for g, x in r.items()} for vn, r in RES.items()}
    F = RES = None
    # shuffled prices: the default and the two best PUSH variants
    sdb = shuffled(cdb, 1)
    Fs, Bs, Ss = events(sdb, fr)
    if Fs:
        for vn, vp in [v for v in VAR[fr] if v[0] in ("default",) + tuple(b[0] for b in best)]:
            rs = run(Fs, Bs, Ss, fr, vp)
            P(f"④ {fr} SHUFFLED [{vn}] ALL {fmt(pooled(rs, 'all'))} · 2nd half {fmt(pooled(rs, 'h2'))} · 📲 PUSH {fmt(pooled(rs, 'h2', lambda g, x: x['gate']))}")
    P(f"{fr} done · {time.time() - T0:.0f}s")
json.dump(OUT, open("/tmp/holysig18.json", "w"), ensure_ascii=False, default=str)
P(f"DONE · {time.time() - T0:.0f}s")
