# ⚠️ patch 26 (dashboard · every page) — the owner (7-11, a screenshot): «عند تشغيل البرنامج تخرج هذه المشكلة صلحها» — the toast
#   «⚠️ خلل واجهة: ResizeObserver loop completed with undelivered notifications.»
#   The cause: the 🔁 periodic bot's order box (v3.36.14: 3 orders, the rest scroll) is fitted from a ResizeObserver, and the fit set the
#   box's own max-height INSIDE the observer's callback ⇒ the box changed size while the browser was delivering its size ⇒ the browser
#   reports «loop completed with undelivered notifications» as a page error (harmless: it delivers on the next frame) ⇒ the
#   dashboard's catcher (every page error ⇒ a toast) showed it at every start with a 🔁 bot.
#   ① the fit runs on the next frame (requestAnimationFrame) — the box no longer resizes inside the callback ⇒ no loop at all
#   ② the catcher skips that one browser note (it can also come from the browser itself or an extension and is never a fault);
#      every other page error still shows its toast
#   python3 devtests/step/patches/p26_ro_loop.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''RCF_RO=RCF_RO||new ResizeObserver(es=>es.forEach(e=>rcFit3(e.target)));''',
     '''RCF_RO=RCF_RO||new ResizeObserver(es=>requestAnimationFrame(()=>es.forEach(e=>rcFit3(e.target))));'''),
    ('''window.addEventListener('error',e=>{try{toast('⚠️ خلل واجهة: '+e.message,false)}catch(_){}});''',
     '''window.addEventListener('error',e=>{try{if(/ResizeObserver loop/.test(String((e&&e.message)||'')))return;   // ⚠️ v3.36.24: ملاحظة المتصفح (مو خلل) — تنعرض الجاية بالإطار التالي
  toast('⚠️ خلل واجهة: '+e.message,false)}catch(_){}});'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
