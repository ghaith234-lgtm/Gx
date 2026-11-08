# 🔮 patch 30 (dashboard · 🔮 forecast · 📊 indicators — apply after p29) — the owner (8-11): «التوقعات والمؤشرات سويهم اقوى عبر
#   الاختبارات حقيقية … اريد المؤشر الي يكون صادق او الافضل خليه بالبداية».
#   Measured on REAL OKX prices (ci/sig_check.py · sig_check2.py — 28 coins, the dashboard's own readings, each past candle seeing only
#   what came before it): the indicators' lean, taken as a forecast, is wrong slightly MORE often than chance on the day and the week
#   (the vote 47.1% vs 50.6%) — after they lean strongly down, the price was higher a day later 52.1% of the time vs 47.8% normally
#   (28/28 coins · 2024 · 2025 · 2026), after they lean up it was lower more often. Month: no difference. 3 months: too few periods.
#   ① each horizon now shows what FOLLOWED this lean on the real prices («higher after a day: 52% · normally 48%» ↗️ / ↘️ / ↔️,
#      «not proven» where it isn't) — the 28-coin table (FC_REAL) + this coin's own record of the same lean (new: counted by the backtest
#      per lean · FC_VER 5 ⇒ the past is re-read once); the indicators' lean stays visible («↘️ 9/14»).
#   ② the indicators under each horizon (🔮) and under each coin (📊) are listed truthful first (🟢 · 🟡 · ⚪ · 🔴 — then by edge).
#   Display only: no order, no notification.
#   python3 devtests/step/patches/p30_fc_real.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''FC_VER = 4                       # 🧮 نسخة الحساب — لو تتغيّر ينعاد فحص الماضي مرة وحدة''',
     '''FC_VER = 5                       # 🧮 نسخة الحساب — لو تتغيّر ينعاد فحص الماضي مرة وحدة (v3.36.27: + ما تبع كل ميل على هذه العملة)
# 🔬 v3.36.27: ما تبع ميل المؤشرات على الأسعار الحقيقية (ci/sig_check2.py · OKX · كل شمعة ماضية بلا نظر لما بعدها): % المرات التي كان
#   السعر فيها أعلى بعد المدة — لكل ميل (هابط بقوة · هابط · محايد · صاعد · صاعد بقوة) مقابل العادي. «ok» = ثبت على العملات والسنوات.
FC_REAL = {
    "d": {"base": 47.8, "b": {"sd": 52.1, "d": 49.7, "f": 45.2, "u": 45.1, "su": 44.9}, "ok": True,
          "src": "28 عملة · شموع 4 ساعات 2024–2026 · ثبت في 28 عملة من 28 وفي كل سنة"},
    "w": {"base": 46.3, "b": {"sd": 48.4, "d": 46.8, "f": 42.9, "u": 44.7, "su": 47.0}, "ok": True,
          "src": "28 عملة · شموع يومية 2021–2026 · أضعف من اليوم: ثبت في 26 عملة من 28 ولم يثبت في كل سنة"},
    "m": {"base": 45.2, "b": {"sd": 45.0, "d": 45.8, "f": 44.5, "u": 47.0, "su": 44.3}, "ok": False,
          "src": "28 عملة · شموع 3 أيام — لا فرق واضح عن العادي"},
    "q": {"base": 45.7, "b": {"sd": 50.9, "d": 47.5, "f": 44.9, "u": 49.1, "su": 37.2}, "ok": False,
          "src": "22 عملة · شموع أسبوعية — الفترات المستقلة قليلة فلا يُعتمد عليها"},
}
FC_EDGE = 2.0                    # فرق نقطتين فأكثر عن العادي ⇒ سهم'''),
    ('''        _, _, _, vk, _ = _fc_vote(sig)
        items = [(kk, s) for kk, (s, _) in sig.items()] + [("vote", 1.0 if vk in ("su", "u") else -1.0 if vk in ("sd", "d") else 0.0)]''',
     '''        _, _, _, vk, _ = _fc_vote(sig)
        bk = e.setdefault("bk", {}).setdefault(vk, [0, 0])        # 🔬 v3.36.27: ما تبع هذا الميل على هذه العملة
        bk[0] += 1
        bk[1] += 1 if upm else 0
        items = [(kk, s) for kk, (s, _) in sig.items()] + [("vote", 1.0 if vk in ("su", "u") else -1.0 if vk in ("sd", "d") else 0.0)]'''),
    ('''        u = (e["U"] / e["N"]) if e["N"] else 0.5
        rel = _fc_grade(e["a"].get("vote"), u, H, FC_TFS[tf])''',
     '''        u = (e["U"] / e["N"]) if e["N"] else 0.5
        rel = _fc_grade(e["a"].get("vote"), u, H, FC_TFS[tf])
        G_ = FC_REAL.get(k) or {}
        pg = (G_.get("b") or {}).get(vk)
        own = (e.get("bk") or {}).get(vk) or [0, 0]
        d_ = (pg - G_["base"]) if pg is not None and G_.get("base") is not None else 0.0
        rk = ("up" if d_ >= FC_EDGE else "dn" if d_ <= -FC_EDGE else "eq") if G_.get("ok") else "na"
        real = {"k": rk, "t": {"up": "↗️ أعلى مرجّح", "dn": "↘️ أدنى مرجّح", "eq": "↔️ مثل العادي", "na": "↔️ غير مؤكد"}[rk],
                "p": pg, "base": G_.get("base"), "src": G_.get("src", ""), "own_n": own[0],
                "own_p": round(own[1] / own[0] * 100) if own[0] >= 20 else None, "own_base": round(u * 100) if e["N"] else None}'''),
    ('''        hz.update(up=up, dn=dn, n=n_, fl=n_ - up - dn, vk=vk, vt=vt, rel=rel,''',
     '''        hz.update(up=up, dn=dn, n=n_, fl=n_ - up - dn, vk=vk, vt=vt, rel=rel, real=real,'''),
    # ── the rows: [horizon][what followed][range][the indicators' lean]
    ('''      if(x.short||!x.vk)return `<div class="fc-r short"><span class="fh">${gEsc(z.name)}</span><span class="fv">⏳ تاريخ قليل</span><span class="fg">—</span><span class="fb short">⏳</span></div>`;
      const b=fcB(x.rel);
      return `<div class="fc-r v-${gEsc(x.vk)}"><span class="fh">${gEsc(z.name)}</span><span class="fv">${FCI[x.vk]||''} ${gEsc(fcVote(x))}</span>
        <span class="fg">${x.lo!=null?fcN(x.lo)+' – '+fcN(x.hi):'—'}</span><span class="fb ${b.g}">${b.t}</span></div>`}).join('');''',
     '''      if(x.short||!x.vk)return `<div class="fc-r short"><span class="fh">${gEsc(z.name)}</span><span class="fv">⏳ تاريخ قليل</span><span class="fg">—</span><span class="fb short">⏳</span></div>`;
      const q=x.real||{},qa={up:'↗️',dn:'↘️'}[q.k]||'↔️';         // 🔬 v3.36.27: ما تبع هذا الميل على الأسعار الحقيقية
      return `<div class="fc-r v-${gEsc(x.vk)}"><span class="fh">${gEsc(z.name)}</span><span class="fv rk-${gEsc(q.k||'na')}" title="${gEsc(fcRealW(q,z.name))}">${qa} ${q.k==='na'||q.p==null?'غير مؤكد':Math.round(q.p)+'% <small>/'+Math.round(q.base)+'</small>'}</span>
        <span class="fg">${x.lo!=null?fcN(x.lo)+' – '+fcN(x.hi):'—'}</span><span class="fb" title="ميل المؤشرات الآن: ${gEsc(x.vt)}">${FCI[x.vk]||''}${['su','u'].includes(x.vk)?x.up:['sd','d'].includes(x.vk)?x.dn:x.fl}/${x.n}</span></div>`}).join('');'''),
    ('''<div class="fc-rows"><div class="fc-r fc-hd"><span>المدى</span><span>المؤشرات</span><span>النطاق المتوقع</span><span>صدقها</span></div>''',
     '''<div class="fc-rows"><div class="fc-r fc-hd"><span>المدى</span><span title="كم مرة كان السعر أعلى بعد المدة على الأسعار الحقيقية / العادي">أعلى بعدها</span><span>النطاق المتوقع</span><span>المؤشرات</span></div>'''),
    ('''          <div>🎯 ${fcBW(x.rel)}</div>''',
     '''          <div>🔬 <b>${gEsc((x.real||{}).t||'')}</b> — ${gEsc(fcRealW(x.real||{},x.name))}</div>
          <div><small>🎯 ميل المؤشرات وحده كتوقّع على ${gEsc(r.base)}: ${fcBW(x.rel)}</small></div>'''),
    ('''          ${(x.sig||[]).map(p=>{const b=fcB(p.acc);''',
     '''          ${(x.sig||[]).slice().sort(fcRank).map(p=>{const b=fcB(p.acc);'''),
    ('''function fcVote(z){''',
     '''function fcRealW(q,nm){q=q||{};if(q.p==null)return 'لم يُقَس بعد';                // 🔬 v3.36.27: السطر بالكلام
  return `على الأسعار الحقيقية كان السعر بعد ${nm} أعلى في ${Math.round(q.p)}% من المرات بعد هذا الميل (العادي ${Math.round(q.base)}%)${q.k==='na'?' — غير مؤكد':''} · ${q.src||''}`
    +(q.own_p!=null?` · على هذه العملة: ${q.own_p}% من ${q.own_n} مرة (العادي ${q.own_base}%)`:'')}
function fcRank(a,b){const o={g:0,y:1,n:2,short:3,r:4},A=a.acc||{},B=b.acc||{};               // 🔬 الصادق أولاً
  return ((o[A.g]??3)-(o[B.g]??3))||((+B.edge||0)-(+A.edge||0))}
function fcVote(z){'''),
    # ── 📊 under each coin: the most accurate first
    ('''      det=`<div class="ind-det" onclick="event.stopPropagation()">${parts.map(p=>{const w=word(+p.s);''',
     '''      det=`<div class="ind-det" onclick="event.stopPropagation()">${parts.slice().sort((a,b)=>((b.acc??-1)-(a.acc??-1))).map(p=>{const w=word(+p.s);'''),
    ('''.fb.g{color:var(--green)}''', '''.fc-r .fv.rk-up{color:var(--green)}.fc-r .fv.rk-dn{color:var(--red)}.fc-r .fv.rk-eq,.fc-r .fv.rk-na{color:var(--mut)}.fc-r .fv small{color:var(--mut2);font-weight:400}.fb.g{color:var(--green)}'''),
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
