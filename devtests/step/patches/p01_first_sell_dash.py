# 🪜 patch 01 (dashboard, without the engine — the engine goes in by embed_engine.py) — the first sell's distance apart from
#   the distance between sells: the plan table (= the engine's layout) · the form · deploy · the card · the drawer · the guard ·
#   the clone · the trial path's wallet · the table refuses any sell that would lose after the two fees (the engine's own rule)
#   python3 devtests/step/patches/p01_first_sell_dash.py Holy_Dashboard.pyw      (in place · every old text found once ·
#   only the expected top-level definitions change (AST) · every embedded engine stays byte for byte the same)
import ast, os, sys

R = [
    # ── _step_layout: the same change as the engine's step_layout
    ("def _step_layout(P0, G, d, N, Q, floor, up, fee, lot=None, mn=None, max_down=400):\n",
     "def _step_layout(P0, G, d, N, Q, floor, up, fee, lot=None, mn=None, max_down=400, d1=None):\n"),
    ("    P0, G, d, Q, floor, fee = float(P0), float(G), float(d), float(Q), float(floor or 0), float(fee or 0)\n"
     "    N, up = max(1, int(N)), max(0, int(up or 0))\n",
     "    P0, G, d, Q, floor, fee = float(P0), float(G), float(d), float(Q), float(floor or 0), float(fee or 0)\n"
     "    d1 = d if d1 is None or d1 == \"\" else float(d1)\n"
     "    N, up = max(1, int(N)), max(0, int(up or 0))\n"),
    ("    if P0 <= 0 or G <= 0 or d <= 0 or Q <= 0:\n        return out\n    m = 0\n",
     "    if P0 <= 0 or G <= 0 or d <= 0 or d1 <= 0 or Q <= 0:\n        return out\n    m = 0\n"),
    ("            sp = sig(bp * (1.0 + k * d))\n",
     "            sp = sig(bp * (1.0 + k * d)) if d1 == d else sig(bp * (1.0 + d1 + (k - 1) * d))\n"),
    # ── _step_args: step_first_pct (empty = the sell spacing itself)
    ('        d = float(data.get("step_sell_pct") or 0) / 100.0\n',
     '        d = float(data.get("step_sell_pct") or 0) / 100.0\n'
     '        _v1 = data.get("step_first_pct")                      # 📈 مسافة أول بيعة — فارغ = مسافة البيع نفسها\n'
     '        d1 = d if _v1 is None or str(_v1).strip() == "" else float(_v1) / 100.0\n'),
    ('    if Q <= 0 or G <= 0 or d <= 0:\n        return None, "المبلغ ومسافة البيع ومسافة الشراء يجب أن تكون أكبر من صفر"\n',
     '    if Q <= 0 or G <= 0 or d <= 0 or d1 <= 0:\n'
     '        return None, "المبلغ ومسافة أول بيعة والمسافة بين البيعات ومسافة الشراء يجب أن تكون أكبر من صفر"\n'),
    ('    return {"sym": sym, "base": sym.split("-")[0], "Q": Q, "N": N, "d": d, "G": G, "floor": floor, "up": up, "p0": p0}, None\n',
     '    return {"sym": sym, "base": sym.split("-")[0], "Q": Q, "N": N, "d": d, "d1": d1, "G": G, "floor": floor, "up": up, "p0": p0}, None\n'),
    # ── step_plan
    ('    lay = _step_layout(P0, a["G"], a["d"], a["N"], a["Q"], a["floor"] if a["floor"] > 0 else P0 * 0.5, a["up"], f, lot, mn)\n',
     '    lay = _step_layout(P0, a["G"], a["d"], a["N"], a["Q"], a["floor"] if a["floor"] > 0 else P0 * 0.5, a["up"], f, lot, mn, d1=a["d1"])\n'),
    ("    if p1 is not None and p1 <= 0:\n"
     "        errs.append(f\"مسافة البيع {a['d'] * 100:g}% لا تغطي العمولتين ({2 * f * 100:.2f}%) — أول بيعة تخسر · كبّر مسافة البيع\")\n"
     "    if a[\"G\"] < a[\"N\"] * a[\"d\"] - 1e-12:\n"
     "        warns.append(f\"النسب تتداخل: بيعات كل مستوى تمتد ({a['N'] * a['d'] * 100:g}%) فوق مسافة الشراء ({a['G'] * 100:g}%) — مسموح، \"\n",
     "    if (p1 is not None and p1 <= 0) or any(not r.get(\"skip\") and r[\"sp\"] * (1.0 - f) * (1.0 - f) <= r[\"bp\"] for r in lay):\n"
     "        errs.append(f\"مسافة أول بيعة {a['d1'] * 100:g}% لا تغطي العمولتين ({2 * f * 100:.2f}%) — البيعة الأولى تخسر · \"   # 💰 = شرط المحرك\n"
     "                    \"كبّر مسافة أول بيعة\")\n"
     "    span = a[\"d1\"] + (a[\"N\"] - 1) * a[\"d\"]          # من الشراء إلى آخر بيعة\n"
     "    if a[\"G\"] < span - 1e-12:\n"
     "        warns.append(f\"النسب تتداخل: بيعات كل مستوى تمتد ({span * 100:g}%) فوق مسافة الشراء ({a['G'] * 100:g}%) — مسموح، \"\n"),
    ('            "err": errs, "warn": warns, "args": {k: a[k] for k in ("Q", "N", "d", "G", "floor", "up")}}\n',
     '            "err": errs, "warn": warns, "args": {k: a[k] for k in ("Q", "N", "d", "d1", "G", "floor", "up")}}\n'),
    # ── deploy_step: the engine reads step_first · the Telegram line
    ('    cfg = {**keys, "symbol": a["sym"], "bot_type": "grid_step", "usd_value": a["Q"], "step_parts": a["N"], "step_sell": a["d"],\n',
     '    cfg = {**keys, "symbol": a["sym"], "bot_type": "grid_step", "usd_value": a["Q"], "step_parts": a["N"], "step_sell": a["d"],\n'
     '           "step_first": a["d1"],\n'),
    ("                f\"`{a['N']}` بيعات لكل شراء · البيع `{a['d'] * 100:g}%` · الشراء `{a['G'] * 100:g}%` · `{a['Q']:g}$` لكل شراء\")\n",
     "                f\"`{a['N']}` بيعات لكل شراء · أول بيعة `{a['d1'] * 100:g}%` · بين البيعات `{a['d'] * 100:g}%` · \"\n"
     "                f\"الشراء `{a['G'] * 100:g}%` · `{a['Q']:g}$` لكل شراء\")\n"),
    # ── the card's settings (bot_snapshot)
    ('            "scfg": ({"N": int(float(b["cfg"].get("step_parts") or 0)), "d": float(b["cfg"].get("step_sell") or 0),\n',
     '            "scfg": ({"N": int(float(b["cfg"].get("step_parts") or 0)), "d": float(b["cfg"].get("step_sell") or 0),\n'
     '                      "d1": float(b["cfg"].get("step_first") or b["cfg"].get("step_sell") or 0),\n'),
    # ── the trial path's suggested wallet
    ('                a = {"Q": f("usd_value", 15), "N": int(f("step_parts", 3)), "d": f("step_sell", 0.01), "G": f("grid_percentage", 0.03),\n',
     '                a = {"Q": f("usd_value", 15), "N": int(f("step_parts", 3)), "d": f("step_sell", 0.01), "d1": f("step_first", 0) or None,\n'
     '                     "G": f("grid_percentage", 0.03),\n'),
    ('                lay = [r for r in _step_layout(a["p0"] or p0, a["G"], a["d"], a["N"], a["Q"], a["floor"] or p0 * 0.5, a["up"], FEE_RATE_DEFAULT,\n'
     '                                               spec.get("lotSz"), spec.get("minSz")) if not r.get("skip")]\n',
     '                lay = [r for r in _step_layout(a["p0"] or p0, a["G"], a["d"], a["N"], a["Q"], a["floor"] or p0 * 0.5, a["up"], FEE_RATE_DEFAULT,\n'
     '                                               spec.get("lotSz"), spec.get("minSz"), d1=a.get("d1")) if not r.get("skip")]\n'),
    # ── the guard's stall check: a buy's first sell is d1 away (the larger distance ⇒ no false «stall»)
    ('            step = max(g, float(cfg.get("buy_offset") or 0)) if bt == "grid_plus" else (float(cfg.get("step_sell") or 0) or g) if bt == "grid_step" else g\n',
     '            step = max(g, float(cfg.get("buy_offset") or 0)) if bt == "grid_plus" else (\n'
     '                max(float(cfg.get("step_sell") or 0), float(cfg.get("step_first") or 0)) or g) if bt == "grid_step" else g\n'),
    # ── the profit page's settings text
    ("            return (f\"{int(float(c.get('step_parts') or 0))} بيعات لكل شراء · البيع {float(c.get('step_sell') or 0) * 100:g}% · \"\n"
     "                    f\"الشراء {g:g}% · {float(c.get('usd_value') or 0):g}$ لكل شراء\")\n",
     "            _d = float(c.get('step_sell') or 0) * 100\n"
     "            _d1 = float(c.get('step_first') or c.get('step_sell') or 0) * 100\n"
     "            return (f\"{int(float(c.get('step_parts') or 0))} بيعات لكل شراء · \"\n"
     "                    + (f\"البيع {_d:g}% · \" if abs(_d1 - _d) < 1e-9 else f\"أول بيعة {_d1:g}% · بين البيعات {_d:g}% · \")\n"
     "                    + f\"الشراء {g:g}% · {float(c.get('usd_value') or 0):g}$ لكل شراء\")\n"),
    # ── 📋 clone (the form filled from a bot)
    ('                                        "step_parts": c.get("step_parts"), "step_sell_pct": round(float(c.get("step_sell") or 0) * 100, 6),\n',
     '                                        "step_parts": c.get("step_parts"), "step_sell_pct": round(float(c.get("step_sell") or 0) * 100, 6),\n'
     '                                        "step_first_pct": round(float(c.get("step_first") or c.get("step_sell") or 0) * 100, 6),\n'),
    # ── JS: the drawer's settings rows
    ('      <tr><td style="text-align:right">مسافة البيع</td><td class="num">${+((+b.scfg.d||0)*100).toFixed(4)}%</td></tr>\n',
     '      <tr><td style="text-align:right">مسافة أول بيعة</td><td class="num">${+((+(b.scfg.d1!=null?b.scfg.d1:b.scfg.d)||0)*100).toFixed(4)}%</td></tr>\n'
     '      <tr><td style="text-align:right">المسافة بين البيعات</td><td class="num">${+((+b.scfg.d||0)*100).toFixed(4)}%</td></tr>\n'),
    # ── JS: the deploy form — two fields
    ('    <div class="fld"><label title="المسافة بين الشراء وأول بيعة = المسافة بين بيعة وبيعة">📈 مسافة البيع (%)</label><input id="st_d" class="num" value="${v(\'step_sell_pct\',1)}" oninput="stPreview()"></div>\n',
     '    <div class="fld"><label title="المسافة بين سعر الشراء وأول بيعة فوقه">📈 مسافة أول بيعة (%)</label><input id="st_d1" class="num" value="${v(\'step_first_pct\',v(\'step_sell_pct\',1))}" oninput="stPreview()"></div>\n'
     '    <div class="fld"><label title="المسافة بين كل بيعة والتي بعدها — متساوية بين كل بيعتين">↔️ المسافة بين البيعات (%)</label><input id="st_d" class="num" value="${v(\'step_sell_pct\',1)}" oninput="stPreview()"></div>\n'),
    ("  return {symbol:g('st_sym').toUpperCase(),usd_value:g('st_q'),step_parts:g('st_n'),step_sell_pct:g('st_d'),grid_pct:g('st_g'),\n",
     "  return {symbol:g('st_sym').toUpperCase(),usd_value:g('st_q'),step_parts:g('st_n'),step_sell_pct:g('st_d'),step_first_pct:g('st_d1'),grid_pct:g('st_g'),\n"),
    # ── JS: the card's sub-line
    ("M.sub=kd==='step'?`${+SC.N||0} بيعات لكل شراء · البيع ${+((+SC.d||0)*100).toFixed(4)}% · الشراء",
     "M.sub=kd==='step'?`${+SC.N||0} بيعات لكل شراء · ${(SC.d1!=null&&Math.abs(+SC.d1-(+SC.d||0))>1e-12)?`أول بيعة ${+((+SC.d1)*100).toFixed(4)}% · بين البيعات ${+((+SC.d||0)*100).toFixed(4)}%`:`البيع ${+((+SC.d||0)*100).toFixed(4)}%`} · الشراء"),
]
ALLOWED = {"_step_layout", "_step_args", "step_plan", "deploy_step", "bot_snapshot", "_bt_wallet_def", "_gd_gather", "_pv_cfg_txt",
           "control", "HTML_PAGE"}


def tops(src):
    out, cnt = {}, {}
    for n in ast.parse(src).body:
        nm = getattr(n, "name", None)
        if nm is None and isinstance(n, ast.Assign) and len(n.targets) == 1:
            nm = ast.unparse(n.targets[0])
        if nm is None:                                    # an import / if / try: the n-th of its kind (lines move)
            cnt[type(n).__name__] = cnt.get(type(n).__name__, 0) + 1
            nm = f"<{type(n).__name__}#{cnt[type(n).__name__]}>"
        out.setdefault(nm, []).append(ast.dump(n))
    return out


def main(path):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        n = src.count(a)
        if n != 1:
            print(f"❌ replacement {i}: the old text is found {n} times (must be once) — nothing written:\n{a[:200]}")
            sys.exit(1)
        src = src.replace(a, b)
    compile(src, path, "exec")
    t0, t1 = tops(src0), tops(src)
    changed = {k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k)}
    if changed - ALLOWED or set(t0) != set(t1):
        print(f"❌ unexpected top-level changes: {sorted(changed - ALLOWED)} · names {sorted(set(t0) ^ set(t1))} — nothing written")
        sys.exit(1)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src)
    os.replace(tmp, path)
    print(f"✅ {len(R)} replacements · compiles · changed only {sorted(changed)} · {path}")


if __name__ == "__main__":
    main(sys.argv[1])
