# p150 — v3.36.79 🔀 «شبكة عملتين» · ⑤ «ولا بوت لازم ياخذ هذا الدولار» (the owner 27-11: «٣ شي جدا مهم»)
#   The dollar of a swap in flight (between its two legs) and the bot's dollar dust are the bot's: the engine writes them as `usd_booked`.
#   · the wallet snapshot (`_gd_gather`) adds them per wallet to the BRIDGE currency's record (USDT — not XRP, the second part of the
#     pair's symbol) as `pair_hold` · the record keeps it (`pair_hold` beside `dca_hold`)
#   · «the free dollar not reserved» subtracts it everywhere it is computed: the wallet's low-dollar watch (`_cw_low` ⇒ free_u, which
#     the temporary pause reads) and a bot's own budget (`_tp_budget` — 🔓 opening the temporary pause)
#   ⇒ no grid bot is told that dollar is free · and `_gd_free_claims` (p146) already keeps every deploy from counting it
#   python3 devtests/step/patches/p150_pair_usdhold.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            if bt == "dca" and st.get("phase") in ("selling", "buying"):       # ⏳ v3.36.58: دولار DCA البيعي (وDCA+) محجوز لإعادة شراء عملته''',
     '''            if bt == "grid_pair":                   # 🔀 v3.36.79: دولار تبديله بالطريق + كسوره = له (لا يُحسب حراً لأي بوت) — بعملة الوسيط
                try:
                    _qb = str(cfg.get("bridge") or "USDT")
                    _qq = snap["quotes"].setdefault(_qb, {"bots_frozen": 0.0, "min_next": 0.0})
                    _qq["pair_hold"] = float(_qq.get("pair_hold") or 0) + max(0.0, float(st.get("usd_booked") or 0))
                except Exception:
                    pass
            if bt == "dca" and st.get("phase") in ("selling", "buying"):       # ⏳ v3.36.58: دولار DCA البيعي (وDCA+) محجوز لإعادة شراء عملته'''),
    ('''                       min_next=float(qi.get("min_next") or 0), dca_hold=round(float(qi.get("dca_hold") or 0), 6), ts=now)''',
     '''                       min_next=float(qi.get("min_next") or 0), dca_hold=round(float(qi.get("dca_hold") or 0), 6),
                       pair_hold=round(float(qi.get("pair_hold") or 0), 6), ts=now)            # 🔀 v3.36.79'''),
    ('''    dh = float(rec.get("dca_hold") or 0)
    eff = av - held
    un = eff - dh''', '''    dh = float(rec.get("dca_hold") or 0)
    eff = av - held - float(rec.get("pair_hold") or 0)          # 🔀 v3.36.79: دولار «شبكة عملتين» بين رجلي التبديل ليس حراً
    un = eff - dh'''),
    ('''    return max(0.0, av - dh - held)''', '''    return max(0.0, av - dh - held - float(rec.get("pair_hold") or 0))      # 🔀 v3.36.79: ولا دولار «شبكة عملتين» بالطريق'''),
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
    print(f"✅ {len(R)} replacements · 🔀 the dollar of a swap in flight is the bot's — never «free» for any other bot · {p}")
