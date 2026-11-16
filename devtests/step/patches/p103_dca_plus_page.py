# ⚡ patch 103 (dashboard v3.36.59 · DCA+ — the page). The owner (16-11): «Dca + خليه زر بالخارج وضيف معه الشرائية وسويلهم تيست
#   وخليلهم زر شرح».
#   · its own button on the main bar «⚡ DCA+» (next to «📉 نشر DCA») ⇒ the same form opened for DCA+ only: «⚡ DCA+ بيعي» and the new
#     «⚡ DCA+ شرائي» · the classic DCA form keeps the sell and the buy DCA only
#   · the editor (table + chart) works both ways (PLX.buy): the buy ladder goes DOWN from the base (each order under the one before), the
#     exit is ABOVE the average, the profit is in dollars after the same fees as the engine · dragging a line keeps it between its
#     neighbours · a tap UNDER the base adds an order there · the exit handle moves the exit % above the average · the summary says the
#     dollars it needs and the rise it needs · switching sell ⇄ buy in the form keeps the rows
#   · «🧪 جرّب على مسار تجريبي» and «🧪 ديمو» in the same form for both types (the server takes «dca_plus_buy» — patch 102)
#   · «📖 شرح DCA+» beside ✕ with two tabs: DCA+ البيعي and DCA+ الشرائي (idea · steps · an example in numbers · the card's buttons · FAQ)
#   · the card: «⚡ DCA+ شرائي» · ✏️ opens the editor in the buy direction · the details window's rows ▼
#   python3 devtests/step/patches/p103_dca_plus_page.py Holy_Dashboard.pyw
import os, sys

TUT_BUY = r'''  dca_plus_buy:{t:'DCA+ الشرائي',
    idea:['مثل DCA الشرائي: يشتري جزءاً بدولارك ثم يشتري أكثر كلما نزل السعر، وحين يصعد السعر يبيع كل ما اشترى دفعة واحدة — الربح بالدولار.',
          'الفرق: أنت تضع كل أمر بنفسك — مسافته تحت الأمر الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم، بدل معادلة واحدة لكل الأوامر.',
          'نسبة الخروج تخص الأمر نفسه: إن كان أعمق أمر نُفّذ هو أمان 5 فالهدف = المتوسط زائد نسبة خروج أمان 5. فتجعل الأوامر الأولى بربح جيد، والأخيرة الكبيرة بربح صغير فيخرج بسرعة ولا يبقى معلّقاً.'],
    steps:[['الشراء الأولي','شراء الأمر الأساسي بسعر السوق.'],['أوامرك','كل أمر تحت الذي قبله بالمسافة التي وضعتها وبكميته هو.'],['المتوسط','متوسط مرجّح لكل ما اشتُري (كالعادي).'],
           ['الهدف','المتوسط زائد نسبة خروج أعمق أمر نُفّذ — يتغيّر فوراً كلما نُفّذ أمر أعمق.'],['الإغلاق','حين يصعد السعر إلى الهدف يبيع كل ما اشترى دفعة واحدة ⇐ دولار أكثر.'],
           ['✏️ التعديل والبوت يعمل','من زر «✏️ أوامر DCA+» في البطاقة: الأوامر التي لم تُنفّذ تنتقل إلى أسعارها الجديدة خلال ثوانٍ، والمنفّذة تبقى بسعرها وكميتها (تتغيّر نسبة خروجها فقط).']],
    ex:['الأساس 10 عملات عند 1.00$ بخروج 0.5% · أمان 1 تحته بـ1% (0.99$) 10 عملات بخروج 0.6% · أمان 2 تحته بـ2% (0.9702$) 30 عملة بخروج 0.3%.',
        'نُفّذت الثلاثة ⇐ المتوسط نحو 0.9801$ والهدف 0.3% فوقه نحو 0.9830$ — أي صعود نحو 1.3% فقط من آخر سعر شراء. لو كانت نسبة الخروج 1% لاحتاج صعوداً نحو 2%.'],
    btns:['dca_plus','dca_close','dca_trail','dca_last','hist','table','lddr','chart','dca_pause','cset','del'],
    faq:[['هل يبيع كل أمر وحده؟','لا. يبيع كل ما اشترى في الدورة دفعة واحدة عند الهدف — مثل DCA الشرائي العادي. نسبة الخروج تحدد مكان الهدف فقط.'],
         ['كم دولاراً يحتاج؟','مجموع كل أمر × سعره، ويعرضه الجدول قبل التشغيل («💵 الدولار لو نُفّذ الكل»).'],
         ['هل أخسر لو جعلت النسبة صغيرة جداً؟','أقل نسبة يستعملها البوت 0.20% (تغطي العمولتين)، والجدول يعرض الربح الصافي لكل صف قبل التشغيل.'],
         ['ماذا لو عدّلت أمراً والبوت يعمل؟','يلغي أوامره على المنصة التي لم تُنفّذ ويضعها بأسعارها الجديدة خلال ثوانٍ، ولا يمس ما نُفّذ.']]},
'''

R = [
    # ── the main bar: its own button
    ('''      <button class="primary" onclick="openDeployDca()" style="background:linear-gradient(94deg,rgb(var(--amber-rgb)/.9),rgb(var(--amber3-rgb)/.9))">📉 نشر DCA</button>''',
     '''      <button class="primary" onclick="openDeployDca()" style="background:linear-gradient(94deg,rgb(var(--amber-rgb)/.9),rgb(var(--amber3-rgb)/.9))">📉 نشر DCA</button>
      <button class="primary" id="bDcap" onclick="openDeployDca('plus')" title="DCA+: كل أمر بمسافته وكميته ونسبة خروجه — بيعي أو شرائي — بالجدول والرسم" style="background:linear-gradient(94deg,rgb(var(--green-rgb)/.9),rgb(var(--amber-rgb)/.9))">⚡ DCA+</button>'''),
    # ── the form: DCA+ only (sell · buy) from its button · the classic form without DCA+
    ('''async function openDeployDca(){
  let ws=[];try{const s=await api('/api/settings');ws=s.wallets||[]}catch(e){}
  showModal(`<h2 class="tuth" style="color:var(--amber)"><span>📊 نشر بوت DCA</span>${tutX('dca')}</h2>
  <div class="fld"><label>نوع البوت</label><select id="dn_type" onchange="dcaTypeSwitch()">
    <option value="dca">📉 بيعي — يبيع عند الصعود، يجمّع العملة (الربح بالعملة)</option>
    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
    <option value="dca_plus">⚡ DCA+ بيعي — كل أمر بمسافته وكميته ونسبة خروجه (جدول ورسم)</option>
  </select></div>''', '''async function openDeployDca(mode){
  let ws=[];try{const s=await api('/api/settings');ws=s.wallets||[]}catch(e){}
  const PL=mode==='plus';                                          // ⚡ v3.36.59: زر DCA+ مستقل (البيعي والشرائي) — نموذج DCA العادي بلا DCA+
  showModal(`<h2 class="tuth" style="color:${PL?'var(--green)':'var(--amber)'}"><span>${PL?'⚡ نشر بوت DCA+':'📊 نشر بوت DCA'}</span>${tutX(PL?'dcap':'dca')}</h2>
  <div class="fld"><label>نوع البوت</label><select id="dn_type" onchange="dcaTypeSwitch()">
    ${PL?`<option value="dca_plus">⚡ DCA+ بيعي — يبيع عند الصعود ويعيد الشراء (الربح بالعملة)</option>
    <option value="dca_plus_buy">⚡ DCA+ شرائي — يشتري عند النزول ويبيع (الربح بالدولار)</option>`:`<option value="dca">📉 بيعي — يبيع عند الصعود، يجمّع العملة (الربح بالعملة)</option>
    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>`}
  </select></div>'''),
    ('''    if(body.dca_type==='dca_plus'){const e=plxBad(plxRows());if(e){toast(e,false);return}}      // ⚡ v3.36.57: DCA+''',
     '''    if(dcaIsPlus()){const e=plxBad(plxRows());if(e){toast(e,false);return}}      // ⚡ v3.36.57: DCA+ · v3.36.59: والشرائي'''),
    ('''  // معاينة أولية
  setTimeout(dcaPreview,200);
  {const bp=$('#dn_bp'),sy=$('#dn_sym');let st=0;                 // ⚡ v3.36.57: DCA+ — السعر والرمز يحدّثان المحرر مباشرة
    if(bp)bp.addEventListener('input',()=>{bp.dataset.man=1;if(($('#dn_type')||{}).value==='dca_plus')plxForm()});
    if(sy)sy.addEventListener('input',()=>{if(($('#dn_type')||{}).value!=='dca_plus')return;clearTimeout(st);st=setTimeout(plxForm,600)})}''',
     '''  // معاينة أولية
  if(PL)dcaTypeSwitch();else setTimeout(dcaPreview,200);
  {const bp=$('#dn_bp'),sy=$('#dn_sym');let st=0;                 // ⚡ v3.36.57: DCA+ — السعر والرمز يحدّثان المحرر مباشرة
    if(bp)bp.addEventListener('input',()=>{bp.dataset.man=1;if(dcaIsPlus())plxForm()});
    if(sy)sy.addEventListener('input',()=>{if(!dcaIsPlus())return;clearTimeout(st);st=setTimeout(plxForm,600)})}'''),
    ('''function dcaTypeSwitch(){
  const t=$('#dn_type').value;
  const buy=t==='dca_buy',plus=t==='dca_plus';                    // ⚡ v3.36.57: DCA+ — الحقول الكلاسيكية تختفي والمحرر مكان المعاينة
  ['dn_base','dn_avg','dn_dev','dn_step','dn_size','dn_n','dn_tp'].forEach(id=>{const f=$('#'+id),fl=f&&f.closest('.fld');if(fl)fl.style.display=plus?'none':''});
  if(!plus&&PLX&&PLX.box===$('#dn_preview')){window._plxKeep=plxRows();PLX=null}''', '''function dcaIsPlus(){const t=($('#dn_type')||{}).value;return t==='dca_plus'||t==='dca_plus_buy'}   // ⚡ v3.36.59
function dcaTypeSwitch(){
  const t=$('#dn_type').value;
  const plus=t==='dca_plus'||t==='dca_plus_buy',buy=t==='dca_buy'||t==='dca_plus_buy';   // ⚡ DCA+ (البيعي · الشرائي) — الحقول الكلاسيكية تختفي والمحرر مكان المعاينة
  ['dn_base','dn_avg','dn_dev','dn_step','dn_size','dn_n','dn_tp'].forEach(id=>{const f=$('#'+id),fl=f&&f.closest('.fld');if(fl)fl.style.display=plus?'none':''});
  if(PLX&&PLX.box===$('#dn_preview')&&(!plus||PLX.buy!==buy)){window._plxKeep=plxRows();PLX=null}   // البيعي ⇄ الشرائي: الصفوف نفسها باتجاهه'''),
    ('''  if(plus)$('#dn_desc').textContent='⚡ DCA+: تضع كل أمر بنفسك — مسافته عن الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم. المتوسط مرجّح كالعادي، وحين ينزل السعر إلى خروج أعمق أمر نُفّذ يعيد شراء كل ما باع دفعة واحدة.';''',
     '''  if(plus)$('#dn_desc').textContent=buy
    ?'⚡ DCA+ الشرائي: تضع كل أمر بنفسك — مسافته تحت الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم. المتوسط مرجّح كالعادي، وحين يصعد السعر إلى خروج أعمق أمر نُفّذ يبيع كل ما اشترى دفعة واحدة (الربح بالدولار).'
    :'⚡ DCA+ البيعي: تضع كل أمر بنفسك — مسافته فوق الذي قبله وكميته ونسبة خروجه — في الجدول أو على الرسم. المتوسط مرجّح كالعادي، وحين ينزل السعر إلى خروج أعمق أمر نُفّذ يعيد شراء كل ما باع دفعة واحدة (الربح بالعملة).';'''),
    ('''    ...(($('#dn_type')||{}).value==='dca_plus'?{plus_rows:JSON.stringify(plxRows())}:{}),        // ⚡ v3.36.57: DCA+''',
     '''    ...(dcaIsPlus()?{plus_rows:JSON.stringify(plxRows())}:{}),        // ⚡ v3.36.57: DCA+ · v3.36.59: والشرائي'''),
    ('''  if(($('#dn_type')||{}).value==='dca_plus')return plxForm();      // ⚡ v3.36.57: DCA+ — المحرر يحسب بنفسه (حساب المحرك نفسه)''',
     '''  if(dcaIsPlus())return plxForm();      // ⚡ v3.36.57: DCA+ — المحرر يحسب بنفسه (حساب المحرك نفسه)'''),
    # ── 🧪 the trial path from the form: DCA+ الشرائي = the buy kind with its rows
    ('''kind==='dca'?(body.dca_type==='dca_buy'?'dca_buy':'dca'):''', '''kind==='dca'?(body.dca_type==='dca_buy'||body.dca_type==='dca_plus_buy'?'dca_buy':'dca'):'''),
    # ── the editor: both directions (PLX.buy)
    ('''function plxCalc(rows,base,trail){const out=[],fl=trail?PLX_FT:PLX_FM;let p=+base||0,cq=0,cv=0,cn=0;
  rows.forEach((r,i)=>{const d=+r.d||0,q=+r.q||0,x=+r.x||0;if(i)p=p*(1+d/100);const fee=i?fl:PLX_FT;
    cq+=q;cv+=p*q;cn+=p*q*(1-fee);const avg=cq>0?cv/cq:0,xu=Math.max(x,0.2),tgt=avg*(1-xu/100);
    out.push({n:i,p,q,cq,cv,avg,tgt,xu,gap:p>0?(1-tgt/p)*100:0,dev:base>0?(p/base-1)*100:0,prof:tgt>0?cn/tgt*(1-PLX_FT)-cq:0})});
  return out}''', '''function plxCalc(rows,base,trail,buy){const out=[],fl=trail?PLX_FT:PLX_FM;let p=+base||0,cq=0,cv=0,cn=0;   // ⚡ v3.36.59: buy = الشرائي (نزولاً · الخروج فوق · ربح دولار)
  rows.forEach((r,i)=>{const d=+r.d||0,q=+r.q||0,x=+r.x||0;if(i)p=buy?p*(1-d/100):p*(1+d/100);const fee=i?fl:PLX_FT;
    cq+=q;cv+=p*q;cn+=buy?q*(1-fee):p*q*(1-fee);const avg=cq>0?cv/cq:0,xu=Math.max(x,0.2),tgt=buy?avg*(1+xu/100):avg*(1-xu/100);
    out.push({n:i,p,q,cq,cv,avg,tgt,xu,gap:p>0?(buy?tgt/p-1:1-tgt/p)*100:0,dev:base>0?Math.abs(p/base-1)*100:0,
      prof:tgt>0?(buy?cn*tgt*(1-PLX_FT)-cv:cn/tgt*(1-PLX_FT)-cq):0})});
  return out}'''),
    ('''  PLX={box,rows,base:+o.base>0?+o.base:1,locked:new Set((o.locked||[]).map(Number)),sel:rows.length-1,sym:o.sym||'',trail:!!o.trail,cp:+o.cp||0,''',
     '''  PLX={box,rows,base:+o.base>0?+o.base:1,locked:new Set((o.locked||[]).map(Number)),sel:rows.length-1,sym:o.sym||'',trail:!!o.trail,cp:+o.cp||0,buy:!!o.buy,'''),
    ('''     <span class="plxhint">اسحب خط أي أمر للأعلى أو الأسفل لتغيير سعره · اسحب دائرته يميناً أو يساراً لتغيير كميته · اضغط مكاناً فارغاً فوق السعر لإضافة أمر · اختر أمراً ثم اسحب خطه الأخضر 🎯 لتغيير نسبة خروجه</span></div>''',
     '''     <span class="plxhint">اسحب خط أي أمر للأعلى أو الأسفل لتغيير سعره · اسحب دائرته يميناً أو يساراً لتغيير كميته · اضغط مكاناً فارغاً ${o.buy?'تحت':'فوق'} السعر لإضافة أمر · اختر أمراً ثم اسحب خطه الأخضر 🎯 لتغيير نسبة خروجه</span></div>'''),
    ('''   <p class="plxnote">💡 صافٍ بعد عمولة OKX: الأساس آخذ 0.1% · الأوامر صانع 0.08%${o.trail?' (بالدرع آخذ 0.1%)':''} · إعادة الشراء آخذ 0.1%. الهدف = متوسط ما بِيع × (1 − نسبة خروج أعمق أمر نُفّذ)، وعنده يعيد شراء كل ما باع دفعة واحدة. الأرقام على سعر الأساس المعروض — البوت يحسب من سعر التنفيذ الفعلي.</p></div>`;''',
     '''   <p class="plxnote">💡 صافٍ بعد عمولة OKX: الأساس آخذ 0.1% · الأوامر صانع 0.08%${o.trail?' (بالدرع آخذ 0.1%)':''} · ${o.buy?'البيع':'إعادة الشراء'} آخذ 0.1%. ${o.buy?'الهدف = متوسط ما اشتُري × (1 + نسبة خروج أعمق أمر نُفّذ)، وعنده يبيع كل ما اشترى دفعة واحدة':'الهدف = متوسط ما بِيع × (1 − نسبة خروج أعمق أمر نُفّذ)، وعنده يعيد شراء كل ما باع دفعة واحدة'}. الأرقام على سعر الأساس المعروض — البوت يحسب من سعر التنفيذ الفعلي.</p></div>`;'''),
    ('''function plxFull(){const P=PLX;if(!P)return;P.calc=plxCalc(P.rows,P.base,P.trail);''', '''function plxFull(){const P=PLX;if(!P)return;P.calc=plxCalc(P.rows,P.base,P.trail,P.buy);'''),
    ('''function plxTbl(){const P=PLX,lm=plxLockMax(),c=gEsc(P.coin);
  let h=`<div class="plxtbl"><table class="dntbl"><thead><tr><th>الأمر</th><th>المسافة %<br><small>عن الذي قبله</small></th><th>الكمية<br><small>${c}</small></th><th>الخروج %<br><small>لو وصل هنا</small></th>
    <th>السعر</th><th>عن الأساس</th><th>المجموع<br><small>${c}</small></th><th>المتوسط</th><th>🎯 سعر الخروج</th><th>يحتاج نزولاً</th><th>💎 ربح صافٍ<br><small>${c}</small></th><th></th></tr></thead><tbody>`;''',
     '''function plxTbl(){const P=PLX,lm=plxLockMax(),c=gEsc(P.coin);
  let h=`<div class="plxtbl"><table class="dntbl"><thead><tr><th>الأمر</th><th>المسافة %<br><small>${P.buy?'تحت':'فوق'} الذي قبله</small></th><th>الكمية<br><small>${c}</small></th><th>الخروج %<br><small>لو وصل هنا</small></th>
    <th>السعر</th><th>عن الأساس</th><th>المجموع<br><small>${c}</small></th><th>المتوسط</th><th>🎯 سعر الخروج</th><th>${P.buy?'يحتاج صعوداً':'يحتاج نزولاً'}</th><th>💎 ربح صافٍ<br><small>${P.buy?'$':c}</small></th><th></th></tr></thead><tbody>`;'''),
    ('''  P.calc=plxCalc(P.rows,P.base,P.trail);
  const tw=P.q('tw');''', '''  P.calc=plxCalc(P.rows,P.base,P.trail,P.buy);
  const tw=P.q('tw'),up=P.buy?'▼ ':'▲ ',dn=P.buy?'▲ ':'▼ ';'''),
    ('''    set('p',f4(c.p));set('dev',i?'▲ '+c.dev.toFixed(2)+'%':'—');set('cq',plxR(c.cq));set('avg',f4(c.avg));set('tgt',f4(c.tgt));set('gap','▼ '+c.gap.toFixed(2)+'%');''',
     '''    set('p',f4(c.p));set('dev',i?up+c.dev.toFixed(2)+'%':'—');set('cq',plxR(c.cq));set('avg',f4(c.avg));set('tgt',f4(c.tgt));set('gap',dn+c.gap.toFixed(2)+'%');'''),
    ('''function plxSum(){const P=PLX,C=P.calc,L=C[C.length-1]||{},F=C[0]||{},c=gEsc(P.coin),bad=plxBad(P.rows),sg=v=>(v>=0?'+':'')+plxR(v,6);
  const low=P.rows.map((r,i)=>(+r.x>0&&+r.x<0.2)?i:-1).filter(i=>i>=0),neg=C.filter(z=>!(z.prof>0)).map(z=>z.n);
  P.q('sum').innerHTML=`<div class="dnsum">
    <div class="dnstat"><span>🪙 العملات لو نُفّذ الكل</span><b><bdi>${plxR(L.cq||0)} ${c}</bdi></b><small style="display:block;color:var(--mut2);font-size:10px"><bdi>≈ ${(L.cv||0).toFixed(2)}$</bdi></small></div>
    <div class="dnstat"><span>📏 التغطية (مدى الصعود)</span><b style="color:var(--vio)">▲ ${(L.dev||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>🎯 بعد آخر أمر يحتاج نزولاً</span><b style="color:var(--cyan)">▼ ${(L.gap||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — الأساس فقط</span><b style="color:var(--green)">${sg(F.prof||0)} ${c}</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — السلم كاملاً</span><b style="color:var(--green)">${sg(L.prof||0)} ${c}</b></div>''',
     '''function plxSum(){const P=PLX,C=P.calc,L=C[C.length-1]||{},F=C[0]||{},c=gEsc(P.coin),bad=plxBad(P.rows),sg=v=>(v>=0?'+':'')+plxR(v,6),pu=P.buy?'$':c;
  const low=P.rows.map((r,i)=>(+r.x>0&&+r.x<0.2)?i:-1).filter(i=>i>=0),neg=C.filter(z=>!(z.prof>0)).map(z=>z.n);
  P.q('sum').innerHTML=`<div class="dnsum">
    ${P.buy?`<div class="dnstat"><span>💵 الدولار لو نُفّذ الكل</span><b><bdi>${(L.cv||0).toFixed(2)}$</bdi></b><small style="display:block;color:var(--mut2);font-size:10px"><bdi>${plxR(L.cq||0)} ${c}</bdi></small></div>`
    :`<div class="dnstat"><span>🪙 العملات لو نُفّذ الكل</span><b><bdi>${plxR(L.cq||0)} ${c}</bdi></b><small style="display:block;color:var(--mut2);font-size:10px"><bdi>≈ ${(L.cv||0).toFixed(2)}$</bdi></small></div>`}
    <div class="dnstat"><span>📏 التغطية (مدى ${P.buy?'النزول':'الصعود'})</span><b style="color:var(--vio)">${P.buy?'▼':'▲'} ${(L.dev||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>🎯 بعد آخر أمر يحتاج ${P.buy?'صعوداً':'نزولاً'}</span><b style="color:var(--cyan)">${P.buy?'▲':'▼'} ${(L.gap||0).toFixed(2)}%</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — الأساس فقط</span><b style="color:var(--green)">${sg(F.prof||0)} ${pu}</b></div>
    <div class="dnstat"><span>💎 ربح صافٍ — السلم كاملاً</span><b style="color:var(--green)">${sg(L.prof||0)} ${pu}</b></div>'''),
    ('''  if(P.locked.size)w+=`<p class="plxnote">✅ = نُفّذ في هذه الدورة: سعره وكميته ثابتان، ونسبة خروجه تتغيّر. الإضافة والحذف فوق آخر أمر نُفّذ.</p>`;''',
     '''  if(P.locked.size)w+=`<p class="plxnote">✅ = نُفّذ في هذه الدورة: سعره وكميته ثابتان، ونسبة خروجه تتغيّر. الإضافة والحذف ${P.buy?'تحت':'فوق'} آخر أمر نُفّذ.</p>`;'''),
    ('''    lo=Math.min(...ps);hi=Math.max(...ps);const pd=(hi-lo)*0.05||hi*0.01,mp=Math.max(...C.map(c=>c.p));lo-=pd;hi=Math.max(hi+pd*2.5,mp*1.03);P.lo=lo;P.hi=hi}   // مكان فوق آخر أمر لإضافة أوامر بالضغط''',
     '''    lo=Math.min(...ps);hi=Math.max(...ps);const pd=(hi-lo)*0.05||hi*0.01,mp=Math.max(...C.map(c=>c.p)),np=Math.min(...C.map(c=>c.p));
    if(P.buy){hi+=pd;lo=Math.min(lo-pd*2.5,np*0.97)}else{lo-=pd;hi=Math.max(hi+pd*2.5,mp*1.03)}P.lo=lo;P.hi=hi}   // مكان بعد آخر أمر لإضافة أوامر بالضغط (فوق البيعي · تحت الشرائي)'''),
    ('''    g+=`<rect x="${XC}" y="${yt}" width="${XR-XC}" height="${Math.max(0,H-pb-yt)}" fill="rgb(var(--green-rgb)/.07)"/>`;''',
     '''    g+=P.buy?`<rect x="${XC}" y="${pt}" width="${XR-XC}" height="${Math.max(0,yt-pt)}" fill="rgb(var(--green-rgb)/.07)"/>`
      :`<rect x="${XC}" y="${yt}" width="${XR-XC}" height="${Math.max(0,H-pb-yt)}" fill="rgb(var(--green-rgb)/.07)"/>`;'''),
    ('''fill="var(--green)" font-weight="700">${plxR(+P.rows[s.n].x,3)}% → ${f4(s.tgt)} · ▼${s.gap.toFixed(2)}%</text>`;''',
     '''fill="var(--green)" font-weight="700">${plxR(+P.rows[s.n].x,3)}% → ${f4(s.tgt)} · ${P.buy?'▲':'▼'}${s.gap.toFixed(2)}%</text>`;'''),
    ('''function plxSetP(i,pr){const P=PLX,C=P.calc;if(i<1||P.locked.has(i)||!C[i]||!(pr>0))return;
  const lo=C[i-1].p*1.0001,hi=i+1<C.length?C[i+1].p/1.0001:C[i-1].p*1.5;pr=Math.min(Math.max(pr,lo),hi);
  P.rows[i].d=+((pr/C[i-1].p-1)*100).toFixed(4);
  if(i+1<C.length&&!P.locked.has(i+1))P.rows[i+1].d=+((C[i+1].p/pr-1)*100).toFixed(4)}   // التي بعده تبقى مكانها''',
     '''function plxDd(a,b){return PLX&&PLX.buy?(1-b/a)*100:(b/a-1)*100}   // ⚡ v3.36.59: مسافة الأمر b عن الذي قبله a (الشرائي: تحته)
function plxSetP(i,pr){const P=PLX,C=P.calc;if(i<1||P.locked.has(i)||!C[i]||!(pr>0))return;
  const lo=P.buy?(i+1<C.length?C[i+1].p*1.0001:C[i-1].p*0.5):C[i-1].p*1.0001,hi=P.buy?C[i-1].p/1.0001:(i+1<C.length?C[i+1].p/1.0001:C[i-1].p*1.5);
  pr=Math.min(Math.max(pr,lo),hi);
  P.rows[i].d=+plxDd(C[i-1].p,pr).toFixed(4);
  if(i+1<C.length&&!P.locked.has(i+1))P.rows[i+1].d=+plxDd(pr,C[i+1].p).toFixed(4)}   // التي بعده تبقى مكانها'''),
    ('''  else if(d.k==='x'){const c=P.calc[d.i];if(c&&c.avg>0)P.rows[d.i].x=+Math.min(50,Math.max(0.2,(1-P.P(y)/c.avg)*100)).toFixed(2)}''',
     '''  else if(d.k==='x'){const c=P.calc[d.i];if(c&&c.avg>0)P.rows[d.i].x=+Math.min(50,Math.max(0.2,(P.buy?P.P(y)/c.avg-1:1-P.P(y)/c.avg)*100)).toFixed(2)}'''),
    ('''  let k=C.findIndex(c=>c.p>pr);if(k<0)k=C.length;
  if(k<1){toast('أوامر البيعي فوق سعر الأساس — اضغط فوقه',false);plxSoft();return}
  if(k<=lm){toast('أضف الأوامر فوق آخر أمر نُفّذ',false);plxSoft();return}
  const d=(pr/C[k-1].p-1)*100;if(!(d>0.01&&d<=50)){toast('المسافة عن الأمر الذي قبله بين 0 و50%',false);plxSoft();return}
  const tpl=P.rows[k-1];
  if(k<C.length)P.rows[k].d=+((C[k].p/pr-1)*100).toFixed(4);''', '''  let k=C.findIndex(c=>P.buy?c.p<pr:c.p>pr);if(k<0)k=C.length;
  if(k<1){toast(P.buy?'أوامر الشرائي تحت سعر الأساس — اضغط تحته':'أوامر البيعي فوق سعر الأساس — اضغط فوقه',false);plxSoft();return}
  if(k<=lm){toast(P.buy?'أضف الأوامر تحت آخر أمر نُفّذ':'أضف الأوامر فوق آخر أمر نُفّذ',false);plxSoft();return}
  const d=plxDd(C[k-1].p,pr);if(!(d>0.01&&d<=50)){toast('المسافة عن الأمر الذي قبله بين 0 و50%',false);plxSoft();return}
  const tpl=P.rows[k-1];
  if(k<C.length)P.rows[k].d=+plxDd(pr,C[k].p).toFixed(4);'''),
    ('''  if(i+1<P.rows.length&&C[i+1]&&C[i-1])P.rows[i+1].d=+((C[i+1].p/C[i-1].p-1)*100).toFixed(4);   // التي بعده تبقى مكانها''',
     '''  if(i+1<P.rows.length&&C[i+1]&&C[i-1])P.rows[i+1].d=+plxDd(C[i-1].p,C[i+1].p).toFixed(4);   // التي بعده تبقى مكانها'''),
    ('''  S('info').innerHTML=`المتوسط <bdi>${f4(c.avg)}</bdi> · 🎯 الخروج <bdi>${f4(c.tgt)}</bdi> · يحتاج نزولاً <bdi>${c.gap.toFixed(2)}%</bdi> · 💎 <bdi>${(c.prof>=0?'+':'')+plxR(c.prof,6)} ${gEsc(P.coin)}</bdi>`}''',
     '''  S('info').innerHTML=`المتوسط <bdi>${f4(c.avg)}</bdi> · 🎯 الخروج <bdi>${f4(c.tgt)}</bdi> · يحتاج ${P.buy?'صعوداً':'نزولاً'} <bdi>${c.gap.toFixed(2)}%</bdi> · 💎 <bdi>${(c.prof>=0?'+':'')+plxR(c.prof,6)} ${P.buy?'$':gEsc(P.coin)}</bdi>`}'''),
    ('''function plxForm(){const box=$('#dn_preview');if(!box)return;
  const sym=($('#dn_sym').value||'').trim().toUpperCase(),bp=plxN($('#dn_bp').value),tr=!!($('#dn_trail')||{}).checked;
  if(!PLX||PLX.box!==box||!box.querySelector('.plx')){
    plxOpen(box,{rows:window._plxKeep||null,base:bp>0?bp:1,sym,trail:tr,mode:'new'});''', '''function plxForm(){const box=$('#dn_preview');if(!box)return;
  const sym=($('#dn_sym').value||'').trim().toUpperCase(),bp=plxN($('#dn_bp').value),tr=!!($('#dn_trail')||{}).checked,buy=($('#dn_type')||{}).value==='dca_plus_buy';
  if(PLX&&PLX.box===box&&PLX.buy!==buy){window._plxKeep=plxRows();PLX=null}
  if(!PLX||PLX.box!==box||!box.querySelector('.plx')){
    plxOpen(box,{rows:window._plxKeep||null,base:bp>0?bp:1,sym,trail:tr,mode:'new',buy});'''),
    ('''  showModal(`<h2 style="color:var(--green)">✏️ أوامر DCA+ — ${gEsc(b.symbol)}</h2>''', '''  const buy=b.bot_type==='dca_buy'||!!d.is_buy;                     // ⚡ v3.36.59: DCA+ الشرائي
  showModal(`<h2 style="color:var(--green)">✏️ أوامر DCA+ ${buy?'الشرائي':'البيعي'} — ${gEsc(b.symbol)}</h2>'''),
    ('''  plxOpen($('#plx_edit'),{rows:P.rows,base:base||1,locked:live?P.locked:[],sym:b.symbol,trail:d.trail_on,cp,mode:'edit'});''',
     '''  plxOpen($('#plx_edit'),{rows:P.rows,base:base||1,locked:live?P.locked:[],sym:b.symbol,trail:d.trail_on,cp,mode:'edit',buy});'''),
    ('''function dcaPlusRowsTbl(P,base){return `<table class="dntbl" style="margin-bottom:10px"><thead><tr><th>الأمر</th><th>المسافة<br><small>عن الذي قبله</small></th><th>الكمية ${gEsc(base)}</th><th>نسبة الخروج</th></tr></thead><tbody>${(P.rows||[]).map((r,i)=>
  `<tr><td>${(P.locked||[]).includes(i)?'✅ ':''}${i?'أمان '+i:'الأساسي'}</td><td class="num">${i?'▲ '+r.d+'%':'—'}</td>''',
     '''function dcaPlusRowsTbl(P,base,buy){return `<table class="dntbl" style="margin-bottom:10px"><thead><tr><th>الأمر</th><th>المسافة<br><small>${buy?'تحت':'فوق'} الذي قبله</small></th><th>الكمية ${gEsc(base)}</th><th>نسبة الخروج</th></tr></thead><tbody>${(P.rows||[]).map((r,i)=>
  `<tr><td>${(P.locked||[]).includes(i)?'✅ ':''}${i?'أمان '+i:'الأساسي'}</td><td class="num">${i?(buy?'▼ ':'▲ ')+r.d+'%':'—'}</td>'''),
    ('''    ${d.plus?dcaPlusRowsTbl(d.plus,base):''}''', '''    ${d.plus?dcaPlusRowsTbl(d.plus,base,d.is_buy):''}'''),
    # ── the card
    ('''    <span class="dcatag">${b.bot_type==='dca_buy'?'📈 DCA شرائي':(b.dca&&b.dca.plus?'⚡ DCA+ بيعي':'📉 DCA بيعي')}</span>''',
     '''    <span class="dcatag">${b.bot_type==='dca_buy'?(b.dca&&b.dca.plus?'⚡ DCA+ شرائي':'📈 DCA شرائي'):(b.dca&&b.dca.plus?'⚡ DCA+ بيعي':'📉 DCA بيعي')}</span>'''),
    ('''      const t=el.querySelector('.dcatag');if(t&&!/DCA\\+/.test(t.textContent))t.textContent='⚡ DCA+ بيعي'}}''',
     '''      const t=el.querySelector('.dcatag'),tl=d.is_buy?'⚡ DCA+ شرائي':'⚡ DCA+ بيعي';if(t&&t.textContent!==tl)t.textContent=tl}}'''),
    # ── 📖 the tutorial: its own button and set (two tabs)
    ('''  rec_buy:{t:'الشراء الدوري',''', TUT_BUY + '''  rec_buy:{t:'الشراء الدوري','''),
    ('''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy','dca_plus'],''',
     '''const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy'],dcap:['dca_plus','dca_plus_buy'],'''),
    ('''const TUT_SEL={grid:'#n_gtype',dca:'#dn_type',rec:'#rd_type'};''', '''const TUT_SEL={grid:'#n_gtype',dca:'#dn_type',dcap:'#dn_type',rec:'#rd_type'};'''),
    ('''const TUT_LBL={grid:'شرح الشبكي',dca:'شرح DCA',''', '''const TUT_LBL={grid:'شرح الشبكي',dca:'شرح DCA',dcap:'شرح DCA+','''),
    ('''dca_buy:'📈',dca:'📉',dca_plus:'⚡',''', '''dca_buy:'📈',dca:'📉',dca_plus:'⚡',dca_plus_buy:'⚡','''),
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
    print(f"✅ {len(R)} replacements · ⚡ DCA+ button (sell · buy) · the editor both ways · trial · demo · tutorial · the card · compiles · {p}")
