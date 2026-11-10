# 🪜 patch 35 (dashboard only — the engine is not touched) — the owner (10-11): «المشكلة البوت حده 200 اذا انزيده نگدر اريد مثلا 500».
#   The graded grid's «levels above the price from your coins» was capped at 200 by the dashboard (the engine itself has no cap) · and
#   the plan refused more than 1,500 slots in the bot's memory (500 levels × 3 sells alone = 1,500).
#   ① up to 500 levels above (STEP_MAX_UP) · ② up to 3,000 slots (STEP_MAX_SLOTS) — t_deep «scale» runs the engine with ≈4,900 slots
#      (its loop ≤ 250 ms every 3 s · the card ≤ 1.5 s) · ③ the form says the range.
#   python3 devtests/step/patches/p35_step_up500.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''STEP_MAX_SLOTS = 1500        # حد الخانات (أوامر بالذاكرة) — أكثر ⇒ الجدول يرفض (مسافة شراء أكبر أو أرضية أعلى) · ملف الحالة يبقى صغير''',
     '''STEP_MAX_SLOTS = 3000        # حد الخانات (أوامر بالذاكرة) — أكثر ⇒ الجدول يرفض (مسافة شراء أكبر أو أرضية أعلى) · 🪜 v3.36.30: 1500 ⇒ 3000 (t_deep «scale»: ≈4,900 خانة ⇐ دورة ≤ 250 ms)
STEP_MAX_UP = 500            # ⬆️ v3.36.30 (المالك 10-11 «اريد مثلا 500»): مستويات فوق السعر من عملاتك — كانت 200 (المحرك نفسه بلا حد)'''),
    ('''    if up < 0 or up > 200:
        return None, "مستويات عملاتك فوق السعر من 0 إلى 200"''',
     '''    if up < 0 or up > STEP_MAX_UP:
        return None, f"مستويات عملاتك فوق السعر من 0 إلى {STEP_MAX_UP}"'''),
    ('''title="عدد المستويات فوق سعر البداية التي تبيع من عملاتك الحرة كأنها اشتُريت بسعر مستواها (0 = لا شيء)">⬆️ مستويات فوق السعر من عملاتك</label>''',
     '''title="عدد المستويات فوق سعر البداية التي تبيع من عملاتك الحرة كأنها اشتُريت بسعر مستواها (0 = لا شيء · حتى 500)">⬆️ مستويات فوق السعر من عملاتك <small>(0–500)</small></label>'''),
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
