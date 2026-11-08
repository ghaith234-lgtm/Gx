# 🔔🎞️ patch 32 (dashboard — apply after p31) — the owner (8-11): «اطفيه» (the turn alert without a proven edge) · «اهم شي من يجيني اشعار
#   له قيمه» · «خلي الشريط المتحرك بالداشبورد ملخص لكل عملة معدل المؤشرات اذا ينزل او يصعد اهم شي يكون مفهوم».
#   🔔 Measured on REAL OKX prices (ci/sig_check.py · 25 coins, a year of hourly candles): the turn alert was right 46.5% vs 50.2% by chance
#      (worse), the squeeze release 46% on its direction and ×0.96 the normal move (nothing); the near-support/resistance alert was never
#      measured. All three are off. The indicator alerts are now the 🟢 bottom alerts (p31's measured reading): a coin entering
#      👀 / 🟡 / 🟢 (sensitivity: quiet = 🟢 only · medium = 🟡 and up · sensitive = 👀 and up), once per level per episode, a new episode
#      alerts even right after a start (an old one stays silent), each with its parts, its 28-coin record, Bitcoin's state, this coin's
#      own record and the honest limit. The forecast loop (where the bottom reading lives) also runs when only the alerts are on.
#   🎞️ The moving indicator strip: per coin the indicators' average in words («↗️ تميل للصعود 7/10» · colour) + what usually followed
#      on the real prices tomorrow when there is a measured edge («غداً ↗️») + the bottom badge (👀 · 🟡 · 🟢) — instead of RSI · volatility
#      · position numbers. Tap/hover = the sentence.
#   python3 devtests/step/patches/p32_alerts_tape.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''INA_SENS = {   # turn: أقل معدل للانقلاب · conf: أقل ثقة · near: قرب الدعم/المقاومة % (0 = بلا) · sq_on: تنبيه بداية الانضغاط
    "low":  {"lbl": "هادئة",  "turn": 45, "conf": 70, "near": 0.0,  "sq_on": False},
    "mid":  {"lbl": "متوسطة", "turn": 30, "conf": 60, "near": 0.35, "sq_on": False},
    "high": {"lbl": "حساسة",  "turn": 15, "conf": 0,  "near": 0.7,  "sq_on": True},
}''',
     '''INA_SENS = {   # 🟢 v3.36.27: «min» = أقل نقاط مؤشر القاع يُبلَّغ بها (هادئة 🟢 فقط · متوسطة 🟡 فأقوى · حساسة 👀 فأقوى) — turn/conf/near/sq_on
    #   بقيت للقياس فقط (ci/sig_check.py): الانقلاب والانضغاط انقاسا على الأسعار الحقيقية بلا قيمة فانطفأت تنبيهاتهما
    "low":  {"lbl": "هادئة",  "min": 60, "turn": 45, "conf": 70, "near": 0.0,  "sq_on": False},
    "mid":  {"lbl": "متوسطة", "min": 50, "turn": 30, "conf": 60, "near": 0.35, "sq_on": False},
    "high": {"lbl": "حساسة",  "min": 30, "turn": 15, "conf": 0,  "near": 0.7,  "sq_on": True},
}
_BOT_RK = {"none": 0, "watch": 1, "zone": 2, "strong": 3}'''),
    ('''    rule = (f"🔄 المؤشرات تنقلب تميل للصعود/النزول (معدل ≥ {S['turn']}" + (f" · ثقة ≥ {S['conf']}%" if S["conf"] else "") + ")"
            + " · ⚡ خروج من الانضغاط" + (" · وبدايته" if S["sq_on"] else "")
            + (f" · 🧱 قرب دعم/مقاومة (≤ {S['near']:g}%)" if S["near"] else "")
            + (f" · حد {c['cap']} باليوم" if c["cap"] else " · بلا حدّ يومي"))   # 📊 v3.36.4: 0 = بلا حد''',
     '''    rule = ("🟢 مؤشر القاع: حين تدخل عملة " + {60: "«🟢 قاع قوي» (60 فأكثر)", 50: "«🟡 منطقة شراء» (50 فأكثر) أو أقوى", 30: "«👀 راقب» (30 فأكثر) أو أقوى"}[S["min"]]
            + " — مرة لكل مستوى في كل نوبة" + (f" · حد {c['cap']} باليوم" if c["cap"] else " · بلا حدّ يومي")
            + " · تنبيهات الانقلاب والانضغاط والدعم/المقاومة متوقفة: لم تثبت لها قيمة على الأسعار الحقيقية")'''),
    ('''    a = {"sym": R.get("sym") or "BTC-USDT", "t": f"🧪 تجربة — 📊 {R.get('base') or 'BTC'}: المؤشرات تميل للصعود ↗️ (7 من 10 · المعدل +32)",
         "b": f"هيج راح توصلك تنبيهات المؤشرات ({INA_SENS[cfg['sens']]['lbl']} · {PXA_CH[cfg['ch']]})", "r": "📏 كل تنبيه بيه صدق المؤشرات على نفس العملة"}''',
     '''    a = {"sym": R.get("sym") or "BTC-USDT", "t": f"🧪 تجربة — 🟡 منطقة شراء — {R.get('base') or 'BTC'}: مؤشر القاع 70/100 (لأيام إلى أسبوعين)",
         "b": f"هكذا تصلك تنبيهات مؤشر القاع ({INA_SENS[cfg['sens']]['lbl']} · {PXA_CH[cfg['ch']]})",
         "r": "🔬 كل تنبيه معه سجله على الأسعار الحقيقية: كم مرة كان السعر أعلى بعد 14 يوماً مقابل الأيام العادية"}'''),
    ('''            if indic_cfg()["on"] and ticker_cfg()["coins"]:
                _fc_run()''',
     '''            if (indic_cfg()["on"] or ina_cfg()["on"]) and ticker_cfg()["coins"]:      # 🟢 v3.36.27: مؤشر القاع للتنبيهات حتى لو الشريط مطفي
                _fc_run()'''),
    ('''        text = f"📊 تنبيهات المؤشرات ({len(al)})\\n"''', '''        text = f"🟢 تنبيهات مؤشر القاع ({len(al)})\\n"'''),
    # ── the panel
    ('''<b>📊 تنبيهات المؤشرات — قبل الحركة <small''', '''<b>🟢 تنبيهات مؤشر القاع — متى أشتري <small'''),
    ('''<div class="ind-sub" style="margin-top:6px">تتفاعل كل 5 دقائق (حتى لو شريط المؤشرات مطفي) · ${gEsc(P.rule||'')} · كل تنبيه بيه صدق المؤشرات على نفس العملة · رسالة لحالها (مو ويّا الأسعار) · بالموبايل قناة «📊 تنبيهات المؤشرات» والضغط يفتح 📊 · اليوم ${P.n_today||0}</div>''',
     '''<div class="ind-sub" style="margin-top:6px">${gEsc(P.rule||'')} · كل تنبيه معه سجله على الأسعار الحقيقية وحالة البيتكوين · رسالة مستقلة عن تنبيهات الأسعار · في الهاتف قناة «📊 تنبيهات المؤشرات» · اليوم ${P.n_today||0}</div>'''),
    # ── the strip: server summary per coin
    ('''            "sum": (globals().get("IND2") or {}).get("summary") or {}}          # 📊 v3.26.6: ⬆️/⬇️ على زر المؤشرات''',
     '''            "sum": (globals().get("IND2") or {}).get("summary") or {},          # 📊 v3.26.6: ⬆️/⬇️ على زر المؤشرات
            "cs": _safe(_tape_sum, default={})}                                  # 🎞️ v3.36.27: ملخص كل عملة للشريط


def _tape_sum():
    """🎞️ v3.36.27: لكل عملة بالشريط: معدل المؤشرات الآن (📊) + ما تبع هذا الميل غداً على الأسعار الحقيقية (🔮 لو فيه فرق مقيس) + مؤشر القاع"""
    out = {}
    I2, F = globals().get("IND2") or {}, globals().get("FC") or {}
    for s, R_ in (I2.get("coins") or {}).items():
        ps = R_.get("parts") or []
        e = {"sc": int(R_.get("score") or 0), "up": sum(1 for p in ps if float(p.get("s") or 0) >= 0.15),
             "dn": sum(1 for p in ps if float(p.get("s") or 0) <= -0.15), "n": len(ps)}
        Fc = (F.get("coins") or {}).get(s) or {}
        b = Fc.get("bot") or {}
        if b.get("lv") in ("watch", "zone", "strong"):
            e["bot"] = {"lv": b["lv"], "s": b.get("score"), "t": b.get("lbl")}
        q = ((Fc.get("h") or {}).get("d") or {}).get("real") or {}
        if q.get("k") in ("up", "dn"):
            e["nx"] = {"k": q["k"], "p": q.get("p"), "b": q.get("base")}
        out[s] = e
    return out'''),
]

BLOCKS = [   # (from, to, new): the text from «from» up to (not including) «to» is replaced — each anchor once, in order
    ('''        parts = R.get("parts") or []
        nz = [p for p in parts if abs(float(p.get("s") or 0)) >= 0.15]''',
     '''        if a and not fresh:''',
     '''        a = None
        b = ((globals().get("FC") or {}).get("coins") or {}).get(sym, {}).get("bot") or {}   # 🟢 v3.36.27: تنبيهات مؤشر القاع فقط
        if b.get("day"):
            ep = int(b["day"]) - int(b.get("since") or 0) * 86400        # يوم بداية النوبة (الإشارة تتغير مرة باليوم: إغلاق يومي)
            if L.get("bot_ep") != ep:
                L["bot_ep"], L["bot_lv"] = ep, 0
            rk = _BOT_RK.get(b.get("lv"), 0)
            if rk and int(b.get("score") or 0) >= S["min"] and rk > int(L.get("bot_lv") or 0):
                L["bot_lv"] = rk
                if fresh and int(b.get("since") or 0) <= 1:
                    fresh = False                                         # نوبة جديدة ⇒ تنبيه حتى بعد التشغيل مباشرة (القديمة تبقى صامتة)
                Rr, Nn, up_ = b.get("real") or {}, b.get("normal") or {}, b.get("btc_up")
                own = (b.get("own") or {}).get(b.get("lv"))
                ctx = ""
                if up_ is not None and Rr.get("up"):
                    ctx = (f"₿ البيتكوين فوق متوسط 200 يوم — في هذا الجو كانت النتيجة أقوى ({Rr['up'][0]}%)" if up_
                           else f"₿ البيتكوين تحت متوسط 200 يوم — في هذا الجو كانت النتيجة أضعف ({Rr['down'][0]}%)")
                a = {"k": "bot", "d": "up", "t": f"{b.get('lbl')} — {base}: مؤشر القاع {int(b.get('score') or 0)}/100 (لأيام إلى أسبوعين)",
                     "b": " · ".join(p["txt"] for p in (b.get("parts") or []) if p.get("on")) + f" · السعر {_px_s(px)}$",
                     "r": (f"🔬 تاريخياً (28 عملة · 2021–2026): أعلى بعد 14 يوماً في {Rr.get('p14')}% من المرات (العادي {Nn.get('p14')}%) · "
                           f"الوسيط {float(Rr.get('m14') or 0):+.1f}%" + (f" · {ctx}" if ctx else "")
                           + (f" · على {base}: {own['p14']}% من {own['n']} مرة" if own else "")
                           + " · قد ينزل أكثر قبل الارتداد — الشراء على دفعات أسلم")}
'''),
    # ── the strip: per coin = the average in words + tomorrow (measured) + the bottom badge
    ('''    const one=rows.map(r=>`<span class="ik" data-s="${gEsc(r.sym)}"><b class="ikb">${gEsc(r.base)}</b>''',
     '''function tkToggle2(){''',
     '''    const one=rows.map(r=>`<span class="ik" data-s="${gEsc(r.sym)}"><b class="ikb">${gEsc(r.base)}</b>
      <i class="iv isum">—</i><i class="iv inx"></i><i class="iv ibot"></i></span>`).join('');
    inn.innerHTML=one+one; inn.dataset.sig=sig;
  }
  if(!TAPES.i)TAPES.i=new Tape($('#tape2 .tapewrap')||el,inn);
  indBtnSync(d);
  TAPES.i.setLoop(Math.max(30,(+((DATA||{}).ticker||{}).speed||45)*1.4));
  const CS=I.cs||{},TR={up:['📈 صاعد','var(--green)'],down:['📉 هابط','var(--red)'],flat:['➖ عرضي','var(--mut)']};   // 🎞️ v3.36.27
  for(const r of rows){
    const sel=(window.CSS&&CSS.escape)?CSS.escape(r.sym):r.sym,c=CS[r.sym];
    inn.querySelectorAll(`.ik[data-s="${sel}"]`).forEach(e=>{
      const su=e.querySelector('.isum'),nx=e.querySelector('.inx'),bo=e.querySelector('.ibot');
      if(c&&c.n){const s=+c.sc||0,w=s>=45?['⬆️ صاعدة بقوة','var(--green)',c.up]:s>=15?['↗️ تميل للصعود','var(--green)',c.up]:s>-15?['↔️ محايدة','var(--mut)',null]:s>-45?['↘️ تميل للهبوط','var(--red)',c.dn]:['⬇️ هابطة بقوة','var(--red)',c.dn];
        su.textContent=w[0]+(w[2]!=null?` ${w[2]}/${c.n}`:'');su.style.color=w[1];
        su.title=`معدل المؤشرات الآن (للساعات القادمة): ${s>0?'+':''}${s} من 100 — ${c.up} صاعدة · ${c.dn} هابطة · ${c.n-c.up-c.dn} محايدة`;
        const q=c.nx;nx.textContent=q?(q.k==='up'?'· غداً ↗️':'· غداً ↘️'):'';nx.style.color=q?(q.k==='up'?'var(--green)':'var(--red)'):'';
        nx.title=q?`على الأسعار الحقيقية (28 عملة): بعد مثل هذا الميل كان السعر أعلى بعد يوم في ${Math.round(q.p)}% من المرات (العادي ${Math.round(q.b)}%)`:'';
        const bt=c.bot;bo.textContent=bt?`· ${bt.t} ${bt.s}`:'';bo.style.color=bt?(bt.lv==='strong'?'var(--green)':bt.lv==='zone'?'var(--amber)':'var(--mut)'):'';
        bo.title=bt?'مؤشر القاع (شموع يومية · لأيام إلى أسبوعين) — التفاصيل في 🔮 التوقعات':''}
      else{const t=TR[r.trend]||TR.flat;su.textContent=t[0];su.style.color=t[1];su.title='الاتجاه — معدل المؤشرات يظهر بعد أول حساب';nx.textContent='';bo.textContent=''}
      e.title=`${r.base} · ${fmtPx(r.px)}`;
    });
  }
}
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for i, (a, z, b) in enumerate(BLOCKS):
        if s.count(a) != 1 or s.count(z) != 1 or s.index(a) > s.index(z):
            print(f"❌ block {i}: anchors {s.count(a)} / {s.count(z)} — nothing written: {a[:70]!r}"); sys.exit(1)
        i0, i1 = s.index(a), s.index(z)
        s = s[:i0] + b + s[i1:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · {len(BLOCKS)} blocks · compiles · {p}")
