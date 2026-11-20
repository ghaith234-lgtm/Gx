# 🧠 patch 117 (dashboard v3.36.69 · the analyst's notifications and record). The owner (20-11): «العملات على حدى … مو يعطي اسعار يعطي
#   تحليل · تنبيهات الشراء والبيع على حدى · الشراء والبيع للعملة الي اختارها مع تحليل العملة · خليهم (الدخول والوقف والهدف) بالنافذة فقط ·
#   عند الاشعار لازم يتحقق الشرط بالسجل … وهذا السجل ينسحب · خلي يصلح نفسه · توقعات تبقى زر ثاني بس بيها ملخص محلل».
#   · a coin's notification is analysis, not prices: «🟢 دخول شراء — XRP-USDT · غداً» (or «🔴 دخول بيع» · «الشهر القادم») · «agreeing
#     indicator groups that held in all four periods» · its record (accuracy · how many times · random · the average) · why in plain words
#     (no indicator names) · the market · «الدخول والهدف والوقف في نافذة 📊 المؤشرات» · not a guarantee
#   · two switches for your coins: 🟢 دخول شراء · 🔴 دخول بيع (the old six kinds fold into these two by direction) · 🔎 «الآن في السوق»: a
#     new state on a coin of yours (accumulation · distribution · aggressive buying/selling · crowding · stronger/weaker than BTC) — once a day
#     at most per reading, a description not a forecast · 🌐 the market: the compass · a crash now (a fact) · fear & greed and the economy
#     ONLY when that reading itself held in all four periods (the real check of 20-11 sent «geopolitical risk low» at 28% vs random 47%)
#   · the record keeps 3,000 judged fires (was 400) · «📥 سحب السجل» saves it as a file (date · coin · direction · horizon · the group ·
#     ✅/❌ · % · whether you were notified) · the accuracy of what reached you, month by month and per horizon
#   · 🔮 every coin gets a «🧠 ملخص المحلل» line (the word · tomorrow · next month) that opens the analyst
#   python3 devtests/step/patches/p117_analyst_notify.py Holy_Dashboard.pyw
import os, sys

NEW_BLOCK = r'''def _sg_tyk(e):
    """🔔 v3.36.69: مفتاح الإشعار — قراءات السوق بنوعها (🌊 😨 🗞️) · كل ما يخص عملة: 🟢 دخول شراء أو 🔴 دخول بيع حسب الجهة"""
    return e["ty"] if e.get("ty") in ("crash", "fng", "eco") else ("buy" if e["s"] > 0 else "sell")


def _sg_why(keys, side):
    """لماذا — بكلام بسيط من أُسر الإشارات (بلا أسماء مؤشرات)"""
    M, out = _sg_meta(), []
    for k in keys:
        f = (M.get(k) or ("other",))[0]
        if f in SG_WHY and SG_WHY[f][0 if side > 0 else 1] not in out:
            out.append(SG_WHY[f][0 if side > 0 else 1])
    return out


def _sg_block(sym, ty, fr, ents, st, cat, scan, comp):
    """📨 v3.36.69: إشعار المحلل لعملة — تحليل لا أسعار: الاتجاه والمدة · المجموعات المتفقة المثبتة · السجل · لماذا · السوق"""
    ents = sorted(ents, key=lambda e: -_sg_wlb(_sg_rec(e, st)["h"] / 100.0 * _sg_rec(e, st)["d"], _sg_rec(e, st)["d"]))
    top = ents[0]
    side = top["s"]
    r = _sg_rec(top, st)
    keys = list(dict.fromkeys(k for e in ents for k in e["k"]))
    L = [f"{'🟢 دخول شراء' if side > 0 else '🔴 دخول بيع'} — {sym} · {SG_HZW[fr]}",
         ("اتفقت عليه مجموعة مؤشرات صدقت في الفترات الأربع من التاريخ" if len(ents) == 1
          else f"اتفقت عليه {_sg_ar(len(ents), 'grp')} من المؤشرات صدقت في الفترات الأربع من التاريخ"),
         _sg_rec_line(top, r, cat)]
    b = (cat.get("base") or {}).get(f"{top['f']}|{top['s']}") or {}
    if r["h"] <= float(b.get("ht") or 0) or r["m"] <= float(b.get("mt") or 0):
        L.append("⚠️ تاريخياً ليست أفضل من العشوائي")
    why = _sg_why(keys, side)
    if why:
        L.append("لماذا: " + " · ".join(why))
    if comp and comp.get("s"):
        L.append("🧭 السوق: " + {"up": "صاعد", "flat": "مختلط", "down": "نازل"}[comp["s"]])
    L.append("📊 الدخول والهدف والوقف في نافذة المؤشرات")
    L.append("⚠️ ليست ضماناً — القرار لك")
    return {"sym": sym, "ty": ty, "f": fr, "t": L[0], "b": "\n".join(L[1:]), "ids": [e["id"] for e in ents], "h": round(r["h"], 1)}


def _sg_nst_block(sym, code, sd, st, cat):
    """🔎 v3.36.69: حالة جديدة الآن على عملة من عملاتك — وصف لا توقع"""
    e = (cat.get("idx") or {}).get(f"1D|{sd}|{code}")
    L = [f"🔎 {sym.split('-')[0]} الآن: {_sg_name(code, sd)}", "وصف لما يحدث الآن على المنصة — ليس توقعاً"]
    if e and e["nt"] >= 10:
        r = _sg_rec(e, st)
        b = (cat.get("base") or {}).get(f"1D|{sd}") or {}
        L.append(f"📊 تاريخياً {'صعد' if sd > 0 else 'هبط'} السعر بعده {r['h']:.0f}% من المرات خلال {SG_HZN['1D']} (العشوائي {float(b.get('ht') or 0):.0f}%)")
    L.append("التحليل الكامل في نافذة 📊 المؤشرات")
    return {"sym": sym, "ty": "nst", "f": "1D", "t": L[0], "b": "\n".join(L[1:]), "h": 0}


def sg_record():
    """📜 v3.36.69: سجل المحلل (كل ما أُطلق وحُكم) — للسحب ملفاً · ونسبة ما وصلك لكل شهر ولكل مدة"""
    st, cat = _sg_st(), _sg_cat() or {}
    idx = cat.get("idx") or {}
    rows = []
    for d in st.get("done") or []:
        try:
            eid, sym, ts, x, flag = d[0], d[1], int(d[2]), float(d[3]), int(d[4])
            fr, side = eid.split("|")[0], int(eid.split("|")[1])
        except Exception:
            continue
        e = idx.get(eid) or {}
        nm = " + ".join(_sg_name(k, side) for k in e.get("k", [])) or eid.split("|", 2)[-1]
        rows.append([time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts)), sym, "دخول شراء" if side > 0 else "دخول بيع", SG_HZW.get(fr, fr), nm,
                     "✅" if x > 0 else "❌", round(x * 100, 2), "نعم" if flag else "لا"])
    return {"ok": True, "rows": rows, "mon": _sg_mon(st), "pend": len(st.get("pend") or [])}


def _sg_mon(st, months=6):
    """✅ نسبة الصح لما وصلك — لكل شهر ولكل مدة (غداً · الشهر القادم)"""
    M = {}
    for d in st.get("done") or []:
        try:
            if not int(d[4]):
                continue
            fr = d[0].split("|")[0]
            mk = time.strftime("%Y-%m", time.gmtime(int(d[2])))
            v = M.setdefault(mk, {}).setdefault(fr, [0, 0])
            v[0] += 1
            v[1] += 1 if float(d[3]) > 0 else 0
        except Exception:
            continue
    return [[k, M[k]] for k in sorted(M, reverse=True)[:months]]
'''

R = [
    ("""          "sig": ("إشارة واحدة", "إشارتان", "إشارات", "إشارة"), "case": ("حالة واحدة", "حالتين", "حالات", "حالة")}""",
     """          "sig": ("إشارة واحدة", "إشارتان", "إشارات", "إشارة"), "case": ("حالة واحدة", "حالتين", "حالات", "حالة"),
          "grp": ("مجموعة واحدة", "مجموعتان", "مجموعات", "مجموعة")}"""),
    ("""SG_COIN_TY = ("buy", "sell", "acc", "dist", "up", "down")""",
     """SG_COIN_TY = ("buy", "sell", "acc", "dist", "up", "down")
SG_TY["nst"] = ("🔎", "الآن في السوق")                    # 🔎 v3.36.69: حالة جديدة على عملة من عملاتك (وصف لا توقع)"""),
    # the switches by direction
    ("""    if not cfg["types"].get(e.get("ty") or "buy", True) or not cfg["fr"].get(e["f"], True):
        return False
    if not e.get("c4"):""",
     """    if not cfg["types"].get(_sg_tyk(e), True) or not cfg["fr"].get(e["f"], True):
        return False
    if not e.get("c4"):"""),
    ("""                if ok:
                    groups.setdefault((sym, e["ty"], fr), []).append(e)""",
     """                if ok:
                    groups.setdefault((sym, _sg_tyk(e), fr), []).append(e)"""),
    # 🔎 a new state on a coin of yours
    ("""            for code in SG_NST:
                for sd in (1, -1):
                    if f"{code}:{sd}" in A1:
                        nst[f"{fr}|{code}"] = [sd, x["t"]]""",
     """            for code in SG_NST:
                for sd in (1, -1):
                    if f"{code}:{sd}" in A1:
                        nst[f"{fr}|{code}"] = [sd, x["t"]]
                        if fr == "1D" and f"{code}:{sd}" not in A0 and sym in mine and cfg["types"].get("nst", True):
                            nst_new.append((sym, code, sd))"""),
    ("""    groups = {}
    mk_fired = {}""", """    groups = {}
    mk_fired = {}
    nst_new = []"""),
    ("""    # 🌊 · 😨 · 🗞️ — مرة لكل حدث (من سجل الإشارة نفسها في الدليل)
    for (ty, code, side), e in mk_fired.items():
        if not cfg["types"].get(ty, True):
            continue""",
     """    for sym, code, sd in nst_new:                             # 🔎 v3.36.69: الآن في السوق — مرة في اليوم على الأكثر لكل قراءة
        sk = f"nst|{sym}|{code}"
        if now - float((sent.get(sk) or [0])[0]) < 86400:
            continue
        sent[sk] = [round(now), 0]
        blocks.append(_sg_nst_block(sym, code, sd, st, cat))
    # 🌊 · 😨 · 🗞️ — مرة لكل حدث (من سجل الإشارة نفسها في الدليل)
    for (ty, code, side), e in mk_fired.items():
        if not cfg["types"].get(ty, True):
            continue
        if ty != "crash" and not e.get("c4"):                 # 🧠 v3.36.69: قراءة لم تصدق في الفترات الأربع لا تصل (الانهيار حقيقة تُذكر)
            continue"""),
    ("""    blocks.sort(key=lambda b: (b["ty"] not in ("buy", "up", "sell", "down"), -float(b.get("h") or 0)))""",
     """    blocks.sort(key=lambda b: (b["ty"] not in ("buy", "sell"), b["ty"] == "nst", -float(b.get("h") or 0)))"""),
    # the estimate follows the same rules
    ("""            if cfg["types"].get(e["ty"], True) and (e["ty"] != "crash" or e["f"] == "4H"):""",
     """            if cfg["types"].get(e["ty"], True) and (e["ty"] != "crash" or e["f"] == "4H") and (e["ty"] == "crash" or e.get("c4")):"""),
    ("""                grp.add((ci, e["ty"], e["f"], t))""", """                grp.add((ci, _sg_tyk(e), e["f"], t))"""),
    # the record
    ("""            del hist[400:]""", """            del hist[3000:]                                   # 📜 v3.36.69: السجل يُسحب ملفاً — يحفظ 3000"""),
    ("""            if act == "sg_test":""",
     """            if act == "sg_rec":                           # 📜 v3.36.69: سجل المحلل للسحب ملفاً
                return self._json(sg_record())
            if act == "sg_test":"""),
    ("""                            for d in (st.get("done") or []) if d[4]][:40]}""",
     """                            for d in (st.get("done") or []) if d[4]][:40], "mon": _sg_mon(st)}"""),
    # 🔮 the analyst's summary per coin
    ("""        x = _sg_coin_rows(r.get("sym"), st, cat, cfg, 4)
        r["sig"] = x""",
     """        x = _sg_coin_rows(r.get("sym"), st, cat, cfg, 4)
        r["sig"] = x
        F_ = (st.get("now") or {}).get(r.get("sym"))
        if F_:
            r["an"] = _safe(_sg_analyst, r.get("sym"), F_, st, cat, cfg, default=None)     # 🧠 v3.36.69: ملخص المحلل"""),
    # page: the settings — two switches for your coins · the market
    ("""  return `<div class="ind-al${c.on?'':' off'}"><div class="ind-al-h"><b>🎯 إشعارات الإشارات <small""",
     """  return `<div class="ind-al${c.on?'':' off'}"><div class="ind-al-h"><b>🔔 إشعارات المحلل <small"""),
    ("""    <div class="sg-set"><div class="sg-sh">✅ الأنواع</div><div class="sg-flt">${Object.entries(ty).map(([k,t])=>`<button class="${T[k]!==false?'on':''}" onclick="sgSet({types:{${k}:${T[k]===false}}})">${t[0]} ${gEsc(t[1])}</button>`).join('')}</div>
      <div class="ind-sub">🧭 السوق: حين يثبت وضع جديد · 🌊 الانهيار: مرة واحدة في اليوم على الأكثر · ✅ النتائج: بعد وقت كل إشارة وصلتك</div></div>""",
     """    <div class="sg-set"><div class="sg-sh">🪙 عملاتك</div><div class="sg-flt">${[['buy','🟢 دخول شراء'],['sell','🔴 دخول بيع'],['nst','🔎 الآن في السوق']].map(([k,t])=>`<button class="${T[k]!==false?'on':''}" onclick="sgSet({types:{${k}:${T[k]===false}}})">${t}</button>`).join('')}</div>
      <div class="ind-sub">🟢 و🔴: حين تتفق مجموعة مؤشرات مثبتة (غداً أو الشهر القادم) — تحليل لا أسعار · 🔎: حالة جديدة (تجميع · تصريف · شراء أو بيع عدواني · ازدحام) — وصف لا توقع</div>
      <div class="sg-sh" style="margin-top:8px">🌐 السوق كله</div><div class="sg-flt">${['mkt','crash','fng','eco','res'].filter(k=>ty[k]).map(k=>`<button class="${T[k]!==false?'on':''}" onclick="sgSet({types:{${k}:${T[k]===false}}})">${ty[k][0]} ${gEsc(ty[k][1])}</button>`).join('')}</div>
      <div class="ind-sub">🧭 السوق: حين يثبت وضع جديد · 🌊 الانهيار: مرة في اليوم على الأكثر · 😨 🗞️: فقط إذا صدقت القراءة نفسها في الفترات الأربع · ✅ النتائج: بعد وقت كل إشعار وصلك</div></div>"""),
    # page: the record — month by month · 📥
    ("""  return `<div class="ind-sub">📒 السجل الحي: حُكم عليها ${lv.done||0} · تنتظر وقتها ${lv.pend||0} (كل ما أُطلق على عملات القياس — لا ما وصلك فقط)</div>""",
     """  const mon=(lv.mon||[]).map(([k,v])=>`<div class="sg-lg"><b>${gEsc(k)}</b> · ${[['4H','غداً'],['1D','الشهر القادم']].map(([f,n])=>v[f]?`${n}: <b>${Math.round(v[f][1]/v[f][0]*100)}%</b> <small>(${v[f][1]} من ${v[f][0]})</small>`:`${n}: —`).join(' · ')}</div>`).join('');
  return `<div class="ind-sub">📒 السجل الحي: حُكم عليها ${lv.done||0} · تنتظر وقتها ${lv.pend||0} (كل ما أُطلق على عملات القياس — لا ما وصلك فقط) · ✅ إذا لمس الهدف قبل الوقف أو انتهت المدة بالاتجاه الصحيح</div>
    <div class="an-more" style="text-align:right"><button onclick="sgRecDl()">📥 سحب السجل</button></div>
    <div class="sg-frh">📅 دقة ما وصلك — كل شهر</div>${mon||'<div class="ind-sub">تظهر بعد أول نتيجة</div>'}"""),
    ("""'<div class="ind-sub">لا نتائج بعد — تُحكم كل إشارة بعد وقتها (3 أيام أو أسبوع)</div>'""",
     """'<div class="ind-sub">لا نتائج بعد — يُحكم كل إشعار بعد وقته (غداً أو بعد شهر)</div>'"""),
    ("""async function sgTest(){""",
     """async function sgRecDl(){try{const r=await api('/api/control',{action:'sg_rec'});if(!r||!r.ok)return toast('تعذّر تحميل السجل',false);   // 📥 v3.36.69
  const esc=v=>{v=String(v);return /[",\\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v};
  const rows=[['التاريخ (UTC)','العملة','الاتجاه','المدة','المجموعة','النتيجة','الربح %','وصلك إشعارها'].join(',')].concat((r.rows||[]).map(x=>x.map(esc).join(',')));
  if(await holySave(new Blob(['\\ufeff'+rows.join('\\r\\n')],{type:'text/csv;charset=utf-8'}),'holy_analyst_record.csv'))toast('⬇️ حُفظ السجل ('+(r.rows||[]).length+')',true)}catch(e){toast('تعذر الاتصال',false)}}
async function sgTest(){"""),
    # page: 🔮 the analyst's summary line
    ("""function sgFc(r){const S=r.sig;if(!S)return '';const fs=['1D','4H'].filter(f=>S[f]&&(S[f].rows||[]).length);if(!fs.length)return '';""",
     """function sgFcAn(r){const A=r.an;if(!A)return '';const H=A.hz||{},z=(x,n)=>x&&x.dir?`${n}: ${x.dir>0?'📈':'📉'} ${x.h}%`:`${n}: —`;    // 🧠 v3.36.69
  return `<div class="sg-fc an-fc" onclick="event.stopPropagation();openInd('an')">🧠 <b>ملخص المحلل:</b> ${gEsc(A.wi||'')} ${gEsc(A.wt||'')} · ${z(H['4H'],'غداً')} · ${z(H['1D'],'الشهر القادم')} ←</div>`}
function sgFc(r){const S=r.sig;const an=sgFcAn(r);if(!S)return an;const fs=['1D','4H'].filter(f=>S[f]&&(S[f].rows||[]).length);if(!fs.length)return an;"""),
    ("""    ${best?`<small> — أقواها: ${gEsc(best.nm.join(' + '))} (صدقت ${best.w} من ${sgAr(best.n,'time')} · ${(+best.h).toFixed(0)}%)</small>`:''}</div>`}""",
     """    ${best?`<small> — أقواها: ${gEsc(best.nm.join(' + '))} (صدقت ${best.w} من ${sgAr(best.n,'time')} · ${(+best.h).toFixed(0)}%)</small>`:''}</div>`.replace(/^/,an)}"""),
    # page: the ticker's mini panel
    ("""<b>🎯 إشعارات الإشارات — شراء · بيع · تجميع · تصريف · صعود · نزول · السوق</b>""",
     """<b>🔔 إشعارات المحلل — 🟢 دخول شراء · 🔴 دخول بيع · 🔎 الآن في السوق · 🌐 السوق</b>"""),
    ("""<button onclick="openSig('now')">🎯 الآن</button></span></div>
  <div class="ind-sub" style="margin-top:6px">كل إشارة وكل تركيبة (2 … 6 معاً) بسجلها على الأسعار الحقيقية · تصلك بالنسبة وعدد المرات اللي تختارهما · مع تقدير كم إشعاراً بالأسبوع قبل أن تختار</div></div>`}""",
     """<button onclick="openInd('an')">🧠 المحلل</button></span></div>
  <div class="ind-sub" style="margin-top:6px">فقط مجموعات مؤشرات متفقة صدقت في الفترات الأربع من تاريخ الأسعار الحقيقية · تصلك بالدقة التي تختارها · مع تقدير كم إشعاراً بالأسبوع قبل أن تختار</div></div>`}"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a = s.index("def _sg_block(sym, ty, fr, ents, st, cat, scan, comp):")
    b = s.index("\n\ndef _sg_chunks(", a)
    s = s[:a] + NEW_BLOCK.rstrip() + "\n" + s[b:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the analyst's notification · 🔎 the state now · 📜 the record (📥) · 🧠 in 🔮 · {p}")
