# 🌌🎞️ patch 57 (dashboard · the moving background · the frames) — the owner (13-11): «عند تحريك كروت البوتات الخلفية متحركه تقف ·
#   عندما قللت الفريمات الى ال٦٠ صارت ما اتقطع».
#   ① the moving background no longer stops while the cards scroll (it stopped on purpose since v3.36.37 — the owner wants it moving)
#      · in a phone browser the address bar hides/shows while scrolling (a small height change) ⇒ the background no longer restarts then
#   ② the app (1.5+ — the screen's rate itself changes): a device that never chose starts at 60 (the owner: 60 ⇒ no stutter) · once ·
#      a choice made before stays · the browser keeps 120 (there the screen sets its own rate)
#   ③ ⚙️ «الفريمات»: «60 — الأسلس على أغلب الهواتف» · the frames texts in MSA
#   python3 devtests/step/patches/p57_bg_scroll_fps60.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''  if(!(document.hidden||r.classList.contains('covered')||r.classList.contains('scrolling'))&&now-HB.last>=32){HB.last=now;try{HB.draw(now/1000)}catch(e){}}''',
     '''  if(!(document.hidden||r.classList.contains('covered'))&&now-HB.last>=32){HB.last=now;try{HB.draw(now/1000)}catch(e){}}   // v3.36.39: تتحرك وقت التمرير كمان'''),
    ('''    addEventListener('resize',()=>{clearTimeout(HB.rt);HB.rt=setTimeout(()=>{if(HB.k!=='orig')hbgApply()},250)})}
  const d=Math.min(window.devicePixelRatio||1,1.5);''',
     '''    addEventListener('resize',()=>{clearTimeout(HB.rt);HB.rt=setTimeout(()=>{if(HB.k!=='orig'&&(Math.abs(innerWidth-HB.w)>2||Math.abs(innerHeight-HB.h)>innerHeight*.25))hbgApply()},250)})}
  HB.w=innerWidth;HB.h=innerHeight;   // v3.36.39: شريط عنوان المتصفح يطلع وينزل وقت التمرير ⇒ ما تبدي الخلفية من جديد
  const d=Math.min(window.devicePixelRatio||1,1.5);'''),
    ('''   لوحة رسم واحدة خلف كل شي (#hbg) · 30 إطاراً بالثانية أقصى شي · بدقة أقل من الشاشة · تتوقف خلف النوافذ والصفحات ووقت التمرير والشاشة مطفية ·''',
     '''   لوحة رسم واحدة خلف كل شي (#hbg) · 30 إطاراً بالثانية أقصى شي · بدقة أقل من الشاشة · تتوقف خلف النوافذ والصفحات والشاشة مطفية (v3.36.39: وقت التمرير تكمل) ·'''),
    ('''  if(IN_APP&&s.code>=6)return `الشاشة هسه <b>${s.hz||'?'} Hz</b>${(s.rates||[]).length?' · تدعم: '+s.rates.join(' · '):''} — الأعلى أنعم وياكل بطارية أكثر`;
  if(IN_APP)return 'حدّث التطبيق لنسخة 1.5 حتى تتغيّر سرعة الشاشة نفسها';
  if(IN_WIN)return 'برنامج ويندوز: بالمتصفح الشاشة تحدد سرعتها (من إعدادات ويندوز) — هنا تتحكم بحركات اللوحة (60/30 يخفف)';
  return 'بالمتصفح الشاشة تحدد سرعتها — هنا تتحكم بحركات اللوحة (60/30 يوفّر بطارية)'}''',
     '''  if(IN_APP&&s.code>=6)return `الشاشة الآن <b>${s.hz||'?'} Hz</b>${(s.rates||[]).length?' · تدعم: '+s.rates.join(' · '):''} — <b>60 الأسلس على أغلب الهواتف</b> · الأعلى أنعم إن تحمّله الهاتف ويستهلك بطارية أكثر`;
  if(IN_APP)return 'حدّث التطبيق إلى النسخة 1.5 لتتغيّر سرعة الشاشة نفسها';
  if(IN_WIN)return 'برنامج ويندوز: سرعة الشاشة تُضبط من إعدادات ويندوز — هنا تتحكم بحركات اللوحة (60/30 أخف)';
  return 'في المتصفح تحدد الشاشة سرعتها — هنا تتحكم بحركات اللوحة (60/30 يوفّر البطارية)'}
/* 🎞️ v3.36.39 (المالك 13-11: «عندما قللت الفريمات الى ال٦٠ صارت ما اتقطع»): التطبيق 1.5+ (الشاشة نفسها تتغيّر) — جهاز ما اختار قبل يبدي على 60 · مرة وحدة ·
   الاختيار السابق يبقى · المتصفح يبقى 120 (الشاشة هناك تحدد سرعتها) */
function fpsFirst(){try{if(!IN_APP||_ls('dash_fps')!==null||_ls('dash_fps1'))return;const s=appStat();
  if(!(+s.code>=6)||typeof HolyApp.setFps!=='function')return;_ls('dash_fps1','1');
  if(+s.fps===120||!s.fps){HolyApp.setFps(60);_ls('dash_fps','60');FPSCAP=60;try{tapesKick()}catch(e){}}}catch(e){}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(fpsFirst,0));else setTimeout(fpsFirst,0);'''),
    ('''  const g=G.ok===null?'🎮 كرت الشاشة: ما كدرت أفحصه':G.ok?`🎮 الرسم على كرت الشاشة ✅${G.name?' ('+gEsc(G.name)+')':''}`:`⚠️ الرسم على المعالج مو كرت الشاشة${G.name?' ('+gEsc(G.name)+')':''} — ${fix}`;''',
     '''  const g=G.ok===null?'🎮 كرت الشاشة: تعذّر فحصه':G.ok?`🎮 الرسم على كرت الشاشة ✅${G.name?' ('+gEsc(G.name)+')':''}`:`⚠️ الرسم على المعالج لا على كرت الشاشة${G.name?' ('+gEsc(G.name)+')':''} — ${fix}`;'''),
    ('''  const fix=IN_APP?'حدّث «Android System WebView» من متجر Google':IN_WIN?'بـEdge: الإعدادات ← النظام والأداء ← «استخدام تسريع الرسومات عند توفره» شغّله وسكّر البرنامج وافتحه':'فعّل «تسريع العتاد / Hardware acceleration» من إعدادات المتصفح';''',
     '''  const fix=IN_APP?'حدّث «Android System WebView» من متجر Google':IN_WIN?'في Edge: الإعدادات ← النظام والأداء ← «استخدام تسريع الرسومات عند توفره» فعّله ثم أغلق البرنامج وافتحه':'فعّل «تسريع العتاد / Hardware acceleration» من إعدادات المتصفح';'''),
    ('''    el.innerHTML=g+`<br>🖥️ الشاشة هسه ~${hz} Hz`+(IN_WIN?' — ترفعها من إعدادات ويندوز ← النظام ← العرض ← العرض المتقدم ← «معدل التحديث»':'')})}''',
     '''    el.innerHTML=g+`<br>🖥️ الشاشة الآن ~${hz} Hz`+(IN_WIN?' — ارفعها من إعدادات ويندوز ← النظام ← العرض ← العرض المتقدم ← «معدل التحديث»':'')})}'''),
    ('''  toast('🎞️ '+f+' فريم'+(f>=120?' — أنعم (ياكل بطارية أكثر)':' — يوفّر بطارية'),true);''',
     '''  toast('🎞️ '+f+' فريم'+(f>=120?' — أنعم إن تحمّله الجهاز (يستهلك بطارية أكثر)':f===60?' — الأسلس على أغلب الهواتف':' — يوفّر البطارية'),true);'''),
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
