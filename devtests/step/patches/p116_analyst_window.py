# 🧠 patch 116 (dashboard v3.36.69 · the analyst's window). The owner (20-11): «المؤشرات نفسها تصير المحلل · التوقعات تبقى زر ثاني ·
#   السوق كله: حالياً شديصير بالعملة بالمنصات شراء او بيع او تصريف وغيرها · الاخر للعملة بس فيه دخول شراء او بيع · خليهم بالنافذة فقط».
#   · ONE window: 📊 «المؤشرات — المحلل» (the old 🎯 window is merged into it — openSig opens it, so every old button and notification tap
#     still works) · tabs: 🧠 المحلل (first) · 📈 المؤشرات العشرة (the old reading, unchanged) · 🎯 الإشارات الشغّالة · 📚 المجموعات ·
#     📜 السجل · ⚙️ الإشعارات
#   · 🧠 المحلل: 🌐 the market now (the compass · what a month gave in this state · a crash now · fear & greed) · then a card for each of
#     your coins: one word (🟢 فرصة شراء · 🟢 فرصة شراء بحذر · ⏸️ انتظر · 🟠 تجنّب الشراء الآن · 🔴 خطر نزول) · «غداً» and «الشهر القادم»
#     (direction · accuracy · expected range · why in plain words · entry/target/stop — in the window only) · 🔎 الآن في السوق (accumulation ·
#     distribution · aggressive buying/selling · crowding · stronger/weaker than BTC · the trend) — a description, not a forecast
#   · the live firing follows the owner's rule too: a group is «on» only when all its signals agree and none of the other side is on
#   · no 💎 in the page any more (the catalog proves nothing on a handful of cases)
#   python3 devtests/step/patches/p116_analyst_window.py Holy_Dashboard.pyw
import os, sys

PY_FUNCS = r'''
SG_NST = ("X-ad", "X-adt", "P-tk", "P-ls", "X-rs")           # 🔎 «الآن في السوق» — وصف للحاضر
SG_NST_AGE = {"4H": 3 * 86400, "1D": 14 * 86400}
SG_WHY = {"trend": ("الاتجاه العام صاعد", "الاتجاه العام هابط"),
          "momentum": ("قوة الحركة تميل إلى الصعود", "قوة الحركة تميل إلى الهبوط"),
          "volatility": ("ارتداد من منطقة ضغط سعري", "تراجع من منطقة تشبّع"),
          "pattern": ("شكل الشموع يدعم الصعود", "شكل الشموع يدعم الهبوط"),
          "volume": ("السيولة تدخل العملة", "السيولة تخرج من العملة"),
          "market": ("حالة السوق كله تساعد", "حالة السوق كله ضاغطة")}
SG_WORD = {"buy": ("🟢", "فرصة شراء"), "buyc": ("🟢", "فرصة شراء بحذر"), "wait": ("⏸️", "انتظر"),
           "avoid": ("🟠", "تجنّب الشراء الآن"), "risk": ("🔴", "خطر نزول")}


def _sg_strict_on(e, A):
    """🤝 v3.36.69: المجموعة شغّالة = كل إشاراتها في A بجهتها ولا إشارة من الجهة المعاكسة (عدا 🌊 · قراءة السوق وحدها تصف السوق)"""
    if not all(f"{k}:{e['s']}" in A for k in e["k"]):
        return False
    if len(e["k"]) == 1 and e["k"][0].startswith(("W-", "M-")):
        return True
    o = f":{-e['s']}"
    return not any(a.endswith(o) and not a.startswith("W-crash:") for a in A)


def _sg_analyst(sym, F, st, cat, cfg):
    """🧠 v3.36.69: المحلل لعملة — كلمة واحدة · غداً والشهر القادم (الاتجاه · الدقة · المدى · لماذا · الدخول والهدف والوقف) · الآن في السوق"""
    idx = cat.get("idx") or {}
    M = _sg_meta()
    best = {}
    for fr in SG_FR:
        for i in (F.get(fr) or {}).get("alive") or []:
            e = idx.get(i)
            if not e or not e.get("c4"):
                continue
            r = _sg_rec(e, st)
            k = (fr, e["s"])
            if k not in best or (r["h"], r["n"]) > (best[k][1]["h"], best[k][1]["n"]):
                best[k] = (e, r)

    def top(c):
        return max(c, key=lambda z: (z[1]["h"], z[1]["n"])) if c else None
    B, S = top([v for k, v in best.items() if k[1] > 0]), top([v for k, v in best.items() if k[1] < 0])
    if B and not S:
        w = "buy" if B[1]["h"] >= 60 else "buyc"
    elif S and not B:
        w = "risk" if S[1]["h"] >= 60 else "avoid"
    elif B and S:
        d = B[1]["h"] - S[1]["h"]
        w = "buyc" if d >= 10 else "avoid" if d <= -10 else "wait"
    else:
        w = "wait"
    hz = {}
    for fr in SG_FR:
        x = F.get(fr) or {}
        px, s = float(x.get("px") or 0), float(x.get("s") or 0)
        c = top([v for k, v in best.items() if k[0] == fr])
        if not c:
            hz[fr] = {"dir": 0, "px": px, "s": s}
            continue
        e, r = c
        sd, fams = e["s"], []
        for k in e["k"]:
            f = (M.get(k) or ("other",))[0]
            if f in SG_WHY and f not in fams:
                fams.append(f)
        hz[fr] = {"dir": sd, "h": round(r["h"]), "n": r["n"], "px": px, "s": s, "id": e["id"],
                  "tgt": px * (1 + s * sd) if px and s else None, "stop": px * (1 - s * sd) if px and s else None,
                  "why": [SG_WHY[f][0 if sd > 0 else 1] for f in fams], "nm": [_sg_name(k, sd) for k in e["k"]],
                  "two": any(k[0] == fr and k[1] == -sd for k in best)}
    tref = max([int((F.get(fr) or {}).get("t") or 0) for fr in SG_FR] or [0])
    seen = {}
    for key, v in ((st.get("nst") or {}).get(sym) or {}).items():
        try:
            fr, code = key.split("|", 1)
            sd, t = int(v[0]), int(v[1])
        except Exception:
            continue
        if fr not in SG_SEC or tref - t > SG_NST_AGE[fr]:
            continue
        if code in seen and seen[code][1] >= t:
            continue
        e = idx.get(f"{fr}|{sd}|{code}")
        note = ""
        if e and e["nt"] >= 10:
            r = _sg_rec(e, st)
            b = (cat.get("base") or {}).get(f"{fr}|{sd}") or {}
            note = (f"تاريخياً {'صعد' if sd > 0 else 'هبط'} السعر بعده {r['h']:.0f}% من المرات خلال {SG_HZN[fr]} "
                    f"(العشوائي {float(b.get('ht') or 0):.0f}%)")
        seen[code] = (_sg_name(code, sd), t, note, sd)
    d = F.get("1D") or {}
    tr = None
    if d.get("px") and d.get("m50") and d.get("m200"):
        a1, a2 = d["px"] > d["m50"], d["px"] > d["m200"]
        tr = ("📈 السعر فوق متوسطي 50 و200 يوم — اتجاه صاعد" if a1 and a2 else "📉 السعر تحت متوسطي 50 و200 يوم — اتجاه هابط" if not a1 and not a2
              else "↔️ السعر بين متوسطي 50 و200 يوم — الاتجاه غير محسوم")
    return {"w": w, "wi": SG_WORD[w][0], "wt": SG_WORD[w][1], "hz": hz, "tr": tr,
            "nst": [[n, t, note, sd] for n, t, note, sd in sorted(seen.values(), key=lambda z: -z[1])]}


def sg_view():'''

JS_FUNCS = r'''const SGW={buy:'p',buyc:'p',wait:'z',avoid:'w',risk:'n'};
function sgPxR(x){return x!=null&&isFinite(+x)&&+x>0?fmtPx(+x):'—'}
function sgHz(z,lbl,V,mon){const C=V.comp||{},nm=SGCOMP[C.s];
  if(!z||!z.dir)return `<div class="an-hz"><b>${lbl}</b>: لا توجد الآن مجموعة مؤشرات مثبتة تتفق على اتجاه${mon&&nm&&C.m30!=null?`<div class="ind-sub">السوق ${nm[0]}: تاريخياً كان متوسط الشهر التالي في هذا الوضع ${sgPct(C.m30)} — ثقة منخفضة</div>`:''}</div>`;
  const up=z.dir>0;
  return `<div class="an-hz ${up?'p':'n'}"><b>${lbl}</b>: ${up?'📈 صعود':'📉 هبوط'} · دقة <b>${z.h}%</b> <small>(من ${sgAr(z.n,'time')})</small>${z.s?` · المدى المتوقع ${sgPxR(z.px*(1-z.s))} – ${sgPxR(z.px*(1+z.s))}`:''}
    ${(z.why||[]).length?`<div class="ind-sub">لماذا: ${z.why.map(gEsc).join(' · ')}</div>`:''}${z.two?'<div class="ind-sub" style="color:var(--amber)">⚠️ توجد أيضاً مجموعة بالاتجاه المعاكس</div>':''}
    ${z.tgt?`<div class="an-lv">💵 الدخول ${sgPxR(z.px)} · 🎯 الهدف ${sgPxR(z.tgt)} · 🛑 الوقف ${sgPxR(z.stop)}</div>`:''}</div>`}
function sgAnCoin(x,V){const A=x.an||{},H=A.hz||{},F=x.fr||{},px=(F['4H']||F['1D']||{}).px,c=SGW[A.w]||'z';
  const ns=(A.nst||[]).map(n=>`<div class="an-st">${gEsc(n[0])} <small>· ${n[1]?gAgo(n[1]):''}${n[2]?' · '+gEsc(n[2]):''}</small></div>`).join('');
  return `<div class="ind-c an-c ${c}"><div class="ind-h"><span class="cn">${gEsc(x.base)}</span>${px?`<span class="px">${fmtPx(px)}</span>`:''}<span class="an-w ${c}">${gEsc(A.wi||'⏸️')} ${gEsc(A.wt||'انتظر')}</span></div>
    ${sgHz(H['4H'],'غداً',V,false)}${sgHz(H['1D'],'الشهر القادم',V,true)}
    <div class="an-now"><div class="sg-frh">🔎 الآن في السوق</div>${A.tr?`<div class="an-st">${gEsc(A.tr)}</div>`:''}${ns||'<div class="ind-sub">لا جديد في السيولة أو العقود في الأيام الأخيرة</div>'}<div class="ind-sub">وصف لما يحدث الآن — ليس توقعاً</div></div>
    <div class="an-more"><button onclick="SGO['${gEsc(x.sym)}']=true;sgTab('now')">كل الإشارات الشغّالة ←</button></div></div>`}
function sgAnMkt(V){const C=V.comp,M=V.mkt||{};let h='<div class="an-mkt"><div class="sg-frh">🌐 السوق كله الآن</div>';
  if(C&&SGCOMP[C.s]){const nm=SGCOMP[C.s];h+=`<div class="an-st"><b>🧭 ${nm[1]} ${nm[0]}</b> <small>منذ ${sgAr(C.days,'day')}</small> · البيتكوين ${C.btc?'فوق':'تحت'} متوسط 200 يوم · ${C.k} من ${sgAr(C.n,'coin')} فوق متوسطها (50 يوماً)</div>
    ${C.m30!=null?`<div class="ind-sub">تاريخياً في هذا الوضع: متوسط الشهر التالي ${sgPct(C.m30)}${C.h30!=null?` · كان السعر أعلى بعد شهر في ${(+C.h30).toFixed(0)}% من الأيام`:''}</div>`:''}
    <div class="sg-hist" title="آخر 60 يوماً — 🟢 صاعد · 🟡 مختلط · 🔴 نازل">${(C.hist||[]).map(x=>`<i class="${gEsc(x[2])}"></i>`).join('')}</div>`}
  else h+='<div class="ind-sub">حالة السوق تظهر بعد أول فحص</div>';
  if(M.crash&&M.crash.on)h+=`<div class="an-st" style="color:var(--red)">🌊 انهيار في السوق كله الآن: ${M.crash.k} من ${sgAr(M.crash.n,'coin')} هبطت بقوة</div>`;
  if(M.fng!=null)h+=`<div class="an-st">😨 الخوف والطمع: <b>${M.fng}</b>${M.fng<=25?' — خوف شديد':M.fng>=75?' — طمع شديد':''}</div>`;
  return h+'</div>'}
function sgAn(V){const B=V.busy||{};let h='';
  if(B.phase)h+=`<div class="sg-busy">${gEsc(B.msg||'…')}<div class="sg-pb"><i style="width:${Math.max(3,+B.pct||0)}%"></i></div></div>`;
  if(V.err)h+=`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(V.err)}</div>`;
  h+=sgAnMkt(V);
  if(!V.cat)return h+`<div class="sg-empty">🏗️ <b>أول مرة:</b> تُجلب شموع العملات (سنتان على 4 ساعات ونحو 7 سنوات يومية) ثم يُبحث عن مجموعات المؤشرات المتفقة التي صدقت في كل فترات التاريخ — بعملية منفصلة لا تُثقل اللوحة، مرة واحدة.</div>`;
  const N=(V.now||[]).filter(x=>x.mine);
  h+=N.length?`<div class="ind-list">${N.map(x=>sgAnCoin(x,V)).join('')}</div>`:'<div class="sg-empty">🔍 أول تحليل عند إغلاق شمعة 4 ساعات القادمة — واختر عملاتك من ⚙️ الإشعارات</div>';
  h+=`<details class="ind-help"><summary>كيف يعمل المحلل؟</summary>
    <div>• يعتمد فقط على <b>مجموعات مؤشرات محددة تتفق</b> — كلها بالاتجاه نفسه ولا مؤشر معاكس — وقد <b>صدقت في الفترات الأربع</b> من تاريخ الأسعار الحقيقية، لا على مؤشر وحده ولا على اختيار عشوائي.</div>
    <div>• <b>الدقة</b>: كم مرة لمس السعر الهدف قبل الوقف (أو انتهت المدة بالاتجاه الصحيح بعد العمولة) على كل التاريخ ثم السجل الحي. الهدف والوقف من تذبذب العملة نفسها.</div>
    <div>• <b>غداً</b> من شموع 4 ساعات · <b>الشهر القادم</b> من الشموع اليومية · لا توقع للساعات القليلة القادمة: القياس وجده أضعف من الصدفة.</div>
    <div>• <b>🔎 الآن في السوق</b>: وصف لما يحدث (تجميع · تصريف · شراء أو بيع عدواني · ازدحام · القوة مقابل البيتكوين) وليس توقعاً.</div>
    <div style="color:var(--amber);margin-top:6px">⚠️ احتمالات لا ضمانات — أفضل دقة مقاسة بين 55% و65% · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;
  return h}
function sgRender(){'''

R = [
    # server: the live firing follows the owner's rule · the coin's state now is kept
    ("""                ks = [f"{k}:{e['s']}" for k in e["k"]]
                if not all(k in A1 for k in ks):
                    continue
                alive.append(e["id"])
                if all(k in A0 for k in ks):
                    continue""",
     """                if not _sg_strict_on(e, A1):                  # 🤝 v3.36.69: كلها متفقة ولا إشارة معاكسة (مثل البحث)
                    continue
                alive.append(e["id"])
                if _sg_strict_on(e, A0):
                    continue"""),
    ("""            nowv.setdefault(sym, {})[fr] = {"t": x["t"], "px": x["px"], "alive": alive, "fired": [e["id"] for e in fired], "lo": x.get("lo"), "hi": x.get("hi")}""",
     """            nowv.setdefault(sym, {})[fr] = {"t": x["t"], "px": x["px"], "alive": alive, "fired": [e["id"] for e in fired], "lo": x.get("lo"), "hi": x.get("hi"),
                                            "s": x.get("s"), "m50": x.get("m50"), "m200": x.get("m200")}
            nst = st.setdefault("nst", {}).setdefault(sym, {})              # 🔎 v3.36.69: «الآن في السوق» (آخر حالة لكل قراءة)
            for code in SG_NST:
                for sd in (1, -1):
                    if f"{code}:{sd}" in A1:
                        nst[f"{fr}|{code}"] = [sd, x["t"]]"""),
    ("""            res.setdefault(sym, {})[fr] = {"t": D["T"][i], "px": D["C"][i], "s": round(_sg_sig(D["C"][-(SG_W + 2):], SG_HZ[fr])[-1], 5),""",
     """            res.setdefault(sym, {})[fr] = {"t": D["T"][i], "px": D["C"][i], "s": round(_sg_sig(D["C"][-(SG_W + 2):], SG_HZ[fr])[-1], 5),
                                           "m50": sum(D["C"][-50:]) / 50.0 if D["n"] >= 50 else None,
                                           "m200": sum(D["C"][-200:]) / 200.0 if D["n"] >= 200 else None,"""),
    ("""        it = {"sym": sym, "base": sym.split("-")[0], "mine": sym in mine, "fr": {}}""",
     """        it = {"sym": sym, "base": sym.split("-")[0], "mine": sym in mine, "fr": {}, "an": _safe(_sg_analyst, sym, F, st, cat, cfg, default=None)}"""),
    ("""    v["est"] = sg_estimate(cfg, st)""",
     """    v["est"] = sg_estimate(cfg, st)
    _fg = _safe(_sg_fng_raw, _safe(_fc_db, default={}), default=None)
    v["mkt"] = {"crash": st.get("crash"), "fng": int(_fg[1][-1]) if _fg and _fg[1] else None}     # 🌐 v3.36.69"""),
    # page: one window
    ("""let SGV=null,SGT=null,SGTAB='now',""", """let SGV=null,SGT=null,SGTAB='an',"""),
    ("""async function openInd(){
  showModal(`<h2>📊 المؤشرات — هل تصعد العملة أم تهبط؟</h2><div id="ind_body" style="color:var(--mut);font-size:12.5px;padding:16px;text-align:center">${LDR('جاري الحساب…')}</div>
    <div class="mbtns"><button onclick="openSig()">🎯 الإشارات</button><button onclick="openGuide('','ind')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await indLoad()}""",
     """async function openInd(tab){SGTAB=tab||'an';                                   // 🧠 v3.36.69: نافذة واحدة — المؤشرات هي المحلل (🎯 بداخلها)
  showModal(`<h2>📊 المؤشرات — المحلل</h2><div class="sg-tabs" id="sg_tabs"></div><div id="sg_body" style="color:var(--mut);font-size:12.5px;padding:16px;text-align:center">${LDR('جاري التحميل…')}</div>
    <div class="mbtns"><button onclick="openFc()">🔮 التوقعات</button><button onclick="openGuide('','ind')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await sgLoad()}"""),
    ("""async function openSig(tab){if(tab)SGTAB=tab;
  showModal(`<h2>🎯 الإشارات — كل المؤشرات وتركيباتها بسجلها</h2><div class="sg-tabs" id="sg_tabs"></div><div id="sg_body" style="color:var(--mut);font-size:12.5px;padding:16px;text-align:center">${LDR('جاري التحميل…')}</div>
    <div class="mbtns"><button onclick="openFc()">🔮 التوقعات</button><button onclick="openInd()">📊 المؤشرات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await sgLoad()}""",
     """async function openSig(tab){return openInd(tab||'an')}                          // (الاسم القديم: الأزرار وضغط الإشعارات تفتح المحلل)"""),
    ("""  if(tb)tb.innerHTML=[['now','🎯 الآن'],['cat','📒 الدليل'],['log','🧾 السجل'],['cfg','⚙️ الإشعارات']].map(([k,t])=>`<button class="${SGTAB===k?'on':''}" onclick="sgTab('${k}')">${t}</button>`).join('');
  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل الإشارات';return}
  el.style.cssText='text-align:right';
  el.innerHTML=SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgNow(V)}""",
     """  if(tb)tb.innerHTML=[['an','🧠 المحلل'],['ind','📈 المؤشرات العشرة'],['now','🎯 الإشارات الشغّالة'],['cat','📚 المجموعات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']].map(([k,t])=>`<button class="${SGTAB===k?'on':''}" onclick="sgTab('${k}')">${t}</button>`).join('');
  if(SGTAB==='ind'){el.style.cssText='text-align:right';if(!$('#ind_body')){el.innerHTML=`<div id="ind_body">${LDR('جاري الحساب…')}</div>`;indLoad()}return}
  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل المحلل';return}
  el.style.cssText='text-align:right';
  el.innerHTML=SGTAB==='an'?sgAn(V):SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgNow(V)}"""),
    # no 💎 in the page · the texts follow the new rule
    ("""  if(!V.cat)return h+`<div class="sg-empty">🏗️ <b>أول مرة:</b> تُجلب شموع ~${(V.uni||[]).length} عملة (سنتان على 4 ساعات و3 سنوات يومية) ثم تُحسب كل الإشارات وتُبحث تركيباتها""",
     """  if(!V.cat)return h+`<div class="sg-empty">🏗️ <b>أول مرة:</b> تُجلب شموع ~${(V.uni||[]).length} عملة (سنتان على 4 ساعات ونحو 7 سنوات يومية) ثم تُحسب كل الإشارات وتُبحث مجموعاتها المتفقة"""),
    ("""<span class="ind-chip">📒 ${V.cat.n} إشارة وتركيبة · 💎 ${V.cat.nrare} نادرة</span>""",
     """<span class="ind-chip">📚 ${V.cat.n} إشارة ومجموعة</span>"""),
    ("""    <div>• السجل من <b>آخر 40% من التاريخ</b> — فترة لم تُختر عليها التركيبة — ثم <b>السجل الحي</b> منذ تشغيل اللوحة (يُحكم وحده). 💎 النادرة: سجلها كل التاريخ لأن حالاتها قليلة.</div>""",
     """    <div>• السجل من <b>كل التاريخ مقسوماً أربع فترات</b> — لا تُعتمد مجموعة إلا إذا صدقت في كل فترة — ثم <b>السجل الحي</b> منذ تشغيل اللوحة (يُحكم وحده بالهدف والوقف).</div>"""),
    ("""(منها ${C.ncombo} تركيبة · 💎 ${C.nrare} نادرة)""", """(منها ${C.ncombo} مجموعة متفقة صدقت في الفترات الأربع)"""),
    ("""${b('size','4','4 فأكثر')}${b('rare','1','💎 النادرة فقط')}${SGF.rare?b('rare','','✕ النادرة'):''}</div>""",
     """${b('size','4','4 فأكثر')}</div>"""),
    ("""    <div class="sg-set">${tg(c.rare,`sgSet({rare:${!c.rare}})`,'💎 النادرة: تصلك','💎 النادرة: لا تصلك')} <span class="sg-sh">أقل عدد لها: <b id="sg_rmin_v">${c.rmin}</b></span>
      <input type="range" min="3" max="30" step="1" value="${c.rmin}" oninput="sgEst({rmin:+this.value})" onchange="sgSet({rmin:+this.value})"><div class="ind-sub">تركيبات ظهرت مرات قليلة بصدق عالٍ وصمدت على الفترة الجديدة — تصلك بعلامة 💎 وتحذير.</div></div>
""", ""),
    # css
    (""".sg-add{display:flex;gap:6px;margin:6px 0}""",
     """.an-mkt{border:1px solid var(--line2);border-radius:12px;padding:8px 10px;margin:4px 0 10px;background:var(--bg1)}
.an-st{font-size:12.5px;margin:3px 0}.an-hz{font-size:12.5px;margin:6px 0;padding:6px 8px;border-radius:10px;background:var(--bg1)}
.an-hz.p{border-inline-start:3px solid var(--green)}.an-hz.n{border-inline-start:3px solid var(--red)}.an-lv{font-size:12px;margin-top:4px}
.an-w{margin-inline-start:auto;font-weight:700;font-size:12.5px;padding:2px 9px;border-radius:9px;background:var(--bg1)}
.an-w.p{color:var(--green)}.an-w.n{color:var(--red)}.an-w.w{color:var(--amber)}.an-now{margin-top:6px}.an-more{text-align:left;margin-top:6px}
.an-more button{font-size:11.5px;padding:4px 10px;border-radius:9px}
.sg-add{display:flex;gap:6px;margin:6px 0}"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for a, b in (("\ndef sg_view():", PY_FUNCS), ("function sgRender(){", JS_FUNCS)):
        if s.count(a) != 1:
            print(f"❌ anchor {a!r} found {s.count(a)} times"); sys.exit(1)
        s = s.replace(a, b if a.startswith("function") else b, 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the analyst (server + page) · 📊 one window «المؤشرات — المحلل» · no 💎 · {p}")
