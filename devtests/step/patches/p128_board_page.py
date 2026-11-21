# 📋 patch 128 (dashboard v3.36.73 · the indicator tables — the page). The owner (21-11): «جدول خاص للسوق بشكل عام … ولكل عملة جدول ·
#   كل مؤشر وتوليفه الها رقم وشنو شغلها · الجيد يصعد فوق والسيء ينزل جوة حسب النسب».
#   · the tab «🎯 المؤشرات» becomes the tables: «🌐 السوق» + a tab for each of your coins · every row: its fixed number · its plain name ·
#     its job (the family) · ⏱ الآن · 🕓 4 ساعات · 📅 يوم — each with the running prediction (⬆️ ⏳) or the last result, ✅ · ❌ and the
#     percentage · ▶️ / ⏸ per row in its table · a tap shows both meanings and the technical name
#   · ranked by the lowest percentage we can trust (Wilson — «⭐ الأفضل» or by one column or by number) · fewer than 10 results ⇒
#     «🧪 قيد الاختبار» · ⏸ rows sink to the bottom · the coin table keeps «📊 اتجاه المؤشرات الآن» · the market table keeps «🌐 السوق كله الآن»
#   · the old per-coin cards (sgIndCoin · sgIndRow · sgIndTen — the history records) are gone: the tables count from zero
#   · 🔮's «🎯» line opens the coin's table · refreshed every minute while open
#   python3 devtests/step/patches/p128_board_page.py Holy_Dashboard.pyw
import os, sys

H = os.path.dirname(os.path.abspath(__file__))

R = [
    ("""if(SGTAB==='ind')sgIndLoad()}""",
     """if(SGTAB==='ind'){sgIndLoad();sbLoad()}}"""),
    ("""if(SGTAB==='ind'&&!INDV)sgIndLoad();""",
     """if(SGTAB==='ind'){if(!INDV)sgIndLoad();if(!SBV)sbLoad()}"""),
    ("""SGO['${gEsc(x.sym)}']=true;sgTab('ind')">🎯 كل مؤشرات العملة النشطة الآن ←""",
     """SBS='${gEsc(x.sym)}';SBV=null;sgTab('ind')">📋 جدول مؤشرات العملة ←"""),
    ("""SGO['${gEsc(r.sym)}']=true;openSig('now')""",
     """SBS='${gEsc(r.sym)}';SBV=null;openSig('now')"""),
    (""".sg-pl{border-top:1px solid var(--bd);padding:6px 2px}""",
     """.sb-tabs,.sb-sort{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0}.sb-sort{font-size:12px;color:var(--mut);margin:8px 0}
.sb-tabs button,.sb-sort button{padding:5px 10px;border-radius:999px;border:1px solid var(--bd);background:var(--bg1);color:var(--tx);font-size:12px;cursor:pointer}
.sb-tabs button.on,.sb-sort button.on{border-color:var(--green);font-weight:700}.sb-top{margin:6px 0}
.sb-sec{margin:12px 0 4px;font-size:12px;color:var(--mut);font-weight:700}
.sb-r{border:1px solid var(--bd);border-radius:10px;padding:6px 8px;margin:6px 0;background:var(--bg1)}.sb-r.off{opacity:.55}
.sb-h{display:flex;gap:8px;align-items:center;cursor:pointer}.sb-n{min-width:26px;text-align:center;font-weight:700;color:var(--mut)}
.sb-nm{flex:1;display:flex;flex-direction:column;gap:1px;min-width:0}.sb-job{color:var(--mut);font-size:11px}
.sb-sw{border:1px solid var(--bd);border-radius:999px;background:transparent;color:var(--tx);font-size:11px;padding:3px 8px;white-space:nowrap;cursor:pointer}
.sb-cells{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-top:6px}
.sb-cell{border:1px solid var(--bd);border-radius:8px;padding:4px 2px;text-align:center;font-size:11.5px;line-height:1.5}.sb-cell.test{opacity:.8}
.sb-fh{color:var(--mut);font-size:11px}.sb-wl .up{color:var(--green)}.sb-wl .dn{color:var(--red)}.sb-p b{font-size:13px}
.sb-det{margin-top:6px;font-size:12px;color:var(--mut);display:flex;flex-direction:column;gap:3px}
.sg-pl{border-top:1px solid var(--bd);padding:6px 2px}"""),
]

BLOCK = """/* 📋 v3.36.73: جداول المؤشرات — جدول للسوق كله ولكل عملة: كل صف (رقم ثابت) يتنبأ وحده لكل مدة ويُحكم بعدها ✅ ❌ — العدّ من الصفر ·
   الترتيب بأقل نسبة نثق بها · ▶️ ⏸ لكل صف في جدوله · عرض فقط */
let SBV=null,SBS='MKT',SBT=null,SBSORT='best';const SBO={};
async function sbLoad(s){if(s){SBS=s;SBV=null;if(SGTAB==='ind'&&$('#sg_body'))sgRender()}clearTimeout(SBT);
  try{SBV=await api('/api/board?s='+encodeURIComponent(SBS))}catch(e){SBV={ok:false,msg:'تعذّر تحميل الجدول'}}
  if(SBV&&SBV.s)SBS=SBV.s;if(SGTAB==='ind'&&$('#sg_body')){sgRender();SBT=setTimeout(()=>{if(SGTAB==='ind'&&$('#sg_body'))sbLoad()},60000)}}
async function sbOff(n,on){try{const r=await api('/api/control',{action:'sb_off',value:{s:SBS,n,on}});toast(r&&r.msg?r.msg:'تم',!!(r&&r.ok))}catch(e){toast('تعذر الاتصال',false)}sbLoad()}
function sbSort(k){SBSORT=k;sgRender()}
function sbN(c){return c?(+c.w||0)+(+c.l||0):0}
function sbScore(r){const fs=SBSORT==='best'||SBSORT==='n'?['1H','4H','1D']:[SBSORT];let b=-1;      // أقل نسبة نثق بها (ويلسون) لمن له نتائج كافية
  fs.forEach(f=>{const c=(r.f||{})[f];if(c&&sbN(c)>=SBV.minn)b=Math.max(b,+c.lb||0)});return b}
function sbCell(c,f){const F=(SBV.frs||{})[f]||['',f,''],n=sbN(c),L=c.last;
  const now=c.now?`<b class="${c.now>0?'up':'dn'}" title="تنبؤ جارٍ لـ${gEsc(F[2])}">${c.now>0?'⬆️':'⬇️'} ⏳</b>`
    :L?`<small title="آخر نتيجة">${L[2]?'✅':'❌'} ${L[0]>0?'⬆️':'⬇️'}</small>`:'<small>—</small>';
  return `<div class="sb-cell${n&&n<SBV.minn?' test':''}"><div class="sb-fh">${F[0]} ${gEsc(F[1])}</div><div class="sb-now">${now}</div>
    <div class="sb-wl"><span class="up">✅ ${+c.w||0}</span> <span class="dn">❌ ${+c.l||0}</span></div><div class="sb-p">${n?`<b>${Math.round(+c.p||0)}%</b>`:'—'}</div></div>`}
function sbRow(r){const op=!!SBO[r.n],G=(SBV.grp||[]).find(g=>g[0]===r.g)||['','🤝','توليفة قوية',''],one=r.up===r.dn;
  return `<div class="sb-r${r.off?' off':''}" data-n="${r.n}"><div class="sb-h" onclick="SBO[${r.n}]=!SBO[${r.n}];sgRender()"><span class="sb-n">${r.n}</span>
      <span class="sb-nm"><b>${gEsc(r.nm)}</b><small class="sb-job">${G[1]} ${gEsc(G[2])}</small></span>
      <button class="sb-sw${r.off?'':' on'}" onclick="event.stopPropagation();sbOff(${r.n},${r.off?'true':'false'})" title="${r.off?'موقوف — اضغط لتشغيله':'يعمل — اضغط لإيقافه'}">${r.off?'⏸ موقوف':'▶️ يعمل'}</button></div>
    <div class="sb-cells">${['1H','4H','1D'].map(f=>sbCell((r.f||{})[f]||{w:0,l:0},f)).join('')}</div>
    ${op?`<div class="sb-det">${r.k?`<div>🤝 ${r.k.map(gEsc).join(' + ')}</div>`:one?`<div><b>${gEsc(r.up)}</b> — ${gEsc(r.mu)}</div>`:`<div>⬆️ <b>${gEsc(r.up)}</b> — ${gEsc(r.mu)}</div><div>⬇️ <b>${gEsc(r.dn)}</b> — ${gEsc(r.md)}</div>`}${r.tech?`<div class="sg-tech">${gEsc(r.tech)}</div>`:''}</div>`:''}</div>`}
function sbTable(V){const S=SBV,cs=(S&&S.coins)||[];
  let h=`<div class="sb-tabs">${[['MKT','🌐 السوق']].concat(cs).map(([s,nm])=>`<button class="${SBS===s?'on':''}" onclick="sbLoad('${gEsc(s)}')">${gEsc(nm)}</button>`).join('')}</div>`;
  if(!S)return h+`<div class="sg-empty">${LDR('جاري تحميل الجدول…')}</div>`;
  if(S.ok===false)return h+`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(S.msg||'تعذّر تحميل الجدول')}</div>`;
  const base=S.s==='MKT'?'':S.s.split('-')[0],I=base?((INDV&&INDV.rows)||[]).find(r=>r.sym===S.s):null;
  const on=S.rows.filter(r=>!r.off),off=S.rows.filter(r=>r.off),top=on.filter(r=>sbScore(r)>=0),tst=on.filter(r=>sbScore(r)<0);
  top.sort((a,b)=>SBSORT==='n'?a.n-b.n:(sbScore(b)-sbScore(a))||(a.n-b.n));tst.sort((a,b)=>a.n-b.n);off.sort((a,b)=>a.n-b.n);
  const since=S.since?new Date(S.since*1000).toLocaleDateString('ar',{day:'numeric',month:'long',year:'numeric'}):'—';
  h+=`<div class="sb-top"><b>${base?`🪙 جدول ${gEsc(base)}`:'🌐 جدول السوق كله'}</b> <small>${base?`كل صف محكوم بسعر ${gEsc(base)}`:'إشارات البيتكوين وقراءات السوق كله — محكومة بسعر البيتكوين'}</small>
    <div class="ind-sub">العدّ بدأ ${gEsc(since)}${S.ts?` · 🔄 آخر فحص ${gAgo(S.ts)}`:''} · لها نتائج كافية: ${top.length} · قيد الاختبار: ${tst.length}${off.length?` · موقوفة: ${off.length}`:''}</div></div>`;
  if(I)h+=sgIndAvg(I);
  if(!base&&INDV&&INDV.ok!==false&&INDV.on)h+=`<details class="sg-more"><summary>🌐 السوق كله الآن — الخوف والطمع · السيولة · المحترفون · الاقتصاد</summary><div style="text-align:right">${indFng(INDV.fng||{})}${indMkt(INDV.mkt)}${indPro(INDV.pro)}</div></details>`;
  h+=`<div class="sb-sort">الترتيب: ${[['best','⭐ الأفضل'],['1H','⏱ الآن'],['4H','🕓 4 ساعات'],['1D','📅 يوم'],['n','# الرقم']].map(([k,t])=>`<button class="${SBSORT===k?'on':''}" onclick="sbSort('${k}')">${t}</button>`).join('')}</div>`;
  if(SBSORT==='n')h+=on.slice().sort((a,b)=>a.n-b.n).map(sbRow).join('');                   // # بالرقم: كل الصفوف العاملة بترتيب أرقامها
  else{if(top.length)h+=`<div class="sb-sec">⭐ لها نتائج كافية — الأصدق في الأعلى</div>${top.map(sbRow).join('')}`;
    if(tst.length)h+=`<div class="sb-sec">🧪 قيد الاختبار (${tst.length}) — أقل من ${S.minn} نتائج</div>${tst.map(sbRow).join('')}`}
  if(off.length)h+=`<div class="sb-sec">⏸ موقوفة (${off.length}) — تبقى تتنبأ وتُحكم بصمت ولا تدخل الإشعارات</div>${off.map(sbRow).join('')}`;
  h+=`<details class="ind-help"><summary>كيف أقرأ الجدول؟</summary>
    <div>• كل صف مؤشر برقم ثابت لا يتغير. حين ينطلق على شمعة مغلقة يتنبأ بجهته: <b>⏱ الآن</b> للساعة القادمة · <b>🕓 4 ساعات</b> للساعات الأربع القادمة · <b>📅 يوم</b> لليوم القادم.</div>
    <div>• بعد المدة يُحكم وحده: <b>✅</b> تحرك السعر بجهته · <b>❌</b> عكسها — والنسبة = ✅ من كل النتائج · ⬆️ ⏳ = تنبؤ جارٍ الآن.</div>
    <div>• الترتيب بـ<b>أقل نسبة نثق بها</b>: تجمع النسبة وعدد النتائج معاً، فـ3 من 3 (100%) لا تسبق 60 من 90 (67%) · وما له أقل من ${S.minn} نتائج «قيد الاختبار».</div>
    <div>• العدّ بدأ من الصفر: المدة الأطول تحتاج وقتاً أطول (خانة اليوم نحو شهر).</div>
    <div>• ▶️ / ⏸ يوقف الصف في هذا الجدول فقط: يبقى يتنبأ ويُحكم بصمت، وينزل إلى آخر الجدول.</div>
    <div style="color:var(--amber);margin-top:6px">⚠️ احتمالات لا ضمانات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;
  return h}
function sgInd(V){let h='';const B=V.busy||{};                                  // 🎯 v3.36.71 · 📋 v3.36.73: الجداول (السوق · كل عملة)
  if(B.phase)h+=`<div class="sg-busy">${gEsc(B.msg||'…')}<div class="sg-pb"><i style="width:${Math.max(3,+B.pct||0)}%"></i></div></div>`;
  if(V.err)h+=`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(V.err)}</div>`;
  return h+sbTable(V)}
"""


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a0 = "function sgIndRow(V,it,hz){"
    a1 = "function sgInd(V){let h='';const B=V.busy||{};"
    z = "<div style=\"color:var(--amber);margin-top:6px\">⚠️ احتمالات لا ضمانات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;\n  return h}\n"
    if s.count(a0) != 1 or s.count(a1) != 1:
        print("❌ the old per-coin cards were not found"); sys.exit(1)
    i0, i1 = s.index(a0), s.index(a1)
    i2 = s.index(z, i1) + len(z)
    if not (i0 < i1 < i2) or i2 - i1 > 6000:
        print("❌ the old block's end was not found"); sys.exit(1)
    s = s[:i0] + BLOCK + s[i2:]
    for gone in ("function sgIndRow(", "function sgIndTen(", "function sgIndCoin(", "sgIndCoin(x,V)"):
        if gone in s:
            print(f"❌ still there: {gone}"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + 1} replacements · 📋 the indicator tables (page) · compiles · {p}")
