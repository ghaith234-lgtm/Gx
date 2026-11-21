# p136 — v3.36.76 🔮 the forecasts on the same basis as 📈 (the owner 21-11: «بناء 🔮 التوقعات على نفس الأساس» — approved)
#   · each coin's card: 🎯 the daily tendency when the champions fired on it today (with its record) · then the range the price should end in
#     with 80% confidence for every horizon of the market layer (the SAME numbers as «📈 السوق» — no second model) with its live record ·
#     🟢 the bottom indicator (measured) as before
#   · on top: 🎯 the daily tendency — its record (all · the last year · since) and today's champions by name
#   · the indicators' lean per horizon moves into the details, said plainly as a description, not a forecast
#   · /api/forecast carries «an» (the range of each coin) · «rec» (the live record) · «hz2» (the horizons) · «td» (the tendency)
#   python3 devtests/step/patches/p136_fc_same_basis.py Holy_Dashboard.pyw
import sys, os, re

R = [
    ('''    v["plain"] = _safe(sg_plain_all, default={})              # 🔮 v3.36.71: المؤشرات نفسها بأسمائها الواضحة (نفس جدول «🎯 المؤشرات»)
''', '''    v["plain"] = _safe(sg_plain_all, default={})              # 🔮 v3.36.71: المؤشرات نفسها بأسمائها الواضحة (نفس جدول «🎯 المؤشرات»)
    A = _safe(_an_load, default={}) or {}                     # 🔮 v3.36.76: على نفس أساس «📈 السوق» — المدى المثبت وصدقه الحي + الميل اليومي
    Pc = (A.get("now") or {}).get("coins") or {}
    v["an"] = {r["sym"]: {"rng": (Pc.get(r["sym"]) or {}).get("rng")} for r in v["rows"] if r.get("sym") in Pc}
    v["rec"] = {k: {"in": x[0], "out": x[1], "p": round(100.0 * x[0] / max(1, x[0] + x[1]), 1)} for k, x in (A.get("rec") or {}).items()}
    v["hz2"] = [[k, nm] for k, _sec, _h, _st, nm in AN_HZ]
    td = A.get("td") or {}
    v["td"] = {"t": td.get("t"), "now": td.get("now") or {}, "rec": td.get("rec") or [0, 0], "rec1": td.get("rec1") or [0, 0], "since": td.get("since"),
               "ch": [[x[0], x[1], SB_NM.get(x[0], x[0]), x[2], x[3]] for x in (td.get("ch") or [])], "names": {c: nm for c, nm in SB_NM.items()}}
'''),
    ('''  let h=sgFcTop(V.sig)+`<div class="ind-top"><span class="ind-chip">🎯 نفس المؤشرات بأسمائها</span>''',
     '''  let h=sgFcTop(V.sig)+fcTdTop()+`<div class="ind-top"><span class="ind-chip">📏 المدى نفسه في «📈 السوق»</span>'''),
    ('''        det=`<div class="ind-det" onclick="event.stopPropagation()">${tabs}${fcBotDet(r)}<div class="fc-sum">''',
     '''        det=`<div class="ind-det" onclick="event.stopPropagation()">${fcTd(r,true)}${fcBotDet(r)}<div class="ind-sub" style="margin-top:6px">📊 ميل المؤشرات على كل مدى — وصف للحال لا توقّع:</div><div class="fc-rows">${rows}</div>${tabs}<div class="fc-sum">'''),
    ('''      if(x.short||!x.vk)det=`<div class="ind-det" onclick="event.stopPropagation()">${tabs}<div class="ind-sub">⏳ تاريخ قليل لهذا المدى''',
     '''      if(x.short||!x.vk)det=`<div class="ind-det" onclick="event.stopPropagation()">${fcTd(r,true)}${tabs}<div class="ind-sub">⏳ تاريخ قليل لهذا المدى'''),
    ('''      ${fcBot(r)}<div class="fc-rows"><div class="fc-r fc-hd"><span>المدى</span><span title="كم مرة كان السعر أعلى بعد المدة على الأسعار الحقيقية / العادي">أعلى بعدها</span><span>النطاق المتوقع</span><span>المؤشرات</span></div>${rows}</div>${det}</div>`}).join('')}</div>`;''',
     '''      ${fcTd(r,false)}${fcRng(r)}${fcBot(r)}${det}</div>`}).join('')}</div>`;'''),
    ('''    <div>• كل سطر مدى زمني: <b>ماذا تقول المؤشرات</b> (كم مؤشراً صاعداً أو هابطاً من العدد كله: المؤشرات العشرة نفسها وأربعة إضافية) · <b>النطاق المتوقع</b> (يقع السعر في نهاية المدة بين الرقمين بنسبة 80%) · <b>صدقها</b>.</div>''',
     '''    <div>• 🔮 على نفس أساس «📈 السوق»: <b>📏 المدى</b> — بين كم وكم سيكون السعر في نهاية كل مدة بثقة 80% (فُحص على سنتين من الأسعار الحقيقية فاحتوى السعر 80–82% من المرات) وصدقه الحي بجانبه · <b>🎯 الميل اليومي</b> — يظهر فقط حين ينطلق على العملة مؤشر أثبت نفسه على كل العملات معاً (بطل)، مع صدق الميل نفسه · <b>🟢 مؤشر القاع</b> كما هو.</div>
    <div>• تحت التفاصيل: <b>ميل المؤشرات على كل مدى</b> (كم مؤشراً صاعداً أو هابطاً) — وصف للحال لا توقّع: اتجاه الساعات والأيام القادمة لم يغلب الصدفة في الفحص.</div>'''),
]

JS = r'''function fcTdTop(){const T=(FCV&&FCV.td)||{},rec=T.rec||[0,0],r1=T.rec1||[0,0],ch=T.ch||[];       // 🎯 v3.36.76: الميل اليومي وأبطاله
  const pc=a=>a[1]?Math.round(100*a[0]/a[1])+'%':'—',nf=x=>(+x||0).toLocaleString('en-US');
  return `<div class="fc-tdt"><div><b>🎯 الميل اليومي</b> <small>— مؤشرات أثبتت نفسها على كل العملات معاً (يُختار كل يوم بما عُرف قبله فقط)</small></div>
    <div class="ind-sub">صدق الميل: <b>${pc(rec)}</b> من ${nf(rec[1])} مرة${T.since?` منذ ${new Date(T.since*1000).getFullYear()}`:''} · آخر سنة ${pc(r1)} من ${nf(r1[1])} — ميل ضعيف يتأخر عن الحركة، ليس ضماناً</div>
    <div class="ind-sub">🏆 الأبطال الآن: ${ch.length?ch.map(x=>`${gEsc(x[2])} <small>(${x[3]}% · ${nf(x[4])} يوماً)</small>`).join(' · '):'لا بطل الآن — لا ميل حتى يثبت مؤشر'}</div></div>`}
function fcTd(r,full){const T=(FCV&&FCV.td)||{},x=(T.now||{})[r.sym],rec=T.rec||[0,0],p=rec[1]>=30?Math.round(100*rec[0]/rec[1]):null;
  if(!x)return full?`<div class="ind-sub">🎯 لا ميل يومي اليوم — لم ينطلق على هذه العملة مؤشر مثبت</div>`:'';
  const nm=(x[1]||[]).slice(0,3).map(c=>gEsc((T.names||{})[c]||c)).join(' · ');
  return `<div class="fc-td ${x[0]>0?'up':'dn'}">🎯 ميل يومي ${x[0]>0?'للصعود':'للنزول'}${p!=null?` <small>— صدق هذا الميل ${p}% من ${rec[1].toLocaleString('en-US')} مرة</small>`:''}${full?`<div class="ind-sub">المؤشرات: ${nm} · ميل ضعيف يتأخر عن الحركة — ليس ضماناً</div>`:''}</div>`}
function fcRng(r){const A=((FCV&&FCV.an)||{})[r.sym]||{},B=A.rng,Q=(FCV&&FCV.rec)||{},H=(FCV&&FCV.hz2)||[];      // 📏 المدى نفسه في «📈 السوق»
  if(!B)return `<div class="ind-sub">⏳ يظهر المدى المتوقع بعد أول فحص للسوق (كل ساعة)</div>`;
  return `<div class="fc-rows"><div class="fc-r fc-hd"><span>المدى</span><span>بين كم وكم (80%)</span><span>±</span><span>صدقه</span></div>${H.map(([k,nm])=>{const b=B[k],q=Q[k];
    return b?`<div class="fc-r"><span class="fh">${gEsc(nm)}</span><span class="fg">${fcN(b.lo)} – ${fcN(b.hi)}</span><span>±${b.w}%</span><span class="fb" title="${q?`${q.in} داخله · ${q.out} خارجه`:'يبدأ العدّ مع أول مدى يكتمل'}">${q&&q.in+q.out>=5?q.p+'%':'—'}</span></div>`:''}).join('')}</div>`}
'''

CSS_OLD = ".an-mvs{display:flex;gap:6px;flex-wrap:wrap;margin:3px 0}"
CSS_NEW = (".fc-tdt{border:1px solid var(--bd);border-radius:12px;padding:8px 10px;margin:6px 0 8px;background:var(--bg1);font-size:12.5px}"
           ".fc-td{font-size:12.5px;margin:4px 0;padding:4px 8px;border-radius:9px;background:var(--bg1)}"
           ".fc-td.up{border-inline-start:3px solid var(--green)}.fc-td.dn{border-inline-start:3px solid var(--red)}\n" + CSS_OLD)

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R + [(CSS_OLD, CSS_NEW)]):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a = s.index("\nfunction fcRender(){") + 1
    s = s[:a] + JS + s[a:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + 2} replacements · 🔮 on the same basis (the range · the tendency · the bottom) · compiles · {p}")
