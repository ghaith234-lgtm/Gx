# 🎬 patch 55 (dashboard · the motion on the computer) — the owner (13-11): «انميشن في برنامج الحاسوب لن يشتغل».
#   The Windows program opens the dashboard in Microsoft Edge (app mode) — every motion works there. The dashboard itself switches the
#   motion off on purpose in two cases: «⚡ الوضع الخفيف» on that device (settings are per device), or the device set to reduce motion
#   (Windows: Settings ⇒ Accessibility ⇒ Visual effects ⇒ «Animation effects» off — many computers have it off ⇒ Edge reports
#   «prefers-reduced-motion») — and it never said which.
#   Now: ① ⚙️ «🎬 حركة فتح النوافذ» says why it is stopped (the light mode · the device's setting) ② when it is the device's setting:
#   «▶️ شغّل الحركة رغم إعداد الجهاز» (this device · the windows and the moving background) and back ③ the motion check says it too.
#   python3 devtests/step/patches/p55_motion_device.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''function hwStyle(){try{if(document.documentElement.classList.contains('lite'))return 'none';
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return 'none'}catch(e){}return uiAnim()}''',
     '''function hwStyle(){try{if(document.documentElement.classList.contains('lite'))return 'none';
  if(hwDevRm()&&!hwForce())return 'none'}catch(e){}return uiAnim()}
function hwDevRm(){try{return !!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)}catch(e){return false}}   // 🎬 v3.36.38
function hwForce(){return _ls('dash_motion_force')==='on'}            // شغّل الحركة رغم «تقليل الحركة» بالجهاز (لهذا الجهاز)
function setMotionForce(on){_ls('dash_motion_force',on?'on':null);try{hbgApply()}catch(e){}openSettings();
  toast(on?'🎬 الحركة تعمل رغم إعداد الجهاز':'🎬 اللوحة تتبع إعداد الجهاز (تقليل الحركة)',true)}'''),
    ('''function hbStill(){try{return uiLite()||!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)}catch(e){return false}}''',
     '''function hbStill(){try{return uiLite()||(hwDevRm()&&!hwForce())}catch(e){return false}}'''),
    ('''  const anN=((HW_ANIMS.find(x=>x[0]===an)||[])[1]||'')+(an!=='none'&&hwStyle()==='none'?' · متوقفة':'');''',
     '''  const anN=((HW_ANIMS.find(x=>x[0]===an)||[])[1]||'')+(an!=='none'&&hwStyle()==='none'?(uiLite()?' · متوقفة (الوضع الخفيف)':' · متوقفة (إعداد الجهاز)'):'');
  const rmN=hwDevRm()?`<div class="snote" style="color:var(--amber)">⚠️ هذا الجهاز مضبوط على «تقليل الحركة» — ويندوز: الإعدادات ⇐ إمكانية الوصول ⇐ التأثيرات المرئية ⇐ «تأثيرات الحركة» · أندرويد: إمكانية الوصول ⇐ «إزالة الرسوم المتحركة».
    ${hwForce()?'الحركة تعمل هنا رغم ذلك.':'لذلك اللوحة أوقفت الحركة.'}</div><div class="pollrow" style="margin-bottom:8px"><button id="motForce" class="${hwForce()?'on':''}" onclick="setMotionForce(${!hwForce()})">${hwForce()?'↩️ اتبع إعداد الجهاز':'▶️ شغّل الحركة رغم إعداد الجهاز'}</button></div>`:'';'''),
    ('''     +X('anim','🎬','حركة فتح النوافذ',anN,`<div class="snote">الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة.</div><div class="pollrow" id="animRow">${AB}</div>`)''',
     '''     +X('anim','🎬','حركة فتح النوافذ',anN,`${rmN}<div class="snote">الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة.</div><div class="pollrow" id="animRow">${AB}</div>`)'''),
    ('''  if(s==='none'){toast(uiLite()?'⚡ الوضع الخفيف مفعّل — لا حركة لقياسها':'📴 الهاتف مضبوط على تقليل الحركة — لا حركة لقياسها',false);return}''',
     '''  if(s==='none'){toast(uiLite()?'⚡ الوضع الخفيف مفعّل — لا حركة لقياسها':uiAnim()==='none'?'🎬 الحركة المختارة «بلا حركة» — لا شيء لقياسه':'📴 هذا الجهاز مضبوط على «تقليل الحركة» — ⚙️ ⇐ حركة فتح النوافذ ⇐ «شغّل الحركة رغم إعداد الجهاز»',false);return}'''),
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
