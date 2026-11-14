# 🔌 patch 81 (dashboard v3.36.49 · the engines' lines about connection cuts are not shown) — the owner (14-11), after being asked about
#   the engines' own log lines («🔌 انقطع الإنترنت — إيقاف الأوامر الجديدة مؤقتاً» · «🌐 عاد الإنترنت بعد Nث — إعادة مزامنة» ·
#   «🧾 [انقطاع] أمر …» · «… انرسل قبل الانقطاع» · «[قيد الأمر المجمّع] انقطاع …»): «زيل من السجل بس ما اتغير في المحرك».
#   · the engines are not touched (♾️ ➕ 🎚️ write those lines into the bot's own trade_history file as before — the file stays whole,
#     and nothing that counts profit or checks the books reads it differently)
#   · one filter `_cut_line` on what the customer is SHOWN: 📜 the bot's log window (/api/history) · 🔔 the notification centre
#     (feed_all) · the card's last line (bot_snapshot «last_event») · the detailed journals (journal_ingest_bots no longer copies such a
#     line in · journal_query no longer shows one copied in before)
#   python3 devtests/step/patches/p81_hide_cut_lines.py Holy_Dashboard.pyw
import os, sys

HELPER = '''# 🔌 v3.36.49 (المالك 14-11: «زيل من السجل بس ما اتغير في المحرك»): أسطر المحركات عن انقطاع الاتصال وما بعده («🔌 انقطع الإنترنت» ·
#    «🌐 عاد الإنترنت» · «[انقطاع]» · «قبل الانقطاع») تبقى بملف البوت كما هي — المحرك ما يتغيّر والحسابات تقراها كما كانت — بس ما تُعرض
#    للزبون: 📜 سجل البوت · 🔔 مركز الإشعارات · سطر البطاقة الأخير · السجلات المفصّلة
_CUT_RE = re.compile(r"انقطع|انقطاع|الإنترنت|إنترنت|الكهرباء|كهرباء|انطفاء")


def _cut_line(e):
    """True ⇒ سطر عن انقطاع الاتصال/الكهرباء — لا يُعرض (يبقى بالملف)."""
    try:
        return bool(_CUT_RE.search(str(e.get("msg") or e.get("m") or "") if isinstance(e, dict) else str(e or "")))
    except Exception:
        return False


def history_of(d, limit=200):'''

R = [
    # the helper, right before history_of — and history_of shows none of them
    ('''def history_of(d, limit=200):''', HELPER),
    ('''    _, hp, _ = paths_of(bots[full])
    return (load_json(hp) or [])[:limit]''',
     '''    _, hp, _ = paths_of(bots[full])
    return [e for e in (load_json(hp) or []) if not _cut_line(e)][:limit]   # 🔌 v3.36.49: أسطر الانقطاع لا تُعرض (تبقى بالملف)'''),
    # 🔔 the notification centre
    ('''                if any(x in str(e.get("msg")) for x in _FEED_SKIP):
                    continue''',
     '''                if any(x in str(e.get("msg")) for x in _FEED_SKIP) or _cut_line(e):   # 🔌 v3.36.49: ولا أسطر الانقطاع
                    continue'''),
    # the card's last line
    ('''    for e in hist[:400]:
        if not isinstance(e, dict):
            continue
        last_event = e.get("msg", "")[:140]
        break''',
     '''    for e in hist[:400]:
        if not isinstance(e, dict) or _cut_line(e):      # 🔌 v3.36.49: سطر الانقطاع لا يصير «آخر حدث» بالبطاقة
            continue
        last_event = e.get("msg", "")[:140]
        break'''),
    # the detailed journals: not copied in · not shown if copied before
    ('''                for ts, msg in reversed(new):
                    try:
                        tt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp()''',
     '''                for ts, msg in reversed(new):
                    if _cut_line(msg):                   # 🔌 v3.36.49: أسطر الانقطاع لا تنسخ للسجلات (تبقى بملف البوت)
                        continue
                    try:
                        tt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp()'''),
    ('''            if after is not None and e.get("t", 0) < after:
                continue
            if lv == "warn" and e.get("lv") not in ("warn", "err"):''',
     '''            if after is not None and e.get("t", 0) < after:
                continue
            if e.get("bot") and _cut_line(e):              # 🔌 v3.36.49: سطر انقطاع نُسخ قبل هذه النسخة — لا يُعرض
                continue
            if lv == "warn" and e.get("lv") not in ("warn", "err"):'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    s = s.replace('APP_VERSION = "3.36.48"', 'APP_VERSION = "3.36.49"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the cut lines are kept in the file and not shown · compiles · {p}")
