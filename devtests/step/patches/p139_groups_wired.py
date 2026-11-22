# p139 — v3.36.77 🧩 the groups wired into the dashboard (server side) · the old 📋 tables and the 🎯 daily tendency removed
#   The owner (21-11): «ابدي زيل مؤشرات القديم ابني واحد من جديد … كل مجموعه تختص باشعار … الاشعار … ونسبته وذكر المؤشر»
#   · the hourly scan: the last candles only (the whole history moved to the daily build) · the market-wide readings by _gp_wide · the live
#     check gp_now (the champions of the last build that fired on the closed candle, one side) ⇒ «gpn»
#   · the daily build (after the daily close · or when there is none / it is older than 30 h / a coin of yours is new — at most every 6 h):
#     gp_build in the worker (no network) ⇒ Holy_Groups.json
#   · the notices: one type per group (g_<group> · 📲/👁/⛔ like every other type) · text = what will happen within the frame + the member's
#     record (right % of n · the usual) + its name · 📲 only when the group's own record (what would have been sent) is ≥ the usual + 3% on
#     ≥ 30 — otherwise 👁 in the window · the same side of the same group on the same coin waits 4 h (1H) · 12 h (4H) · 20 h (1D)
#   · /api/groups (the build + what fired now + each group's notice level) · ⚙️ shows each group's record per frame · 🔮 gets the coin's
#     group calls (gp) instead of the tendency
#   · removed: the 📋 tables (SB_* · sb_* · /api/board · sb_off · Holy_Board.json on disk) · the 🎯 tendency (TD_P · td_* · its notice type ·
#     A["td"]) — the neutral names stay as GP_NM (rule 16: a new indicator = its entry in _SG_NM/_SG_XNM + its neutral name here)
#   python3 devtests/step/patches/p139_groups_wired.py Holy_Dashboard.pyw
import sys, os, re, ast

R = [
    ('SG_N = {"1H": 720, "4H": 4400, "1D": 2600}            # تاريخ القياس (~سنتان · ~7 سنوات — للشهر القادم)\n',
     'SG_N = {"1H": 2160, "4H": 4400, "1D": 2600}           # تاريخ القياس (🧩 v3.36.77: الساعة ~3 أشهر للمجاميع · 4 ساعات ~سنتان · اليوم ~7 سنوات)\n'),
    # the scan
    ('    frs = [f for f in (job.get("frs") or []) if f in SB_FR]\n', '    frs = [f for f in (job.get("frs") or []) if f in GP_FR]\n'),
    ('            D, E = _sg_events(rows, fr == "1D", ctx, t0=210 if fr == "1D" else len(rows) - SG_LK[fr] - 3, dx=SG_SEC[fr])   # 🎯 v3.36.76: اليومي بكامل تاريخه (للميل)\n',
     '            D, E = _sg_events(rows, fr == "1D", ctx, t0=len(rows) - SG_LK[fr] - 3, dx=SG_SEC[fr])   # 🧩 v3.36.77: آخر الشموع (التاريخ كله في البناء اليومي)\n'),
    ('''        crash = {"t": tl, "n": len(z), "k": sum(1 for x in z if x <= -2.5), "on": tl in CR}
        _safe(_sb_surge, F4, Z, min(D["n"] for D, E in F4.values()) - 8, default=None)     # 📋 v3.36.73: 🚀 الصعود المفاجئ للسوق كله
    _safe(_sb_wide, FF, default=None)                         # 📋 v3.36.73: قراءات السوق كله للجداول (الساعة · عدد العملات الصاعدة · البوصلة)
''', '''        crash = {"t": tl, "n": len(z), "k": sum(1 for x in z if x <= -2.5), "on": tl in CR}
    _safe(_gp_wide, FF, default=None)                         # 🧩 v3.36.77: قراءات السوق كله على آخر الشموع (🌊 🚀 📊 🧭) لكل إطار
'''),
    ('''    td = _safe(td_pack, FF.get("1D"), default=None) if "1D" in frs else None     # 🎯 v3.36.76: الميل اليومي (أبطال الجداول المجمّعة)
    return {"ok": True, "c": res, "crash": crash, "ts": time.time(), "an": an, "td": td}
''', '''    G = None
    if job.get("build"):                                      # 🧩 v3.36.77: مرة باليوم — كل عملة بكل إطار على تاريخها ⇒ السجل والأبطال
        _sg_prog(jd, 90, "🧩 بناء سجل المجاميع على التاريخ")
        keep = [s for s in (job.get("keep") or []) if isinstance(s, str)]
        G = _safe(gp_build, cdb, coins, keep, pdb, fdb, lambda p_, msg: _sg_prog(jd, 90 + 0.099 * p_, msg), default=None)
        if G:
            G["keep"] = keep
    gsrc = G or _safe(load_json, GP_FILE, default=None)
    gpn = (_safe(gp_now, FF, gsrc, default=None) or {}) if isinstance(gsrc, dict) and gsrc.get("v") == GP_VER else {}
    return {"ok": True, "c": res, "crash": crash, "ts": time.time(), "an": an, "gp": G, "gpn": gpn}
'''),
    # the tick
    ('''        if os.path.exists(os.path.join(SG_DIR, "catalog.json")):
            _safe(os.remove, os.path.join(SG_DIR, "catalog.json"), default=None)
        T = {fr: int(now // SG_SEC[fr]) * SG_SEC[fr] - SG_SEC[fr] for fr in SB_FR}       # 📋 v3.36.73: والساعة للجداول
        due = [fr for fr in SB_FR if now - (T[fr] + SG_SEC[fr]) >= 90 and st.get("b_" + fr) != T[fr]]       # كل شمعة مغلقة مرة واحدة
''', '''        for f_ in (os.path.join(SG_DIR, "catalog.json"), os.path.join(ROOT, "Holy_Board.json")):     # 🧹 v3.36.77: وجداول 📋 القديمة
            if os.path.exists(f_):
                _safe(os.remove, f_, default=None)
        T = {fr: int(now // SG_SEC[fr]) * SG_SEC[fr] - SG_SEC[fr] for fr in GP_FR}
        due = [fr for fr in GP_FR if now - (T[fr] + SG_SEC[fr]) >= 90 and st.get("b_" + fr) != T[fr]]       # كل شمعة مغلقة مرة واحدة
'''),
    ('            bd_ = _sg_refresh(uni, list(SB_FR) if missing else [f for f in SB_FR if f in due], cdb, pg)\n',
     '            bd_ = _sg_refresh(uni, list(GP_FR) if missing else [f for f in GP_FR if f in due], cdb, pg)\n'),
    ('            sj = _sg_spawn("scan", {"coins": have, "frs": due})\n',
     '''            keep = [s for s in sg_coins(cfg) if s in have]
            bld = "1D" in due or _gp_need(st, now, keep)      # 🧩 v3.36.77: البناء اليومي (أو لا بناء / قديم / عملة جديدة من عملاتك)
            if bld:
                st["gp_try"] = now
            sj = _sg_spawn("scan", {"coins": have, "frs": due, "build": bld, "keep": keep})
'''),
    ('''                _safe(sb_feed, sc, due, cdb or {}, now, default=None)          # 📋 v3.36.73: الجداول — كل صف يتنبأ ويُحكم من الصفر
''', '''                if isinstance(sc.get("gp"), dict) and sc["gp"].get("f"):
                    _safe(save_json_atomic, GP_FILE, sc["gp"], default=None)      # 🧩 v3.36.77: سجل المجاميع وأبطالها (البناء اليومي)
                    _GP["mt"] = None
                gq = st.setdefault("gpn", {})
                for fr in due:
                    gq[fr] = (sc.get("gpn") or {}).get(fr) or {}          # 🧩 ما انطلق الآن من الأبطال (للنافذة و🔮)
'''),
    # the market layer: no tendency · the group notices
    ('def _an_facts(prev, P, rng_prev, mine, lv, sc=None, lvd=None, cdb=None, td=None):\n', 'def _an_facts(prev, P, rng_prev, mine, lv, sc=None, lvd=None, cdb=None):\n'),
    ('''        daily = "1D" in frs
        td = (sc or {}).get("td") if daily else None
        if isinstance(td, dict):
            A["td"] = td                                     # 🎯 الميل اليومي وأبطاله (للنافذة و🔮)
        scx = {"crash": (sc or {}).get("crash") if "4H" in frs else None, "c": (sc or {}).get("c") or {}}
        facts = _an_facts(prev, P, rng_prev, sg_coins(cfg), cfg.get("alv") or {}, scx, (A.get("lvd") or {}) if daily else None, cdb,
                          td if isinstance(td, dict) else None) if prev else []
''', '''        daily = "1D" in frs
        A.pop("td", None)                                    # 🧹 v3.36.77: الميل اليومي صار داخل المجاميع
        scx = {"crash": (sc or {}).get("crash") if "4H" in frs else None, "c": (sc or {}).get("c") or {}}
        mine = sg_coins(cfg)
        facts = _an_facts(prev, P, rng_prev, mine, cfg.get("alv") or {}, scx, (A.get("lvd") or {}) if daily else None, cdb) if prev else []
        facts += _safe(_gp_facts, (sc or {}).get("gpn") or {}, (sc or {}).get("gp") or gp_load(), mine, cfg.get("alv") or {}, frs, default=[]) or []
'''),
    ('            if now - float(A["sent"].get(key) or 0) < AN_DUP.get(f["ty"], 20 * 3600):\n',
     '            if now - float(A["sent"].get(key) or 0) < (f.get("dup") or AN_DUP.get(f["ty"], 20 * 3600)):\n'),
    ('    "tend": ("🎯", "الميل اليومي (حين يثبت)", "coin", "now"), "rs": ("💪", "القوة مقابل البيتكوين", "coin", "view"),\n',
     '    "rs": ("💪", "القوة مقابل البيتكوين", "coin", "view"),\n'),
    # 🔮 the coin's group calls instead of the tendency
    ('''    A = _safe(_an_load, default={}) or {}                     # 🔮 v3.36.76: على نفس أساس «📈 السوق» — المدى المثبت وصدقه الحي + الميل اليومي
''', '''    A = _safe(_an_load, default={}) or {}                     # 🔮 v3.36.76: على نفس أساس «📈 السوق» — المدى المثبت وصدقه الحي
'''),
    ('''    td = A.get("td") or {}
    v["td"] = {"t": td.get("t"), "now": td.get("now") or {}, "rec": td.get("rec") or [0, 0], "rec1": td.get("rec1") or [0, 0], "since": td.get("since"),
               "ch": [[x[0], x[1], SB_NM.get(x[0], x[0]), x[2], x[3]] for x in (td.get("ch") or [])], "names": {c: nm for c, nm in SB_NM.items()}}
''', '''    v["gp"] = _safe(gp_coin_now, [r.get("sym") for r in v["rows"]], default={}) or {}     # 🧩 v3.36.77: ما تتوقعه مجاميع العملة الآن (أبطالها)
'''),
    # ⚙️ each group's record per frame
    ('''    v["plain"], v["grp"] = sg_plain_all(), [list(g) for g in SG_GRP]                  # 🎯 v3.36.71: كل مؤشر بكلام واضح
    return v
''', '''    v["plain"], v["grp"] = sg_plain_all(), [list(g) for g in SG_GRP]                  # 🎯 v3.36.71: كل مؤشر بكلام واضح
    v["gpr"], v["frs"] = _safe(gp_recs, default={}) or {}, {k: list(x) for k, x in GP_FRN.items()}      # 🧩 v3.36.77: سجل كل مجموعة بكل إطار
    return v
'''),
    # the routes
    ('''        if u.path == "/api/board":                        # 📋 v3.36.73: جدول المؤشرات (السوق أو عملة) — من الملف · لا ينتظر الحساب
            return self._json(_safe(sb_view, (q.get("s") or [""])[0], default={"ok": False, "rows": [], "msg": "تعذّر تحميل الجدول"}))
''', '''        if u.path == "/api/groups":                       # 🧩 v3.36.77: المجاميع (العملات · السوق) — من الملف · لا ينتظر الحساب
            return self._json(_safe(gp_view, default={"ok": False, "msg": "تعذّر تحميل المجاميع"}))
'''),
    ('''            if act == "sb_off":                           # 📋 v3.36.73: ⏸ صف في جدول المؤشرات
                return self._json(sb_off((data.get("value") if isinstance(data.get("value"), dict) else {})))
''', ''),
]

# the 🎯 tendency's notice block inside _an_facts (removed whole)
TD_FACTS = re.compile(r"\n    if td:                                                   # 🎯 الميل اليومي — أبطال الجداول المجمّعة فقط \(p131\)\n(?:        .*\n|            .*\n|                .*\n)+")

HELP = r'''
AN_TY.update({"g_" + g: (G["ic"], G["nm"], "g" + G["sec"], G["lv"]) for g, G in GP_GROUPS.items()})   # 🔔 إشعار لكل مجموعة (📲 / 👁 / ⛔)
GP_DUP = {"1H": 4 * 3600, "4H": 12 * 3600, "1D": 20 * 3600}      # الجهة نفسها للمجموعة نفسها على العملة نفسها لا تتكرر قبل هذه المدة
_GP = {"v": None, "mt": None}


def gp_load():
    """آخر بناء من الملف (بالذاكرة حتى يتغير الملف)"""
    try:
        mt = os.path.getmtime(GP_FILE)
    except Exception:
        return None
    if _GP["mt"] != mt:
        G = _safe(load_json, GP_FILE, default=None)
        _GP.update(v=G if isinstance(G, dict) and G.get("v") == GP_VER else None, mt=mt)
    return _GP["v"]


def _gp_need(st, now, keep):
    """يحتاج بناءً الآن؟ لا بناء · أقدم من 30 ساعة · عملة من عملاتك (لها شموع) ليس لها سجل — ولا يُعاد قبل 6 ساعات من محاولة سابقة"""
    if now - float(st.get("gp_try") or 0) < 6 * 3600:
        return False
    G = gp_load()
    return not G or now - float(G.get("ts") or 0) > 30 * 3600 or any(s not in (G.get("keep") or []) for s in keep)


def gp_name(key):
    """اسم العضو بكلام واضح: المؤشر باسمه المحايد (GP_NM) · التوليفة «أ + ب»"""
    def one(c):
        if c in GP_NM:
            return GP_NM[c]
        p = _sg_plain(c)
        return p[1] if p else c
    return " + ".join(one(c) for c in str(key).split("+"))


def _gp_grp(G, fr, sec, g):
    return (((((G or {}).get("f") or {}).get(fr) or {}).get(sec) or {}).get("g") or {}).get(g) or {}


def _gp_best(Gg, keys):
    """أصدق الأبطال المنطلقين ⇒ صف العضو [المفتاح · صدق · أخطأ · أيام · الحالة · العادي]"""
    rows = [x for x in Gg.get("m") or [] if x[0] in keys and x[1] + x[2] > 0]
    return max(rows, key=lambda x: (x[1] / (x[1] + x[2]) - x[5], x[1] + x[2])) if rows else None


def gp_proven(rec):
    """📲 للمجموعة على هذا الإطار؟ سجلها نفسه (ما كان سيصل) ≥ العادي + GP_SAY على 30 مرة فأكثر"""
    w, n, b = (list(rec or []) + [0, 0, 0.0])[:3]
    return n >= 30 and w / n >= b / n + GP_SAY


def _gp_facts(gpn, G, mine, lv, frs):
    """📨 ما انطلق الآن من أبطال كل مجموعة ⇒ [(مفتاح التكرار, {sym · ty · lv · urg · ln · t · b · dup})] — 🪙 لعملاتك فقط · 🌐 للسوق"""
    out = []
    for fr in frs:
        for sec, D in ((gpn or {}).get(fr) or {}).items():
            for g, by in (D or {}).items():
                if g not in GP_GROUPS:
                    continue
                ty = "g_" + g
                L = (lv or {}).get(ty) or AN_TY[ty][3]
                if L not in ("now", "view"):
                    continue
                X, Gg = GP_GROUPS[g], _gp_grp(G, fr, sec, g)
                ok = gp_proven(Gg.get("rec"))
                for sym, x in (by or {}).items():
                    if sec == "coin" and sym not in mine:
                        continue
                    s = int(x[0])
                    best = _gp_best(Gg, list(x[1] or []))
                    if not best or s not in (1, -1):
                        continue
                    n_ = best[1] + best[2]
                    fi = GP_FRN[fr]
                    ln = (f"{X['ic']} {fi[0]} {X['say'][0 if s > 0 else 1]} {fi[2]}\n"
                          f"{gp_name(best[0])} — صدق {round(100.0 * best[1] / n_)}% من {n_:,} مرة (العادي {round(100.0 * best[5])}%)")
                    if not ok:
                        ln += "\nسجل هذه المجموعة لم يثبت بعد — في النافذة فقط"
                    sy = sym if sec == "coin" else "السوق"
                    head = ln.split("\n")[0]
                    out.append((f"g|{g}|{fr}|{sym}|{s}", {"sym": sy, "ty": ty, "lv": L if ok else "view", "urg": False, "ln": ln, "dup": GP_DUP[fr],
                                                         "t": (f"{sym.split('-')[0]}: " if sec == "coin" else "السوق: ") + head,
                                                         "b": " · ".join(ln.split("\n")[1:])}))
    return out


def gp_recs():
    """⚙️ سجل كل مجموعة بكل إطار (ما كان سيصل): {g_المجموعة: {الإطار: [صدق · المحكوم · مجموع العادي]}}"""
    out = {}
    for fr, x in ((gp_load() or {}).get("f") or {}).items():
        for sec in ("coin", "mkt"):
            for g, y in ((x.get(sec) or {}).get("g") or {}).items():
                out.setdefault("g_" + g, {})[fr] = y.get("rec") or [0, 0, 0.0]
    return out


def gp_coin_now(syms):
    """🔮 ما تتوقعه مجاميع العملة الآن: {العملة: [[الإطار · المجموعة · الجهة · اسم العضو · صدق · المحكوم · العادي · مثبتة؟]]}"""
    G, gpn = gp_load(), _sg_st().get("gpn") or {}
    out = {}
    for fr in GP_FR:
        for g, by in (((gpn.get(fr) or {}).get("coin")) or {}).items():
            if g not in GP_GROUPS:
                continue
            Gg = _gp_grp(G, fr, "coin", g)
            for sym in syms:
                x = (by or {}).get(sym)
                best = _gp_best(Gg, list(x[1] or [])) if x else None
                if best:
                    out.setdefault(sym, []).append([fr, g, int(x[0]), gp_name(best[0]), best[1], best[1] + best[2], best[5], gp_proven(Gg.get("rec"))])
    return out


def gp_view():
    """🧩 GET /api/groups — المجاميع كما بُنيت آخر مرة (من الملف · لا ينتظر الحساب) + ما انطلق الآن + مستوى إشعار كل مجموعة"""
    G = gp_load() or {}
    cfg = sg_cfg()
    codes = _gp_codes()
    return {"ok": True, "ts": G.get("ts"), "n": G.get("n") or {}, "p": G.get("p") or GP_P, "f": G.get("f") or {}, "now": _sg_st().get("gpn") or {},
            "groups": {g: {"sec": x["sec"], "ic": x["ic"], "nm": x["nm"], "job": x["job"], "say": list(x["say"]), "mem": gp_members(g, codes)}
                       for g, x in GP_GROUPS.items()},
            "jobs": {k: list(v) for k, v in GP_JOBS.items()}, "frs": {k: list(v) for k, v in GP_FRN.items()}, "secn": {k: list(v) for k, v in GP_SECN.items()},
            "names": {c: gp_name(c) for c in codes}, "plain": sg_plain_all(), "mine": sg_coins(cfg), "lv": {g: cfg["alv"].get("g_" + g) for g in GP_GROUPS},
            "say": GP_SAY, "busy": {"phase": _SG.get("phase") or "", "pct": int(_SG.get("pct") or 0), "msg": _SG.get("msg") or ""}, "err": _SG.get("err") or ""}
'''

EXTRA_NM = {"P-fund": "رسوم التمويل في العقود"}      # had no row in the old tables — every indicator has its neutral name now

DEAD_PY = ('SB_FR', 'SB_FRN', 'SB_FILE', 'SB_MKT', 'SB_ALL', 'SB_MINN', 'SB_MV', 'SB_ONE', 'SB_ROWS', 'SB_NUM', 'SB_NM', 'SB_COMBOS', '_SB',
           '_sb_load', '_sb_surge', '_sb_wide', '_sb_count', '_sb_grade', '_sb_fired', 'sb_feed', '_sb_cell', 'sb_view', 'sb_off',
           'TD_P', '_td_fires', '_td_fam', 'td_walk', 'td_score', 'td_prep', 'td_pack')


def py_spans(s, names):
    tree = ast.parse(s)
    spans = []
    for node in tree.body:
        nm = node.name if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else \
            (node.targets[0].id if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) else None)
        if nm in names:
            spans.append((node.lineno, node.end_lineno, isinstance(node, (ast.FunctionDef, ast.ClassDef)), nm))
    return spans


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if len(TD_FACTS.findall(s)) != 1:
        print("❌ the tendency notice block not found once"); sys.exit(1)
    s = TD_FACTS.sub("\n", s)
    # the neutral names stay (GP_NM) — taken from SB_ROWS before it goes
    rows = next(ast.literal_eval(n.value) for n in ast.parse(s).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SB_ROWS")
    gpnm = ("GP_NM = {   # 🧩 v3.36.77: كل مؤشر باسم محايد واضح (بلا حروف فنية) — مؤشر جديد = مدخله في _SG_NM/_SG_XNM + اسمه هنا (القاعدة 16)\n"
            + "".join(f"    {c!r}: {nm!r},\n" for _n, c, nm in rows) + "".join(f"    {c!r}: {nm!r},\n" for c, nm in EXTRA_NM.items()) + "}\n")
    # the two old section headers (their comments) go with their code
    for hdr, nxt in (("# ───────────── 📋 v3.36.73: جداول المؤشرات", "SB_FR = "), ("# ───────────── 🎯 v3.36.76: الميل اليومي", "TD_P = ")):
        a = s.index(hdr)
        b = s.index(nxt, a)
        s = s[:a] + s[b:]
    L = s.split("\n")
    sp = py_spans(s, DEAD_PY)
    miss = set(DEAD_PY) - {x[3] for x in sp}
    if miss:
        print(f"❌ not found as a top-level definition: {sorted(miss)}"); sys.exit(1)
    first_sb = min(x[0] for x in sp if x[3] == "SB_FR")
    for a0, b0, is_def, nm in sorted(sp, reverse=True):
        b1 = b0
        if is_def:
            while b1 < len(L) and L[b1].strip() == "" and b1 - b0 < 2:
                b1 += 1
        del L[a0 - 1:b1]
        if nm == "SB_FR":
            L.insert(a0 - 1, gpnm.rstrip("\n") + "\n\n")
    s = "\n".join(L)
    s = re.sub(r"\n{4,}(?=# ───────────── )", "\n\n\n", s)
    a = "\ndef sg_loop():"
    if s.count(a) != 1:
        print("❌ sg_loop anchor"); sys.exit(1)
    s = s.replace(a, HELP.rstrip("\n") + "\n\n" + a, 1)
    left = [n for n in DEAD_PY if re.search(r"(?<![\w.'\"])" + re.escape(n) + r"(?![\w'\"])", s)]
    if left:
        print(f"❌ still referenced after the cleanup: {left}"); sys.exit(1)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined after the change:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the groups wired (scan · daily build · notices · /api/groups · ⚙️ · 🔮) · {len(DEAD_PY)} old names removed · compiles · {p}")
