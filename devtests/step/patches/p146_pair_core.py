# p146 — v3.36.79 🔀 «شبكة عملتين» · ① the core: the engine in the dashboard and the type in every book that must know it
#   The owner 27-11: «سوي البوت وضيفه … xrp عملة رىيسية … الكمية راح تنحسب بالxrp مثل انفنتي العادي ينحسب بالدولار» · «واحد لكل عملة ·
#   يستعمل الي موجود بالمحفظة · يحسبها مثل الحاسبة · كله للxrp · شبكة عملتين» · «ولا بوت لازم ياخذ هذا الدولار» · «لعد خليه بدون نشر على المنصه».
#   · the engine: devtests/pair/eng/main_pair.py (new — no other engine touched) embedded as `_GRIDX_B64` · `engine_for` grid_pair ⇒ main.py
#   · `_BOT_KINDS["grid_pair"]`: profit in a COIN (the main coin) · its own family «pair» (not «grid»: a grid is a dollar source)
#     ⇒ `_NONGRID` includes it (no grid ladder · no reinvest wrapper · no ladder audit) — the kinds audit reads the same table
#   · ⚠️ the dollar ledger (`ledger_tick`) books the total_profit of any type that is not DCA/recurring AS DOLLARS ⇒ grid_pair is skipped
#     there (its profit is XRP — it goes to the coin books, p147)
#   · `net_factor` = 1 (the engine books the real net from every fill, four fees included)
#   · the card's data: today = the engine's own day book · `pair` = everything the card needs (ratio · the two next orders · the books ·
#     the dollar booked · profit in the main coin and ≈ $ · per day · the last swaps · the levels · the wallet counted in the main coin)
#   · `_gd_free_claims`: the bot holds ALL its coins free in the wallet (nothing rests on the exchange) ⇒ main + other + the dollar booked
#     ⇒ no other bot / deploy may count them as free
#   · prices: `SOL-XRP` is no OKX instrument ⇒ the price loop asks for its two USDT legs and writes the ratio itself
#   python3 devtests/step/patches/p146_pair_core.py Holy_Dashboard.pyw
import base64, os, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(HERE, "..", "..", "pair", "eng", "main_pair.py")


def literal(var, path, width=120):
    src = open(path, encoding="utf-8").read()
    compile(src, path, "exec")
    b = base64.b64encode(zlib.compress(src.encode("utf-8"), 9)).decode("ascii")
    assert zlib.decompress(base64.b64decode(b)).decode("utf-8") == src
    return var + " = (\n" + "\n".join('"' + b[i:i + width] + '"' for i in range(0, len(b), width)) + "\n)\n"


R = [
    # ① the engine literal right after the graded grid's
    ('GRIDS_VERSION = _eng_fp(GRIDS_SRC)\n',
     'GRIDS_VERSION = _eng_fp(GRIDS_SRC)\n'
     '# 🔀 v3.36.79: محرك «شبكة عملتين» (جديد — عملة رئيسية مثل الدولار · رجلان عبر الدولار بأمر فوري · ولا أمر قاعد على المنصة) — يُكتب\n'
     '#   بمجلد البوت باسم main.py · المصدر devtests/pair/eng/main_pair.py · يتغيّر بـ devtests/step/embed_engine.py … --var=_GRIDX_B64 فقط\n'
     + "@@LIT@@" +
     'GRIDX_SRC = _zlib.decompress(_b64.b64decode(_GRIDX_B64)).decode("utf-8")\n'
     'GRIDX_VERSION = _eng_fp(GRIDX_SRC)\n'),
    ('''    if bt == "grid_step":
        return GRIDS_SRC, "main.py", GRIDS_VERSION          # 🪜 v3.36.15: الشبكي المتدرج
''', '''    if bt == "grid_step":
        return GRIDS_SRC, "main.py", GRIDS_VERSION          # 🪜 v3.36.15: الشبكي المتدرج
    if bt == "grid_pair":
        return GRIDX_SRC, "main.py", GRIDX_VERSION          # 🔀 v3.36.79: شبكة عملتين
'''),
    # ② the type
    ('''                   "route": ("events", "ledger", "trade", "released", "box", "report")},      # 🪜 v3.36.15: الشبكي المتدرج (بلا 💠 بهذا الإصدار)
''', '''                   "route": ("events", "ledger", "trade", "released", "box", "report")},      # 🪜 v3.36.15: الشبكي المتدرج (بلا 💠 بهذا الإصدار)
    "grid_pair":  {"lbl": "شبكة عملتين", "ico": "🔀", "cur": "coin", "src": "hist",   "unit": "بيعة", "fam": "pair", "state": "grid_state_", "eng": "GRIDX_SRC",
                   "route": ("events", "coin_ledger", "coin_trade", "report")},      # 🔀 v3.36.79: ربحه بالعملة الرئيسية (ثاني جزء من الرمز: SOL-XRP ⇒ XRP)
'''),
    ('''           ("_NONGRID", set(globals().get("_NONGRID") or ()), set(_kinds(fam=("dca", "rec")))),''',
     '''           ("_NONGRID", set(globals().get("_NONGRID") or ()), set(_kinds(fam=("dca", "rec", "pair")))),'''),
    ('''_NONGRID = _kinds(fam=("dca", "rec"))        # بوتات بلا سلّم شبكة''',
     '''_NONGRID = _kinds(fam=("dca", "rec", "pair"))   # 🔀 v3.36.79: + شبكة عملتين · بوتات بلا سلّم شبكة'''),
    # ③ the dollar ledger skips it (its profit is the main coin, never dollars)
    ('''        if b["cfg"].get("is_demo") or b["cfg"].get("bot_type") == "dca":''',
     '''        if b["cfg"].get("is_demo") or b["cfg"].get("bot_type") in ("dca", "grid_pair"):     # 🔀 v3.36.79: ربحه XRP ⇒ دفتر العملات (لا الدولار)'''),
    ('''    if str(b["cfg"].get("bot_type") or "") == "grid_step":
        return 1.0                          # 🪜 v3.36.15: المحرك يكتب الربح الصافي الحقيقي (العمولتين من التنفيذ نفسه)''',
     '''    if str(b["cfg"].get("bot_type") or "") in ("grid_step", "grid_pair"):
        return 1.0                          # 🪜 v3.36.15: المحرك يكتب الربح الصافي الحقيقي (العمولتين من التنفيذ نفسه) · 🔀 الأربع'''),
    # ④ the card's data
    ('''    if (_bt in ("dca", "dca_buy") and st.get("cycles_log")) or _bt in _REC_T:   # 🔁 الدوري: نفس سجل الصفقات''',
     '''    if _bt == "grid_pair":                       # 🔀 v3.36.79: ربح اليوم من دفتر المحرك نفسه (بالعملة الرئيسية)
        try:
            today_profit = float((st.get("daily") or {}).get(today) or 0)
        except Exception:
            today_profit = 0.0
    elif (_bt in ("dca", "dca_buy") and st.get("cycles_log")) or _bt in _REC_T:   # 🔁 الدوري: نفس سجل الصفقات'''),
    ('''            "bot_type": b["cfg"].get("bot_type", "grid"),
''', '''            "bot_type": b["cfg"].get("bot_type", "grid"),
            "pair": (_safe(_pair_snapshot, b, st, default=None) if _bt == "grid_pair" else None),     # 🔀 v3.36.79
'''),
    ('''def _dca_snapshot(b, st):''', '''def _pair_parts(b):
    """🔀 (الثانية · الرئيسية) من الرمز: SOL-XRP ⇒ (SOL, XRP)"""
    p = (str((b or {}).get("symbol") or "").upper().split("-") + ["", ""])[:2]
    return p[0], p[1]


def _pair_snapshot(b, st):
    """🔀 v3.36.79: بيانات بطاقة «شبكة عملتين» — كلها من حالة المحرك (المحرك ما يقرا شي منها)"""
    pr = st.get("pair") or {}
    oth, mn = _pair_parts(b)
    f = lambda x: float(x or 0)
    pm, po = f(st.get("px_main")), f(st.get("px_other"))
    r = f(st.get("ratio")) or (po / pm if pm > 0 and po > 0 else 0.0)
    tp = f(st.get("total_profit"))
    born = f(pr.get("born"))
    age = max(0.0, (time.time() - born) / 86400.0) if born else 0.0
    S = st.get("slots") or {}
    lv = sorted(({"j": s.get("j"), "bp": s.get("bp"), "sp": s.get("sp"), "side": s.get("side"),
                  "q": round(f(s.get("q")) + f(s.get("dq")), 12)} for s in S.values() if isinstance(s, dict)), key=lambda x: int(x["j"] or 0))
    w_now = f(st.get("main_book")) + f(st.get("other_book")) * r + (f(st.get("usd_booked")) / pm if pm > 0 else 0.0)
    w0 = f(st.get("main_start")) + f(st.get("other_start")) * f(pr.get("r0"))
    days = sorted((st.get("daily") or {}).items())
    return {"main": pr.get("main") or mn, "other": pr.get("other") or oth, "ratio": r, "r0": pr.get("r0"), "g": pr.get("g"), "mv": pr.get("mv"),
            "dn": pr.get("dn"), "up": pr.get("up"), "pt": pr.get("pt") or "main", "px_main": pm, "px_other": po,
            "next_buy": st.get("next_buy"), "next_sell": st.get("next_sell"), "n_buy": st.get("n_buy"), "n_sell": st.get("n_sell"),
            "main_book": f(st.get("main_book")), "other_book": f(st.get("other_book")), "usd_booked": f(st.get("usd_booked")),
            "profit": tp, "profit_usd": round(tp * pm, 6) if pm > 0 else None, "profit_other": f(st.get("profit_other")),
            "today": f((st.get("daily") or {}).get(time.strftime("%Y-%m-%d"))),
            "per_day": round(tp / age, 10) if age >= 0.5 else None, "age_days": round(age, 3),
            "days": [[k, v] for k, v in days[-31:]], "swaps": (st.get("swaps") or [])[-12:], "in_flight": bool(st.get("op")),
            "levels": lv[:600], "n_levels": len(lv), "wallet_main": round(w_now, 10), "wallet_main0": round(w0, 10),
            "wallet_pct": round((w_now / w0 - 1) * 100, 4) if w0 > 0 else None, "born": born,
            "destructing": bool(st.get("self_destruct")) and not st.get("destruct_done")}


def _dca_snapshot(b, st):'''),
    # ⑤ the coins it needs free (nothing of it rests in an exchange order)
    ('''        elif bt in ("dca", "dca_buy"):
            if st.get("phase") == "selling" and st.get("filled") and not st.get("close") and not st.get("pending_close_id"):''',
     '''        elif bt == "grid_pair":                 # 🔀 v3.36.79: كل ما يملكه حرّ بالمحفظة (لا أوامر قاعدة) ⇒ الرئيسية · الثانية · الدولار المحجوز
            oth, mn = _pair_parts(b)
            op = st.get("op") if isinstance(st.get("op"), dict) else {}
            m_ = float(st.get("main_book") or 0) - (float(op.get("sold") or 0) if op.get("kind") == "buy" else 0.0) \\
                + (float(op.get("got") or 0) if op.get("kind") == "sell" else 0.0)
            o_ = float(st.get("other_book") or 0) + (float(op.get("got") or 0) if op.get("kind") == "buy" else 0.0) \\
                - (float(op.get("sold") or 0) if op.get("kind") == "sell" else 0.0)
            quote_ = str((b.get("cfg") or {}).get("bridge") or "USDT")
            out[mn] = max(0.0, m_)
            out[oth] = max(0.0, o_)
            out[quote_] = max(0.0, float(st.get("usd_booked") or 0))
        elif bt in ("dca", "dca_buy"):
            if st.get("phase") == "selling" and st.get("filled") and not st.get("close") and not st.get("pending_close_id"):'''),
    # ⑥ prices: the two USDT legs of a pair, the ratio written by the dashboard
    ('''            _sy = {b["symbol"] for b in bot_dirs().values()}''',
     '''            _pairs = {}
            _sy = set()
            for _b in bot_dirs().values():
                if str((_b.get("cfg") or {}).get("bot_type") or "") == "grid_pair":     # 🔀 v3.36.79: SOL-XRP ليست أداة ⇒ ساقاها بالدولار
                    _o, _m = _pair_parts(_b)
                    _q = str((_b.get("cfg") or {}).get("bridge") or "USDT")
                    _pairs[_b["symbol"]] = (f"{_o}-{_q}", f"{_m}-{_q}")
                    _sy |= {f"{_o}-{_q}", f"{_m}-{_q}"}
                else:
                    _sy.add(_b["symbol"])'''),
    ('''            if syms:
                if got_any:''', '''            for _ps, (_lo, _lm) in _pairs.items():         # 🔀 النسبة = سعر الثانية ÷ سعر الرئيسية
                if float(PX.get(_lo) or 0) > 0 and float(PX.get(_lm) or 0) > 0:
                    PX[_ps] = float(PX[_lo]) / float(PX[_lm])
            if syms:
                if got_any:'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    lit = literal("_GRIDX_B64", ENG)
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b.replace("@@LIT@@", lit))
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
    print(f"✅ {len(R)} replacements · 🔀 the engine embedded · the type · the coin-profit books · the card data · the coins it holds · the pair prices · {p}")
