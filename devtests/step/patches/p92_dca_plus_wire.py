# ⚡ patch 92 (dashboard v3.36.56 · DCA+) — the DCA+ engine inside the dashboard and chosen for a DCA+ bot:
#   · `_DCAP_B64` (devtests/step/eng/dca_plus.py — patch 91) · DCAP_SRC · DCAP_VERSION
#   · DCA+ = a sell DCA (bot_type «dca» — the same books, card and profit route, so every place that counts the sell DCA counts it)
#     with `dca_plus: true` in its config ⇒ `engine_for` gives it dca_plus.py (the normal sell DCA keeps dca.py, byte for byte)
#   · deploy_dca: «dca_type: dca_plus» (or dca_plus=1) ⇒ the layered-exit settings: lx_on · lx_pct (0.3–10%) · lx_from · lx_reopen
#   python3 devtests/step/patches/p92_dca_plus_wire.py Holy_Dashboard.pyw devtests/step/eng/dca_plus.py
import base64, os, sys, zlib

if __name__ == "__main__":
    p, eng = sys.argv[1], sys.argv[2]
    s = open(p, encoding="utf-8").read()
    src = open(eng, encoding="utf-8").read()
    compile(src, eng, "exec")
    b = base64.b64encode(zlib.compress(src.encode("utf-8"), 9)).decode()
    lit = "\n".join('"' + b[i:i + 120] + '"' for i in range(0, len(b), 120))
    R = [
        ('''DCAB_SRC = _zlib.decompress(_b64.b64decode(_DCAB_B64)).decode("utf-8")
DCAB_VERSION = _eng_fp(DCAB_SRC)
''',
         '''DCAB_SRC = _zlib.decompress(_b64.b64decode(_DCAB_B64)).decode("utf-8")
DCAB_VERSION = _eng_fp(DCAB_SRC)

# ⚡ v3.36.56: DCA+ — البيعي + الخروج بالطبقات (نسخة من dca.py بإضافة ج1 · الأصل ما تغيّر · devtests/step/eng/dca_plus.py)
_DCAP_B64 = (
''' + lit + '''
)
DCAP_SRC = _zlib.decompress(_b64.b64decode(_DCAP_B64)).decode("utf-8")
DCAP_VERSION = _eng_fp(DCAP_SRC)
'''),
        ('''    if bt == "dca":
        return DCA_SRC, "dca.py", DCA_VERSION''',
         '''    if bt == "dca":
        if cfg.get("dca_plus"):                              # ⚡ v3.36.56: DCA+ (بيعي + الخروج بالطبقات)
            return DCAP_SRC, "dca.py", DCAP_VERSION
        return DCA_SRC, "dca.py", DCA_VERSION'''),
        ('''    if fields["take_profit_pct"] <= 0:
        return {"ok": False, "msg": "يجب أن يكون هدف الربح أكبر من صفر"}
''',
         '''    if fields["take_profit_pct"] <= 0:
        return {"ok": False, "msg": "يجب أن يكون هدف الربح أكبر من صفر"}
    # ⚡ v3.36.56: DCA+ (بيعي + الخروج بالطبقات) — يتحقق قبل ما ينعمل أي مجلد
    lx = {}
    if str(data.get("dca_type") or "").strip() == "dca_plus" or str(data.get("dca_plus") or "").lower() in ("1", "true", "on", "yes"):
        try:
            _lp = float(data.get("lx_pct") if data.get("lx_pct") not in (None, "") else 0.5)
            _lf = int(float(data.get("lx_from") if data.get("lx_from") not in (None, "") else 1))
        except Exception:
            return {"ok": False, "msg": "تأكد من أرقام الخروج بالطبقات"}
        if not (_lp == _lp) or _lp < 0.3 or _lp > 10:
            return {"ok": False, "msg": "ارتداد الخروج بالطبقات بين 0.3% و10% (أقل من 0.3% لا يغطي العمولة)"}
        if _lf < 1 or _lf > fields["max_safety_orders"]:
            return {"ok": False, "msg": f"الخروج بالطبقات يبدأ من أمر أمان بين 1 و{fields['max_safety_orders']}"}
        _rv = data.get("lx_reopen", True)
        lx = {"dca_plus": True, "lx_on": True, "lx_pct": round(_lp, 4), "lx_from": _lf,
              "lx_reopen": _rv is True or str(_rv).lower() in ("1", "true", "on", "yes")}
'''),
        ('''    dn_type = str(data.get("dca_type", "dca")).strip()
    if dn_type not in ("dca", "dca_buy"): dn_type = "dca"
    cfg = {**keys, "symbol": sym, "bot_type": dn_type, **fields,
           "auto_restart": bool(data.get("auto", True))}''',
         '''    dn_type = str(data.get("dca_type", "dca")).strip()
    if dn_type not in ("dca", "dca_buy"): dn_type = "dca"
    cfg = {**keys, "symbol": sym, "bot_type": dn_type, **fields,
           "auto_restart": bool(data.get("auto", True))}
    if lx and dn_type == "dca":                              # ⚡ DCA+ بيعي بهذا الإصدار
        cfg.update(lx)'''),
        ('''    _lbl = "DCA شرائي" if dn_type == "dca_buy" else "DCA بيعي"''',
         '''    _lbl = "DCA شرائي" if dn_type == "dca_buy" else ("DCA+ بيعي" if cfg.get("dca_plus") else "DCA بيعي")'''),
    ]
    for i, (a, b2) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b2)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · DCA+ engine inside ({len(src.splitlines())} lines) and chosen for dca_plus · compiles · {p}")
