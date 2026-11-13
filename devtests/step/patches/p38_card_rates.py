# 📈 patch 38 (dashboard · cards) — the owner (13-11): «اريد معدل الربح المتوقع يومي شهري سنوي لكل الكروت ، زيل القديم لان القديم عند
#   تشغيل اعادة الاستثمار يطفي لانه مرتبط بعداد الربح ، لا اتعدل على عداد الربح ، بس خلي الكروت تعتمد كل واحد على تداولها ان كان بدون
#   استثمار او استثمار».
#   ① the old rate = the profit counter (total_profit × net) ÷ days — with 💠 reinvest the counter stays near zero (the profit goes back into
#      orders) ⇒ the rate died. New: each card's rate = ITS OWN trading profit (n + 💠 r per day — the same `trade_period` the widget,
#      the reports and the archive use) ÷ its run days (from its fixed start, else its first sight) — daily · ×30 · ×365.
#      DCA (sell: coin · buy: USDT) and the 🔴 periodic SELL (coin) keep their own coin profit (that IS their trading). The profit counter
#      itself is not touched.
#   ② every card shows it: ♾️ ➕ 🎚️ 🪜 (as before, now with the sign and small amounts kept) · DCA (+ yearly in the new skins) ·
#      🔁 periodic and 💹 value path get «⏱️ التشغيل» and «📈 معدل يومي / شهري / سنوي» rows (they had none) · the tip says where it comes from
#   ③ all-time trading per bot is read once a minute (one `trade_period` from the first day any live bot has), not on every refresh
#   python3 devtests/step/patches/p38_card_rates.py Holy_Dashboard.pyw
import os, sys

PY_RATES = '''_BTA_CACHE = {"t": 0.0, "v": None}


def _bot_trade_all(force=False):
    """📈 v3.36.33: ربح التداول لكل بوت بكل أيامه (عادي + 💠 — نفس `trade_period` للويدجت والتقارير والأرشيف) · يتحدّث كل دقيقة
    من أقدم يوم لأي بوت حي (دفتره أو تاريخ تشغيله) لليوم"""
    c = _BTA_CACHE
    if not force and c["v"] is not None and time.time() - c["t"] < 60:
        return c["v"]
    today = datetime.now().strftime("%Y-%m-%d")
    d0 = today
    led = load_json(LEDGER) or {}
    meta = _safe(bot_meta, default={}) or {}
    for b in bot_dirs().values():
        key = os.path.relpath(b["dir"], ROOT)
        days = [d for d in (((led.get(key) or {}) if isinstance(led, dict) else {}).get("daily") or {}) if isinstance(d, str) and len(d) == 10]
        if days:
            d0 = min(d0, min(days))
        s = float((meta.get(key) or {}).get("started") or 0)
        if s > 0:
            d0 = min(d0, datetime.fromtimestamp(s).strftime("%Y-%m-%d"))
    tb = trade_period(d0, today).get("by_bot") or {}
    v = {k: round(float(x.get("n") or 0) + float(x.get("r") or 0), 8) for k, x in tb.items()}
    c.update(t=time.time(), v=v)
    return v


def _rate_fix(b, ta):
    """📈 v3.36.33 (المالك 13-11): معدل الربح لكل بطاقة من تداولها هي ÷ أيام تشغيلها — بدل عدّاد الربح (يبقى قرب الصفر بإعادة
    الاستثمار) · عدّاد الربح نفسه ما يتغيّر · DCA والدوري البيعي ربحهم بالعملة = تداولهم"""
    bt = b.get("bot_type") or "grid"
    days = float(b.get("age_days") or 0) or float(b.get("rate_days") or 0)
    if bt in ("dca", "dca_buy"):
        d = b.get("dca") or {}
        tot, unit = float(d.get("coin_profit") or 0), ("$" if (bt == "dca_buy" or d.get("is_buy")) else (d.get("base_coin") or ""))
    elif bt == "rec_sell":
        r = b.get("rec") or {}
        tot, unit = float(r.get("profit") or 0), (r.get("base") or b["symbol"].split("-")[0])
    else:
        unit = "$"
        if ta is not None and b.get("dir") in ta:
            tot = float(ta[b["dir"]])
        elif ta is not None:
            tot = 0.0                                    # لا تداول مسجّل بعد
        else:                                            # تعذّرت قراءة الدفاتر ⇒ ربح البطاقة نفسه (كما كان)
            tot = float((b.get("rec") or {}).get("profit") or 0) if bt in _REC_T else float(b.get("profit") or 0)
    b["rate_unit"], b["rate_trade"], b["rate_days"] = unit, round(tot, 8), round(days, 4)
    b["rate_daily"] = round(tot / days, 8) if days >= 0.5 else None


'''

JS_RATES = '''/* 📈 v3.36.33 (المالك 13-11): معدل الربح لكل بطاقة = تداولها هي (عادي + 💠) ÷ أيام تشغيلها — يومي · ×30 · ×365 · بالدولار أو بعملة البوت */
function rateNum(v){v=+v||0;const a=Math.abs(v),k=a>=100?1:a>=1?2:a>=0.01?4:a>=0.0001?6:8;return (v>=0?'+':'')+v.toFixed(k)}
function rateU(b){return b&&b.rate_unit&&b.rate_unit!=='$'?' '+b.rate_unit:'$'}
function rateTxt(b){const rd=b&&b.rate_daily;if(rd==null)return '—';const u=rateU(b);return `${rateNum(rd)}${u} / ${rateNum(rd*30)}${u} / ${rateNum(rd*365)}${u}`}
function rateTip(b){if(!b||b.rate_daily==null)return 'يحتاج نصف يوم تشغيل على الأقل';
  return `معدل ربح هذا البوت من تداوله هو${b.bot_type==='dca'||b.bot_type==='dca_buy'||b.bot_type==='rec_sell'?'':' (عادي + 💠 إعادة الاستثمار)'}: ${rateNum(+b.rate_trade||0)}${rateU(b)} خلال ${(+b.rate_days||0).toFixed(1)} يوم ÷ الأيام — الشهري ×30 والسنوي ×365 تقديريان · عدّاد الربح لا يتغيّر`}
function cardRates(R,b){if(R.age){const t=stAge(b);if(R.age.textContent!==t)R.age.textContent=t;R.age.title=stAgeT(b)}
  if(R.rates){const t=rateTxt(b);if(R.rates.textContent!==t)R.rates.textContent=t;R.rates.title=rateTip(b)}}
'''

ROWS = '''    <div class="rcrow"><span class="dl" title="منذ تاريخ تشغيل البوت">⏱️ التشغيل</span><b class="num" data-k="age">—</b></div>
    <div class="rcrow"><span class="dl" title="ربح تداول هذا البوت (عادي + 💠 إعادة الاستثمار) ÷ أيام تشغيله — الشهري ×30 والسنوي ×365 تقديريان">📈 معدل يومي / شهري / سنوي</span><b class="num" data-k="rates">—</b></div>'''

R = [
    # ── the server: each bot's rate from its own trading
    ('''            "age_days": round(age_days, 4), "started": round(_started, 1),''',
     '''            "age_days": round(age_days, 4), "started": round(_started, 1), "rate_days": round(rate_days, 4),'''),
    ('''def overview():
    bots = [bot_snapshot(b) for b in bot_dirs().values()]
    bots.sort(key=lambda x: x["symbol"])''',
     '''def overview():
    bots = [bot_snapshot(b) for b in bot_dirs().values()]
    bots.sort(key=lambda x: x["symbol"])
    _ta = _safe(_bot_trade_all, default=None)          # 📈 v3.36.33: معدل كل بطاقة من تداولها هي (عادي + 💠)
    for _b in bots:
        _safe(_rate_fix, _b, _ta)'''),
    # ── ♾️ ➕ 🎚️ 🪜 card
    ('''    const rd=b.rate_daily;
    if(rd!=null){
      R.rates.textContent=`+${rd.toFixed(2)} / +${(rd*30).toFixed(1)} / +${(rd*365).toFixed(0)} $`;
      R.rates.title='معدل الربح $ (الكلي ÷ أيام التشغيل) — الشهري والسنوي تقديريان';
    }else{R.rates.textContent='—';R.rates.title='يحتاج نصف يوم تشغيل على الأقل'}''',
     '''    R.rates.textContent=rateTxt(b);R.rates.title=rateTip(b);      // 📈 v3.36.33: من تداول البوت نفسه (عادي + 💠) — لا من عدّاد الربح'''),
    # ── DCA card
    ('''      R.rday.title=R.rmon.title=R.ryear.title='معدل ربح '+bc+' (محسوب من الربح الكلي ÷ أيام التشغيل)';''',
     '''      R.rday.title=R.rmon.title=R.ryear.title=rateTip(b);'''),
    # ── 🔁 periodic and 💹 value path: two new rows each + their update
    ('''    <div class="rcrow"><span class="dl" title="العمولات اللي دفعها البوت فعلاً بالمنصة (بعملتها) — ونسبة عمولة حسابك المتعلّمة من التنفيذ">💸 العمولات المدفوعة</span><b class="num" data-k="fees">—</b></div>''',
     '''    <div class="rcrow"><span class="dl" title="العمولات اللي دفعها البوت فعلاً بالمنصة (بعملتها) — ونسبة عمولة حسابك المتعلّمة من التنفيذ">💸 العمولات المدفوعة</span><b class="num" data-k="fees">—</b></div>
''' + ROWS),
    ('''    <div class="rcrow"><span class="dl" title="العمولات التي دفعها البوت فعلاً بالمنصة (بعملتها) — ونسبة عمولة حسابك المتعلَّمة من التنفيذ">💸 العمولات المدفوعة</span><b class="num" data-k="fees">—</b></div>''',
     '''    <div class="rcrow"><span class="dl" title="العمولات التي دفعها البوت فعلاً بالمنصة (بعملتها) — ونسبة عمولة حسابك المتعلَّمة من التنفيذ">💸 العمولات المدفوعة</span><b class="num" data-k="fees">—</b></div>
''' + ROWS),
    ('''   const F=r.fees||{},ks=Object.keys(F);R.fees.innerHTML=''',
     '''   cardRates(R,b);const F=r.fees||{},ks=Object.keys(F);R.fees.innerHTML='''),
    ('''  {const F=r.fees||{},ks=Object.keys(F);R.fees.innerHTML=''',
     '''  cardRates(R,b);{const F=r.fees||{},ks=Object.keys(F);R.fees.innerHTML='''),
    # ── the new skins read them too
    ('''['التشغيل',skText(el,'age')],['يومي / شهري',skText(el,'rday')+' / '+skText(el,'rmon')]];''',
     '''['التشغيل',skText(el,'age')],['المعدل يومي / شهري / سنوي',[skText(el,'rday'),skText(el,'rmon'),skText(el,'ryear')].join(' / ')]];'''),
    ('''['السعر الآن',skText(el,'cp')],['الوضع',r.mode==='avg'?'📊 بالمعدل':'🧩 كل أمر وحده']];''',
     '''['السعر الآن',skText(el,'cp')],['الوضع',r.mode==='avg'?'📊 بالمعدل':'🧩 كل أمر وحده'],['التشغيل',skText(el,'age')],['المعدل يومي / شهري / سنوي',skText(el,'rates')]];'''),
    ('''['📦 يحمل',skText(el,'pos')],['السعر الآن',skText(el,'cp')],['💸 العمولات',skText(el,'fees')]];''',
     '''['📦 يحمل',skText(el,'pos')],['السعر الآن',skText(el,'cp')],['💸 العمولات',skText(el,'fees')],['التشغيل',skText(el,'age')],['المعدل يومي / شهري / سنوي',skText(el,'rates')]];'''),
    # ── the helpers (JS) · the server functions
    ('''function stAge(x){''', JS_RATES + '''function stAge(x){'''),
    ('''def overview():
    bots = [bot_snapshot(b) for b in bot_dirs().values()]''', PY_RATES + '''def overview():
    bots = [bot_snapshot(b) for b in bot_dirs().values()]'''),
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
