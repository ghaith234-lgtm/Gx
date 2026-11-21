# 🔮 patch 122 (dashboard v3.36.71 · the forecasts on the same indicators). The owner (21-11): «اريد المؤشرات مفهومة وسهلة وكلامها
#   مفهوم … كذلك تعتمد التوقعات عليها».
#   · every indicator under a horizon in 🔮 is the SAME indicator as in «🎯 المؤشرات»: the same plain name for its state (rise · fall ·
#     neutral), the same meaning in one sentence, the technical name small — from the one table (_sg_plain · /api/forecast «plain»);
#     the funding rate gets its entry too (P-fund)
#   · the horizons «يوم» and «شهر» show the analyst's forecast first: «🧠 المحلل — مجموعات مؤشرات متفقة صدقت في كل فترات التاريخ:
#     📈 صعود · دقة 62% (من 40 مرة) · لماذا …» (tomorrow from the 4-hour groups · next month from the daily ones) — or, plainly, that no
#     proven group agrees now · the indicators' own vote stays below it as a description, with its own record
#   python3 devtests/step/patches/p122_fc_same_indicators.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""    "P-mv": ("market", "🔗 الحائزون قريبون من سعر شرائهم", "🔗 الحائزون في ربح كبير",
             "أغلب الحائزين قريبون من سعر شرائهم — ضغط البيع عادة أقل", "أغلب الحائزين في ربح كبير — قد يبيع بعضهم", "MVRV"),
}""",
     """    "P-mv": ("market", "🔗 الحائزون قريبون من سعر شرائهم", "🔗 الحائزون في ربح كبير",
             "أغلب الحائزين قريبون من سعر شرائهم — ضغط البيع عادة أقل", "أغلب الحائزين في ربح كبير — قد يبيع بعضهم", "MVRV"),
    "P-fund": ("market", "💸 البيع مزدحم في العقود (قراءة عكسية)", "💸 الشراء مزدحم في العقود (قراءة عكسية)",
               "البائعون في العقود يدفعون الرسوم — البيع مزدحم وقد يرتد السعر", "المشترون في العقود يدفعون رسوماً عالية — الشراء مزدحم وقد يتراجع السعر", "Funding"),
}"""),
    ("""    v["sig"] = _safe(sg_fc, v["rows"], default=None)          # 🎯 v3.36.66: إشارات كل عملة الآن + البوصلة""",
     """    v["sig"] = _safe(sg_fc, v["rows"], default=None)          # 🎯 v3.36.66: إشارات كل عملة الآن + البوصلة
    v["plain"] = _safe(sg_plain_all, default={})              # 🔮 v3.36.71: المؤشرات نفسها بأسمائها الواضحة (نفس جدول «🎯 المؤشرات»)"""),
    # the page
    ("""function fcVote(z){""",
     """const FCK={vp:'O-vp',avwap:'O-avwap',of:'O-of',pa:'O-pa',trend:'O-trend',st:'O-st',macd:'O-macd',rsi:'O-rsi',adx:'O-adx',cmf:'O-cmf',lc:'F-lc',nw:'F-nw',fng:'M-fng',fund:'P-fund'};
function fcPl(p){const P=((FCV&&FCV.plain)||{})[FCK[p.k]]||null;                 // 🔮 v3.36.71: المؤشر نفسه في «🎯 المؤشرات» — اسمه الواضح لحاله ومعناه
  if(!P)return {nm:p.name,mean:p.what||'',tech:''};
  return {nm:p.w==='p'?P[1]:p.w==='n'?P[2]:(P[5]||p.name)+': محايد',mean:p.w==='p'?P[3]:p.w==='n'?P[4]:(p.what||''),tech:P[5]||''}}
function fcAn(r,k){const fr={d:'4H',m:'1D'}[k];if(!fr)return '';const A=r.an,z=A&&(A.hz||{})[fr],nm=fr==='4H'?'غداً':'الشهر القادم';   // 🧠 المحلل لهذا المدى
  if(!A)return `<div class="fc-an">🧠 <b>المحلل (${nm})</b>: يظهر بعد أول فحص للمؤشرات على هذه العملة</div>`;
  if(!z||!z.dir)return `<div class="fc-an">🧠 <b>المحلل (${nm})</b>: لا توجد الآن مجموعة مؤشرات مثبتة تتفق على اتجاه — الأصدق ألا تُبنى قراءة على الميل وحده</div>`;
  return `<div class="fc-an ${z.dir>0?'p':'n'}">🧠 <b>المحلل (${nm})</b>: ${z.dir>0?'📈 صعود':'📉 هبوط'} · دقة <b>${z.h}%</b> <small>(من ${sgAr(z.n,'time')})</small>${(z.why||[]).length?` · لماذا: ${z.why.map(gEsc).join(' · ')}`:''}
    <div class="ind-sub">مجموعة مؤشرات متفقة صدقت في كل فترات التاريخ (${(z.nm||[]).map(gEsc).join(' + ')}) — التفاصيل في «🧠 المحلل»</div></div>`}
function fcVote(z){"""),
    ("""          <div><b style="color:var(${['su','u'].includes(x.vk)?'--green':['sd','d'].includes(x.vk)?'--red':'--mut'})">${gEsc(x.vt)}</b> — ${x.up} صاعدة · ${x.dn} هابطة · ${x.fl} محايدة <small>(على شموع ${gEsc(x.tfn)} · بعد ${gEsc(x.name)})</small></div>""",
     """          ${fcAn(r,k)}
          <div>📊 ميل المؤشرات: <b style="color:var(${['su','u'].includes(x.vk)?'--green':['sd','d'].includes(x.vk)?'--red':'--mut'})">${gEsc(x.vt)}</b> — ${x.up} صاعدة · ${x.dn} هابطة · ${x.fl} محايدة <small>(على شموع ${gEsc(x.tfn)} · بعد ${gEsc(x.name)} · وصف لا توقع)</small></div>"""),
    ("""          ${(x.sig||[]).slice().sort(fcRank).map(p=>{const b=fcB(p.acc);return `<div class="ind-row" onclick="openGuide('${gEsc(p.k)}','fc')"><span>${p.ico} <b>${gEsc(p.name)}</b> <small class="gd-i">ⓘ</small></span><span class="w ${p.w}">${{p:'⬆️ صاعد',n:'⬇️ هابط',z:'↔️ محايد'}[p.w]}<i class="fb ${b.g}" title="${gEsc(fcBW(p.acc))}">${b.t}</i></span><small>${gEsc(p.txt)}</small></div>`}).join('')}</div>`}}""",
     """          ${(x.sig||[]).slice().sort(fcRank).map(p=>{const b=fcB(p.acc),q=fcPl(p);return `<div class="ind-row" onclick="openGuide('${gEsc(p.k)}','fc')"><span><b>${gEsc(q.nm)}</b> <small class="gd-i">ⓘ</small></span><span class="w ${p.w}">${{p:'⬆️ صاعد',n:'⬇️ هابط',z:'↔️ محايد'}[p.w]}<i class="fb ${b.g}" title="${gEsc(fcBW(p.acc))}">${b.t}</i></span><small>${q.mean?gEsc(q.mean)+' · ':''}${gEsc(p.txt)}${q.tech?` <span class="sg-tech">· ${gEsc(q.tech)}</span>`:''}</small></div>`}).join('')}</div>`}}"""),
    ("""<span class="ind-chip">📊 نفس مؤشرات «المؤشرات» + 4 إضافات</span>""",
     """<span class="ind-chip">🎯 نفس المؤشرات بأسمائها في «🎯 المؤشرات» + 🧠 المحلل</span>"""),
    ("""    <div>• كل سطر مدى زمني: <b>ماذا تقول المؤشرات</b> (كم مؤشراً صاعداً أو هابطاً من العدد كله: المؤشرات العشرة نفسها وأربعة إضافية) · <b>النطاق المتوقع</b> (يقع السعر في نهاية المدة بين الرقمين بنسبة 80%) · <b>صدقها</b>.</div>""",
     """    <div>• كل سطر مدى زمني: <b>ماذا تقول المؤشرات</b> (كم مؤشراً صاعداً أو هابطاً من العدد كله: المؤشرات العشرة نفسها وأربعة إضافية) · <b>النطاق المتوقع</b> (يقع السعر في نهاية المدة بين الرقمين بنسبة 80%) · <b>صدقها</b>.</div>
    <div>• المؤشرات هنا هي نفسها في «🎯 المؤشرات» بأسمائها ومعانيها · وفي «يوم» و«شهر» يأتي أولاً <b>🧠 المحلل</b>: لا يتوقع إلا حين تتفق مجموعة مؤشرات صدقت في كل فترات التاريخ (غداً من شموع 4 ساعات · الشهر القادم من اليومية)، وميل المؤشرات تحته وصف للحال.</div>"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    css_a = ".sg-pl{border-top:1px solid var(--bd);padding:6px 2px}"
    if s.count(css_a) != 1:
        print("❌ css anchor (p121 first)"); sys.exit(1)
    s = s.replace(css_a, ".fc-an{padding:6px 8px;margin:2px 0 6px;border-radius:8px;background:var(--bg1)}.fc-an.p{border-inline-start:3px solid var(--green)}.fc-an.n{border-inline-start:3px solid var(--red)}\n" + css_a, 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + 1} replacements · 🔮 the forecasts on the same indicators · compiles · {p}")
