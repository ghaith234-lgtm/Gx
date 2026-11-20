# 🔒📏 patch 108 (dashboard v3.36.64 · a locked card opens from its compact row). The owner (20-11): «مشكلة في قفل الكرت ما يفتح اذا مقفول ،
#   خليه يفتح الكرت بس ما يفتح القفل». The card lock (v3.36.7) stops every tap inside a locked card (a capture listener on the page) —
#   the compact row (v3.36.63) is inside the card, so a locked card stayed a row.
#   · the row opens and closes the card while it is locked · the lock is not opened (no minute starts · 🔒 stays) · every button inside
#     the opened card still asks for 🔒 first (as before)
#   · the row is not dimmed like the locked card's buttons · it shows a small 🔒 while the card is locked
#   python3 devtests/step/patches/p108_lock_compact.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""  if(e.target.closest('.lkbtn'))return;
  if(!cardLocked(el)){CLK.open.set(cardKey(el),Date.now()+CLK.ms);return}                 // مفتوحة ⇒ كل استعمال يجدّد الدقيقة""",
     """  if(e.target.closest('.lkbtn,.cmini'))return;                     // 📏 v3.36.64: سطر المختصر يفتح البطاقة ويسدّها — بلا فتح القفل ولا تجديد دقيقته
  if(!cardLocked(el)){CLK.open.set(cardKey(el),Date.now()+CLK.ms);return}                 // مفتوحة ⇒ كل استعمال يجدّد الدقيقة"""),
    (""".card.lk button:not(.lkbtn){opacity:.5;filter:saturate(.55)}""",
     """.card.lk button:not(.lkbtn):not(.cmini){opacity:.5;filter:saturate(.55)}
.card.lk>.cmini .cm-sym::after{content:" 🔒";font-size:11px;opacity:.85}              /* 📏 v3.36.64: السطر يفتح البطاقة المقفلة ويبيّن قفلها */"""),
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
    print(f"✅ {len(R)} replacements · 🔒📏 a locked card opens from its compact row (the lock stays) · compiles · {p}")
