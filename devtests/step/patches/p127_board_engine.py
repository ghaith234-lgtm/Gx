# 📋 patch 127 (dashboard v3.36.73 · the indicator tables — the engine). The owner (21-11): «افضل اتسوي المؤشرات والتوليفات جدول للسوق بشكل
#   عام وللعملة بشكل خاص جدول كلهم يشتغلون ويتنبؤون ويمهم رقمين كم نجح والاخر فشل والنسبة تزداد وتنقص حسب هذه الرقمين وانخلي ثلاث خانات
#   للمؤشرات (الآن ، ٤ ساعات ، يوم) وكذلك تشغيل واطفاء … افضل تبدي من الصفر».
#   · hourly candles join the scan («⏱ الآن» = the next hour): SG_BAR «1H» (c1 · 720 candles ≈ 30 days) · the scan runs every hour (the
#     analyst's groups still see only 4H and 1D) · _fc_cache steps a 1H gap right
#   · every row (a fixed number 1–70 · combos from 101) predicts when it fires on a closed candle: its side for the NEXT candle of the same
#     frame · graded at that candle's close from the saved candles (✅ moved its way · ❌ the other way) · a table per coin + «🌐 السوق»
#     (Bitcoin's rows + the whole market's readings, graded on Bitcoin) + «*» every coin together (for the inner filter, later) ·
#     counted from zero in Holy_Board.json · ⏸ a row per table (keeps counting silently)
#   · three new market readings with their plain entries (rule 16): 🚀 W-surge (a third of the coins jumped together) · 📊 W-breadth
#     (60% of the coins above / 40% below their 50-candle mean) · 🧭 W-comp (the compass turned up / down) · 🌊 the crash on the hour too
#   · display only: no keys, no orders · the worker stays without network
#   python3 devtests/step/patches/p127_board_engine.py Holy_Dashboard.pyw
import os, sys

H = os.path.dirname(os.path.abspath(__file__))

R = [
    ('APP_VERSION = "3.36.72"', 'APP_VERSION = "3.36.73"'),
    ("""SG_SEC = {"4H": 14400, "1D": 86400}""",
     """SG_SEC = {"1H": 3600, "4H": 14400, "1D": 86400}"""),
    ("""SG_BAR = {"4H": ("c4", "4H", "4h"), "1D": ("c", "1Dutc", "1d")}""",
     """SG_BAR = {"1H": ("c1", "1H", "1h"), "4H": ("c4", "4H", "4h"), "1D": ("c", "1Dutc", "1d")}     # 📋 v3.36.73: الساعة للجداول"""),
    ("""SG_LK = {"4H": 3, "1D": 2}""",
     """SG_LK = {"1H": 3, "4H": 3, "1D": 2}"""),
    ("""SG_HZ = {"4H": 6, "1D": 30}""",
     """SG_HZ = {"1H": 1, "4H": 6, "1D": 30}"""),
    ("""SG_FN = {"4H": "4 ساعات", "1D": "يومي"}""",
     """SG_FN = {"1H": "ساعة", "4H": "4 ساعات", "1D": "يومي"}"""),
    ("""SG_N = {"4H": 4400, "1D": 2600}""",
     """SG_N = {"1H": 720, "4H": 4400, "1D": 2600}"""),
    ("""SG_MIN = {"4H": 700, "1D": 300}""",
     """SG_MIN = {"1H": 320, "4H": 700, "1D": 300}"""),
    ("""SG_NST_AGE = {"4H": 3 * 86400, "1D": 14 * 86400}""",
     """SG_NST_AGE = {"1H": 86400, "4H": 3 * 86400, "1D": 14 * 86400}"""),
    ("""    step = FC_TFS["4H"] if sec == "c4" else 86400""",
     """    step = {"c1": 3600, "c4": FC_TFS["4H"]}.get(sec, 86400)               # 📋 v3.36.73: شموع الساعة للجداول"""),
    ("""def _sg_events(rows, daily, ctx, t0=210):""",
     """def _sg_events(rows, daily, ctx, t0=210, dx=None):"""),
    ("""    _sg_extra(D, rows, daily, ctx, t0, ev)
    return D, ev""",
     """    _sg_extra(D, rows, daily, ctx, t0, ev, dx)
    return D, ev"""),
    ("""def _sg_extra(D, rows, daily, ctx, t0, ev):""",
     """def _sg_extra(D, rows, daily, ctx, t0, ev, dx=None):"""),
    ("""    dx = 86400 if daily else 14400
    try:
""",
     """    dx = dx or (86400 if daily else 14400)
    try:
        if dx < 14400:
            raise ValueError("📋 قراءات التوقعات لا تُقرأ على شموع الساعة")
"""),
    ("""frs = [f for f in (job.get("frs") or []) if f in SG_FR]""",
     """frs = [f for f in (job.get("frs") or []) if f in SB_FR]"""),
    ("""    out, F4 = {}, {}""",
     """    out, F4, FF = {}, {}, {}"""),
    ("""            D, E = _sg_events(rows, fr == "1D", ctx, t0=len(rows) - SG_LK[fr] - 3)
            out.setdefault(sym, {})[fr] = (D, E)
""",
     """            D, E = _sg_events(rows, fr == "1D", ctx, t0=len(rows) - SG_LK[fr] - 3, dx=SG_SEC[fr])
            out.setdefault(sym, {})[fr] = (D, E)
            FF.setdefault(fr, {})[sym] = (D, E)
"""),
    ("""        crash = {"t": tl, "n": len(z), "k": sum(1 for x in z if x <= -2.5), "on": tl in CR}
""",
     """        crash = {"t": tl, "n": len(z), "k": sum(1 for x in z if x <= -2.5), "on": tl in CR}
        _safe(_sb_surge, F4, Z, min(D["n"] for D, E in F4.values()) - 8, default=None)     # 📋 v3.36.73: 🚀 الصعود المفاجئ للسوق كله
    _safe(_sb_wide, FF, default=None)                         # 📋 v3.36.73: قراءات السوق كله للجداول (الساعة · عدد العملات الصاعدة · البوصلة)
"""),
    (""""hi": max(D["H"][i - lk + 1:i + 1]), "ch": D["C"][i] / D["C"][i - 1] - 1.0 if D["C"][i - 1] else 0.0}
    return {"ok": True, "c": res, "crash": crash, "ts": time.time()}""",
     """"hi": max(D["H"][i - lk + 1:i + 1]), "ch": D["C"][i] / D["C"][i - 1] - 1.0 if D["C"][i - 1] else 0.0}
            res[sym][fr]["e1"] = sorted(f"{c}:{s}" for (c, s), lst in E.items() if i in lst[-4:])      # 📋 ما انطلق على هذه الشمعة بالذات
    return {"ok": True, "c": res, "crash": crash, "ts": time.time()}"""),
    ("""    for sec in ("c", "c4"):
        for s in list((cdb.get(sec) or {}).keys()):""",
     """    for sec in ("c", "c4", "c1"):
        for s in list((cdb.get(sec) or {}).keys()):"""),
    ("""for s, e in (cdb.get(sec) or {}).items()} for sec in ("c", "c4")}""",
     """for s, e in (cdb.get(sec) or {}).items()} for sec in ("c", "c4", "c1")}"""),
    ("""T = {fr: int(now // SG_SEC[fr]) * SG_SEC[fr] - SG_SEC[fr] for fr in SG_FR}""",
     """T = {fr: int(now // SG_SEC[fr]) * SG_SEC[fr] - SG_SEC[fr] for fr in SB_FR}       # 📋 v3.36.73: والساعة للجداول"""),
    ("""        due = [fr for fr in SG_FR if st.get("t_" + fr) != T[fr] and now - (T[fr] + SG_SEC[fr]) >= 90]""",
     """        due = [fr for fr in SB_FR if now - (T[fr] + SG_SEC[fr]) >= 90 and (st.get("b_" + fr) != T[fr]                 # 📋 الجداول: كل شمعة مرة
               or (cat and fr in SG_FR and st.get("t_" + fr) != T[fr]))]                             # 🧠 المحلل: حين يجهز دليله"""),
    ("""missing = [s for s in uni if (s not in ci["c4"] or s not in ci["c"])""",
     """missing = [s for s in uni if (s not in ci["c4"] or s not in ci["c"] or s not in ci.get("c1", {}))"""),
    ("""            st["bad"] = sorted(set(bd_))
            if bd_:""",
     """            st["bad"] = sorted(set(bd_) if (missing or build_now) else set(st.get("bad") or []) | set(bd_))   # 📋 جلب جزئي لا يمحو ما فشل
            if bd_:"""),
    ("""bd_ = _sg_refresh(uni, list(SG_FR), cdb, pg)""",
     """bd_ = _sg_refresh(uni, list(SB_FR) if (missing or build_now) else [f for f in SB_FR if f in due], cdb, pg)"""),
    ("""        if cat and due:
            have = [s for s in uni if ci["c4"].get(s, 0) >= 300 and ci["c"].get(s, 0) >= 220]""",
     """        if due:                                               # 📋 v3.36.73: الفحص للجداول دائماً · المحلل حين يكون دليله جاهزاً
            have = [s for s in uni if ci["c4"].get(s, 0) >= 300 and ci["c"].get(s, 0) >= 220]"""),
    ("""                for fr in due:
                    st["t_" + fr] = T[fr]
                st["scan_ts"] = now
                st["crash"] = sc.get("crash")
                res = _sg_grade(st, cdb or {}, cat, now)
                cf = cfg if cfg["on"] else dict(cfg, types={k: False for k in SG_TY})
                blocks = _sg_process(sc, due, st, cf, cat, cdb, now)
                comp = st.get("comp")
                if st.pop("comp_new", None) and comp and cf["types"].get("mkt", True):
                    blocks.insert(0, _sg_comp_block(comp))
                if res and cf["types"].get("res", True):
                    rb = _sg_res_block(res, st, cat)
                    if rb:
                        blocks.append(rb)
""",
     """                for fr in due:
                    st["b_" + fr] = T[fr]                     # 📋 الجداول رأت هذه الشمعة
                    if cat and fr in SG_FR:
                        st["t_" + fr] = T[fr]                 # 🧠 والمحلل (لا تُعلَّم قبل جاهزية دليله — يراها حين يجهز)
                st["scan_ts"] = now
                if "4H" in due:
                    st["crash"] = sc.get("crash")
                _safe(sb_feed, sc, due, cdb or {}, now, default=None)          # 📋 v3.36.73: الجداول — كل صف يتنبأ ويُحكم من الصفر
                cf = cfg if cfg["on"] else dict(cfg, types={k: False for k in SG_TY})
                if cat and any(f in SG_FR for f in due):
                    res = _sg_grade(st, cdb or {}, cat, now)
                    blocks = _sg_process(sc, [f for f in due if f in SG_FR], st, cf, cat, cdb, now)
                    if res and cf["types"].get("res", True):
                        rb = _sg_res_block(res, st, cat)
                        if rb:
                            blocks.append(rb)
                comp = st.get("comp")
                if st.pop("comp_new", None) and comp and cf["types"].get("mkt", True):
                    blocks.insert(0, _sg_comp_block(comp))
"""),
    ("""    "M-fng": ("market", "😨 خوف في السوق", "🤑 طمع في السوق",""",
     """    "W-surge": ("market", "🚀 صعود السوق كله المفاجئ", "🚀 صعود السوق كله المفاجئ",
                "ثلث العملات أو أكثر صعدت بقوة غير معتادة في الشمعة نفسها", "ثلث العملات أو أكثر صعدت بقوة غير معتادة في الشمعة نفسها", ""),
    "W-breadth": ("market", "📊 أغلب العملات صاعدة", "📊 أغلب العملات هابطة",
                  "60% من العملات أو أكثر أصبحت فوق متوسط آخر 50 شمعة", "60% من العملات أو أكثر أصبحت تحت متوسط آخر 50 شمعة", "Market breadth"),
    "W-comp": ("market", "🧭 بوصلة السوق أصبحت صاعدة", "🧭 بوصلة السوق أصبحت نازلة",
               "البيتكوين فوق متوسط 200 يوم و60% من العملات فوق متوسط 50 يوماً — ثبت ذلك 3 أيام",
               "البيتكوين تحت متوسط 200 يوم و60% من العملات تحت متوسط 50 يوماً — ثبت ذلك 3 أيام", ""),
    "M-fng": ("market", "😨 خوف في السوق", "🤑 طمع في السوق","""),
    ('''def sg_loop():
    """''',
     '''# ───────────── 📋 v3.36.73: جداول المؤشرات — كل مؤشر وتوليفة يتنبأ وحده ويُحكم بعد مدته (العدّ من الصفر) ─────────────
#   المالك (21-11): «جدول للسوق بشكل عام وللعملة بشكل خاص … كلهم يشتغلون ويتنبؤون ويمهم رقمين كم نجح والاخر فشل … ثلاث خانات (الآن ·
#   4 ساعات · يوم) · تشغيل واطفاء … الجيد يصعد فوق والسيء ينزل جوة · افضل تبدي من الصفر»
#   · الصف = رقم ثابت + مؤشر (أو توليفة من 101) · ينطلق المؤشر على شمعة مغلقة ⇒ تنبؤ بجهته للشمعة القادمة من الإطار نفسه
#     (⏱ الآن = الساعة القادمة · 🕓 الساعات الأربع القادمة · 📅 اليوم القادم) ⇒ يُحكم بإغلاقها: ✅ إذا تحرك السعر بجهته · ❌ عكسها
#   · جدول لكل عملة بأسعارها · و«🌐 السوق» = إشارات البيتكوين + قراءات السوق كله (الانهيار · الصعود المفاجئ · عدد العملات الصاعدة ·
#     البوصلة) محكومة بسعر البيتكوين · و«*» سجل كل العملات معاً لكل صف (للفلتر الداخلي في الإشعارات)
#   · عرض فقط: لا أوامر ولا مفاتيح · الحساب في عامل الفحص المنفصل (بلا شبكة) والحكم من الشموع المحفوظة
SB_FR = ("1H", "4H", "1D")
SB_FRN = {"1H": ("⏱", "الآن", "الساعة القادمة"), "4H": ("🕓", "4 ساعات", "الساعات الأربع القادمة"), "1D": ("📅", "يوم", "اليوم القادم")}
SB_FILE = os.path.join(ROOT, "Holy_Board.json")
SB_MKT = "MKT"                                # جدول السوق كله
SB_ALL = "*"                                  # سجل كل العملات معاً لكل صف
SB_MINN = 10                                  # أقل عدد نتائج قبل الخروج من «قيد الاختبار» (الترتيب بأقل نسبة نثق بها — ويلسون)
SB_ONE = {"W-crash": -1, "W-surge": 1}        # أحداث تُقرأ بجهة واحدة في الجداول
SB_ROWS = (   # 📋 الرقم ثابت للأبد · مؤشر جديد = رقم جديد بآخر القائمة + اسمه هنا + مدخله في _SG_NM/_SG_XNM (القاعدة 16)
    (1, "O-trend", "الاتجاه العام (متوسط 50 مقابل 200)"),
    (2, "O-st", "لون خط الاتجاه"),
    (3, "O-adx", "وجود اتجاه حقيقي وقوته"),
    (4, "O-verdict", "معدل المؤشرات العشرة"),
    (5, "09", "عبور المتوسط السريع للأبطأ"),
    (6, "12", "انقلاب خط الاتجاه مع متوسط 150"),
    (7, "13", "ترتيب المتوسطات القصيرة والطويلة"),
    (8, "25", "اتجاه تؤكده ثلاثة مقاييس"),
    (9, "26", "الارتداد أو الرفض عند المتوسط"),
    (10, "27", "انقلاب الوقف المتحرك"),
    (11, "28", "التصحيح القصير داخل الاتجاه"),
    (12, "33", "التقاطع حول المتوسط الأطول"),
    (13, "34", "التقاطع المؤكد بشمعة كاملة"),
    (14, "36", "انقلاب الدفع قرب المتوسط الطويل"),
    (15, "37", "العودة إلى منطقة المتوسطات في اتجاه قوي"),
    (16, "42", "اختراق أو كسر منطقة خط الاتجاه"),
    (17, "F-nw", "اتجاه خط السعر الناعم"),
    (18, "F-vote", "ميل قراءات التوقعات"),
    (19, "O-macd", "تزايد قوة الدفع"),
    (20, "O-rsi", "الغالب بين قوة الشراء والبيع"),
    (21, "08", "اتجاه مقياسي سرعة الحركة"),
    (22, "10", "عبور منتصف النطاق بقوة"),
    (23, "11", "تجاوز قوة الشراء أو البيع للمنتصف مع الاتجاه"),
    (24, "21", "انقلاب مقياس التشبع"),
    (25, "22", "الاندفاع السريع"),
    (26, "23", "اتفاق الدفع والمتوسطات"),
    (27, "24", "الانقلاب من التشبع حول متوسط 50"),
    (28, "30", "موقع السعر من مداه"),
    (29, "35", "انقلاب الدفع حول متوسط 20"),
    (30, "40", "اتفاق المتوسطات والقوة والدفع"),
    (31, "41", "الانقلاب من التشبع مع الاتجاه الطويل"),
    (32, "X-rs", "القوة مقابل البيتكوين"),
    (33, "O-bottom", "مؤشر القاع"),
    (34, "14", "الارتداد من طرف النطاق بعد مبالغة"),
    (35, "15", "اختراق أو كسر نطاق الحركة"),
    (36, "18", "العودة القوية من خارج النطاق"),
    (37, "19", "عبور منتصف النطاق بتأكيد الدفع"),
    (38, "O-vp", "السعر ومنطقة أكثر التداول"),
    (39, "O-avwap", "ربح المشترين منذ آخر قاع وقمة"),
    (40, "O-pa", "القمم والقيعان"),
    (41, "16", "انتهاء التصحيح داخل الاتجاه"),
    (42, "17", "اختراق أول مقاومة أو كسر أول دعم"),
    (43, "20", "الشمعة الابتلاعية"),
    (44, "29", "التقاطع حول المستوى المحوري"),
    (45, "31", "قاع أو قمة جديدة حول المستوى المحوري"),
    (46, "38", "كسر خط الصعود أو الهبوط"),
    (47, "39", "شمعة الانعكاس عند التشبع"),
    (48, "43", "الابتعاد الحاد عن قاعدة سعرية"),
    (49, "F-lc", "حالات الماضي المشابهة"),
    (50, "O-of", "صفقات الشراء مقابل البيع"),
    (51, "O-cmf", "دخول الأموال وخروجها"),
    (52, "O-botv", "القاع المؤكد بالحجم"),
    (53, "32", "الحركة القوية بحجم كبير"),
    (54, "X-ad", "التجميع والتصريف"),
    (55, "X-adt", "حركة السعر مع السيولة"),
    (56, "P-ls", "ازدحام جهة واحدة في العقود"),
    (57, "P-tk", "الشراء والبيع العدواني في العقود"),
    (58, "P-pc", "ميل عقود الخيارات"),
    (59, "P-mv", "ربح الحائزين"),
    (60, "W-crash", "انهيار السوق كله"),
    (61, "M-fng", "الخوف والطمع"),
    (62, "M-vix", "قلق أسواق الأسهم"),
    (63, "M-dxy", "قوة الدولار"),
    (64, "M-us10", "فائدة السندات الأمريكية"),
    (65, "M-epu", "عدم اليقين الاقتصادي"),
    (66, "M-gpr", "التوترات العالمية"),
    (67, "M-tone", "نبرة الأخبار"),
    (68, "W-surge", "صعود السوق كله المفاجئ"),
    (69, "W-breadth", "عدد العملات الصاعدة"),
    (70, "W-comp", "بوصلة السوق"),
)
SB_NUM = {c: n for n, c, _nm in SB_ROWS}
SB_NM = {c: nm for _n, c, nm in SB_ROWS}
SB_COMBOS = ()                                # 🤝 التوليفات القوية (101 فما فوق) — تُضاف بعد فحصها على الأسعار الحقيقية
_SB = {"lock": threading.Lock()}


def _sb_load():
    B = _safe(load_json, SB_FILE, default=None)
    if not isinstance(B, dict) or B.get("v") != 1:
        B = {"v": 1, "since": round(time.time()), "rec": {}, "pend": [], "last": {}, "off": {}}
    for k, d in (("rec", {}), ("pend", []), ("last", {}), ("off", {})):
        if not isinstance(B.get(k), type(d)):
            B[k] = d
    return B


def _sb_surge(F, Z, k0):
    """🚀 الصعود المفاجئ للسوق كله: ≥ ثلث العملات (10 فأكثر) صعدت ≥ 2.5× حركتها المعتادة في الشمعة نفسها (مرآة 🌊 الانهيار)"""
    UP = {t for t, z in Z.items() if len(z) >= 10 and sum(1 for x in z if x >= 2.5) / len(z) >= 0.3}
    for sym, (D, E) in F.items():
        idx = [i for i in range(max(210, k0), D["n"]) if D["T"][i] in UP]
        if idx:
            E[("W-surge", 1)] = idx


def _sb_wide(FF):
    """📋 قراءات السوق كله لكل إطار ⇒ تُضاف لكل عملة على آخر الشموع: 🌊 الانهيار و🚀 الصعود المفاجئ على الساعة (الأربع ساعات في
    الفحص نفسه) · 📊 عدد العملات فوق متوسط آخر 50 شمعة (60% ⇒ صعود · 40% ⇒ هبوط · لا ترجع إلا بعد أن تعبر المنتصف) · 🧭 البوصلة
    على اليومي (انقلبت إلى صاعد أو نازل)"""
    F1 = FF.get("1H") or {}
    if len(F1) >= 10:
        k0 = min(D["n"] for D, E in F1.values()) - 8
        CR, Z = _sg_crash(F1, k0=k0)
        _sb_surge(F1, Z, k0)
    for fr, F in FF.items():
        AB = {}
        for sym, (D, E) in F.items():
            C, n = D["C"], D["n"]
            if n < 100:
                continue
            for i in range(n - 40, n):
                AB.setdefault(D["T"][i], []).append(C[i] > sum(C[i - 49:i + 1]) / 50.0)
        cur, ev = 0, {}
        for t in sorted(AB):
            a = AB[t]
            if len(a) < 10:
                continue
            sh = sum(a) / len(a)
            nxt = 1 if sh >= 0.6 else -1 if sh <= 0.4 else (0 if (cur > 0 and sh < 0.5) or (cur < 0 and sh > 0.5) else cur)
            if nxt and nxt != cur:
                ev[t] = nxt
            cur = nxt
        for sym, (D, E) in F.items():
            for i in range(max(210, D["n"] - 4), D["n"]):
                s = ev.get(D["T"][i])
                if s:
                    E.setdefault(("W-breadth", s), []).append(i)
    Fd = FF.get("1D") or {}
    if "BTC-USDT" in Fd and len(Fd) >= 10:
        seq = _sg_compass_states(Fd["BTC-USDT"][0], [D for D, E in Fd.values()])
        for k in range(max(1, len(seq) - 4), len(seq)):
            if seq[k][2] != seq[k - 1][2] and seq[k][2] in ("up", "down"):
                t, s = seq[k][0], 1 if seq[k][2] == "up" else -1
                for sym, (D, E) in Fd.items():
                    for i in range(max(210, D["n"] - 4), D["n"]):
                        if D["T"][i] == t:
                            E.setdefault(("W-comp", s), []).append(i)


def _sb_count(B, sc, num, fr, ok, t):
    """✅ ❌ لكل صف بكل إطار: [صدق · أخطأ · أيام مختلفة · آخر يوم]"""
    r = B["rec"].setdefault(sc, {}).setdefault(str(num), {}).setdefault(fr, [0, 0, 0, 0])
    r[0 if ok else 1] += 1
    d = int(t) // 86400
    if d != r[3]:
        r[2] += 1
        r[3] = d


def _sb_grade(B, cdb, now):
    """⚖️ كل تنبؤ يُحكم بإغلاق الشمعة التالية من إطاره (من الشموع المحفوظة): السعر تحرك بجهته ⇒ ✅ · عكسها ⇒ ❌ · لم يتحرك ⇒ لا يُحسب"""
    keep, T, n = [], {}, 0
    for it in B.get("pend") or []:
        try:
            sc, num, fr, side, t, px = str(it[0]), int(it[1]), str(it[2]), int(it[3]), int(it[4]), float(it[5])
        except Exception:
            continue
        if fr not in SB_FR or side not in (1, -1) or px <= 0:
            continue
        sym = "BTC-USDT" if sc == SB_MKT else sc
        sec = SG_BAR[fr][0]
        if (sym, sec) not in T:
            rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
            T[(sym, sec)] = {int(r[0]): float(r[4]) for r in rows[-400:]}
        c1 = T[(sym, sec)].get(t + SG_SEC[fr])
        if c1 is None:
            if now - t < 3 * SG_SEC[fr] + 2 * 86400:
                keep.append(it)
            continue
        if c1 == px:
            continue
        ok = 1 if (c1 - px) * side > 0 else 0
        _sb_count(B, sc, num, fr, ok, t)
        if sc != SB_MKT:
            _sb_count(B, SB_ALL, num, fr, ok, t)
        B["last"].setdefault(sc, {}).setdefault(str(num), {})[fr] = [side, t, ok, round(c1 / px - 1.0, 5)]
        n += 1
    B["pend"] = keep
    return n


def _sb_fired(x):
    """{رقم الصف: الجهة} لما انطلق على آخر شمعة (المؤشرات · ثم التوليفات: كل أعضائها متفقون ولا عضو معاكس، وبدأ اتفاقهم الآن)"""
    out = {}
    for k in x.get("e1") or []:
        try:
            code, s = k.rsplit(":", 1)
            s = int(s)
        except Exception:
            continue
        num = SB_NUM.get(code)
        if not num or (code in SB_ONE and s != SB_ONE[code]):
            continue
        out[num] = s if out.get(num, s) == s else 0          # الجهتان معاً على الشمعة نفسها ⇒ لا تنبؤ
    A1, A0 = set(x.get("a1") or []), set(x.get("a0") or [])
    for num, _nm, codes in SB_COMBOS:
        for s in (1, -1):
            on1 = all(f"{c}:{s}" in A1 for c in codes) and not any(f"{c}:{-s}" in A1 for c in codes)
            on0 = all(f"{c}:{s}" in A0 for c in codes) and not any(f"{c}:{-s}" in A0 for c in codes)
            if on1 and not on0:
                out[num] = s
    return {k: v for k, v in out.items() if v}


def sb_feed(sc, frs, cdb, now):
    """📋 بعد كل فحص: يُحكم ما حان وقته ثم تُسجَّل تنبؤات الشمعة الجديدة لكل جدول (العملة · و«🌐 السوق» من البيتكوين)"""
    with _SB["lock"]:
        B = _sb_load()
        g = _sb_grade(B, cdb, now)
        have = {(p[0], p[1], p[2], p[4]) for p in B["pend"] if isinstance(p, list) and len(p) >= 6}
        a = 0
        for sym, F in (sc.get("c") or {}).items():
            for fr in frs:
                x = F.get(fr)
                if fr not in SB_FR or not x or not x.get("px"):
                    continue
                for num, s in _sb_fired(x).items():
                    for scp in ([sym, SB_MKT] if sym == "BTC-USDT" else [sym]):
                        k = (scp, num, fr, int(x["t"]))
                        if k in have:
                            continue
                        have.add(k)
                        B["pend"].append([scp, num, fr, s, int(x["t"]), float(x["px"])])
                        a += 1
        del B["pend"][:-6000]
        B["ts"] = round(now)
        save_json_atomic(SB_FILE, B)
        return {"graded": g, "added": a}


def _sb_cell(r, p, l):
    r = r if isinstance(r, list) and len(r) >= 3 else [0, 0, 0, 0]
    w, ls = int(r[0]), int(r[1])
    n = w + ls
    return {"w": w, "l": ls, "nd": int(r[2]), "p": round(100.0 * w / n, 1) if n else None, "lb": round(_sg_wlb(w, n), 1),
            "now": p[0] if p else 0, "t": p[1] if p else 0, "last": l if isinstance(l, list) else None}


def sb_view(scope=None):
    """📋 جدول واحد: كل الصفوف (الرقم · الاسم · شغله · ⏱ 🕓 📅 بـ✅ ❌ والنسبة وأقل نسبة نثق بها · التنبؤ الجاري · آخر نتيجة) + العملات"""
    mine = sg_coins()
    scope = str(scope or SB_MKT)
    if scope != SB_MKT and scope not in mine and scope not in _sg_universe():
        scope = SB_MKT
    B = _sb_load()
    R, L, off = (B["rec"].get(scope) or {}), (B["last"].get(scope) or {}), set(int(x) for x in (B["off"].get(scope) or []) if str(x).isdigit())
    P = {}
    for p in B["pend"]:
        if isinstance(p, list) and len(p) >= 6 and p[0] == scope:
            P[(int(p[1]), p[2])] = (int(p[3]), int(p[4]))
    rows = []
    for num, code, nm in SB_ROWS:
        pl = _sg_plain(code) or ("market", nm, nm, "", "", "")
        rows.append({"n": num, "c": code, "nm": nm, "g": pl[0], "up": pl[1], "dn": pl[2], "mu": pl[3], "md": pl[4], "tech": pl[5], "off": num in off,
                     "f": {fr: _sb_cell((R.get(str(num)) or {}).get(fr), P.get((num, fr)), (L.get(str(num)) or {}).get(fr)) for fr in SB_FR}})
    for num, nm, codes in SB_COMBOS:
        rows.append({"n": num, "c": "+".join(codes), "nm": nm, "g": "combo", "k": [SB_NM[c] for c in codes if c in SB_NM],
                     "off": num in off, "f": {fr: _sb_cell((R.get(str(num)) or {}).get(fr), P.get((num, fr)), (L.get(str(num)) or {}).get(fr)) for fr in SB_FR}})
    return {"ok": True, "s": scope, "since": B.get("since"), "ts": B.get("ts"), "rows": rows, "frs": SB_FRN, "minn": SB_MINN,
            "coins": [[s, s.split("-")[0]] for s in mine], "grp": [list(g) for g in SG_GRP]}


def sb_off(v):
    """⏸ تشغيل وإطفاء صف في جدول (يبقى يتنبأ ويُحكم بصمت — لا يدخل الإشعارات وينزل لآخر الجدول)"""
    try:
        scope, num, on = str(v.get("s") or SB_MKT), int(v.get("n")), bool(v.get("on"))
    except Exception:
        return {"ok": False, "msg": "طلب غير صالح"}
    if num not in SB_NUM.values() and num not in [c[0] for c in SB_COMBOS]:
        return {"ok": False, "msg": "صف غير معروف"}
    with _SB["lock"]:
        B = _sb_load()
        cur = set(int(x) for x in (B["off"].get(scope) or []) if str(x).isdigit())
        (cur.discard if on else cur.add)(num)
        B["off"][scope] = sorted(cur)
        save_json_atomic(SB_FILE, B)
    return {"ok": True, "msg": f"✅ الصف {num} يعمل" if on else f"⏸ الصف {num} موقوف", "off": num in cur}


def sg_loop():
    """'''),
    ("""        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح""",
     """        if u.path == "/api/board":                        # 📋 v3.36.73: جدول المؤشرات (السوق أو عملة) — من الملف · لا ينتظر الحساب
            return self._json(_safe(sb_view, (q.get("s") or [""])[0], default={"ok": False, "rows": [], "msg": "تعذّر تحميل الجدول"}))
        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح"""),
    ("""            if act == "sg_est":""",
     """            if act == "sb_off":                           # 📋 v3.36.73: ⏸ صف في جدول المؤشرات
                return self._json(sb_off((data.get("value") if isinstance(data.get("value"), dict) else {})))
            if act == "sg_est":"""),
]


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 📋 the indicator tables (engine) · compiles · {p}")
