# ⚙️ patch 45 (dashboard · the settings window) — the owner (13-11): «الاعدادات سوي الكل لستات يعني المظهر اضغط عليه يظهرن اللوان كذلك
#   الفريمات يعني كلهم · واريد التوزيع يختلف مثلا صوت الربح مع صوت القفل شريط الاسعار مع التليجرام لان اثنينهم خاصه بالاشعارات».
#   ① every setting is one row of a list (like a phone's settings): a row with choices shows its current value and opens them on a tap
#      (🎨 المظهر ⇒ the colours · 🃏 the cards · 🔤 the font · 🎬 the motion · ⏱️ the refresh · 🎞️ the frames) · on/off settings carry a
#      switch on their own row · the windows (🔐 · 🩺 · 📈 …) are rows ending with ‹
#   ② the groups: 🖌️ الشكل والحركة · ⚡ الأداء · 🔔 الإشعارات (تيليغرام + شريط الأسعار وإشعاراته) · 🔊 الأصوات (الربح + فتح القفل) ·
#      📱 التطبيقات · 🛡️ الحماية والتشغيل · 🩺 التشخيص · 🖥️ النظام · ⚠️ منطقة الخطر
#   ③ an opened row stays open when the window is drawn again (after a choice) — it is remembered until the page reloads
#   ④ the texts of this window in MSA
#   ⑤ lighter to open: the refresh from the server (tick) and the graphics-card line wait until the opening motion is over
#   ⑥ the refresh keeps the rows' own classes (it set the whole class name of 🤖 / 🪟 — now it only switches «on»)
#   python3 devtests/step/patches/p45_settings_list.py Holy_Dashboard.pyw
import os, sys

OLD_FN_HEAD = '''/* ⚙️ درج الإعدادات — مقسّم: تشخيص · حماية وتشغيل · نظام · منطقة خطر */
function openSettings(){'''
OLD_FN_TAIL = '''   <p style="color:var(--mut2);font-size:11px;margin-top:12px;line-height:1.7">
     ولا زر هنا يلمس أوامر البوتات بالمنصة — أدوات لوحة وتشخيص وتشغيل.</p>
   <div class="mbtns"><button onclick="hideModal()">إغلاق</button></div>`);
  tick();gpuFill();
}'''

NEW_FN = r'''/* ⚙️ v3.36.35 (المالك 13-11): الإعدادات قائمة — كل إعداد صف: صف الخيارات يبين قيمته الحالية وتنفتح خياراته بضغطة (🎨 المظهر ⇒ الألوان ·
   🎞️ الفريمات …) · التشغيل والإطفاء بمفتاح على صفه · النوافذ صفوف تنتهي بـ‹ · الصف المفتوح يبقى مفتوحاً لما تنرسم النافذة من جديد ·
   المجموعات: الشكل والحركة · الأداء · الإشعارات (تيليغرام + شريط الأسعار) · الأصوات (الربح + فتح القفل) · التطبيقات · الحماية · التشخيص · النظام · الخطر */
const STO=new Set();let STT=0;
function stTog(k){const on=!STO.has(k);if(on)STO.add(k);else STO.delete(k);
  const r=document.querySelector('#modal .sx[data-k="'+k+'"]');
  if(r){r.classList.toggle('open',on);r.classList.add('anim');const h=r.querySelector('.shd');if(h)h.setAttribute('aria-expanded',String(on))}
  if(on&&k==='fps')try{gpuFill()}catch(e){}}
function openSettings(){
  const d=DATA||{}, os=d.srv_os||'';
  const X=(k,ic,t,val,body)=>`<div class="sitem sx${STO.has(k)?' open':''}" data-k="${k}"><button type="button" class="shd" aria-expanded="${STO.has(k)}" onclick="stTog('${k}')">
    <span class="sic">${ic}</span><span class="stt"><b>${t}</b></span><span class="sval">${val}</span><span class="sch" aria-hidden="true">⌄</span></button><div class="sbody">${body}</div></div>`;
  const T=(ic,t,fn,id,on,a,b)=>`<button type="button" id="${id}" class="sitem stg${on?' on':''}" role="switch" aria-checked="${!!on}" onclick="${fn}">
    <span class="sic">${ic}</span><span class="stt"><b>${t}</b><small>${on?a:b}</small></span><span class="ssw" aria-hidden="true"><i></i></span></button>`;
  const L=(ic,t,fn,sub,id)=>`<button type="button" ${id?`id="${id}" `:''}class="sitem sln" onclick="${fn}">
    <span class="sic">${ic}</span><span class="stt"><b>${t}</b>${sub?`<small>${sub}</small>`:''}</span><span class="sch" aria-hidden="true">›</span></button>`;   // يتعكس باتجاه العربي ⇒ يبين ‹
  const G=(t,rows,warn)=>`<div class="sgrp${warn?' warn':''}"><div class="sgt">${t}</div><div class="sgl">${rows}</div></div>`;
  const win=(os==='nt'), lin=(!!os&&os!=='nt');
  const th=uiTheme(),pm=pollMs(),fp=uiFps(),sk=uiSkin(),an=uiAnim();
  const thT=THEMES.find(t=>t[0]===th)||THEMES[0], fnT=HFONTS.find(x=>x[0]===uiFont())||HFONTS[0];
  const SKS=[['old','القديم'],['c','ج — الرسمة أولاً'],['b','ب — شريط الأرقام'],['o','OKX']];
  const POL=[[2000,'سريع 2ث'],[3000,'عادي 3ث'],[6000,'موفّر 6ث'],[10000,'هادئ 10ث']];
  const TB=THEMES.map(t=>`<button class="thb ${t[0]===th?'on':''}" onclick="setTheme('${t[0]}')" title="${t[1]}">
      <span class="sw3" style="background:${t[2]}"><i style="background:${t[3]}"></i><i style="background:${t[4]}"></i><i style="background:${t[5]}"></i></span>
      <span>${t[1]}${t[0]===th?' ✓':''}</span></button>`).join('');
  const PB=POL.map(p=>`<button class="${p[0]===pm?'on':''}" onclick="setPoll(${p[0]})">${p[1]}</button>`).join('');
  const FB=[240,120,60,30].map(f=>`<button class="${f===fp?'on':''}" onclick="setFps(${f})">${f}</button>`).join('');
  const SB=SKS.map(x=>`<button class="${sk===x[0]?'on':''}" onclick="setSkin('${x[0]}')">${x[1]}</button>`).join('');
  const FN=HFONTS.map(x=>`<button class="${fnT[0]===x[0]?'on':''}" data-font="${x[0]}" style="font-family:${x[1]==='system-ui'?'system-ui':`'${x[1]}'`},system-ui" onmouseenter="hFontPre('${x[0]}')" onclick="setFont('${x[0]}')">${x[2]}</button>`).join('');
  const AB=HW_ANIMS.map(x=>`<button class="${an===x[0]?'on':''}" data-anim="${x[0]}" onclick="setAnim('${x[0]}')">${x[1]}</button>`).join('');
  const anN=((HW_ANIMS.find(x=>x[0]===an)||[])[1]||'')+(an!=='none'&&hwStyle()==='none'?' · متوقفة':'');
  const ff=fnT[1]==='system-ui'?'system-ui':`'${fnT[1]}',system-ui`;
  showModal(`<h2>⚙️ الإعدادات والأدوات</h2>
   <div class="sgrid">
   ${G('🖌️ الشكل والحركة — لهذا الجهاز',
      X('theme','🎨','المظهر',`<i class="sdot" style="background:${thT[3]}"></i>${thT[1]}`,`<div class="thgrid">${TB}</div>`)
     +X('skin','🃏','شكل البطاقات',(SKS.find(x=>x[0]===sk)||SKS[0])[1],`<div class="snote">الأرقام والأزرار نفسها في كل الأشكال.</div><div class="pollrow" id="skinRow">${SB}</div>`)
     +X('font','🔤','خط الكتابة',`<span style="font-family:${ff}">${fnT[2]}</span>`,`<div class="snote">كل زر مكتوب بخطّه · الأرقام تبقى بخطّها الثابت.</div><div class="pollrow" id="fontRow">${FN}</div>`)
     +X('anim','🎬','حركة فتح النوافذ',anN,`<div class="snote">الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة.</div><div class="pollrow" id="animRow">${AB}</div>`)
     +T('🕺','رجل العصا','STK.toggle();openSettings()','bStk',STK.on(),'يعمل — يمشي ويلعب فوق الأيقونات · اسحبه','متوقف'))}
   ${G('⚡ الأداء',
      T('⚡','الوضع الخفيف','uiLiteToggle()','bLite',uiLite(),'مفعّل — بلا حركات ولا ضبابية','متوقف — الحركات كاملة')
     +X('poll','⏱️','تحديث الأرقام',(POL.find(p=>p[0]===pm)||POL[1])[1],`<div class="snote">كل كم ثانية تُقرأ الأرقام من الخادم — الأسعار لحظية في كل الأحوال.</div><div class="pollrow">${PB}</div>`)
     +X('fps','🎞️','الفريمات',fp+' فريم',`<div class="snote">سلاسة الحركة — ${fpsNote()}</div><div class="pollrow" id="fpsRow">${FB}</div><div id="gpuNote" style="font-size:10.5px;color:var(--mut2);margin-top:8px;line-height:1.7">🎮 …</div>`))}
   ${G('🔔 الإشعارات',
      T('✈️','تنبيهات تيليغرام',"g('mute');setTimeout(openSettings,700)",'sMute',!d.muted,'تعمل — تصل إلى تيليغرام','مكتومة — لا تصل')
     +L('📈','شريط الأسعار وإشعاراته','openTicker()','العملات في الشريط · إشعارات الأسعار'))}
   ${G('🔊 الأصوات — لهذا الجهاز',
      T('🎵','صوت الربح',"toggleSound();openSettings()",'sSound',soundOn(),'يعمل — نغمة مع كل ربح','متوقف')
     +T('🔊','صوت فتح القفل','uiUnlockToggle()','bUnl',uiUnlockOn(),'يعمل — نغمة عند فتح القفل','متوقف'))}
   ${G('📱 التطبيقات',
      L('📱','تطبيق أندرويد','openAppPanel()',IN_APP?'أنت داخل من التطبيق الآن':'تنزيله · إشعارات مختصرة على الهاتف','bApp')
     +L('💻','برنامج ويندوز','openWinPanel()',IN_WIN?'أنت داخل من البرنامج الآن':'نافذة خاصة على الحاسوب','bWin'))}
   ${G('🛡️ الحماية والتشغيل',
      L('🔐','كلمة السر','openSecurity()','حماية اللوحة')
     +T('🔒','قفل البطاقات — لهذا الجهاز','uiCardLockToggle()','bCLock',uiCardLock(),'مفعّل — اضغط 🔒 في البطاقة قبل أي زر','غير مفعّل')
     +T('🤖','الحارس الآلي',"g('watchdog');setTimeout(openSettings,700)",'bWd',!!d.watchdog,'يعمل — يعيد تشغيل البوت المتوقف','متوقف — البوت المتوقف يبقى متوقفاً')
     +L('🛡️','فحص الرقابة الآن',"g('guard_scan')",'مطابقة الأرصدة والأوامر مع المنصة'))}
   ${G('🩺 التشخيص', L('🩺','تشخيص','runDiag()')+L('📄','تقرير كامل','openExport()')+L('🔍','فحص OKX','okxCheck()')+L('🧰','المكتبات','openLibs()'))}
   ${G('🖥️ النظام', ((lin||!os)?L('🐧','إقلاع لينكس','openBoot()'):'')
      +((win||!os)?T('🪟','إقلاع ويندوز',"g('boot');setTimeout(openSettings,700)",'bBoot',!!d.boot,'مفعّل — تعمل مع تشغيل الحاسوب','معطّل'):'')
      +L('🧬','تحديث المحركات','confirmUpgrade()'))}
   ${G('⚠️ منطقة الخطر', L('📒','بداية جديدة للحسابات','confirmLedgerReset()'), true)}
   <p class="sfoot">لا يلمس أيُّ زر هنا أوامرَ البوتات في المنصة — أدوات للوحة والتشخيص والتشغيل.</p>
   </div>
   <div class="mbtns"><button onclick="hideModal()">إغلاق</button></div>`);
  clearTimeout(STT);STT=setTimeout(()=>{try{tick()}catch(e){}try{gpuFill()}catch(e){}},(HW_MS[hwStyle()]||0)+120);   // ⑤ بعد ما تخلص حركة الفتح
}'''

CSS_ANCHOR = '''.hwclone{overflow:hidden}
'''
CSS_NEW = '''.hwclone{overflow:hidden}
/* ═══ ⚙️ v3.36.35: الإعدادات قائمة — صف لكل إعداد · قيمته الحالية ظاهرة · تضغطه تنفتح خياراته · المفتاح على صفه ═══ */
.sgrid{max-width:780px;margin:0 auto}
.sgrp{margin-top:16px}.sgrp:first-child{margin-top:2px}
.sgt{font-size:11.5px;font-weight:600;color:var(--mut);margin:0 6px 7px}
.sgrp.warn .sgt{color:var(--red)}
.sgl{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:rgb(var(--surf-rgb)/.35)}
.sgl>.sitem+.sitem{border-top:1px solid var(--line)}
.sitem{display:block;width:100%;margin:0}
button.shd,button.stg,button.sln{display:flex;align-items:center;gap:12px;width:100%;min-height:54px;margin:0;padding:10px 14px;border:0;border-radius:0;
  background:none;color:var(--tx);font-size:13px;font-weight:400;text-align:start;box-shadow:none;transform:none;transition:background .15s}
button.shd:hover,button.stg:hover,button.sln:hover{transform:none;box-shadow:none;background:rgb(var(--surf-rgb)/.7)}
button.shd:active,button.stg:active,button.sln:active{transform:none;background:rgb(var(--surf-rgb)/.9)}
button.stg.on{color:var(--tx);border-color:transparent;box-shadow:none}
.sic{flex:none;width:26px;text-align:center;font-size:19px;line-height:1}
.stt{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:2px}
.stt b{font-size:13.5px;font-weight:600}
.stt small{font-size:11px;color:var(--mut2);line-height:1.5}
.stg.on .stt small{color:var(--green)}
.sgrp.warn .sln b{color:var(--red)}
.sval{flex:0 1 auto;max-width:48%;display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sval>span{overflow:hidden;text-overflow:ellipsis}
.sdot{flex:none;width:12px;height:12px;border-radius:50%;display:inline-block;border:1px solid var(--line2)}
.sch{flex:none;color:var(--mut2);font-size:15px;line-height:1;transition:transform .2s ease}
.sx.open .sch{transform:rotate(180deg)}
.sx.open .shd{background:rgb(var(--surf-rgb)/.5)}
.sbody{display:none;padding:4px 14px 14px}
.sx.open .sbody{display:block}
.sx.open.anim .sbody{animation:sbIn .22s cubic-bezier(.2,.8,.2,1)}
@keyframes sbIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.snote{font-size:11px;color:var(--mut2);margin:0 0 8px;line-height:1.7}
.ssw{flex:none;position:relative;width:44px;height:26px;border-radius:13px;background:rgb(140 140 165/.38);transition:background .2s}
.ssw i{position:absolute;top:3px;inset-inline-start:3px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgb(0 0 0/.35);transition:inset-inline-start .2s}
.stg.on .ssw{background:var(--green)}
.stg.on .ssw i{inset-inline-start:21px}
.sfoot{color:var(--mut2);font-size:11px;margin:14px 6px 0;line-height:1.7}
'''

R = [
    ('''  _sf('#bWd',x=>x.className=d.watchdog?'on':'');
  _sf('#bBoot',x=>x.className=d.boot?'on':'');''',
     '''  _sf('#bWd',x=>x.classList.toggle('on',!!d.watchdog));             // ⚙️ v3.36.35: «on» فقط (صف القائمة له أصنافه)
  _sf('#bBoot',x=>x.classList.toggle('on',!!d.boot));'''),
    (CSS_ANCHOR, CSS_NEW),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    # ① the whole old openSettings (head … tail) becomes the new one
    if s.count(OLD_FN_HEAD) != 1 or s.count(OLD_FN_TAIL) != 1:
        print(f"❌ openSettings: head {s.count(OLD_FN_HEAD)} · tail {s.count(OLD_FN_TAIL)} — nothing written"); sys.exit(1)
    a = s.index(OLD_FN_HEAD); b = s.index(OLD_FN_TAIL) + len(OLD_FN_TAIL)
    if not 0 < a < b or s[a:b].count("\nfunction ") != 1:
        print("❌ openSettings: the span holds more than one function — nothing written"); sys.exit(1)
    s = s[:a] + NEW_FN + s[b:]
    for i, (x, y) in enumerate(R, 1):
        if s.count(x) != 1:
            print(f"❌ replacement {i}: found {s.count(x)} times — nothing written: {x[:90]!r}"); sys.exit(1)
        s = s.replace(x, y)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ openSettings rewritten + {len(R)} replacements · compiles · {p}")
