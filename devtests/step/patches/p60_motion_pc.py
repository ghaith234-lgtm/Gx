# 🎬 patch 60 (dashboard · the motion on a computer) — the owner (13-11, from the Windows program): «الخلفية المتحركة ما تشغل على الحاسوب
#   وكلك حركة البطاقات».
#   Nothing on a big screen stops them except an open window — the computer reports «reduce motion» (Windows: Settings ⇒ Accessibility ⇒
#   Visual effects ⇒ «Animation effects» off · also «Adjust for best performance») ⇒ the dashboard stops every motion on purpose, and the
#   switch to run it anyway sat only inside «🎬 حركة فتح النوافذ».
#   Now: ① the moving background row and the card motions row say it too, with the same «▶️ شغّل الحركة رغم إعداد الجهاز» button
#   ② picking a moving background on such a device ⇒ it asks once (this session) ③ a device that already has a moving background chosen
#   and reports «reduce motion» ⇒ it asks once when the dashboard opens (this device · never again after an answer).
#   python3 devtests/step/patches/p60_motion_pc.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''function setMotionForce(on){_ls('dash_motion_force',on?'on':null);try{hbgApply()}catch(e){}openSettings();
  toast(on?'🎬 الحركة تعمل رغم إعداد الجهاز':'🎬 اللوحة تتبع إعداد الجهاز (تقليل الحركة)',true)}''',
     '''function setMotionForce(on){_ls('dash_motion_force',on?'on':null);try{hbgApply()}catch(e){}openSettings();
  toast(on?'🎬 الحركة تعمل رغم إعداد الجهاز':'🎬 اللوحة تتبع إعداد الجهاز (تقليل الحركة)',true)}
/* 🎬 v3.36.40 (المالك 13-11: «الخلفية المتحركة ما تشغل على الحاسوب وكلك حركة البطاقات»): الحاسوب مضبوط على «تقليل الحركة» ⇒ يسأل مرة —
   لما يختار خلفية متحركة (مرة بالجلسة) · أو تنفتح اللوحة وعنده خلفية متحركة مختارة (مرة لهذا الجهاز) · الجواب ينحفظ لهذا الجهاز */
function rmStop(){return hwDevRm()&&!hwForce()&&!uiLite()}
function rmRow(){return rmStop()?`<div class="snote" style="color:var(--amber)">⚠️ الحركة متوقفة: هذا الجهاز مضبوط على «تقليل الحركة».</div><div class="pollrow" style="margin-bottom:8px"><button type="button" class="rmGo" onclick="setMotionForce(true)">▶️ شغّل الحركة رغم إعداد الجهاز</button></div>`:''}
function rmAsk(back){if(!rmStop())return;_ls('dash_rm_seen','1');
  showDialog(`<h2>🎬 الحركة متوقفة على هذا الجهاز</h2><p style="color:var(--mut);font-size:13.5px;line-height:1.9">هذا الجهاز مضبوط على «تقليل الحركة»
    (ويندوز: الإعدادات ⇐ إمكانية الوصول ⇐ التأثيرات المرئية ⇐ «تأثيرات الحركة» · أندرويد: إمكانية الوصول ⇐ «إزالة الرسوم المتحركة»)،
    لذلك أوقفت اللوحة الخلفية المتحركة وحركات البطاقات والنوافذ.</p><p style="font-size:13.5px;line-height:1.9">تشغيلها على هذا الجهاز؟ تُرجعها من ⚙️ في أي وقت.</p>
    <div class="mbtns"><button class="primary" id="rmY">▶️ شغّل الحركة</button><button id="rmN">اتركها متوقفة</button></div>`);
  $('#rmY').onclick=()=>{_ls('dash_motion_force','on');try{hbgApply()}catch(e){}if(back)openSettings();else hideModal();toast('🎬 الحركة تعمل على هذا الجهاز رغم إعداده',true)};
  $('#rmN').onclick=()=>{if(back)openSettings();else hideModal()}}
function rmBoot(n){n=n||0;try{if(!rmStop()||_ls('dash_rm_seen')||uiBg()==='orig')return;
  const m=$('#mbg');if(document.getElementById('splash')||(m&&!m.hidden)||document.hidden){if(n<20)setTimeout(()=>rmBoot(n+1),1500);return}rmAsk(false)}catch(e){}}'''),
    ('''function setBg(v){if(!HBG.some(x=>x[0]===v))v='orig';_ls('dash_bg',v==='orig'?null:v);hbgApply();openSettings();
  toast('🌌 الخلفية: '+HBG.find(x=>x[0]===v)[1],true)}''',
     '''function setBg(v){if(!HBG.some(x=>x[0]===v))v='orig';_ls('dash_bg',v==='orig'?null:v);hbgApply();openSettings();
  toast('🌌 الخلفية: '+HBG.find(x=>x[0]===v)[1],true);
  if(v!=='orig'&&rmStop()){let s='';try{s=sessionStorage.getItem('holy_rmask')||'';sessionStorage.setItem('holy_rmask','1')}catch(e){}if(!s)setTimeout(()=>rmAsk(true),450)}}   // 🎬 v3.36.40'''),
    ('''        `<div class="snote">تتلوّن بـ«🎨 الألوان» المختارة · تتوقف وحدها خلف النوافذ وفي «⚡ الوضع الخفيف» · «الأصلية» كما كانت.</div><div class="bgrid" id="bgRow">''',
     '''        `${rmRow()}<div class="snote">تتلوّن بـ«🎨 الألوان» المختارة · تتوقف وحدها خلف النوافذ وفي «⚡ الوضع الخفيف» · «الأصلية» كما كانت.</div><div class="bgrid" id="bgRow">'''),
    ('''  return `<div class="snote">اضغط أي خيار فيتحرك على البطاقة التجريبية فوراً · يُحفظ لهذا الجهاز.${caOff()?` <b style="color:var(--amber)">الحركة متوقفة الآن على البطاقات (${uiLite()?'الوضع الخفيف':'إعداد الجهاز — ⚙️ «حركة فتح النوافذ»'}) — التجربة هنا فقط.</b>`:''}</div>''',
     '''  return `${rmRow()}<div class="snote">اضغط أي خيار فيتحرك على البطاقة التجريبية فوراً · يُحفظ لهذا الجهاز.${caOff()?` <b style="color:var(--amber)">الحركة متوقفة الآن على البطاقات (${uiLite()?'الوضع الخفيف':'إعداد الجهاز'}) — التجربة هنا فقط.</b>`:''}</div>'''),
    ('''tick();schedPoll();applyTheme(uiTheme());STK.boot();''',
     '''tick();schedPoll();applyTheme(uiTheme());STK.boot();setTimeout(rmBoot,3600);'''),
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
