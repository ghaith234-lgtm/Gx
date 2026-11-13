# 🃏 patch 58 (dashboard · the cards' motions) — the owner (13-11): «انميشن الكرت اريده وخليه داخل وخلي في امثلة تتحرك حتى واحد يعرف ماذا يختار».
#   The five groups from the examples page — each a choice in ⚙️ 🖌️ «🃏 حركات البطاقات» (this device):
#     ⋯ the menu (skins C · B · OKX): تكبير من الزر · انزلاق · تكبير + الأزرار بالتتابع · بلا
#     ⌄ opening a section: انفتاح ناعم · انزلاق مع تلاشٍ · بلا
#     💰 the profit number on a winning trade: عدّ تصاعدي · وميض أخضر · عدّ + وميض · نبضة للبطاقة · بلا
#     📊 the ladder bars when a card shows: امتلاء · امتلاء متتابع · بلا
#     🃏 the cards when the dashboard opens (and a new bot's card): صعود خفيف · واحدة بعد واحدة · تكبير ناعم · بلا
#   Inside the row: a small sample card that moves — every choice plays on it the moment it is tapped (+ «شغّل الكل»).
#   «⚡ الوضع الخفيف» or the device's «تقليل الحركة» (without «شغّل الحركة رغم إعداد الجهاز») ⇒ the cards do not move (the sample still
#   plays when tapped). transform/opacity only, except a section opening (its height · one section · a quarter second).
#   The number moves only when it goes UP (a winning trade · the accumulated coin) — at most once every 1.5 s per card.
#   python3 devtests/step/patches/p58_card_motion.py Holy_Dashboard.pyw
import os, sys

CA_JS = r'''/* 🃏 v3.36.39 (المالك 13-11: «انميشن الكرت اريده وخليه داخل وخلي في امثلة تتحرك حتى واحد يعرف ماذا يختار»): حركات البطاقات — خمس مجموعات ·
   لهذا الجهاز · ⚙️ 🖌️ «🃏 حركات البطاقات»: بطاقة تجريبية صغيرة — أي خيار ينضغط يتحرك عليها فوراً ·
   «⚡ الوضع الخفيف» أو «تقليل الحركة» بالجهاز (بلا «شغّل الحركة رغم إعداد الجهاز») ⇒ البطاقات بلا حركة (التجربة بـ⚙️ تتحرك عند الضغط بس) ·
   كلها transform/opacity (كرت الشاشة) إلا انفتاح القسم (ارتفاعه — قسم واحد ربع ثانية) · الرقم يتحرك بس لما يصعد (صفقة رابحة) */
const CA_EZ='cubic-bezier(.2,.8,.2,1)';
const HCA={
  menu:['⋯ القائمة (أشكال C · B · OKX)','pop',[['pop','تكبير من الزر','تكبر من مكان «⋯» نفسه — مثل قوائم الهاتف'],['drop','انزلاق','تنزلق من جهة الزر وتظهر تدريجياً'],
    ['stag','تكبير + الأزرار بالتتابع','القائمة تكبر ثم تظهر أزرارها واحداً بعد واحد'],['none','بلا حركة','تظهر مباشرة']]],
  sec:['⌄ فتح الأقسام (السلم · التفاصيل)','grow',[['grow','انفتاح ناعم','القسم يطول بنعومة'],['fade','انزلاق مع تلاشٍ','ينزل القسم قليلاً ويظهر'],['none','بلا حركة','يظهر مباشرة']]],
  num:['💰 رقم الربح عند صفقة رابحة','both',[['count','عدّ تصاعدي','الرقم يعدّ من القيمة القديمة إلى الجديدة'],['flash','وميض أخضر','الرقم يومض أخضر لحظة ثم يرجع'],
    ['both','عدّ + وميض','الاثنان معاً'],['pulse','نبضة للبطاقة','البطاقة كلها تنبض نبضة خفيفة مع الرقم الجديد'],['none','بلا حركة','يتبدّل الرقم مباشرة']]],
  bars:['📊 أشرطة السلم','fill',[['fill','امتلاء','كل شريط يمتلئ من بدايته حين تظهر البطاقة'],['wave','امتلاء متتابع','الأشرطة تمتلئ واحداً بعد واحد'],['none','بلا حركة','تظهر مباشرة']]],
  enter:['🃏 ظهور البطاقات عند فتح اللوحة','rise',[['rise','صعود خفيف','تصعد قليلاً وتظهر معاً'],['stagger','واحدة بعد واحدة','تظهر بتتابع سريع'],
    ['zoom','تكبير ناعم','تكبر من حجم أصغر قليلاً'],['none','بلا حركة','تظهر مباشرة']]]};
function uiCa(g){const G=HCA[g],v=_ls('dash_ca_'+g);return G[2].some(x=>x[0]===v)?v:G[1]}
function caOff(){try{return uiLite()||(hwDevRm()&&!hwForce())}catch(e){return true}}
function caOn(g){return !caOff()&&uiCa(g)!=='none'}
function caG(){return getComputedStyle(document.documentElement).getPropertyValue('--green-rgb').trim()||'52 211 153'}
const CA={
  menu(m,k){if(!m||k==='none'||typeof m.animate!=='function')return;m.style.transformOrigin='bottom '+(getComputedStyle(m).direction==='rtl'?'left':'right');
    if(k==='drop'){m.animate([{opacity:0,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:200,easing:CA_EZ});return}
    m.animate([{opacity:0,transform:k==='stag'?'scale(.6)':'scale(.4)'},{opacity:1,transform:'none'}],{duration:k==='stag'?180:220,easing:k==='stag'?CA_EZ:'cubic-bezier(.34,1.4,.64,1)'});
    if(k==='stag')[...m.children].forEach((b,i)=>b.animate([{opacity:0,transform:'translateX(10px)'},{opacity:1,transform:'none'}],{duration:180,delay:60+i*35,easing:CA_EZ,fill:'backwards'}))},
  sec(n,k){if(!n||k==='none'||typeof n.animate!=='function')return;
    if(k==='fade'){n.animate([{opacity:0,transform:'translateY(-10px)'},{opacity:1,transform:'none'}],{duration:220,easing:CA_EZ});return}
    const h=n.scrollHeight;if(!h)return;const ov=n.style.overflow;n.style.overflow='hidden';
    const a=n.animate([{height:'0px',opacity:.2},{height:h+'px',opacity:1}],{duration:260,easing:CA_EZ});a.onfinish=a.oncancel=()=>{n.style.overflow=ov}},
  bars(c,k,dl){if(!c||k==='none')return;c.querySelectorAll('rect.skb,.mrow .ln,.cfx-bars i').forEach((i,j)=>{if(typeof i.animate==='function')
    i.animate([{transform:'scaleX(0)'},{transform:'none'}],{duration:k==='wave'?420:500,delay:(dl||0)+(k==='wave'?j*70:0),easing:CA_EZ,fill:'backwards'})})},
  enter(L,k,dl){if(k==='none')return;(L||[]).forEach((x,j)=>{if(typeof x.animate==='function')x.animate(k==='zoom'?[{opacity:0,transform:'scale(.94)'},{opacity:1,transform:'none'}]
    :[{opacity:0,transform:k==='stagger'?'translateY(14px) scale(.98)':'translateY(14px)'},{opacity:1,transform:'none'}],{duration:k==='zoom'?280:320,delay:(dl||0)+(k==='stagger'?j*40:0),easing:CA_EZ,fill:'backwards'})})}};
function caCount(n,a,b){const t=n&&n.firstChild;if(!t||t.nodeType!==3||!isFinite(a)||!isFinite(b))return;   // الرقم بس يعدّ — اللي قبله وبعده (الوحدة) يبقى
  const end=t.nodeValue,m=end.match(/^(\D*?)(-?[\d,]*\.?\d+)([\s\S]*)$/);if(!m)return;const dp=(m[2].split('.')[1]||'').length,t0=performance.now(),put=x=>{t.nodeValue=m[1]+x.toFixed(dp)+m[3]};
  const f=now=>{if(!t.isConnected)return;const k=Math.min(1,(now-t0)/600),e=1-Math.pow(1-k,3);if(k<1){put(a+(b-a)*e);requestAnimationFrame(f)}else t.nodeValue=end};
  put(a);requestAnimationFrame(f)}
function caFlash(n){if(!n||typeof n.animate!=='function')return;const c=getComputedStyle(n).color,g=caG();
  n.animate([{color:c,textShadow:'0 0 0 transparent'},{color:`rgb(${g})`,textShadow:`0 0 16px rgb(${g}/.6)`},{color:c,textShadow:'0 0 0 transparent'}],{duration:900,easing:'ease-out'})}
function caPulse(el){if(!el||typeof el.animate!=='function')return;const s=getComputedStyle(el).boxShadow,b=s&&s!=='none'?s:'0 0 0 0 transparent',g=caG();
  el.animate([{transform:'none',boxShadow:b},{transform:'scale(1.02)',boxShadow:`0 0 0 2px rgb(${g}/.6),0 14px 34px rgb(${g}/.18)`},{transform:'none',boxShadow:b}],{duration:700,easing:CA_EZ})}
/* الرقم الكبير بالبطاقة صعد (صفقة رابحة · العملة المتجمّعة) ⇒ حركته — الشكل القديم: الربح يعدّ أصلاً (نابض) ⇒ وميض / نبضة بس */
function caNumChk(el,b){try{const sk=uiSkin(),M=el._skM;let v,txt='',n;
  if(sk!=='old'&&M){txt=String(M.big||'');v=parseFloat(txt.replace(/,/g,''));n=el.querySelector('.sk-big .v,.sk-kpi>div:first-child>b,.ok-pnl .v')}else{v=+b.profit;n=el._r&&el._r.profit}
  const p=el._caV,ps=el._caS;el._caV=v;el._caS=sk;
  if(p===undefined||ps!==sk||!isFinite(v)||!isFinite(p)||v<=p+1e-9||!caOn('num')||el.style.display==='none')return;
  const now=performance.now();if(now-(el._caT||0)<1500)return;el._caT=now;const k=uiCa('num');
  if(k==='pulse'){caPulse(el);return}
  if(sk!=='old'&&(k==='count'||k==='both'))caCount(n,p,v);
  if(k==='flash'||k==='both')caFlash(n)}catch(e){}}
/* أول رسم للبطاقات ⇒ ظهورها (اللي بالشاشة · بعد شاشة البداية) · بطاقة بوت جديد ⇒ ظهورها · كل بطاقة أول ما تبان ⇒ أشرطة السلم */
const CAS={first:0,io:null,seen:new WeakSet(),mt:0};
function caSplash(){return document.getElementById('splash')?Math.max(0,2450-performance.now()):0}
function caAfterSync(){const els=[...CARDS.values()].filter(e=>e.style.display!=='none');
  if(!CAS.first){CAS.first=1;els.forEach(e=>e._caNew=0);
    if(caOn('enter')){const vis=els.filter(e=>{const r=e.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight});CA.enter(vis,uiCa('enter'),caSplash())}}
  else{const nw=els.filter(e=>e._caNew);nw.forEach(e=>e._caNew=0);if(nw.length&&caOn('enter'))CA.enter(nw,uiCa('enter'),0)}
  if(!caOn('bars')||!window.IntersectionObserver)return;
  if(!CAS.io)CAS.io=new IntersectionObserver(es=>es.forEach(x=>{if(!x.isIntersecting)return;CAS.io.unobserve(x.target);try{if(caOn('bars'))CA.bars(x.target,uiCa('bars'),caSplash())}catch(e){}}),{threshold:.2});
  els.forEach(e=>{if(!CAS.seen.has(e)){CAS.seen.add(e);CAS.io.observe(e)}})}
/* ⚙️ البطاقة التجريبية */
function caVal(){if(caOff())return uiLite()?'متوقفة (الوضع الخفيف)':'متوقفة (إعداد الجهاز)';const n=Object.keys(HCA).filter(g=>uiCa(g)!=='none').length;return n?`${n} من 5 تعمل`:'بلا حركة'}
function cfxBody(){const rows=[['🟢 بيع','0.5321','120'],['⚡ السعر','0.5208',''],['🔵 شراء','0.5150','120']].map(r=>`<div><span>${r[0]}</span><span class="num">${r[1]}</span><span class="num">${r[2]}</span></div>`).join('');
  const minis=[['♾️ XRP','+1.24$'],['🪜 SUI','+0.49$'],['📉 DOGE','+0.12$']].map(x=>`<div><span>${x[0]}</span><b class="num">${x[1]}</b></div>`).join('');
  return `<div class="snote">اضغط أي خيار فيتحرك على البطاقة التجريبية فوراً · يُحفظ لهذا الجهاز.${caOff()?` <b style="color:var(--amber)">الحركة متوقفة الآن على البطاقات (${uiLite()?'الوضع الخفيف':'إعداد الجهاز — ⚙️ «حركة فتح النوافذ»'}) — التجربة هنا فقط.</b>`:''}</div>
  <div class="cfx-demo"><div class="cfx-card" id="cfxCard"><div class="cfx-hd"><b>♾️ XRP</b><span>نشط</span></div>
    <div class="cfx-big"><span class="v num" id="cfxV">28.1278</span><small>$</small></div>
    <div class="cfx-bars"><i style="width:88%"></i><i style="width:56%"></i><i style="width:72%"></i><i style="width:38%"></i></div>
    <button type="button" class="cfx-sh" onclick="cfxRun('sec')"><span>🪜 السلم</span><span class="cv">⌄</span></button><div class="cfx-sb" hidden>${rows}</div>
    <div class="cfx-ft"><button type="button" class="cfx-go" onclick="cfxRun('num')">➕ صفقة رابحة (تجربة)</button><button type="button" class="cfx-more" aria-label="القائمة" onclick="cfxRun('menu')">⋯</button></div></div>
   <div class="cfx-minis" id="cfxMinis">${minis}</div></div>
  ${Object.keys(HCA).map(g=>`<div class="cfx-g" data-g="${g}"><div class="cfx-gt">${HCA[g][0]}</div><div class="pollrow">${HCA[g][2].map(x=>`<button type="button" class="${uiCa(g)===x[0]?'on':''}" data-ca="${x[0]}" onclick="setCa('${g}','${x[0]}')">${x[1]}</button>`).join('')}</div><div class="cfx-d">${(HCA[g][2].find(x=>x[0]===uiCa(g))||[])[2]||''}</div></div>`).join('')}
  <div class="pollrow" style="margin-top:12px"><button type="button" id="cfxAllB" onclick="cfxAll()">▶️ شغّل الكل على البطاقة التجريبية</button></div>`}
function setCa(g,k){const G=HCA[g];if(!G||!G[2].some(x=>x[0]===k))return;_ls('dash_ca_'+g,k===G[1]?null:k);
  const box=document.querySelector('#modal .cfx-g[data-g="'+g+'"]');
  if(box){box.querySelectorAll('button[data-ca]').forEach(b=>b.classList.toggle('on',b.dataset.ca===k));const d=box.querySelector('.cfx-d');if(d)d.textContent=(G[2].find(x=>x[0]===k)||[])[2]||''}
  const v=document.querySelector('#modal .sx[data-k="cfx"] .sval');if(v)v.textContent=caVal();
  cfxRun(g,1)}
function cfxRun(g,again){const c=document.getElementById('cfxCard');if(!c)return;const k=uiCa(g);
  if(g==='menu'){let m=c.querySelector('.cfx-menu');if(m){m.remove();clearTimeout(CAS.mt);if(!again)return}
    m=document.createElement('div');m.className='cfx-menu';m.setAttribute('role','menu');
    m.innerHTML=['⏸️ إيقاف الشراء','⏸️ إيقاف البيع','⚙️ تفاصيل البوت','📜 السجل'].map(t=>`<button type="button" tabindex="-1">${t}</button>`).join('');
    c.appendChild(m);CA.menu(m,k);clearTimeout(CAS.mt);CAS.mt=setTimeout(()=>{try{m.remove()}catch(e){}},2600)}
  if(g==='sec'){const b=c.querySelector('.cfx-sb'),h=c.querySelector('.cfx-sh .cv');if(!b.hidden){b.hidden=true;h.textContent='⌄';if(!again)return}
    b.hidden=false;h.textContent='⌃';CA.sec(b,k)}
  if(g==='num'){const n=document.getElementById('cfxV'),a=+n.firstChild.nodeValue||0,v=+(a+0.0613).toFixed(4),t=v.toFixed(4);
    n.firstChild.nodeValue=t;if(k==='count'||k==='both')caCount(n,a,v);if(k==='flash'||k==='both')caFlash(n);if(k==='pulse')caPulse(c)}
  if(g==='bars')CA.bars(c,k,0);
  if(g==='enter')CA.enter([...document.querySelectorAll('#cfxMinis>div')],k,0)}
function cfxAll(){cfxRun('enter');cfxRun('bars');setTimeout(()=>cfxRun('num'),450);setTimeout(()=>cfxRun('sec',1),1150);setTimeout(()=>cfxRun('menu',1),1850)}
function skinUpd(el,b){'''

CA_CSS = '''.skx [data-skx]{display:none}.skx [data-skx].on{display:block}
/* 🃏 v3.36.39 حركات البطاقات: أشرطة السلم تمتلئ من طرفها · البطاقة التجريبية بـ⚙️ */
.sk-gfx rect.skb{transform-box:fill-box;transform-origin:100% 50%}
.cfx-demo{display:grid;gap:10px;margin:8px 0 4px}
.cfx-card{position:relative;border:1px solid var(--line);border-radius:14px;padding:10px 12px;background:rgb(var(--ov-rgb)/.04)}
.cfx-hd{display:flex;justify-content:space-between;align-items:center;font-size:13px}.cfx-hd span{font-size:11px;color:var(--green)}
.cfx-big{margin:6px 0 8px;font-size:22px;font-weight:600;line-height:1.2}.cfx-big small{font-size:12px;color:var(--mut);margin-inline-start:3px;font-weight:500}
.cfx-bars{display:grid;gap:5px;margin-bottom:9px}.cfx-bars i{display:block;height:6px;border-radius:3px;background:rgb(var(--green-rgb)/.7);transform-origin:100% 50%}
.cfx-bars i:nth-child(n+3){background:rgb(var(--cyan-rgb)/.7)}
.cfx-sh{width:100%;display:flex;justify-content:space-between;align-items:center;background:rgb(var(--ov-rgb)/.04);border:1px solid var(--line);border-radius:10px;padding:7px 10px;color:var(--tx);font:inherit;font-size:12px;cursor:pointer}
.cfx-sb{margin-top:6px;display:grid;gap:3px;font-size:11.5px;color:var(--mut)}.cfx-sb[hidden]{display:none}.cfx-sb>div{display:grid;grid-template-columns:1fr auto 44px;gap:8px;padding:3px 6px;border-radius:7px;background:rgb(var(--ov-rgb)/.04)}
.cfx-ft{display:flex;gap:6px;margin-top:9px}
.cfx-go,.cfx-more{border:1px solid var(--line);border-radius:10px;background:rgb(var(--vio-rgb)/.12);color:var(--tx);font:inherit;font-size:12px;padding:7px 10px;cursor:pointer}
.cfx-go{flex:1}.cfx-more{width:42px;font-weight:700}
.cfx-menu{position:absolute;inset-inline-end:10px;bottom:48px;z-index:3;width:min(200px,80%);display:grid;gap:2px;background:var(--bg1);border:1px solid var(--line);border-radius:12px;padding:5px;box-shadow:0 14px 30px rgb(0 0 0/.4)}
.cfx-menu button{background:none;border:0;color:var(--tx);font:inherit;font-size:12px;text-align:start;padding:7px 8px;border-radius:8px}
.cfx-minis{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.cfx-minis>div{display:flex;flex-direction:column;gap:2px;border:1px solid var(--line);border-radius:10px;padding:6px 8px;font-size:11px;background:rgb(var(--ov-rgb)/.04)}.cfx-minis b{color:var(--green)}
.cfx-g{margin-top:12px}.cfx-gt{font-size:12px;font-weight:600;margin-bottom:5px}.cfx-d{font-size:10.5px;color:var(--mut2);margin-top:4px}'''

R = [
    ('''.skx [data-skx]{display:none}.skx [data-skx].on{display:block}''', CA_CSS),
    ('''function skinUpd(el,b){''', CA_JS),
    ('''if(w&&n.classList.contains('rclots'))rcFit3(n)''',
     '''if(w&&n.classList.contains('rclots'))rcFit3(n);if(w&&el._caOk&&caOn('sec'))CA.sec(n,uiCa('sec'))'''),
    ('''  skinLockPaint(el,uiCardLock(),uiCardLock()&&cardLocked(el))}''',
     '''  el._caOk=1;skinLockPaint(el,uiCardLock(),uiCardLock()&&cardLocked(el))}'''),
    ('''  if(k==='menu'){el._skm=el._skm?0:1;el._skv._h='';skinUpd(el);return}''',
     '''  if(k==='menu'){el._skm=el._skm?0:1;el._skv._h='';skinUpd(el);if(el._skm&&caOn('menu'))CA.menu(el.querySelector('.sk-menu'),uiCa('menu'));return}'''),
    ('''    if(!el){el=buildCard(b,0);CARDS.set(b.dir,el);cardLockDeco(el)}''',
     '''    if(!el){el=buildCard(b,0);CARDS.set(b.dir,el);cardLockDeco(el);el._caNew=1}'''),
    ('''    updCard(el,b,bench);skinUpd(el,b)});''',
     '''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b)});'''),
    ('''  // العدّاد''',
     '''  try{caAfterSync()}catch(e){}                     // 🃏 v3.36.39: ظهور البطاقات · أشرطة السلم
  // العدّاد'''),
    ('''  box.style.display='';
}
function updDcaCard(el,b){''',
     '''  box.style.display='';if(caOn('sec'))CA.sec(box,uiCa('sec'));
}
function updDcaCard(el,b){'''),
    ('''      <rect x="${x1-L}" y="${cy-3}" width="${Math.max(2,L)}" height="6" rx="3" fill="rgb(${c}/.75)"/>''',
     '''      <rect class="skb" x="${x1-L}" y="${cy-3}" width="${Math.max(2,L)}" height="6" rx="3" fill="rgb(${c}/.75)"/>'''),
    ('''  if(on&&k==='bg')try{hbPrev()}catch(e){}}''',
     '''  if(on&&k==='bg')try{hbPrev()}catch(e){}
  if(on&&k==='cfx')setTimeout(()=>{try{cfxRun('enter');cfxRun('bars')}catch(e){}},280)}'''),
    ('''     +X('anim','🎬','حركة فتح النوافذ',anN,`${rmN}<div class="snote">الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة.</div><div class="pollrow" id="animRow">${AB}</div>`)''',
     '''     +X('anim','🎬','حركة فتح النوافذ',anN,`${rmN}<div class="snote">الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة.</div><div class="pollrow" id="animRow">${AB}</div>`)
     +X('cfx','🃏','حركات البطاقات',caVal(),cfxBody())'''),
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
