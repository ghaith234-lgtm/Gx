# p135 — v3.36.76 🧹 the old analyst's dead code removed (the owner 21-11: «تنظيف الكود القديم اللي بقى بلا شغل»)
#   Since v3.36.75 the catalog of combinations was never built and its notices never sent — but its code was still in the file. Now:
#   · gone: the catalog build (worker «build» mode · the search · the compass history) · its browser (/api/signals_cat) · the old live record
#     and its CSV (sg_rec) · «rebuild» (sg_rebuild) · the weekly estimate (sg_est) · the analyst's words, blocks and lines in 🔮 (sg_fc) ·
#     the old settings (the % · types · frames · rare · cap · summary) · their page leftovers
#   · the tick: no catalog · one-time cleanup of the old state keys and of _signals/catalog.json on disk
#   · kept: the 36 systems and every reading (the tables use them) · the scan · the compass · the market layer · the tables · the tendency
#   · every removed name is checked to be unreferenced afterwards (the patch stops otherwise)
#   python3 devtests/step/patches/p135_cleanup_catalog.py Holy_Dashboard.pyw
import sys, os, re

R = [
    # the routes
    ('        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح\n'
     '            return self._json(_safe(sg_catlist, q, default={"ok": False, "rows": [], "msg": "تعذّر تحميل الدليل"}))\n', ''),
    ('            if act == "sg_est":\n'
     '                return self._json(_safe(sg_est, (data.get("value") if isinstance(data.get("value"), dict) else {}), default={"ok": False, "est": None}))\n'
     '            if act == "sg_rec":                           # 📜 v3.36.69: سجل المحلل للسحب ملفاً\n'
     '                return self._json(sg_record())\n', ''),
    ('            if act == "sg_rebuild":\n                return self._json(sg_rebuild())\n', ''),
    # 🔮 no analyst lines
    ('    v["sig"] = _safe(sg_fc, v["rows"], default=None)          # 🎯 v3.36.66: إشارات كل عملة الآن + البوصلة\n', ''),
    # the worker: the scan only
    ('        out = sg_build(jd, job) if job.get("mode") == "build" else sg_scan_calc(jd, job)\n', '        out = sg_scan_calc(jd, job)\n'),
    # the tick
    ('''        uni = _sg_universe()
        cat = _sg_cat()
        bj = _SG.get("build")
        if bj and _sg_job_done(bj):
            o = _sg_job_out(bj) or {}
            _SG["build"] = None
            _SG["err"] = "" if o.get("ok") else ("🏗️ " + str(o.get("err") or "تعذّر بناء الدليل"))
            cat = _sg_cat()
''', '''        uni = _sg_universe()
        for k_ in ("pend", "done", "now", "nst", "cat_try", "cat_force", "t_4H", "t_1D", "sumq", "sum_day", "comp_new"):   # 🧹 v3.36.76: بقايا المحلل القديم
            st.pop(k_, None)
        if os.path.exists(os.path.join(SG_DIR, "catalog.json")):
            _safe(os.remove, os.path.join(SG_DIR, "catalog.json"), default=None)
'''),
    ('''        due = [fr for fr in SB_FR if now - (T[fr] + SG_SEC[fr]) >= 90 and (st.get("b_" + fr) != T[fr]                 # 📋 الجداول: كل شمعة مرة
               or (cat and fr in SG_FR and st.get("t_" + fr) != T[fr]))]                             # 🧠 المحلل: حين يجهز دليله
''', '''        due = [fr for fr in SB_FR if now - (T[fr] + SG_SEC[fr]) >= 90 and st.get("b_" + fr) != T[fr]]       # كل شمعة مغلقة مرة واحدة
'''),
    ('''        full = lambda s: ci["c4"].get(s, 0) >= SG_MIN["4H"] and ci["c"].get(s, 0) >= SG_MIN["1D"]
        need_cat = (not cat or now - float(cat.get("ts") or 0) > SG_CAT_AGE or bool(st.get("cat_force")) or int(cat.get("cv") or 1) != SG_CAT_VER
                    or any(s not in (cat.get("coins") or []) and full(s) for s in sg_coins(cfg)))
        build_now = False                                    # 📈 v3.36.75: دليل المحلل القديم لا يُبنى (المحلل الجديد: حقائق + المدى المثبت)
        cdb = None
        if missing or due or build_now:
''', '''        cdb = None
        if missing or due:
'''),
    ('            bd_ = _sg_refresh(uni, list(SB_FR) if (missing or build_now) else [f for f in SB_FR if f in due], cdb, pg)\n',
     '            bd_ = _sg_refresh(uni, list(SB_FR) if missing else [f for f in SB_FR if f in due], cdb, pg)\n'),
    ('            st["bad"] = sorted(set(bd_) if (missing or build_now) else set(st.get("bad") or []) | set(bd_))   # 📋 جلب جزئي لا يمحو ما فشل\n',
     '            st["bad"] = sorted(set(bd_) if missing else set(st.get("bad") or []) | set(bd_))   # 📋 جلب جزئي لا يمحو ما فشل\n'),
    ('''        if build_now:
            coins = [s for s in uni if full(s)]
            if len(coins) >= 3:
                st["cat_try"] = now
                st.pop("cat_force", None)
                _SG["build"] = _sg_spawn("build", {"coins": coins})
''', ''),
    ('            comp = _safe(_sg_compass, cdb, cat, default=None)\n', '            comp = _safe(_sg_compass, cdb, default=None)\n'),
    ('''                if prev_c.get("s") and comp["s"] != prev_c.get("s") and comp["since"] != prev_c.get("since"):
                    st["comp_new"] = comp["s"]
''', ''),
    ('''                    st["b_" + fr] = T[fr]                     # 📋 الجداول رأت هذه الشمعة
                    if cat and fr in SG_FR:
                        st["t_" + fr] = T[fr]                 # 🧠 والمحلل (لا تُعلَّم قبل جاهزية دليله — يراها حين يجهز)
''', '''                    st["b_" + fr] = T[fr]                     # 📋 رأى الفحص هذه الشمعة
'''),
    ('                st.pop("comp_new", None)\n', ''),
    ('''                for s in [s for s in (st.get("now") or {}) if s not in uni]:
                    st["now"].pop(s, None)
''', ''),
    # the settings: what the window uses
    ('''    for k, key in (("on", "sg_on"), ("rare", "sg_rare")):                     # 🎯 v3.36.71: «أفضل من العشوائي» ثابت بالداخل
        if v.get(k) is not None:
            c[key] = bool(v[k])
    for k, key, lo, hi in (("thr", "sg_thr", 50, 95), ("rmin", "sg_rmin", 3, 50), ("cap", "sg_cap", 0, 100)):     # «أقل عدد مرات» ثابت بالداخل
        if v.get(k) is not None:
            try:
                c[key] = max(lo, min(hi, int(v[k])))
            except Exception:
                pass
    if isinstance(v.get("types"), dict):
        t = dict(c.get("sg_types") or {})
        t.update({k: bool(x) for k, x in v["types"].items() if k in SG_TY})
        c["sg_types"] = t
''', '''    if v.get("on") is not None:
        c["sg_on"] = bool(v["on"])
'''),
    ('''    if isinstance(v.get("fr"), dict):
        f = dict(c.get("sg_fr") or {})
        f.update({k: bool(x) for k, x in v["fr"].items() if k in SG_FR})
        c["sg_fr"] = f
''', ''),
    ('''    if "sum" in v:
        c["sg_sum"] = (int(v["sum"]) % 24) if isinstance(v["sum"], (int, float)) and not isinstance(v["sum"], bool) else None
''', ''),
    ('    return {"ok": True, "msg": msg, "cfg": p, "est": sg_estimate(p)}\n', '    return {"ok": True, "msg": msg, "cfg": p}\n'),
    # the page
    ("let SGV=null,SGT=null,SGTAB='mkt',SGC=null,SGP={},SGET=null;const SGO={},SGF={fr:'',side:'1',size:'',rare:'',ty:'',q:'',sort:''};",
     "let SGV=null,SGT=null,SGTAB='mkt';"),
    ("${fcBot(r)}${sgFc(r)}<div class=\"fc-rows\">", "${fcBot(r)}<div class=\"fc-rows\">"),
    ("          ${fcAn(r,k)}\n", ""),
]

CFG = '''def sg_cfg():
    """⚙️ تنبيهات السوق: التشغيل · عملاتك · ساعات الهدوء · القناة · مستوى كل نوع (الحد اليومي داخلي 12)"""
    c = _safe(app_cfg, default={}) or {}
    coins = c.get("sg_coins")
    coins = [str(x).upper() for x in coins if isinstance(x, str)] if isinstance(coins, list) else None
    qh = c.get("sg_quiet")
    qh = [int(qh[0]) % 24, int(qh[1]) % 24] if isinstance(qh, list) and len(qh) == 2 and all(isinstance(x, (int, float)) for x in qh) else None
    ch = str(c.get("sg_ch") or "both")
    lv = _an_lv_cfg(c)
    return {"on": bool(c.get("sg_on", True)), "coins": coins, "cap": 12, "quiet": qh, "ch": ch if ch in SG_CH else "both",
            "alv": lv, "atypes": {k: x != "off" for k, x in lv.items()}}
'''

VIEW = '''def sg_view():
    """🎯 GET /api/signals — إعدادات تنبيهات السوق وسجلها وحالة الفحص (🧹 v3.36.76: بلا دليل المحلل القديم)"""
    cfg = sg_cfg()
    st = _sg_st()
    v = {"ok": True, "cfg": cfg, "atypes": {k: list(x) for k, x in AN_TY.items()}, "ch": SG_CH, "mine": sg_coins(cfg), "tick": ticker_cfg()["coins"],
         "uni": _sg_universe(), "busy": {"phase": _SG.get("phase") or "", "pct": int(_SG.get("pct") or 0), "msg": _SG.get("msg") or ""},
         "err": _SG.get("err") or "", "comp": st.get("comp"), "crash": st.get("crash"), "scan_ts": st.get("scan_ts"),
         "on": indic_cfg()["on"] or cfg["on"], "log": (st.get("log") or [])[:60]}
    _ci = _safe(_sg_cidx, default=None) or {"c4": {}, "c": {}}
    v["bad"] = [s for s in v["mine"] if s in (st.get("bad") or [])]                          # 🪙 v3.36.67: المنصة لا تعرفها
    v["short"] = [s for s in v["mine"] if s not in v["bad"] and s in _ci["c4"] and (_ci["c4"].get(s, 0) < 300 or _ci["c"].get(s, 0) < 220)]
    v["plain"], v["grp"] = sg_plain_all(), [list(g) for g in SG_GRP]                  # 🎯 v3.36.71: كل مؤشر بكلام واضح
    return v


def sg_api():
    v = sg_view()
    if v["on"] and not _SG["busy"] and not v.get("scan_ts"):
        threading.Thread(target=_safe, args=(sg_tick,), daemon=True).start()     # أول فتح: يبدأ الفحص الأول بالخلفية
    return v
'''

DEAD_PY = (   # found by tracing the call graph from every live entry point after the cuts above — repeated until nothing new (td_prep stays: ci/sig_check15.py)
    'SG_CAT', 'SG_CAT_AGE', 'SG_CAT_VER', 'SG_COIN_TY', 'SG_FN', 'SG_FR', 'SG_HZN', 'SG_HZW', 'SG_MIN', 'SG_MINC', 'SG_NST', 'SG_NST_AGE',
    'SG_NST_NOTE', 'SG_PMIN', 'SG_RNDC', 'SG_TY', 'SG_WHY', 'SG_WORD', '_SG_FAM_TREND', '_SG_OLDF', '_sg_analyst', '_sg_block', '_sg_cat',
    '_sg_cfg_merge', '_sg_coin_rows', '_sg_comp_block', '_sg_compass_hist', '_sg_days', '_sg_dtxt', '_sg_grade', '_sg_hit', '_sg_keys_txt',
    '_sg_mean', '_sg_meta', '_sg_mkt_block', '_sg_mktwide', '_sg_mon', '_sg_name', '_sg_nst_block', '_sg_out', '_sg_pass', '_sg_pct',
    '_sg_process', '_sg_rec', '_sg_rec_line', '_sg_res_block', '_sg_row', '_sg_search', '_sg_strict_on', '_sg_tyk', '_sg_type', '_sg_why',
    'sg_build', 'sg_catlist', 'sg_est', 'sg_estimate', 'sg_fc', 'sg_rebuild', 'sg_record',
)
DEAD_JS = ("sgFc", "sgFcAn", "fcAn", "sgAr", "sgDt", "sgPct", "sgTy", "sgPlNm", "fcVote", "indPDet", "indX", "indXDet")


def py_span(s, name):
    m = re.search(r"\n(?:def |class )" + re.escape(name) + r"\(|\n" + re.escape(name) + r" = ", s)
    i = m.start() + 1
    j = s.find("\n\n\n", i)
    j = len(s) if j < 0 else j + 1
    while s[j:j + 1] == "\n":
        j += 1
    return i, j


def js_span(s, name):
    m = re.search(r"\n(?:async )?function " + re.escape(name) + r"\(", s)
    i = m.start() + 1
    n = re.search(r"\n(?:async function |function |const |let |/\*)", s[i + 1:])
    return i, i + 1 + n.start() + 1


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a, b = py_span(s, "sg_cfg")
    s = s[:a] + CFG + "\n\n" + s[b:]
    v_view, v_api = VIEW.split("\n\n\ndef sg_api():\n")
    a, b = py_span(s, "sg_view")
    s = s[:a] + v_view.rstrip("\n") + "\n\n\n" + s[b:]
    a, b = py_span(s, "sg_api")
    s = s[:a] + "def sg_api():\n" + v_api.rstrip("\n") + "\n\n\n" + s[b:]
    import ast
    tree = ast.parse(s)
    spans = []
    for node in tree.body:
        nm = node.name if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else \
            (node.targets[0].id if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) else None)
        if nm is None and isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript) \
                and isinstance(node.targets[0].value, ast.Name) and node.targets[0].value.id in DEAD_PY:
            spans.append((node.lineno, node.end_lineno, False, "[]" + node.targets[0].value.id))       # NAME["k"] = … of a removed name
            continue
        if nm in DEAD_PY:
            a0 = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
            spans.append((a0, node.end_lineno, isinstance(node, (ast.FunctionDef, ast.ClassDef)), nm))
    miss = set(DEAD_PY) - {x[3] for x in spans if not x[3].startswith("[]")}
    if miss:
        print(f"❌ not found as a top-level definition: {sorted(miss)}"); sys.exit(1)
    L = s.split("\n")
    for a0, b0, is_def, nm in sorted(spans, reverse=True):                 # exact statement lines (a function also takes its blank lines after)
        b1 = b0
        if is_def:
            while b1 < len(L) and L[b1].strip() == "" and b1 - b0 < 2:
                b1 += 1
        del L[a0 - 1:b1]
    s = "\n".join(L)
    for name in DEAD_JS:
        a, b = js_span(s, name)
        s = s[:a] + s[b:]
    left = [n for n in DEAD_PY + DEAD_JS if re.search(r"(?<![\w.'\"])" + re.escape(n) + r"(?![\w'\"])", s)]
    if left:
        print(f"❌ still referenced after the cleanup: {left}"); sys.exit(1)
    compile(s, p, "exec")
    try:                                                   # every name a function uses must still be defined (pyflakes when present)
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined after the cleanup:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · {len(DEAD_PY)} dead Python names and {len(DEAD_JS)} dead page functions removed · compiles · {p}")
