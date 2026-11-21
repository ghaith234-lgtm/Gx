# 🔬 Holy signals check, sixteenth pass — the indicator GROUPS, with the dashboard's OWN code (v3.36.77 · p138: gp_walk · gp_pack · _gp_wide)
#    The owner (21-11): «قسمين للعملات وللسوق … كل مجموعه تختص باشعار … تصنف التجارب على اختباراتك … الاشعارات فقط ساعه ٤ ساعات يوم
#    … واهم شي الاختبار»
#    ① every group (🪙 8 coin groups graded on each coin's price · 🌐 7 market groups graded on Bitcoin) on every frame (1H · 4H · 1D):
#       the record of WHAT WOULD HAVE BEEN SENT (champions picked only from what was known at the time) vs its usual (a random call with the
#       same sides on the same candles) · first half · second half · the last quarter · z · the champions now · the best members
#    ② the pre-registered rule (dmin 30 · lift 5% · gap 2% · cap 2 · combos on) vs variants (no combos · dmin 20/50 · lift 3/8% · cap 1/3 ·
#       no gap) — pooled over the groups, all and second half only (the variants are shown, NOT picked: the rule was fixed before this run)
#    ③ the «📲 only when the group itself is proven» gate (≥ usual + 3% on ≥ 30 before the middle) ⇒ how did the gated groups do AFTER the
#       middle (unseen) vs the others
#    ④ the dashboard's history (1H 2160 · 4H 3000 · 1D 2600) vs a longer one (1H 8760 · 4H 4400)
#    ⑤ the same walk on SHUFFLED prices (no information) ⇒ the sent record must sit at its usual
#    ⑥ the new data sources (probe only — what history each one serves): OKX open interest · top traders · quarterly futures + index ·
#       funding · Coinbase · stablecoins · the US calendar
#    Results: lines HOLYSIG16 + /tmp/holysig16.json. Public market data only — no keys, no orders, no notifications.
#    python3 ci/sig_check16.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig16_")
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
DRY = os.environ.get("SIG16_DRY") == "1"
OUT = {"version": m.APP_VERSION, "rule": m.GP_P, "hist": m.GP_HIST, "groups": {}, "variants": {}, "probe": {}}


def P(*a):
    print("HOLYSIG16", *a, flush=True)


EXTRA = ["TON-USDT", "PEPE-USDT", "FET-USDT", "CRV-USDT", "LDO-USDT", "IMX-USDT", "GRT-USDT", "ALGO-USDT", "SAND-USDT", "MANA-USDT",
         "AXS-USDT", "EOS-USDT"]
COINS = list(dict.fromkeys(list(m.MKT_COINS) + EXTRA))
LONG = {"1H": 8760, "4H": 4400, "1D": 2600}
P("dashboard", m.APP_VERSION, "· coins", len(COINS), "· rule", m.GP_P, "· history", m.GP_HIST, "· longer", LONG)


# ── ⑥ probes first (cheap) — what each new source serves
def probe():
    import requests
    S = requests.Session()
    S.headers["User-Agent"] = "holy-check"

    def get(url):
        try:
            r = S.get(url, timeout=25)
            return r.status_code, (r.json() if "json" in r.headers.get("content-type", "") or r.text[:1] in "[{" else r.text[:200])
        except Exception as ex:
            return None, f"{type(ex).__name__}: {ex}"

    def okx(path):
        code, j = get("https://www.okx.com" + path)
        d = (j.get("data") if isinstance(j, dict) else None) or []
        return code, (j.get("code") if isinstance(j, dict) else None), d

    def span(rows, k=0, div=1000):
        ts = []
        for x in rows:
            try:
                ts.append(int(float(x[k] if isinstance(x, (list, tuple)) else x.get(k))) // div)
            except Exception:
                pass
        return (len(rows), time.strftime("%Y-%m-%d", time.gmtime(min(ts))), time.strftime("%Y-%m-%d", time.gmtime(max(ts)))) if ts else (len(rows), None, None)
    pr = {}
    for nm, path, k in (("oi_hist_1D", "/api/v5/rubik/stat/contracts/open-interest-history?instId=BTC-USDT-SWAP&period=1D&limit=100", 0),
                        ("oi_hist_1H", "/api/v5/rubik/stat/contracts/open-interest-history?instId=BTC-USDT-SWAP&period=1H&limit=100", 0),
                        ("oi_vol_1D", "/api/v5/rubik/stat/contracts/open-interest-volume?ccy=BTC&period=1D", 0),
                        ("top_acct_1D", "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader?instId=BTC-USDT-SWAP&period=1D", 0),
                        ("top_pos_1D", "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader?instId=BTC-USDT-SWAP&period=1D", 0),
                        ("ls_acct_1D", "/api/v5/rubik/stat/contracts/long-short-account-ratio?ccy=BTC&period=1D", 0),
                        ("index_1D", "/api/v5/market/history-index-candles?instId=BTC-USDT&bar=1D&limit=100", 0),
                        ("fund_hist", "/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=100", "fundingTime")):
        code, c, d = okx(path)
        pr[nm] = {"http": code, "code": c, "span": span(d, k), "sample": d[:1]}
        P(f"⑥ {nm}: http {code} · code {c} · rows/first/last {pr[nm]['span']} · sample {json.dumps(d[:1])[:160]}")
        time.sleep(0.3)
    # paging depth (how far back): OI history 1D · top traders 1D · funding
    for nm, base, k, key in (("oi_hist_1D", "/api/v5/rubik/stat/contracts/open-interest-history?instId=BTC-USDT-SWAP&period=1D&limit=100", 0, "end"),
                             ("top_pos_1D", "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader?instId=BTC-USDT-SWAP&period=1D&limit=100", 0, "end"),
                             ("fund_hist", "/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=100", "fundingTime", "after")):
        allr, cur = [], None
        for _ in range(40):
            code, c, d = okx(base + (f"&{key}={cur}" if cur else ""))
            if not d:
                break
            allr += d
            last = d[-1][k] if isinstance(d[-1], list) else d[-1].get(k)
            if cur == last:
                break
            cur = last
            time.sleep(0.25)
        pr[nm + "_deep"] = span(allr, k)
        P(f"⑥ {nm} paged back: rows/first/last {pr[nm + '_deep']}")
    # quarterly futures: the instruments · the current quarter's candles · an expired contract's candles
    code, c, d = okx("/api/v5/public/instruments?instType=FUTURES&instFamily=BTC-USDT")
    fut = sorted([(x.get("alias"), x.get("instId"), x.get("expTime")) for x in d], key=lambda x: x[2] or "")
    pr["futures"] = fut
    P(f"⑥ futures BTC-USDT: {fut}")
    q = next((x[1] for x in fut if x[0] == "quarter"), None)
    if q:
        code, c, d = okx(f"/api/v5/market/history-candles?instId={q}&bar=1D&limit=100")
        pr["quarter_candles"] = span(d)
        P(f"⑥ quarter {q} daily candles: {pr['quarter_candles']}")
        code, c, d = okx(f"/api/v5/market/ticker?instId={q}")
        code2, c2, d2 = okx("/api/v5/market/index-tickers?instId=BTC-USDT")
        try:
            fp, ip = float(d[0]["last"]), float(d2[0]["idxPx"])
            P(f"⑥ quarter premium now: {100 * (fp / ip - 1):.3f}% (future {fp} · index {ip})")
        except Exception as ex:
            P("⑥ quarter premium now: error", ex)
    for old in ("BTC-USDT-250926", "BTC-USDT-250627", "BTC-USD-250926"):
        code, c, d = okx(f"/api/v5/market/history-candles?instId={old}&bar=1D&limit=100")
        pr["expired_" + old] = {"code": c, "span": span(d)}
        P(f"⑥ expired {old} candles: code {c} · {span(d)}")
        time.sleep(0.3)
    # Coinbase · stablecoins · the calendar
    code, j = get("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400")
    pr["coinbase_1D"] = {"http": code, "span": span(j if isinstance(j, list) else [], 0, 1)}
    P(f"⑥ coinbase BTC-USD daily: http {code} · {pr['coinbase_1D']['span']}")
    end = int(time.time()) - 2000 * DAY
    code, j = get(f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400&start={time.strftime('%Y-%m-%dT00:00:00Z', time.gmtime(end))}"
                  f"&end={time.strftime('%Y-%m-%dT00:00:00Z', time.gmtime(end + 290 * DAY))}")
    pr["coinbase_old"] = {"http": code, "span": span(j if isinstance(j, list) else [], 0, 1)}
    P(f"⑥ coinbase 2000 days ago: http {code} · {pr['coinbase_old']['span']}")
    code, j = get("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600")
    pr["coinbase_1H"] = {"http": code, "span": span(j if isinstance(j, list) else [], 0, 1)}
    P(f"⑥ coinbase BTC-USD hourly: http {code} · {pr['coinbase_1H']['span']}")
    code, j = get("https://stablecoins.llama.fi/stablecoincharts/all")
    rows = j if isinstance(j, list) else []
    pr["stable"] = {"http": code, "span": span(rows, "date", 1), "last": rows[-1:] if rows else None}
    P(f"⑥ stablecoins (all, daily): http {code} · {pr['stable']['span']} · last {json.dumps(rows[-1:])[:200]}")
    code, j = get("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
    ev = [x for x in (j if isinstance(j, list) else []) if x.get("country") == "USD" and x.get("impact") in ("High", "Medium")]
    pr["calendar"] = {"http": code, "usd": len(ev), "sample": ev[:2]}
    P(f"⑥ US calendar this week: http {code} · USD high/medium {len(ev)} · {json.dumps(ev[:2], ensure_ascii=False)[:260]}")
    return pr


if not DRY:
    try:
        OUT["probe"] = probe()
    except Exception as ex:
        P("⑥ probe error", type(ex).__name__, ex)

# ── the prices (public)
if DRY:
    COINS = COINS[:12]
    rnd0 = random.Random(3)
    now_ = int(time.time())
    cdb = {"c1": {}, "c4": {}, "c": {}}
    for sec, step, n in (("c1", 3600, 1200), ("c4", 14400, 1000), ("c", DAY, 1000)):
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
    LONG = {"1H": 1200, "4H": 1000, "1D": 1000}
    m.GP_HIST.update({"1H": 700, "4H": 700, "1D": 1000})
else:
    m.SG_N["1H"], m.SG_N["4H"] = LONG["1H"], LONG["4H"]
    cdb = {}
    m._sg_refresh(COINS, ["1H", "4H", "1D"], cdb)
    db, now = {}, time.time()
    for fn in ("_pro_vix", "_pro_dxy", "_pro_us10", "_pro_epu", "_pro_gpr", "_pro_tone"):
        try:
            getattr(m, fn)(db, now)
        except Exception as ex:
            P(fn, "error", ex)
    ccys = [c.split("-")[0] for c in COINS]
    for fn, args in (("_pro_ls", (db, now, ccys)), ("_pro_tk", (db, now, ccys)), ("_pro_pc", (db, now)), ("_pro_mv", (db, now))):
        try:
            getattr(m, fn)(*args)
        except TypeError:
            try:
                getattr(m, fn)(db, now, ccys)
            except Exception as ex:
                P(fn, "error", ex)
        except Exception as ex:
            P(fn, "error", ex)
    fdb = {}
    try:
        m._fc_fng(fdb)
    except Exception as ex:
        P("fng error", ex)
P(f"prices fetched · {time.time() - T0:.0f}s · " + " · ".join(f"{sec} {sum(1 for e in (cdb.get(sec) or {}).values() if len(e.get('d') or []) > 300)} coins "
                                                          f"(BTC {len(((cdb.get(sec) or {}).get('BTC-USDT') or {}).get('d') or [])})" for sec in ("c1", "c4", "c")))


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


def events(cdb_, fr, hist):
    """the dashboard's gp_build, frame by frame, returning the events (to walk several rules on the same events)"""
    mkt, fng = m._sg_mkt(db, fdb), m._sg_fng_raw(fdb)
    bd = ((cdb_.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    btcd = {int(r[0]): float(r[4]) for r in bd}
    sec_ = m.SG_BAR[fr][0]
    F = {}
    for sym in COINS:
        rd = ((cdb_.get("c") or {}).get(sym) or {}).get("d") or []
        rows = (((cdb_.get(sec_) or {}).get(sym) or {}).get("d") or [])[-hist:]
        if len(rows) < 300 or len(rd) < 220:
            continue
        F[sym] = m._sg_events(rows, fr == "1D", m._sg_ctx(sym, rd, db, mkt, fng, btcd), t0=210, dx=m.SG_SEC[fr])
    if "BTC-USDT" not in F:
        return None, None
    m._gp_wide({fr: F}, full=True)
    Db = F["BTC-USDT"][0]
    return F, {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}


def walks(F, B, fr, p=None):
    return {"coin": m.gp_walk(F, "coin", fr, B=B, p=p), "mkt": m.gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=p)}


def zs(w, n, b):
    pb = b / n if n else 0.5
    return (w - b) / math.sqrt(n * pb * (1 - pb)) if n and 0 < pb < 1 else 0.0


def fmt(sc):
    w, n, b = sc
    return f"{100 * w / n:.1f}% of {n} (usual {100 * b / n:.1f}% · z {zs(w, n, b):+.1f})" if n else "— (none)"


def nm(k):
    return " + ".join((m.SB_NM.get(c) if hasattr(m, "SB_NM") else None) or (m._sg_plain(c) or [None, c])[1] for c in k.split("+"))


def report(W, fr, label, keep=True):
    """① per group: the sent record (all · halves · last quarter) · the champions now · the best members"""
    pooled = {"all": [0, 0, 0.0], "h1": [0, 0, 0.0], "h2": [0, 0, 0.0], "q4": [0, 0, 0.0]}
    rows = {}
    for sec, Ws in W.items():
        tl = Ws["t"]
        for g, S in Ws["sent"].items():
            t1 = S[0][0] if S else tl
            mid, q4 = t1 + (tl - t1) // 2, tl - (tl - t1) // 4
            sc = {"all": m.gp_score(S), "h1": m.gp_score(S, 0, mid), "h2": m.gp_score(S, mid), "q4": m.gp_score(S, q4)}
            for k, v in sc.items():
                for j in range(3):
                    pooled[k][j] += v[j]
            R = Ws["rec"][g]
            u = Ws["U"].get(m.GP_GROUPS[g]["job"], 0.5)
            mem = []
            for key, r in R.items():
                n_ = r[0] + r[1]
                if n_ < 20:
                    continue
                pb = m._gp_pb(r[4], n_, u)
                mem.append((m._sg_wlb(r[0], n_) / 100.0 - pb, key, r[0], n_, pb, r[2]))
            mem.sort(reverse=True)
            ch = [(k_, R[k_][0], R[k_][0] + R[k_][1], m._gp_pb(R[k_][4], R[k_][0] + R[k_][1], u)) for k_ in Ws["champ"][g]]
            rows[f"{sec}:{g}"] = {"sc": sc, "ch": ch, "best": [x[1:] for x in mem[:6]], "nmem": len(Ws["mem"][g]), "nkeys": len(R), "mid": mid}
            if keep:
                P(f"① {label} {fr} {m.GP_SECN[sec][1]} {m.GP_GROUPS[g]['ic']} {m.GP_GROUPS[g]['nm']} ({g} · job {m.GP_GROUPS[g]['job']} · "
                  f"{len(Ws['mem'][g])} members · {len(R)} graded incl. combos): SENT {fmt(sc['all'])} · 1st half {fmt(sc['h1'])} · 2nd half {fmt(sc['h2'])} · "
                  f"last quarter {fmt(sc['q4'])}")
                P(f"①   champions now: " + (" · ".join(f"{nm(k_)} [{k_}] {100 * w / max(1, n):.1f}% of {n} (usual {100 * pb:.1f}%)" for k_, w, n, pb in ch) or "none") +
                  " ‖ best members: " + " · ".join(f"[{k_}] {100 * w / n:.1f}% of {n} usual {100 * pb:.1f}% days {d}" for _x, k_, w, n, pb, d in mem[:4]))
    P(f"① {label} {fr} POOLED over all groups: SENT {fmt(pooled['all'])} · 1st half {fmt(pooled['h1'])} · 2nd half {fmt(pooled['h2'])} · last quarter {fmt(pooled['q4'])}")
    return rows, pooled


def gate(rows):
    """③ the 📲 gate decided on the first half ⇒ how the gated groups did on the second half (unseen)"""
    a, b = [0, 0, 0.0], [0, 0, 0.0]
    names = []
    for k, x in rows.items():
        h1, h2 = x["sc"]["h1"], x["sc"]["h2"]
        passed = h1[1] >= 30 and h1[0] / h1[1] >= h1[2] / h1[1] + m.GP_SAY
        tgt = a if passed else b
        for j in range(3):
            tgt[j] += h2[j]
        if passed:
            names.append(k)
    return a, b, names


ALL = {}
for fr in m.GP_FR:
    t1 = time.time()
    for hl, hist in (("dash", m.GP_HIST[fr]), ("long", LONG[fr])):
        if hl == "long" and hist == m.GP_HIST[fr]:
            continue
        F, B = events(cdb, fr, hist)
        if not F:
            P(f"{fr} {hl}: no Bitcoin — skipped")
            continue
        P(f"{fr} {hl}: events for {len(F)} coins on {hist} candles · {time.time() - t1:.0f}s")
        W = walks(F, B, fr)
        rows, pooled = report(W, fr, hl)
        a, b, names = gate(rows)
        P(f"③ {hl} {fr} the 📲 gate (decided on the 1st half): passed {len(names)} groups {names} ⇒ 2nd half {fmt(a)} · the others ⇒ {fmt(b)}")
        OUT["groups"][f"{fr}:{hl}"] = {"rows": rows, "pooled": pooled, "gate": {"pass": a, "fail": b, "names": names}}
        if hl == "dash":
            ALL[fr] = (F, B)
            var = {}
            for vn, vp in (("default", None), ("no combos", {"combo": 0}), ("dmin 20", {"dmin": 20}), ("dmin 50", {"dmin": 50}), ("lift 3%", {"lift": 0.03}),
                           ("lift 8%", {"lift": 0.08}), ("cap 1", {"cap": 1}), ("cap 3", {"cap": 3}), ("no gap", {"gap": m.GP_P["lift"]})):
                Wv = W if vp is None else walks(F, B, fr, vp)
                _r, pv = report(Wv, fr, "variant " + vn, keep=False)
                var[vn] = pv
                P(f"② {fr} variant {vn}: SENT {fmt(pv['all'])} · 2nd half {fmt(pv['h2'])} · last quarter {fmt(pv['q4'])}")
            OUT["variants"][fr] = var
        F = W = None
    P(f"{fr} done · {time.time() - T0:.0f}s")

# ── ⑤ shuffled prices (the dashboard's history) ⇒ the sent record must sit at its usual
for seed in ((1,) if DRY else (1, 2)):
    sdb = shuffled(cdb, seed)
    for fr in m.GP_FR:
        F, B = events(sdb, fr, m.GP_HIST[fr])
        if not F:
            continue
        _r, pv = report(walks(F, B, fr), fr, f"SHUFFLED#{seed}", keep=False)
        OUT.setdefault("shuffled", {})[f"{fr}#{seed}"] = pv
        P(f"⑤ SHUFFLED#{seed} {fr}: SENT {fmt(pv['all'])} · 2nd half {fmt(pv['h2'])}")
json.dump(OUT, open("/tmp/holysig16.json", "w"), ensure_ascii=False, indent=1, default=str)
P(f"DONE · {time.time() - T0:.0f}s")
