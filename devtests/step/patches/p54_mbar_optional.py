# 📌 patch 54 (dashboard · the small top bar optional) — the owner (13-11, a screenshot of the thin bar «🔄 0.62 · 💵 410.15 · 📅 0.62 · 🛡️ 3»
#   that comes down when the page is scrolled): «خلي هذا الشريط في الاعدادات اختياري».
#   ⚙️ 🖌️ «📌 الشريط المصغّر» (this device): on (as before) / off · applied before the page is drawn (no flash) · its items to add
#   (battery · the bots' computer …) wait for the owner's choice.
#   python3 devtests/step/patches/p54_mbar_optional.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''if(localStorage.getItem('dash_lite')==='on')document.documentElement.classList.add('lite')}catch(e){}</script>''',
     '''if(localStorage.getItem('dash_lite')==='on')document.documentElement.classList.add('lite');
if(localStorage.getItem('dash_mbar')==='off')document.documentElement.classList.add('nombar')}catch(e){}</script>'''),
    ('''.sfoot{color:var(--mut2);font-size:11px;margin:14px 6px 0;line-height:1.7}''',
     '''.sfoot{color:var(--mut2);font-size:11px;margin:14px 6px 0;line-height:1.7}
html.nombar #mbar{display:none!important}   /* 📌 v3.36.38: الشريط المصغّر مطفي بهذا الجهاز */'''),
    ('''     +T('🕺','رجل العصا','STK.toggle();openSettings()','bStk',''',
     '''     +T('📌','الشريط المصغّر','uiMbarToggle()','bMbar',uiMbar(),'يظهر — أرقام اليوم أعلى الشاشة حين تنزل للأسفل','مخفي')
     +T('🕺','رجل العصا','STK.toggle();openSettings()','bStk','''),
    ('''function mbarSync(){''',
     '''function uiMbar(){return _ls('dash_mbar')!=='off'}                  // 📌 v3.36.38: الشريط المصغّر اختياري (لهذا الجهاز)
function uiMbarToggle(){const on=!uiMbar();_ls('dash_mbar',on?null:'off');document.documentElement.classList.toggle('nombar',!on);openSettings();
  toast(on?'📌 الشريط المصغّر يظهر حين تنزل للأسفل':'📌 الشريط المصغّر مخفي',true)}
function mbarSync(){'''),
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
