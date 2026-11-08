# 🟢 patch 31 (dashboard · 🔮 forecast — apply after p30) — the owner (8-11): «اريد اتضيف مؤشر القاع له حتى اعرف متى اشتري» · days to weeks.
#   Built only from what proved itself on REAL OKX prices (ci/sig_check2.py · sig_check3.py — 28 coins, daily candles 2021–2026, each day
#   seeing only the days before it). Three parts, 0–100:
#     a 7-day drop of more than 2× the coin's usual weekly move (50) · RSI ≤ 25 (30) or ≤ 30 (20) · a close under the lower Bollinger band (20)
#   ⇒ 👀 watch ≥ 30 · 🟡 buy zone ≥ 50 · 🟢 strong ≥ 60.
#   Measured: at ≥ 60, 14 days later higher 64% vs 46% normally, median +3.9% vs −1.3%, 26 of 28 coins, 2022 +20 · 2023 +16 · 2024 +26 ·
#   2025 +33 · 2026 so far −4 · Bitcoin above its 200-day average 76% (+5.3%), below 57% (+2.5%) · 30 days: no edge · waiting for a
#   confirmation (daily or 4-hour) lost most of the bounce ⇒ none.
#   Each coin card in 🔮 gets the reading (the last closed day) · its parts · the 28-coin record · Bitcoin's state · this coin's own record
#   of the same reading · the honest limits. A 📖 guide entry. Read only — no order, no notification here (alerts: p32).
#   python3 devtests/step/patches/p31_bottom.py Holy_Dashboard.pyw
import os, sys

PY = '''# ═══════════════ 🟢 v3.36.27: مؤشر القاع — متى أشتري؟ (من أيام إلى أسبوعين · شموع يومية مسكّرة · قراءة فقط) ═══════════════
#   (المالك 8-11: «اريد اتضيف مؤشر القاع له حتى اعرف متى اشتري») — مبني فقط مما ثبت على أسعار OKX الحقيقية (ci/sig_check2.py · 3):
#   ثلاثة أجزاء من 100: نزول 7 أيام أكبر من ضعف حركة العملة الأسبوعية المعتادة (50) · RSI ≤ 25 (30) أو ≤ 30 (20) · إغلاق تحت حد بولنجر
#   السفلي (20) ⇒ 👀 راقب ≥ 30 · 🟡 منطقة شراء ≥ 50 · 🟢 قاع قوي ≥ 60 · بلا انتظار تأكيد (القياس: التأكيد أضاع أغلب الارتداد).
BOT_W = {"z7": 50, "rsi25": 30, "rsi30": 20, "bb": 20}
BOT_LV = ((60, "strong", "🟢 قاع قوي"), (50, "zone", "🟡 منطقة شراء"), (30, "watch", "👀 راقب"))
BOT_REAL = {   # 28 عملة · شموع يومية 2021–2026 · % أعلى بعد 7 / 14 / 30 يوماً · وسيط 14 يوماً · النزول قبل الارتداد (وسيط أدنى سعر خلال 30 يوماً)
    "normal": {"p7": 47, "p14": 46, "p30": 44, "m14": -1.3, "dd": -14.6},
    "watch": {"n": 495, "p7": 52, "p14": 57, "p30": 42, "m14": 1.3, "dd": -17.7, "up": (62, 2.5), "down": (55, 0.5), "coins": "22 من 28"},
    "zone": {"n": 384, "p7": 54, "p14": 61, "p30": 44, "m14": 2.7, "dd": -15.9, "up": (75, 5.3), "down": (54, 0.7), "coins": "24 من 28"},
    "strong": {"n": 299, "p7": 57, "p14": 64, "p30": 45, "m14": 3.9, "dd": -15.3, "up": (76, 5.3), "down": (57, 2.5), "coins": "26 من 28"},
    "years": "2022 +20 · 2023 +16 · 2024 +26 · 2025 +33 · 2026 حتى الآن −4 نقاط عن العادي",
}


def _bot_at(C, rsi, t):
    """🟢 قراءة يوم t (مسكّر): (النقاط, {جزء: شغّال}, التفاصيل) — نفس قياس ci/sig_check3.py حرفياً"""
    if t < 60 or not C[t] or not C[t - 7] or any(not C[i] for i in range(t - 60, t + 1)):
        return None
    lr = [math.log(C[i] / C[i - 1]) for i in range(t - 59, t + 1)]
    m_ = sum(lr) / 60.0
    sd = math.sqrt(sum((x - m_) ** 2 for x in lr) / 59.0) or 1e-9
    z7 = math.log(C[t] / C[t - 7]) / (sd * math.sqrt(7))
    w = C[t - 19:t + 1]
    mu = sum(w) / 20.0
    lb = mu - 2.0 * math.sqrt(sum((x - mu) ** 2 for x in w) / 20.0)
    r = rsi[t]
    on = {"z7": z7 <= -2.0, "rsi25": r is not None and r <= 25, "rsi30": r is not None and 25 < r <= 30, "bb": C[t] < lb}
    return sum(BOT_W[k] for k, v in on.items() if v), on, {"z7": z7, "ch7": C[t] / C[t - 7] - 1.0, "rsi": r, "lb": lb}


def bot_coin(sym, d1, btc_m):
    """🟢 مؤشر القاع لعملة: قراءة آخر يوم مسكّر + أجزاؤه + سجلها على ماضي العملة نفسها + حالة البيتكوين (فوق/تحت متوسط 200 يوم)"""
    if not d1 or len(d1) < 120:
        return None
    T = [int(r[0]) for r in d1]
    O, H, L, C, V = ([float(r[i]) for r in d1] for i in range(1, 6))
    S = _i2_series(O, H, L, C, V)
    n = len(C)
    sc = [None] * n
    for t in range(60, n):
        a = _bot_at(C, S["rsi"], t)
        sc[t] = a[0] if a else None
    t = n - 1
    cur = _bot_at(C, S["rsi"], t)
    if not cur:
        return None
    s, on, inf = cur
    lv, lbl = next(((k, l) for thr, k, l in BOT_LV if s >= thr), ("none", "لا إشارة"))
    st = t
    while st - 1 >= 0 and sc[st - 1] is not None and sc[st - 1] >= 30 and s >= 30:
        st -= 1
    own = {}
    for thr, k, _ in BOT_LV:                                 # 📒 سجلها على العملة: أول يوم يبلغ المستوى بعد 10 أيام هدوء ⇒ بعد 14 يوماً
        last, ev = -99, []
        for i in range(60, n - 14):
            if sc[i] is not None and sc[i] >= thr:
                if i - last >= 10:
                    ev.append(C[i + 14] / C[i] - 1.0)
                last = i
        if ev:
            ev.sort()
            own[k] = {"n": len(ev), "p14": round(sum(1 for x in ev if x > 0) / len(ev) * 100), "m14": round(ev[len(ev) // 2] * 100, 1)}
    btc_up = None
    try:
        bt = sorted(btc_m.items())
        if len(bt) >= 200:
            bts = [x[0] for x in bt]
            be = _i2_ema([x[1] for x in bt], 200)
            j = bisect.bisect_right(bts, T[t]) - 1
            if j >= 0 and be[j]:
                btc_up = bt[j][1] > be[j]
    except Exception:
        btc_up = None
    f = _i2_f
    r = inf["rsi"]
    parts = [{"k": "z7", "on": on["z7"], "w": BOT_W["z7"],
              "txt": (f"نزل {abs(inf['ch7']) * 100:.1f}% في 7 أيام — أكثر من ضعف حركته الأسبوعية المعتادة" if on["z7"]
                      else f"حركة 7 أيام {inf['ch7'] * 100:+.1f}% — ضمن المعتاد")},
             {"k": "rsi", "on": bool(on["rsi25"] or on["rsi30"]), "w": BOT_W["rsi25"] if on["rsi25"] else BOT_W["rsi30"],
              "txt": ("RSI غير متاح" if r is None else f"RSI {r:.0f} — " + ("تشبّع بيع شديد" if on["rsi25"] else "تشبّع بيع" if on["rsi30"] else "ليس في تشبّع بيع"))},
             {"k": "bb", "on": on["bb"], "w": BOT_W["bb"],
              "txt": (f"أغلق تحت حد بولنجر السفلي ({f(inf['lb'])})" if on["bb"] else f"فوق حد بولنجر السفلي ({f(inf['lb'])})")}]
    return {"score": s, "lv": lv, "lbl": lbl, "parts": parts, "day": T[t], "px": C[t], "since": (t - st) if s >= 30 else 0,
            "low": min(L[st:t + 1]) if s >= 30 else None, "btc_up": btc_up, "own": own,
            "real": BOT_REAL.get(lv if lv != "none" else "zone"), "normal": BOT_REAL["normal"], "years": BOT_REAL["years"]}


'''

GUIDE = '''    "bot": {"sec": "fc", "ico": "🟢", "name": "مؤشر القاع — متى أشتري؟", "lead": "m",
            "idea": "يبحث عن هبوط حادّ مبالغ فيه بالنسبة لطبيعة العملة نفسها، وهي حالات ارتدّ بعدها السعر غالباً خلال أيام إلى أسبوعين.",
            "calc": "ثلاثة أجزاء على شموع يومية مسكّرة، مجموعها من 100: نزول 7 أيام أكبر من ضعف حركة العملة الأسبوعية المعتادة (تُقاس من تذبذب آخر 60 يوماً) = 50 · مؤشر القوة النسبية RSI ≤ 25 = 30 أو ≤ 30 = 20 · إغلاق تحت حد بولنجر السفلي (20، 2) = 20.",
            "read": "👀 راقب من 30 · 🟡 منطقة شراء من 50 · 🟢 قاع قوي من 60. لا ينتظر تأكيد الانعطاف لأن القياس أظهر أن الانتظار يضيّع أغلب الارتداد.",
            "meas": "على 28 عملة بأسعار OKX الحقيقية (2021–2026، كل يوم يرى ما قبله فقط): من 60 فأكثر كان السعر أعلى بعد 14 يوماً في 64% من المرات مقابل 46% في الأيام العادية، والوسيط +3.9% مقابل −1.3%، وتحقق ذلك في 26 عملة من 28 · حين يكون البيتكوين فوق متوسط 200 يوم: 76% · تحته: 57% · بعد 30 يوماً لا فرق يُذكر.",
            "limit": "في السوق الهابط المستمر قد يستمر الهبوط (في 2026 حتى الآن لم ينجح: −4 نقاط عن العادي)، وقد ينزل السعر بعد الإشارة نحو 15% خلال شهر قبل أن يرتد أو دونه — لذلك الشراء على دفعات أسلم. ليس نصيحة مالية."},
'''

JS = '''function fcBot(r){const b=r.bot;if(!b)return '';                                    // 🟢 v3.36.27: مؤشر القاع على بطاقة العملة
  return `<div class="fc-bot lv-${gEsc(b.lv)}" title="مؤشر القاع (شموع يومية · من أيام إلى أسبوعين) — اضغط للتفاصيل">${b.lv==='none'?'🟢 مؤشر القاع':gEsc(b.lbl)} <b>${b.score}/100</b>${b.lv==='none'?' — لا إشارة شراء الآن':b.since>0?` · منذ ${b.since} ${b.since===1?'يوم':'أيام'}`:' · اليوم'}</div>`}
function fcBotDet(r){const b=r.bot;if(!b)return '';const R=b.real||{},N=b.normal||{},o=(b.own||{})[b.lv!=='none'?b.lv:'zone'],B=gEsc(r.base);
  const lvT={watch:'«👀 راقب» (30 فأكثر)',zone:'«🟡 منطقة شراء» (50 فأكثر)',strong:'«🟢 قاع قوي» (60 فأكثر)'}[b.lv!=='none'?b.lv:'zone'];
  const bt=b.btc_up==null?'':b.btc_up?`₿ البيتكوين فوق متوسط 200 يوم — في هذا الجو كانت النتيجة أقوى: ${R.up[0]}% (الوسيط ${R.up[1]>0?'+':''}${R.up[1]}%)`
    :`₿ البيتكوين تحت متوسط 200 يوم — في هذا الجو كانت النتيجة أضعف: ${R.down[0]}% (الوسيط ${R.down[1]>0?'+':''}${R.down[1]}%)`;
  return `<div class="fc-botd lv-${gEsc(b.lv)}"><div><b>🟢 مؤشر القاع — متى أشتري؟</b> <small>(من أيام إلى أسبوعين · آخر إغلاق يومي)</small> · <b>${b.score}/100</b> ${b.lv==='none'?'— لا إشارة الآن':gEsc(b.lbl)}</div>
    ${(b.parts||[]).map(p=>`<div class="fc-botp ${p.on?'on':''}">${p.on?'✅':'▫️'} ${gEsc(p.txt)} <small>(${p.w})</small></div>`).join('')}
    <div>🔬 ${b.lv==='none'?'حين يدخل '+lvT:'بعد '+lvT}، على 28 عملة بأسعار حقيقية (2021–2026): كان السعر أعلى بعد 14 يوماً في <b>${R.p14}%</b> من المرات (العادي ${N.p14}%) · بعد 7 أيام ${R.p7}% (العادي ${N.p7}%) · الوسيط بعد 14 يوماً <b>${R.m14>0?'+':''}${R.m14}%</b> (العادي ${N.m14}%) · تحقق في ${gEsc(R.coins||'')} عملة · بعد 30 يوماً لا فرق يُذكر.</div>
    ${bt?`<div>${bt}</div>`:''}
    ${o?`<div>📒 على ${B}: ${o.p14}% من ${o.n} ${o.n>2&&o.n<11?'مرات':'مرة'} كان أعلى بعد 14 يوماً (الوسيط ${o.m14>0?'+':''}${o.m14}%)</div>`:''}
    <div class="fc-botw">⚠️ ${gEsc(b.years||'')} · قد ينزل السعر بعد الإشارة: عادةً حتى ${Math.abs(R.dd||0)}% خلال 30 يوماً (مثل الأيام العادية) — الشراء على دفعات أسلم · لا ننتظر تأكيد الانعطاف لأن الانتظار أضاع أغلب الارتداد في القياس.</div></div>`}
'''

CSS = '''.fc-bot{margin-top:6px;font-size:12px;padding:4px 8px;border-radius:8px;background:rgb(var(--ov-rgb)/.03);color:var(--mut)}.fc-bot.lv-watch{color:var(--amber)}.fc-bot.lv-zone{color:var(--amber);background:rgb(var(--amber-rgb)/.08)}.fc-bot.lv-strong{color:var(--green);background:rgb(var(--green-rgb)/.10);font-weight:700}.fc-botd{margin:8px 0;padding:8px 10px;border:1px solid var(--line);border-radius:10px;font-size:12px;line-height:1.8}.fc-botd.lv-strong{border-color:rgb(var(--green-rgb)/.5)}.fc-botd.lv-zone{border-color:rgb(var(--amber-rgb)/.5)}.fc-botp{color:var(--mut2)}.fc-botp.on{color:var(--tx)}.fc-botw{color:var(--amber);font-size:11.5px;margin-top:4px}'''

R = [
    ('''def _fc_meta():''', PY + '''def _fc_meta():'''),
    ('''    out["x"] = _safe(xc_coin, sym, d1, l1, _XC_BTC.get("m") or {}, default=None)      # 🧲💪 v3.32.0: برّه التصويت''',
     '''    out["x"] = _safe(xc_coin, sym, d1, l1, _XC_BTC.get("m") or {}, default=None)      # 🧲💪 v3.32.0: برّه التصويت
    out["bot"] = _safe(bot_coin, sym, d1, _XC_BTC.get("m") or {}, default=None)      # 🟢 v3.36.27: مؤشر القاع'''),
    ('''    # ── 🔮 الإضافات ──''', GUIDE + '''    # ── 🔮 الإضافات ──'''),
    ('''      <div class="fc-rows"><div class="fc-r fc-hd">''', '''      ${fcBot(r)}<div class="fc-rows"><div class="fc-r fc-hd">'''),
    ('''<div class="ind-det" onclick="event.stopPropagation()">${tabs}<div class="fc-sum">''',
     '''<div class="ind-det" onclick="event.stopPropagation()">${tabs}${fcBotDet(r)}<div class="fc-sum">'''),
    ('''function fcVote(z){''', JS + '''function fcVote(z){'''),
    ('''.fb.g{color:var(--green)}''', CSS + '''.fb.g{color:var(--green)}'''),
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
