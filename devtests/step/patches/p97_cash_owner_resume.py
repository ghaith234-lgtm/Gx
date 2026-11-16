# 💵 patch 97 (dashboard v3.36.58) — the owner (16-11): «عند نزول السعر في الشبكي ونفاذ الاموال هل راح يسوي ايقاف شراء ان ما اريده يرجع
#   يشتري الا بموافقتي». Until now (v3.36.44 · p70) a bot the system paused because the free dollars ran out resumed BY ITSELF once the
#   dollars covered its order for 30 minutes. Now it waits for the owner (the dashboard only writes control fields — no order from here):
#   · the dollars back ⇒ the bot stays paused · one «✅ عاد الدولار الحر» message that says buying waits for you and which bots
#   · while it waits the floor keeps following the price up (nothing is bought above it either)
#   · the card's chip turns green «▶️ عاد الدولار — استأنف الشراء» ⇒ a confirm ⇒ control «cash_resume»: your own floor comes back (or
#     none) and the engine buys the saved levels in one order at the market price (cheaper than their levels) as far as the dollars go
#   · the card's own ▶️ (or a floor you type) works as before (the system lets that bot alone)
#   · 🛡️ the switch off / the guard paused ⇒ the bots it paused STAY paused (a plain pause — resume from each card); before they resumed
#   · a new switch in 🛡️ «▶️ يعود الشراء تلقائياً حين يعود الدولار» — off by default (on = the old behaviour)
#   python3 devtests/step/patches/p97_cash_owner_resume.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── the setting
    ('''def _cw_key(d):''', '''_CW_MODE = {"auto": False}      # ▶️ v3.36.58: إعداد الجولة الحالية (يُضبط ببداية _cash_watch)


def _cw_auto(g):
    """▶️ v3.36.58: يعود الشراء تلقائياً حين يعود الدولار؟ (افتراضياً لا — ينتظر موافقة المالك)"""
    return bool((g or {}).get("cash_auto_resume"))


def _cw_key(d):'''),
    # ── the wallet message: what happens when the dollars are back
    ('''               + (f"⏸ أُوقف شراؤها تلقائياً فوق السعر بقليل: {' · '.join(paused)} — كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار\\n"
                  if paused else "")
               + "البوتات تكمل البيع، ويعود الشراء وحده حين يتوفر الدولار — رسالة الآن وأخرى حين يعود (وتذكير مرة في اليوم على الأكثر).")''',
     '''               + (f"⏸ أُوقف شراؤها تلقائياً فوق السعر بقليل: {' · '.join(paused)} — كل مستوى ينزل إليه السعر يُحفظ"
                  + (" ويُشترى بأمر واحد حين يعود الدولار\\n" if _cw_auto(g) else " ويُشترى بأمر واحد حين تستأنف أنت الشراء\\n") if paused else "")
               + ("البوتات تكمل البيع، ويعود الشراء وحده حين يتوفر الدولار" if _cw_auto(g) else
                  "البوتات تكمل البيع، ويبقى الشراء الموقوف حتى تستأنفه أنت من البطاقة (▶️ استأنف الشراء)")
               + " — رسالة الآن وأخرى حين يعود (وتذكير مرة في اليوم على الأكثر).")'''),
    ('''              f"المتاح {av:.2f} {q} يغطي أمر الشراء ({mn:.2f} {q}) منذ {CW_BACK_S // 60} دقيقة — تعود البوتات إلى الشراء"
              + (" ويُستأنف الشراء الموقوف تلقائياً (المستويات المحفوظة تُشترى بأمر واحد بقدر الدولار)" if _cw_recs(wid, q) else ""),''',
     '''              f"المتاح {av:.2f} {q} يغطي أمر الشراء ({mn:.2f} {q}) منذ {CW_BACK_S // 60} دقيقة"
              + ((" — تعود البوتات إلى الشراء ويُستأنف الشراء الموقوف تلقائياً (المستويات المحفوظة تُشترى بأمر واحد بقدر الدولار)" if _cw_auto(g) else
                  " — الشراء الموقوف ينتظر موافقتك: اضغط «▶️ استأنف الشراء» في بطاقة "
                  + " · ".join(_cw_lbl(r) for r in _cw_recs(wid, q))
                  + " (تعود أرضيتك إن كانت لك أرضية، والمستويات المحفوظة تُشترى بأمر واحد بقدر الدولار)") if _cw_recs(wid, q) else
                 " — تعود البوتات إلى الشراء"),'''),
    ('''        _dash_event(i.get("sym") or "", f"⏸💵 أُوقف الشراء تلقائياً — الدولار الحر ({max(0.0, eff):.2f}$) لا يكفي أمر الشراء ({need:g}$) · "
                                        f"الأرضية {_px_s(new)} فوق السعر بقليل: كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار"''',
     '''        _dash_event(i.get("sym") or "", f"⏸💵 أُوقف الشراء تلقائياً — الدولار الحر ({max(0.0, eff):.2f}$) لا يكفي أمر الشراء ({need:g}$) · "
                                        f"الأرضية {_px_s(new)} فوق السعر بقليل: كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين "
                                        + ("يعود الدولار" if _CW_MODE["auto"] else "تستأنف أنت الشراء")'''),
    # ── the restore: whose decision
    ('''def _cw_restore(k, r, d, why):''', '''def _cw_restore(k, r, d, why, owner=False):'''),
    ('''            _dash_event(r.get("sym") or "", (f"▶️💵 {why} — استؤنف الشراء تلقائياً"''',
     '''            _dash_event(r.get("sym") or "", (f"▶️💵 {why} — استؤنف الشراء" + ("" if owner else " تلقائياً")'''),
    ('''    on = g.get("cash_pause", True) is not False
    with _CW_LOCK:''', '''    on = g.get("cash_pause", True) is not False
    _CW_MODE["auto"] = _cw_auto(g)
    with _CW_LOCK:'''),
    # ── the round: the dollars back ⇒ wait for the owner (or the old automatic resume when the switch says so)
    ('''                    if (not on) or now - float(d["ok"].get(wq) or now) >= CW_BACK_S:
                        left = eff''', '''                    _bk = (not on) or now - float(d["ok"].get(wq) or now) >= CW_BACK_S
                    if _bk and not _cw_auto(g):
                        for k, r in recs:                   # 👤 v3.36.58: الشراء ينتظر موافقة المالك — ولا شي يُستأنف من هنا
                            if r.get("hands_off") or not on:
                                d["bots"].pop(k, None)      # المالك تصرّف بنفسه · أو أُطفئ المفتاح ⇒ يبقى إيقافاً عادياً (▶️ من البطاقة)
                                ch = True
                            elif not r.get("back"):
                                r["back"] = now             # عاد الدولار ⇒ شارة «▶️ استأنف الشراء» بالكرت
                                ch = True
                    elif _bk:
                        left = eff'''),
    ('''                    if eff < u and i.get("alive"):
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": int(sv.get("n") or 0) + 1, "need": u, "ts": now}
                        seen_now.add(k)
                        ch = True
                    else:
                        continue''', '''                    if eff < u and i.get("alive"):
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": int(sv.get("n") or 0) + 1, "need": u, "ts": now}
                        seen_now.add(k)
                        ch = True
                    else:
                        _rw = d["bots"].get(k)              # 👤 v3.36.58: ينتظر موافقتك ⇒ الأرضية تبقى تتبع السعر صعوداً (ولا شراء فوقها أيضاً)
                        if on and _rw is not None and _rw.get("back") and not _rw.get("hands_off") and _cw_pause(k, i, _rw, d, wid, q, eff, now):
                            ch = True
                        continue'''),
    # ── the switch off / the guard paused: the owner decides
    ('''def _cw_release_all(why):
    """▶️ كل بوت أوقفه النظام للدولار يُستأنف الآن (أرضية المالك ترجع) — حين تُوقف الرقابة أو يُطفأ المفتاح (لا جولة قادمة تستأنفه)"""
    n = 0
    with _CW_LOCK:
        d = _cw_load()
        for k, r in list(d["bots"].items()):
            if _cw_restore(k, r, d, why):
                n += 1''', '''def _cw_release_all(why):
    """▶️ كل بوت أوقفه النظام للدولار يُستأنف الآن (أرضية المالك ترجع) — حين تُوقف الرقابة أو يُطفأ المفتاح (لا جولة قادمة تستأنفه)
    👤 v3.36.58: بلا «يعود الشراء تلقائياً» ⇒ تبقى موقوفة (إيقاف عادي — ▶️ من كل بطاقة) · الرقم سالب = عدد الباقية موقوفة"""
    n = 0
    auto = _cw_auto(_gd_load())
    with _CW_LOCK:
        d = _cw_load()
        for k, r in list(d["bots"].items()):
            if not auto:
                d["bots"].pop(k, None)
                if not r.get("hands_off"):
                    n -= 1
                    _dash_event(r.get("sym") or "", f"⏸💵 {why} — يبقى الشراء موقوفاً حتى تستأنفه من البطاقة (▶️ استئناف الشراء)")
                continue
            if _cw_restore(k, r, d, why):
                n += 1'''),
    ('''            if _n:                                       # 💵 v3.36.44: لا جولة قادمة تستأنفها ⇒ الآن
                msg.append(f"▶️ استؤنف شراء {_n} بوت أوقفه النظام لنفاد الدولار")''',
     '''            if _n > 0:                                   # 💵 v3.36.44: لا جولة قادمة تستأنفها ⇒ الآن
                msg.append(f"▶️ استؤنف شراء {_n} بوت أوقفه النظام لنفاد الدولار")
            elif _n < 0:                                 # 👤 v3.36.58: تبقى موقوفة حتى تستأنفها
                msg.append(f"⏸ يبقى شراء {-_n} بوت موقوفاً حتى تستأنفه من بطاقته")'''),
    ('''def guard_cfg(auto_fix=None, paused=None, by="", cash_pause=None):''',
     '''def guard_cfg(auto_fix=None, paused=None, by="", cash_pause=None, cash_auto_resume=None):'''),
    ('''        if cash_pause is not None:
            g["cash_pause"] = bool(cash_pause)
            msg.append("⏸💵 إيقاف الشراء تلقائياً حين ينفد الدولار " + ("مفعّل" if g["cash_pause"] else
                                                                       "معطّل — البوتات الموقوفة تلقائياً تُستأنف بالفحص القادم"))''',
     '''        if cash_pause is not None:
            g["cash_pause"] = bool(cash_pause)
            msg.append("⏸💵 إيقاف الشراء تلقائياً حين ينفد الدولار " + ("مفعّل" if g["cash_pause"] else "معطّل"))
        if cash_auto_resume is not None:                 # ▶️ v3.36.58
            g["cash_auto_resume"] = bool(cash_auto_resume)
            msg.append("▶️ عودة الشراء تلقائياً حين يعود الدولار " + ("مفعّلة" if g["cash_auto_resume"] else
                                                                   "متوقفة — الشراء الموقوف ينتظر موافقتك (▶️ استأنف الشراء في البطاقة)"))'''),
    ('''                return self._json(guard_cfg(auto_fix=v.get("auto_fix"), paused=v.get("paused"), by=_by, cash_pause=v.get("cash_pause")))''',
     '''                return self._json(guard_cfg(auto_fix=v.get("auto_fix"), paused=v.get("paused"), by=_by, cash_pause=v.get("cash_pause"),
                                            cash_auto_resume=v.get("cash_auto_resume")))'''),
    ('''            "cash_pause": g.get("cash_pause", True) is not False,                       # 💵 v3.36.44''',
     '''            "cash_pause": g.get("cash_pause", True) is not False,                       # 💵 v3.36.44
            "cash_auto_resume": bool(g.get("cash_auto_resume")),                         # ▶️ v3.36.58'''),
    # ── the card's chip: waiting for the owner
    ('''        if r and not r.get("hands_off"):
            return {"need": round(float(r.get("need") or 0), 4), "auto": True}''',
     '''        if r and not r.get("hands_off"):
            return {"need": round(float(r.get("need") or 0), 4), "auto": True, "back": bool(r.get("back"))}   # back: ينتظر موافقتك'''),
    # ── the card's button: control «cash_resume» (state fields only — the engine buys)
    ('''    if action == "plus_edit":''', '''    if action == "cash_resume":                               # ▶️ v3.36.58: عاد الدولار ⇒ المالك يستأنف (حقول التحكم فقط — المحرك يشتري)
        with _CW_LOCK:
            d = _cw_load()
            k = _cw_key(b["dir"])
            r = d["bots"].get(k)
            if not r:
                return {"ok": False, "msg": "لا يوجد إيقاف تلقائي لهذا البوت"}
            ok_ = _cw_restore(k, r, d, "استأنفتَ الشراء", owner=True)
            save_json_atomic(CASHW_FILE, d)
        o = float(r.get("orig") or 0)
        return {"ok": bool(ok_), "msg": ("▶️ استؤنف الشراء" + (f" · عادت أرضيتك {_px_s(o)}" if o > 0 else
                                                               " — المستويات المحفوظة تُشترى بأمر واحد بقدر الدولار الحر")) if ok_ else "تعذّر الاستئناف — أعد المحاولة"}
    if action == "plus_edit":'''),
    # ── the page: the chip (green when the dollars are back) · its confirm
    ('''  const CW=b.cashw;if(CW&&+CW.need>0)c+=`<span class="chip cashw"''',
     '''  const CW=b.cashw;if(CW&&CW.back)c+=`<span class="chip cashw cwback" onclick="event.stopPropagation();cashResume('${b.dir}')" style="cursor:pointer;color:var(--green);border-color:rgb(var(--green-rgb)/.5);background:rgb(var(--green-rgb)/.10)"
    title="عاد الدولار الحر — الشراء ما زال موقوفاً بانتظار موافقتك · اضغط للاستئناف">▶️ عاد الدولار — استأنف الشراء</span>`;
  else if(CW&&+CW.need>0)c+=`<span class="chip cashw"'''),
    ('''title="${CW.auto?'⏸ أُوقف الشراء تلقائياً فوق السعر بقليل لأن الدولار الحر في المحفظة لا يكفي أمر الشراء — كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار (وتعود أرضيتك إن كانت لك أرضية) · زر الاستئناف يلغي الإيقاف التلقائي لهذا البوت\'''',
     '''title="${CW.auto?'⏸ أُوقف الشراء تلقائياً فوق السعر بقليل لأن الدولار الحر في المحفظة لا يكفي أمر الشراء — كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين تستأنف الشراء (وتعود أرضيتك إن كانت لك أرضية) · زر الاستئناف يلغي الإيقاف التلقائي لهذا البوت\''''),
    ('''function accChipsOf(b){''', '''function cashResume(dir){const b=botOf(dir)||{};      // ▶️ v3.36.58: عاد الدولار — الاستئناف بقرارك
  showDialog(`<h2>▶️ استئناف الشراء — ${gEsc(b.symbol||'')}</h2>
    <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:14px">عاد الدولار الحر. عند الاستئناف تعود أرضيتك كما كانت (إن كانت لك أرضية)، والمستويات التي نزل إليها السعر والشراء موقوف تُشترى <b>بأمر واحد بسعر السوق</b> — أرخص من مستوياتها — بقدر الدولار الحر، ويعود البوت إلى الشراء العادي.</p>
    <div class="mbtns"><button class="primary" onclick="hideModal();ctl('${dir}','cash_resume')">▶️ استأنف الشراء</button><button onclick="hideModal()">رجوع</button></div>`)}
function accChipsOf(b){'''),
    ('''      يُحفظ، والأرضية تتبع السعر إن صعد · وحين يعود الدولار نصف ساعة يُستأنف الشراء (يُشترى المحفوظ بأمر واحد) وتعود أرضيتك إن كانت لك أرضية.
      رسالة واحدة للمحفظة حين ينفد وأخرى حين يعود.</span></div>
    <button onclick="guardCfg({cash_pause:${V.cash_pause?'false':'true'}})" class="${V.cash_pause?'on':''}" style="font-size:12px;padding:6px 12px">${V.cash_pause?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;''',
     '''      يُحفظ، والأرضية تتبع السعر إن صعد · ${V.cash_auto_resume?'وحين يعود الدولار نصف ساعة يُستأنف الشراء (يُشترى المحفوظ بأمر واحد) وتعود أرضيتك إن كانت لك أرضية':'وحين يعود الدولار يبقى الشراء موقوفاً حتى تستأنفه أنت: شارة خضراء «▶️ استأنف الشراء» في البطاقة'}.
      رسالة واحدة للمحفظة حين ينفد وأخرى حين يعود.</span></div>
    <button onclick="guardCfg({cash_pause:${V.cash_pause?'false':'true'}})" class="${V.cash_pause?'on':''}" style="font-size:12px;padding:6px 12px">${V.cash_pause?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;
  h+=`<div id="gv_cashr" style="${box};display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between">
    <div style="font-size:12px;line-height:1.8">▶️💵 <b>يعود الشراء تلقائياً حين يعود الدولار:</b> <b style="color:${V.cash_auto_resume?'var(--green)':'var(--mut2)'}">${V.cash_auto_resume?'مفعّل':'متوقف — ينتظر موافقتك'}</b><br>
      <span style="color:var(--mut2);font-size:11px">متوقف (الافتراضي): البوت الذي أُوقف شراؤه لنفاد الدولار لا يشتري حتى تضغط «▶️ استأنف الشراء» في بطاقته · مفعّل: يُستأنف وحده بعد نصف ساعة من عودة الدولار.</span></div>
    <button onclick="guardCfg({cash_auto_resume:${V.cash_auto_resume?'false':'true'}})" class="${V.cash_auto_resume?'on':''}" style="font-size:12px;padding:6px 12px">${V.cash_auto_resume?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if s.count('APP_VERSION = "3.36.57"') != 1:
        print("❌ APP_VERSION 3.36.57 not found"); sys.exit(1)
    s = s.replace('APP_VERSION = "3.36.57"', 'APP_VERSION = "3.36.58"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the dollar outage waits for the owner to resume (card chip · cash_resume · 🛡️ switch) · v3.36.58 · compiles · {p}")
