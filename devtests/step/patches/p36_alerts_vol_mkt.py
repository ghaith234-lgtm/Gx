# 🔔 patch 36 (dashboard · indicator alerts) — the owner (13-11): «المؤشرات تنطي اشعارات لكن جدا ضعيفة … اهم شي عندي التنبيه الصحيح الناتج
#   عن اختبارك» ⇒ «للاثنين · لا تربط بالبوتات · اترك قاع الاربع ساعات · اختبر الجديد وحدث». Built only from what passed on REAL OKX prices
#   (ci/sig_check4.py · ci/sig_check5.py — 28 coins · the last 40% of time judged apart):
#   ① 🟢 the bottom CONFIRMED BY VOLUME: the bottom score (unchanged) + a volume blow-off in the last 3 days (≥ 2.5× the 20-day average)
#      ⇒ higher 14 days later in 69% of cases (normal 46%) · the last 40% of time 60% · the drop before the bounce ~10% instead of ~15%
#      · WITHOUT volume the last 40% of time was 48% (chance) ⇒ only the confirmed bottom alerts (quiet from 60 · medium/sensitive from 50);
#      the card shows the volume part either way
#   ② 🌊 the whole market crashing in one 4-hour candle (share of 28 coins falling ≥ 2.5× their usual 4-hour move) ⇒ higher a day later
#      in 62–69% of cases (normal 48%), 3 days later 56–63% (normal 46%) — a short bounce: a week later worse than normal lately ·
#      the single coin crashing with huge volume only had an edge WITH the market (alone: 50%) ⇒ one market alert (quiet ≥ 70% · medium
#      ≥ 50% · sensitive ≥ 30% of the coins) naming the ticker's coins that crashed with huge volume (≥ 3× their move · ≥ 3× volume)
#   · stays off (measured useless): the bottom without volume · turn · squeeze · support/resistance · a top score · a jump with volume ·
#     Bitcoin's crash on its own · negative funding · nothing is linked to the bots
#   python3 devtests/step/patches/p36_alerts_vol_mkt.py Holy_Dashboard.pyw
import os, sys

PY_BOT = '''BOT_VOL_X = 2.5                   # 🟢 v3.36.31: حجم الاستسلام — أعلى حجم بآخر 3 أيام ÷ متوسط الـ20 يوماً قبلها (ci/sig_check4.py)
BOT_REAL_V = {   # القاع مع حجم ضخم · 28 عملة · شموع يومية 2021–2026 · «l40» = آخر 40% من الزمن (الاختبار الأعمى)
    "normal": {"p14": 46, "p14_l40": 46},
    "zone": {"n": 224, "p7": 65, "p14": 70, "p30": 58, "m14": 6.5, "dd": -10.3, "p14_l40": 61, "m14_l40": 2.5},
    "strong": {"n": 206, "p7": 65, "p14": 69, "p30": 58, "m14": 6.8, "dd": -10.2, "p14_l40": 60, "m14_l40": 3.5},
    "novol": {"p14": 58, "p14_l40": 48},
}


def _bot_vx(V, i):
    """حجم يوم i: أعلى حجم بآخر 3 أيام (i-2..i) ÷ متوسط الـ20 يوماً قبلها — نفس ci/sig_check4.py"""
    if i < 22:
        return 0.0
    va = sum(V[i - 22:i - 2]) / 20.0
    return max(V[i - 2:i + 1]) / va if va > 0 else 0.0


'''

PY_MKT = '''# ═══════════════ 🌊 v3.36.31: انهيار السوق كله في شمعة 4 ساعات (ci/sig_check5.py — 28 عملة · سنتان) ═══════════════
MKT_COINS = ("BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
             "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
             "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "HBAR-USDT", "ICP-USDT", "INJ-USDT", "SHIB-USDT")
MKT_REAL = {     # % أعلى بعد يوم / 3 أيام · «l40» = آخر 40% من الزمن · «p7_l40» = بعد أسبوع (الارتداد قصير)
    "normal": {"p1": 48, "p3": 46, "p1_l40": 47, "p3_l40": 45, "p7_l40": 44},
    30: {"n": 57, "p1": 57, "p3": 55, "p1_l40": 55, "p3_l40": 55, "m1": 0.6, "m3": 0.6, "p7_l40": 43},
    50: {"n": 44, "p1": 62, "p3": 56, "p1_l40": 62, "p3_l40": 60, "m1": 1.0, "m3": 0.9, "p7_l40": 37},
    70: {"n": 29, "p1": 68, "p3": 60, "p1_l40": 69, "p3_l40": 63, "m1": 1.5, "m3": 1.4, "p7_l40": 25},
    "coin": {"p3": 65, "p3_l40": 63, "m3": 2.1, "p7_l40": 28},   # عملة تنهار ≥ 3× حركتها بحجم ≥ 3× والسوق ينهار معها (≥ 30%)
}
_MKT = {"rows": {}, "t": None, "res": None, "try": 0.0}


def _mkt_rows(sym):
    """شموع 4 ساعات مغلقة لعملة (الأقدم أول · بالذاكرة · 260 شمعة كحد أقصى) — قراءة عامة"""
    d = _MKT["rows"].setdefault(sym, {})
    for c in _fc_okx_rows(sym, "4H", hist=False, limit=100):
        if c[6]:
            d[int(c[0])] = c[:6]
    if d and len(d) < 125:
        for c in _fc_okx_rows(sym, "4H", after=min(d) * 1000, hist=True, limit=100):
            if c[6]:
                d[int(c[0])] = c[:6]
    for k in sorted(d)[:-260]:
        d.pop(k, None)
    return [d[k] for k in sorted(d)]


def _mkt_at(rows, T):
    """شمعة 4 ساعات T: (نزولها ÷ حركة العملة المعتادة بآخر 120 شمعة · حجمها ÷ متوسط 30 شمعة · تغيّرها) — نفس ci/sig_check5.py"""
    ts = [int(r[0]) for r in rows]
    k = bisect.bisect_left(ts, int(T))
    if k >= len(ts) or ts[k] != int(T) or k < 121:
        return None
    C = [float(r[4]) for r in rows]
    V = [float(r[5]) for r in rows]
    if any(c <= 0 for c in C[k - 121:k + 1]):
        return None
    lr = [math.log(C[i] / C[i - 1]) for i in range(k - 120, k + 1)]
    rs = lr[:120]
    rm = sum(rs) / 120.0
    sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 119.0) or 1e-9
    va = sum(V[k - 30:k]) / 30.0 or 1e-9
    return lr[120] / sd, V[k] / va, C[k] / C[k - 1] - 1.0


def mkt_scan(now=None, force=False):
    """🌊 آخر شمعة 4 ساعات مغلقة لـ28 عملة ⇒ كم عملة انهارت معاً (≥ 2.5× حركتها المعتادة) + عملات الشريط التي انهارت بحجم ضخم"""
    now = float(now if now is not None else time.time())
    T = int(now // 14400) * 14400 - 14400
    if not force and _MKT.get("t") == T:
        return _MKT.get("res")
    if not force and now - float(_MKT.get("try") or 0) < 300:
        return None
    _MKT["try"] = now
    tick = list(ticker_cfg().get("coins") or [])
    zs, cr, btc = [], [], None
    for sym in list(dict.fromkeys(list(MKT_COINS) + tick)):
        rows = _safe(_mkt_rows, sym, default=[]) or []
        if rows:
            time.sleep(0.12)                                  # حد OKX العام
        x = _mkt_at(rows, T)
        if not x:
            continue
        if sym in MKT_COINS:
            zs.append(x[0])
        if sym == "BTC-USDT":
            btc = x[2]
        if sym in tick and x[0] <= -3.0 and x[1] >= 3.0:
            cr.append({"sym": sym, "z": round(x[0], 2), "vr": round(x[1], 2), "ch": round(x[2], 5)})
    if len(zs) < 15:
        return None
    res = {"t": T, "n": len(zs), "k": sum(1 for z in zs if z <= -2.5), "crash": cr, "btc": btc}
    _MKT.update(t=T, res=res)
    return res


'''

MKT_ALERT = '''            al.append(a)
    mk = mkt if mkt is not None else (_safe(mkt_scan, now, default=None) if S.get("mkt") else None)    # 🌊 v3.36.31: انهيار السوق كله
    if mk and S.get("mkt") and mk.get("n") and mk["k"] / mk["n"] >= S["mkt"] / 100.0 - 1e-9 \\
            and now - (float(mk["t"]) + 14400) < 7200 and st.get("mkt_t") != mk["t"] and now - float(st.get("mkt_at") or 0) >= 86400:
        st["mkt_t"], st["mkt_at"] = mk["t"], now
        sh = mk["k"] / mk["n"]
        thr = max(x for x in (30, 50, 70) if sh >= x / 100.0 - 1e-9)
        Q, N0, Cn = MKT_REAL[thr], MKT_REAL["normal"], MKT_REAL["coin"]
        cr = mk.get("crash") or []
        cb = (" · ".join(f"{c['sym'].split('-')[0]} {c['ch'] * 100:+.1f}% (حجم {c['vr']:.1f}× المعتاد)" for c in cr) if cr
              else "لم تنهر عملة من عملات الشريط بحجم ضخم")
        al.append({"k": "mkt", "d": "up", "sym": "السوق", "px": 0, "sc": 0,
                   "t": f"🌊 انهيار في السوق كله — {mk['k']} من {mk['n']} عملة نزلت بقوة غير معتادة في شمعة 4 ساعات واحدة (لـ1–3 أيام)",
                   "b": ("من عملاتك: " if cr else "") + cb + (f" · البيتكوين {float(mk['btc']) * 100:+.1f}%" if mk.get("btc") is not None else ""),
                   "r": (f"🔬 تاريخياً (28 عملة · سنتان): حين انهار {thr}% من العملات فأكثر كان السعر أعلى بعد يوم في {Q['p1']}% من المرات "
                         f"(العادي {N0['p1']}%) وبعد 3 أيام {Q['p3']}% (العادي {N0['p3']}%) · في السنوات الأخيرة {Q['p1_l40']}% و{Q['p3_l40']}% · "
                         f"الوسيط بعد يوم {Q['m1']:+.1f}%"
                         + (f" · العملة التي تنهار بحجم ضخم مع السوق: أعلى بعد 3 أيام {Cn['p3']}% (في السنوات الأخيرة {Cn['p3_l40']}%)" if cr else "")
                         + f" · ارتداد قصير: بعد أسبوع كان أسوأ من العادي في السنوات الأخيرة ({Q['p7_l40']}% مقابل {N0['p7_l40']}%) · قد ينزل أكثر قبل الارتداد")})
    cut = []'''

BOT_ALERT = '''            rk = _BOT_RK.get(b.get("lv"), 0) if b.get("vol") else 0        # 🟢 v3.36.31: القاع المؤكد بالحجم فقط (بلا حجم: مثل الصدفة مؤخراً)
            if rk and int(b.get("score") or 0) >= S["minv"] and rk > int(L.get("bot_lv") or 0):
                L["bot_lv"] = rk
                if fresh and int(b.get("since") or 0) <= 1:
                    fresh = False                                         # نوبة جديدة ⇒ تنبيه حتى بعد التشغيل مباشرة (القديمة تبقى صامتة)
                V_ = b.get("real_v") or BOT_REAL_V.get(b.get("lv")) or {}
                own = (b.get("own_v") or {}).get(b.get("lv"))
                a = {"k": "bot", "d": "up", "t": f"{b.get('lbl')} ✅ مؤكد بالحجم — {base}: مؤشر القاع {int(b.get('score') or 0)}/100 (لأيام إلى أسبوعين)",
                     "b": " · ".join(p["txt"] for p in (b.get("parts") or []) if p.get("on")) + f" · السعر {_px_s(px)}$",
                     "r": (f"🔬 تاريخياً (28 عملة · 2021–2026): القاع مع حجم ضخم ⇒ أعلى بعد 14 يوماً في {V_.get('p14')}% من المرات "
                           f"(العادي {BOT_REAL_V['normal']['p14']}%) · في السنوات الأخيرة {V_.get('p14_l40')}% · الوسيط {float(V_.get('m14') or 0):+.1f}% · "
                           f"النزول قبل الارتداد عادةً نحو {abs(float(V_.get('dd') or 0)):.0f}%"
                           + (f" · على {base}: {own['p14']}% من {own['n']} مرة" if own else "")
                           + f" · بلا حجم كان في السنوات الأخيرة مثل الصدفة ({BOT_REAL_V['novol']['p14_l40']}%) · قد ينزل أكثر قبل الارتداد — الشراء على دفعات أسلم")}'''

R = [
    # ── the bottom: the volume part
    ('''def _bot_at(C, rsi, t):''', PY_BOT + '''def _bot_at(C, rsi, t):'''),
    ('''    lv, lbl = next(((k, l) for thr, k, l in BOT_LV if s >= thr), ("none", "لا إشارة"))''',
     '''    lv, lbl = next(((k, l) for thr, k, l in BOT_LV if s >= thr), ("none", "لا إشارة"))
    vx = _bot_vx(V, t)                                       # 🟢 v3.36.31: تأكيد الحجم (يؤكد القاع · لا يغيّر النقاط)
    vol = vx >= BOT_VOL_X'''),
    ('''    btc_up = None
    try:
        bt = sorted(btc_m.items())''',
     '''    own_v = {}
    for thr, k, _ in BOT_LV:                                 # 📒 سجلها على العملة نفسها مع الحجم
        last, ev = -99, []
        for i in range(60, n - 14):
            if sc[i] is not None and sc[i] >= thr and _bot_vx(V, i) >= BOT_VOL_X:
                if i - last >= 10:
                    ev.append(C[i + 14] / C[i] - 1.0)
                last = i
        if ev:
            ev.sort()
            own_v[k] = {"n": len(ev), "p14": round(sum(1 for x in ev if x > 0) / len(ev) * 100), "m14": round(ev[len(ev) // 2] * 100, 1)}
    btc_up = None
    try:
        bt = sorted(btc_m.items())'''),
    ('''              "txt": (f"أغلق تحت حد بولنجر السفلي ({f(inf['lb'])})" if on["bb"] else f"فوق حد بولنجر السفلي ({f(inf['lb'])})")}]''',
     '''              "txt": (f"أغلق تحت حد بولنجر السفلي ({f(inf['lb'])})" if on["bb"] else f"فوق حد بولنجر السفلي ({f(inf['lb'])})")},
             {"k": "vol", "on": vol, "w": "تأكيد",
              "txt": (f"حجم تداول ضخم بآخر 3 أيام ({vx:.1f}× المعتاد) — يؤكد القاع" if vol
                      else f"حجم التداول {vx:.1f}× المعتاد — بلا تأكيد (يلزم {BOT_VOL_X:g}× فأكثر)")}]'''),
    ('''"real": BOT_REAL.get(lv if lv != "none" else "zone"), "normal": BOT_REAL["normal"], "years": BOT_REAL["years"]}''',
     '''"real": BOT_REAL.get(lv if lv != "none" else "zone"), "normal": BOT_REAL["normal"], "years": BOT_REAL["years"],
            "vol": vol, "vx": round(vx, 2), "own_v": own_v, "real_v": BOT_REAL_V.get(lv if lv != "none" else "zone"), "normal_v": BOT_REAL_V["normal"],
            "novol": BOT_REAL_V["novol"]}'''),
    # ── the guide
    ('''"read": "👀 راقب من 30 · 🟡 منطقة شراء من 50 · 🟢 قاع قوي من 60. لا ينتظر تأكيد الانعطاف لأن القياس أظهر أن الانتظار يضيّع أغلب الارتداد.",''',
     '''"read": "👀 راقب من 30 · 🟡 منطقة شراء من 50 · 🟢 قاع قوي من 60 · ✅ «مؤكد بالحجم» حين يبلغ حجم التداول بآخر 3 أيام 2.5 ضعف متوسطه فأكثر — وهو الأقوى، وعليه وحده تصل التنبيهات. لا ينتظر تأكيد الانعطاف لأن القياس أظهر أن الانتظار يضيّع أغلب الارتداد.",'''),
    ('''· بعد 30 يوماً لا فرق يُذكر.",''',
     '''· بعد 30 يوماً لا فرق يُذكر · ✅ مع حجم ضخم (2.5 ضعف فأكثر بآخر 3 أيام): أعلى بعد 14 يوماً في 69% من المرات مقابل 46%، وفي آخر 40% من الزمن 60%، والنزول قبل الارتداد نحو 10% بدل 15% — بلا حجم: في آخر 40% من الزمن 48% فقط (مثل الصدفة).",'''),
    # ── the alerts
    ('''    "low":  {"lbl": "هادئة",  "min": 60, "turn": 45, "conf": 70, "near": 0.0,  "sq_on": False},
    "mid":  {"lbl": "متوسطة", "min": 50, "turn": 30, "conf": 60, "near": 0.35, "sq_on": False},
    "high": {"lbl": "حساسة",  "min": 30, "turn": 15, "conf": 0,  "near": 0.7,  "sq_on": True},''',
     '''    "low":  {"lbl": "هادئة",  "min": 60, "minv": 60, "mkt": 70, "turn": 45, "conf": 70, "near": 0.0,  "sq_on": False},   # 🔔 v3.36.31: «minv» القاع المؤكد
    "mid":  {"lbl": "متوسطة", "min": 50, "minv": 50, "mkt": 50, "turn": 30, "conf": 60, "near": 0.35, "sq_on": False},   #   بالحجم · «mkt» % العملات المنهارة
    "high": {"lbl": "حساسة",  "min": 30, "minv": 50, "mkt": 30, "turn": 15, "conf": 0,  "near": 0.7,  "sq_on": True},    #   معاً في شمعة 4 ساعات'''),
    ('''def ina_tick(now=None, rows=None, send=True):''', PY_MKT + '''def ina_tick(now=None, rows=None, send=True, mkt=None):'''),
    ('''            al.append(a)
    cut = []''', MKT_ALERT),
    ('''        text = f"🟢 تنبيهات مؤشر القاع ({len(al)})\\n"''', '''        text = f"🔔 تنبيهات المؤشرات ({len(al)})\\n"'''),
    ('''    a = {"sym": R.get("sym") or "BTC-USDT", "t": f"🧪 تجربة — 🟡 منطقة شراء — {R.get('base') or 'BTC'}: مؤشر القاع 70/100 (لأيام إلى أسبوعين)",
         "b": f"هكذا تصلك تنبيهات مؤشر القاع ({INA_SENS[cfg['sens']]['lbl']} · {PXA_CH[cfg['ch']]})",
         "r": "🔬 كل تنبيه معه سجله على الأسعار الحقيقية: كم مرة كان السعر أعلى بعد 14 يوماً مقابل الأيام العادية"}''',
     '''    a = {"sym": R.get("sym") or "BTC-USDT", "t": f"🧪 تجربة — 🟢 قاع قوي ✅ مؤكد بالحجم — {R.get('base') or 'BTC'}: مؤشر القاع 70/100 (لأيام إلى أسبوعين)",
         "b": f"هكذا تصلك تنبيهات المؤشرات: 🟢 القاع المؤكد بالحجم و🌊 انهيار السوق ({INA_SENS[cfg['sens']]['lbl']} · {PXA_CH[cfg['ch']]})",
         "r": "🔬 كل تنبيه معه سجله على الأسعار الحقيقية: كم مرة كان السعر أعلى بعدها مقابل الأيام العادية"}'''),
    ('''    rule = ("🟢 مؤشر القاع: حين تدخل عملة " + {60: "«🟢 قاع قوي» (60 فأكثر)", 50: "«🟡 منطقة شراء» (50 فأكثر) أو أقوى", 30: "«👀 راقب» (30 فأكثر) أو أقوى"}[S["min"]]
            + " — مرة لكل مستوى في كل نوبة" + (f" · حد {c['cap']} باليوم" if c["cap"] else " · بلا حدّ يومي")
            + " · تنبيهات الانقلاب والانضغاط والدعم/المقاومة متوقفة: لم تثبت لها قيمة على الأسعار الحقيقية")''',
     '''    rule = (f"🟢 قاع مؤكد بالحجم: مؤشر القاع {S['minv']} فأكثر مع حجم تداول ضخم ({BOT_VOL_X:g} ضعف المعتاد فأكثر بآخر 3 أيام) — مرة لكل مستوى في كل نوبة"
            + f" · 🌊 انهيار السوق: {S['mkt']}% فأكثر من 28 عملة تنهار في شمعة 4 ساعات واحدة — مرة باليوم كحد أقصى، ومعه عملات الشريط التي انهارت بحجم ضخم"
            + (f" · حد {c['cap']} باليوم" if c["cap"] else " · بلا حدّ يومي")
            + " · متوقفة لأنها لم تثبت لها قيمة على الأسعار الحقيقية: القاع بلا حجم · الانقلاب · الانضغاط · الدعم/المقاومة · القمة")'''),
    # ── the screen
    ('''<b>🟢 تنبيهات مؤشر القاع — متى أشتري <small''', '''<b>🔔 تنبيهات المؤشرات — 🟢 القاع المؤكد بالحجم · 🌊 انهيار السوق <small'''),
    ('''${b.lv==='none'?'🟢 مؤشر القاع':gEsc(b.lbl)} <b>${b.score}/100</b>${b.lv==='none'?' — لا إشارة شراء الآن':b.since>0?` · منذ ${b.since} ${b.since===1?'يوم':'أيام'}`:' · اليوم'}</div>`}''',
     '''${b.lv==='none'?'🟢 مؤشر القاع':gEsc(b.lbl)} <b>${b.score}/100</b>${b.lv==='none'?' — لا إشارة شراء الآن':b.since>0?` · منذ ${b.since} ${b.since===1?'يوم':'أيام'}`:' · اليوم'}${b.lv==='none'?'':b.vol?' · ✅ مؤكد بالحجم':' · بلا تأكيد حجم'}</div>`}'''),
    ('''    ${bt?`<div>${bt}</div>`:''}
    ${o?`<div>📒 على ${B}:''',
     '''    ${b.real_v?`<div>📊 مع حجم ضخم (التأكيد): أعلى بعد 14 يوماً في <b>${b.real_v.p14}%</b> (العادي ${(b.normal_v||{}).p14}%) · في السنوات الأخيرة ${b.real_v.p14_l40}% · الوسيط <b>+${b.real_v.m14}%</b> · بلا حجم: في السنوات الأخيرة ${(b.novol||{}).p14_l40}% (مثل الصدفة) — ${b.vol?'✅ متحقق الآن':'▫️ غير متحقق الآن'} · التنبيهات على المؤكد بالحجم فقط</div>`:''}
    ${bt?`<div>${bt}</div>`:''}
    ${o?`<div>📒 على ${B}:'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    BLOCK_A = '''            rk = _BOT_RK.get(b.get("lv"), 0)
            if rk and int(b.get("score") or 0) >= S["min"] and rk > int(L.get("bot_lv") or 0):'''
    BLOCK_Z = '''                           + " · قد ينزل أكثر قبل الارتداد — الشراء على دفعات أسلم")}'''
    if s.count(BLOCK_A) != 1 or s.count(BLOCK_Z) != 1 or s.index(BLOCK_A) > s.index(BLOCK_Z):
        print(f"❌ block: anchors {s.count(BLOCK_A)} / {s.count(BLOCK_Z)} — nothing written"); sys.exit(1)
    i0, i1 = s.index(BLOCK_A), s.index(BLOCK_Z) + len(BLOCK_Z)
    s = s[:i0] + BOT_ALERT + s[i1:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 1 block · compiles · {p}")
