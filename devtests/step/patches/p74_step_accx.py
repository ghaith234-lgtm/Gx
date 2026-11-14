# 🪜 patch 74 (dashboard v3.36.45) — the owner (14-11): «بوت المتدرج افحص ايقاف الشراء وايقاف البيع شوفه نفس نمط الشبكي يعني من المكان
#   المحدد وكذلك سوي فحص عليه اذا بدون استثمار او استثمار». Checked in the trial sandbox (devtests/t_step_pause.py): the 🪜 engine
#   already keeps the pattern — no buy under the floor / no sell over the ceiling while paused (the floor = the market at the press,
#   or the typed price) · on ▶️ every level the price crossed goes out at the market (cheaper than its level / dearer for sells) and
#   its counter-order goes back to its own place. But the dashboard reads the levels of a pause from accum_buys/accum_sells — the
#   ♾️ ➕ 🎚️ engines keep them there, the 🪜 engine keeps everything in its slots ⇒ on a 🪜 card the button always said «▶️ استئناف
#   الشراء (0)», no «📦 شراء N ≈ $X» chip, no «📦 عبر N درجة» notification, no «تفريغ المخزن», the resume window counted 0.
#   Now _accx_src() gives the same list for 🪜 from its slots: the levels in the bot's memory behind the floor (buy) / ceiling (sell)
#   — every one the price crossed + the window's worth (step_window) next to the price that the pause pulled off the exchange.
#   Only the dashboard's counting — the engine is not touched.
#   python3 devtests/step/patches/p74_step_accx.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''def _accx_levels(b, st, side, cp):''',
     '''def _accx_src(b, st, side, cp=None):
    """📦 مخزن الإيقاف {مفتاح: {target_price, locked_qty}} — ♾️ ➕ 🎚️ من accum_* · 🪜 v3.36.45 من خاناته: كل خانة بذاكرة البوت خلف
    الأرضية (شراء) / السقف (بيع) اللي قطعها السعر (تنشرى/تنباع بسعر السوق عند الاستئناف) + بقدر نافذة البوت جنب السعر (اللي سحبها الإيقاف)"""
    ak = "accum_buys" if side == "buy" else "accum_sells"
    if str((b.get("cfg") or {}).get("bot_type") or "") != "grid_step":
        return st.get(ak) or {}
    lim = float(st.get("buy_floor" if side == "buy" else "sell_ceiling") or 0)
    if lim <= 0:
        return {}
    if cp is None:
        cp = float(PX.get(b.get("symbol")) or st.get("current_price") or 0)
    W = max(1, int(float((b.get("cfg") or {}).get("step_window") or 8)))
    rows = []
    for k, s in (st.get("slots") or {}).items():
        if not isinstance(s, dict) or s.get("side") != side:
            continue
        o = s.get("o") or {}
        if o.get("id") and o.get("st") == "live":
            continue                                    # حي بالمنصة (مثلاً منفّذ جزئياً) — مو بالمخزن
        try:
            if side == "buy":
                p, q = float(s.get("bp") or 0), float(s.get("q") or 0) + float(s.get("g") or 0) - float(s.get("acc") or 0)
                if not (0 < p < lim):
                    continue
            else:
                p, q = float(s.get("sp") or 0), float(s.get("sq") or 0) - float(s.get("acc") or 0)
                if not p > lim:
                    continue
        except Exception:
            continue
        if q > 1e-12:
            rows.append((k, p, round(q, 10)))
    rows.sort(key=lambda t: -t[1] if side == "buy" else t[1])
    cut = [t for t in rows if (t[1] >= cp if side == "buy" else t[1] <= cp)] if cp and cp > 0 else []
    rest = [t for t in rows if t not in cut][:W]
    return {k: {"target_price": p, "locked_qty": q} for k, p, q in cut + rest}


def _accx_levels(b, st, side, cp):'''),
    ('''    for v in (st.get("accum_buys" if side == "buy" else "accum_sells") or {}).values():
        try:
            p, q = float((v or {}).get("target_price") or 0), float((v or {}).get("locked_qty") or 0)''',
     '''    for v in _accx_src(b, st, side, cp).values():           # 🪜 v3.36.45: من خاناته
        try:
            p, q = float((v or {}).get("target_price") or 0), float((v or {}).get("locked_qty") or 0)'''),
    ('''           "kb": len(st.get("accum_buys") or {}), "ks": len(st.get("accum_sells") or {})}''',
     '''           "kb": len(_accx_src(b, st, "buy", cp)), "ks": len(_accx_src(b, st, "sell", cp))}'''),
    ('''        have = {f"{float((v or {}).get('target_price') or 0):.10g}" for v in (st.get(ak) or {}).values()}''',
     '''        have = {f"{float((v or {}).get('target_price') or 0):.10g}" for v in _accx_src(b, st, side, cp).values()}'''),
    ('''                ab, asl = len(st.get("accum_buys") or {}), len(st.get("accum_sells") or {})''',
     '''                ab, asl = len(_safe(_accx_src, b, st, "buy", default={}) or {}), len(_safe(_accx_src, b, st, "sell", default={}) or {})   # 🪜 v3.36.45'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
