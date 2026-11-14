# ➕🎚️ patch 69 (engines · ➕ plus and 🎚️ range) — the same kind as p67, found by the path sweep once the sandbox's own numbers were
#   clean (p68): «⚡ [لحاق مستوى] 85.954 · كمية 0.12000000000000001 · …» — the level's share of an aggregated fill is a float division.
#   The line prints it rounded to 10 decimals (the share itself is not on the lot step, so not _sz_str). Text only.
#   python3 devtests/step/patches/p69_grid_catch_qty_text.py devtests/step/eng/grid_plus.py devtests/step/eng/grid_range.py
import sys

R = [
    ('''                    log_trade_history(symbol, f"⚡ [لحاق مستوى] {level_p} · كمية {part} · كلفة {round(_cost, 8)} · بسعر {avg_px}")''',
     '''                    log_trade_history(symbol, f"⚡ [لحاق مستوى] {level_p} · كمية {round(float(part), 10)} · كلفة {round(_cost, 8)} · بسعر {avg_px}")'''),
    ('''                log_trade_history(symbol, f"⚡ [لحاق مستوى] {level_p} · كمية {q} · كلفة {round(_cost, 8)} · بسعر {avg_px}")''',
     '''                log_trade_history(symbol, f"⚡ [لحاق مستوى] {level_p} · كمية {round(float(q), 10)} · كلفة {round(_cost, 8)} · بسعر {avg_px}")'''),
]

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = open(p, encoding="utf-8").read()
        for i, (a, b) in enumerate(R):
            if s.count(a) != 1:
                print(f"❌ {p}: replacement {i} found {s.count(a)} times — nothing written"); sys.exit(1)
            s = s.replace(a, b)
        compile(s, p, "exec")
        open(p, "w", encoding="utf-8").write(s)
        print(f"✅ {len(R)} replacement(s) · compiles · {p}")
