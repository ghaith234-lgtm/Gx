# 🩺 patch 83 (dashboard v3.36.50 · the full audit, batch 1 — the control requests) — found by the same bad-input sweep (p82):
#   ④ /api/control with «dir» missing or not text cut the connection (os.path.join on None) ⇒ read as text ⇒ «البوت غير موجود»
#   ⑤ five settings actions (guard_ack · ticker_set · pxa_set · ina_set · guard_cfg) with «value» not an object cut the connection
#     ⇒ read as an empty object
#   ⑥ the DCA table divided by zero when the profit target makes the exit price zero (a sell DCA with target 100%) · the «levels above
#     from your coins» calculator divided by zero on a grid step too small to count ⇒ both answer with a clear message
#   ⑦ a leftover action «shutdown_beacon» (nothing in the page sends it · «die» is the one --stop uses and stays) stopped every bot and closed the dashboard for any signed-in
#     request ⇒ removed
#   python3 devtests/step/patches/p83_audit_control.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            return self._json(control(data.get("dir", ""), act, data.get("value")))''',
     '''            return self._json(control(str(data.get("dir") or ""), act, data.get("value")))   # 🩺 v3.36.50: «dir» ليس نصاً كان يقطع الاتصال'''),
    ('''            if act == "shutdown_beacon":
                # يُستدعى من المتصفح عند إغلاق التبويب (sendBeacon) — يوقف كل البوتات
                stop_all_bots("أُغلق التبويب")
                kill_all_bot_procs()
                threading.Timer(0.5, lambda: os._exit(0)).start()
                return self._json({"ok": True, "msg": "🛑 توقف الكل"})
''', '''            # 🩺 v3.36.50: «shutdown_beacon» انشال — بقايا قديمة (ولا شي بالصفحة يرسله) كانت توقف كل البوتات وتطفي اللوحة بأي طلب
'''),
    ('''        avg = cv / cq
        tgt = _target(avg)
        if is_buy:
            prof = cnet * tgt * (1 - DCA_FEE_TAKER) - cv''',
     '''        avg = cv / cq
        tgt = _target(avg)
        if not (tgt > 0 and price > 0):                # 🩺 v3.36.50: هدف يجعل سعر الخروج صفراً (أو مستوى تحت الصفر) كان يقسم على صفر
            return {"rows": [], "msg": "الأرقام تجعل سعر الخروج أو أحد المستويات صفراً — صغّر هدف الربح أو المسافة"}
        if is_buy:
            prof = cnet * tgt * (1 - DCA_FEE_TAKER) - cv'''),
    ('''    step = 1.0 + g
    if top > 0:
        if top < base * step * (1 - 1e-9):''',
     '''    step = 1.0 + g
    if not step > 1.0:                                 # 🩺 v3.36.50: نسبة أصغر من أن تُحسب كانت تقسم على صفر
        return {"ok": False, "msg": "نسبة الشبكة صغيرة جداً"}
    if top > 0:
        if top < base * step * (1 - 1e-9):'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a, b = 'data.get("value") or {}', '(data.get("value") if isinstance(data.get("value"), dict) else {})'
    if s.count(a) != 5:
        print(f"❌ value-object sites: {s.count(a)}"); sys.exit(1)
    s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + 5 value sites · compiles · {p}")
