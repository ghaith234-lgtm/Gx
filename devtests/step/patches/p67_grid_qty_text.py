# ➕🎚️ patch 67 (engines · ➕ plus and 🎚️ range) — found while examining the plus bot (the owner, 14-11: «افحص البوت البلس كليا»):
#   the confirmed aggregated-order line printed the float tail of a sum: «⚡ [تجميع شراء مؤكد] نُفذ (1.42) من (1.4200000000000002)».
#   The line now prints both quantities with _sz_str (the exact multiple of the coin's lot step — the text the order itself is sent with). Text only — the order and
#   the books use the same numbers as before.
#   python3 devtests/step/patches/p67_grid_qty_text.py devtests/step/eng/grid_plus.py devtests/step/eng/grid_range.py
import sys

R = [
    ('''        _bl = f"⚡ [تجميع {side_ar} مؤكد] نُفذ ({filled_qty}) من ({total_qty_rounded}) بمتوسط سعر ({avg_px}). جاري نشر الأوامر المقابلة في أماكنها الأصلية."''',
     '''        _bl = (f"⚡ [تجميع {side_ar} مؤكد] نُفذ ({_sz_str(filled_qty)}) من ({_sz_str(total_qty_rounded or 0)}) "   # 🔢 v3.36.44: بلا ذيل الجمع (1.4200000000000002)
               f"بمتوسط سعر ({avg_px}). جاري نشر الأوامر المقابلة في أماكنها الأصلية.")'''),
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
