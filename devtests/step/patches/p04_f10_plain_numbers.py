# 🪜 patch 04 (engine · F10) — the numbers in the log lines were written with Python's round(): a small value comes out in
#   scientific notation («الربح: +9e-05$») and the dashboard reads the profit with PROFIT_RE (digits and a dot only) ⇒ 9$
#   instead of 0.00009$ · the profit was also rounded to 6 decimals while the books keep 10 (the log's sum ≠ the books).
#   Now: every number in a log line is a plain decimal (`_n`) · the profit with the books' own 10 decimals (log sum = books).
#   python3 devtests/step/patches/p04_f10_plain_numbers.py ENGINE.py      (in place · every old text found once)
import os, sys

R = [
    ("def _b36(n):\n",
     "def _n(x, nd=10):\n"
     "    \"\"\"🔢 رقم بالسجل عشري عادي بلا صيغة علمية: «9e-05» كانت اللوحة تقراها 9 (PROFIT_RE أرقام ونقطة بس) — هسه «0.00009»\"\"\"\n"
     "    try:\n"
     "        s = format(Decimal(repr(round(float(x), nd))), \"f\")\n"
     "    except Exception:\n"
     "        return str(x)\n"
     "    if \".\" in s:\n"
     "        s = s.rstrip(\"0\").rstrip(\".\")\n"
     "    return \"0\" if s in (\"\", \"-0\") else s\n"
     "\n\n"
     "def _b36(n):\n"),
    ("    lines = [f\"🪜 [بدء الشبكي المتدرج] سعر البداية {stp['P0']} · {nb} شراء ثابت تحته حتى {lo} · {ns} بيعة من المحفظة فوقه · \"\n",
     "    lines = [f\"🪜 [بدء الشبكي المتدرج] سعر البداية {_n(stp['P0'])} · {nb} شراء ثابت تحته حتى {_n(lo)} · {ns} بيعة من المحفظة فوقه · \"\n"),
    ("f\"⚠️ [رفض أمر {nm}] الكمية {sz} بسعر {px} (المستوى",
     "f\"⚠️ [رفض أمر {nm}] الكمية {_n(sz)} بسعر {_n(px)} (المستوى"),
    ("f\"🟢 [شراء فوري] السعر: {round(spent / bought, 10)} | الكمية: {round(bought, 10)} -> تم تجهيز بيع بسعر:",
     "f\"🟢 [شراء فوري] السعر: {_n(spent / bought)} | الكمية: {_n(bought)} -> تم تجهيز بيع بسعر:"),
    ("f\"🔴 [بيع فوري] السعر: {round(gross / sold, 10)} | الكمية: {round(sold, 10)} | الربح: {sgn}{abs(round(profit, 6))}$\"",
     "f\"🔴 [بيع فوري] السعر: {_n(gross / sold)} | الكمية: {_n(sold)} | الربح: {sgn}{_n(abs(profit))}$\""),
    ("الجزء {s['k']}/{N} (كلفة {cb})\")",
     "الجزء {s['k']}/{N} (كلفة {_n(cb)})\")"),
    ("{round(acc, 10)} بسعر {avg} — الباقي {round(rem, 10)} ينرسل من جديد",
     "{_n(acc)} بسعر {_n(avg)} — الباقي {_n(rem)} ينرسل من جديد"),
    ("f\"⏸️→📦 إيقاف الشراء — الأرضية {cp} (", "f\"⏸️→📦 إيقاف الشراء — الأرضية {_n(cp)} ("),
    ("f\"⏸️→📦 إيقاف البيع — السقف {cp} (", "f\"⏸️→📦 إيقاف البيع — السقف {_n(cp)} ("),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:80]}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
