# 🧠 patch 115 (dashboard v3.36.69 · the analyst's engine). The owner (20-11): «ابدي» — after ci/sig_check11.py (run 44794372408):
#   «مؤشرات محددة دائماً إذا اتفقت طلع توقعها صحيح» · «بدون أسبوع خلي الشهر التالي» · the 4-hour forecasts measured worse than luck.
#   · the horizons: the 4-hour frame is judged after ONE DAY (6 candles) = «غداً» · the daily frame after 30 DAYS = «الشهر القادم» (was
#     3 days and a week) · the daily history goes back ~7 years (2600 candles) so a month has enough separate cases — a coin already saved
#     with a shorter history is filled backwards once (page by page, public data)
#   · the catalog search (_sg_search) is rebuilt on the owner's rule: a combination counts only when ALL its signals say the same direction
#     and NONE of the other direction is on · the history is cut into 4 equal periods and a combination is «proven» (c4) only if it beats
#     random (hit AND average) in EVERY one of the four, with enough cases and ≥ 3 separate windows in each (a day for «غداً» · 30 days for
#     the month) · its accuracy (1–100) is its hit over the whole history · single signals stay listed (with their %) but only proven ones
#     can notify · no 💎 «rare» any more (a handful of cases can never be proven in four periods)
#   · ONE rule for the history and for the live record (_sg_out): a target and a stop from the coin's own volatility just before the entry
#     (the spread of its candle moves × √horizon) ⇒ ✅ the target first · ❌ the stop first (both in one candle ⇒ ❌, the careful reading) ·
#     neither by the end ⇒ ✅ if it moved the right way after the fee
#   · the catalog version 3 ⇒ rebuilt by itself
#   python3 devtests/step/patches/p115_analyst_engine.py Holy_Dashboard.pyw
import os, sys

NEW_SEARCH = r'''def _sg_sig(C, h, w=SG_W):
    """📏 تذبذب العملة قبل كل شمعة: انحراف عوائد الشمعة الواحدة (آخر w شمعة) × √المدة ⇒ بُعد الهدف والوقف (محصور 0.4% … 40%)"""
    n = len(C)
    out = [0.0] * n
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, n)]
    s1 = s2 = 0.0
    for i in range(1, n):
        s1 += lr[i]
        s2 += lr[i] * lr[i]
        if i > w:
            s1 -= lr[i - w]
            s2 -= lr[i - w] * lr[i - w]
        if i >= w:
            var = max(0.0, (s2 - s1 * s1 / w) / (w - 1))
            out[i] = min(0.4, max(0.004, math.sqrt(var) * math.sqrt(h)))
    return out


def _sg_out(H, L, C, i, h, side, s, p=None):
    """🎯 الحكم (التاريخ والسجل الحي بقاعدة واحدة): الهدف قبل الوقف ⇒ ربح بُعده · الوقف أولاً (أو كلاهما بالشمعة نفسها) ⇒ خسارة بُعده ·
    لا هذا ولا ذاك حتى نهاية المدة ⇒ حركة السعر · كله بعد العمولة"""
    if i + h >= len(C):
        return None
    p = p or C[i]
    if p <= 0 or C[i + h] <= 0:
        return None
    if s and s > 0:
        up, dn = p * (1 + s), p * (1 - s)
        for j in range(i + 1, i + h + 1):
            if side > 0:
                if L[j] <= dn:
                    return -s - SG_FEE
                if H[j] >= up:
                    return s - SG_FEE
            else:
                if H[j] >= up:
                    return -s - SG_FEE
                if L[j] <= dn:
                    return s - SG_FEE
    r = C[i + h] / p - 1.0 if side > 0 else p / C[i + h] - 1.0
    return r - SG_FEE


def _sg_search(COIN, prog=None):
    """🔎 (v3.36.69 · المحلل) كل إشارة وحدها + التركيبات (2 … 6 معاً · كلها بالجهة نفسها ولا إشارة من الجهة المعاكسة) — التاريخ 4 فترات
    متساوية · «مثبتة» (c4) فقط إذا غلبت العشوائي (النسبة والمتوسط) في كل فترة بحالات كافية و≥ 3 نوافذ مستقلة (نفس ci/sig_check11.py) ·
    الحكم بالهدف والوقف (_sg_out) · الدقة = نسبة الصح على كل التاريخ"""
    names = list(COIN)
    PRE, BND = {}, {}
    for fr in SG_FR:
        k0 = 0 if fr == "4H" else 2
        vs = [v[k0] for v in COIN.values() if v[k0]["n"] > 260]
        t0 = min(D["T"][210] for D in vs)
        t1 = max(D["T"][-1] for D in vs)
        BND[fr] = [t0 + (t1 - t0) * q / 4.0 for q in (1, 2, 3)]
    for sym, v in COIN.items():
        for fr, D, E in (("4H", v[0], v[1]), ("1D", v[2], v[3])):
            h, lk = SG_HZ[fr], SG_LK[fr]
            act = {k: set(j for i in lst for j in range(i, min(D["n"], i + lk))) for k, lst in E.items() if lst}
            opp = {1: set(), -1: set()}
            for (code, sd), st_ in act.items():
                if code != "W-crash":                 # 🌊 الانهيار قراءة بالجهتين (ارتداد أو استمرار) — ليس «ضد» نفسه
                    opp[sd] |= st_
            sg = _sg_sig(D["C"], h)
            rl, rs = {}, {}
            for i in range(210, D["n"] - h):
                rl[i] = _sg_out(D["H"], D["L"], D["C"], i, h, 1, sg[i])
                rs[i] = _sg_out(D["H"], D["L"], D["C"], i, h, -1, sg[i])
            pr = [bisect.bisect_right(BND[fr], t) for t in D["T"]]
            PRE[(sym, fr)] = (act, opp, rl, rs, pr, D["T"], max(86400, h * SG_SEC[fr]))
        time.sleep(0.001)

    def base(fr, side):
        P = [[] for _ in range(4)]
        for sym in names:
            act, opp, rl, rs, pr, T, win = PRE[(sym, fr)]
            for i, x in (rl if side > 0 else rs).items():
                if x is not None:
                    P[pr[i]].append(x)
        return P

    def evalc(fr, keys, side, want=False):
        P, W, ev = [[] for _ in range(4)], [set() for _ in range(4)], []
        for ci, sym in enumerate(names):
            act, opp, rl, rs, pr, T, win = PRE[(sym, fr)]
            sets = [act.get(k) for k in keys]
            if any(s is None for s in sets):
                continue
            inter = set.intersection(*sorted(sets, key=len))
            if not (len(keys) == 1 and keys[0][0].startswith(("W-", "M-"))):  # قراءة السوق وحدها تصف السوق — ليست اتفاق مؤشرات عملة
                inter -= opp[-side]                                            # 🤝 كلها متفقة ولا إشارة معاكسة شغّالة
            r = rl if side > 0 else rs
            last = -10 ** 9
            for i in sorted(inter):
                if i - 1 in inter or i - last < SG_LK[fr]:
                    continue
                last = i
                x = r.get(i)
                if x is None:
                    continue
                q = pr[i]
                P[q].append(x)
                W[q].add(T[i] // win)
                if want:
                    ev.append([ci, T[i]])
        return P, W, ev

    def c4(fr, P, W, B):
        return all(len(P[q]) >= SG_PMIN[fr] and len(W[q]) >= 3 and _sg_hit(P[q]) > _sg_hit(B[q]) and _sg_mean(P[q]) > _sg_mean(B[q])
                   for q in range(4))

    def score(P, B):
        return min(((_sg_mean(P[q]) - _sg_mean(B[q])) * math.sqrt(len(P[q])) if P[q] else -9.0) for q in range(4))

    def mk(fr, side, keys, P, W, ev, ok):
        ks = [k[0] for k in keys]
        allv = [x for p in P for x in p]
        return {"id": f"{fr}|{side}|{'+'.join(ks)}", "f": fr, "s": side, "k": ks, "ty": _sg_type(ks, side),
                "nt": len(allv), "wt": sum(1 for x in allv if x > 0), "mt": round(_sg_mean(allv), 5),
                "nl": 0, "wl": 0, "ml": 0.0, "rare": False, "c4": bool(ok),
                "pp": [[len(p), sum(1 for x in p if x > 0), round(_sg_mean(p), 5), len(w)] for p, w in zip(P, W)],
                "nd": len(set().union(*W)), "ndl": 0, "ev": ev if len(ev) <= 300 else None}

    out, BASE, WK, step = {}, {}, {}, 0
    for fr in SG_FR:
        k0 = 0 if fr == "4H" else 2
        WK[fr] = round(_sg_mean([(v[k0]["T"][-1] - v[k0]["T"][210]) / 604800.0 for v in COIN.values() if v[k0]["n"] > 260]), 2)
        for side in (1, -1):
            step += 1
            if prog:
                prog(78 + 5 * step, f"البحث عن المجموعات المتفقة: {SG_HZN[fr]} · {'شراء' if side > 0 else 'بيع'}")
            B = base(fr, side)
            allb = [x for p in B for x in p]
            BASE[f"{fr}|{side}"] = {"ht": round(_sg_hit(allb), 1), "mt": round(_sg_mean(allb), 5), "hl": round(_sg_hit(allb), 1),
                                    "ml": round(_sg_mean(allb), 5), "nt": len(allb), "nl": 0,
                                    "pp": [[len(p), round(_sg_hit(p), 1), round(_sg_mean(p), 5)] for p in B]}
            singles = []
            keys = sorted(set(k for sym in names for k in PRE[(sym, fr)][0] if k[1] == side))
            for k in keys:
                P, W, ev = evalc(fr, [k], side, True)
                n = sum(len(p) for p in P)
                if n >= 3:
                    e = mk(fr, side, [k], P, W, ev, c4(fr, P, W, B))
                    out[e["id"]] = e
                if n >= 3 * SG_PMIN[fr] and all(P[q] for q in range(4)):
                    singles.append((score(P, B), k))
            singles.sort(reverse=True)
            top1 = [k for s, k in singles[:SG_TOPS]]
            seen, cur = set(), [(k,) for k in top1]
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
                        P, W, _ = evalc(fr, list(nc), side)
                        if sum(len(p) for p in P) >= 4 * SG_PMIN[fr]:
                            cand[nc] = (score(P, B), P, W)
                best = sorted(cand.items(), key=lambda x: -x[1][0])[:SG_BEAM]
                if not best:
                    break
                cur = [c for c, _ in best]
                kept = 0
                for c, (s, P, W) in best:
                    if kept >= SG_KEEP:
                        break
                    if c4(fr, P, W, B):
                        P, W, ev = evalc(fr, list(c), side, True)
                        e = mk(fr, side, c, P, W, ev, True)
                        out[e["id"]] = e
                        kept += 1
    # ✂️ تركيبة بنفس حالات تركيبة أصغر منها (الإشارة الزايدة ما أضافت شي) ⇒ تُحذف — الأصغر تكفي
    bk = {}
    for e in out.values():
        bk.setdefault((e["f"], e["s"], e["nt"], e["wt"], tuple(tuple(x) for x in e["pp"])), []).append(e)
    drop = set()
    for grp in bk.values():
        if len(grp) < 2:
            continue
        for e in grp:
            ks = set(e["k"])
            if any(o is not e and set(o["k"]) < ks for o in grp):
                drop.add(e["id"])
    return {"e": [e for e in out.values() if e["id"] not in drop], "base": BASE, "wk": WK, "dup": len(drop), "rule": "c4",
            "bnd": {fr: [int(x) for x in BND[fr]] for fr in SG_FR}}
'''

R = [
    # the horizons · the history · the version
    ("""SG_HZ = {"4H": 18, "1D": 7}                # الحكم بعد: 4 ساعات ← 3 أيام · اليومي ← أسبوع
SG_HZN = {"4H": "3 أيام", "1D": "أسبوع"}""",
     """SG_HZ = {"4H": 6, "1D": 30}                # 🧠 v3.36.69: الحكم بعد: إطار 4 ساعات ← يوم (غداً) · اليومي ← 30 يوماً (الشهر القادم)
SG_HZN = {"4H": "يوم", "1D": "شهر"}
SG_HZW = {"4H": "غداً", "1D": "الشهر القادم"}
SG_PMIN = {"4H": 6, "1D": 4}               # أقل عدد حالات في كل فترة من الأربع (مع ≥ 3 نوافذ مستقلة)
SG_W = 120                                 # 📏 شموع التذبذب قبل الدخول (بُعد الهدف والوقف)"""),
    ("""SG_N = {"4H": 4400, "1D": 1100}            # تاريخ القياس (~سنتان · ~3 سنوات)""",
     """SG_N = {"4H": 4400, "1D": 2600}            # تاريخ القياس (~سنتان · ~7 سنوات — للشهر القادم)"""),
    ("""SG_CAT_VER = 2                             # 🔄 v3.36.68: نسخة الدليل — دليل بُني بكود أقدم (بلا إشارة جديدة) يُعاد بناؤه وحده""",
     """SG_CAT_VER = 3                             # 🔄 نسخة الدليل — دليل بُني بكود أقدم يُعاد بناؤه وحده (v3: المجموعات المتفقة بالفترات الأربعة)"""),
    # the compass: also a month
    ("""    for h in (7, 14):
        acc = {"up": [], "flat": [], "down": []}""", """    for h in (7, 14, 30):
        acc = {"up": [], "flat": [], "down": []}"""),
    ("""            "m14": H.get("m14"), "h14": H.get("h14"), "run": H.get("run"), "hist": [[x[0], x[1], x[2]] for x in seq[-60:]]}""",
     """            "m14": H.get("m14"), "h14": H.get("h14"), "m30": H.get("m30"), "h30": H.get("h30"), "run": H.get("run"),
            "hist": [[x[0], x[1], x[2]] for x in seq[-60:]]}"""),
    # an older saved history is filled backwards once
    ("""            r = _safe(_fc_cache, sym, cdb, sec, bar, ib, SG_N[fr], default=None)
            if not r or not r[0]:
                bad.append(sym)
            time.sleep(0.15)""",
     """            r = _safe(_fc_cache, sym, cdb, sec, bar, ib, SG_N[fr], default=None)
            if not r or not r[0]:
                bad.append(sym)
            else:
                e_ = (cdb.get(sec) or {}).get(sym) or {}
                if e_.get("d") and len(e_["d"]) < SG_N[fr] - 5 and not e_.get("full"):
                    _safe(_sg_backfill, sym, e_, bar, SG_N[fr], default=None)     # 📅 v3.36.69: تاريخ أقدم مرة واحدة
            time.sleep(0.15)"""),
    ("""def _sg_refresh(coins, frs, cdb, prog=None):""",
     """def _sg_backfill(sym, e, bar, maxn, pages=40):
    \"\"\"📅 v3.36.69: تاريخ أقدم لعملة محفوظة بتاريخ أقصر (اليومي من ~3 سنوات إلى ~7 للشهر القادم) — صفحة صفحة حتى الحد أو بداية تاريخها\"\"\"
    rows = [list(x) for x in e.get("d") or []]
    for _ in range(pages):
        if not rows:
            return
        oldest = rows[0][0]
        pg = _fc_okx_rows(sym, bar, after=oldest * 1000, hist=True, limit=100) or []
        pg = sorted(list(c[:6]) for c in pg if len(c) > 6 and c[6] and c[0] < oldest)
        if not pg:
            e["full"] = True
            break
        rows = pg + rows
        if len(rows) >= maxn:
            break
        time.sleep(0.25)
    e["d"] = rows[-maxn:]


def _sg_refresh(coins, frs, cdb, prog=None):"""),
    # the scan carries the entry's target/stop distance
    ("""            res.setdefault(sym, {})[fr] = {"t": D["T"][i], "px": D["C"][i], "a1": a1, "a0": a0, "lo": min(D["L"][i - lk + 1:i + 1]),""",
     """            res.setdefault(sym, {})[fr] = {"t": D["T"][i], "px": D["C"][i], "s": round(_sg_sig(D["C"][-(SG_W + 2):], SG_HZ[fr])[-1], 5),
                                           "a1": a1, "a0": a0, "lo": min(D["L"][i - lk + 1:i + 1]),"""),
    ("""                pend.append([e["id"], sym, x["t"], x["px"], 1 if ok else 0])""",
     """                pend.append([e["id"], sym, x["t"], x["px"], 1 if ok else 0, x.get("s") or 0])"""),
    # the live record: the same target/stop rule
    ("""        try:
            eid, sym, ts, px, flag = it[0], it[1], int(it[2]), float(it[3]), int(it[4])
        except Exception:
            continue
        fr, side = eid.split("|")[0], int(eid.split("|")[1])
        sec = SG_BAR[fr][0]
        if (sym, sec) not in T:
            rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
            T[(sym, sec)] = ([int(r[0]) for r in rows], [float(r[4]) for r in rows])
        ts_, cs = T[(sym, sec)]
        tgt = ts + SG_HZ[fr] * SG_SEC[fr]
        j = bisect.bisect_left(ts_, tgt)
        if j < len(ts_) and ts_[j] == tgt and px > 0:
            c1 = cs[j]
            x = (c1 / px - 1.0 if side > 0 else px / c1 - 1.0) - SG_FEE""",
     """        try:
            eid, sym, ts, px, flag = it[0], it[1], int(it[2]), float(it[3]), int(it[4])
            s_ = float(it[5]) if len(it) > 5 and it[5] else 0.0
        except Exception:
            continue
        fr, side = eid.split("|")[0], int(eid.split("|")[1])
        sec = SG_BAR[fr][0]
        if (sym, sec) not in T:
            rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
            T[(sym, sec)] = ([int(r[0]) for r in rows], [float(r[4]) for r in rows], [float(r[2]) for r in rows], [float(r[3]) for r in rows])
        ts_, cs, hs, ls = T[(sym, sec)]
        tgt = ts + SG_HZ[fr] * SG_SEC[fr]
        j = bisect.bisect_left(ts_, tgt)
        if j < len(ts_) and ts_[j] == tgt and px > 0:
            j0 = bisect.bisect_left(ts_, ts)
            if j0 < len(ts_) and ts_[j0] == ts and j0 + SG_HZ[fr] == j:
                x = _sg_out(hs, ls, cs, j0, SG_HZ[fr], side, s_, px)          # 🎯 v3.36.69: الهدف قبل الوقف (نفس قاعدة التاريخ)
            else:
                c1 = cs[j]
                x = (c1 / px - 1.0 if side > 0 else px / c1 - 1.0) - SG_FEE"""),
    # only proven groups notify
    ("""    if not cfg["types"].get(e.get("ty") or "buy", True) or not cfg["fr"].get(e["f"], True):
        return False
    r = _sg_rec(e, st)""",
     """    if not cfg["types"].get(e.get("ty") or "buy", True) or not cfg["fr"].get(e["f"], True):
        return False
    if not e.get("c4"):                                   # 🧠 v3.36.69: فقط المجموعات المتفقة التي صدقت في الفترات الأربعة كلها
        return False
    r = _sg_rec(e, st)"""),
    ("""APP_VERSION = "3.36.68\"""", """APP_VERSION = "3.36.69\""""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a = s.index("def _sg_search(COIN, prog=None):")
    b = s.index("\n\ndef _sg_compass_states(", a)
    s = s[:a] + NEW_SEARCH.rstrip() + "\n" + s[b:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the new search · 🧠 proven agreeing groups (4 periods) · 🎯 target/stop rule · غداً + الشهر القادم · {p}")
