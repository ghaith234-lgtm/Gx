# 📏 patch 107 (dashboard v3.36.63 · the compact cards). The owner (20-11): «اريد اتسوي شكل مختصر للكروت … ينطبق على كل الاشكال الكروت ويبين
#   نوع البوت والسعر والربح» ⇒ (after the 4 mock-ups) «نعم اريد في الاعداد اذا اريد شكل مختصر ام لا · اريدها طوليه بعرض الكروت من اضغط
#   عليها تتمدد يعني فيها انميشن وتدفع الي تحت ، بحيث يتناسق مع كل اشكال الكروت حتى لو ضفنا اشكال كروت جديدة · ربح اليوم ، الحاله ،
#   نوع البوت ، سعر العملة».
#   · ⚙️ «📏 الكروت المختصرة» (this device · off by default)
#   · on: every bot card shows one row as wide as the card — the coin · the bot's type · its state (نشط · متوقف · ⏳ مؤقت · ⏸ · 🚨) ·
#     the coin's live price · today's profit (its own unit: $ · or the coin for the sell DCA and the recurring sell) · a stripe in the bot
#     kind's colour · tap ⇒ the card opens to its full self with a height animation that pushes the cards below down · tap again ⇒ back
#   · ONE layer above whatever draws the card (the classic look · ج · ب · OKX — and any look added later): the row is the card's first
#     child, the rest of the card is only hidden while it is short — no look is touched · the colours are the theme's
#   · «⚡ الوضع الخفيف» / no motion ⇒ it opens at once (no animation)
#   python3 devtests/step/patches/p107_compact_cards.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 📏 v3.36.63: الكروت المختصرة (لهذا الجهاز) — طبقة فوق أي شكل للبطاقة (القديم · ج · ب · OKX · وأي شكل يُضاف): سطر بعرض البطاقة فيه
   نوع البوت · حالته · سعر العملة · ربح اليوم — الضغط عليه يمدّ البطاقة كاملة بحركة ويدفع اللي تحتها، ومرة ثانية يرجّعها سطراً */
function uiCmp(){return _ls('dash_cmp')==='on'}
function uiCmpToggle(){const on=!uiCmp();_ls('dash_cmp',on?'on':null);
  document.querySelectorAll('#grid .card[data-dir]').forEach(el=>{el._cmpO=0;cmpApply(el,botOf(el.dataset.dir))});openSettings();
  toast(on?'📏 الكروت مختصرة — اضغط سطر أي بوت لفتح بطاقته':'📏 الكروت كاملة',true)}
const CMP_T={grid:'♾️ شبكة',grid_range:'🎚️ مدى',grid_plus:'➕ بلس',grid_step:'🪜 متدرج',dca:'📉 DCA بيعي',dca_buy:'📈 DCA شرائي',rec_buy:'🔁 دوري شرائي',
  rec_sell:'🔂 دوري بيعي',rec_va:'💹 مسار القيمة'};
const CMP_RGB={grid:'var(--vio-rgb)',grid_range:'var(--blue-rgb)',grid_plus:'244 114 182',grid_step:'var(--cyan-rgb)',dca:'var(--amber-rgb)',dca_buy:'var(--amber-rgb)',
  rec_buy:'var(--cyan-rgb)',rec_sell:'var(--cyan-rgb)',rec_va:'var(--green-rgb)'};
function cmpType(b){const t=b.bot_type||'grid';if(b.dca&&b.dca.plus)return t==='dca_buy'?'⚡ DCA+ شرائي':'⚡ DCA+ بيعي';return CMP_T[t]||gEsc(t)}
function cmpState(b){const d=b.dca||{},r=b.rec||{};
  if(!b.alive)return ['متوقف','off'];
  if(b.cashw&&b.cashw.tp)return ['⏳ مؤقت','tp'];
  if((b.health||{}).state==='bad')return ['🚨 أوامر مرفوضة','bad'];
  if(b.pause_buy||d.paused||r.paused)return ['⏸ موقوف الشراء','tp'];
  return ['نشط','on']}
function cmpToday(b){const t=b.bot_type||'grid',v=+b.today||0,a=Math.abs(v),sg=v>0?'+':v<0?'−':'';
  const coin=t==='dca'?((b.dca||{}).base_coin||b.symbol.split('-')[0]):t==='rec_sell'?((b.rec||{}).base||b.symbol.split('-')[0]):'';
  return {v,s:coin?`${sg}${a?+a.toPrecision(4):0} ${coin}`:`${sg}${a?a.toFixed(a>=1?2:4):'0.00'}$`}}
function cmpApply(el,b){if(!el||!b)return;const on=uiCmp();
  if(el.classList.contains('cmp')!==on)el.classList.toggle('cmp',on);
  if(!on){if(el.classList.contains('cmpo'))el.classList.remove('cmpo');return}
  let row=el._cmr;
  if(!row){row=document.createElement('button');row.type='button';row.className='cmini';
    const im=el.querySelector('img.coin');
    row.innerHTML=`<span class="cm-ic">${im?'':`<b>${gEsc(b.symbol.split('-')[0].slice(0,1))}</b>`}</span><span class="cm-mid"><b class="cm-sym"></b><span class="cm-ln"><span class="cm-typ"></span><span class="cm-st"></span></span></span>
      <span class="cm-end"><span class="cm-pf"><small>اليوم</small> <b class="num" dir="ltr"></b></span><small class="cm-px"><span>السعر</span> <span class="num"></span></small></span><span class="cm-ch" aria-hidden="true">▾</span>`;
    if(im){const c=im.cloneNode(true);c.removeAttribute('id');row.querySelector('.cm-ic').appendChild(c)}
    row.onclick=ev=>{ev.stopPropagation();cmpToggle(el)};
    el._cmr=row;el._cmq={sym:row.querySelector('.cm-sym'),typ:row.querySelector('.cm-typ'),st:row.querySelector('.cm-st'),pw:row.querySelector('.cm-pf'),pf:row.querySelector('.cm-pf b'),px:row.querySelector('.cm-px .num')}}
  if(el.firstElementChild!==row)el.prepend(row);                   // أول ابن دائماً — أي شكل يضيف طبقته بعده
  const Q=el._cmq,set=(n,t)=>{if(n.textContent!==t)n.textContent=t};
  set(Q.sym,b.symbol+(b.demo?' 🧪':''));set(Q.typ,cmpType(b));
  const [st,sc]=cmpState(b);set(Q.st,st);if(Q.st.dataset.c!==sc){Q.st.dataset.c=sc;Q.st.className='cm-st '+sc}
  const td=cmpToday(b);set(Q.pf,td.s);const pc=td.v>1e-12?'up':td.v<-1e-12?'dn':'z';if(Q.pw.dataset.c!==pc){Q.pw.dataset.c=pc;Q.pw.className='cm-pf '+pc}
  const cp=(window.JPX&&JPX[b.symbol])||b.cp||(b.rec||{}).cp||(b.dca||{}).cp;set(Q.px,cp?f4(+cp):'—');
  const rgb=CMP_RGB[b.bot_type||'grid']||'var(--vio-rgb)';if(el._cmrgb!==rgb){el._cmrgb=rgb;el.style.setProperty('--cm-rgb',rgb)}
  const o=!!el._cmO;if(el.classList.contains('cmpo')!==o)el.classList.toggle('cmpo',o);
  row.setAttribute('aria-expanded',String(o));row.title=o?'اضغط لإرجاع البطاقة سطراً':'اضغط لفتح البطاقة كاملة'}
function cmpToggle(el){const b=botOf(el.dataset.dir);if(!b)return;
  const motion=!(typeof hwStyle==='function'&&hwStyle()==='none'),h0=el.getBoundingClientRect().height;
  if(el._cmA){try{el._cmA.cancel()}catch(e){}el._cmA=null}
  const open=!el._cmO;
  if(open){el._cmO=1;cmpApply(el,b);try{skinUpd(el,b)}catch(e){}}
  if(!motion){if(!open){el._cmO=0;cmpApply(el,b)}return}
  let h1;
  if(open)h1=el.getBoundingClientRect().height;
  else{el.classList.remove('cmpo');h1=el.getBoundingClientRect().height;el.classList.add('cmpo')}   // نفس الإطار — بلا رسم بينهما
  el.classList.add('cmpa');
  const a=el.animate([{height:h0+'px'},{height:h1+'px'}],{duration:340,easing:'cubic-bezier(.2,.8,.2,1)'});el._cmA=a;
  const done=()=>{if(el._cmA!==a)return;el._cmA=null;el.classList.remove('cmpa');if(!open){el._cmO=0;cmpApply(el,b)}};
  a.onfinish=done;a.oncancel=()=>{el.classList.remove('cmpa')}}
'''

CSS = '''
/* 📏 v3.36.63: الكروت المختصرة — طبقة فوق أي شكل */
.card>.cmini{display:none}
.card.cmp.cmp>.cmini.cmini{display:grid!important}
.card.cmp:not(.cmpo)>:not(.cmini){display:none!important}
.card.cmp.cmpa{overflow:hidden}
.cmini{grid-template-columns:auto minmax(0,1fr) auto auto;align-items:center;gap:2px 10px;width:100%;margin:0;padding:6px 10px 6px 4px;border:0;background:transparent;
  color:inherit;font:inherit;text-align:start;cursor:pointer;position:relative;border-radius:12px;min-height:46px}
.cmini::before{content:"";position:absolute;inset-block:6px;inset-inline-start:-6px;width:4px;border-radius:4px;background:rgb(var(--cm-rgb,var(--vio-rgb)))}
.cmini:hover{background:rgb(var(--ov-rgb)/.04)}
.cmini:focus-visible{outline:2px solid rgb(var(--cm-rgb,var(--vio-rgb))/.7);outline-offset:2px}
.card.cmp.cmpo>.cmini{margin-bottom:10px;border-bottom:1px solid rgb(var(--ov-rgb)/.08);border-radius:12px 12px 0 0}
.cm-ic{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:rgb(var(--cm-rgb,var(--vio-rgb))/.18);overflow:hidden;flex:none}
.cm-ic img{width:100%;height:100%;object-fit:cover}.cm-ic b{font-size:13px}
.cm-mid{min-width:0;display:flex;flex-direction:column;gap:2px}
.cm-sym{font-size:14px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cm-ln{display:flex;flex-wrap:wrap;align-items:center;gap:2px 8px;font-size:11.5px;color:var(--mut)}
.cm-st::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;margin-inline-end:5px;vertical-align:middle;background:var(--mut2)}
.cm-st.on{color:var(--green)}.cm-st.on::before{background:var(--green);box-shadow:0 0 6px var(--green)}
.cm-st.tp{color:var(--amber)}.cm-st.tp::before{background:var(--amber)}
.cm-st.bad{color:var(--red)}.cm-st.bad::before{background:var(--red)}
.cm-end{display:flex;flex-direction:column;align-items:flex-end;gap:2px;text-align:end;min-width:0}
.cm-pf{white-space:nowrap;color:var(--mut)}.cm-pf small{font-size:11px;margin-inline-end:3px}.cm-pf b{font-size:14.5px;font-weight:800;unicode-bidi:isolate}
.cm-pf.up b{color:var(--green)}.cm-pf.dn b{color:var(--red)}.cm-pf.z b{color:var(--mut)}
.cm-px{font-size:11.5px;color:var(--mut);white-space:nowrap}.cm-px .num{color:var(--tx)}
.cm-ch{font-size:12px;color:var(--mut2);transition:transform .3s}
.card.cmp.cmpo>.cmini .cm-ch{transform:rotate(180deg)}
@media (max-width:380px){.cmini{gap:2px 7px}.cm-sym{font-size:13px}.cm-pf b{font-size:13.5px}}'''

R = [
    ('''function uiMbar(){return _ls('dash_mbar')!=='off'}''', JS + '''function uiMbar(){return _ls('dash_mbar')!=='off'}'''),
    ('''    updCard(el,b,b.demo?benchD:bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});''',
     '''    updCard(el,b,b.demo?benchD:bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b);cmpApply(el,b)});   // 📏 v3.36.63: المختصر'''),
    ('''     +X('skin','🃏','شكل البطاقات',(SKS.find(x=>x[0]===sk)||SKS[0])[1],`<div class="snote">الأرقام والأزرار نفسها في كل الأشكال.</div><div class="pollrow" id="skinRow">${SB}</div>`)''',
     '''     +X('skin','🃏','شكل البطاقات',(SKS.find(x=>x[0]===sk)||SKS[0])[1],`<div class="snote">الأرقام والأزرار نفسها في كل الأشكال.</div><div class="pollrow" id="skinRow">${SB}</div>`)
     +T('📏','الكروت المختصرة','uiCmpToggle()','bCmp',uiCmp(),'مختصرة — كل بوت بسطر (نوعه · حالته · السعر · ربح اليوم) · اضغطه ليفتح كاملاً','كاملة')'''),
    ('''.card.sk:not(.skfull)>:not(.skin){display:none!important}''', '''.card.sk:not(.skfull)>:not(.skin){display:none!important}''' + CSS),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 📏 compact cards (⚙️ · one row per bot · tap to open with motion · above every card look) · compiles · {p}")
