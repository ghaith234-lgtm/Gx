# ⚡ patch 102 (dashboard v3.36.59 · DCA+ الشرائي — the server side). Patch 101's engine inside the dashboard, the same way patch 95
#   put DCA+ (the sell one) in: a buy DCA with dca_plus = the free ladder going DOWN, its exit ABOVE the average (dollar profit).
#   · `_DCAPB_B64` · DCAPB_SRC · DCAPB_VERSION · `engine_for`: a buy DCA with dca_plus ⇒ dca_plus_buy (the normal buy DCA keeps its own)
#   · deploy_dca «dca_type: dca_plus_buy» + plus_rows ⇒ bot_type dca_buy + dca_plus + the rows (checked before any folder is made —
#     the same rules as DCA+) · its label «DCA+ شرائي»
#   · the preview `_plus_table`: both directions (buy: each order under the one before · exit = average × (1 + x) · the net dollar
#     profit with the same fees as the engine · the dollars it needs) · compute_dca_table takes both DCA+ types
#   · control «plus_edit»: DCA+ of both directions · the trial path (from the form and from a bot) and the demo: «dca_plus_buy» ⇒ the buy
#     kind with its rows · the trial/demo wallet: the dollars of every row at its own price
#   python3 devtests/step/patches/p102_dca_plus_buy_server.py Holy_Dashboard.pyw devtests/step/eng/dca_plus_buy.py
import base64, os, sys, zlib

if __name__ == "__main__":
    p, eng = sys.argv[1], sys.argv[2]
    s = open(p, encoding="utf-8").read()
    src = open(eng, encoding="utf-8").read()
    compile(src, eng, "exec")
    b64 = base64.b64encode(zlib.compress(src.encode("utf-8"), 9)).decode()
    lit = "\n".join('"' + b64[i:i + 120] + '"' for i in range(0, len(b64), 120))
    R = [
        ('''DCAP_SRC = _zlib.decompress(_b64.b64decode(_DCAP_B64)).decode("utf-8")
DCAP_VERSION = _eng_fp(DCAP_SRC)
''', '''DCAP_SRC = _zlib.decompress(_b64.b64decode(_DCAP_B64)).decode("utf-8")
DCAP_VERSION = _eng_fp(DCAP_SRC)

# ⚡ v3.36.59: DCA+ الشرائي — السلّم الحر نزولاً (كل أمر بمسافته وكميته ونسبة خروجه فوق المتوسط) · نسخة من محرك DCA الشرائي — الأصل
#   ما تغيّر · devtests/step/eng/dca_plus_buy.py (patch 101)
_DCAPB_B64 = (
''' + lit + '''
)
DCAPB_SRC = _zlib.decompress(_b64.b64decode(_DCAPB_B64)).decode("utf-8")
DCAPB_VERSION = _eng_fp(DCAPB_SRC)
'''),
        ('''    if bt == "dca_buy":
        return DCAB_SRC, "dca.py", DCAB_VERSION''', '''    if bt == "dca_buy":
        if cfg.get("dca_plus"):                              # ⚡ v3.36.59: DCA+ الشرائي (سلّم حر نزولاً)
            return DCAPB_SRC, "dca.py", DCAPB_VERSION
        return DCAB_SRC, "dca.py", DCAB_VERSION'''),
        # ── the preview: both directions
        ('''    rows, why = _plus_rows_ok(cfg.get("plus_rows"))
    if rows is None:
        return {"rows": [], "msg": why}
    if base_price <= 0:
        return []
    trail = str(cfg.get("trail_on")).lower() in ("1", "true", "on", "yes")''', '''    rows, why = _plus_rows_ok(cfg.get("plus_rows"))
    if rows is None:
        return {"rows": [], "msg": why}
    if base_price <= 0:
        return []
    is_buy = str(cfg.get("dca_type") or "") == "dca_plus_buy" or str(cfg.get("bot_type") or "") == "dca_buy"   # ⚡ v3.36.59: الشرائي
    trail = str(cfg.get("trail_on")).lower() in ("1", "true", "on", "yes")'''),
        ('''        if i:
            p = p * (1 + r["d"] / 100.0)
        q, fee = r["q"], (DCA_FEE_TAKER if i == 0 else f_lv)
        cq += q; cv += p * q; cnet += p * q * (1 - fee)
        avg = cv / cq
        x_used = max(r["x"], 0.20)
        tgt = avg * (1 - x_used / 100.0)
        prof = cnet / tgt * (1 - DCA_FEE_TAKER) - cq
        out.append({"n": i, "label": "أساسي" if i == 0 else f"أمان {i}", "price": round(p, 10), "order_qty": round(q, 6),
                    "order_val": round(p * q, 2), "step": round(r["d"], 4), "dev": round((p / base_price - 1) * 100, 3),
                    "cum_qty": round(cq, 6), "cum_vol": round(cv, 2), "avg": round(avg, 10), "target": round(tgt, 10),
                    "gap_pct": round((1 - tgt / p) * 100, 3), "exit_profit": round(prof, 6), "exit_usd": round(prof * tgt, 4),
                    "gap": round(abs(tgt - avg), 10), "x": r["x"], "x_used": x_used})''', '''        if i:
            p = p * (1 - r["d"] / 100.0) if is_buy else p * (1 + r["d"] / 100.0)
        q, fee = r["q"], (DCA_FEE_TAKER if i == 0 else f_lv)
        cq += q; cv += p * q; cnet += q * (1 - fee) if is_buy else p * q * (1 - fee)
        avg = cv / cq
        x_used = max(r["x"], 0.20)
        tgt = avg * (1 + x_used / 100.0) if is_buy else avg * (1 - x_used / 100.0)
        if is_buy:                                           # الشرائي: يبيع كل ما اشترى (صافيه) عند الهدف ⇒ ربح دولار
            prof = cnet * tgt * (1 - DCA_FEE_TAKER) - cv
            gap, prof_usd = (tgt / p - 1) * 100, prof
        else:
            prof = cnet / tgt * (1 - DCA_FEE_TAKER) - cq
            gap, prof_usd = (1 - tgt / p) * 100, prof * tgt
        out.append({"n": i, "label": "أساسي" if i == 0 else f"أمان {i}", "price": round(p, 10), "order_qty": round(q, 6),
                    "order_val": round(p * q, 2), "step": round(r["d"], 4), "dev": round(abs(p / base_price - 1) * 100, 3),
                    "cum_qty": round(cq, 6), "cum_vol": round(cv, 2), "avg": round(avg, 10), "target": round(tgt, 10),
                    "gap_pct": round(gap, 3), "exit_profit": round(prof, 6), "exit_usd": round(prof_usd, 4),
                    "gap": round(abs(tgt - avg), 10), "x": r["x"], "x_used": x_used})'''),
        ('''    last, first = out[-1], out[0]
    cov = (last["price"] / base_price - 1) * 100
    gaps = [r["gap_pct"] for r in out]
    return {"rows": out, "summary": {
        "is_buy": False, "trail": trail, "plus": True,''', '''    last, first = out[-1], out[0]
    cov = abs(last["price"] / base_price - 1) * 100
    gaps = [r["gap_pct"] for r in out]
    return {"rows": out, "summary": {
        "is_buy": is_buy, "trail": trail, "plus": True,'''),
        ('''        "coverage": round(cov, 3), "cov_warn": cov < 3.0, "capital_needed": round(last["cum_qty"], 6), "capital_usd": round(last["cum_vol"], 2),''',
         '''        "coverage": round(cov, 3), "cov_warn": cov < 3.0, "capital_usd": round(last["cum_vol"], 2),
        "capital_needed": round(last["cum_vol"], 2) if is_buy else round(last["cum_qty"], 6),'''),
        ('''    if str(cfg.get("dca_type") or "") == "dca_plus":         # ⚡ v3.36.57: DCA+ — من صفوف المالك''',
         '''    if str(cfg.get("dca_type") or "") in ("dca_plus", "dca_plus_buy"):   # ⚡ v3.36.57 · v3.36.59 (الشرائي): DCA+ — من صفوف المالك'''),
        # ── deploy
        ('''    _plus = None
    if str(data.get("dca_type") or "").strip() == "dca_plus":
        _plus, _why = _plus_rows_ok(data.get("plus_rows"))
        if _plus is None:
            return {"ok": False, "msg": _why}
        if len(_plus) < 2:
            return {"ok": False, "msg": "أضف أمر أمان واحداً على الأقل"}
        data = dict(data, base_order_qty=_plus[0]["q"], avg_order_qty=_plus[1]["q"], first_deviation=_plus[1]["d"], step_multiplier=1,
                    size_multiplier=1, max_safety_orders=len(_plus) - 1, take_profit_pct=_plus[0]["x"])''', '''    _plus = None
    _dt0 = str(data.get("dca_type") or "").strip()
    if _dt0 in ("dca_plus", "dca_plus_buy"):                       # ⚡ DCA+ البيعي · v3.36.59: والشرائي
        _plus, _why = _plus_rows_ok(data.get("plus_rows"))
        if _plus is None:
            return {"ok": False, "msg": _why}
        if len(_plus) < 2:
            return {"ok": False, "msg": "أضف أمر أمان واحداً على الأقل"}
        data = dict(data, base_order_qty=_plus[0]["q"], avg_order_qty=_plus[1]["q"], first_deviation=_plus[1]["d"], step_multiplier=1,
                    size_multiplier=1, max_safety_orders=len(_plus) - 1, take_profit_pct=_plus[0]["x"],
                    dca_type="dca_buy" if _dt0 == "dca_plus_buy" else "dca")'''),
        ('''    if _plus and dn_type == "dca":                                  # ⚡ DCA+ (بيعي)
        cfg.update({"dca_plus": True, "plus_rows": _plus})''', '''    if _plus:                                                      # ⚡ DCA+ (بيعي · شرائي)
        cfg.update({"dca_plus": True, "plus_rows": _plus})'''),
        ('''    _lbl = "DCA شرائي" if dn_type == "dca_buy" else ("DCA+ بيعي" if cfg.get("dca_plus") else "DCA بيعي")''',
         '''    _lbl = ("DCA+ شرائي" if cfg.get("dca_plus") else "DCA شرائي") if dn_type == "dca_buy" else ("DCA+ بيعي" if cfg.get("dca_plus") else "DCA بيعي")'''),
        # ── ✏️ edits from the table/chart: both directions
        ('''        if b["cfg"].get("bot_type") != "dca" or not b["cfg"].get("dca_plus"):''',
         '''        if b["cfg"].get("bot_type") not in ("dca", "dca_buy") or not b["cfg"].get("dca_plus"):'''),
        # ── the trial path · the demo
        ('''    if body.get("dca_type") is not None:
        return "dca_buy" if str(body.get("dca_type")) == "dca_buy" else "dca"''', '''    if body.get("dca_type") is not None:
        return "dca_buy" if str(body.get("dca_type")) in ("dca_buy", "dca_plus_buy") else "dca"'''),
        ('''            b["dca_type"] = "dca_plus" if kind == "dca" and str(body.get("dca_type") or "") == "dca_plus" else kind   # ⚡ DCA+ من النموذج''',
         '''            b["dca_type"] = ({"dca": "dca_plus", "dca_buy": "dca_plus_buy"}[kind] if str(body.get("dca_type") or "") in ("dca_plus", "dca_plus_buy")
                             else kind)                                            # ⚡ DCA+ (البيعي · الشرائي) من النموذج'''),
        ('''        if kind == "dca" and ((cfg or {}).get("dca_plus") or str(g.get("dca_type") or "") == "dca_plus"):''',
         '''        if kind == "dca_buy" and ((cfg or {}).get("dca_plus") or str(g.get("dca_type") or "") == "dca_plus_buy"):
            _pr, _pw = _plus_rows_ok(g.get("plus_rows"))              # ⚡ v3.36.59: DCA+ الشرائي — دولار كل صف بسعره
            if _pr:
                _p, _usd = float(p0), 0.0
                for _i, _r in enumerate(_pr):
                    if _i:
                        _p *= 1 - _r["d"] / 100.0
                    _usd += _p * _r["q"]
                return round(_usd * 1.03 + 1.0, 2), 0.0
        if kind == "dca" and ((cfg or {}).get("dca_plus") or str(g.get("dca_type") or "") == "dca_plus"):'''),
        ('''    if kind == "dca_plus":                                   # ⚡ v3.36.57: DCA+ = البيعي بصفوف المالك
        kind = "dca"''', '''    if kind in ("dca_plus", "dca_plus_buy"):                 # ⚡ v3.36.57: DCA+ = البيعي بصفوف المالك · v3.36.59: والشرائي
        kind = "dca" if kind == "dca_plus" else "dca_buy"'''),
        ('''    if cfg.get("dca_plus"):
        _lbl = "⚡ DCA+ بيعي"''', '''    if cfg.get("dca_plus"):
        _lbl = "⚡ DCA+ شرائي" if cfg.get("bot_type") == "dca_buy" else "⚡ DCA+ بيعي"'''),
    ]
    for i, (a, b2) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b2)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · DCA+ الشرائي on the server (engine · deploy · preview · edits · trial · demo) · compiles · {p}")
