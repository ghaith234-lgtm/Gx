# 🪜 patch 03 (engine · F9) — fill lines left pending in memory (their save failed) were written to the log by the next loop
#   BEFORE the state holding the fill was on disk: a power cut between the two ⇒ on restart the fill was processed again and
#   its line was in the log twice (the dashboard books profit from the log ⇒ twice the profit).
#   Now: the loop saves the state (with the pending lines) first; only a successful save lets the lines be written.
#   python3 devtests/step/patches/p03_f9_save_first.py ENGINE.py      (in place · the old text must be found once)
import os, sys

R = [
    ('    if state.get("fx_log"):\n'
     '        _fx_log_flush(state)\n'
     '        save_json(STATE_FILE, state)\n',
     '    if state.get("fx_log") and save_json(STATE_FILE, state) is True:   # 🧾 التنفيذ على القرص أول ⇒ بعدين سطره (F9)\n'
     '        _fx_log_flush(state)\n'
     '        save_json(STATE_FILE, state)\n'),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · compiles · {p}")
