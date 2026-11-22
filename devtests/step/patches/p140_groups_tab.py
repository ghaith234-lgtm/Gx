# p140 — v3.36.77 🧩 the «📋 المؤشرات» tab rebuilt as groups · ⚙️ notices in two sections with each group's record · 🔮 the coin's group calls
#   The owner (21-11): «خانه المؤشرات فيها خانتين للعملات وللسوق اذا دخلنا مثلا للعملات انشوف عملة بداخلها مجاميع كل مجموعه مختصه بشيء
#   ونسبتها ، وخانة الاشعارات بيها النسبة واختيار نوع للاشعار كل اشعار مربوط بمجموعته»
#   · 📋: two sub-tabs 🪙 العملات (all coins together or one coin of yours) and 🌐 السوق · a card per group: its job · its record on ⏱ 🕓 📅
#     (what would have been sent vs the usual — on the chosen coin, or all coins together) · 🔔 what fired now · ⭐ its champions · tap ⇒ every
#     member (indicators + combos 🤝) per frame with % · count · usual · days · state (⭐ / ✅ / 🧪 / —) and its record on the chosen coin
#   · ⚙️: 🔴 urgent · 🪙 the coin groups (with ⏱ 🕓 📅 %) · 🪙 the coin facts · 🌐 the market groups · 🌐 the market facts — 📲/👁/⛔ each
#   · 🔮: «🧩» lines (the coin's groups whose champions fired now, per frame, with the member's record) instead of the 🎯 tendency
#   · the old tables' page code (sbLoad · sbTable · sbRow · …) and their CSS go
#   python3 devtests/step/patches/p140_groups_tab.py Holy_Dashboard.pyw
import sys, os, re

R = [
    ("async function sgLoad(){clearTimeout(SGT);try{SGV=await api('/api/signals')}catch(e){SGV=null}sgRender();anLoad();if(SGTAB==='ind'){if(!INDV)sgIndLoad();if(!SBV)sbLoad()}",
     "async function sgLoad(){clearTimeout(SGT);try{SGV=await api('/api/signals')}catch(e){SGV=null}sgRender();anLoad();if(SGTAB==='ind'){if(!INDV)sgIndLoad();if(!GPV)gpLoad()}"),
    ("if(SGTAB==='ind'){sgIndLoad();sbLoad()}}", "if(SGTAB==='ind'){sgIndLoad();gpLoad()}}"),
    ("  return h+sbTable(V)}", "  return h+gpTab(V)}"),
    ("function sgInd(V){let h='';const B=V.busy||{};                                  // 🎯 v3.36.71 · 📋 v3.36.73: الجداول (السوق · كل عملة)",
     "function sgInd(V){let h='';const B=V.busy||{};                                  // 🎯 v3.36.71 · 🧩 v3.36.77: المجاميع (العملات · السوق)"),
    # ⚙️
    ("  const row=([k,x])=>{const cur=A[k]||x[3];return `<div class=\"an-ty\" data-k=\"${k}\"><span>${x[0]} ${gEsc(x[1])}</span>",
     "  const gr=k=>{const R=(V.gpr||{})[k];if(!R)return '';return ` <small class=\"gp-rc\">${['1H','4H','1D'].map(f=>{const r=R[f],F=(V.frs||{})[f]||['',''];return `${F[0]} ${r&&r[1]?Math.round(100*r[0]/r[1])+'%':'—'}`}).join(' · ')}</small>`};\n"
     "  const row=([k,x])=>{const cur=A[k]||x[3];return `<div class=\"an-ty\" data-k=\"${k}\"><span>${x[0]} ${gEsc(x[1])}${gr(k)}</span>"),
    ("    <div class=\"sg-set\">${grp('urgent','🔴 طوارئ — تصل فوراً حتى في ساعات الهدوء')}${grp('coin','🪙 عملاتك')}${grp('mkt','🌐 السوق كله')}\n"
     "      <div class=\"ind-sub\">📲 فوري: يصلك على تيليغرام والتطبيق · 👁 بالنافذة: في 📜 السجل فقط · ⛔ متوقف — بطاقة واحدة لكل عملة (التالية بعد 6 ساعات إلا إذا انقلب اتجاهها) · الحد 12 بطاقة في اليوم والطارئ خارجه · لا توقّع اتجاه ولا أوامر</div></div>",
     "    <div class=\"sg-set\">${grp('urgent','🔴 طوارئ — تصل فوراً حتى في ساعات الهدوء')}${grp('gcoin','🪙 العملة — المجاميع (كل مجموعة تتنبأ بشغلها · النسبة سجلها على التاريخ لكل إطار)')}${grp('coin','🪙 العملة — حقائق الآن')}${grp('gmkt','🌐 السوق — المجاميع (محكومة بسعر البيتكوين)')}${grp('mkt','🌐 السوق — حقائق الآن')}\n"
     "      <div class=\"ind-sub\">📲 فوري: يصلك على تيليغرام والتطبيق · 👁 بالنافذة: في 📜 السجل فقط · ⛔ متوقف — إشعار المجموعة يصل فوراً فقط إذا كان سجلها نفسه أعلى من العادي بـ3% على 30 مرة فأكثر، وإلا يبقى بالنافذة · بطاقة واحدة لكل عملة (التالية بعد 6 ساعات إلا إذا انقلب اتجاهها) · الحد 12 بطاقة في اليوم والطارئ خارجه · احتمالات لا ضمانات · لا أوامر</div></div>"),
    # 🔮
    ("  let h=sgFcTop(V.sig)+fcTdTop()+`<div class=\"ind-top\">", "  let h=sgFcTop(V.sig)+`<div class=\"ind-top\">"),
    ("${fcTd(r,true)}${tabs}<div class=\"ind-sub\">⏳ تاريخ قليل لهذا المدى", "${fcGp(r,true)}${tabs}<div class=\"ind-sub\">⏳ تاريخ قليل لهذا المدى"),
    ("det=`<div class=\"ind-det\" onclick=\"event.stopPropagation()\">${fcTd(r,true)}${fcBotDet(r)}", "det=`<div class=\"ind-det\" onclick=\"event.stopPropagation()\">${fcGp(r,true)}${fcBotDet(r)}"),
    ("      ${fcTd(r,false)}${fcRng(r)}${fcBot(r)}${det}</div>`}).join('')}</div>`;", "      ${fcGp(r,false)}${fcRng(r)}${fcBot(r)}${det}</div>`}).join('')}</div>`;"),
    (" · <b>🎯 الميل اليومي</b> — يظهر فقط حين ينطلق على العملة مؤشر أثبت نفسه على كل العملات معاً (بطل)، مع صدق الميل نفسه · <b>🟢 مؤشر القاع</b> كما هو.</div>",
     " · <b>🧩 المجاميع</b> — يظهر السطر فقط حين ينطلق على العملة بطل من مجموعة (مؤشر أو توليفة أثبتت نفسها على التاريخ بشغل مجموعتها)، مع صدقه والعادي · <b>🟢 مؤشر القاع</b> كما هو.</div>"),
]

JS_GP = r'''/* 🧩 v3.36.77: المؤشرات — مجاميع للعملة وللسوق: كل مجموعة بشغلها وإشعارها · سجلها على التاريخ (ساعة · 4 ساعات · يوم) · أعضاؤها وأبطالها
   (المالك 21-11: «خانتين للعملات وللسوق … عملة بداخلها مجاميع كل مجموعه مختصه بشيء ونسبتها») · عرض فقط: لا أوامر */
let GPV=null,GPS='coin',GPC='',GPF='4H',GPT=null;const GPO={};
async function gpLoad(){clearTimeout(GPT);try{GPV=await api('/api/groups')}catch(e){GPV={ok:false,msg:'تعذّر تحميل المجاميع'}}
  if(SGTAB==='ind'&&$('#sg_body')){sgRender();GPT=setTimeout(()=>{if(SGTAB==='ind'&&$('#sg_body'))gpLoad()},120000)}}
function gpSec(s){GPS=s;sgRender()}
function gpCoin(s){GPC=s;sgRender()}
function gpNm(k){const N=(GPV&&GPV.names)||{};return String(k).split('+').map(c=>N[c]||c).join(' + ')}
function gpG(fr,sec,g){return (((((GPV&&GPV.f)||{})[fr]||{})[sec]||{}).g||{})[g]||null}
function gpRec(G,coin){const c=coin&&G&&(G.coin||{})[coin];return c?[c.rec||[0,0,0],true]:[(G&&G.rec)||[0,0,0],false]}
function gpCell(fr,G,coin){const F=((GPV&&GPV.frs)||{})[fr]||['',fr,''];
  if(!G)return `<div class="gp-cell"><div class="gp-fh">${F[0]} ${gEsc(F[1])}</div><div class="gp-p">—</div><small>لم يُبنَ بعد</small></div>`;
  const [r,own]=gpRec(G,coin),p=r[1]?Math.round(100*r[0]/r[1]):null,b=r[1]?Math.round(100*r[2]/r[1]):null,ok=r[1]>=30&&r[0]/r[1]>=r[2]/r[1]+(+GPV.say||0.03);
  return `<div class="gp-cell${ok?' ok':''}" title="ما كان سيصل من هذه المجموعة على هذا الإطار${coin?(own?' على هذه العملة':' (كل العملات معاً — لا سجل لهذه العملة بعد)'):' (كل العملات معاً)'} وصدقه · العادي: ما يصيبه تنبؤ عشوائي بالجهات نفسها على الشموع نفسها">
    <div class="gp-fh">${F[0]} ${gEsc(F[1])}</div><div class="gp-p">${p!=null?`<b>${p}%</b>`:'—'}${ok?' ✅':''}</div><small>${r[1]?`من ${r[1].toLocaleString('en-US')} · العادي ${b}%`:'لا تنبؤات بعد'}</small></div>`}
function gpNow(g,X,coin){const out=[];['1H','4H','1D'].forEach(fr=>{const by=((((GPV.now||{})[fr]||{})[X.sec]||{})[g])||{},F=(GPV.frs||{})[fr]||['',''];
    const who=X.sec==='mkt'?['BTC-USDT']:coin?[coin]:(GPV.mine||[]);
    who.forEach(s=>{const x=by[s];if(x)out.push(`<div class="gp-nw ${x[0]>0?'up':'dn'}">🔔 ${X.sec==='coin'&&!coin?`<b>${gEsc(s.split('-')[0])}</b> `:''}${F[0]} ${gEsc(F[1])}: ${gEsc(X.say[x[0]>0?0:1])} <small>— ${gEsc(gpNm((x[1]||[])[0]||''))}</small></div>`)})});
  return out.join('')}
function gpDet(g,X,coin){const G=gpG(GPF,X.sec,g)||{},M=G.m||[],CM=coin?(((G.coin||{})[coin]||{}).m||{}):null,P=GPV.p||{};
  const ST={'2':'⭐ بطل','1':'✅ مثبت','0':'🧪 قيد الاختبار','-1':'— لم يثبت'};
  const rows=M.map(x=>{const n=x[1]+x[2],p=n?Math.round(100*x[1]/n):null,c=CM&&CM[x[0]],cn=c?c[0]+c[1]:0;
    return `<div class="gp-m s${x[4]}"><span class="gp-mn">${x[0].includes('+')?'🤝 ':''}${gEsc(gpNm(x[0]))}</span><b>${p!=null?p+'%':'—'}</b>
      <small>${n?`من ${n.toLocaleString('en-US')} · العادي ${Math.round(100*x[5])}% · ${x[3]} يوماً`:'لم ينطلق بعد'}${cn?` · على ${gEsc(coin.split('-')[0])}: ${Math.round(100*c[0]/cn)}% من ${cn}`:''}</small><span class="gp-st">${ST[String(x[4])]||''}</span></div>`}).join('');
  return `<div class="gp-det" onclick="event.stopPropagation()"><div class="sb-tabs">${['1H','4H','1D'].map(fr=>{const F=(GPV.frs||{})[fr]||['',fr];return `<button class="${GPF===fr?'on':''}" onclick="GPF='${fr}';sgRender()">${F[0]} ${gEsc(F[1])}</button>`}).join('')}</div>
    <div class="ind-sub">${X.mem.length} مؤشراً في هذه المجموعة + التوليفات (كل اثنين منها انطلقا معاً بالجهة نفسها) · البطل: ${P.dmin||30} يوماً من النتائج على الأقل وصدقه أعلى من العادي بـ${Math.round(100*(P.lift||0.05))}% فأكثر — ويبقى حتى ينزل قرب العادي · ${P.cap||2} أبطال على الأكثر</div>
    ${rows||'<div class="ind-sub">لا أعضاء بنتائج بعد على هذا الإطار</div>'}</div>`}
function gpCard(g,X){const op=!!GPO[g],J=(GPV.jobs||{})[X.job]||['',''],coin=X.sec==='coin'?GPC:'',lv=(GPV.lv||{})[g]||'view';
  const ch=['1H','4H','1D'].map(fr=>{const G=gpG(fr,X.sec,g),F=(GPV.frs||{})[fr]||[''];return G&&(G.ch||[]).length?`${F[0]} ${G.ch.map(k=>gEsc(gpNm(k))).join(' · ')}`:''}).filter(Boolean);
  const nw=gpNow(g,X,coin);
  return `<div class="gp-g${nw?' live':''}" data-g="${g}"><div class="gp-h" onclick="GPO['${g}']=!GPO['${g}'];sgRender()"><span class="gp-ic">${X.ic}</span>
      <span class="gp-nm"><b>${gEsc(X.nm)}</b><small>شغلها: ${gEsc(J[0])} — ${gEsc(J[1])}</small></span>
      <span class="gp-lv" title="إشعار هذه المجموعة (يُغيَّر من ⚙️ الإشعارات)">${({now:'📲',view:'👁',off:'⛔'})[lv]||'👁'}</span></div>
    <div class="gp-cells">${['1H','4H','1D'].map(fr=>gpCell(fr,gpG(fr,X.sec,g),coin)).join('')}</div>${nw}
    <div class="ind-sub">⭐ الأبطال: ${ch.length?ch.join(' · '):'لا بطل الآن — لا إشعار من هذه المجموعة حتى يثبت عضو'}</div>${op?gpDet(g,X,coin):''}</div>`}
function gpTab(V){let h=`<div class="gp-secs">${[['coin','🪙 العملات'],['mkt','🌐 السوق']].map(([k,t])=>`<button class="${GPS===k?'on':''}" onclick="gpSec('${k}')">${t}</button>`).join('')}</div>`;
  if(!GPV)return h+`<div class="sg-empty">${LDR('جاري تحميل المجاميع…')}</div>`;
  if(GPV.ok===false)return h+`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(GPV.msg||'تعذّر تحميل المجاميع')}</div>`;
  const N=GPV.n||{},nc=(N['1D']||N['4H']||[0])[0];
  if(GPS==='coin'){const cs=GPV.mine||[];if(GPC&&!cs.includes(GPC))GPC='';
    h+=`<div class="sb-tabs">${[['','كل العملات معاً']].concat(cs.map(s=>[s,s.split('-')[0]])).map(([s,nm])=>`<button class="${GPC===s?'on':''}" onclick="gpCoin('${gEsc(s)}')">${gEsc(nm)}</button>`).join('')}</div>`;
    const I=GPC?((INDV&&INDV.rows)||[]).find(r=>r.sym===GPC):null;
    h+=`<div class="sb-top"><b>${GPC?`🪙 ${gEsc(GPC.split('-')[0])}`:'🪙 كل العملات معاً'}</b> <small>${GPC?`النسبة على ${gEsc(GPC.split('-')[0])} وحدها · الأبطال من كل العملات معاً`:`كل مجموعة محكومة بسعر كل عملة — ${nc} عملة معاً`}</small></div>`;
    if(I)h+=sgIndAvg(I)}
  else{h+=`<div class="sb-top"><b>🌐 السوق كله</b> <small>محكوم بسعر البيتكوين ومعه قراءات السوق كله والمزاج والاقتصاد والعقود</small></div>`;
    if(INDV&&INDV.ok!==false&&INDV.on)h+=`<details class="sg-more"><summary>🌐 السوق كله الآن — الخوف والطمع · السيولة · المحترفون · الاقتصاد</summary><div style="text-align:right">${indFng(INDV.fng||{})}${indMkt(INDV.mkt)}${indPro(INDV.pro)}</div></details>`}
  if(!GPV.ts)return h+`<div class="sg-empty">🧩 يُبنى سجل المجاميع على تاريخ الأسعار عند أول فحص (دقائق) — ثم يُعاد كل يوم بعد إغلاق اليوم</div>`;
  h+=`<div class="ind-sub">🔄 آخر بناء للسجل ${gAgo(GPV.ts)} (يُعاد كل يوم) · ✅ = سجل المجموعة نفسها أعلى من العادي بـ${Math.round(100*(+GPV.say||0.03))}% فأكثر على 30 مرة — إشعارها يصل فوراً</div>`;
  h+=Object.entries(GPV.groups||{}).filter(([g,x])=>x.sec===GPS).map(([g,x])=>gpCard(g,x)).join('');
  h+=`<details class="ind-help"><summary>كيف أقرأ المجاميع؟</summary>
    <div>• كل مجموعة لها <b>شغل واحد وإشعار واحد</b>: الجهة (هل يكمل السعر بجهته؟) · حجم الحركة (هل تأتي حركة أكبر من المعتاد؟) · مقابل البيتكوين (هل تسبقه العملة؟).</div>
    <div>• أعضاؤها مؤشرات من نوعها و<b>توليفات</b> (اثنان منها انطلقا معاً بالجهة نفسها). كل عضو يُحكم على شغل مجموعته بالشمعة التالية من إطاره: <b>⏱ ساعة · 🕓 4 ساعات · 📅 يوم</b> — على تاريخ الأسعار كله بترتيب الزمن.</div>
    <div>• <b>⭐ البطل</b>: عضو صدقه أعلى من العادي بفارق واضح على عدد كافٍ من الأيام (بما عُرف وقتها فقط). الإشعار يأتي من الأبطال وحدهم ويذكر اسم العضو وصدقه والعادي.</div>
    <div>• <b>العادي</b>: ما يصيبه تنبؤ عشوائي بالجهات نفسها على الشموع نفسها — يزيل أثر صعود السوق الطويل. النسبة في الخانة = صدق ما كان سيصل من المجموعة (لا أفضل عضو وحده).</div>
    <div>• مؤشر جديد يُضاف إلى مجموعته بحسب نوعه ويُختبر على التاريخ قبل أن يتكلم (🧪 قيد الاختبار حتى تكفي نتائجه).</div>
    <div style="color:var(--amber);margin-top:6px">⚠️ احتمالات لا ضمانات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;
  return h}
'''

JS_FC = r'''function fcGp(r,full){const L=((FCV&&FCV.gp)||{})[r.sym]||[],FR={'1H':'⏱ ساعة','4H':'🕓 4 ساعات','1D':'📅 يوم'};      // 🧩 v3.36.77: ما تتوقعه مجاميع العملة الآن
  if(!L.length)return full?`<div class="ind-sub">🧩 لا بطل من المجاميع منطلق على هذه العملة الآن</div>`:'';
  return L.map(x=>{const G=((typeof GPV!=='undefined'&&GPV&&GPV.groups)||{})[x[1]]||null,sy=G?G.say[x[2]>0?0:1]:(x[2]>0?'صعود':'هبوط');
    return `<div class="fc-td ${x[2]>0?'up':'dn'}">🧩 ${G?G.ic+' ':''}${FR[x[0]]||x[0]}: ${gEsc(sy)} <small>— ${gEsc(x[3])} · صدق ${Math.round(100*x[4]/Math.max(1,x[5]))}% من ${(+x[5]).toLocaleString('en-US')} (العادي ${Math.round(100*x[6])}%)${x[7]?'':' · سجل المجموعة لم يثبت بعد'}</small></div>`}).join('')}
'''

CSS = (".gp-secs{display:flex;gap:6px;margin:4px 0 8px}.gp-secs button{flex:1;padding:8px 10px;border-radius:12px;border:1px solid var(--bd);background:var(--bg1);color:var(--tx);font-size:13.5px;cursor:pointer}"
       ".gp-secs button.on{border-color:var(--green);font-weight:700}\n"
       ".gp-g{border:1px solid var(--bd);border-radius:12px;padding:8px 10px;margin:8px 0;background:var(--bg1)}.gp-g.live{border-color:var(--cyan)}\n"
       ".gp-h{display:flex;gap:8px;align-items:center;cursor:pointer}.gp-ic{font-size:20px}.gp-nm{flex:1;display:flex;flex-direction:column;gap:1px;min-width:0}"
       ".gp-nm small{color:var(--mut);font-size:11px}.gp-lv{font-size:15px}\n"
       ".gp-cells{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-top:6px}"
       ".gp-cell{border:1px solid var(--bd);border-radius:9px;padding:4px 2px;text-align:center;font-size:11.5px;line-height:1.5}.gp-cell.ok{border-color:var(--green)}"
       ".gp-fh{color:var(--mut);font-size:11px}.gp-p b{font-size:14px}.gp-cell small{color:var(--mut2);font-size:10.5px}\n"
       ".gp-nw{font-size:12.5px;margin:5px 0 0;padding:3px 8px;border-radius:9px}.gp-nw.up{border-inline-start:3px solid var(--green)}.gp-nw.dn{border-inline-start:3px solid var(--red)}"
       ".gp-rc{color:var(--mut2);font-weight:400}\n"
       ".gp-det{margin-top:6px;border-top:1px dashed var(--bd);padding-top:6px}.gp-m{display:grid;grid-template-columns:1fr auto;gap:0 8px;padding:4px 0;border-bottom:1px dashed var(--bd);font-size:12.5px}"
       ".gp-m small{color:var(--mut);font-size:11px}.gp-m .gp-st{font-size:11px;color:var(--mut)}.gp-m.s2 .gp-mn{font-weight:700;color:var(--tx)}.gp-m.s-1{opacity:.7}\n")

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    # the old tables' page code (one block: its comment … the end of sbTable) ⇒ the groups
    a = s.index("/* 📋 v3.36.73: جداول المؤشرات — جدول للسوق كله ولكل عملة")
    b = s.index("\nfunction sgInd(V){", a) + 1
    s = s[:a] + JS_GP + s[b:]
    # 🔮 the tendency's two functions ⇒ fcGp
    a = s.index("function fcTdTop(){")
    b = s.index("function fcRng(r){", a)
    s = s[:a] + JS_FC + s[b:]
    # CSS: the old tables' rules ⇒ the groups'
    a = s.index(".sb-tabs,.sb-sort{")
    b = s.index(".sg-pl{border-top:", a)
    old = s[a:b]
    keep = (".sb-tabs{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0}"
            ".sb-tabs button{padding:5px 10px;border-radius:999px;border:1px solid var(--bd);background:var(--bg1);color:var(--tx);font-size:12px;cursor:pointer}"
            ".sb-tabs button.on{border-color:var(--green);font-weight:700}.sb-top{margin:6px 0}\n")
    s = s[:a] + keep + CSS + s[b:]
    for n in ("sbLoad", "sbTable", "sbRow", "sbCell", "sbScore", "sbSort", "sbOff", "SBV", "fcTdTop", "fcTd", "/api/board"):
        if re.search(r"(?<![\w/])" + re.escape(n) + r"(?![\w])", s):
            print(f"❌ still in the page: {n}"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 📋 the groups tab (🪙 · 🌐) · ⚙️ two sections with records · 🔮 🧩 lines · old table page code and CSS removed ({len(old)} chars) · {p}")
