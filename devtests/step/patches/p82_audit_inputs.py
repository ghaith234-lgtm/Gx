# 🩺 patch 82 (dashboard v3.36.50 · the full audit, batch 1: inputs that took the dashboard down) — the owner (14-11): «سوي فحص لكل
#   البوت واكتشف ان هناك اخطاء بكل شي حتى وان كان على شكل وجبات». Found by sending every server request bad inputs in a closed folder:
#   ① DCA «عدد أوامر الأمان» had no upper limit: the table (it recalculates as you type) built one row per order ⇒ a typo like
#      99999999 filled the memory and the whole dashboard went down (and a DCA bot could be deployed with any count) ⇒ limit 100:
#      the table says so · the deploy refuses with a clear message · the trial path's suggested wallet is bounded too
#   ② a request whose body is valid JSON but not an object ([] · "text" · null) cut the connection without an answer ⇒ «طلب غير صالح»
#   ③ pairing the phone app with a non-number app version cut the connection ⇒ the version is read safely
#   python3 devtests/step/patches/p82_audit_inputs.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''DCA_FEE_TAKER = 0.001       # الأساس والإغلاق والأوامر الفورية (آخذ)''',
     '''DCA_FEE_TAKER = 0.001       # الأساس والإغلاق والأوامر الفورية (آخذ)
DCA_MAX_SAFETY = 100        # 🩺 v3.36.50: حد عدد أوامر الأمان (كان بلا حد ⇒ رقم خاطئ كبير يملأ الذاكرة ويوقف اللوحة)'''),
    # ① the table
    ('''    fee_min = 0.20
    fee_warn = tp_raw < fee_min
    tp_pct = max(tp_raw, fee_min) / 100.0
    if base_price <= 0 or base_qty <= 0 or n_safety < 0:
        return []''',
     '''    fee_min = 0.20
    fee_warn = tp_raw < fee_min
    tp_pct = max(tp_raw, fee_min) / 100.0
    if n_safety > DCA_MAX_SAFETY:                      # 🩺 v3.36.50
        return {"rows": [], "msg": f"عدد أوامر الأمان أكبر من الحد ({DCA_MAX_SAFETY}) — اكتب عدداً أصغر"}
    if base_price <= 0 or base_qty <= 0 or n_safety < 0:
        return []'''),
    ('''box.innerHTML='<p style="color:var(--mut);font-size:12px">أكمل الأرقام لرؤية الجدول</p>';return}''',
     '''box.innerHTML='<p style="color:var(--mut);font-size:12px">'+((res&&res.msg)||'أكمل الأرقام لرؤية الجدول')+'</p>';return}'''),
    # ① the deploy
    ('''    if fields["max_safety_orders"] <= 0:
        return {"ok": False, "msg": "يجب أن يكون عدد أوامر الأمان ١ على الأقل"}''',
     '''    if fields["max_safety_orders"] <= 0:
        return {"ok": False, "msg": "يجب أن يكون عدد أوامر الأمان ١ على الأقل"}
    if fields["max_safety_orders"] > DCA_MAX_SAFETY:   # 🩺 v3.36.50
        return {"ok": False, "msg": f"عدد أوامر الأمان أكبر من الحد ({DCA_MAX_SAFETY}) — اكتب عدداً أصغر"}'''),
    # ① the trial path's suggested wallet
    ('''f("size_multiplier", 1), int(f("max_safety_orders", 0))
''', '''f("size_multiplier", 1), min(DCA_MAX_SAFETY, int(min(1e6, f("max_safety_orders", 0))))   # 🩺 v3.36.50
'''),
    # ② a body that is not an object
    ('''            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"ok": False, "msg": "طلب غير صالح"}, 400)
        path = urlparse(self.path).path
        if path == "/api/fonts":''',
     '''            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"ok": False, "msg": "طلب غير صالح"}, 400)
        if not isinstance(data, dict):                     # 🩺 v3.36.50: [] · "نص" · null كانت تقطع الاتصال بلا رد
            return self._json({"ok": False, "msg": "طلب غير صالح"}, 400)
        path = urlparse(self.path).path
        if path == "/api/fonts":'''),
    # ③ the app's version
    ('''"created": int(time.time()), "seen": int(time.time()), "code": int(code or 0), "ip": str(ip)[:45]})''',
     '''"created": int(time.time()), "seen": int(time.time()), "code": _safe(lambda: int(float(code or 0)), default=0) or 0, "ip": str(ip)[:45]})'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    s = s.replace('APP_VERSION = "3.36.49"', 'APP_VERSION = "3.36.50"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
