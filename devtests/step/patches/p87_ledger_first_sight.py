# 📒 patch 87 (dashboard v3.36.52 · the full audit, batch 3 — the numbers shown) — bot folders written by the real engines over three
#   days, then read by the dashboard: card = book after fees = what the wallet gained · Σ cards = the total = Σ days · two days with the
#   dashboard off ⇒ each day gets its own profit — all right. One thing wrong: the FIRST time the ledger sees a grid bot that already
#   has profit (a new install over running bots · a bot folder brought in), all its earlier profit was written on TODAY («ربح اليوم»
#   jumped, the day chart showed one tall day, and 🔗 warned «سطور البيع اليوم … الدفتر …»).
#   ⇒ on first sight the amount is spread over the days of the bot's own sell lines (the same rule the ledger already uses for a
#     period the dashboard was off — `_hist_window` · the total is exactly the same; no lines ⇒ today as before)
#   python3 devtests/step/patches/p87_ledger_first_sight.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            else:
                ent = {"last_seen_total": 0.0, "daily": {}, "monthly": {}, "trades_daily": {}, "hourly": {}}
        ent.setdefault("symbol", b["symbol"])''',
     '''            else:
                ent = {"last_seen_total": 0.0, "daily": {}, "monthly": {}, "trades_daily": {}, "hourly": {}}
                ent["_first"] = True                        # 📒 v3.36.52: أول مرة يشوفه الدفتر
        ent.setdefault("symbol", b["symbol"])'''),
    ('''            parts = _safe(_hist_window, b, gap_t, now_t, default=None) if gap_cross else None
            _book_split(ent.setdefault("daily", {}), diff, parts, today)''',
     '''            # 📒 v3.36.52: أول مرة يشوف الدفتر بوتاً له ربح سابق ⇒ على أيام سطور بيعه (كان كله على «اليوم»)
            parts = (_safe(_hist_window, b, 0.0, now_t, default=None) if ent.get("_first") else
                     _safe(_hist_window, b, gap_t, now_t, default=None) if gap_cross else None)
            _book_split(ent.setdefault("daily", {}), diff, parts, today)'''),
    ('''    if changed:
        try: save_json_atomic(LEDGER, led)
        except Exception: pass
    _LT_LAST["t"] = now_t
    return led''',
     '''    for _e in led.values():                                 # 📒 v3.36.52: علامة «أول مرة» لنبضة واحدة فقط
        if isinstance(_e, dict) and _e.pop("_first", None):
            changed = True
    if changed:
        try: save_json_atomic(LEDGER, led)
        except Exception: pass
    _LT_LAST["t"] = now_t
    return led'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:80]!r}"); sys.exit(1)
        s = s.replace(a, b)
    s = s.replace('APP_VERSION = "3.36.51"', 'APP_VERSION = "3.36.52"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
