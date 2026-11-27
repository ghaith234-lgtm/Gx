# p151 — v3.36.79 🔀 «شبكة عملتين» · ⑥ the page: the deploy button, the form with its calculator, the 📖 guide
#   · «🔀 شبكة عملتين» beside the other deploy buttons · the form: the main coin (XRP by default — the owner: «الخزنة العملة الرئيسية انا
#     اختارها») · the other coin · the step % · the main coin per buy (like ♾️'s dollars per buy) · how much main coin for the buys below ·
#     how much of the other coin for the sells above (from the wallet — nothing is bought at the deploy) · the start ratio (optional) ·
#     where the profit goes (the main coin by default · the other · half) · the wallet
#   · 📋 the table before the deploy = /api/pair_plan (calculation only — the engine's own formula): every level with its buy and sell
#     ratio · the cycle profit after the FOUR fees and the spread · the worst capped price · the smallest step that profits · what each
#     coin needs · refusals in red
#   · 📖 TUT.grid_pair (idea · steps · a worked example · the card's buttons · questions) — formal Arabic like every customer text
#   python3 devtests/step/patches/p151_pair_form.py Holy_Dashboard.pyw
import os, sys

JS = r'''let _paT=0,_paSeq=0;
async function openDeployPair(pre){pre=pre||{};      // 🔀 v3.36.79: «شبكة عملتين»
  let ws=[];try{const s=await api('/api/settings');ws=s.wallets||[]}catch(e){}
  const v=(k,d)=>pre[k]!=null&&pre[k]!==''?pre[k]:d;
  showModal(`<h2 class="tuth" style="color:var(--blue)"><span>🔀 نشر «شبكة عملتين»</span>${tutX('pair')}</h2>
  <p class="sthelp">عملة <b>رئيسية</b> (مثل XRP) تؤدي دور الدولار، وعملة <b>ثانية</b> (مثل SOL) تُتداول على سعرها محسوباً بالرئيسية — كم XRP يساوي SOL واحد. كل شراء تحت يدفع <b>الكمية نفسها من الرئيسية</b>، وبيعته فوقه بالخطوة نفسها تعيدها <b>مع الربح</b>. البيعات فوق نسبة البداية من عملاتك الثانية الموجودة في المحفظة — لا يُشترى شيء عند النشر. التحويل عبر الدولار لحظي بأمرين فوريين، ولا تبقى أوامر على المنصة: البوت يراقب النسبة كل ثانيتين.</p>
  <div class="frm">
    <div class="fld"><label title="العملة التي تؤدي دور الدولار — الربح يُحسب بها">🏦 العملة الرئيسية (مثل XRP)</label><input id="pa_main" style="text-transform:uppercase" value="${gEsc(String(v('main','XRP')))}" oninput="paPreview()"></div>
    <div class="fld"><label title="العملة التي تُتداول على سعرها بالرئيسية">🔁 العملة الثانية (مثل SOL)</label><input id="pa_oth" style="text-transform:uppercase" placeholder="SOL" value="${gEsc(String(v('other','')))}" oninput="paPreview()"></div>
    <div class="fld"><label title="المسافة بين مستوى وآخر — والبيعة فوق شرائها بالمسافة نفسها">📏 الخطوة (%)</label><input id="pa_g" class="num" value="${v('step_pct',2)}" oninput="paPreview()"></div>
    <div class="fld"><label title="مثل «دولار كل شراء» في الشبكة اللانهائية: كل شراء يدفع هذه الكمية من الرئيسية">💰 كمية كل شراء (بالرئيسية)</label><input id="pa_mv" class="num" value="${v('main_value',20)}" oninput="paPreview()"></div>
    <div class="fld"><label title="كمية الرئيسية التي تخصّصها للشراءات تحت نسبة البداية — عدد المستويات = الكمية ÷ كمية كل شراء">⬇️ كمية الرئيسية للشراءات تحت</label><input id="pa_am" class="num" value="${v('main_amount','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="كمية الثانية من محفظتك للبيعات فوق نسبة البداية — كل مستوى يبيع ما يساوي كمية شراء بنسبته">⬆️ كمية الثانية للبيعات فوق (من محفظتك)</label><input id="pa_ao" class="num" value="${v('other_amount','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="فارغ = النسبة لحظة النشر">🎯 نسبة البداية (اختياري)</label><input id="pa_r0" class="num" value="${+v('forced_ratio',0)||''}" oninput="paPreview()"></div>
    <div class="fld"><label title="الافتراضي: الربح كله يعود بالرئيسية">💎 الربح يذهب إلى</label><select id="pa_pt" onchange="paPreview()"><option value="main">العملة الرئيسية</option><option value="other">العملة الثانية</option><option value="half">نصفان</option></select></div>
    <div class="fld"><label>المحفظة</label><select id="pa_wallet">${ws.map(w=>`<option>${gEsc(w.name)}</option>`).join('')||'<option value="">— أضف محفظة أولاً —</option>'}</select></div>
  </div>
  <div class="cklist" style="margin-top:10px"><label class="ck"><input type="checkbox" id="pa_auto" checked>🤖 يشمله الحارس</label></div>
  <div class="dnsec" style="margin-top:12px">📋 الجدول قبل النشر — كل مستوى بنسبة شرائه وبيعه، وربح الدورة صافياً بعد العمولات الأربع</div>
  <div id="pa_plan"><div class="vach0">…</div></div>
  <div class="mbtns" style="margin-top:14px"><button class="primary" id="pa_go" style="background:linear-gradient(94deg,var(--green),rgb(var(--green-rgb)/.8))">🚀 انشر وشغّل</button><button onclick="hideModal()">إلغاء</button></div>`);
  const pt=$('#pa_pt');if(pt)pt.value=['main','other','half'].includes(pre.profit_to)?pre.profit_to:'main';
  $('#pa_go').onclick=async()=>{const body=paBody();
    if(!body.other){toast('اكتب رمز العملة الثانية مثل SOL',false);return}
    $('#pa_go').disabled=true;
    try{const r=await api('/api/deploy_pair',body);toast(r.msg,r.ok);if(r.ok){hideModal();tick()}}
    finally{const g=$('#pa_go');if(g)g.disabled=false}};
  paPreview()}
function paBody(){const g=k=>(($('#'+k)||{}).value||'').trim();
  return {main:g('pa_main').toUpperCase(),other:g('pa_oth').toUpperCase(),step_pct:g('pa_g'),main_value:g('pa_mv'),main_amount:g('pa_am'),
    other_amount:g('pa_ao'),forced_ratio:g('pa_r0'),profit_to:g('pa_pt')||'main',wallet:g('pa_wallet'),auto:!!($('#pa_auto')||{}).checked}}
function paPreview(){clearTimeout(_paT);_paT=setTimeout(paPlan,350)}
async function paPlan(){const box=$('#pa_plan');if(!box)return;const b=paBody();
  if(!b.other||!b.main){box.innerHTML='<div class="vach0">اكتب رمزي العملتين لعرض الجدول</div>';return}
  const my=++_paSeq;let P=null;try{P=await api('/api/pair_plan',b,true)}catch(e){}
  if(my!==_paSeq||!$('#pa_plan'))return;
  box.innerHTML=paPlanHtml(P)}
function paPlanHtml(P){
  if(!P||!P.ok)return `<div class="sterr">❌ ${gEsc((P&&P.msg)||'تعذّر الحساب')}</div>`;
  const A=P.a||{},M=gEsc(A.main||''),O=gEsc(A.other||''),pc=x=>((+x||0)*100).toFixed(2)+'%';
  let h='';
  (P.err||[]).forEach(e=>h+=`<div class="sterr">⛔ ${gEsc(e)}</div>`);
  h+=`<div class="stsum">
   <span>⚖️ الآن: 1 ${O} = <b dir="ltr">${stN(P.r_now)}</b> ${M}</span><span>🎯 البداية <b dir="ltr">${stN(P.r0)}</b></span>
   <span>⬇️ ${P.dn} شراء تحت حتى <b dir="ltr">${stN(P.lo)}</b> — يحتاج <b dir="ltr">${stN(P.main_need)}</b> ${M}</span>
   <span>⬆️ ${P.up} بيع فوق حتى <b dir="ltr">${stN(P.hi)}</b> — من عملاتك <b dir="ltr">${stN(P.other_need)}</b> ${O}</span>
   <span>💎 ربح كل دورة صافياً (العمولات الأربع ${pc(P.fee)} لكل أمر وفرق السعر) <b dir="ltr">${stN(P.cycle_main)}</b> ${M} ≈ <b>${vaD(P.cycle_usd)}$</b></span>
   <span>🛡️ حتى بأسوأ سعر يسمح به سقف الأمر: <b dir="ltr">${stN(P.worst_main)}</b> ${M} · أقل خطوة تربح ≈ ${pc(P.min_step)}</span>
   <span>💵 قيمة كل أمر ≈ ${vaD(P.usd_order)}$ · التحويل عبر الدولار لحظي — لا أوامر تبقى على المنصة</span>
   ${(+P.main_left>0||+P.other_left>0)?`<span>ℹ️ يبقى خارج البوت: <b dir="ltr">${stN(P.main_left)}</b> ${M} · <b dir="ltr">${stN(P.other_left)}</b> ${O}</span>`:''}</div>`;
  h+=`<div class="stwrap"><table class="sttab"><thead><tr><th>المستوى</th><th>الجهة</th><th>نسبة الشراء</th><th>نسبة البيع</th><th>الكمية</th></tr></thead><tbody>`;
  (P.rows||[]).forEach(r=>{h+=`<tr class="${r.side==='sell'?'stinv':''}${r.j===0?' st0':''}" data-j="${r.j}"><td>${r.j}</td><td>${r.side==='sell'?'بيع من عملاتك':'شراء'}</td>`
    +`<td dir="ltr">${stN(r.bp)}</td><td dir="ltr">${stN(r.sp)}</td><td dir="ltr">${r.side==='sell'?stN(r.q)+' '+O:stN(r.main)+' '+M}</td></tr>`});
  if((+P.n_rows||0)>(P.rows||[]).length)h+=`<tr><td colspan="5">… و${(+P.n_rows)-(P.rows||[]).length} مستوى آخر</td></tr>`;
  h+='</tbody></table></div>';
  return h}
'''

TUT = r'''  grid_pair:{t:'شبكة عملتين',
    idea:['عملة رئيسية (مثل XRP) تؤدي دور الدولار، وعملة ثانية (مثل SOL) تُتداول على سعرها محسوباً بالرئيسية — النسبة: كم XRP يساوي SOL واحد.',
          'كلما رخصت الثانية مقابل الرئيسية خطوةً اشترى منها بكمية ثابتة من الرئيسية، وكلما غلت خطوةً باع ما اشتراه وأعاد الرئيسية مع الربح — مثل الشبكة اللانهائية، لكن «الدولار» هنا عملة.',
          'لا تبقى أوامر على المنصة: البوت يراقب النسبة كل ثانيتين، وحين تصل إلى المستوى يبيع ويشتري عبر الدولار في اللحظة نفسها بأمرين فوريين.'],
    steps:[['المستويات','من نسبة البداية: كل مستوى أعلى أو أدنى بالخطوة نفسها.'],['الشراء','تنزل النسبة إلى مستوى ⇐ يبيع كمية الرئيسية الثابتة بالدولار ويشتري بها الثانية فوراً.'],
           ['البيع','تصعد النسبة خطوةً فوق شرائه ⇐ يبيع ما اشتراه ويشتري الرئيسية — ولا يبيع إلا بربح بعد العمولات الأربع حتى بأسوأ سعر يسمح به سقف الأمر.'],
           ['فوق البداية','مستويات تبيع من عملاتك الثانية الموجودة في المحفظة كأنها اشتُريت بنسبة مستواها.'],
           ['الدولار المحجوز','الدولار بين الرجلين ملك البوت حتى يُصرف — لا يحسبه أي بوت آخر حراً، وإن رُفض الرجل الثاني يعيد المحاولة حتى يكمل.'],
           ['الإيقاف','⏸ إيقاف الشراء أو البيع من النسبة الحالية، والاستئناف يكمل من حيث وصلت النسبة.']],
    ex:['XRP رئيسية وSOL ثانية، والنسبة 75 (SOL واحد = 75 XRP)، والخطوة 2%، وكل شراء 20 XRP.',
        'نزلت النسبة إلى 73.53 ⇐ باع 20 XRP بالدولار واشترى بها نحو 0.272 SOL في اللحظة نفسها.',
        'عادت النسبة إلى 75 ⇐ باع 0.272 SOL واشترى نحو 20.30 XRP ⇐ ربح الدورة نحو 0.30 XRP بعد العمولات الأربع وفرق السعر، ويعود المستوى إلى الشراء.'],
    btns:['pw','ab','as','hist','cset','del'],
    faq:[['لماذا الربح بالرئيسية لا بالدولار؟','لأن الرئيسية هي «الدولار» هنا: كل دورة تعيدها أكثر. ويمكنك عند النشر أن تجعل الربح في الثانية أو نصفين.'],
         ['هل يحمي من نزول السوق كله؟','لا — العملتان تتحركان مع السوق. البوت يزيد عدد العملة الرئيسية من تذبذب النسبة بين العملتين.'],
         ['لماذا لا أوامر على المنصة؟','لا يوجد في المنصة زوج يسعّر الثانية بالرئيسية مباشرة؛ لذلك يحفظ البوت الأمرين التاليين ويراقب، ثم ينفذ الرجلين لحظياً.'],
         ['ماذا لو قفز السعر بين الرجلين؟','كل رجل أمر فوري بسقف سعر؛ وإن كان إكمال البيعة سيؤدي إلى خسارة ينتظر سعراً لا يخسر حتى عشر دقائق.'],
         ['هل أشغّل أكثر من بوت على الزوج نفسه؟','لا — بوت واحد لكل زوج حتى لا تتداخل مستوياته. ويمكن تشغيل أزواج أخرى بالرئيسية نفسها.']]},
'''

R = [
    ('''      <button onclick="accEdit()" style=''',
     '''      <button class="primary" onclick="openDeployPair()" title="شبكة عملتين: عملة رئيسية تؤدي دور الدولار وعملة ثانية تُتداول على سعرها بالرئيسية — الربح بالرئيسية · بلا أوامر على المنصة" style="background:linear-gradient(94deg,rgb(var(--blue-rgb)/.9),rgb(var(--vio-rgb)/.85))">🔀 شبكة عملتين</button>
      <button onclick="accEdit()" style='''),
    ('''  dca_buy:{t:'DCA الشرائي',''', TUT + '''  dca_buy:{t:'DCA الشرائي','''),
    ("""step:'شرح المتدرج',""", """step:'شرح المتدرج',pair:'شرح شبكة عملتين',"""),
    ("""step:['grid_step'],""", """step:['grid_step'],pair:['grid_pair'],"""),
    ("""const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',""", """const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',grid_pair:'🔀',"""),
    ('''async function openDeploy(pre){pre=pre||{};''', JS + '''async function openDeploy(pre){pre=pre||{};'''),
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
    print(f"✅ {len(R)} replacements · 🔀 the deploy button · the form and its calculator · the 📖 guide · {p}")
