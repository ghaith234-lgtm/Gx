# 🧠 patch 118 (dashboard v3.36.69 · the analyst — quieter, its own name). The real-price check of the final build (RUN_SIGDASH 6) sent 7
#   «🔎 الآن في السوق» notifications in one round (4 coins × «نزول مدعوم بخروج السيولة» and «ازدحام الشراء») under the old title
#   «🎯 إشارات جديدة».
#   · 🔎 notifies only what the owner named: 🧲 accumulation / 🔻 distribution and 🐂 aggressive buying / 🐻 aggressive selling — the trend
#     with liquidity, the crowding and the strength vs BTC stay in the window (🔎 الآن في السوق on the card)
#   · the messages carry the analyst's name: «🧠 المحلل — إشعارات جديدة (n)» · «🌙 إشعارات المحلل أثناء ساعات الهدوء» · «🗓️ ملخص المحلل
#     اليوم» · the daily cap note points to 📊 المؤشرات
#   python3 devtests/step/patches/p118_analyst_quiet.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""SG_NST_AGE = {"4H": 3 * 86400, "1D": 14 * 86400}""",
     """SG_NST_AGE = {"4H": 3 * 86400, "1D": 14 * 86400}
SG_NST_NOTE = ("X-ad", "P-tk")                              # 🔔 منها ما يُشعَر به: التجميع/التصريف · الشراء/البيع العدواني (الباقي بالنافذة)"""),
    ("""                        if fr == "1D" and f"{code}:{sd}" not in A0 and sym in mine and cfg["types"].get("nst", True):""",
     """                        if fr == "1D" and code in SG_NST_NOTE and f"{code}:{sd}" not in A0 and sym in mine and cfg["types"].get("nst", True):"""),
    ("""                note = f"🔕 وصلت حد إشعارات الإشارات اليوم ({cfg['cap']}) — الباقي في اللوحة فقط (🎯)\"""",
     """                note = f"🔕 وصلت حد إشعارات المحلل اليوم ({cfg['cap']}) — الباقي في نافذة 📊 المؤشرات\""""),
    ("""        text = f"🎯 إشارات جديدة ({len(out)})\\n\\n\"""", """        text = f"🧠 المحلل — إشعارات جديدة ({len(out)})\\n\\n\""""),
    ("""        text = f"🌙 إشارات وصلت أثناء ساعات الهدوء ({len(q)})\\n\\n\"""", """        text = f"🌙 إشعارات المحلل أثناء ساعات الهدوء ({len(q)})\\n\\n\""""),
    ("""            (f"\\n\\n… و{len(q) - 15} غيرها في اللوحة (🎯)" if len(q) > 15 else "")""",
     """            (f"\\n\\n… و{len(q) - 15} غيرها في نافذة 📊 المؤشرات" if len(q) > 15 else "")"""),
    ("""            text = f"🗓️ ملخص الإشارات اليوم ({len(q)})" + ("\\n\\n" + "\\n\\n".join(x["t"] + "\\n" + x["b"] for x in q[:20]) if q else "\\nلا توجد إشارات جديدة اليوم بإعداداتك")""",
     """            text = f"🗓️ ملخص المحلل اليوم ({len(q)})" + ("\\n\\n" + "\\n\\n".join(x["t"] + "\\n" + x["b"] for x in q[:20]) if q else "\\nلا جديد اليوم بإعداداتك")"""),
    ("""      <div class="ind-sub">🟢 و🔴: حين تتفق مجموعة مؤشرات مثبتة (غداً أو الشهر القادم) — تحليل لا أسعار · 🔎: حالة جديدة (تجميع · تصريف · شراء أو بيع عدواني · ازدحام) — وصف لا توقع</div>""",
     """      <div class="ind-sub">🟢 و🔴: حين تتفق مجموعة مؤشرات مثبتة (غداً أو الشهر القادم) — تحليل لا أسعار · 🔎: حالة جديدة (تجميع · تصريف · شراء أو بيع عدواني) — وصف لا توقع · مرة في اليوم على الأكثر لكل حالة</div>"""),
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
    print(f"✅ {len(R)} replacements · 🔎 quieter (accumulation/distribution · aggressive buying/selling) · 🧠 the analyst's name on its messages · {p}")
