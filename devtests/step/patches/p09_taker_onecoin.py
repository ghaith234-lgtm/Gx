# 🪜 patch 09 (dashboard + engine · the owner 6-11) — ① the table before deploy counts every sell's profit with OKX's TAKER fee
#   (0.10%) on both sides — the worst case (a jump fills at once) — and refuses on it · the bot uses the same rule at birth · the real
#   fills keep their exact fee  ② a losing row is all red  ③ one graded grid per coin: deploy refuses a second one on the same coin
#   (the form's table says so · the trial path does not refuse)
#   python3 devtests/step/patches/p09_taker_onecoin.py ENGINE.py Holy_Dashboard.pyw     (both checked before either is written)
import ast, os, sys

ENG = [
    ('''        if config.get("step_first") not in (None, ""):          # 📈 مسافة أول بيعة (بلاها = مسافة البيع نفسها)
            stp["d1"] = float(config.get("step_first"))
''',
     '''        if config.get("step_first") not in (None, ""):          # 📈 مسافة أول بيعة (بلاها = مسافة البيع نفسها)
            stp["d1"] = float(config.get("step_first"))
        stp["t"] = float(config.get("taker_rate") or 0.001)    # 🧾 عمولة taker لشرط «ما يشتغل إذا اكو خسارة» (الأسوأ)
'''),
    ('''    fr = float(stp["f"])
''', '''    fr = max(float(stp["f"]), float(stp.get("t") or 0))
'''),
]

DASH = [
    ('''STEP_WINDOW = 8              # 🪟 الأقرب فقط على المنصة لكل جهة (المحرك step_window)
''',
     '''STEP_WINDOW = 8              # 🪟 الأقرب فقط على المنصة لكل جهة (المحرك step_window)
STEP_TAKER_FEE = 0.001       # 🧾 v3.36.18: taker OKX 0.10% — الجدول يحسب ربح كل بيعة بالأسوأ (المالك 6-11) · التنفيذ الحقيقي بعمولته
'''),
    ('''def step_plan(data, px=None):
''',
     '''def _step_taken(sym):
    """🪜 v3.36.18 (المالك 6-11: «واحد لكل عملة»): مجلد شبكي متدرج موجود على هالعملة (أي محفظة) · None = لا"""
    for b in bot_dirs().values():
        try:
            if str((b.get("cfg") or {}).get("bot_type") or "") == "grid_step" and str(b.get("symbol") or "").upper() == str(sym).upper():
                return os.path.basename(str(b["dir"]).rstrip("/\\\\"))
        except Exception:
            continue
    return None


def step_plan(data, px=None, live=False):
'''),
    ('''    f = FEE_RATE_DEFAULT
    errs, warns = [], []
''',
     '''    f = FEE_RATE_DEFAULT
    t = max(f, STEP_TAKER_FEE)                  # 🧾 v3.36.18: ربح البيعة والرفض بعمولة taker للطرفين (الأسوأ)
    errs, warns = [], []
'''),
    ('''            pr = cq * r["sp"] * (1 - f) - r["q"] * r["bp"]''',
     '''            pr = r["q"] * (1 - t) * r["sp"] * (1 - t) - r["q"] * r["bp"]'''),
    ('''                gap = ((cq - qn) * r["sp"], qn, cq, qn * r["sp"] * (1 - f) - r["q"] * r["bp"])''',
     '''                gap = ((cq - qn) * r["sp"], qn, cq, qn * (r["sp"] * (1 - t) - r["bp"] / (1 - t)))'''),
    ('''    if (p1 is not None and p1 <= 0) or any(not r.get("skip") and r["sp"] * (1.0 - f) * (1.0 - f) <= r["bp"] for r in lay):
        errs.append(f"مسافة أول بيعة {a['d1'] * 100:g}% لا تغطي العمولتين ({2 * f * 100:.2f}%) — البيعة الأولى تخسر · "   # 💰 = شرط المحرك
                    "كبّر مسافة أول بيعة")
''',
     '''    if (p1 is not None and p1 <= 0) or any(not r.get("skip") and r["sp"] * (1.0 - t) * (1.0 - t) <= r["bp"] for r in lay):
        errs.append(f"مسافة أول بيعة {a['d1'] * 100:g}% لا تغطي العمولتين ({2 * t * 100:.2f}% بعمولة taker — الأسوأ) — البيعة الأولى "   # 💰 = شرط المحرك
                    "ممكن تخسر · كبّر مسافة أول بيعة")
    _tk = _step_taken(a["sym"]) if live else None
    if _tk:
        errs.insert(0, f"يوجد شبكي متدرج على {a['sym']} ({_tk}) — واحد لكل عملة · احذفه أولاً")
'''),
    ('''    return {"ok": True, "sym": a["sym"], "base": a["base"], "P0": P0, "fee": f, "lot": lot, "mn": mn, "rows": rows, "tot": tot,''',
     '''    return {"ok": True, "sym": a["sym"], "base": a["base"], "P0": P0, "fee": f, "taker": t, "lot": lot, "mn": mn, "rows": rows, "tot": tot,'''),
    ('''    P = step_plan(data, px=px)
    if not P.get("ok"):
        return P
    if P["err"]:
        return {"ok": False, "msg": "⛔ " + P["err"][0]}
''',
     '''    P = step_plan(data, px=px)
    if not P.get("ok"):
        return P
    if P["err"]:
        return {"ok": False, "msg": "⛔ " + P["err"][0]}
    _tk = _step_taken(a["sym"])                     # 🪜 v3.36.18: واحد لكل عملة
    if _tk:
        return {"ok": False, "msg": f"⛔ يوجد شبكي متدرج على {a['sym']} ({_tk}) — واحد لكل عملة · احذفه أولاً"}
'''),
    ('''           "fee_rate": P["fee"], "step_window": STEP_WINDOW,''',
     '''           "fee_rate": P["fee"], "taker_rate": P["taker"], "step_window": STEP_WINDOW,'''),
    ('''return self._json(_safe(step_plan, data, default={"ok": False, "msg": "تعذّر الحساب"}))''',
     '''return self._json(_safe(step_plan, data, None, True, default={"ok": False, "msg": "تعذّر الحساب"}))'''),
    ('''h+=`<tr class="${cls}${i===0?' stg':''}${i===0&&r.j===0?' st0':''}" data-j=''',
     '''h+=`<tr class="${cls}${i===0?' stg':''}${i===0&&r.j===0?' st0':''}${s&&s.pr<=0?' stneg':''}" data-j='''),
    ('''<th>الربح الصافي</th>''',
     '''<th title="بعمولة taker 0.1% للشراء والبيع — الأسوأ · التنفيذ الحقيقي بعمولته بالضبط">الربح الصافي (أسوأ عمولة)</th>'''),
    ('''.sttab td[rowspan]{vertical-align:middle}''',
     '''.sttab td[rowspan]{vertical-align:middle}.sttab tr.stneg td{background:rgb(var(--red-rgb)/.2)!important;color:var(--red)!important}'''
     '''.sttab tr.stneg td b{color:var(--red)!important}'''),
    ('''<span>💰 ربح أول بيعة صافياً <b>''', '''<span>💰 ربح أول بيعة صافياً (أسوأ عمولة) <b>'''),
]
ALLOWED = {"step_plan", "deploy_step", "_step_taken", "STEP_TAKER_FEE", "Handler", "HTML_PAGE"}


def tops(src):
    out, cnt = {}, {}
    for n in ast.parse(src).body:
        nm = getattr(n, "name", None)
        if nm is None and isinstance(n, ast.Assign) and len(n.targets) == 1:
            nm = ast.unparse(n.targets[0])
        if nm is None:
            cnt[type(n).__name__] = cnt.get(type(n).__name__, 0) + 1
            nm = f"<{type(n).__name__}#{cnt[type(n).__name__]}>"
        out.setdefault(nm, []).append(ast.dump(n))
    return out


def patch(path, R, allowed=None):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        if src.count(a) != 1:
            print(f"❌ {os.path.basename(path)} replacement {i}: found {src.count(a)} times — nothing written: {a[:70]}"); sys.exit(1)
        src = src.replace(a, b)
    compile(src, path, "exec")
    if allowed is not None:
        t0, t1 = tops(src0), tops(src)
        changed = {k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k)}
        if changed - allowed:
            print(f"❌ unexpected top-level changes: {sorted(changed - allowed)} — nothing written"); sys.exit(1)
    return src


if __name__ == "__main__":
    e, d = sys.argv[1], sys.argv[2]
    out = [(e, patch(e, ENG)), (d, patch(d, DASH, ALLOWED))]
    for p, s in out:
        with open(p + ".tmp", "w", encoding="utf-8") as fh:
            fh.write(s)
        os.replace(p + ".tmp", p)
    print(f"✅ engine {len(ENG)} · dashboard {len(DASH)} replacements · compile")
