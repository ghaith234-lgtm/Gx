# p147 — v3.36.79 🔀 «شبكة عملتين» · ② its profit in the coin books (the main coin — never the dollar books)
#   The coin ledger had three sources (📉 DCA بيعي · 💠 تحرير إعادة الاستثمار · 🔁 الدوري) ⇒ a fourth: «pair» (🔀 شبكة عملتين).
#   · every sale of the engine (state «swaps», kind sell) = one event, once by its id («pair:<t×10>:<level>»), on its real day, in the
#     MAIN coin (SOL-XRP ⇒ XRP — the second part of the symbol, not the first like DCA)
#   · the coin ledger · the coin trade book · the period view · the all-time view · the report line · the reset · the guard's reconcile
#     and the diagnostics — all with the fourth source
#   python3 devtests/step/patches/p147_pair_coinbooks.py Holy_Dashboard.pyw
import os, sys

R = [
    # the helper: the engine's sales as coin events
    ('''def _pair_snapshot(b, st):''', '''def _pair_coin_events(st):
    """🔀 بيعات المحرك (state «swaps» · kind sell) ⇒ [(المعرّف، الربح بالرئيسية، الوقت، "pair")] — مرة وحدة لكل بيعة"""
    out = []
    for s in (st.get("swaps") or []):
        try:
            if isinstance(s, dict) and s.get("kind") == "sell":
                out.append((f"pair:{int(round(float(s.get('t') or 0) * 10))}:{int(s.get('j') or 0)}", float(s.get("profit") or 0), float(s.get("t") or 0), "pair"))
        except Exception:
            continue
    return out


def _pair_snapshot(b, st):'''),
    # ① the coin ledger
    ('''    tot = {"dca": cl.setdefault("total_dca", {}), "ri": cl.setdefault("total_ri", {}), "rec": cl.setdefault("total_rec", {})}''',
     '''    tot = {"dca": cl.setdefault("total_dca", {}), "ri": cl.setdefault("total_ri", {}), "rec": cl.setdefault("total_rec", {}),
           "pair": cl.setdefault("total_pair", {})}                  # 🔀 v3.36.79: شبكة عملتين (ربحها بالرئيسية)'''),
    ('''        key = os.path.relpath(b["dir"], ROOT)
        base = str(b["symbol"]).split("-")[0].upper()
        evs = []
        if c0.get("bot_type") == "dca":''', '''        key = os.path.relpath(b["dir"], ROOT)
        base = (_pair_parts(b)[1] if c0.get("bot_type") == "grid_pair" else str(b["symbol"]).split("-")[0].upper())   # 🔀 الرئيسية
        evs = []
        if c0.get("bot_type") == "grid_pair":
            evs += _pair_coin_events(st)
        if c0.get("bot_type") == "dca":'''),
    ('''{'DCA بيعي' if src == 'dca' else ('البوت الدوري' if src == 'rec' else 'تحرير إعادة الاستثمار')} · يوم {day}''',
     '''{'DCA بيعي' if src == 'dca' else ('البوت الدوري' if src == 'rec' else ('شبكة عملتين' if src == 'pair' else 'تحرير إعادة الاستثمار'))} · يوم {day}'''),
    # ② the period view · the all-time view · the report · the reset
    ('''            o = out.setdefault(base, {"dca": 0.0, "ri": 0.0, "rec": 0.0, "t": 0.0})
            for k in ("dca", "ri", "rec"):''', '''            o = out.setdefault(base, {"dca": 0.0, "ri": 0.0, "rec": 0.0, "pair": 0.0, "t": 0.0})
            for k in ("dca", "ri", "rec", "pair"):'''),
    ('''    for src in ("total_dca", "total_ri", "total_rec"):''', '''    for src in ("total_dca", "total_ri", "total_rec", "total_pair"):'''),
    ('''                + ([f"الدوري `{v['rec']:+.8g}`"] if abs(v.get("rec", 0)) > 1e-12 else [])''',
     '''                + ([f"الدوري `{v['rec']:+.8g}`"] if abs(v.get("rec", 0)) > 1e-12 else []) \\
                + ([f"شبكة عملتين `{v['pair']:+.8g}`"] if abs(v.get("pair", 0)) > 1e-12 else [])'''),
    ('''            tot = {"dca": {}, "ri": {}, "rec": {}}
            for row in cl["daily"].values():
                for base, e in (row or {}).items():
                    for src in ("dca", "ri", "rec"):''', '''            tot = {"dca": {}, "ri": {}, "rec": {}, "pair": {}}
            for row in cl["daily"].values():
                for base, e in (row or {}).items():
                    for src in ("dca", "ri", "rec", "pair"):'''),
    ('''            cl["total_dca"], cl["total_ri"], cl["total_rec"], cl["bots"] = tot["dca"], tot["ri"], tot["rec"], {}''',
     '''            cl["total_dca"], cl["total_ri"], cl["total_rec"], cl["total_pair"], cl["bots"] = tot["dca"], tot["ri"], tot["rec"], tot["pair"], {}'''),
    # ③ the guard's reconcile (today: the ledger = the bots' sales)
    ('''            base = str(b["symbol"]).split("-")[0].upper()
            evs = []
            if bt == "dca":
                evs = [("dca", e["q"], e["ts"]) for e in (_safe(bot_day_events, b, today, default=[]) or [])]''',
     '''            base = (_pair_parts(b)[1] if bt == "grid_pair" else str(b["symbol"]).split("-")[0].upper())
            evs = []
            if bt == "grid_pair":                     # 🔀 v3.36.79
                for _eid, q, ts, _s in _pair_coin_events(_safe(load_json, paths_of(b)[0], default={}) or {}):
                    if datetime.fromtimestamp(float(ts or 0)).strftime("%Y-%m-%d") == today:
                        evs.append(("pair", float(q or 0), float(ts or 0)))
            if bt == "dca":
                evs = [("dca", e["q"], e["ts"]) for e in (_safe(bot_day_events, b, today, default=[]) or [])]'''),
    ('''for s in ("dca", "rec") if abs''', '''for s in ("dca", "rec", "pair") if abs'''),
    ('''            lab = f"{bs} · {'DCA بيعي' if src == 'dca' else 'الدوري'}"''',
     '''            lab = f"{bs} · {'DCA بيعي' if src == 'dca' else ('شبكة عملتين' if src == 'pair' else 'الدوري')}"'''),
    # ④ the diagnostics: the coin ledger's total = the sum of its days — for the fourth source too
    ('''    cl = load_json(COIN_LEDGER) or {}
    for src in ("dca", "ri", "rec"):''', '''    cl = load_json(COIN_LEDGER) or {}
    for src in ("dca", "ri", "rec", "pair"):'''),
    ('''        add(f"دفتر العملات ({'DCA بيعي' if src == 'dca' else ('الدوري' if src == 'rec' else 'إعادة استثمار')}): الإجمالي = مجموع الأيام"''',
     '''        add(f"دفتر العملات ({'DCA بيعي' if src == 'dca' else ('الدوري' if src == 'rec' else ('شبكة عملتين' if src == 'pair' else 'إعادة استثمار'))}): الإجمالي = مجموع الأيام"'''),
    # ⑤ the coin trade book: the main coin · the engine's sales
    ('''        elif bt == "rec_sell":
            out.append((str(c["id"]), c.get("rel") if c.get("rel") is not None else c.get("profit"), c.get("ri") or 0.0, c.get("ts")))
    return out''', '''        elif bt == "rec_sell":
            out.append((str(c["id"]), c.get("rel") if c.get("rel") is not None else c.get("profit"), c.get("ri") or 0.0, c.get("ts")))
    if bt == "grid_pair":                                       # 🔀 v3.36.79: كل بيعة تداول بالرئيسية
        out += [(eid, q, 0.0, ts) for eid, q, ts, _s in _pair_coin_events(st)]
    return out'''),
    ('''        base = str(b["symbol"]).split("-")[0].upper()
        if first and bt in _REC_T:''', '''        base = (_pair_parts(b)[1] if bt == "grid_pair" else str(b["symbol"]).split("-")[0].upper())   # 🔀 الرئيسية
        if first and bt in _REC_T:'''),
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
    print(f"✅ {len(R)} replacements · 🔀 its profit in the coin books (the main coin) · the fourth source everywhere · {p}")
