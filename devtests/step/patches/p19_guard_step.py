# 🪜🛡️ patch 19 (dashboard · the guard reads a 🪜 bot by its own rules — two false alerts after «باع وفتح شراء»)
#   Found by running the dashboard's real guard (gather · apply · qty audit · trade scan, every 10 minutes) on the 🪜 engine and
#   the mock OKX (devtests/step/t_win.py):
#   ① «💵 رصيد USDT الحر أقل من أمر شراء واحد» measured the free dollars against usd_value — for 🪜 that is the amount of a whole
#      LEVEL, split over its parts: one 🪜 order is usd_value ÷ step_parts (25$ in 3 parts ⇒ 8.33$). A sale that opens a buy
#      took the free dollars under 25$ ⇒ «any new buy will be refused» while the next 🪜 buy (8.33$) fits.
#   ② «☠️ … السعر تحرك X درجة من آخر تنفيذ وما صار ولا تنفيذ» — a 🪜 that sold its top part and opened its buy has NOTHING above
#      the price (its ladder is fixed): the price going on up is the bot waiting, not a dead bot. Now for 🪜: only when the price
#      passed one of its own orders (published or in memory) on that side since the last fill (≥ 0.1% past it) — a dead 🪜 is still
#      caught (the price crossed its sells/buys and nothing filled).
#   (the other grids keep their rules — REVIEW «📌 تخص المحركات الثانية»)
#   python3 devtests/step/patches/p19_guard_step.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''                usd = float(cfg.get("usd_value") or 0)
                if usd > 0 and not st.get("destruct_done"):
                    q["min_next"] = usd if not q["min_next"] else min(q["min_next"], usd)
''',
     '''                usd = float(cfg.get("usd_value") or 0)
                if bt == "grid_step":                    # 🪜 usd_value = مبلغ المستوى كله ⇒ أمره الواحد = ÷ الأجزاء
                    try:
                        usd /= max(1, int(float(cfg.get("step_parts") or 1)))
                    except Exception:
                        pass
                if usd > 0 and not st.get("destruct_done"):
                    q["min_next"] = usd if not q["min_next"] else min(q["min_next"], usd)
'''),
    ('''            idle = now - float(bb["fill_ts"])
            if steps >= GUARD_STALL_STEPS and idle >= GUARD_STALL_MIN and not zone:
''',
     '''            idle = now - float(bb["fill_ts"])
            if not zone and bb.get("type") == "grid_step":    # 🪜 سلّمه ثابت: ولا أمر له بين آخر تنفيذ والسعر ⇒ ينتظر صح (مو ميت)
                _rg = (bb.get("rungs") or {}).get("sell" if cp > fp else "buy") or []
                zone = not any((fp < r < cp / 1.001) if cp > fp else (cp * 1.001 < r < fp) for r in _rg)
            if steps >= GUARD_STALL_STEPS and idle >= GUARD_STALL_MIN and not zone:
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
