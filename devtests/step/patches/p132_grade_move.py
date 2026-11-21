# p132 — v3.36.76 ⚖️ the tables count a result only when the price moved more than the fees (Gemini's point, checked: before, +0.001% was a ✅)
#   · SB_MV = 0.2% (round-trip fee) — a smaller move is not counted (neither ✅ nor ❌) · the same rule as the daily tendency (TD_P["mv"])
#   · the help line under the tables says so
#   python3 devtests/step/patches/p132_grade_move.py Holy_Dashboard.pyw
import sys, os

R = [
    ("SB_MINN = 10                                  # أقل عدد نتائج قبل الخروج من «قيد الاختبار» (الترتيب بأقل نسبة نثق بها — ويلسون)\n",
     "SB_MINN = 10                                  # أقل عدد نتائج قبل الخروج من «قيد الاختبار» (الترتيب بأقل نسبة نثق بها — ويلسون)\n"
     "SB_MV = 0.002                                 # ⚖️ v3.36.76: حركة أصغر من 0.2% (عمولة الذهاب والعودة) لا تُحسب — لا ✅ ولا ❌\n"),
    ("    \"\"\"⚖️ كل تنبؤ يُحكم بإغلاق الشمعة التالية من إطاره (من الشموع المحفوظة): السعر تحرك بجهته ⇒ ✅ · عكسها ⇒ ❌ · لم يتحرك ⇒ لا يُحسب\"\"\"\n",
     "    \"\"\"⚖️ كل تنبؤ يُحكم بإغلاق الشمعة التالية من إطاره (من الشموع المحفوظة): السعر تحرك بجهته ⇒ ✅ · عكسها ⇒ ❌ · أقل من SB_MV ⇒ لا يُحسب\"\"\"\n"),
    ("        if c1 == px:\n            continue\n        ok = 1 if (c1 - px) * side > 0 else 0\n",
     "        if abs(c1 / px - 1.0) < SB_MV:                    # ⚖️ v3.36.76: أصغر من العمولة ⇒ لا يُحسب\n            continue\n        ok = 1 if (c1 - px) * side > 0 else 0\n"),
    ("<b>✅</b> تحرك السعر بجهته · <b>❌</b> عكسها — والنسبة = ✅ من كل النتائج",
     "<b>✅</b> تحرك السعر بجهته · <b>❌</b> عكسها · حركة أصغر من 0.2% (العمولة) لا تُحسب — والنسبة = ✅ من كل النتائج"),
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
    print(f"✅ {len(R)} replacements · ⚖️ a result counts only above the fees · compiles · {p}")
