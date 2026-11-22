# p142 — v3.36.77 🏦 new data for the groups: derivatives (funding · open interest · the quarterly premium · the top traders) · the Coinbase
#   premium · the stablecoins · the US calendar (the owner 21-11: «وهذه ضيفها : بيانات العقود (التمويل، العقود المفتوحة، العلاوة الفصلية،
#   مراكز الكبار)، وعلاوة كوينبيس، والعملات المستقرة، وتقويم الأخبار الأمريكية»)
#   · fetchers (public · no keys · each on its own schedule · saved in Holy_Pro.json like the other readings): open interest and top
#     traders (OKX rubik · daily · ~400 days back the first time) · funding (OKX · the daily mean of the realised rate · ~3 months) · the
#     quarterly premium (OKX quarterly future vs its index · annualised · a daily snapshot from now on — OKX keeps no history of expired
#     contracts) · Coinbase BTC-USD daily closes (years back the first time) · the stablecoins' total supply (DefiLlama · daily)
#   · the long/short accounts, taker volume, open interest, top traders and funding now for every coin the groups measure (not only the strip)
#   · new members (each with its plain name and its neutral name): P-oi · P-top · P-fund · P-basis (🏦 the derivatives groups of the coin and
#     the market) · M-cbp · M-stb (🏦 the market's money group) · M-cal (🎢 the market's «calm or storm» group: a high-impact US release falls
#     inside the next candle) — tested on history like every member (the ones without history stay 🧪 until they earn it)
#   · every daily reading is read after its day has closed (p141) · Coinbase vs OKX closes of the same UTC day
#   · 📈 the market now: one line each (the Coinbase premium · the stablecoins · Bitcoin's derivatives · the quarterly premium · the next US
#     release) · 🗓️ a notice ~30 minutes before a high-impact US release (its own type in ⚙️, 📲 by default)
#   python3 devtests/step/patches/p142_new_data.py Holy_Dashboard.pyw
import sys, os

R = [
    ('''PRO_EVERY = {"ls": 6 * 3600, "tk": 6 * 3600, "dv": 3600, "pc": 6 * 3600, "mv": 12 * 3600, "cal": 6 * 3600,''',
     '''PRO_EVERY = {"ls": 6 * 3600, "tk": 6 * 3600, "dv": 3600, "pc": 6 * 3600, "mv": 12 * 3600, "cal": 6 * 3600,
             "oi": 12 * 3600, "top": 12 * 3600, "fund": 8 * 3600, "basis": 4 * 3600, "cbp": 6 * 3600, "stb": 12 * 3600,     # 🏦 v3.36.77'''),
    # pro_tick: the new sources · every coin the groups measure
    ('''        coins = [s_.split("-")[0].upper() for s_ in ticker_cfg()["coins"]]
        db = _pro_db()                                       # 🌐 الجلب على نسخة — بلا قفل (أول مرة يجيب التاريخ ~دقيقة)
        ch = False
        for f, a in ((_pro_ls, (coins,)), (_pro_tk, (coins,)), (_pro_pc, ()), (_pro_dv, ()), (_pro_mv, (coins,)), (_pro_cal, ()),
                     (_pro_vix, ()), (_pro_us10, ()), (_pro_dxy, ()), (_pro_epu, ()), (_pro_gpr, ()), (_pro_tone, ())):''',
     '''        coins = [s_.split("-")[0].upper() for s_ in ticker_cfg()["coins"]]
        uc = list(dict.fromkeys(coins + [s_.split("-")[0].upper() for s_ in (_safe(_sg_universe, default=[]) or [])]))   # 🏦 v3.36.77: كل عملات المجاميع
        db = _pro_db()                                       # 🌐 الجلب على نسخة — بلا قفل (أول مرة يجيب التاريخ ~دقيقة)
        ch = False
        for f, a in ((_pro_ls, (uc,)), (_pro_tk, (uc,)), (_pro_pc, ()), (_pro_dv, ()), (_pro_mv, (coins,)), (_pro_cal, ()),
                     (_pro_vix, ()), (_pro_us10, ()), (_pro_dxy, ()), (_pro_epu, ()), (_pro_gpr, ()), (_pro_tone, ()),
                     (_pro_oi, (uc,)), (_pro_top, (uc,)), (_pro_fund, (uc,)), (_pro_basis, ()), (_pro_cbp, ()), (_pro_stb, ())):'''),
    # the members: plain names
    ('''    "P-fund": ("market", "💸 البيع مزدحم في العقود (قراءة عكسية)", "💸 الشراء مزدحم في العقود (قراءة عكسية)",
               "البائعون في العقود يدفعون الرسوم — البيع مزدحم وقد يرتد السعر", "المشترون في العقود يدفعون رسوماً عالية — الشراء مزدحم وقد يتراجع السعر", "Funding"),
}''', '''    "P-fund": ("market", "💸 البيع مزدحم في العقود (قراءة عكسية)", "💸 الشراء مزدحم في العقود (قراءة عكسية)",
               "البائعون في العقود يدفعون الرسوم — البيع مزدحم وقد يرتد السعر", "المشترون في العقود يدفعون رسوماً عالية — الشراء مزدحم وقد يتراجع السعر", "Funding"),
    "P-oi": ("market", "🏦 أموال جديدة تدفع الصعود في العقود", "🏦 أموال جديدة تدفع الهبوط في العقود",          # 🏦 v3.36.77
             "العقود المفتوحة زادت بقوة مع صعود السعر — مراكز شراء جديدة تدعم الصعود", "العقود المفتوحة زادت بقوة مع هبوط السعر — مراكز بيع جديدة تدفع الهبوط",
             "Open interest"),
    "P-top": ("market", "🐋 كبار المتداولين يميلون للشراء", "🐋 كبار المتداولين يميلون للبيع",
              "مراكز كبار المتداولين في العقود تميل للشراء أكثر من المعتاد", "مراكز كبار المتداولين في العقود تميل للبيع أكثر من المعتاد", "Top traders"),
    "P-basis": ("market", "📆 العقود الفصلية رخيصة (قراءة عكسية)", "📆 العقود الفصلية مرتفعة كثيراً (قراءة عكسية)",
                "علاوة العقود الفصلية على السعر الفوري منخفضة على غير العادة — تشاؤم قد ينقلب", "علاوة العقود الفصلية على السعر الفوري عالية على غير العادة — حماس زائد قد يتراجع",
                "Quarterly basis"),
    "M-cbp": ("market", "🇺🇸 علاوة كوينبيس مرتفعة", "🇺🇸 علاوة كوينبيس منخفضة",
              "سعر البيتكوين في كوينبيس أعلى من المعتاد مقابل المنصات الأخرى — طلب أمريكي قوي", "سعر البيتكوين في كوينبيس أقل من المعتاد مقابل المنصات الأخرى — طلب أمريكي ضعيف",
              "Coinbase premium"),
    "M-stb": ("market", "💵 العملات المستقرة تزيد", "💵 العملات المستقرة تنقص",
              "المعروض من العملات المستقرة زاد أكثر من المعتاد خلال أسبوع — سيولة جديدة جاهزة للشراء", "المعروض من العملات المستقرة نقص أكثر من المعتاد خلال أسبوع — سيولة تخرج من السوق",
              "Stablecoin supply"),
    "M-cal": ("market", "🗓️ خبر أمريكي مهم في المدة القادمة", "🗓️ خبر أمريكي مهم في المدة القادمة",
              "موعد خبر اقتصادي أمريكي عالي التأثير يقع داخل المدة القادمة — الحركة عادة أكبر", "موعد خبر اقتصادي أمريكي عالي التأثير يقع داخل المدة القادمة — الحركة عادة أكبر",
              "US calendar"),
}'''),
    ("    'P-fund': 'رسوم التمويل في العقود',\n",
     "    'P-fund': 'رسوم التمويل في العقود',\n    'P-oi': 'العقود المفتوحة مع حركة السعر',\n    'P-top': 'مراكز كبار المتداولين',\n"
     "    'P-basis': 'علاوة العقود الفصلية',\n    'M-cbp': 'علاوة كوينبيس',\n    'M-stb': 'معروض العملات المستقرة',\n    'M-cal': 'مواعيد الأخبار الأمريكية',\n"),
    # the groups: the market's money and «calm or storm»
    ('''              "no": ("O-bottom",), "add": ("W-crash", "W-surge"), "lv": "now"},
    "m_pro":''', '''              "no": ("O-bottom",), "add": ("W-crash", "W-surge", "M-cal"), "lv": "now"},
    "m_pro":'''),
    ('''    "m_pro": {"sec": "mkt", "ic": "🏦", "nm": "العقود والسيولة الكبيرة", "job": "dir", "say": ("المحترفون والسيولة يدفعون للصعود", "المحترفون والسيولة يدفعون للهبوط"),
              "fam": ("pro",), "lv": "view"},''', '''    "m_pro": {"sec": "mkt", "ic": "🏦", "nm": "العقود والسيولة الكبيرة", "job": "dir", "say": ("المحترفون والسيولة يدفعون للصعود", "المحترفون والسيولة يدفعون للهبوط"),
              "fam": ("pro",), "add": ("M-cbp", "M-stb"), "lv": "view"},'''),
    # the readings into the events (the same _sg_series as the others)
    ('''    for k, (ks, vs) in (ctx.get("mkt") or {}).items():
        sf = _SG_FNG if k == "fng" else (lambda vs_, j, k=k: _mac_sig(k, vs_, j)[0])
        _sg_series(D, dx, "M-" + k, ks, vs, sf, t0, ev)
    for k, (ks, vs) in (ctx.get("pro") or {}).items():
        sf = {"ls": lambda vs_, j: _pro_ls_sig(vs_, j)[0], "tk": lambda vs_, j: _pro_tk_sig(vs_, j)[0],
              "pc": lambda vs_, j: _pro_pc_sig(vs_, j)[0], "mv": lambda vs_, j: _pro_mv_sig(vs_[j])}[k]
        _sg_series(D, dx, "P-" + k, ks, vs, sf, t0, ev)''', '''    for k, (ks, vs) in (ctx.get("mkt") or {}).items():
        if k == "cal":                                       # 🗓️ v3.36.77: خبر أمريكي عالي التأثير يقع داخل الشمعة التالية (المواعيد معروفة مسبقاً)
            _sg_cal_ev(D, dx, ks, t0, ev)
            continue
        sf = _SG_FNG if k == "fng" else _SG_MSF[k] if k in _SG_MSF else (lambda vs_, j, k=k: _mac_sig(k, vs_, j)[0])
        _sg_series(D, dx, "M-" + k, ks, vs, sf, t0, ev)
    for k, (ks, vs) in (ctx.get("pro") or {}).items():
        sf = {"ls": lambda vs_, j: _pro_ls_sig(vs_, j)[0], "tk": lambda vs_, j: _pro_tk_sig(vs_, j)[0],
              "pc": lambda vs_, j: _pro_pc_sig(vs_, j)[0], "mv": lambda vs_, j: _pro_mv_sig(vs_[j])}.get(k) or _SG_PSF.get(k)
        if sf:
            _sg_series(D, dx, "P-" + k, ks, vs, sf, t0, ev)'''),
    ('''def _sg_mkt(pdb, fdb):
    """😨 + 🗞️ السلاسل اليومية العامة من ملفات اللوحة (بلا شبكة) — كل واحدة مؤخّرة بتأخر نشرها"""
    out = {}''', '''def _sg_mkt(pdb, fdb, cdb=None):
    """😨 + 🗞️ السلاسل اليومية العامة من ملفات اللوحة (بلا شبكة) — كل واحدة مؤخّرة بتأخر نشرها · 🏦 v3.36.77: علاوة كوينبيس (مع إغلاقات
    البيتكوين اليومية من ملف الشموع) · العملات المستقرة · مواعيد الأخبار الأمريكية"""
    out = _safe(_sg_mkt2, pdb, cdb, default=None) or {}'''),
    ('''    for k in ("ls", "tk", "pc", "mv"):
        e_ = (pdb.get(k) or {}).get(ccy)
        if isinstance(e_, dict) and e_.get("d"):
            ks, vs = _pro_sorted(e_)
            if len(vs) >= 30:
                pro[k] = ([x + SG_PLAG for x in ks], vs)''', '''    for k in ("ls", "tk", "pc", "mv", "top", "fund", "basis"):
        e_ = (pdb.get(k) or {}).get(ccy)
        if isinstance(e_, dict) and e_.get("d"):
            ks, vs = _pro_sorted(e_)
            if len(vs) >= 30:
                pro[k] = ([x + SG_PLAG for x in ks], vs)
    oi = _safe(_sg_oi_px, (pdb.get("oi") or {}).get(ccy), drows, default=None)     # 🏦 v3.36.77: العقود المفتوحة مع سعر اليوم نفسه
    if oi:
        pro["oi"] = oi'''),
    ("    mkt, fng = _sg_mkt(pdb, fdb), _sg_fng_raw(fdb)\n", "    mkt, fng = _sg_mkt(pdb, fdb, cdb), _sg_fng_raw(fdb)\n"),
    # 📈 the market now: the new lines
    ('''    out["mkt"] = M
    return out


AN_TY = {''', '''    for ln in _safe(_an_newdata, pdb or {}, cdb, default=[]) or []:       # 🏦 v3.36.77: العقود · كوينبيس · العملات المستقرة · الأخبار الأمريكية
        M["lines"].append(ln)
    out["mkt"] = M
    return out


AN_TY = {'''),
    ('''    "season": ("🪙", "السيولة بين البيتكوين والعملات", "mkt", "view"), "fng": ("😨", "خوف أو طمع شديد", "mkt", "view")}''',
     '''    "season": ("🪙", "السيولة بين البيتكوين والعملات", "mkt", "view"), "fng": ("😨", "خوف أو طمع شديد", "mkt", "view"),
    "cal": ("🗓️", "خبر أمريكي مهم بعد قليل (قبل نصف ساعة)", "mkt", "now")}'''),
    # 🗓️ the tick: the calendar notice (every 5 minutes, before delivery)
    ('''        cdb = None
        if cfg["on"]:
            _sg_deliver(blocks, st, cfg, now, send=send)''', '''        cdb = None
        blocks = list(blocks or []) + (_safe(_cal_facts, _pro_db(), st, now, cfg.get("alv") or {}, default=[]) or [])     # 🗓️ v3.36.77
        if cfg["on"]:
            _sg_deliver(blocks, st, cfg, now, send=send)'''),
]

# the new fetchers (after _pro_cal) and the readings' functions (after _pro_mv_sig)
FETCH = r'''

def _pro_page(path, pages, key=0):
    """صفحات OKX للخلف (end = أقدم وقت في الصفحة السابقة) — None إن فشل الطلب الأول"""
    rows, cur = [], None
    for k in range(max(1, pages)):
        d = _pro_okx(path + (f"&end={cur}" if cur else ""))
        if d is None:
            return None if k == 0 else rows
        if not d:
            break
        rows += d
        last = d[-1][key] if isinstance(d[-1], list) else d[-1].get(key)
        if last == cur:
            break
        cur = last
        time.sleep(0.45)                                     # حد OKX للإحصاءات: 5 طلبات كل ثانيتين
    return rows


def _pro_rubik(db, now, coins, key, path, col):
    """🏦 سلسلة يومية لكل عملة من إحصاءات OKX للعقود (نحو 400 يوم أول مرة · ثم الجديد) — col: رقم العمود"""
    ch = False
    for ccy in coins:
        e = db.setdefault(key, {}).setdefault(ccy, {})
        if not _pro_due(e, key, now) or (e.get("na") and now - float(e.get("ts") or 0) < 7 * _PRO_DAY):
            continue
        e["ts"] = now
        ch = True
        rows = _pro_page(path.format(ccy=ccy), 1 if len(e.get("d") or {}) > 30 else 4)
        if rows is None:
            e["ts"] = now - PRO_EVERY[key] + 1800                 # ما وصل ⇒ يحاول بعد نصف ساعة
            continue
        pr = []
        for x in rows:
            try:
                v = float(x[col])
                if v > 0:
                    pr.append((_pro_dk(x[0]), round(v, 6)))
            except Exception:
                continue
        _pro_merge(e, pr)
        e["na"] = not pr                                       # العملة بلا عقود دائمة في OKX
        time.sleep(0.45)
    return ch


def _pro_oi(db, now, coins):
    """🏦 العقود المفتوحة لكل عملة (OKX العام · يومي · بعدد العملات لا بالدولار) — كل 12 ساعة"""
    return _pro_rubik(db, now, coins, "oi", "/api/v5/rubik/stat/contracts/open-interest-history?instId={ccy}-USDT-SWAP&period=1D&limit=100", 2)


def _pro_top(db, now, coins):
    """🐋 نسبة مراكز كبار المتداولين الطويلة إلى القصيرة لكل عملة (OKX العام · يومي) — كل 12 ساعة"""
    return _pro_rubik(db, now, coins, "top", "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader?instId={ccy}-USDT-SWAP&period=1D&limit=100", 1)


def _pro_fund(db, now, coins):
    """💸 التمويل لكل عملة: متوسط اليوم من الرسوم المحققة (OKX العام · آخر 3 أشهر فقط ثم يتراكم) — كل 8 ساعات"""
    ch = False
    for ccy in coins:
        e = db.setdefault("fund", {}).setdefault(ccy, {})
        if not _pro_due(e, "fund", now) or (e.get("na") and now - float(e.get("ts") or 0) < 7 * _PRO_DAY):
            continue
        e["ts"] = now
        ch = True
        by, after = {}, None
        for k in range(1 if len(e.get("d") or {}) > 30 else 3):
            d = _pro_okx(f"/api/v5/public/funding-rate-history?instId={ccy}-USDT-SWAP&limit=100" + (f"&after={after}" if after else ""))
            if d is None and k == 0:
                e["ts"] = now - PRO_EVERY["fund"] + 1800
            if not d:
                break
            for x in d:
                try:
                    by.setdefault(_pro_dk(x["fundingTime"]), []).append(float(x.get("realizedRate") or x.get("fundingRate") or 0))
                except Exception:
                    continue
            after = d[-1].get("fundingTime")
            time.sleep(0.3)
        pr = [(k_, round(sum(v) / len(v), 8)) for k_, v in by.items() if v]
        _pro_merge(e, pr)
        e["na"] = not pr and e.get("ts") == now
    return ch


def _pro_basis(db, now):
    """📆 علاوة العقود الفصلية على المؤشر (سنوياً %) للبيتكوين والإيثيريوم — لقطة يومية من الآن (المنصة لا تحفظ تاريخ العقود المنتهية) — كل 4 ساعات"""
    ch = False
    for ccy in PRO_BIG:
        e = db.setdefault("basis", {}).setdefault(ccy, {})
        if not _pro_due(e, "basis", now):
            continue
        e["ts"] = now
        ch = True
        got = None
        for fam, idx in ((f"{ccy}-USD", f"{ccy}-USD"), (f"{ccy}-USDT", f"{ccy}-USDT")):
            ins = _pro_okx(f"/api/v5/public/instruments?instType=FUTURES&instFamily={fam}") or []
            q = next((x for x in ins if x.get("alias") == "quarter"), None)
            if not q:
                continue
            tk = _pro_okx(f"/api/v5/market/ticker?instId={q['instId']}") or []
            ix = _pro_okx(f"/api/v5/market/index-tickers?instId={idx}") or []
            try:
                fp, ip, ex = float(tk[0]["last"]), float(ix[0]["idxPx"]), int(q["expTime"]) / 1000.0
                days = (ex - now) / _PRO_DAY
                if fp > 0 and ip > 0 and days > 7:
                    got = round((fp / ip - 1.0) * 365.0 / days * 100.0, 3)
                    break
            except Exception:
                continue
        if got is None:
            e["ts"] = now - PRO_EVERY["basis"] + 1800
            continue
        _pro_merge(e, [(_pro_dk(now), got)])
    return ch


def _pro_cbp(db, now):
    """🇺🇸 إغلاقات البيتكوين اليومية في كوينبيس (العامة · BTC-USD · سنوات للخلف أول مرة) — العلاوة تُحسب مقابل إغلاقات OKX لليوم نفسه — كل 6 ساعات"""
    e = db.setdefault("cbp", {})
    if not _pro_due(e, "cbp", now):
        return False
    e["ts"] = now
    have = e.get("d") or {}
    pages = 1 if len(have) > 200 else 8
    end, pr = int(now), []
    for k in range(pages):
        st = end - 290 * _PRO_DAY
        j = _http_json("https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400"
                       f"&start={time.strftime('%Y-%m-%dT00:00:00Z', time.gmtime(st))}&end={time.strftime('%Y-%m-%dT00:00:00Z', time.gmtime(end))}", timeout=15)
        if not isinstance(j, list):
            if k == 0:
                e["ts"] = now - PRO_EVERY["cbp"] + 1800
            break
        for x in j:
            try:
                if float(x[4]) > 0 and int(x[0]) + _PRO_DAY <= now:    # يوم مكتمل فقط
                    pr.append((_pro_dk(x[0]), float(x[4])))
            except Exception:
                continue
        if len(j) < 50:
            break
        end = st
        time.sleep(0.4)
    _pro_merge(e, pr)
    return True


def _pro_stb(db, now):
    """💵 المعروض الكلي للعملات المستقرة بالدولار (DefiLlama العام · يومي) — كل 12 ساعة"""
    e = db.setdefault("stb", {})
    if not _pro_due(e, "stb", now):
        return False
    e["ts"] = now
    j = _http_json("https://stablecoins.llama.fi/stablecoincharts/all", timeout=20)
    if not isinstance(j, list):
        e["ts"] = now - PRO_EVERY["stb"] + 1800
        return True
    pr = []
    for x in j:
        try:
            v = (x.get("totalCirculatingUSD") or x.get("totalCirculating") or {}).get("peggedUSD")
            if v and float(v) > 0:
                pr.append((_pro_dk(x["date"]), round(float(v))))
        except Exception:
            continue
    _pro_merge(e, pr)
    return True
'''

SIGS = r'''

def _pro_q(vals, i, n=90, m=30):
    """موقع القيمة i بين آخر n قيمة قبلها ومعها (0..1) — None إن قلّ التاريخ عن m"""
    w = vals[max(0, i - n + 1):i + 1]
    return _pro_pct(w, vals[i]) if len(w) >= m else None


def _pro_top_sig(vals, i):
    """🐋 كبار المتداولين: ميلهم أعلى من 85% من آخر 3 أشهر ⇒ +1 · أقل من 15% ⇒ −1 (نتبعهم)"""
    p = _pro_q(vals, i)
    return None if p is None else 1.0 if p >= 0.85 else -1.0 if p <= 0.15 else 0.0


def _pro_fund_sig(vals, i):
    """💸 التمويل: أعلى من 90% من آخر 3 أشهر ⇒ الشراء مزدحم (−1) · أقل من 10% ⇒ البيع مزدحم (+1) — قراءة عكسية"""
    p = _pro_q(vals, i)
    return None if p is None else -1.0 if p >= 0.9 else 1.0 if p <= 0.1 else 0.0


def _pro_basis_sig(vals, i):
    """📆 العلاوة الفصلية: أعلى من 90% من آخر 3 أشهر ⇒ حماس زائد (−1) · أقل من 10% ⇒ تشاؤم (+1) — قراءة عكسية"""
    p = _pro_q(vals, i)
    return None if p is None else -1.0 if p >= 0.9 else 1.0 if p <= 0.1 else 0.0


def _pro_oi_sig(vals, i):
    """🏦 العقود المفتوحة [العقود · سعر اليوم]: زيادة 3 أيام أعلى من 80% من آخر 3 أشهر مع حركة سعر ≥ 1% ⇒ بجهة السعر (أموال جديدة تدفعها)"""
    if i < 33:
        return None
    ch = [vals[j][0] / vals[j - 3][0] - 1.0 if vals[j - 3][0] else 0.0 for j in range(max(3, i - 89), i + 1)]
    if len(ch) < 30:
        return None
    p = _pro_pct(ch, ch[-1])
    cp = vals[i][1] / vals[i - 3][1] - 1.0 if vals[i - 3][1] else 0.0
    return (1.0 if cp >= 0.01 else -1.0 if cp <= -0.01 else 0.0) if p >= 0.8 and ch[-1] > 0 else 0.0


def _mkt_cbp_sig(vals, i):
    """🇺🇸 علاوة كوينبيس (%): أعلى من 85% من آخر 3 أشهر ⇒ +1 · أقل من 15% ⇒ −1"""
    p = _pro_q(vals, i)
    return None if p is None else 1.0 if p >= 0.85 else -1.0 if p <= 0.15 else 0.0


def _mkt_stb_sig(vals, i):
    """💵 العملات المستقرة: تغيّر 7 أيام أعلى من 80% من تغيّرات السنة ⇒ +1 · أقل من 20% ⇒ −1"""
    if i < 67:
        return None
    ch = [vals[j] / vals[j - 7] - 1.0 for j in range(max(7, i - 364), i + 1) if vals[j - 7]]
    if len(ch) < 60:
        return None
    p = _pro_pct(ch, ch[-1])
    return 1.0 if p >= 0.8 else -1.0 if p <= 0.2 else 0.0


_SG_PSF = {"top": lambda vs_, j: _pro_top_sig(vs_, j), "fund": lambda vs_, j: _pro_fund_sig(vs_, j), "basis": lambda vs_, j: _pro_basis_sig(vs_, j),
           "oi": lambda vs_, j: _pro_oi_sig(vs_, j)}
_SG_MSF = {"cbp": lambda vs_, j: _mkt_cbp_sig(vs_, j), "stb": lambda vs_, j: _mkt_stb_sig(vs_, j)}


def _sg_oi_px(e, drows):
    """🏦 العقود المفتوحة مع إغلاق العملة لليوم نفسه ⇒ (المفاتيح بعد إغلاق يومها, [[العقود, السعر]])"""
    if not isinstance(e, dict) or not e.get("d") or not drows:
        return None
    px = {int(r[0]): float(r[4]) for r in drows}
    ks, vs = _pro_sorted(e)
    kk, vv = [], []
    for k, v in zip(ks, vs):
        if px.get(k):
            kk.append(k + SG_PLAG)
            vv.append([float(v), px[k]])
    return (kk, vv) if len(vv) >= 40 else None


def _sg_mkt2(pdb, cdb):
    """🇺🇸 العلاوة (%) = إغلاق كوينبيس ÷ إغلاق OKX لليوم نفسه − 1 · 💵 المعروض · 🗓️ مواعيد الأخبار عالية التأثير — كلها بعد إغلاق يومها"""
    out = {}
    cb = ((pdb or {}).get("cbp") or {}).get("d") or {}
    bd = (((cdb or {}).get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    if cb and bd:
        ok_ = {int(r[0]): float(r[4]) for r in bd}
        ks = sorted(int(k) for k in cb if ok_.get(int(k)))
        if len(ks) > 30:
            out["cbp"] = ([k + SG_PLAG for k in ks], [round((float(cb[str(k)]) / ok_[k] - 1.0) * 100.0, 4) for k in ks])
    ks, vs = _pro_sorted((pdb or {}).get("stb"))
    if len(vs) > 70:
        out["stb"] = ([k + SG_PLAG for k in ks], vs)
    ev = sorted(int(x["t"]) for x in (((pdb or {}).get("cal") or {}).get("ev") or []) if x.get("im") == "h" and x.get("t"))
    if ev:
        out["cal"] = (ev, [])
    return out


def _sg_cal_ev(D, dx, evt, t0, ev):
    """🗓️ عند إغلاق الشمعة t: هل يقع خبر أمريكي عالي التأثير داخل الشمعة التالية؟ ⇒ (M-cal, +1) — المواعيد منشورة قبلها بأيام"""
    if not evt:
        return
    for t in range(max(210, t0), D["n"]):
        a, b = D["T"][t] + dx, D["T"][t] + 2 * dx              # الشمعة التالية [a, b)
        j = bisect.bisect_left(evt, a)
        if j < len(evt) and evt[j] < b:
            ev.setdefault(("M-cal", 1), []).append(t)
'''

NOW = r'''

def _an_newdata(pdb, cdb):
    """📈 v3.36.77: أسطر «الآن» الجديدة للسوق — 🇺🇸 علاوة كوينبيس · 💵 العملات المستقرة · 🏦 عقود البيتكوين · 📆 العلاوة الفصلية · 🗓️ أقرب خبر"""
    L = []
    m2 = _safe(_sg_mkt2, pdb, cdb, default={}) or {}
    if m2.get("cbp"):
        v = m2["cbp"][1]
        p = _pro_q(v, len(v) - 1)
        L.append(("🇺🇸", f"علاوة كوينبيس: {v[-1]:+.3f}% (إغلاق أمس)" + ("" if p is None else f" — أعلى من {round(100 * p)}% من أيام 3 أشهر" if p >= 0.5
                                                                    else f" — أقل من {round(100 * (1 - p))}% من أيام 3 أشهر"),
                  "p" if p is not None and p >= 0.85 else "n" if p is not None and p <= 0.15 else "z"))
    ks, vs = _pro_sorted(pdb.get("stb"))
    if len(vs) >= 8 and vs[-8]:
        c7 = (vs[-1] / vs[-8] - 1.0) * 100.0
        L.append(("💵", f"العملات المستقرة: {vs[-1] / 1e9:,.1f} مليار دولار · {c7:+.2f}% خلال أسبوع", "p" if c7 >= 0.5 else "n" if c7 <= -0.3 else "z"))
    parts = []
    ks, vs = _pro_sorted((pdb.get("fund") or {}).get("BTC"))
    if vs:
        parts.append(f"التمويل {vs[-1] * 100:+.4f}%")
    ks, vs = _pro_sorted((pdb.get("oi") or {}).get("BTC"))
    if len(vs) >= 4 and vs[-4]:
        parts.append(f"العقود المفتوحة {(vs[-1] / vs[-4] - 1) * 100:+.1f}% خلال 3 أيام")
    ks, vs = _pro_sorted((pdb.get("top") or {}).get("BTC"))
    if vs:
        parts.append(f"مراكز الكبار {vs[-1]:.2f} شراء لكل بيع")
    if parts:
        L.append(("🏦", "عقود البيتكوين: " + " · ".join(parts), "z"))
    ks, vs = _pro_sorted((pdb.get("basis") or {}).get("BTC"))
    if vs:
        L.append(("📆", f"علاوة العقود الفصلية للبيتكوين: {vs[-1]:+.1f}% سنوياً", "w" if vs[-1] >= 15 else "z"))
    cr = _safe(_cal_row, pdb, time.time(), None, default=None)
    if cr and cr.get("val") and cr["val"] != "—":
        nm = cr.get("sub", "").split(" · ")[0]
        L.append(("🗓️", f"أقرب خبر أمريكي مهم: {nm} — {cr['val']}", "w" if cr.get("flag") else "z"))
    return L


def _cal_facts(pdb, st, now, lv):
    """🗓️ قبل نحو نصف ساعة من خبر أمريكي عالي التأثير ⇒ إشعار واحد لكل خبر"""
    L_ = (lv or {}).get("cal") or AN_TY["cal"][3]
    if L_ not in ("now", "view"):
        return []
    sent, out = st.setdefault("cal_sent", {}), []
    for x in ((pdb or {}).get("cal") or {}).get("ev") or []:
        try:
            t = int(x["t"])
        except Exception:
            continue
        if x.get("im") != "h" or not (0 < t - now <= 35 * 60):
            continue
        key = f"{t}|{str(x.get('ti') or '')[:40]}"
        if key in sent:
            continue
        sent[key] = round(now)
        nm = _cal_name(x.get("ti"))
        if re.search(r"[A-Za-z]", nm or ""):
            nm = "خبر اقتصادي أمريكي عالي التأثير"
        g = time.gmtime(t)
        ln = f"🗓️ بعد {max(1, round((t - now) / 60))} دقيقة: {nm} ({g.tm_hour:02d}:{g.tm_min:02d} بتوقيت غرينتش)\nالحركة حول هذه الأخبار عادة أكبر من المعتاد — احتمالات لا ضمانات"
        out.append({"sym": "السوق", "ty": "cal", "lv": L_, "urg": False, "ln": ln, "t": "السوق: " + ln.split("\n")[0], "b": ln.split("\n")[1]})
    for k in [k for k, v in sent.items() if now - float(v) > 3 * _PRO_DAY]:
        sent.pop(k, None)
    return out
'''

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        n = s.count(a)
        if n != (2 if a.startswith("    mkt, fng = _sg_mkt(pdb, fdb)") else 1):
            print(f"❌ replacement {i}: found {n} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for anchor, add in (("\ndef _cal_row(db, now, closes):", FETCH), ("\ndef _pro_grade(ks, sigs, closes, H):", SIGS), ("\ndef an_scan(cdb, pdb, fdb, coins):", NOW)):
        if s.count(anchor) != 1:
            print(f"❌ anchor {anchor!r}"); sys.exit(1)
        s = s.replace(anchor, add.rstrip("\n") + "\n\n" + anchor, 1)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 6 fetchers · 7 new members · 📈 new lines · 🗓️ the calendar notice · compiles · {p}")
