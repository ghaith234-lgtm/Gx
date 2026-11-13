# 🪟 patch 42 (dashboard · every window) — the owner (13-11): «الواجهات كل واحد صايرة تصميمها يختلف عن الاخر اريد الكل تتوحد واتصير فل
#   سكرين مثل الاختبار التجريبي ومكان الx · اريد زر الموبايل عند ضغط رجوع يرجع» ⇒ (after the motion samples) «اريدهم كلهم واتضيفهم
#   للاعدادات · دخول سطر بعد سطر لا اريده · اهم شي عند اضافة تصميم جديد في المستقبل يصير نفس النمط · سويهم حتى لو وجبه وجبه اهم شي ما
#   في اخطاء · النوافذ متاكد تحذف بقيها بس غير شكلها للنمط الجديد واي شي مشابه الها بس غير شكلة بس حجمه بقيه».
#   ① ONE window frame for every window: full screen on a phone · on a computer a large panel like «🧪 الاختبار التجريبي» (22 px around ·
#      up to 1180 px) · the title as a header that stays on top · ✕ always in the same corner (where the trial window has it) · the lone
#      «إغلاق» buttons gone (✕ does it) — the 77 windows of showModal · the 4 pages (reports · logs · flow · wallets) · the bot details ·
#      the trial window · the notifications
#   ② confirmations and their kind (25: «متأكد؟» · buy/sell now · the small forms) keep their size, in the new look (showDialog)
#   ③ ⚙️ «🎬 حركة فتح النوافذ»: بلا حركة · انزلاق من الأسفل · تكبير ناعم (default) · انزلاق جانبي · تتوسّع من الزر · تلاشٍ مع ضبابية ·
#      ارتداد خفيف — closing plays it backwards · «⚡ الوضع الخفيف» and the phone's «reduce motion» = no motion · the window counts as closed
#      at once (a copy plays the closing), so nothing waits for it
#   ④ the back button closes the TOP thing first: a menu «⋯» / a line's popover · a dialog · a window · a page · the details · the trial ·
#      the notifications — in the app (holyBack) and in a phone browser (history) · Esc the same · a window opened over another is
#      always drawn above it
#   ⑤ the future: a new window made with showModal (full) or showDialog (small) gets all of it by itself · pages / details / trial /
#      notifications opened by any code are tracked by watching them (not by who opened them) · devtests/t_windows.py fails on a new
#      full-screen overlay made outside this frame
#   python3 devtests/step/patches/p42_windows.py Holy_Dashboard.pyw
import os, re, sys

SMALL = ["accumPrompt", "resumeConfirm", "recSell", "recWithdraw", "recRi", "recNow", "recRange", "vaDelete", "vaHgRi", "dcaLast",
         "dcaShield", "dcaBuyNow", "riSetPct", "riInject", "riWithdraw", "pfEnv", "pfSpend", "pfAssign", "testWallet", "updWallet",
         "testTg", "askConfirm", "accBuyNow", "accSell", "accToFinal"]

JS = r'''/* 🪟 v3.36.34 (المالك 13-11): نمط واحد لكل النوافذ — كاملة الشاشة (بالحاسوب لوحة كبيرة مثل «الاختبار التجريبي») · ✕ بنفس الزاوية ·
   التأكيدات وشبهها بحجمها بالشكل الجديد (showDialog) · حركة الفتح من ⚙️ والإغلاق بعكسها · زر الرجوع يسكّر الأعلى أولاً (بالتطبيق وبالمتصفح) ·
   نافذة جديدة بـshowModal / showDialog تاخذ كل هذا وحدها */
const HW_ANIMS=[['none','بلا حركة'],['up','انزلاق من الأسفل'],['zoom','تكبير ناعم'],['side','انزلاق جانبي'],['btn','تتوسّع من الزر'],['blur','تلاشٍ مع ضبابية'],['spring','ارتداد خفيف']];
const HW_MS={up:320,zoom:260,side:300,btn:420,blur:300,spring:440};
const HW={st:[],pt:null,skip:0,popping:0};
function uiAnim(){const v=_ls('dash_anim');return HW_ANIMS.some(x=>x[0]===v)?v:'zoom'}
function setAnim(v){if(!HW_ANIMS.some(x=>x[0]===v))v='zoom';_ls('dash_anim',v==='zoom'?null:v);const n=(HW_ANIMS.find(x=>x[0]===v)||[])[1]||'';
  hideModal();setTimeout(()=>{openSettings();toast('🎬 حركة النوافذ: '+n,true)},v==='none'?0:Math.round((HW_MS[v]||0)*.75)+80)}   // تنفتح من جديد ⇒ تشوف الحركة
function hwStyle(){try{if(document.documentElement.classList.contains('lite'))return 'none';
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return 'none'}catch(e){}return uiAnim()}
document.addEventListener('pointerdown',e=>{HW.pt={x:e.clientX,y:e.clientY,t:Date.now()}},true);
function hwKF(s,el,small,pt){
  if(s==='up')return [{transform:'translateY('+(small?Math.round(innerHeight*.4)+'px':'100%')+')'},{transform:'none'}];
  if(s==='zoom')return [{opacity:0,transform:'scale(.92)'},{opacity:1,transform:'none'}];
  if(s==='side')return [{opacity:small?0:1,transform:'translateX('+(small?'-40vw':'-100%')+')'},{opacity:1,transform:'none'}];
  if(s==='blur')return [{opacity:0,filter:'blur(14px)',transform:'scale(1.04)'},{opacity:1,filter:'blur(0px)',transform:'none'}];
  if(s==='spring')return [{opacity:0,transform:'translateY(48px) scale(.96)'},{opacity:1,transform:'none'}];
  if(s==='btn'){const r=el.getBoundingClientRect(),p=pt||{x:innerWidth/2,y:innerHeight/2},cx=Math.round(p.x-r.left),cy=Math.round(p.y-r.top),
    R=Math.ceil(Math.hypot(Math.max(Math.abs(cx),Math.abs(r.width-cx)),Math.max(Math.abs(cy),Math.abs(r.height-cy))))+2;
    return [{clipPath:`circle(0px at ${cx}px ${cy}px)`},{clipPath:`circle(${R}px at ${cx}px ${cy}px)`}]}
  return null}
function hwPt(){return HW.pt&&Date.now()-HW.pt.t<5000?HW.pt:null}
function hwIn(panel,scrim,small,pt){const s=hwStyle();if(s==='none'||!panel||!panel.animate)return;
  try{const kf=hwKF(s,panel,small,pt||hwPt());if(!kf)return;
    panel.animate(kf,{duration:HW_MS[s],easing:s==='spring'?'cubic-bezier(.34,1.56,.64,1)':'cubic-bezier(.2,.8,.2,1)'});
    if(scrim&&scrim!==panel){const bc=getComputedStyle(scrim).backgroundColor;
      scrim.animate([{backgroundColor:'rgba(0,0,0,0)'},{backgroundColor:bc}],{duration:Math.round(HW_MS[s]*.8),easing:'linear'})}}catch(e){}}
function hwOut(box,panelSel,small,pt){                 // النافذة تنسدّ فوراً (الكود يشوفها مسدودة) · نسخة منها تلعب الإغلاق
  const s=hwStyle();if(s==='none'||!box||!box.animate||!box.isConnected)return;
  try{const r=box.getBoundingClientRect();if(!r.width||!r.height)return;
    const z=getComputedStyle(box).zIndex,c=box.cloneNode(true);
    c.removeAttribute('id');c.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));
    c.querySelectorAll('[data-dir],[data-acc]').forEach(n=>{n.removeAttribute('data-dir');n.removeAttribute('data-acc')});
    c.setAttribute('aria-hidden','true');c.setAttribute('inert','');c.classList.add('hwclone');c.classList.add('on');c.hidden=false;
    Object.assign(c.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',right:'auto',bottom:'auto',
      margin:'0',zIndex:String(+z||150),pointerEvents:'none',transition:'none',animation:'none',transform:'none',opacity:'1',visibility:'visible'});
    document.body.appendChild(c);
    const sc=[[box,c]].concat(['.hwb','.pwrap','.dbody','.npbody'].map(q=>[box.querySelector(q),c.querySelector(q)]));
    sc.forEach(([a,b])=>{if(a&&b&&a.scrollTop)b.scrollTop=a.scrollTop});
    const p=(panelSel&&c.querySelector(panelSel))||c,kf=hwKF(s,p,small,pt||hwPt()),d=Math.round(HW_MS[s]*.75);
    if(kf)p.animate(kf.slice().reverse(),{duration:d,easing:'cubic-bezier(.4,0,.7,.2)',fill:'forwards'});
    if(p!==c)c.animate([{opacity:1},{opacity:0}],{duration:d,easing:'linear',fill:'forwards'});
    setTimeout(()=>{try{c.remove()}catch(e){}},d+80)}catch(e){}}
/* الطبقات: كل وحدة تنعرف من حالتها (مو من اللي فتحها) ⇒ أي كود يفتحها تاخذ الحركة والترتيب وزر الرجوع */
function hwLayers(){const L=[],mb=$('#mbg');
  if(mb)L.push({k:'modal',el:mb,panel:$('#modal'),scrim:mb,on:!mb.hidden,small:mb.classList.contains('small'),close:hideModal});
  const bt=$('#btov');L.push({k:'bt',el:bt,panel:bt&&bt.querySelector('.btbox'),scrim:bt,on:!!bt,close:btClose});
  document.querySelectorAll('.page[id]').forEach(p=>L.push({k:p.id,el:p,panel:p.querySelector('.pwrap')||p,on:p.classList.contains('on'),
    close:()=>{const b=p.querySelector('.phead .x')||p.querySelector('button[onclick*="close"]');b?b.click():p.classList.remove('on')}}));
  const dr=$('#drawer');if(dr)L.push({k:'drawer',el:dr,panel:dr,on:dr.classList.contains('on'),close:closeDrawer});
  const np=$('#notifPanel');if(np)L.push({k:'np',el:np,panel:np,on:np.classList.contains('on'),close:()=>{if(npOpen)toggleNotif()}});
  return L}
function hwPush(x){const top=HW.st[HW.st.length-1];
  if(top&&x.el&&top.el&&top.el.isConnected){x.el.style.zIndex='';const base=+getComputedStyle(x.el).zIndex||0,tz=+getComputedStyle(top.el).zIndex||0;
    if(tz>=base)x.el.style.zIndex=String(tz+3)}                        // المفتوحة فوق غيرها تنرسم فوقها دائماً
  const it={k:x.k,el:x.el,close:x.close,pt:hwPt(),h:0};HW.st.push(it);
  if(!IN_APP){try{history.pushState({hw:x.k,n:HW.st.length},'');it.h=1}catch(e){}}   // 📱 رجوع المتصفح يسكّرها (التطبيق: holyBack)
  hwIn(x.panel,x.scrim,x.small,it.pt)}
function hwPop(k){const i=HW.st.findIndex(s=>s.k===k);if(i<0)return;const it=HW.st.splice(i,1)[0];
  if(it.el&&it.el.style)it.el.style.zIndex='';
  if(it.h&&!HW.popping){HW.skip++;try{history.back()}catch(e){HW.skip--}}}
function hwSync(){for(const x of hwLayers()){const i=HW.st.findIndex(s=>s.k===x.k);if(x.on&&i<0)hwPush(x);else if(!x.on&&i>=0)hwPop(x.k)}}
window.addEventListener('popstate',()=>{if(HW.skip>0){HW.skip--;return}const t=HW.st[HW.st.length-1];if(!t)return;
  t.h=0;HW.popping=1;try{t.close()}catch(e){}HW.popping=0;hwSync()});
function hwWatch(){if(HW.mo)return;HW.mo=new MutationObserver(()=>hwSync());
  ['#mbg','#drawer','#notifPanel'].forEach(q=>{const e=$(q);if(e)HW.mo.observe(e,{attributes:true,attributeFilter:['hidden','class']})});
  document.querySelectorAll('.page[id]').forEach(e=>HW.mo.observe(e,{attributes:true,attributeFilter:['class']}));
  HW.mo.observe(document.body,{childList:true});hwSync()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',hwWatch);else setTimeout(hwWatch,0);
function hwDress(m,small){                                           // ✕ بالزاوية · أزرار «إغلاق» وحدها تنشال (✕ يسويها)
  m.querySelectorAll('.hwb .mbtns button').forEach(b=>{if((b.getAttribute('onclick')||'').replace(/\s/g,'')==='hideModal()'&&/^(إغلاق|رجوع|✕)$/.test((b.textContent||'').trim()))b.hidden=true});
  m.querySelectorAll('.hwb .mbtns').forEach(x=>{if(![...x.children].some(c=>!c.hidden&&c.style.display!=='none'))x.hidden=true})}
function showModal(html,o){const m=$('#modal'),bg=$('#mbg'),small=!!(o&&o.small),was=!bg.hidden,wasSmall=bg.classList.contains('small');
  m.innerHTML=`<button type="button" class="hwx" aria-label="إغلاق" title="إغلاق" onclick="hideModal()">✕</button><div class="hwb">${html}</div>`;
  hwDress(m,small);bg.classList.toggle('small',small);bg.classList.toggle('full',!small);bg.hidden=false;hwSync();   // الترتيب يتسجّل فوراً (المراقب احتياط لأي طريق ثاني)
  if(was&&wasSmall!==small)hwIn(m,null,small)}                       // تأكيد فوق نافذة (أو العكس) ⇒ الجديدة تدخل بحركتها
function showDialog(html){showModal(html,{small:true})}             // 🪟 التأكيدات وشبهها: حجمها نفسه بالشكل الجديد
function hideModal(){const bg=$('#mbg');if(bg&&!bg.hidden){const it=HW.st.find(s=>s.k==='modal');hwOut(bg,'.modal',bg.classList.contains('small'),it&&it.pt)}if(bg)bg.hidden=true;hwSync()}
'''

CSS = r'''
/* ═══ 🪟 v3.36.34: نمط النوافذ الموحّد — كاملة الشاشة (بالحاسوب لوحة كبيرة مثل «الاختبار التجريبي») · ✕ بنفس الزاوية · التأكيدات بحجمها ═══ */
:root{--hw-gap:22px;--hw-max:1180px;--hw-r:22px}
.hwx,.phead .x,.dhead .x,.npx,.btx{width:36px;height:36px;min-width:36px;padding:0;border-radius:50%;display:grid;place-items:center;font-size:15px;line-height:1;
  border:1px solid var(--line2);background:rgb(var(--surf-rgb)/.92);color:var(--tx)}
.hwx{position:absolute;top:12px;inset-inline-end:12px;z-index:6;margin:0}
.mbg .modal{position:relative;display:flex;flex-direction:column;overflow:hidden;animation:none}
.mbg .hwb{flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain}
.mbg .hwb>h2:first-child{padding-inline-end:48px}
/* الكاملة */
.mbg.full{padding:var(--hw-gap);place-items:stretch}
.mbg.full .modal{width:min(var(--hw-max),100%);max-width:none;height:100%;max-height:none;margin:0 auto;padding:0;border-radius:var(--hw-r);border:1px solid var(--line2)}
.mbg.full .hwb{padding:0 22px 26px}
.mbg.full .hwb>h2:first-child{position:sticky;top:0;z-index:4;margin:0 -22px 16px;padding:15px 22px 13px;padding-inline-end:62px;background:var(--modal-bg);
  border-bottom:1px solid var(--line);font-size:17px;line-height:1.45}
/* الصغيرة (التأكيدات وشبهها): حجمها كما كان · نفس الشكل */
.mbg.small .modal{border:1px solid var(--line2);border-radius:var(--hw-r)}
.mbg.small .hwb>h2:first-child{margin-bottom:14px}
/* الصفحات */
.page,.page.on{transition:none}.page{transform:none}
.page .pwrap{max-width:var(--hw-max);min-height:calc(100% - 2*var(--hw-gap));margin:var(--hw-gap) auto;padding:0 22px 40px;background:var(--modal-bg);
  border:1px solid var(--line2);border-radius:var(--hw-r);box-shadow:0 30px 80px rgb(var(--sh-rgb)/.5)}
.page .phead{position:sticky;top:0;z-index:4;margin:0 -22px 18px;padding:13px 22px 12px;padding-inline-end:16px;background:var(--modal-bg);border-bottom:1px solid var(--line);
  border-radius:var(--hw-r) var(--hw-r) 0 0}
.page .phead h2{font-size:17px}
/* تفاصيل البوت */
#drawer{inset:var(--hw-gap);width:auto;max-width:var(--hw-max);margin:0 auto;border:1px solid var(--line2);border-radius:var(--hw-r);background:var(--modal-bg);
  transform:none;opacity:0;visibility:hidden;transition:none;box-shadow:0 0 0 100vmax rgb(var(--scrim-rgb)/.66),0 30px 80px rgb(var(--sh-rgb)/.5)}
html[dir="rtl"] #drawer{transform:none}
#drawer.on{opacity:1;visibility:visible}
#drawer>*{width:100%;max-width:880px;margin-inline:auto}
#drawer .dhead{max-width:none}
/* الإشعارات */
#notifPanel{left:var(--hw-gap);right:var(--hw-gap);top:var(--hw-gap);bottom:var(--hw-gap);width:auto;max-width:var(--hw-max);margin:0 auto;
  border:1px solid var(--line2);border-radius:var(--hw-r);background:var(--modal-bg);transform:none;transition:none}
#notifPanel.on{transform:none;transition:none}
#notifPanel>*{width:100%;max-width:880px;margin-inline:auto}
#notifPanel .nphead{max-width:none}
/* الاختبار التجريبي (المرجع) */
.btov{padding:var(--hw-gap)}
.btbox{min-height:100%;border-radius:var(--hw-r)}
/* الهاتف: كل نافذة تملأ الشاشة */
@media (max-width:720px){
  .mbg.full,.btov{padding:0}
  .mbg.full .modal,.btbox{width:100%;height:100%;border-radius:0;border:0}
  .mbg.full{padding-top:env(safe-area-inset-top,0px)}
  .page .pwrap{margin:0;min-height:100%;border-radius:0;border:0;padding-top:env(safe-area-inset-top,0px)}
  .page .phead{border-radius:0}
  #drawer,#notifPanel{inset:0;border-radius:0;border:0}
}
.hwclone{overflow:hidden}
'''

SET_ANCHOR = '''onclick="setFont('${x[0]}')">${x[2]}</button>`).join('')}</div></div>'''
SET_ADD = SET_ANCHOR + '''
   <div style="margin-top:8px"><div style="font-size:11px;color:var(--mut2);margin-bottom:6px">🎬 حركة فتح النوافذ (لهذا الجهاز) — الإغلاق بعكسها · «⚡ الوضع الخفيف» بلا حركة:</div><div class="pollrow" id="animRow">${HW_ANIMS.map(x=>`<button class="${uiAnim()===x[0]?'on':''}" data-anim="${x[0]}" onclick="setAnim('${x[0]}')">${x[1]}</button>`).join('')}</div></div>'''

HB_OLD = '''function holyBack(){                                    // ↩️ زر الرجوع بالموبايل: يسكّر اللي فوق أولاً — بعدين يطلع
  try{if(npOpen){toggleNotif();return true}}catch(e){}
  if(!$('#mbg').hidden){hideModal();return true}
  const dr=$('#drawer');if(dr&&dr.classList.contains('on')){closeDrawer();return true}
  const pg=[...document.querySelectorAll('.page.on')].pop();
  if(pg){const b=pg.querySelector('button[onclick*="close"]');b?b.click():pg.classList.remove('on');return true}
  if(window.scrollY>300){goTop();return true}
  return false}'''
HB_NEW = '''function holyBack(){                                    // ↩️ زر الرجوع بالموبايل: يسكّر اللي فوق أولاً — بعدين يطلع
  // 🪟 v3.36.34: القائمة «⋯» · نافذة الخط الصغيرة ⇐ ثم الطبقة الأعلى بترتيب فتحها (تأكيد · نافذة · صفحة · تفاصيل · اختبار · إشعارات)
  try{const p=document.getElementById('stpop');if(p&&p.style.display==='block'){p.style.display='none';return true}}catch(e){}
  try{const c=[...document.querySelectorAll('.card.sk')].find(el=>el._skm);if(c){c._skm=0;c._skv._h='';skinUpd(c);return true}}catch(e){}
  try{hwSync();const t=HW.st[HW.st.length-1];if(t){t.close();hwSync();return true}}catch(e){}
  try{if(npOpen){toggleNotif();return true}}catch(e){}
  if(!$('#mbg').hidden){hideModal();return true}
  const dr=$('#drawer');if(dr&&dr.classList.contains('on')){closeDrawer();return true}
  const pg=[...document.querySelectorAll('.page.on')].pop();
  if(pg){const b=pg.querySelector('button[onclick*="close"]');b?b.click():pg.classList.remove('on');return true}
  if(window.scrollY>300){goTop();return true}
  return false}'''

R = [
    ('''function showModal(html){$('#modal').innerHTML=html;$('#mbg').hidden=false}
function hideModal(){$('#mbg').hidden=true}''', JS),
    (HB_OLD, HB_NEW),
    ('''document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(npOpen){toggleNotif();return}hideModal();closeDrawer();closePage('reports');closePage('wallets')}});''',
     '''document.addEventListener('keydown',e=>{if(e.key==='Escape')holyBack()});   // 🪟 v3.36.34: Esc = زر الرجوع (الأعلى أولاً)'''),
    ('''function btClose(){const o=$('#btov');if(o)o.remove();''',
     '''function btClose(){const o=$('#btov');if(o){const it=HW.st.find(s=>s.k==='bt');hwOut(o,'.btbox',false,it&&it.pt);o.remove();hwSync()}'''),
    ('''function closePage(p){$('#page_'+p).classList.remove('on')}''',
     '''function closePage(p){const e=$('#page_'+p);if(!e)return;if(e.classList.contains('on')){const it=HW.st.find(s=>s.k===e.id);hwOut(e,'.pwrap',false,it&&it.pt)}e.classList.remove('on');hwSync()}'''),
    ('''function closeDrawer(){CUR=null;$('#drawer').classList.remove('on')}''',
     '''function closeDrawer(){CUR=null;const e=$('#drawer');if(e&&e.classList.contains('on')){const it=HW.st.find(s=>s.k==='drawer');hwOut(e,null,false,it&&it.pt)}e.classList.remove('on');hwSync()}'''),
    ('''function toggleNotif(){npOpen=!npOpen;''',
     '''function toggleNotif(){if(npOpen){const it=HW.st.find(s=>s.k==='np');hwOut($('#notifPanel'),null,false,it&&it.pt)}npOpen=!npOpen;'''),
    # every opening registers at once (in the order it happened) — the watcher stays as the safety net for any other path
    ('''function openPage(p){$('#page_'+p).classList.add('on')}''', '''function openPage(p){$('#page_'+p).classList.add('on');hwSync()}'''),
    ('''document.body.appendChild(o);document.body.classList.add('btopen');''', '''document.body.appendChild(o);document.body.classList.add('btopen');hwSync();'''),
    ('''$('#notifPanel').classList.toggle('on',npOpen);''', '''$('#notifPanel').classList.toggle('on',npOpen);hwSync();'''),
    (SET_ANCHOR, SET_ADD),
]
CSS_ANCHOR = '''.tape2 .iv{unicode-bidi:isolate;direction:rtl}.tape2 .iv b{unicode-bidi:isolate;direction:ltr}'''   # the end of the main stylesheet: the frame wins over the older rules


def fn_span(s, name):
    m = re.search(r"\n(?:async )?function " + re.escape(name) + r"\(", s)
    if not m:
        return None
    a = m.start() + 1
    n = re.search(r"\n(?:async )?function [A-Za-z0-9_]+\(|\n/\*|\n</script>", s[a + 10:])
    return a, (a + 10 + n.start()) if n else len(s)


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if s.count(CSS_ANCHOR) != 1:
        print("❌ CSS anchor not found once — nothing written"); sys.exit(1)
    s = s.replace(CSS_ANCHOR, CSS_ANCHOR + CSS)
    done = []
    for nm in SMALL:
        sp = fn_span(s, nm)
        if not sp:
            print(f"❌ function {nm} not found — nothing written"); sys.exit(1)
        seg = s[sp[0]:sp[1]]
        k = seg.count("showModal(")
        if not k:
            print(f"❌ {nm}: no showModal( inside — nothing written"); sys.exit(1)
        s = s[:sp[0]] + seg.replace("showModal(", "showDialog(") + s[sp[1]:]
        done.append(f"{nm}×{k}")
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the frame CSS · {len(done)} dialogs keep their size ({' '.join(done)}) · compiles · {p}")
