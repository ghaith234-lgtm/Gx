# p148 — v3.36.79 🔀 «شبكة عملتين» · ③ notices and the remaining places that read a bot's total profit
#   · Telegram: one message per completed sale (like ♾️ — the owner chose it) in the MAIN coin («💎 ربح الدورة +0.31 XRP ≈ 0.62$»)
#     — never «$» on an XRP number · a buy sends nothing (like ♾️) · the demo sends nothing (the loop skips it already)
#   · the dollar reconciliation (`reconcile`) and the all-time dollar total (`alltime_view`) skip it (its profit is XRP — the coin books)
#   · the export (`export_md`) writes its profit in its main coin · the archive keeps its profit as a coin ({XRP: …}) like DCA
#   python3 devtests/step/patches/p148_pair_notices.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''                    continue  # DCA لا يستعمل منطق الدولار أدناه
''', '''                    continue  # DCA لا يستعمل منطق الدولار أدناه
                if b["cfg"].get("bot_type") == "grid_pair":      # 🔀 v3.36.79: إشعار لكل بيعة مكتملة — بالعملة الرئيسية (لا «$» على رقم XRP)
                    _lt = st.get("last_trade") or {}
                    _o, _mn = _pair_parts(b)
                    _n = int(_lt.get("n") or 0)
                    if prev.get("pair_n") is None:
                        prev["pair_n"] = _n                       # أول مرة: ما ينعاد القديم
                    elif _n > int(prev.get("pair_n") or 0):
                        if _lt.get("side") == "sell":
                            _p, _pm, _tp = float(_lt.get("profit") or 0), float(st.get("px_main") or 0), float(st.get("total_profit") or 0)
                            _kp = float(_lt.get("kept") or 0)
                            tg_send(f"🔀 *ربح محقّق — شبكة عملتين `{_o}/{_mn}`* 🤑\\n"
                                    f"━━━━━━━━━━━━━\\n"
                                    f"🔴 باع: `{float(_lt.get('qty') or 0):.8g}` {_o} ⇐ `{float(_lt.get('main') or 0):.8g}` {_mn}\\n"
                                    f"⚖️ النسبة: `{float(_lt.get('ratio') or 0):.8g}` {_mn} لكل {_o}\\n"
                                    f"💎 ربح الدورة: `{_p:+.8g}` {_mn}" + (f" + `{_kp:.8g}` {_o}" if _kp > 0 else "")
                                    + (f" (≈ `{_p * _pm:.4f}$`)" if _pm > 0 else "") + "\\n"
                                    f"━━━━━━━━━━━━━\\n"
                                    f"📊 إجمالي الربح: `{_tp:.8g}` {_mn}" + (f" (≈ `{_tp * _pm:.2f}$`)" if _pm > 0 else ""))
                        prev["pair_n"] = _n
                    continue                                       # 🔀 لا يستعمل منطق الدولار أدناه
'''),
    ('''            sp, _, _ = paths_of(b)
            st = _safe(load_json, sp, default={}) or {}
            px = float(b.get("cp") or st.get("current_price") or 0)
            pos = position_of(b, st, px)''', '''            if str((b.get("cfg") or {}).get("bot_type") or "") == "grid_pair":
                continue                                   # 🔀 v3.36.79: ربحه وعملاته بالرئيسية ⇒ دفتر العملات (لا مطابقة الدولار)
            sp, _, _ = paths_of(b)
            st = _safe(load_json, sp, default={}) or {}
            px = float(b.get("cp") or st.get("current_price") or 0)
            pos = position_of(b, st, px)'''),
    ('''        if bt == "dca":
            continue                                   # 📒 v3.22.6: ربح عملة DCA البيعي من دفتر العملات''',
     '''        if bt in ("dca", "grid_pair"):
            continue                                   # 🔀 v3.36.79: شبكة عملتين ربحها بالرئيسية · 📒 v3.22.6: ربح عملة DCA البيعي من دفتر العملات'''),
    ('''        elif bt in ("dca", "dca_buy"):
            pr = float(st.get("total_coin_profit") or 0)
            unit = "USDT" if bt == "dca_buy" else b["symbol"].split("-")[0]
        else:''', '''        elif bt in ("dca", "dca_buy"):
            pr = float(st.get("total_coin_profit") or 0)
            unit = "USDT" if bt == "dca_buy" else b["symbol"].split("-")[0]
        elif bt == "grid_pair":                              # 🔀 v3.36.79: بالعملة الرئيسية
            pr = float(st.get("total_profit") or 0)
            unit = _pair_parts(b)[1]
        else:'''),
    ('''    if bt == "dca":
        e["coin"] = {base: round(float(st.get("total_coin_profit") or 0), 10)}
    elif bt == "dca_buy":''', '''    if bt == "dca":
        e["coin"] = {base: round(float(st.get("total_coin_profit") or 0), 10)}
    elif bt == "grid_pair":                                # 🔀 v3.36.79: ربحه عملة (الرئيسية)
        e["coin"] = {_pair_parts(b)[1]: round(float(st.get("total_profit") or 0), 10)}
    elif bt == "dca_buy":'''),
    ('''            if not ge and str(cfg.get("bot_type") or "grid") not in ("dca", "dca_buy") and not cfg.get("is_demo"):
                stx = _safe(load_json, os.path.join(d, f"grid_state_{cfg.get('symbol')}.json"), default={}) or {}
                it["rel"] = round(float(stx.get("total_profit") or 0), 8)''',
     '''            if not ge and str(cfg.get("bot_type") or "grid") not in ("dca", "dca_buy") and not cfg.get("is_demo"):
                stx = _safe(load_json, os.path.join(d, f"grid_state_{cfg.get('symbol')}.json"), default={}) or {}
                if str(cfg.get("bot_type") or "") == "grid_pair":     # 🔀 v3.36.79: ربحه عملة
                    it["coin"] = {_pair_parts({"symbol": cfg.get("symbol")})[1]: round(float(stx.get("total_profit") or 0), 10)}
                else:
                    it["rel"] = round(float(stx.get("total_profit") or 0), 8)'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 🔀 one notice per sale in the main coin · kept out of the dollar reconcile/all-time · export and archive in the coin · {p}")
