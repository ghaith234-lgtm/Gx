# 💵 patch 73 (dashboard v3.36.45 · follow-up of p70) — the owner's own ⏸ floor already above the price when the dollars run out ⇒
#   the system changes nothing (it only remembers the floor so it can follow the price up and give it back) — but it still told the 🔔
#   centre «⏸💵 أُوقف الشراء تلقائياً …» (a pause that did not happen). Now that line is written only when the floor really moved.
#   python3 devtests/step/patches/p73_cash_quiet.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''        d["bots"][k] = {"wid": wid, "q": q, "sym": i.get("sym"), "type": i.get("type"), "orig": cur, "set": new,
                        "ts": now, "need": need, "freed": round(freed, 6), "moves": 0}
        _dash_event(i.get("sym") or "",''',
     '''        d["bots"][k] = {"wid": wid, "q": q, "sym": i.get("sym"), "type": i.get("type"), "orig": cur, "set": new,
                        "ts": now, "need": need, "freed": round(freed, 6), "moves": 0}
        if new <= cur * (1 + 1e-9):
            return True                                  # 🔕 v3.36.45: أرضيتك فوق السعر أصلاً ⇒ ما تغيّر شي ⇒ ولا سطر «أُوقف» (نتذكرها بس)
        _dash_event(i.get("sym") or "",'''),
    ('''APP_VERSION = "3.36.44"''', '''APP_VERSION = "3.36.45"'''),
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
