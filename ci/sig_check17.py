# 🔬 Holy signals check, seventeenth pass — the NEW data inside the groups, with the dashboard's OWN code (v3.36.77 · p142)
#    The owner (21-11): «وهذه ضيفها : بيانات العقود (التمويل، العقود المفتوحة، العلاوة الفصلية، مراكز الكبار)، وعلاوة كوينبيس، والعملات
#    المستقرة، وتقويم الأخبار الأمريكية … واهم شي الاختبار»
#    ① the dashboard's fetchers on the real public sources (OKX open interest · top traders · funding · the quarterly premium · Coinbase ·
#       DefiLlama · the calendar) ⇒ how much history each one gives
#    ② every new member graded on its group's job at the next candle (1H · 4H · 1D) in time order — its record vs its usual, its days, and
#       whether it became a champion (gp_walk · pooled over the coins for 🏦 of the coin · Bitcoin for 🏦 and 🎢 of the market)
#    ③ the derivatives groups with and without the new members (what would have been sent) · the same on SHUFFLED prices (the readings no
#       longer match the prices ⇒ the record must fall to its usual)
#    Results: lines HOLYSIG17 + /tmp/holysig17.json. Public data only — no keys, no orders, no notifications.
#    python3 ci/sig_check17.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig17_")
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
NEW = ("P-oi", "P-top", "P-fund", "P-basis", "M-cbp", "M-stb", "M-cal")
GROUPS = ("c_pro", "m_pro", "m_vol")
OUT = {"version": m.APP_VERSION, "rule": m.GP_P, "hist": m.GP_HIST, "sources": {}, "members": {}, "groups": {}}


def P(*a):
    print("HOLYSIG17", *a, flush=True)


EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
CCY = [c.split("-")[0] for c in COINS]
m.PRO_KEEP = 3000                                              # the whole history the sources give (the dashboard keeps 800 days)
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· groups", GROUPS, "· new members", NEW)

# ── ① the sources (the dashboard's own fetchers)
db, now = {}, time.time()
for fn, args in (("_pro_ls", (CCY,)), ("_pro_tk", (CCY,)), ("_pro_pc", ()), ("_pro_mv", (["BTC"],)), ("_pro_oi", (CCY,)), ("_pro_top", (CCY,)),
                 ("_pro_fund", (CCY,)), ("_pro_basis", ()), ("_pro_cbp", ()), ("_pro_stb", ()), ("_pro_cal", ())):
    t1 = time.time()
    try:
        getattr(m, fn)(db, now, *args)
    except Exception as ex:
        P(f"① {fn} error {type(ex).__name__}: {ex}")
    P(f"① {fn} · {time.time() - t1:.0f}s")


def span(d):
    ks = sorted(int(k) for k in (d or {}))
    return (len(ks), time.strftime("%Y-%m-%d", time.gmtime(ks[0])), time.strftime("%Y-%m-%d", time.gmtime(ks[-1]))) if ks else (0, None, None)


for k in ("oi", "top", "fund", "ls", "tk"):
    per = {c: span((db.get(k) or {}).get(c, {}).get("d")) for c in CCY}
    have = {c: v for c, v in per.items() if v[0]}
    OUT["sources"][k] = per
    P(f"① {k}: {len(have)} of {len(CCY)} coins · BTC {per.get('BTC')} · median days {sorted(v[0] for v in have.values())[len(have) // 2] if have else 0}")
for k in ("cbp", "stb"):
    OUT["sources"][k] = span((db.get(k) or {}).get("d"))
    P(f"① {k}: {OUT['sources'][k]}")
OUT["sources"]["basis"] = {c: (db.get("basis") or {}).get(c, {}).get("d") for c in m.PRO_BIG}
P(f"① basis (a snapshot from now on): {OUT['sources']['basis']}")
ev = [x for x in ((db.get("cal") or {}).get("ev") or []) if x.get("im") == "h"]
OUT["sources"]["cal"] = len(ev)
P(f"① the calendar: {len(ev)} high-impact US releases known (this week — the history grows with the dashboard)")

# ── the prices
m.SG_N["1H"], m.SG_N["4H"] = m.GP_HIST["1H"], max(m.GP_HIST["4H"], 3000)
cdb = {}
m._sg_refresh(COINS, ["1H", "4H", "1D"], cdb)
P(f"prices · {time.time() - T0:.0f}s · " + " · ".join(f"{sec} {sum(1 for e in (cdb.get(sec) or {}).values() if len(e.get('d') or []) > 300)} coins" for sec in ("c1", "c4", "c")))


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
    mkt, fng = m._sg_mkt(db, {}, cdb_), None
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
        return None, None
    m._gp_wide({fr: F}, full=True)
    Db = F["BTC-USDT"][0]
    return F, {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}


def zs(w, n, b):
    pb = b / n if n else 0.5
    return (w - b) / math.sqrt(n * pb * (1 - pb)) if n and 0 < pb < 1 else 0.0


def fmt(sc):
    w, n, b = sc
    return f"{100 * w / n:.1f}% of {n} (usual {100 * b / n:.1f}% · z {zs(w, n, b):+.1f})" if n else "— (none)"


def walk(F, B, fr, codes=None):
    out = {}
    for g in GROUPS:
        sec = m.GP_GROUPS[g]["sec"]
        FF = F if sec == "coin" else {"BTC-USDT": F["BTC-USDT"]}
        W = m.gp_walk(FF, sec, fr, B=B, codes=codes, groups=[g])
        out[g] = W
    return out


ALLC = m._gp_codes()
OLDC = {c: f for c, f in ALLC.items() if c not in NEW}
for fr in m.GP_FR:
    t1 = time.time()
    F, B = events(cdb, fr)
    if not F:
        P(f"{fr}: no Bitcoin — skipped")
        continue
    tot = {c: sum(len(v) for D, E in F.values() for (k, s), v in E.items() if k == c) for c in NEW}
    P(f"② {fr}: events for {len(F)} coins · {time.time() - t1:.0f}s · firings of the new members (all coins): {tot}")
    Wn = walk(F, B, fr)
    Wo = walk(F, B, fr, codes=OLDC)
    for g in GROUPS:
        W = Wn[g]
        R_ = W["rec"][g]
        u = W["U"].get(m.GP_GROUPS[g]["job"], 0.5)
        for c in NEW:
            if c not in W["mem"][g]:
                continue
            r = R_.get(c)
            st = "⭐ champion" if c in W["champ"][g] else "✅ proven" if c in W["on"][g] else "—"
            if r and r[0] + r[1]:
                n_ = r[0] + r[1]
                pb = m._gp_pb(r[4], n_, u)
                P(f"② {fr} {g} {c} {m.GP_NM.get(c)}: {100 * r[0] / n_:.1f}% of {n_} (usual {100 * pb:.1f}% · Wilson low {m._sg_wlb(r[0], n_):.1f}%) · {r[2]} days · {st}")
                OUT["members"][f"{fr}:{g}:{c}"] = {"w": r[0], "n": n_, "pb": round(pb, 4), "days": r[2], "st": st}
            else:
                P(f"② {fr} {g} {c} {m.GP_NM.get(c)}: no graded firing")
        combos = sorted(((k, r) for k, r in R_.items() if "+" in k and any(x in NEW for x in k.split("+")) and r[0] + r[1] >= 20),
                        key=lambda kr: -(m._sg_wlb(kr[1][0], kr[1][0] + kr[1][1]) - 100 * m._gp_pb(kr[1][4], kr[1][0] + kr[1][1], u)))[:3]
        if combos:
            P(f"② {fr} {g} best combos with a new member: " + " · ".join(f"[{k}] {100 * r[0] / (r[0] + r[1]):.1f}% of {r[0] + r[1]}" for k, r in combos))
        so, sn = m.gp_score(Wo[g]["sent"][g]), m.gp_score(W["sent"][g])
        P(f"③ {fr} {g} what would have been sent: WITHOUT the new members {fmt(so)} · WITH them {fmt(sn)} · champions now {W['champ'][g]}")
        OUT["groups"][f"{fr}:{g}"] = {"without": so, "with": sn, "champ": W["champ"][g]}
    F = Wn = Wo = None
    sdb = shuffled(cdb, 1)
    Fs, Bs = events(sdb, fr)
    if Fs:
        Ws = walk(Fs, Bs, fr)
        for g in GROUPS:
            ss = m.gp_score(Ws[g]["sent"][g])
            nm_ = {c: (Ws[g]["rec"][g].get(c) or [0, 0])[:2] for c in NEW if c in Ws[g]["mem"][g]}
            P(f"③ {fr} {g} SHUFFLED prices: sent {fmt(ss)} · new members {nm_}")
            OUT["groups"][f"{fr}:{g}"]["shuffled"] = ss
    P(f"{fr} done · {time.time() - T0:.0f}s")
json.dump(OUT, open("/tmp/holysig17.json", "w"), ensure_ascii=False, indent=1, default=str)
P(f"DONE · {time.time() - T0:.0f}s")
