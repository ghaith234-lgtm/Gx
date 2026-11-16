# ⚡ patch 96 (dashboard v3.36.57 · the new DCA+ — the page). The owner (15-11): «الشي الي اضيفه انا اتحكم بالجدول البياني في وضع
#   الاوردرات» · «سويه ملاحضة اقدر اضيفه يدوي لكل اوردر واقدر اضيف عبر الرسم البياني». One editor (`plxOpen`) used in two places:
#   · the deploy form: «⚡ DCA+ بيعي» in the DCA type list — the classic fields hide and the editor takes the preview's place
#   · the card: «✏️ أوامر DCA+ — الجدول والرسم» opens the same editor on the running bot (filled orders ✅ locked) → control plus_edit
#   The editor = the table and the chart together (a change in one shows in the other at once):
#   · the table: per order its distance from the one before %, its size, its exit % (inputs) · and what follows (price · from the base ·
#     total · average · exit price · the drop it needs · the net profit after the fees — the engine's own sums) · ✕ · ➕ at the end
#   · the chart (SVG · mouse and touch): the coin's candles behind (OKX public data) · every order a line with a bar as long as its
#     size · drag a line up/down = its price (the others stay where they are) · drag the circle sideways = its size · tap an empty place
#     above the base = a new order there · the selected order's average and its exit line 🎯 (drag it = that order's exit %)
#   · the selected order: price · size · exit % fields · previous/next · delete · ⚡ a quick fill (count · first distance · its growth ·
#     sizes and their multiplier · exit % from the base to the last order) then any order by hand
#   · warnings: bad rows · an exit under 0.20% (the engine uses 0.20%) · a row with no net profit
#   · the card's table: the exit % column · the details window: the rows instead of the classic settings · the skins: the same button
#   · 📖 the tutorial: a DCA+ tab in the DCA form's tutorial · the ✏️ button explained · 🧪 the trial path runs DCA+ from the form
#   python3 devtests/step/patches/p96_dca_plus_ui.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* ⚡ v3.36.57: DCA+ — محرر السلّم الحر: كل أمر بمسافته وكميته ونسبة خروجه · الجدول والرسم معاً (أي تغيير في أحدهما يظهر في الآخر فوراً) ·
   في نموذج النشر وفي نافذة «✏️ أوامر DCA+» من البطاقة · الحساب نفسه الذي يستعمله المحرك: متوسط مرجّح · هدف = المتوسط × (1 − خروج أعمق
   أمر نُفّذ، لا أقل من 0.20%) · عمولة الأساس آخذ 0.1% · الأوامر صانع 0.08% (بالدرع آخذ) · إعادة الشراء آخذ 0.1% */
const PLX_FM=0.0008,PLX_FT=0.001,PLX_MAX=101,PLX_W=640,PLX_BL=170;
let PLX=null;
function plxDef(){return [{d:0,q:10,x:0.5},{d:1,q:10,x:0.6},{d:1.5,q:15,x:0.7},{d:2,q:20,x:0.8},{d:2.5,q:30,x:0.7},{d:3,q:40,x:0.6}]}
function plxN(v){const s=String(v==null?'':v).trim().replace(/[٠-٩]/g,c=>'٠١٢٣٤٥٦٧٨٩'.indexOf(c)).replace(/[٫,]/g,'.');
  if(!/^-?(\d+\.?\d*|\.\d+)(e-?\d+)?$/i.test(s))return NaN;return parseFloat(s)}
function plxR(v,k){v=+v;if(!isFinite(v))return '';const a=Math.abs(v);return String(+v.toFixed(k!=null?k:(a>=1000?0:a>=100?2:a>=1?4:8)))}
function plxQ(q){return q>=100?Math.round(q):q>=1?+q.toFixed(2):+q.toPrecision(4)}
function plxCalc(rows,base,trail){const out=[],fl=trail?PLX_FT:PLX_FM;let p=+base||0,cq=0,cv=0,cn=0;
  rows.forEach((r,i)=>{const d=+r.d||0,q=+r.q||0,x=+r.x||0;if(i)p=p*(1+d/100);const fee=i?fl:PLX_FT;
    cq+=q;cv+=p*q;cn+=p*q*(1-fee);const avg=cq>0?cv/cq:0,xu=Math.max(x,0.2),tgt=avg*(1-xu/100);
    out.push({n:i,p,q,cq,cv,avg,tgt,xu,gap:p>0?(1-tgt/p)*100:0,dev:base>0?(p/base-1)*100:0,prof:tgt>0?cn/tgt*(1-PLX_FT)-cq:0})});
  return out}
function plxCellOk(rows,i,k){const v=+rows[i][k];if(!isFinite(v))return false;
  return k==='d'?(i===0||(v>0&&v<=50)):k==='q'?v>0:(v>0&&v<=50)}
function plxBad(rows){                                     // نفس قواعد المحرك واللوحة
  if(!rows||rows.length<2)return 'أضف أمر أمان واحداً على الأقل';
  if(rows.length>PLX_MAX)return `الحد ${PLX_MAX-1} أمر أمان`;
  for(let i=0;i<rows.length;i++)if(!['d','q','x'].every(k=>plxCellOk(rows,i,k)))
    return `${i?'أمان '+i:'الأساسي'}: الكمية أكبر من صفر · المسافة بين 0 و50% · نسبة الخروج بين 0 و50%`;
  return ''}
function plxRows(){return PLX?PLX.rows.map((r,i)=>({d:i?+r.d:0,q:+r.q,x:+r.x})):[]}
function plxLockMax(){return PLX&&PLX.locked.size?Math.max(...PLX.locked):-1}
function plxLen(q,qm){return 20+PLX_BL*Math.max(0,q)/(qm||1)}
function plxOpen(box,o){
  if(!box)return;
  const rows=(o.rows&&o.rows.length?o.rows:plxDef()).map((r,i)=>({d:i?+r.d||0:0,q:+r.q,x:+r.x}));
  PLX={box,rows,base:+o.base>0?+o.base:1,locked:new Set((o.locked||[]).map(Number)),sel:rows.length-1,sym:o.sym||'',trail:!!o.trail,cp:+o.cp||0,
       mode:o.mode||'new',bar:'1H',cd:[],fz:null,drag:null,k:1,H:400,coin:((o.sym||'').split('-')[0])||'عملة',calc:[]};
  const last=rows[rows.length-1]||{},r1=rows[1]||{};
  box.innerHTML=`<div class="plx">
   <div data-p="sum"></div><div data-p="warn"></div>
   <div class="plxhd"><b>📈 الأوامر على الرسم</b><span class="plxbars" data-p="bars">${['15m','1H','4H','1D'].map(b=>`<button type="button" data-b="${b}" class="${b==='1H'?'on':''}">${b}</button>`).join('')}</span>
     <span class="plxhint">اسحب خط أي أمر للأعلى أو الأسفل لتغيير سعره · اسحب دائرته يميناً أو يساراً لتغيير كميته · اضغط مكاناً فارغاً فوق السعر لإضافة أمر · اختر أمراً ثم اسحب خطه الأخضر 🎯 لتغيير نسبة خروجه</span></div>
   <div class="plxch" data-p="ch"><svg viewBox="0 0 ${PLX_W} 400" role="img" aria-label="سلّم DCA+"><g data-p="g"></g></svg></div>
   <div data-p="sel"></div>
   <details class="plxfill"><summary>⚡ تعبئة سريعة — ثم عدّل أي أمر وحده</summary>
    <div class="frm">
     <div class="fld"><label>عدد أوامر الأمان</label><input class="num" data-f="n" value="${rows.length-1}"></div>
     <div class="fld"><label>📏 أول مسافة %</label><input class="num" data-f="d1" value="${plxR(+r1.d||1,3)}"></div>
     <div class="fld"><label>زيادة المسافة لكل أمر %</label><input class="num" data-f="dg" value="0.5"><small>0 = ثابتة</small></div>
     <div class="fld"><label>كمية الأساسي</label><input class="num" data-f="q0" value="${plxR(+rows[0].q)}"></div>
     <div class="fld"><label>كمية أول أمان</label><input class="num" data-f="q1" value="${plxR(+r1.q||+rows[0].q)}"></div>
     <div class="fld"><label>مضاعف الكمية</label><input class="num" data-f="qm" value="1.3"><small>1 = متساوية</small></div>
     <div class="fld"><label>🎯 خروج الأساسي %</label><input class="num" data-f="x0" value="${plxR(+rows[0].x,3)}"></div>
     <div class="fld"><label>🎯 خروج آخر أمر %</label><input class="num" data-f="x1" value="${plxR(+last.x,3)}"><small>بينهما يتدرّج</small></div>
    </div><button type="button" class="primary" onclick="plxFill()" style="margin-top:8px">املأ الجدول</button></details>
   <div data-p="tw"></div>
   <p class="plxnote">💡 صافٍ بعد عمولة OKX: الأساس آخذ 0.1% · الأوامر صانع 0.08%${o.trail?' (بالدرع آخذ 0.1%)':''} · إعادة الشراء آخذ 0.1%. الهدف = متوسط ما بِيع × (1 − نسبة خروج أعمق أمر نُفّذ)، وعنده يعيد شراء كل ما باع دفعة واحدة. الأرقام على سعر الأساس المعروض — البوت يحسب من سعر التنفيذ الفعلي.</p></div>`;
  const q=k=>box.querySelector(`[data-p="${k}"]`);PLX.q=q;
  const svg=q('ch').querySelector('svg');PLX.svg=svg;PLX.g=q('g');
  svg.addEventListener('pointerdown',plxDown);svg.addEventListener('pointermove',plxMove);
  svg.addEventListener('pointerup',plxUp);svg.addEventListener('pointercancel',plxUp);
  q('bars').onclick=e=>{const b=e.target.closest('button');if(!b||!PLX)return;PLX.bar=b.dataset.b;q('bars').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x===b));plxCandles()};
  plxFull();plxCandles()}
function plxFull(){const P=PLX;if(!P)return;P.calc=plxCalc(P.rows,P.base,P.trail);if(P.sel!=null&&P.sel>=P.rows.length)P.sel=P.rows.length-1;plxTbl();P.selK=null;plxSoft()}
function plxTbl(){const P=PLX,lm=plxLockMax(),c=gEsc(P.coin);
  let h=`<div class="plxtbl"><table class="dntbl"><thead><tr><th>الأمر</th><th>المسافة %<br><small>عن الذي قبله</small></th><th>الكمية<br><small>${c}</small></th><th>الخروج %<br><small>لو وصل هنا</small></th>
    <th>السعر</th><th>عن الأساس</th><th>المجموع<br><small>${c}</small></th><th>المتوسط</th><th>🎯 سعر الخروج</th><th>يحتاج نزولاً</th><th>💎 ربح صافٍ<br><small>${c}</small></th><th></th></tr></thead><tbody>`;
  P.rows.forEach((r,i)=>{const L=P.locked.has(i);
    h+=`<tr data-i="${i}" class="${L?'lk':''}"><td class="plxn">${L?'✅ ':''}${i?'أمان '+i:'الأساسي'}</td>
     <td>${i?`<input class="num" data-k="d" inputmode="decimal"${L?' disabled':''}>`:'—'}</td>
     <td><input class="num" data-k="q" inputmode="decimal"${L?' disabled':''}></td>
     <td><input class="num" data-k="x" inputmode="decimal"></td>
     <td class="num" data-c="p"></td><td class="num" data-c="dev" style="color:var(--vio)"></td><td class="num" data-c="cq"></td><td class="num" data-c="avg"></td>
     <td class="num" data-c="tgt" style="color:var(--green)"></td><td class="num" data-c="gap" style="color:var(--cyan);font-weight:700"></td><td class="num" data-c="prof"></td>
     <td>${i>lm&&i>0?`<button type="button" class="plxdel" onclick="plxDel(${i})" title="حذف هذا الأمر">✕</button>`:''}</td></tr>`});
  h+=`</tbody></table></div><div class="plxadd"><button type="button" onclick="plxAdd()"${P.rows.length>=PLX_MAX?' disabled':''}>➕ أمر في النهاية</button></div>`;
  const tw=P.q('tw');tw.innerHTML=h;
  tw.querySelectorAll('input[data-k]').forEach(inp=>{const i=+inp.closest('tr').dataset.i;
    inp.oninput=()=>plxIn(i,inp.dataset.k,inp.value);inp.onfocus=()=>{if(PLX.sel!==i){PLX.sel=i;plxSoft()}}});
  tw.querySelectorAll('td.plxn').forEach(td=>td.onclick=()=>plxSel(+td.closest('tr').dataset.i))}
function plxIn(i,k,v){const P=PLX;if(!P||!P.rows[i])return;if(P.locked.has(i)&&k!=='x')return;P.rows[i][k]=plxN(v);plxSoft()}
function plxSel(i){if(!PLX)return;PLX.sel=i;plxSoft()}
function plxSoft(){const P=PLX;if(!P||!P.box.isConnected)return;
  P.calc=plxCalc(P.rows,P.base,P.trail);
  const tw=P.q('tw');
  P.calc.forEach((c,i)=>{const tr=tw.querySelector(`tr[data-i="${i}"]`);if(!tr)return;tr.classList.toggle('on',i===P.sel);
    const set=(k,v)=>{const e=tr.querySelector(`[data-c="${k}"]`);if(e&&e.textContent!==v)e.textContent=v};
    set('p',f4(c.p));set('dev',i?'▲ '+c.dev.toFixed(2)+'%':'—');set('cq',plxR(c.cq));set('avg',f4(c.avg));set('tgt',f4(c.tgt));set('gap','▼ '+c.gap.toFixed(2)+'%');
    const pe=tr.querySelector('[data-c="prof"]');if(pe){pe.textContent=(c.prof>=0?'+':'')+plxR(c.prof,6);pe.style.color=c.prof>0?'var(--green)':'var(--red)'}
    ['d','q','x'].forEach(k=>{const inp=tr.querySelector(`input[data-k="${k}"]`);if(!inp)return;
      if(document.activeElement!==inp){const val=plxR(+P.rows[i][k],k==='q'?null:3);if(inp.value!==val)inp.value=val}
      inp.classList.toggle('bad',!plxCellOk(P.rows,i,k))})});
  plxSum();plxDraw();plxSelBox();if(P.onchg)P.onchg()}
function plxSum(){const P=PLX,C=P.calc,L=C[C.length-1]||{},F=C[0]||{},c=gEsc(P.coin),bad=plxBad(P.rows),sg=v=>(v>=0?'+':'')+plxR(v,6);
  const low=P.rows.map((r,i)=>(+r.x>0&&+r.x<0.2)?i:-1).filter(i=>i>=0),neg=C.filter(z=>!(z.prof>0)).map(z=>z.n);
  P.q('sum').innerHTML=`<div class="dnsum">
    <div class="dnstat"><span>🪙 العملات لو نُفّذ الكل</span><b><bdi>${plxR(L.cq||0)} ${c}</bdi></b><small style="display:block;color:var(--mut2);font-size:10px"><bdi>≈ ${(L.cv||0).toFixed(2)}$</bdi></small></div>
    <div class="dnstat"><span>📏 التغطية (مدى الصعود)</span><b style="color:var(--vio)">▲ ${(L.dev||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>🎯 بعد آخر أمر يحتاج نزولاً</span><b style="color:var(--cyan)">▼ ${(L.gap||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — الأساس فقط</span><b style="color:var(--green)">${sg(F.prof||0)} ${c}</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — السلم كاملاً</span><b style="color:var(--green)">${sg(L.prof||0)} ${c}</b></div>
    <div class="dnstat"><span>📋 الأوامر</span><b>${P.rows.length-1} أمر أمان</b></div></div>`;
  let w='';
  if(bad)w+=`<div class="dnwarn plxred">⚠️ ${gEsc(bad)}</div>`;
  if(low.length)w+=`<div class="dnwarn plxamb">🛡️ نسبة خروج أقل من 0.20% (${low.map(n=>n?'أمان '+n:'الأساسي').join('، ')}) — لا تغطي العمولتين، فيستعمل البوت 0.20% (الجدول محسوب عليها)</div>`;
  if(!bad&&neg.length)w+=`<div class="dnwarn plxred">⚠️ لا ربح صافياً لو خرج عند: ${neg.map(n=>n?'أمان '+n:'الأساسي').join('، ')} — ارفع نسبة خروجه</div>`;
  if(P.locked.size)w+=`<p class="plxnote">✅ = نُفّذ في هذه الدورة: سعره وكميته ثابتان، ونسبة خروجه تتغيّر. الإضافة والحذف فوق آخر أمر نُفّذ.</p>`;
  P.q('warn').innerHTML=w}
function plxDraw(){const P=PLX,svg=P.svg;if(!svg||!P.calc.length)return;const C=P.calc;
  if(!P.fz){const cw=svg.clientWidth||svg.getBoundingClientRect().width||PLX_W;P.k=Math.min(2.2,Math.max(1,PLX_W/Math.max(260,cw)));P.H=P.k>1.4?560:360}
  const W=PLX_W,H=P.H,k=P.k,fs=11*k,pt=fs+8,pb=fs+6,XR=W-10,XC=Math.round(W*0.46);
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  let lo,hi;
  if(P.fz){lo=P.fz.lo;hi=P.fz.hi}
  else{const ps=[];C.forEach(c=>ps.push(c.p,c.tgt));if(P.cp>0)ps.push(P.cp);P.cd.slice(-72).forEach(r=>ps.push(+r[2],+r[3]));
    lo=Math.min(...ps);hi=Math.max(...ps);const pd=(hi-lo)*0.05||hi*0.01,mp=Math.max(...C.map(c=>c.p));lo-=pd;hi=Math.max(hi+pd*2.5,mp*1.03);P.lo=lo;P.hi=hi}   // مكان فوق آخر أمر لإضافة أوامر بالضغط
  const Y=p=>pt+(hi-p)/(hi-lo)*(H-pt-pb);P.Y=Y;P.P=y=>hi-(y-pt)/(H-pt-pb)*(hi-lo);
  let g='';
  const cd=P.cd.slice(-72);
  if(cd.length){const w=(XC-14)/cd.length;cd.forEach((r,j)=>{const o=+r[1],h=+r[2],l=+r[3],c=+r[4],x=10+j*w+w/2,col=c>=o?'var(--green)':'var(--red)';
      g+=`<line x1="${x}" y1="${Y(h)}" x2="${x}" y2="${Y(l)}" stroke="${col}" stroke-width="${Math.max(1,w*0.14)}" opacity=".4"/><rect x="${x-w*0.32}" y="${Y(Math.max(o,c))}" width="${w*0.64}" height="${Math.max(1,Math.abs(Y(o)-Y(c)))}" fill="${col}" opacity=".4"/>`});
    g+=`<text x="12" y="${fs+2}" font-size="${fs*0.85}" fill="var(--mut2)">${gEsc(P.sym)} · ${P.bar}</text>`}
  const s=P.sel!=null?C[P.sel]:null;
  if(s){const ya=Y(s.avg),yt=Y(s.tgt),hk=7*k;
    g+=`<rect x="${XC}" y="${yt}" width="${XR-XC}" height="${Math.max(0,H-pb-yt)}" fill="rgb(var(--green-rgb)/.07)"/>`;
    g+=`<line x1="10" y1="${ya}" x2="${XR}" y2="${ya}" stroke="var(--amber)" stroke-width="${1.2*k}" stroke-dasharray="${6*k} ${4*k}"/>`;
    g+=`<line x1="10" y1="${yt}" x2="${XR}" y2="${yt}" stroke="var(--green)" stroke-width="${2*k}"/>`;
    g+=`<path d="M${XC} ${yt-hk} l${hk} ${hk} l${-hk} ${hk} l${-hk} ${-hk} z" fill="var(--green)"/>`;
    g+=`<text x="${XC-hk-6}" y="${yt+fs+3}" font-size="${fs}" fill="var(--green)" font-weight="700" direction="rtl" unicode-bidi="embed">🎯 خروج ${s.n?'أمان '+s.n:'الأساسي'}</text>`;   // العربي يسار المقبض والأرقام يمينه (لا تختلط الاتجاهات)
    g+=`<text x="${XC+hk+6}" y="${yt+fs+3}" font-size="${fs}" fill="var(--green)" font-weight="700">${plxR(+P.rows[s.n].x,3)}% → ${f4(s.tgt)} · ▼${s.gap.toFixed(2)}%</text>`;
    g+=`<text x="12" y="${ya-5}" font-size="${fs*0.9}" fill="var(--amber)" direction="rtl" unicode-bidi="embed" text-anchor="end">المتوسط ${f4(s.avg)}</text>`}
  if(P.cp>0&&Math.abs(P.cp/C[0].p-1)>0.0005){const yc=Y(P.cp);
    g+=`<line x1="10" y1="${yc}" x2="${XR}" y2="${yc}" stroke="var(--vio)" stroke-width="${1.4*k}" stroke-dasharray="${2*k} ${3*k}"/><text x="12" y="${yc-5}" font-size="${fs*0.9}" fill="var(--vio)">⚡ الآن ${f4(P.cp)}</text>`}
  const qm=Math.max(...C.map(c=>c.q).filter(v=>v>0),1e-12),lab=[];
  C.forEach((c,i)=>{const y=Y(c.p),L=P.locked.has(i),on=i===P.sel,col=L?'var(--green)':(on?'var(--amber)':(i?'var(--red)':'var(--vio)')),x0=XR-plxLen(c.q,qm);
    g+=`<line x1="10" y1="${y}" x2="${XR}" y2="${y}" stroke="${col}" stroke-width="${0.8*k}" opacity="${on?0.75:0.3}" stroke-dasharray="${3*k} ${3*k}"/>`;
    g+=`<line x1="${x0}" y1="${y}" x2="${XR}" y2="${y}" stroke="${col}" stroke-width="${(on?7:5)*k}" stroke-linecap="round" opacity=".9"/>`;
    if(!L)g+=`<circle cx="${x0}" cy="${y}" r="${6*k}" fill="rgb(var(--ov-rgb)/.04)" stroke="${col}" stroke-width="${2*k}"/>`;
    lab.push({y,on,col,x:x0-10*k,t:`${L?'✅ ':''}${i?'أمان '+i:'الأساس'} · ${f4(c.p)} · ${plxR(c.q)}`})});
  lab.sort((a,b)=>a.y-b.y);let ly=-1e9;const keep=lab.filter(o=>o.on);
  lab.forEach(o=>{if(o.on)return;if(o.y-ly>=fs*1.2&&keep.every(z=>Math.abs(z.y-o.y)>=fs*1.2)){keep.push(o);ly=o.y}});
  keep.forEach(o=>{g+=`<text x="${o.x}" y="${o.y+fs*0.36}" font-size="${fs}" fill="${o.col}" text-anchor="end" font-weight="${o.on?700:400}">${o.t}</text>`});
  P.g.innerHTML=g}
function plxPt(ev){const r=PLX.svg.getBoundingClientRect();return {x:(ev.clientX-r.left)/r.width*PLX_W,y:(ev.clientY-r.top)/r.height*PLX.H}}
function plxSetP(i,pr){const P=PLX,C=P.calc;if(i<1||P.locked.has(i)||!C[i]||!(pr>0))return;
  const lo=C[i-1].p*1.0001,hi=i+1<C.length?C[i+1].p/1.0001:C[i-1].p*1.5;pr=Math.min(Math.max(pr,lo),hi);
  P.rows[i].d=+((pr/C[i-1].p-1)*100).toFixed(4);
  if(i+1<C.length&&!P.locked.has(i+1))P.rows[i+1].d=+((C[i+1].p/pr-1)*100).toFixed(4)}   // التي بعده تبقى مكانها
function plxDown(ev){const P=PLX;if(!P||!P.calc.length||!P.Y)return;const {x,y}=plxPt(ev),C=P.calc,tol=12*P.k;P.fz={lo:P.lo,hi:P.hi};
  let dr=null;const s=P.sel!=null?C[P.sel]:null;
  if(s&&Math.abs(y-P.Y(s.tgt))<tol)dr={k:'x',i:P.sel};
  else{let b=-1,bd=1e9;C.forEach((c,i)=>{const d=Math.abs(y-P.Y(c.p));if(d<bd){bd=d;b=i}});
    if(bd<tol){const qm=Math.max(...C.map(c=>c.q).filter(v=>v>0),1e-12),x0=PLX_W-10-plxLen(C[b].q,qm);
      if(!P.locked.has(b)&&Math.abs(x-x0)<tol*1.4)dr={k:'q',i:b,x0:x,l0:plxLen(C[b].q,qm),qm};
      else if(b>0&&!P.locked.has(b))dr={k:'p',i:b};
      else dr={k:'sel',i:b};
      P.sel=b}
    else dr={k:'tap',x0:x,y0:y}}
  P.drag=dr;try{P.svg.setPointerCapture(ev.pointerId)}catch(e){}ev.preventDefault();plxSoft()}
function plxMove(ev){const P=PLX;if(!P||!P.drag)return;const {x,y}=plxPt(ev),d=P.drag;
  if(d.k==='p')plxSetP(d.i,P.P(y));
  else if(d.k==='x'){const c=P.calc[d.i];if(c&&c.avg>0)P.rows[d.i].x=+Math.min(50,Math.max(0.2,(1-P.P(y)/c.avg)*100)).toFixed(2)}
  else if(d.k==='q'){const L=Math.max(21,d.l0+(d.x0-x));P.rows[d.i].q=plxQ(Math.max(d.qm*0.01,(L-20)/PLX_BL*d.qm))}
  else return;
  ev.preventDefault();if(!P.raf)P.raf=requestAnimationFrame(()=>{if(PLX){PLX.raf=0;plxSoft()}})}
function plxUp(ev){const P=PLX;if(!P)return;const d=P.drag;P.drag=null;
  if(d&&d.k==='tap'){const {x,y}=plxPt(ev);if(Math.hypot(x-d.x0,y-d.y0)<8*P.k){const pr=P.P(y);P.fz=null;plxAddAt(pr);return}}
  P.fz=null;plxSoft()}
function plxAddAt(pr){const P=PLX,C=P.calc,lm=plxLockMax();
  if(P.rows.length>=PLX_MAX){toast(`الحد ${PLX_MAX-1} أمر أمان`,false);return}
  let k=C.findIndex(c=>c.p>pr);if(k<0)k=C.length;
  if(k<1){toast('أوامر البيعي فوق سعر الأساس — اضغط فوقه',false);plxSoft();return}
  if(k<=lm){toast('أضف الأوامر فوق آخر أمر نُفّذ',false);plxSoft();return}
  const d=(pr/C[k-1].p-1)*100;if(!(d>0.01&&d<=50)){toast('المسافة عن الأمر الذي قبله بين 0 و50%',false);plxSoft();return}
  const tpl=P.rows[k-1];
  if(k<C.length)P.rows[k].d=+((C[k].p/pr-1)*100).toFixed(4);
  P.rows.splice(k,0,{d:+d.toFixed(4),q:+tpl.q,x:+tpl.x});P.sel=k;plxFull()}
function plxAdd(){const P=PLX;if(!P||P.rows.length>=PLX_MAX)return;const l=P.rows[P.rows.length-1];
  P.rows.push({d:+(P.rows.length>1?+l.d||1:1),q:+l.q||1,x:+l.x||0.5});P.sel=P.rows.length-1;plxFull()}
function plxDel(i){const P=PLX;if(!P||i<1||i<=plxLockMax()||!P.rows[i])return;const C=P.calc;
  if(i+1<P.rows.length&&C[i+1]&&C[i-1])P.rows[i+1].d=+((C[i+1].p/C[i-1].p-1)*100).toFixed(4);   // التي بعده تبقى مكانها
  P.rows.splice(i,1);P.sel=Math.min(i,P.rows.length-1);plxFull()}
function plxFill(){const P=PLX;if(!P)return;const v=k=>plxN((P.box.querySelector(`[data-f="${k}"]`)||{}).value);
  const n=Math.round(v('n')),d1=v('d1'),dg=v('dg'),q0=v('q0'),q1=v('q1'),qm=v('qm'),x0=v('x0'),x1=v('x1');
  if(!(n>=1&&n<=PLX_MAX-1)||!(d1>0)||!isFinite(dg)||!(q0>0)||!(q1>0)||!(qm>0)||!(x0>0)||!(x1>0)){toast('أكمل أرقام التعبئة السريعة',false);return}
  const rows=P.rows.slice(0,plxLockMax()+1);
  for(let i=rows.length;i<=n;i++)rows.push(i===0?{d:0,q:q0,x:x0}:{d:+Math.max(0.05,d1+dg*(i-1)).toFixed(3),q:plxQ(q1*Math.pow(qm,i-1)),x:+(x0+(x1-x0)*i/n).toFixed(2)});
  P.rows=rows;P.sel=rows.length-1;plxFull()}
function plxSelBox(){const P=PLX,box=P.q('sel'),i=P.sel,C=P.calc;
  if(i==null||!C[i]){box.innerHTML='<p class="plxnote">اختر أمراً من الرسم أو من الجدول.</p>';P.selK=null;return}
  const c=C[i],L=P.locked.has(i),key=i+'|'+P.rows.length+'|'+L;
  if(P.selK!==key){P.selK=key;
    box.innerHTML=`<div class="plxselb"><b>${L?'✅ ':''}${i?'أمان '+i:'الأساسي'}</b>
      <label>السعر <input class="num" data-s="p" inputmode="decimal"${L||i===0?' disabled':''}></label>
      <label>الكمية <input class="num" data-s="q" inputmode="decimal"${L?' disabled':''}></label>
      <label>الخروج % <input class="num" data-s="x" inputmode="decimal"></label>
      <span class="plxsi" data-s="info"></span>
      <span class="plxsb"><button type="button" onclick="plxSel(${Math.max(0,i-1)})"${i?'':' disabled'} title="الأمر الذي قبله">▼</button><button type="button" onclick="plxSel(${Math.min(P.rows.length-1,i+1)})"${i<P.rows.length-1?'':' disabled'} title="الأمر الذي بعده">▲</button>${i>plxLockMax()&&i>0?`<button type="button" class="plxdel" onclick="plxDel(${i})">✕ حذف</button>`:''}</span></div>`;
    const S=k=>box.querySelector(`[data-s="${k}"]`);
    S('p').onchange=()=>{const v=plxN(S('p').value);if(v>0){plxSetP(i,v);plxSoft()}};
    S('q').oninput=()=>plxIn(i,'q',S('q').value);S('x').oninput=()=>plxIn(i,'x',S('x').value)}
  const S=k=>box.querySelector(`[data-s="${k}"]`),setv=(k,v)=>{const e=S(k);if(e&&document.activeElement!==e&&e.value!==v)e.value=v};
  setv('p',String(+c.p.toPrecision(8)));setv('q',plxR(+P.rows[i].q));setv('x',plxR(+P.rows[i].x,3));
  ['q','x'].forEach(k=>{const e=S(k);if(e)e.classList.toggle('bad',!plxCellOk(P.rows,i,k))});
  S('info').innerHTML=`المتوسط <bdi>${f4(c.avg)}</bdi> · 🎯 الخروج <bdi>${f4(c.tgt)}</bdi> · يحتاج نزولاً <bdi>${c.gap.toFixed(2)}%</bdi> · 💎 <bdi>${(c.prof>=0?'+':'')+plxR(c.prof,6)} ${gEsc(P.coin)}</bdi>`}
async function plxCandles(){const P=PLX;if(!P||!/^[A-Z0-9]{2,15}-[A-Z]{2,10}$/.test(P.sym))return;
  let r=null;try{r=await api('/api/candles',{sym:P.sym,bar:P.bar},true)}catch(e){}
  if(PLX!==P||!r||!r.ok)return;P.cd=r.rows||[];if(P.onCd)P.onCd(P.cd);plxSoft()}
function plxForm(){const box=$('#dn_preview');if(!box)return;
  const sym=($('#dn_sym').value||'').trim().toUpperCase(),bp=plxN($('#dn_bp').value),tr=!!($('#dn_trail')||{}).checked;
  if(!PLX||PLX.box!==box||!box.querySelector('.plx')){
    plxOpen(box,{rows:window._plxKeep||null,base:bp>0?bp:1,sym,trail:tr,mode:'new'});
    PLX.onCd=cd=>{const e=$('#dn_bp');if(e&&!e.dataset.man&&cd.length){const lc=+cd[cd.length-1][4];if(lc>0){e.value=String(+lc.toPrecision(8));PLX.base=lc}}}}
  else{const ch=PLX.sym!==sym;PLX.sym=sym;PLX.coin=sym.split('-')[0]||'عملة';if(bp>0)PLX.base=bp;PLX.trail=tr;plxSoft();if(ch)plxCandles()}}
function dcaPlusEdit(b){const d=b.dca||{},P=d.plus||{};
  const live=d.phase==='selling'||d.phase==='buying',cp=(window.JPX&&JPX[b.symbol])||b.cp||0,base=live&&P.base>0?P.base:cp;
  showModal(`<h2 style="color:var(--green)">✏️ أوامر DCA+ — ${gEsc(b.symbol)}</h2>
    <p class="plxnote" style="margin-bottom:8px">${live?'الأوامر المنفّذة في هذه الدورة ✅ ثابتة بسعرها وكميتها (تستطيع تغيير نسبة خروجها). حرّك أي أمر لم يُنفّذ أو غيّر كميته، أو أضف أوامر واحذفها — يطبّقها البوت خلال ثوانٍ: يلغي أوامره التي لم تُنفّذ على المنصة ويضعها بأسعارها الجديدة.':'لا توجد دورة مفتوحة الآن — تبدأ الدورة القادمة بهذه الأوامر.'}</p>
    ${P.pending?'<div class="dnwarn plxamb">⏳ تعديل سابق ينتظر البوت</div>':''}${P.err?`<div class="dnwarn plxred">⚠️ لم يطبّق البوت آخر تعديل: ${gEsc(P.err)}</div>`:''}
    <div id="plx_edit"></div>
    <div class="mbtns" style="margin-top:12px"><button class="primary" id="plx_save" style="background:linear-gradient(94deg,var(--green),#16a34a)">💾 احفظ الأوامر</button><button onclick="hideModal()">إلغاء</button></div>`);
  plxOpen($('#plx_edit'),{rows:P.rows,base:base||1,locked:live?P.locked:[],sym:b.symbol,trail:d.trail_on,cp,mode:'edit'});
  $('#plx_save').onclick=async()=>{const e=plxBad(plxRows());if(e){toast(e,false);return}
    const btn=$('#plx_save');btn.disabled=true;
    try{const r=await api('/api/control',{dir:b.dir,action:'plus_edit',value:{rows:plxRows()}});toast(r.msg,r.ok);if(r.ok){hideModal();tick()}}
    catch(e){toast('تعذر الاتصال',false)}finally{if(btn.isConnected)btn.disabled=false}}}
function dcaPlusRowsTbl(P,base){return `<table class="dntbl" style="margin-bottom:10px"><thead><tr><th>الأمر</th><th>المسافة<br><small>عن الذي قبله</small></th><th>الكمية ${gEsc(base)}</th><th>نسبة الخروج</th></tr></thead><tbody>${(P.rows||[]).map((r,i)=>
  `<tr><td>${(P.locked||[]).includes(i)?'✅ ':''}${i?'أمان '+i:'الأساسي'}</td><td class="num">${i?'▲ '+r.d+'%':'—'}</td><td class="num">${r.q}</td><td class="num">${r.x}%</td></tr>`).join('')}</tbody></table>`}
'''

TUT = r'''  dca_plus:{t:'DCA+ البيعي',
    idea:['مثل DCA البيعي: يبيع جزءاً من عملتك ثم يبيع أكثر كلما صعد السعر، وحين ينزل السعر يعيد شراء كل ما باع دفعة واحدة — الربح بالعملة.',
          'الفرق: أنت تضع كل أمر بنفسك — مسافته عن الأمر الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم، بدل معادلة واحدة لكل الأوامر.',
          'نسبة الخروج تخص الأمر نفسه: إن كان أعمق أمر نُفّذ هو أمان 5 فالهدف = المتوسط ناقص نسبة خروج أمان 5. فتجعل الأوامر الأولى بربح جيد، والأخيرة الكبيرة بربح صغير فيخرج بسرعة ولا يبقى معلّقاً.'],
    steps:[['البيع الأولي','بيع الأمر الأساسي بسعر السوق.'],['أوامرك','كل أمر فوق الذي قبله بالمسافة التي وضعتها وبكميته هو.'],['المتوسط','متوسط مرجّح لكل ما بِيع (كالعادي).'],
           ['الهدف','المتوسط ناقص نسبة خروج أعمق أمر نُفّذ — يتغيّر فوراً كلما نُفّذ أمر أعمق.'],['الإغلاق','حين ينزل السعر إلى الهدف يعيد شراء كل ما باع بدولاره دفعة واحدة ⇐ عملات أكثر.'],
           ['✏️ التعديل والبوت يعمل','من زر «✏️ أوامر DCA+» في البطاقة: الأوامر التي لم تُنفّذ تنتقل إلى أسعارها الجديدة خلال ثوانٍ، والمنفّذة تبقى بسعرها وكميتها (تتغيّر نسبة خروجها فقط).']],
    ex:['الأساس 10 عملات عند 1.00$ بخروج 0.5% · أمان 1 بعده بـ1% (1.01$) 10 عملات بخروج 0.6% · أمان 2 بعده بـ2% (1.0302$) 30 عملة بخروج 0.3%.',
        'نُفّذت الثلاثة ⇐ المتوسط نحو 1.0201$ والهدف 0.3% تحته نحو 1.0171$ — أي نزول نحو 1.3% فقط من آخر سعر بيع. لو كانت نسبة الخروج 1% لاحتاج نزولاً نحو 2%.'],
    btns:['dca_plus','dca_close','dca_trail','dca_last','hist','table','lddr','chart','dca_pause','cset','del'],
    faq:[['هل يبيع كل أمر وحده؟','لا. يعيد شراء كل ما باع في الدورة دفعة واحدة عند الهدف — مثل DCA العادي. نسبة الخروج تحدد مكان الهدف فقط.'],
         ['لماذا أجعل خروج الأوامر الأخيرة صغيراً؟','لأن المتوسط يبتعد عن السعر بعد أوامر كثيرة؛ خروج صغير يقرّب الهدف فيخرج أسرع بربح أقل بدل أن يبقى معلّقاً.'],
         ['هل أخسر لو جعلت النسبة صغيرة جداً؟','أقل نسبة يستعملها البوت 0.20% (تغطي العمولتين)، والجدول يعرض الربح الصافي لكل صف قبل التشغيل.'],
         ['ماذا لو عدّلت أمراً والبوت يعمل؟','يلغي أوامره على المنصة التي لم تُنفّذ ويضعها بأسعارها الجديدة خلال ثوانٍ، ولا يمس ما نُفّذ.']]},
'''

CSS = '''
.dcaplusb{width:100%;padding:9px 10px;margin-bottom:6px;border-radius:10px;font-size:12.5px;border:1px solid rgb(var(--green-rgb)/.45);background:rgb(var(--green-rgb)/.08);color:var(--green);text-align:center}
.dcaplusb.wait{border-color:rgb(var(--amber-rgb)/.5);background:rgb(var(--amber-rgb)/.1);color:var(--amber)}
.dcaplusb.bad{border-color:rgb(var(--red-rgb)/.5);background:rgb(var(--red-rgb)/.08);color:var(--red)}
.plx{display:grid;gap:10px;grid-template-columns:minmax(0,1fr)}
.plx>*{min-width:0}
.plxhd{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:12.5px}
.plxhint{flex:1 1 100%;color:var(--mut2);font-size:10.5px;line-height:1.7}
.plxbars{display:inline-flex;gap:4px}.plxbars button{padding:3px 9px;font-size:11px;border-radius:7px}
.plxbars button.on{background:linear-gradient(94deg,var(--cyan),var(--vio));color:#fff}
.plxch{border:1px solid var(--line);border-radius:12px;background:rgb(var(--ov-rgb)/.02);overflow:hidden}
.plxch svg{display:block;width:100%;height:auto;direction:ltr;touch-action:none;user-select:none;-webkit-user-select:none;cursor:crosshair}
.plxselb{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;padding:8px 10px;border:1px solid rgb(var(--amber-rgb)/.4);border-radius:10px;background:rgb(var(--amber-rgb)/.06);font-size:12px}
.plxselb label{display:inline-flex;align-items:center;gap:4px;color:var(--mut)}
.plxselb input,.plxtbl input{width:68px;padding:4px 6px;font-size:12px}
.plxsi{flex:1 1 220px;color:var(--mut);font-size:11.5px}
.plxsb{display:inline-flex;gap:4px}.plxsb button{padding:3px 9px;font-size:12px}
.plxtbl{overflow-x:auto}.plxtbl td,.plxtbl th{white-space:nowrap}
.plxtbl tr.on td{background:rgb(var(--amber-rgb)/.10)}
.plxtbl tr.lk td{background:rgb(var(--green-rgb)/.06)}
.plxtbl input.bad,.plxselb input.bad{border-color:var(--red);color:var(--red)}
.plxtbl input:disabled,.plxselb input:disabled{opacity:.55}
.plxn{cursor:pointer}
.plxdel{padding:2px 7px;font-size:11px;color:var(--red);border-color:rgb(var(--red-rgb)/.4)}
.plxadd{display:flex;gap:8px}
.plxfill{border:1px dashed var(--line);border-radius:10px;padding:6px 10px;font-size:12px}
.plxfill summary{cursor:pointer;color:var(--cyan)}
.plxfill .frm{margin-top:8px}
.plxnote{color:var(--mut);font-size:11.5px;line-height:1.8}
.dnwarn.plxred{background:rgb(var(--red-rgb)/.10);border:1px solid rgb(var(--red-rgb)/.3);color:var(--red)}
.dnwarn.plxamb{background:rgb(var(--amber-rgb)/.12);border:1px solid rgb(var(--amber-rgb)/.3);color:var(--amber)}'''

R = [
    # ── the editor (before the classic chart of the form)
    ('''function dcaChart(rows,s,base){''', JS + '''function dcaChart(rows,s,base){'''),
    # ── the deploy form
    ('''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
  </select></div>''', '''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
    <option value="dca_plus">⚡ DCA+ بيعي — كل أمر بمسافته وكميته ونسبة خروجه (جدول ورسم)</option>
  </select></div>'''),
    ('''    if(!body.symbol||!body.symbol.includes('-')){toast('اكتب الرمز كاملاً مثل XRP-USDT',false);return}
    $('#dn_go').disabled=true;''', '''    if(!body.symbol||!body.symbol.includes('-')){toast('اكتب الرمز كاملاً مثل XRP-USDT',false);return}
    if(body.dca_type==='dca_plus'){const e=plxBad(plxRows());if(e){toast(e,false);return}}      // ⚡ v3.36.57: DCA+
    $('#dn_go').disabled=true;'''),
    ('''  // معاينة أولية
  setTimeout(dcaPreview,200);''', '''  // معاينة أولية
  setTimeout(dcaPreview,200);
  {const bp=$('#dn_bp'),sy=$('#dn_sym');let st=0;                 // ⚡ v3.36.57: DCA+ — السعر والرمز يحدّثان المحرر مباشرة
    if(bp)bp.addEventListener('input',()=>{bp.dataset.man=1;if(($('#dn_type')||{}).value==='dca_plus')plxForm()});
    if(sy)sy.addEventListener('input',()=>{if(($('#dn_type')||{}).value!=='dca_plus')return;clearTimeout(st);st=setTimeout(plxForm,600)})}'''),
    ('''  const t=$('#dn_type').value;
  const buy=t==='dca_buy';
  $('#dn_desc').textContent=buy''', '''  const t=$('#dn_type').value;
  const buy=t==='dca_buy',plus=t==='dca_plus';                    // ⚡ v3.36.57: DCA+ — الحقول الكلاسيكية تختفي والمحرر مكان المعاينة
  ['dn_base','dn_avg','dn_dev','dn_step','dn_size','dn_n','dn_tp'].forEach(id=>{const f=$('#'+id),fl=f&&f.closest('.fld');if(fl)fl.style.display=plus?'none':''});
  if(!plus&&PLX&&PLX.box===$('#dn_preview')){window._plxKeep=plxRows();PLX=null}
  $('#dn_desc').textContent=buy'''),
    ('''  $('#dn_tp_lbl').textContent=buy?'هدف الربح % (فوق المتوسط)':'هدف الربح % (تحت المتوسط)';
  dcaPreview();''', '''  $('#dn_tp_lbl').textContent=buy?'هدف الربح % (فوق المتوسط)':'هدف الربح % (تحت المتوسط)';
  if(plus)$('#dn_desc').textContent='⚡ DCA+: تضع كل أمر بنفسك — مسافته عن الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم. المتوسط مرجّح كالعادي، وحين ينزل السعر إلى خروج أعمق أمر نُفّذ يعيد شراء كل ما باع دفعة واحدة.';
  dcaPreview();'''),
    ('''    take_profit_pct:$('#dn_tp').value,exchange_orders:$('#dn_ex').value,''', '''    take_profit_pct:$('#dn_tp').value,exchange_orders:$('#dn_ex').value,
    ...(($('#dn_type')||{}).value==='dca_plus'?{plus_rows:JSON.stringify(plxRows())}:{}),        // ⚡ v3.36.57: DCA+'''),
    ('''async function dcaPreview(){
  const body=dcaFormBody();''', '''async function dcaPreview(){
  if(($('#dn_type')||{}).value==='dca_plus')return plxForm();      // ⚡ v3.36.57: DCA+ — المحرر يحسب بنفسه (حساب المحرك نفسه)
  const body=dcaFormBody();'''),
    # ── 🧪 the trial path from the form: DCA+ is a sell DCA with its rows
    ('''  const k=kind==='rec'?(body.rec_type||'rec_buy'):kind==='dca'?(body.dca_type||'dca'):''',
     '''  const k=kind==='rec'?(body.rec_type||'rec_buy'):kind==='dca'?(body.dca_type==='dca_buy'?'dca_buy':'dca'):'''),
    # ── the card
    ('''    <span class="dcatag">${b.bot_type==='dca_buy'?'📈 DCA شرائي':'📉 DCA بيعي'}</span>''',
     '''    <span class="dcatag">${b.bot_type==='dca_buy'?'📈 DCA شرائي':(b.dca&&b.dca.plus?'⚡ DCA+ بيعي':'📉 DCA بيعي')}</span>'''),
    ('''    <div class="dcaopts x3"><button class="dcashield" data-k="dtrail">🛡️ الدرع —</button>''',
     '''    <button class="dcaplusb" data-k="dplus" style="display:${b.dca&&b.dca.plus?'':'none'}">✏️ أوامر DCA+ — الجدول والرسم</button>
    <div class="dcaopts x3"><button class="dcashield" data-k="dtrail">🛡️ الدرع —</button>'''),
    ('''  R.dtrail.onclick=()=>dcaShield(botOf(b.dir)||b);''', '''  R.dtrail.onclick=()=>dcaShield(botOf(b.dir)||b);
  R.dplus.onclick=()=>dcaPlusEdit(botOf(b.dir)||b);       // ⚡ v3.36.57: DCA+'''),
    ('''  R.dpause.textContent=d.paused?'▶️ استئناف':'⏸ إيقاف';
}
function dcaViz(el,d,cp){''', '''  R.dpause.textContent=d.paused?'▶️ استئناف':'⏸ إيقاف';
  if(R.dplus){const P=d.plus;R.dplus.style.display=P?'':'none';      // ⚡ v3.36.57: DCA+
    if(P){R.dplus.className='dcaplusb'+(P.err?' bad':(P.pending?' wait':''));
      R.dplus.textContent=P.err?'⚠️ لم يُطبَّق آخر تعديل — اضغط للتفاصيل':(P.pending?'⏳ تعديل الأوامر ينتظر البوت…':`✏️ أوامر DCA+ (${Math.max(0,(P.rows||[]).length-1)} أمر أمان) — الجدول والرسم`);
      R.dplus.title='اضغط لتعديل الأوامر: المسافة والكمية ونسبة الخروج لكل أمر — في الجدول أو على الرسم';
      const t=el.querySelector('.dcatag');if(t&&!/DCA\\+/.test(t.textContent))t.textContent='⚡ DCA+ بيعي'}}
}
function dcaViz(el,d,cp){'''),
    # ── 📋 the card's table: the exit % of each row
    ('''<th>🎯 الخروج<br><small>لو نفّذ</small></th><th>💎 ربح صافي<br><small>لو خرج</small></th></tr></thead><tbody>`;''',
     '''${d.plus?'<th>نسبة<br><small>الخروج</small></th>':''}<th>🎯 الخروج<br><small>لو نفّذ</small></th><th>💎 ربح صافي<br><small>لو خرج</small></th></tr></thead><tbody>`;'''),
    ('''      <td class="num">${f4(r.avg)}</td><td class="num" style="color:var(--green)">${f4(r.tgt)}</td>''',
     '''      <td class="num">${f4(r.avg)}</td>${d.plus?`<td class="num">${r.x!=null?r.x+'%':'—'}</td>`:''}<td class="num" style="color:var(--green)">${f4(r.tgt)}</td>'''),
    # ── ⚙ the details window: the rows instead of the classic settings
    ('''    <div class="dnsec">⚙ الإعدادات</div>
    <table class="dntbl"><tbody>
      <tr><td style="text-align:right">حجم الأمر الأساسي</td><td class="num">${c.base_order_qty||'—'}</td></tr>''', '''    <div class="dnsec">⚙ الإعدادات${d.plus?' — أوامر DCA+':''}</div>
    ${d.plus?dcaPlusRowsTbl(d.plus,base):''}<table class="dntbl"${d.plus?' style="display:none"':''}><tbody>
      <tr><td style="text-align:right">حجم الأمر الأساسي</td><td class="num">${c.base_order_qty||'—'}</td></tr>'''),
    ('''    <p style="font-size:11px;color:var(--mut2);margin-top:10px">الإعدادات تثبت من الإنشاء. لتغييرها، احذف البوت وأنشئ واحداً جديداً بالأرقام الجديدة (لحماية الدورة الجارية).</p>''',
     '''    <p style="font-size:11px;color:var(--mut2);margin-top:10px">${d.plus?'تعدّل أوامر DCA+ والبوت يعمل من زر «✏️ أوامر DCA+» في البطاقة (الجدول والرسم) — المنفّذ في الدورة الجارية يبقى كما هو.':'الإعدادات تثبت من الإنشاء. لتغييرها، احذف البوت وأنشئ واحداً جديداً بالأرقام الجديدة (لحماية الدورة الجارية).'}</p>'''),
    # ── the skins (C · B · OKX): the same button
    ('''    M.chips=[skText(el,'dtrail'),skText(el,'dlast')].filter(Boolean).map((t,i)=>`<span class="chip ${(i===0&&d.trail_on)||(i===1&&d.stop_after)?'gOn':''}">${SKE(t)}</span>`).join('');''',
     '''    M.chips=[skText(el,'dtrail'),skText(el,'dlast')].filter(Boolean).map((t,i)=>`<span class="chip ${(i===0&&d.trail_on)||(i===1&&d.stop_after)?'gOn':''}">${SKE(t)}</span>`).join('')
      +(d.plus?`<span class="chip gOn">${SKE(skText(el,'dplus'))}</span>`:'');'''),
    ('''    M.menu=[ME('🪜 السلم','dladder'),ME(null,'dtrail'),ME(null,'dlast'),''',
     '''    M.menu=[ME('🪜 السلم','dladder'),d.plus?ME('✏️ أوامر DCA+ (الجدول والرسم)','dplus'):null,ME(null,'dtrail'),ME(null,'dlast'),'''),
    # ── 📖 the tutorial
    ('''  rec_buy:{t:'الشراء الدوري',''', TUT + '''  rec_buy:{t:'الشراء الدوري','''),
    ('''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy'],''', '''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy','dca_plus'],'''),
    ('''  const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',''', '''  const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',dca_plus:'⚡','''),
    ('''  dca_last:['🏁 آخر دورة ويخرج',''', '''  dca_plus:['✏️ أوامر DCA+','DCA+ فقط: الجدول والرسم معاً — حرّك أي أمر لم يُنفّذ أو غيّر كميته ونسبة خروجه، أو أضف أوامر واحذفها، ويطبّقها البوت خلال ثوانٍ. المنفّذ في هذه الدورة ثابت بسعره وكميته، وتتغيّر نسبة خروجه فقط.'],
  dca_last:['🏁 آخر دورة ويخرج','''),
    # ── the look
    ('''.dcaopts.x3{grid-template-columns:1fr 1fr auto}''', '''.dcaopts.x3{grid-template-columns:1fr 1fr auto}''' + CSS),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if s.count('APP_VERSION = "3.36.55"') != 1:
        print("❌ APP_VERSION 3.36.55 not found"); sys.exit(1)
    s = s.replace('APP_VERSION = "3.36.55"', 'APP_VERSION = "3.36.57"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · DCA+ editor (table + chart) in the form and on the card · card table · details · skins · tutorial · v3.36.57 · compiles · {p}")
