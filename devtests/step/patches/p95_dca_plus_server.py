# ⚡ patch 95 (dashboard v3.36.57 · the new DCA+ — the server side; applied on the v3.36.55 dashboard: the layered DCA+ of patches 92–93
#   is NOT carried over). The free ladder (patch 94's engine) inside the dashboard:
#   · `_DCAP_B64` · DCAP_SRC · DCAP_VERSION · `engine_for`: a sell DCA with dca_plus ⇒ dca_plus.py (the normal sell DCA keeps dca.py)
#   · `_plus_rows_ok` (the same rules as the engine) · deploy_dca: «dca_type: dca_plus» + plus_rows [{d, q, x}] — the classic fields
#     follow from the rows (base = row 1 · safety count = rows − 1 …) so every place that reads a DCA's settings still reads them
#   · the deploy preview (`compute_dca_table`): the rows' own distances, sizes and exit % — per row the average, the exit if it gets
#     there, the drop it needs, the net profit (the same fees as the engine)
#   · the card: each table row's exit = its own row's exit % (`_dca_live`) · `_dca_snapshot` «plus» = the rows · the filled orders
#     (locked) · the base price · an edit still waiting for the engine · an edit the engine refused
#   · control «plus_edit» (from the table or the chart while it runs): the rows checked · the orders filled this cycle keep their
#     distance and size (only their exit % can change) and cannot be removed · written to the bot's config (the next start reads them)
#     and to its state (the engine applies them within seconds) — state fields only: the engine sends the orders
#   · the chart's candles: POST /api/candles {sym, bar} (OKX public market data · 60 s cache · nothing private)
#   · the trial path and the demo take DCA+ from the form (the sell DCA's kind with the rows)
#   python3 devtests/step/patches/p95_dca_plus_server.py Holy_Dashboard.pyw devtests/step/eng/dca_plus.py
import base64, os, sys, zlib

HELP = '''def _dca_tp(cfg):'''
HELP_NEW = '''PLUS_MAX_ROWS = 101          # ⚡ v3.36.57 DCA+: الأساس + 100 أمر أمان (نفس DCA_MAX_SAFETY)


def _plus_rows_ok(rows):
    """⚡ DCA+: صفوف السلّم الحر سليمة؟ ⇒ (صفوف نظيفة، "") أو (None، السبب) — نفس قواعد المحرك (plus_rows_ok)"""
    if isinstance(rows, str):
        try:
            rows = json.loads(rows)
        except Exception:
            return None, "صفوف الأوامر غير صالحة"
    if not isinstance(rows, list) or not (1 <= len(rows) <= PLUS_MAX_ROWS):
        return None, f"عدد الأوامر بين 2 و{PLUS_MAX_ROWS}"
    out = []
    for i, r in enumerate(rows):
        try:
            d, q, x = float((r or {}).get("d") or 0), float((r or {}).get("q") or 0), float((r or {}).get("x") or 0)
        except Exception:
            return None, f"أرقام الصف {i + 1} غير صالحة"
        if not all(v == v and abs(v) != float("inf") for v in (d, q, x)):
            return None, f"أرقام الصف {i + 1} غير صالحة"
        if q <= 0 or x <= 0 or x > 50 or (i > 0 and not (0 < d <= 50)):
            return None, f"الصف {i + 1}: الكمية أكبر من صفر · المسافة بين 0 و50% · نسبة الخروج بين 0 و50%"
        out.append({"d": 0.0 if i == 0 else round(d, 6), "q": q, "x": round(x, 6)})
    return out, ""


def _plus_tp_n(cfg, n):
    """⚡ DCA+: هدف الصف n (كسر عشري) — لا ينزل تحت 0.20% مثل المحرك"""
    rows, _w = _plus_rows_ok(cfg.get("plus_rows"))
    if not rows:
        return _dca_tp(cfg)
    return max(float(rows[min(max(0, int(n)), len(rows) - 1)]["x"]), 0.20) / 100.0


def _plus_locked(st):
    """أوامر هذه الدورة اللي نفّذت (لا تتحرك)"""
    out = set()
    if (st or {}).get("phase") not in ("selling", "buying"):
        return out
    for f in (st.get("filled") or []):
        try:
            k = int(f.get("n", 0))
            out |= set(int(x) for x in (f.get("ns") or [])) if k < 0 else {k}
        except Exception:
            pass
    return out


def _plus_table(cfg, base_price):
    """⚡ DCA+: جدول المعاينة من صفوف المالك — لكل صف: لو وصل السعر لهالأمر ورجع لخروجه (صافي بعد العمولة كالمحرك)"""
    rows, why = _plus_rows_ok(cfg.get("plus_rows"))
    if rows is None:
        return {"rows": [], "msg": why}
    if base_price <= 0:
        return []
    trail = str(cfg.get("trail_on")).lower() in ("1", "true", "on", "yes")
    f_lv = DCA_FEE_TAKER if trail else DCA_FEE_MAKER
    out, cq, cv, cnet, p = [], 0.0, 0.0, 0.0, float(base_price)
    for i, r in enumerate(rows):
        if i:
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
                    "gap": round(abs(tgt - avg), 10), "x": r["x"], "x_used": x_used})
    last, first = out[-1], out[0]
    cov = (last["price"] / base_price - 1) * 100
    gaps = [r["gap_pct"] for r in out]
    return {"rows": out, "summary": {
        "is_buy": False, "trail": trail, "plus": True, "tp_used": round(rows[0]["x"], 3), "fee_warn": any(r["x"] < 0.20 for r in rows),
        "low_rows": [r["n"] for r in out if r["exit_profit"] <= 0],
        "coverage": round(cov, 3), "cov_warn": cov < 3.0, "capital_needed": round(last["cum_qty"], 6), "capital_usd": round(last["cum_vol"], 2),
        "max_exit": round(max(gaps), 3), "avg_exit": round(sum(gaps) / len(gaps), 3), "profit_base": first["exit_profit"],
        "profit_full": last["exit_profit"], "profit_full_usd": last["exit_usd"], "final_avg": last["avg"], "final_target": last["target"],
        "last_price": last["price"], "fee_maker": DCA_FEE_MAKER * 100, "fee_taker": DCA_FEE_TAKER * 100,
        "drop_needed": round(last["gap_pct"], 3), "coin_profit": last["exit_profit"], "total_sold": last["cum_qty"], "total_usdt": last["cum_vol"]}}


_CANDLES = {}


def candles_view(data):
    """📈 v3.36.57: شموع السعر لرسم DCA+ (بيانات OKX العامة · بلا مفاتيح · ذاكرة 60 ثانية)"""
    sym = str((data or {}).get("sym") or "").strip().upper()
    bar = str((data or {}).get("bar") or "1H")
    if not re.fullmatch(r"[A-Z0-9]{2,15}-[A-Z]{2,10}", sym) or bar not in ("15m", "1H", "4H", "1D"):
        return {"ok": False, "rows": [], "msg": "طلب غير صالح"}
    k = (sym, bar)
    c = _CANDLES.get(k)
    if c and time.time() - c[0] < 60:
        return {"ok": True, "rows": c[1]}
    r = _okx_pub(f"/api/v5/market/candles?instId={sym}&bar={bar}&limit=168")
    rows = []
    for x in ((r or {}).get("data") or [])[::-1]:
        try:
            rows.append([int(x[0]) // 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4])])
        except Exception:
            pass
    if rows:
        _CANDLES[k] = (time.time(), rows)
    return {"ok": bool(rows), "rows": rows}


def _dca_tp(cfg):'''

CTL = '''    if action == "plus_edit":                                 # ⚡ v3.36.57: DCA+ — الأوامر من الجدول/الرسم والبوت شغّال (حقول فقط — المحرك يرسل)
        if b["cfg"].get("bot_type") != "dca" or not b["cfg"].get("dca_plus"):
            return {"ok": False, "msg": "تعديل الأوامر لبوتات DCA+ فقط"}
        rows, why = _plus_rows_ok((value or {}).get("rows") if isinstance(value, dict) else None)
        if rows is None:
            return {"ok": False, "msg": why}
        if len(rows) < 2:
            return {"ok": False, "msg": "أضف أمر أمان واحداً على الأقل"}
        sp, _, _ = paths_of(b)
        stt = load_json(sp) or {}
        old, _w = _plus_rows_ok(b["cfg"].get("plus_rows"))
        old = old or []
        locked = _plus_locked(stt)
        if locked and max(locked) >= len(rows):
            return {"ok": False, "msg": "لا يمكن حذف أمر نُفّذ في هذه الدورة"}
        for n_ in locked:
            if n_ < len(old):
                rows[n_]["d"], rows[n_]["q"] = old[n_]["d"], old[n_]["q"]     # المنفّذة: مسافتها وكميتها كما هي (نسبة خروجها تتغيّر)
        write_cfg_keys(b["cfg_path"], {"plus_rows": rows, "base_order_qty": rows[0]["q"], "avg_order_qty": rows[1]["q"],
                                       "first_deviation": rows[1]["d"], "max_safety_orders": len(rows) - 1, "take_profit_pct": rows[0]["x"]})
        upd = {"plus_edit": {"seq": int(time.time() * 1000), "rows": rows}}
        if not save_state_keys(sp, upd):
            stt.update(upd)
            save_json_atomic(sp, stt)
        return {"ok": True, "msg": "✏️ حُفظت الأوامر — يطبّقها البوت خلال ثوانٍ (المنفّذة في هذه الدورة تبقى بأسعارها)"}
    if action in ("trail_on", "trail_off"):
        if b["cfg"].get("bot_type") not in ("dca", "dca_buy"):
            return {"ok": False, "msg": "الدرع لبوتات DCA فقط"}'''

if __name__ == "__main__":
    p, eng = sys.argv[1], sys.argv[2]
    s = open(p, encoding="utf-8").read()
    src = open(eng, encoding="utf-8").read()
    compile(src, eng, "exec")
    b64 = base64.b64encode(zlib.compress(src.encode("utf-8"), 9)).decode()
    lit = "\n".join('"' + b64[i:i + 120] + '"' for i in range(0, len(b64), 120))
    R = [
        (HELP, HELP_NEW),
        ('''DCAB_SRC = _zlib.decompress(_b64.b64decode(_DCAB_B64)).decode("utf-8")
DCAB_VERSION = _eng_fp(DCAB_SRC)
''', '''DCAB_SRC = _zlib.decompress(_b64.b64decode(_DCAB_B64)).decode("utf-8")
DCAB_VERSION = _eng_fp(DCAB_SRC)

# ⚡ v3.36.57: DCA+ — البيعي بسلّم حر (كل أمر بمسافته وكميته ونسبة خروجه) · نسخة من dca.py — الأصل ما تغيّر · devtests/step/eng/dca_plus.py
_DCAP_B64 = (
''' + lit + '''
)
DCAP_SRC = _zlib.decompress(_b64.b64decode(_DCAP_B64)).decode("utf-8")
DCAP_VERSION = _eng_fp(DCAP_SRC)
'''),
        ('''    if bt == "dca":
        return DCA_SRC, "dca.py", DCA_VERSION''', '''    if bt == "dca":
        if cfg.get("dca_plus"):                              # ⚡ v3.36.57: DCA+ (البيعي بسلّم حر)
            return DCAP_SRC, "dca.py", DCAP_VERSION
        return DCA_SRC, "dca.py", DCA_VERSION'''),
        # deploy: the rows (checked before any folder is made)
        ('''def deploy_dca(data):
    """ينشئ بوت DCA بإعدادات نمط 3Commas"""
    sym = str(data.get("symbol", "")).strip().upper()
    if not sym or "-" not in sym:
        return {"ok": False, "msg": "اكتب الرمز كاملاً مثل XRP-USDT"}''', '''def deploy_dca(data):
    """ينشئ بوت DCA بإعدادات نمط 3Commas · ⚡ v3.36.57: DCA+ = صفوف المالك (plus_rows)"""
    sym = str(data.get("symbol", "")).strip().upper()
    if not sym or "-" not in sym:
        return {"ok": False, "msg": "اكتب الرمز كاملاً مثل XRP-USDT"}
    _plus = None
    if str(data.get("dca_type") or "").strip() == "dca_plus":
        _plus, _why = _plus_rows_ok(data.get("plus_rows"))
        if _plus is None:
            return {"ok": False, "msg": _why}
        if len(_plus) < 2:
            return {"ok": False, "msg": "أضف أمر أمان واحداً على الأقل"}
        data = dict(data, base_order_qty=_plus[0]["q"], avg_order_qty=_plus[1]["q"], first_deviation=_plus[1]["d"], step_multiplier=1,
                    size_multiplier=1, max_safety_orders=len(_plus) - 1, take_profit_pct=_plus[0]["x"])'''),
        ('''    cfg = {**keys, "symbol": sym, "bot_type": dn_type, **fields,
           "auto_restart": bool(data.get("auto", True))}''', '''    cfg = {**keys, "symbol": sym, "bot_type": dn_type, **fields,
           "auto_restart": bool(data.get("auto", True))}
    if _plus and dn_type == "dca":                                  # ⚡ DCA+ (بيعي)
        cfg.update({"dca_plus": True, "plus_rows": _plus})'''),
        ('''    _lbl = "DCA شرائي" if dn_type == "dca_buy" else "DCA بيعي"''',
         '''    _lbl = "DCA شرائي" if dn_type == "dca_buy" else ("DCA+ بيعي" if cfg.get("dca_plus") else "DCA بيعي")'''),
        ('''                     "exitp": round(exitp, 3), "prof": round(prof, 6 if is_buy else 4), "cq": round(cq, 4), "cv": round(cv, 2)})
''', '''                     "exitp": round(exitp, 3), "prof": round(prof, 6 if is_buy else 4), "cq": round(cq, 4), "cv": round(cv, 2)})
        if cfg.get("plus_rows"):
            rows[-1]["x"] = round(_tpn * 100, 3)                # ⚡ DCA+: نسبة خروج هذا الصف
'''),
        # the preview
        ('''def compute_dca_table(cfg, base_price):
    """📋 v3.22.1 (ح٥): جدول خطة DCA قبل النشر''', '''def compute_dca_table(cfg, base_price):
    if str(cfg.get("dca_type") or "") == "dca_plus":         # ⚡ v3.36.57: DCA+ — من صفوف المالك
        return _plus_table(cfg, base_price)
    return _dca_table_classic(cfg, base_price)


def _dca_table_classic(cfg, base_price):
    """📋 v3.22.1 (ح٥): جدول خطة DCA قبل النشر'''),
        # the card's table: each row's own exit
        ('''        tgt = avg * (1 + tp) if is_buy else avg * (1 - tp)''',
         '''        _tpn = _plus_tp_n(cfg, n) if cfg.get("plus_rows") else tp     # ⚡ DCA+: هدف صفّه هو
        tgt = avg * (1 + _tpn) if is_buy else avg * (1 - _tpn)'''),
        ('''    _ts, _tt = st.get("trail_s") or {}, st.get("trail_t") or {}
''', '''    _ts, _tt = st.get("trail_s") or {}, st.get("trail_t") or {}
    plus = None
    if cfg.get("dca_plus"):                                     # ⚡ v3.36.57: DCA+ — الصفوف · المنفّذة · سعر الأساس · تعديل ينتظر
        _pr, _pw = _plus_rows_ok(cfg.get("plus_rows"))
        _pe = st.get("plus_edit") if isinstance(st.get("plus_edit"), dict) else {}
        plus = {"rows": _pr or [], "locked": sorted(_plus_locked(st)), "base": _pv_sig(float(st.get("base_price") or 0)),
                "pending": bool(_pe.get("seq") is not None and str(_pe.get("seq")) != str(st.get("plus_seq"))),
                "err": str(st.get("plus_edit_err") or "")}
'''),
        ('''        "is_buy": is_buy,
        "cycles": int(st.get("cycles_done") or 0),''', '''        "is_buy": is_buy, "plus": plus,
        "cycles": int(st.get("cycles_done") or 0),'''),
        ('''    if action in ("trail_on", "trail_off"):
        if b["cfg"].get("bot_type") not in ("dca", "dca_buy"):
            return {"ok": False, "msg": "الدرع لبوتات DCA فقط"}''', CTL),
        # the chart's candles
        ('''        if path == "/api/dca_preview":''', '''        if path == "/api/candles":                                # 📈 v3.36.57: شموع رسم DCA+ (بيانات عامة)
            return self._json(_safe(candles_view, data, default={"ok": False, "rows": []}))
        if path == "/api/dca_preview":'''),
        # the trial/demo wallet: the coins the rows need (the classic formula would count every safety order at row 1's size)
        ('''        if kind in ("dca", "dca_buy"):
            bq, aq, sm, n = f("base_order_qty", 0)''', '''        if kind == "dca" and ((cfg or {}).get("dca_plus") or str(g.get("dca_type") or "") == "dca_plus"):
            _pr, _pw = _plus_rows_ok(g.get("plus_rows"))              # ⚡ v3.36.57: DCA+ — مجموع كميات الصفوف
            if _pr:
                return 0.0, round(sum(r["q"] for r in _pr) * 1.02, 8)
        if kind in ("dca", "dca_buy"):
            bq, aq, sm, n = f("base_order_qty", 0)'''),
        # the trial path and the demo from the form
        ('''        elif kind in ("dca", "dca_buy"):
            b["dca_type"] = kind''', '''        elif kind in ("dca", "dca_buy"):
            b["dca_type"] = "dca_plus" if kind == "dca" and str(body.get("dca_type") or "") == "dca_plus" else kind   # ⚡ DCA+ من النموذج'''),
        ('''    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    if kind not in _BT_KINDS:''', '''    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    if kind == "dca_plus":                                   # ⚡ v3.36.57: DCA+ = البيعي بصفوف المالك
        kind = "dca"
    if kind not in _BT_KINDS:'''),
        ('''    _lbl = (_BOT_KINDS.get(kind) or {}).get("ico", "") + " " + (_BOT_KINDS.get(kind) or {}).get("lbl", kind)
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق بوت ديمو ({_lbl.strip()})''', '''    _lbl = (_BOT_KINDS.get(kind) or {}).get("ico", "") + " " + (_BOT_KINDS.get(kind) or {}).get("lbl", kind)
    if cfg.get("dca_plus"):
        _lbl = "⚡ DCA+ بيعي"
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق بوت ديمو ({_lbl.strip()})'''),
    ]
    for i, (a, b2) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b2)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the free-ladder DCA+ on the server (engine · deploy · preview · card · edits · candles · demo/trial) · compiles · {p}")
