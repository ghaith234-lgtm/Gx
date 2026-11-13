# 🎬 patch 49 (dashboard · ⚙️ 🩺 «فحص سلاسة الحركة») — the owner (13-11): «الانميشن فيه بعده مشكلة يقطع وشوي بطئة».
#   The motions are measured here on a desktop machine with the CPU slowed ×4 — the owner's phone (its screen rate, its graphics chip,
#   the app's WebView) is not. This button measures them ON THE PHONE ITSELF: it opens and closes ⚙️, a confirmation and the 📊 page with
#   the chosen motion, counts the frames, and shows a table (the wait before the motion · the longest gap · the stutters) with the phone's
#   facts (cores · memory · screen rate · graphics chip · app or browser) — a screenshot of it says exactly what stutters there.
#   Display only: it opens the dashboard's own windows and closes them · nothing is sent anywhere.
#   python3 devtests/step/patches/p49_motion_check.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''   ${G('🩺 التشخيص', L('🩺','تشخيص','runDiag()')+L('📄','تقرير كامل','openExport()')''',
     '''   ${G('🩺 التشخيص', L('🩺','تشخيص','runDiag()')+L('🎬','فحص سلاسة الحركة','motionCheck()','يقيس الحركة على هذا الجهاز نفسه')+L('📄','تقرير كامل','openExport()')'''),
    ('''function hwIdle(){''',
     '''/* 🎬 v3.36.36: فحص سلاسة الحركة على الجهاز نفسه — يفتح ويسد ⚙️ والتأكيد و📊 بالحركة المختارة ويعدّ الإطارات (عرض فقط · لا يرسل شيئاً) */
async function motionCheck(){const s=hwStyle(),nm=(HW_ANIMS.find(x=>x[0]===uiAnim())||[])[1]||'';
  if(s==='none'){toast(uiLite()?'⚡ الوضع الخفيف مفعّل — لا حركة لقياسها':'📴 الهاتف مضبوط على تقليل الحركة — لا حركة لقياسها',false);return}
  const W=ms=>new Promise(r=>setTimeout(r,ms)),hz=await new Promise(r=>hzProbe(r)),fr=hz>0?1000/hz:16.7;
  for(let i=0;i<8&&holyBack();i++);await W(500);toast('🎬 أقيس الحركة… لا تلمس الشاشة (10 ثوانٍ تقريباً)',true);await W(900);
  const T=[['⚙️ الإعدادات',()=>openSettings(),()=>hideModal()],['تأكيد',()=>askConfirm('🧪 نافذة قياس','لا تضغط شيئاً — تنسدّ وحدها.',()=>{}),()=>hideModal()],
           ['📊 التقارير',()=>openReports(),()=>closePage('reports')]],R=[];
  for(const [w,op,cl] of T)for(const ph of ['فتح','سد']){
    if(ph==='سد'){op();await W(1100)}
    const t0=performance.now();if(ph==='فتح')op();else cl();const c0=performance.now()-t0;
    const pick=()=>ph==='فتح'?((w.includes('التقارير')?document.querySelector('#page_reports .pwrap'):document.getElementById('modal'))||{getAnimations:()=>[]}).getAnimations()[0]
      :document.getAnimations().find(x=>x.effect&&x.effect.target&&x.effect.target.closest&&x.effect.target.closest('.hwclone')&&x.effect.target.matches('.modal,.pwrap'));
    const A=pick(),ts=[];let st=0;
    await new Promise(res=>{(function f(){const n=performance.now(),ps=A?A.playState:'none';
      if(ps==='running'||ps==='finished'){if(!st)st=n;ts.push(n)}
      if(A&&ps!=='finished'&&n-t0<2500)requestAnimationFrame(f);else res()})()});
    const g=ts.slice(1).map((t,i)=>t-ts[i]);
    R.push({w,ph,cost:Math.round(c0),first:st?Math.round(st-t0):-1,max:Math.round(g.length?Math.max(...g):0),bad:g.filter(x=>x>fr*2.2).length,n:g.length});
    if(ph==='فتح')cl();await W(800)}
  const G=gpuInfo(),dm=navigator.deviceMemory,cores=navigator.hardwareConcurrency,where=IN_APP?'📱 التطبيق':IN_WIN?'💻 برنامج ويندوز':'🌐 المتصفح';
  const v=x=>x.first<0?'—':x.bad===0&&x.first<=120?'✅ سلسة':x.bad<=2&&x.first<=250?'🟡 مقبولة':x.bad>2?'🔴 تقطّع':'🐢 بطيئة البداية';
  const row=x=>`<tr><td>${x.w}</td><td>${x.ph}</td><td class="num">${x.first<0?'—':x.first+' ms'}</td><td class="num">${x.max} ms</td><td class="num">${x.bad}</td><td>${v(x)}</td></tr>`;
  const worst=R.reduce((a,x)=>Math.max(a,x.bad),0)+R.filter(x=>x.first>250).length,slow=R.reduce((a,x)=>Math.max(a,x.first),0);
  showModal(`<h2>🎬 فحص سلاسة الحركة</h2>
    <p style="color:var(--mut);font-size:13px;line-height:1.9">الحركة: <b>${nm}</b> · ${where} · الشاشة <b class="num">${hz||'?'} Hz</b> (الإطار ${fr.toFixed(1)} ms) ·
      المعالج <b class="num">${cores||'?'}</b> أنوية${dm?` · الذاكرة <b class="num">${dm} GB</b>`:''} · الرسوميات: ${G.name?SKE(G.name):'غير معروفة'}${G.ok===false?' ⚠️ (الرسم على المعالج)':''}</p>
    <div style="overflow-x:auto"><table class="mtab" style="width:100%;border-collapse:collapse;font-size:13px">
      <tr style="color:var(--mut2)"><th style="text-align:start">النافذة</th><th>المرحلة</th><th>بدأت بعد</th><th>أطول فجوة</th><th>تقطّعات</th><th></th></tr>
      ${R.map(row).join('')}</table></div>
    <p style="color:var(--mut2);font-size:12px;line-height:1.8;margin-top:10px">«بدأت بعد» = من الضغطة حتى أول إطار من الحركة (يشمل بناء النافذة) · «أطول فجوة» بين إطارين أثناء الحركة ·
      «تقطّعات» = إطارات تأخرت أكثر من ضعف إطار الشاشة أثناء الحركة. ${worst?'صوّر هذه النافذة وأرسلها لنعرف أين التقطّع بالضبط.':'الحركة سلسة على هذا الجهاز.'}
      ${slow>250?' البداية بطيئة: بناء النافذة نفسها يأخذ وقتاً على هذا الجهاز.':''}</p>
    <div class="mbtns"><button onclick="motionCheck()">🔁 أعد القياس</button><button onclick="hideModal()">إغلاق</button></div>`);
  try{const tb=document.querySelector('#modal .mtab');tb.querySelectorAll('td,th').forEach(c=>{c.style.padding='6px 4px';c.style.borderBottom='1px solid var(--line)'})}catch(e){}}
function hwIdle(){'''),
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
