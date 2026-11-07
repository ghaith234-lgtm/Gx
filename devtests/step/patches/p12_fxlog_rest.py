# 🪜🧾 patch 12 (engine · the fill's lines after a power cut: only the ones not written)
#   A fill writes its lines after its one save (F9); a cut between them ⇒ at the restart _fx_log_flush rewrote ALL the lines when
#   not all were in the log ⇒ the ones already written came twice (a reinvested sale at 0–100% writes two: the sale line, then
#   «💠 [ربح داخلي]» — a cut between them ⇒ the sale line twice in the log and in the notifications). Now: the lines already
#   in the log (the longest first part of them, after the save's mark) are skipped · the rest written in order.
#   (the profit was never counted twice: the books take total_profit, not the lines)
#   python3 devtests/step/patches/p12_fxlog_rest.py ENGINE.py
import os, sys

R = [
    ('''        ms = [m_ for _, m_ in lines]
        if not any(rec[i:i + len(ms)] == ms for i in range(len(rec) - len(ms) + 1)):
            for s_, m_ in lines:
                log_trade_history(s_, m_)
''',
     '''        ms = [m_ for _, m_ in lines]
        done = next(p for p in range(len(ms), -1, -1)                    # أول جزء منها مكتوب (انقطاع بين سطر وسطر) ⇒ الباقي بس
                    if p == 0 or any(rec[i:i + p] == ms[:p] for i in range(len(rec) - p + 1)))
        for s_, m_ in lines[done:]:
            log_trade_history(s_, m_)
'''),
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
    print(f"✅ {len(R)} replacements · compiles · {p}")
