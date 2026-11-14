# 💵 patch 71 (dashboard v3.36.44 · follow-up of p70) — a bot the system paused for dollars waited for the next guard round to resume:
#   ⏸️ «الرقابة موقوفة» ⇒ there is no next round (guard_scan returns at once) ⇒ the bot stayed paused until the guard came back.
#   Now pausing the guard or switching «⏸💵 إيقاف الشراء تلقائياً» off resumes every bot it paused at once (the owner's own floors back).
#   python3 devtests/step/patches/p71_cash_release.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''def _cw_card(bdir):''',
     '''def _cw_release_all(why):
    """▶️ كل بوت أوقفه النظام للدولار يُستأنف الآن (أرضية المالك ترجع) — حين تُوقف الرقابة أو يُطفأ المفتاح (لا جولة قادمة تستأنفه)"""
    n = 0
    with _CW_LOCK:
        d = _cw_load()
        for k, r in list(d["bots"].items()):
            if _cw_restore(k, r, d, why):
                n += 1
        d["ok"], d["seen"] = {}, {}
        save_json_atomic(CASHW_FILE, d)
    return n


def _cw_card(bdir):'''),
    ('''        if paused is not None:
            g["paused"] = bool(paused)
            msg.append("⏸️ الرقابة موقوفة" if g["paused"] else "▶️ الرقابة تعمل")
        _gd_save(g)''',
     '''        if paused is not None:
            g["paused"] = bool(paused)
            msg.append("⏸️ الرقابة موقوفة" if g["paused"] else "▶️ الرقابة تعمل")
        _gd_save(g)
        if (cash_pause is not None and not g.get("cash_pause", True)) or (paused is not None and g.get("paused")):
            _n = _safe(_cw_release_all, "أُوقفت الرقابة" if g.get("paused") else "أُطفئ الإيقاف التلقائي", default=0) or 0
            if _n:                                       # 💵 v3.36.44: لا جولة قادمة تستأنفها ⇒ الآن
                msg.append(f"▶️ استؤنف شراء {_n} بوت أوقفه النظام لنفاد الدولار")'''),
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
    print(f"✅ {len(R)} replacements · compiles · {p}")
