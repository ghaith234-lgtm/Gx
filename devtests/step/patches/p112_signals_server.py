# 🎯 the server half of patch 112 (dashboard v3.36.66 · the signals). Read by p112_signals.py — not run alone.
#   The owner (20-11): «اني اريد اتضيف كل الاشارات … الثناىية وفوق كذلك على حدى … بدون مستويات · الاشعارات حسب المؤشر اذا شراء او تجميع او
#   بيع او صعود او نزول حسب كل عملة وكذلك بشكل عام · انا احدد النسبة … انا ابحث على التركيبة النادرة … افحص وضيف وكذلك التوقعات لا تنسها».
#   · every signal the measurement (ci/sig_check6 … 10) used — the 36 systems (the SAME code: _SG_LIB is ci/sig_check6.py's block, a test keeps
#     them equal) · the old 📊 readings and their verdict · 🟢 the bottom · 🔮 the forecast's readings · 🧲 · 💪 · 🌊 · 😨 · 🗞️ (each macro
#     reading moved later by its publication delay — ci/sig_check10.py) · 🏦 — on the 4-hour and the daily candles, BUY and SELL
#   · every one alone AND their combinations (2 … 6 together, searched from the best like ci/sig_check9.py) are separate signals, each with its
#     own record: the part of time it was NOT chosen on (the last 40%) + the live record since (graded by itself after 3 days / 1 week)
#   · 💎 the rare ones apart · the 🧭 market compass (smoothed) · notifications by type with the owner's threshold — display and notifications
#     only: no order is placed or cancelled, no bot is touched, no key is read
#   · the heavy work (the history of ~34 coins · the search · each scan) runs in its own process at low priority (a thread in the Windows
#     program) with NO network — the dashboard fetches the public candles and hands them over in a file
PY = r'''

# ═══════════════ 🎯 v3.36.66: الإشارات — كل المؤشرات وتركيباتها بسجلها على الأسعار الحقيقية (عرض وإشعارات فقط · ولا أمر) ═══════════════
#   (المالك 20-11: «اريد اتضيف كل الاشارات … الثناىية وفوق كذلك على حدى … بدون مستويات … انا احدد النسبة … افحص وضيف وكذلك التوقعات»)
#   · الأنظمة الـ36 بنفس كود القياس حرفياً (_SG_LIB = كتلة ci/sig_check6.py · فحص يبقيهما متطابقين) + قراءات 📊 العشر وحكمها + 🟢 القاع +
#     قراءات 🔮 + 🧲 + 💪 + 🌊 + 😨 + 🗞️ (كل قراءة اقتصادية مؤخّرة بتأخر نشرها — ci/sig_check10.py) + 🏦 — على شموع 4 ساعات واليومية · شراء وبيع
#   · كل إشارة وحدها وكل تركيبة (2 … 6 معاً · بحث من الأفضل مثل ci/sig_check9.py) إشارة مستقلة بسجلها: آخر 40% من الوقت (لم تُختر عليه) +
#     السجل الحي بعدها (يُحكم وحده بعد 3 أيام / أسبوع) · 💎 النادرة · 🧭 بوصلة السوق (منعّمة) · إشعارات حسب النوع بعتبة المالك
#   · الحساب الثقيل (تاريخ ~34 عملة · البحث · كل فحص) بعملية منفصلة بأولوية منخفضة (خيط في برنامج ويندوز) وبلا شبكة — اللوحة تجلب
#     الشموع العامة وتسلّمها بملف · لا أمر ولا إلغاء ولا لمس لأي بوت ولا قراءة مفتاح
SG_DIR = os.path.join(ROOT, "_signals")
SG_CFILE = os.path.join(SG_DIR, "candles.json")
SG_CAT = os.path.join(SG_DIR, "catalog.json")
SG_FILE = os.path.join(ROOT, "Holy_Signals.json")
SG_FR = ("4H", "1D")
SG_SEC = {"4H": 14400, "1D": 86400}
SG_BAR = {"4H": ("c4", "4H", "4h"), "1D": ("c", "1Dutc", "1d")}
SG_LK = {"4H": 3, "1D": 2}                 # «معاً» = أُطلقت خلال هذا العدد من الشموع (مثل القياس)
SG_HZ = {"4H": 18, "1D": 7}                # الحكم بعد: 4 ساعات ← 3 أيام · اليومي ← أسبوع
SG_HZN = {"4H": "3 أيام", "1D": "أسبوع"}
SG_FN = {"4H": "4 ساعات", "1D": "يومي"}
SG_N = {"4H": 4400, "1D": 1100}            # تاريخ القياس (~سنتان · ~3 سنوات)
SG_MIN = {"4H": 700, "1D": 300}
SG_UNI = 34                                # عملات القياس: عملاتك + أكبر 28 عملة (حالات أكثر = سجل أوثق)
SG_EVERY = 300
SG_CAT_AGE = 7 * 86400                     # يُعاد البحث عن التركيبات كل أسبوع (على التاريخ الأحدث)
SG_FEE = 0.002
SG_BEAM, SG_TOPS, SG_KEEP, SG_RAREK = 40, 40, 25, 40
SG_MLAG = {"fng": 0, "vix": 1, "dxy": 1, "us10": 1, "epu": 2, "gpr": 8, "tone": 1}
#   🗞️ أيام تأخر النشر (ci/sig_lagdates.py يوم 20-11 13:23 UTC: VIX والدولار والسندات وعدم اليقين آخرها 19-11 · المخاطر الجيوسياسية 16-11 (تُحدَّث
#   أسبوعياً ⇒ حتى 8 أيام) · الخوف والطمع 20-11) — قيمة اليوم t لا تُستعمل قبل t + التأخير · ci/sig_check10.py: إشارات المخاطر الجيوسياسية للبيع
#   صمدت بتأخير 1–3 أيام وضعفت بعد أسبوع ⇒ سجلها هنا هو سجلها الصادق بتأخيرها الحقيقي
SG_TY = {"buy": ("🟢", "شراء"), "sell": ("🔴", "بيع"), "acc": ("🧲", "تجميع"), "dist": ("🔻", "تصريف"), "up": ("📈", "صعود"),
         "down": ("📉", "نزول"), "mkt": ("🧭", "السوق"), "crash": ("🌊", "الانهيار"), "fng": ("😨", "الخوف والطمع"),
         "eco": ("🗞️", "الاقتصاد"), "res": ("✅", "النتائج")}
SG_COIN_TY = ("buy", "sell", "acc", "dist", "up", "down")
SG_CH = {"both": "تيليغرام + التطبيق", "tg": "تيليغرام فقط", "app": "التطبيق فقط"}
_SG = {"m": None, "cat": None, "cat_mt": 0, "busy": False, "build": None, "scan": None, "phase": "", "pct": 0, "msg": "", "err": "",
       "lock": threading.Lock()}
_SG_FAM_TREND = ("trend", "momentum")
_SG_NM = {   # الأنظمة الـ36 — (للشراء · للبيع) بالعربية للإشعار والنافذة
    "08": ("CCI المزدوج وRSIOMA فوق الصفر", "CCI المزدوج وRSIOMA تحت الصفر"),
    "09": ("EMA 5 تقطع EMA 13 صعوداً", "EMA 5 تقطع EMA 13 هبوطاً"),
    "10": ("عبور منتصف بولنجر صعوداً (نبتون)", "عبور منتصف بولنجر هبوطاً (نبتون)"),
    "11": ("RSI يعبر 50 صعوداً مع الاتجاه", "RSI يعبر 50 هبوطاً مع الاتجاه"),
    "12": ("Supertrend انقلب أخضر فوق EMA 150", "Supertrend انقلب أحمر تحت EMA 150"),
    "13": ("شرائط Guppy صاعدة", "شرائط Guppy هابطة"),
    "14": ("ارتداد من أسفل بولنجر (RSI 30)", "ارتداد من أعلى بولنجر (RSI 70)"),
    "15": ("اختراق أعلى قناة Keltner", "كسر أسفل قناة Keltner"),
    "16": ("SAR صاعد مع تصحيح فيبوناتشي", "SAR هابط مع ارتداد فيبوناتشي"),
    "17": ("اختراق المقاومة R1 مع GMMA صاعد", "كسر الدعم S1 مع GMMA هابط"),
    "18": ("عودة من تحت حد بولنجر بقوة", "عودة من فوق حد بولنجر بقوة"),
    "19": ("عبور منتصف Keltner صعوداً (MACD · ستوكاستك)", "عبور منتصف Keltner هبوطاً (MACD · ستوكاستك)"),
    "20": ("شمعة ابتلاعية صاعدة", "شمعة ابتلاعية هابطة"),
    "21": ("الستوكاستك يرتد من القاع", "الستوكاستك ينقلب من القمة"),
    "22": ("اختراق سريع بزخم", "كسر سريع بزخم"),
    "23": ("CCI المزدوج مع المتوسطات صاعدة", "CCI المزدوج مع المتوسطات هابطة"),
    "24": ("Stoch RSI يرتد من القاع فوق EMA 50", "Stoch RSI ينقلب من القمة تحت EMA 50"),
    "25": ("SAR صاعد فوق EMA 100 مع MACD", "SAR هابط تحت EMA 100 مع MACD"),
    "26": ("ارتداد من EMA 50 (ستوكاستك)", "رفض عند EMA 50 (ستوكاستك)"),
    "27": ("SAR انقلب صاعداً مع CCI", "SAR انقلب هابطاً مع CCI"),
    "28": ("تصحيح إلى EMA 21 في اتجاه صاعد", "ارتداد إلى EMA 21 في اتجاه هابط"),
    "29": ("EMA 8 تقطع EMA 21 فوق المحور", "EMA 8 تقطع EMA 21 تحت المحور"),
    "30": ("Williams %R يعبر المنتصف صعوداً", "Williams %R يعبر المنتصف هبوطاً"),
    "31": ("قاع فركتل فوق المحور", "قمة فركتل تحت المحور"),
    "32": ("اندفاع صاعد بحجم كبير", "هبوط حاد بحجم كبير"),
    "33": ("تقاطع EMA 10/25 فوق EMA 50 مع SAR", "تقاطع EMA 10/25 تحت EMA 50 مع SAR"),
    "34": ("تقاطع EMA 9/21 بشمعة كاملة فوقه", "تقاطع EMA 9/21 بشمعة كاملة تحته"),
    "35": ("تقاطع MACD صاعد فوق EMA 20", "تقاطع MACD هابط تحت EMA 20"),
    "36": ("تقاطع MACD صاعد قرب SMA 100", "تقاطع MACD هابط قرب SMA 100"),
    "37": ("منطقة EMA 10/21 في اتجاه صاعد قوي", "منطقة EMA 10/21 في اتجاه هابط قوي"),
    "38": ("كسر خط الاتجاه الهابط", "كسر خط الاتجاه الصاعد"),
    "39": ("شمعة انعكاس صاعدة مع ستوكاستك منخفض", "شمعة انعكاس هابطة مع ستوكاستك مرتفع"),
    "40": ("توافق المتوسطات وRSI وMACD صعوداً", "توافق المتوسطات وRSI وMACD هبوطاً"),
    "41": ("ارتداد الستوكاستك مع GMMA صاعد", "انقلاب الستوكاستك مع GMMA هابط"),
    "42": ("اختراق منطقة Supertrend", "كسر منطقة Supertrend"),
    "43": ("كسر قاعدة سعرية (QFL)", "اختراق قمة سعرية (QFL معكوس)"),
}
_SG_XNM = {   # (الأسرة · للشراء · للبيع)
    "O-verdict": ("trend", "📊 حكم المؤشرات العشرة: صعود", "📊 حكم المؤشرات العشرة: هبوط"),
    "O-bottom": ("volatility", "🟢 مؤشر القاع", "🟢 مؤشر القاع"),
    "F-lc": ("pattern", "🧠 أقرب الحالات (Lorentzian) صاعدة", "🧠 أقرب الحالات (Lorentzian) هابطة"),
    "F-nw": ("trend", "〰️ الخط الناعم صاعد", "〰️ الخط الناعم هابط"),
    "F-vote": ("trend", "🔮 تصويت التوقعات: صعود", "🔮 تصويت التوقعات: هبوط"),
    "X-ad": ("volume", "🧲 السيولة تدخل والسعر لم يتحرك بعد (تجميع)", "🔻 السيولة تخرج والسعر لم ينزل بعد (تصريف)"),
    "X-adt": ("volume", "🧲 صعود مدعوم بدخول السيولة", "🧲 نزول مدعوم بخروج السيولة"),
    "X-rs": ("momentum", "💪 أقوى من البيتكوين", "💪 أضعف من البيتكوين"),
    "W-crash": ("market", "🌊 انهيار السوق كله", "🌊 انهيار السوق كله"),
    "M-fng": ("market", "😨 خوف في السوق", "🤑 طمع في السوق"),
    "M-vix": ("market", "😱 VIX هادئ", "😱 VIX مرتفع"),
    "M-dxy": ("market", "💱 الدولار يضعف", "💱 الدولار يقوى"),
    "M-us10": ("market", "📜 عوائد السندات الأمريكية تنزل", "📜 عوائد السندات الأمريكية تصعد"),
    "M-epu": ("market", "🏛️ عدم اليقين الاقتصادي منخفض", "🏛️ عدم اليقين الاقتصادي مرتفع"),
    "M-gpr": ("market", "🌍 المخاطر الجيوسياسية منخفضة", "🌍 المخاطر الجيوسياسية مرتفعة"),
    "M-tone": ("market", "📰 نبرة الأخبار إيجابية", "📰 نبرة الأخبار سلبية"),
    "P-ls": ("market", "⚖️ ازدحام البيع في العقود (قراءة عكسية)", "⚖️ ازدحام الشراء في العقود (قراءة عكسية)"),
    "P-tk": ("market", "🐂 الشراء العدواني في العقود", "🐻 البيع العدواني في العقود"),
    "P-pc": ("market", "🎲 الخيارات تميل للصعود", "🎲 الخيارات تميل للهبوط"),
    "P-mv": ("market", "🔗 MVRV منخفض", "🔗 MVRV مرتفع"),
}
_SG_OLDF = {"vp": "pattern", "avwap": "pattern", "pa": "pattern", "of": "volume", "cmf": "volume", "trend": "trend", "st": "trend", "adx": "trend",
            "macd": "momentum", "rsi": "momentum"}
_SG_FNG = lambda vs, j: (1.0 if vs[j] <= 20 else 0.4 if vs[j] <= 30 else -1.0 if vs[j] >= 80 else -0.4 if vs[j] >= 70 else 0.0)


def _sg_lib():
    """🎯 الأنظمة الـ36 والمؤشرات — كود القياس نفسه في مساحة أسماء خاصة (لا يختلط بأسماء اللوحة)"""
    m = _SG.get("m")
    if m is None:
        import types as _ty
        m = _ty.ModuleType("holy_signals")
        m.__dict__.update(math=math, FEE=SG_FEE)
        exec(compile(_SG_LIB, "holy_signals", "exec"), m.__dict__)
        _SG["m"] = m
    return m


def _sg_meta():
    """رمز ⇒ (الأسرة · اسم الشراء · اسم البيع) لكل إشارة"""
    M = _SG.get("meta")
    if M is None:
        L = _sg_lib()
        M = {c: (fam, _SG_NM.get(c, (nm, nm))[0], _SG_NM.get(c, (nm, nm))[1]) for c, (nm, fam, fn) in L.SYS.items()}
        for k, nm, ic, _w, _d in _IND2_K:
            M["O-" + k] = (_SG_OLDF.get(k, "trend"), f"{ic} {nm}: صاعد", f"{ic} {nm}: هابط")
        M.update(_SG_XNM)
        _SG["meta"] = M
    return M


def _sg_name(code, side):
    m = _sg_meta().get(code)
    return (m[1] if side > 0 else m[2]) if m else code


def _sg_type(keys, side):
    """نوع الإشارة: 🧲/🔻 فيها التجميع · 📈/📉 كلها اتجاه وزخم (بداية اتجاه) · 🟢/🔴 غير ذلك (ارتداد أو اختراق) · وحدها للسوق: 🌊 😨 🗞️"""
    M = _sg_meta()
    if len(keys) == 1:
        k = keys[0]
        if k == "W-crash":
            return "crash"
        if k == "M-fng":
            return "fng"
        if k.startswith("M-"):
            return "eco"
    if "X-ad" in keys:
        return "acc" if side > 0 else "dist"
    fams = [M.get(k, ("trend",))[0] for k in keys]
    if all(f in _SG_FAM_TREND for f in fams) and "trend" in fams:
        return "up" if side > 0 else "down"
    return "buy" if side > 0 else "sell"


def _sg_D(rows, daily):
    return {"T": [int(r[0]) for r in rows], "O": [float(r[1]) for r in rows], "H": [float(r[2]) for r in rows], "L": [float(r[3]) for r in rows],
            "C": [float(r[4]) for r in rows], "V": [float(r[5]) for r in rows], "n": len(rows), "blk": 5 if daily else 6}


def _sg_series(D, dx, code, ks, vs, sigf, t0, ev, thr=0.4, stale=4 * 86400):
    """سلسلة يومية منشورة قبل إغلاق الشمعة ⇒ شراء حين تصبح قراءتها ≥ thr · بيع ≤ −thr (نفس ci/sig_check7.py)"""
    prev = 0
    for t in range(max(210, t0 - 1), D["n"]):
        tcl = D["T"][t] + dx
        j = bisect.bisect_right(ks, tcl - 1) - 1
        cur = 0
        if j >= 0 and tcl - ks[j] <= stale:
            try:
                sv = sigf(vs, j)
            except Exception:
                sv = None
            cur = 1 if sv is not None and sv >= thr else -1 if sv is not None and sv <= -thr else 0
        if t >= t0 and cur and cur != prev:
            ev.setdefault((code, cur), []).append(t)
        prev = cur


def _sg_old(D, daily, t0, ev):
    """📊 قراءات اللوحة العشر وحكمها (و🟢 القاع على اليومي) ⇒ شراء حين تصبح ≥ +0.5 · بيع ≤ −0.5 (الحكم ±15 · القاع ≥ 50)"""
    O, H, L, C, V = D["O"], D["H"], D["L"], D["C"], D["V"]
    S2 = _i2_series(O, H, L, C, V)
    DD = {"o": O, "h": H, "l": L, "c": C, "v": V, "t": D["T"]}
    base = {k: w for k, _, _, w, _ in _IND2_K}
    prev = {}
    for t in range(max(210, t0 - 1), D["n"]):
        try:
            sg, _ = _i2_signals(DD, S2, t)
        except Exception:
            continue
        cur = {("O-" + k): (1 if v >= 0.5 else -1 if v <= -0.5 else 0) for k, (v, _) in sg.items()}
        sc = _i2_combine(sg, base) * 100
        cur["O-verdict"] = 1 if sc >= 15 else -1 if sc <= -15 else 0
        if daily:
            a = _bot_at(C, S2["rsi"], t)
            cur["O-bottom"] = 1 if a and a[0] >= 50 else 0
        if t >= t0:
            for k, v in cur.items():
                if v and v != prev.get(k, 0):
                    ev.setdefault((k, v), []).append(t)
        prev = cur


def _sg_extra(D, rows, daily, ctx, t0, ev):
    """🔮 قراءات التوقعات · 🧲 · 💪 · 😨 🗞️ · 🏦 — كل واحدة بدالة اللوحة نفسها (نفس ci/sig_check7.py)"""
    dx = 86400 if daily else 14400
    try:
        P = _fc_pack([list(r) for r in rows], [list(r) for r in ctx["drows"]], dx, 86400)
        X = {"H": 7 if daily else 6, "hn": "—", "fng": ctx.get("fng")}
        prev = {}
        for t in range(max(210, t0 - 1), D["n"]):
            sg, _ = _fc_read(P, t, "w" if daily else "d", X)
            up, dn, n_, vk, vt = _fc_vote(sg)
            cur = {"F-vote": 1 if vk in ("u", "su") else -1 if vk in ("d", "sd") else 0}
            for kk in ("lc", "nw"):
                v = sg.get(kk)
                cur["F-" + kk] = 0 if not v else (1 if v[0] >= 0.5 else -1 if v[0] <= -0.5 else 0)
            if t >= t0:
                for k, v in cur.items():
                    if v and v != prev.get(k, 0):
                        ev.setdefault((k, v), []).append(t)
            prev = cur
    except Exception:
        pass
    if daily:
        try:
            S = _xc_ad(D["T"], D["H"], D["L"], D["C"], D["V"])
            pa = pb = 0
            for t in range(max(210, t0 - 1), D["n"]):
                q = _xc_ad_at(t, S, D["C"])
                a = (1 if q[0] == "acc" else -1 if q[0] == "dist" else 0) if q else 0
                b = (1 if q[0] == "up" else -1 if q[0] == "down" else 0) if q else 0
                if t >= t0:
                    if a and a != pa:
                        ev.setdefault(("X-ad", a), []).append(t)
                    if b and b != pb:
                        ev.setdefault(("X-adt", b), []).append(t)
                pa, pb = a, b
        except Exception:
            pass
        B = ctx.get("btc") or {}
        if B and not ctx.get("sym", "").startswith("BTC-"):
            R = [(D["C"][i] / B[D["T"][i]]) if B.get(D["T"][i]) else None for i in range(D["n"])]
            E, e = [None] * D["n"], None
            for i, x in enumerate(R):
                if x is None:
                    e = None
                    continue
                e = x if e is None else e + (x - e) * (2.0 / 21.0)
                E[i] = e
            pr = 0
            for t in range(max(210, t0 - 1), D["n"]):
                q = _xc_rs_at(t, R, E)
                c = (1 if q[0] == "strong" else -1 if q[0] == "weak" else 0) if q else 0
                if t >= t0 and c and c != pr:
                    ev.setdefault(("X-rs", c), []).append(t)
                pr = c
    for k, (ks, vs) in (ctx.get("mkt") or {}).items():
        sf = _SG_FNG if k == "fng" else (lambda vs_, j, k=k: _mac_sig(k, vs_, j)[0])
        _sg_series(D, dx, "M-" + k, ks, vs, sf, t0, ev)
    for k, (ks, vs) in (ctx.get("pro") or {}).items():
        sf = {"ls": lambda vs_, j: _pro_ls_sig(vs_, j)[0], "tk": lambda vs_, j: _pro_tk_sig(vs_, j)[0],
              "pc": lambda vs_, j: _pro_pc_sig(vs_, j)[0], "mv": lambda vs_, j: _pro_mv_sig(vs_[j])}[k]
        _sg_series(D, dx, "P-" + k, ks, vs, sf, t0, ev)


def _sg_events(rows, daily, ctx, t0=210):
    """عملة واحدة · فريم واحد ⇒ (الشموع, {(الرمز, الجهة): [أرقام الشموع ≥ t0]}) — نفس كود القياس"""
    L = _sg_lib()
    D = _sg_D(rows, daily)
    ev = {}
    if D["n"] < 260:
        return D, ev
    S1, Dm = L.build(D), L.mirror(D)
    Sm = L.build(Dm)
    for code, (_nm, _fam, fn) in L.SYS.items():
        for side, DD, SS in ((1, D, S1), (-1, Dm, Sm)):
            try:
                lst = sorted(i for i in fn(DD, SS) if i >= max(210, t0))
            except Exception:
                lst = []
            if lst:
                ev[(code, side)] = lst
    try:
        _sg_old(D, daily, t0, ev)
    except Exception:
        pass
    _sg_extra(D, rows, daily, ctx, t0, ev)
    return D, ev


def _sg_mkt(pdb, fdb):
    """😨 + 🗞️ السلاسل اليومية العامة من ملفات اللوحة (بلا شبكة) — كل واحدة مؤخّرة بتأخر نشرها"""
    out = {}
    for k in ("vix", "dxy", "us10", "epu", "gpr", "tone"):
        ks, vs = _pro_sorted(pdb.get(k))
        if len(vs) > 30:
            out[k] = ([x + SG_MLAG.get(k, 0) * 86400 for x in ks], vs)
    f = _sg_fng_raw(fdb)
    if f:
        out["fng"] = ([x + SG_MLAG.get("fng", 0) * 86400 for x in f[0]], f[1])
    return out


def _sg_fng_raw(fdb):
    d = ((fdb or {}).get("fng") or {}).get("d") or {}
    ks = sorted(int(x) for x in d)
    return (ks, [d[str(x)] for x in ks]) if len(ks) > 30 else None


def _sg_ctx(sym, drows, pdb, mkt, fng, btc):
    ccy = sym.split("-")[0]
    pro = {}
    for k in ("ls", "tk", "pc", "mv"):
        e_ = (pdb.get(k) or {}).get(ccy)
        if isinstance(e_, dict) and e_.get("d"):
            ks, vs = _pro_sorted(e_)
            if len(vs) >= 30:
                pro[k] = (ks, vs)
    return {"sym": sym, "drows": drows, "fng": fng, "btc": btc, "mkt": mkt, "pro": pro}


def _sg_z(D):
    """🌊 تحرك كل شمعة 4 ساعات بمقياس تذبذب العملة (آخر 120 شمعة)"""
    C = D["C"]
    lr = [0.0] + [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, D["n"])]
    out = {}
    for k in range(130, D["n"]):
        w = lr[k - 120:k]
        mu = sum(w) / 120
        sd = math.sqrt(sum((x - mu) ** 2 for x in w) / 119) or 1e-9
        out[k] = lr[k] / sd
    return out


def _sg_crash(F4, k0=210):
    """🌊 شموع انهيار السوق كله: ≥ 30% من العملات (10 فأكثر) نزلت ≥ 2.5× حركتها المعتادة في الشمعة نفسها ⇒ تُضاف لكل عملة"""
    Z, ZI = {}, {}
    for sym, (D, E) in F4.items():
        zz = _sg_z(D)
        ZI[sym] = zz
        for k, z in zz.items():
            Z.setdefault(D["T"][k], []).append(z)
    CR = {t for t, z in Z.items() if len(z) >= 10 and sum(1 for x in z if x <= -2.5) / len(z) >= 0.3}
    for sym, (D, E) in F4.items():
        idx = [i for i in range(max(210, k0), D["n"]) if D["T"][i] in CR]
        if idx:
            E[("W-crash", 1)] = idx
            E[("W-crash", -1)] = list(idx)
    return CR, Z


def _sg_mean(v):
    return sum(v) / len(v) if v else 0.0


def _sg_hit(v):
    return sum(1 for x in v if x > 0) / len(v) * 100.0 if v else 0.0


def _sg_search(COIN, prog=None):
    """🔎 كل إشارة وحدها + التركيبات (2 … 6 معاً) — البحث على أول 60% من الوقت فقط · الحكم على آخر 40% (نفس ci/sig_check9.py)"""
    L = _sg_lib()
    names = list(COIN)
    PRE = {}
    for sym, (D4, E4, Dd, Ed, st) in COIN.items():
        for fr, D, E in (("4H", D4, E4), ("1D", Dd, Ed)):
            h, lk = SG_HZ[fr], SG_LK[fr]
            act = {k: set(j for i in lst for j in range(i, min(D["n"], i + lk))) for k, lst in E.items() if lst}
            rl = {i: L.fwd(D["C"], i, h, 1) for i in range(210, D["n"])}
            rs = {i: L.fwd(D["C"], i, h, -1) for i in range(210, D["n"])}
            cut = bisect.bisect_left(D["T"], st)
            PRE[(sym, fr)] = (act, rl, rs, cut, D["T"])

    def base(fr, side):
        l, t = [], []
        for sym in names:
            act, rl, rs, cut, T = PRE[(sym, fr)]
            for i, x in (rl if side > 0 else rs).items():
                if x is not None:
                    (l if i < cut else t).append(x)
        return l, t

    def evalc(fr, keys, side, want=False):
        l, t, ev = [], [], []
        for ci, sym in enumerate(names):
            act, rl, rs, cut, T = PRE[(sym, fr)]
            sets = [act.get(k) for k in keys]
            if any(s is None for s in sets):
                continue
            inter = set.intersection(*sorted(sets, key=len))
            r = rl if side > 0 else rs
            last = -10 ** 9
            for i in sorted(inter):
                if i - 1 in inter or i - last < SG_LK[fr]:
                    continue
                last = i
                x = r.get(i)
                if x is None:
                    continue
                if i < cut:
                    l.append(x)
                else:
                    t.append(x)
                    if want:
                        ev.append([ci, T[i]])
        return l, t, ev

    def score(v, b):
        return (_sg_mean(v) - _sg_mean(b)) * math.sqrt(len(v)) if v else -9.0

    def mk(fr, side, keys, l, t, ev, rare=False):
        ks = [k[0] for k in keys]
        return {"id": f"{fr}|{side}|{'+'.join(ks)}", "f": fr, "s": side, "k": ks, "ty": _sg_type(ks, side),
                "nl": len(l), "wl": sum(1 for x in l if x > 0), "ml": round(_sg_mean(l), 5),
                "nt": len(t), "wt": sum(1 for x in t if x > 0), "mt": round(_sg_mean(t), 5), "rare": bool(rare),
                "ev": ev if len(ev) <= 300 else None}

    out, BASE, WK, step = {}, {}, {}, 0
    for fr in SG_FR:
        wk = []
        for sym in names:
            act, rl, rs, cut, T = PRE[(sym, fr)]
            if cut < len(T):
                wk.append((T[-1] - T[cut]) / 604800.0)
        WK[fr] = round(_sg_mean(wk), 2) if wk else 0.0
        for side in (1, -1):
            step += 1
            if prog:
                prog(78 + 5 * step, f"البحث عن التركيبات: {SG_FN[fr]} · {'شراء' if side > 0 else 'بيع'}")
            bl, bt = base(fr, side)
            BASE[f"{fr}|{side}"] = {"hl": round(_sg_hit(bl), 1), "ml": round(_sg_mean(bl), 5), "ht": round(_sg_hit(bt), 1),
                                    "mt": round(_sg_mean(bt), 5), "nl": len(bl), "nt": len(bt)}
            singles = []
            keys = sorted(set(k for sym in names for k in PRE[(sym, fr)][0] if k[1] == side))
            for k in keys:
                l, t, ev = evalc(fr, [k], side, True)
                if len(l) + len(t) >= 3:
                    e = mk(fr, side, [k], l, t, ev)
                    out[e["id"]] = e
                if len(l) >= 6:
                    singles.append((score(l, bl), k))
            singles.sort(reverse=True)
            top1 = [k for s, k in singles[:SG_TOPS] if s > 0]
            seen, cur, allc = set(), [(k,) for k in top1], []
            for size in range(2, 7):
                cand = {}
                for c in cur:
                    for k in top1:
                        if k in c:
                            continue
                        nc = tuple(sorted(c + (k,)))
                        if nc in seen:
                            continue
                        seen.add(nc)
                        l, t, _ = evalc(fr, list(nc), side)
                        if len(l) >= 6 and _sg_mean(l) > _sg_mean(bl):
                            cand[nc] = (score(l, bl), l, t)
                best = sorted(cand.items(), key=lambda x: -x[1][0])[:SG_BEAM]
                if not best:
                    break
                cur = [c for c, _ in best]
                for c, (s, l, t) in best[:SG_KEEP]:
                    l, t, ev = evalc(fr, list(c), side, True)
                    e = mk(fr, side, c, l, t, ev)
                    out[e["id"]] = e
                allc += [(c, l, t) for c, (s, l, t) in cand.items()]
            rare = [(_sg_hit(l), len(l), c) for c, l, t in allc if 6 <= len(l) <= 30 and _sg_hit(l) >= 75]
            rare.sort(key=lambda x: (-x[0], -x[1]))
            for hh, nn, c in rare[:SG_RAREK]:
                l, t, ev = evalc(fr, list(c), side, True)
                e = mk(fr, side, c, l, t, ev, rare=True)
                if e["id"] in out:
                    out[e["id"]]["rare"] = True
                else:
                    out[e["id"]] = e
    return {"e": list(out.values()), "base": BASE, "wk": WK}


def _sg_compass_states(Dd_btc, dailies):
    """🧭 حالة السوق لكل يوم: البيتكوين فوق/تحت متوسط 200 يوم + نصيب العملات فوق متوسط 50 يوماً ⇒ صاعد · مختلط · نازل —
    منعّمة: لا تتغير إلا إذا ثبتت الحالة الجديدة 3 أيام متتالية (القياس: الحالة الخام تتقلب كل 2–3 أيام)"""
    L = _sg_lib()
    C = Dd_btc["C"]
    b200 = L.sma(C, 200)
    BT = {Dd_btc["T"][i]: (C[i] > b200[i]) for i in range(Dd_btc["n"]) if b200[i] is not None}
    AB = {}
    for D in dailies:
        s50 = L.sma(D["C"], 50)
        for i in range(D["n"]):
            if s50[i] is not None:
                AB.setdefault(D["T"][i], []).append(D["C"][i] > s50[i])
    seq, cur, cand, cnt, since = [], None, None, 0, None
    for t in sorted(BT):
        a = AB.get(t) or []
        if len(a) < 10:
            continue
        sh = sum(a) / len(a)
        raw = "up" if BT[t] and sh >= 0.6 else "down" if (not BT[t]) and sh <= 0.4 else "flat"
        if cur is None:
            cur, since = raw, t
        elif raw != cur:
            if raw == cand:
                cnt += 1
            else:
                cand, cnt = raw, 1
            if cnt >= 3:
                cur, since, cand, cnt = cand, t, None, 0
        else:
            cand, cnt = None, 0
        seq.append((t, raw, cur, since, round(sh, 3), bool(BT[t]), len(a), sum(a)))
    return seq


def _sg_compass_hist(COIN):
    """🧭 ماذا أعطى الشراء العشوائي لأي عملة بعد أسبوع وأسبوعين في كل حالة (منعّمة) + كم تدوم"""
    btc = COIN.get("BTC-USDT")
    if not btc:
        return {}
    L = _sg_lib()
    seq = _sg_compass_states(btc[2], [v[2] for v in COIN.values()])
    S = {t: s for t, raw, s, *_ in seq}
    res = {}
    for h in (7, 14):
        acc = {"up": [], "flat": [], "down": []}
        for sym, (D4, E4, Dd, Ed, st) in COIN.items():
            for i in range(210, Dd["n"]):
                s = S.get(Dd["T"][i])
                x = L.fwd(Dd["C"], i, h, 1) if s else None
                if x is not None:
                    acc[s].append(x)
        for s, v in acc.items():
            res.setdefault(s, {})[f"m{h}"] = round(_sg_mean(v), 5)
            res[s][f"h{h}"] = round(_sg_hit(v), 1)
            res[s]["n"] = sum(1 for x in seq if x[2] == s)
    runs, cur, n0 = [], None, 0
    for x in seq:
        if x[2] != cur:
            if cur:
                runs.append((cur, n0))
            cur, n0 = x[2], 0
        n0 += 1
    for s in res:
        r = sorted(n for k, n in runs if k == s)
        res[s]["run"] = r[len(r) // 2] if r else 0
    return res


def _sg_prog(jd, p, msg):
    _safe(save_json_atomic, os.path.join(jd, "prog.json"), {"pct": round(p), "msg": msg, "ts": time.time()}, default=None)


def sg_build(jd, job):
    """🏗️ (عملية منفصلة · بلا شبكة) دليل الإشارات: كل إشارة وتركيباتها على تاريخ عملات القياس ⇒ _signals/catalog.json"""
    t0 = time.time()
    coins = [c for c in (job.get("coins") or []) if isinstance(c, str)]
    cdb = _safe(load_json, SG_CFILE, default={}) or {}
    pdb, fdb = _pro_db(), _fc_db()
    mkt, fng = _sg_mkt(pdb, fdb), _sg_fng_raw(fdb)
    bd = ((cdb.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    btc = {int(r[0]): float(r[4]) for r in bd}
    COIN = {}
    for k, sym in enumerate(coins):
        _sg_prog(jd, 3 + 72.0 * k / max(1, len(coins)), f"{sym.split('-')[0]}: حساب كل الإشارات على تاريخها ({k + 1} من {len(coins)})")
        r4 = ((cdb.get("c4") or {}).get(sym) or {}).get("d") or []
        rd = ((cdb.get("c") or {}).get(sym) or {}).get("d") or []
        if len(r4) < SG_MIN["4H"] or len(rd) < SG_MIN["1D"]:
            continue
        ctx = _sg_ctx(sym, rd, pdb, mkt, fng, btc)
        D4, E4 = _sg_events(r4, False, ctx)
        Dd, Ed = _sg_events(rd, True, ctx)
        COIN[sym] = (D4, E4, Dd, Ed, D4["T"][int(D4["n"] * 0.6)])
        time.sleep(0.002)
    if len(COIN) < 3:
        return {"ok": False, "err": "تاريخ العملات غير كافٍ بعد"}
    _sg_prog(jd, 76, "🌊 انهيارات السوق كله على التاريخ")
    _sg_crash({s: (v[0], v[1]) for s, v in COIN.items()})
    cat = _sg_search(COIN, lambda p, m: _sg_prog(jd, p, m))
    _sg_prog(jd, 98, "🧭 بوصلة السوق على التاريخ")
    cat["compass"] = _sg_compass_hist(COIN)
    cat.update(v=1, ts=time.time(), coins=list(COIN), secs=round(time.time() - t0), lag=SG_MLAG,
               span={fr: [min(v[0 if fr == "4H" else 2]["T"][0] for v in COIN.values()), max(v[0 if fr == "4H" else 2]["T"][-1] for v in COIN.values())]
                     for fr in SG_FR})
    save_json_atomic(SG_CAT, cat)
    return {"ok": True, "n": len(cat["e"]), "coins": len(COIN), "secs": cat["secs"]}


def sg_scan_calc(jd, job):
    """🔍 (عملية منفصلة · بلا شبكة) آخر شمعة مغلقة لكل عملة وفريم: الإشارات الشغّالة الآن والشمعة السابقة + 🌊 + 🗞️ اليوم"""
    coins = [c for c in (job.get("coins") or []) if isinstance(c, str)]
    frs = [f for f in (job.get("frs") or []) if f in SG_FR]
    cdb = _safe(load_json, SG_CFILE, default={}) or {}
    pdb, fdb = _pro_db(), _fc_db()
    mkt, fng = _sg_mkt(pdb, fdb), _sg_fng_raw(fdb)
    bd = ((cdb.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    btc = {int(r[0]): float(r[4]) for r in bd}
    out, F4 = {}, {}
    for k, sym in enumerate(coins):
        _sg_prog(jd, 90.0 * k / max(1, len(coins)), f"{sym.split('-')[0]} ({k + 1} من {len(coins)})")
        rd = ((cdb.get("c") or {}).get(sym) or {}).get("d") or []
        ctx = _sg_ctx(sym, rd, pdb, mkt, fng, btc)
        for fr in frs:
            sec, bar, ib = SG_BAR[fr]
            rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
            if len(rows) < 300 or len(rd) < 220:
                continue
            D, E = _sg_events(rows, fr == "1D", ctx, t0=len(rows) - SG_LK[fr] - 3)
            out.setdefault(sym, {})[fr] = (D, E)
            if fr == "4H":
                F4[sym] = (D, E)
        time.sleep(0.002)
    crash = None
    if F4:
        CR, Z = _sg_crash(F4, k0=min(D["n"] for D, E in F4.values()) - 8)
        tl = max(D["T"][-1] for D, E in F4.values())
        z = Z.get(tl) or []
        crash = {"t": tl, "n": len(z), "k": sum(1 for x in z if x <= -2.5), "on": tl in CR}
    res = {}
    for sym, frs_ in out.items():
        for fr, (D, E) in frs_.items():
            i, lk = D["n"] - 1, SG_LK[fr]
            a1 = sorted(f"{c}:{s}" for (c, s), lst in E.items() if any(i - lk < j <= i for j in lst))
            a0 = sorted(f"{c}:{s}" for (c, s), lst in E.items() if any(i - 1 - lk < j <= i - 1 for j in lst))
            res.setdefault(sym, {})[fr] = {"t": D["T"][i], "px": D["C"][i], "a1": a1, "a0": a0, "lo": min(D["L"][i - lk + 1:i + 1]),
                                           "hi": max(D["H"][i - lk + 1:i + 1]), "ch": D["C"][i] / D["C"][i - 1] - 1.0 if D["C"][i - 1] else 0.0}
    return {"ok": True, "c": res, "crash": crash, "ts": time.time()}


def sg_child(jd, proc=False):
    """🧪 العامل: يكتب out.json · بعملية منفصلة (proc): بلا شبكة (كل دوال الجلب معطّلة فيها) وبأولوية منخفضة"""
    if proc:
        try:
            if hasattr(os, "nice"):
                os.nice(10)
        except Exception:
            pass
        for fn in ("_okx_pub", "_http_json", "_pro_text", "_pro_bytes", "_fc_okx_rows", "_fc_bin_rows", "tg_send", "app_feed_push"):
            globals()[fn] = (lambda *a, **k: None)
    job = _safe(load_json, os.path.join(jd, "job.json"), default={}) or {}
    try:
        out = sg_build(jd, job) if job.get("mode") == "build" else sg_scan_calc(jd, job)
        rc = 0
    except Exception as ex:
        out, rc = {"ok": False, "err": f"{type(ex).__name__}: {ex}"}, 1
    save_json_atomic(os.path.join(jd, "out.json"), out)
    return rc


def _sg_spawn(mode, job):
    """عملية منفصلة بأولوية منخفضة (مثل الاختبار التجريبي) · في برنامج ويندوز المجمّع: خيط"""
    os.makedirs(SG_DIR, exist_ok=True)
    jd = os.path.join(SG_DIR, "job_" + mode)
    shutil.rmtree(jd, ignore_errors=True)
    os.makedirs(jd, exist_ok=True)
    save_json_atomic(os.path.join(jd, "job.json"), dict(job, mode=mode, ts=time.time()))
    if getattr(sys, "frozen", False) or os.environ.get("HOLY_SIG_THREAD") == "1":
        th = threading.Thread(target=_safe, args=(sg_child, jd), daemon=True)
        th.start()
        return {"jd": jd, "th": th, "t0": time.time(), "mode": mode}
    flags = (0x08000000 | 0x00004000) if os.name == "nt" else 0
    lf = open(os.path.join(jd, "w.log"), "w", encoding="utf-8")
    p = subprocess.Popen([PYTHON_EXE, "-u", os.path.abspath(__file__), "--holy-sig", jd], cwd=jd, stdout=lf, stderr=lf, creationflags=flags,
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return {"jd": jd, "p": p, "lf": lf, "t0": time.time(), "mode": mode}


def _sg_job_done(job):
    if not job:
        return True
    if "p" in job:
        if job["p"].poll() is None:
            return False
        try:
            job["lf"].close()
        except Exception:
            pass
        return True
    return not job["th"].is_alive()


def _sg_job_out(job):
    return _safe(load_json, os.path.join(job["jd"], "out.json"), default=None)


def _sg_job_prog(job):
    return _safe(load_json, os.path.join(job["jd"], "prog.json"), default={}) or {}


def _sg_job_stop(job):
    try:
        if job and "p" in job and job["p"].poll() is None:
            job["p"].kill()
    except Exception:
        pass


# ───────────── ⚙️ الإعدادات · الحالة ─────────────
def sg_cfg():
    c = _safe(app_cfg, default={}) or {}

    def iv(k, d, lo, hi):
        try:
            return max(lo, min(hi, int(c.get(k) if c.get(k) is not None else d)))
        except Exception:
            return d
    ty = c.get("sg_types") if isinstance(c.get("sg_types"), dict) else {}
    fr = c.get("sg_fr") if isinstance(c.get("sg_fr"), dict) else {}
    coins = c.get("sg_coins")
    coins = [str(x).upper() for x in coins if isinstance(x, str)] if isinstance(coins, list) else None
    qh = c.get("sg_quiet")
    qh = [int(qh[0]) % 24, int(qh[1]) % 24] if isinstance(qh, list) and len(qh) == 2 and all(isinstance(x, (int, float)) for x in qh) else None
    sm = c.get("sg_sum")
    ch = str(c.get("sg_ch") or "both")
    return {"on": bool(c.get("sg_on", True)), "thr": iv("sg_thr", 65, 50, 95), "min": iv("sg_min", 15, 3, 200),
            "rnd": bool(c.get("sg_rnd", True)), "rare": bool(c.get("sg_rare", True)), "rmin": iv("sg_rmin", 6, 3, 50),
            "types": {k: bool(ty.get(k, True)) for k in SG_TY}, "coins": coins, "cap": iv("sg_cap", 8, 0, 100),
            "quiet": qh, "sum": (int(sm) % 24) if isinstance(sm, (int, float)) and not isinstance(sm, bool) else None,
            "ch": ch if ch in SG_CH else "both", "fr": {f: bool(fr.get(f, True)) for f in SG_FR}}


def sg_coins(cfg=None):
    """🪙 عملات الإشعارات: اختيارك · وإلا عملات الشريط (📊)"""
    cfg = cfg or sg_cfg()
    return list(cfg["coins"]) if cfg["coins"] is not None else list(ticker_cfg()["coins"])


def _sg_universe():
    tick = list(ticker_cfg()["coins"])
    mine = sg_coins()
    u = list(dict.fromkeys(["BTC-USDT"] + mine + tick + list(MKT_COINS)))
    return u[:max(SG_UNI, len(dict.fromkeys(["BTC-USDT"] + mine + tick)))]


def _sg_st():
    st = _safe(load_json, SG_FILE, default={}) or {}
    return st if isinstance(st, dict) else {}


def _sg_save(st):
    _safe(save_json_atomic, SG_FILE, st, default=None)


def _sg_cat():
    """📒 الدليل من الملف (يُعاد تحميله حين يتغير)"""
    try:
        mt = os.path.getmtime(SG_CAT)
    except Exception:
        return None
    if _SG["cat"] is None or _SG["cat_mt"] != mt:
        c = _safe(load_json, SG_CAT, default=None)
        if isinstance(c, dict) and isinstance(c.get("e"), list):
            c["idx"] = {e["id"]: e for e in c["e"]}
            _SG["cat"], _SG["cat_mt"] = c, mt
    return _SG["cat"]


def _sg_rec(e, st):
    """📊 سجل الإشارة: آخر 40% من التاريخ (لم تُختر عليه) + السجل الحي بعده — 💎 النادرة: كل التاريخ + الحي (وسطر الاختبار وحده)"""
    lv = (st.get("rec") or {}).get(e["id"]) or [0, 0, 0.0]
    n, w, sm = e["nt"] + lv[0], e["wt"] + lv[1], e["mt"] * e["nt"] + lv[2]
    if e.get("rare"):
        n, w, sm = n + e["nl"], w + e["wl"], sm + e["ml"] * e["nl"]
    return {"n": n, "w": w, "h": (w / n * 100.0) if n else 0.0, "m": (sm / n) if n else 0.0, "ln": lv[0], "lw": lv[1]}


def _sg_pass(e, st, cfg, cat):
    """هل تصل إشعاراتها؟ النسبة · العدد · أفضل من العشوائي · 💎 بحدها الخاص"""
    if not cfg["types"].get(e.get("ty") or "buy", True) or not cfg["fr"].get(e["f"], True):
        return False
    r = _sg_rec(e, st)
    b = (cat.get("base") or {}).get(f"{e['f']}|{e['s']}") or {}
    if e.get("rare"):
        if not cfg["rare"] or r["n"] < cfg["rmin"] or r["h"] < cfg["thr"]:
            return False
        return e["nt"] < 2 or (e["wt"] / e["nt"] * 100.0 > float(b.get("ht") or 0) and e["mt"] > float(b.get("mt") or 0))
    if r["n"] < cfg["min"] or r["h"] < cfg["thr"]:
        return False
    return (not cfg["rnd"]) or (r["h"] > float(b.get("ht") or 0) and r["m"] > float(b.get("mt") or 0))


def sg_estimate(cfg=None, st=None):
    """🗓️ كم إشعاراً بالأسبوع لو كانت هذه الإعدادات أيام الاختبار (على عملاتك · إشعار واحد لكل عملة ونوع وشمعة · بعد الحد اليومي)"""
    cat = _sg_cat()
    if not cat:
        return None
    cfg = cfg or sg_cfg()
    st = st if st is not None else _sg_st()
    coins = cat.get("coins") or []
    mine = set(sg_coins(cfg))
    sel = {i for i, s in enumerate(coins) if s in mine}
    share = len(sel) / len(coins) if coins else 0.0
    grp, big, mk, ne = set(), 0.0, set(), 0
    ina_on = bool((_safe(ina_cfg, default={}) or {}).get("on"))
    for e in cat["e"]:
        if e["ty"] in ("crash", "fng", "eco"):
            if cfg["types"].get(e["ty"], True) and not (e["ty"] == "crash" and ina_on) and (e["ty"] != "crash" or e["f"] == "4H"):
                for ci, t in (e.get("ev") or []):
                    mk.add((e["ty"], e["k"][0], e["s"], t // 86400))
            continue
        if not _sg_pass(e, st, cfg, cat):
            continue
        ne += 1
        wk = float((cat.get("wk") or {}).get(e["f"]) or 0) or 1.0
        if e.get("ev") is None:
            big += e["nt"] * share / wk
            continue
        for ci, t in e["ev"]:
            if ci in sel:
                grp.add((ci, e["ty"], e["f"], t))
    w4 = float((cat.get("wk") or {}).get("4H") or 0) or 1.0
    per = len([g for g in grp if g[2] == "4H"]) / w4 + len([g for g in grp if g[2] == "1D"]) / (float((cat.get("wk") or {}).get("1D") or 0) or 1.0)
    per += big + len(mk) / w4
    capw = cfg["cap"] * 7 if cfg["cap"] else None
    return {"wk": round(per, 1), "cut": round(min(per, capw), 1) if capw else round(per, 1), "capped": bool(capw and per > capw), "n": ne}


def sg_set(v):
    v = v or {}
    c = app_cfg()
    for k, key in (("on", "sg_on"), ("rnd", "sg_rnd"), ("rare", "sg_rare")):
        if v.get(k) is not None:
            c[key] = bool(v[k])
    for k, key, lo, hi in (("thr", "sg_thr", 50, 95), ("min", "sg_min", 3, 200), ("rmin", "sg_rmin", 3, 50), ("cap", "sg_cap", 0, 100)):
        if v.get(k) is not None:
            try:
                c[key] = max(lo, min(hi, int(v[k])))
            except Exception:
                pass
    if isinstance(v.get("types"), dict):
        t = dict(c.get("sg_types") or {})
        t.update({k: bool(x) for k, x in v["types"].items() if k in SG_TY})
        c["sg_types"] = t
    if isinstance(v.get("fr"), dict):
        f = dict(c.get("sg_fr") or {})
        f.update({k: bool(x) for k, x in v["fr"].items() if k in SG_FR})
        c["sg_fr"] = f
    if "coins" in v:
        if v["coins"] is None:
            c.pop("sg_coins", None)
        elif isinstance(v["coins"], list):
            out = []
            for x in v["coins"][:40]:
                s = str(x or "").strip().upper().replace("/", "-").replace(" ", "")
                if s and re.fullmatch(r"[A-Z0-9]{1,15}(-[A-Z0-9]{2,8})?", s):
                    s = s if "-" in s else s + "-USDT"
                    if s not in out:
                        out.append(s)
            c["sg_coins"] = out
    if "quiet" in v:
        q = v["quiet"]
        c["sg_quiet"] = [int(q[0]) % 24, int(q[1]) % 24] if isinstance(q, list) and len(q) == 2 else None
    if "sum" in v:
        c["sg_sum"] = (int(v["sum"]) % 24) if isinstance(v["sum"], (int, float)) and not isinstance(v["sum"], bool) else None
    if v.get("ch") in SG_CH:
        c["sg_ch"] = v["ch"]
    save_app_cfg(c)
    p = sg_cfg()
    return {"ok": True, "msg": ("🎯 إشعارات الإشارات مفعّلة — " + f"{p['thr']}% فأكثر · {_sg_ar(p['min'], 'time')} فأكثر · " + SG_CH[p["ch"]]) if p["on"]
            else "🔕 إشعارات الإشارات متوقفة", "cfg": p, "est": sg_estimate(p)}


# ───────────── 📨 النصوص ─────────────
_SG_AR = {"day": ("يوم واحد", "يومين", "أيام", "يوماً"), "time": ("مرة واحدة", "مرتين", "مرات", "مرة"), "coin": ("عملة واحدة", "عملتين", "عملات", "عملة"),
          "sig": ("إشارة واحدة", "إشارتان", "إشارات", "إشارة")}


def _sg_ar(n, kind):
    """العدد ومعدوده بالعربية: 1 · 2 · من 3 إلى 10 جمع · 11 فأكثر مفرد (منذ 55 يوماً · ظهرت 13 مرة · 9 مرات)"""
    w = _SG_AR[kind]
    n = int(n)
    return w[0] if n == 1 else w[1] if n == 2 else f"{n} {w[2]}" if 3 <= n % 100 <= 10 else f"{n} {w[3]}"


def _sg_pct(x):
    return f"{x * 100:+.1f}%"


def _sg_keys_txt(keys, side, mx=6):
    nm = [_sg_name(k, side) for k in keys]
    return " · ".join(nm[:mx]) + (f" · و{len(nm) - mx} غيرها" if len(nm) > mx else "")


def _sg_rec_line(e, r, cat, rare=False):
    b = (cat.get("base") or {}).get(f"{e['f']}|{e['s']}") or {}
    rnd = f"{'الشراء' if e['s'] > 0 else 'البيع'} العشوائي {float(b.get('ht') or 0):.0f}%"
    mv = f"المتوسط بعد {SG_HZN[e['f']]} {_sg_pct(r['m'] if e['s'] > 0 else -r['m'])}"
    if rare:
        return f"📊 ظهرت {_sg_ar(r['n'], 'time')} فقط، صدقت {r['w']} ({r['h']:.0f}%) · {rnd} · {mv}"
    return f"📊 السجل: صدقت {r['w']} من {_sg_ar(r['n'], 'time')} ({r['h']:.0f}%) · {rnd} · {mv}"


def _sg_block(sym, ty, fr, ents, st, cat, scan, comp):
    """📨 إشعار عملة واحدة لنوع واحد — يجمع كل ما اتفق (أقواها أولاً)"""
    ents = sorted(ents, key=lambda e: (-_sg_rec(e, st)["h"], -_sg_rec(e, st)["n"]))
    top = ents[0]
    side = top["s"]
    keys = list(dict.fromkeys(k for e in ents for k in e["k"]))
    r = _sg_rec(top, st)
    ico, nm = SG_TY[ty]
    rare = bool(top.get("rare"))
    x = scan or {}
    px = float(x.get("px") or 0)
    head = (f"💎 تركيبة نادرة — {nm} — {sym}" if rare else f"{ico} {nm} — {sym}") + f" · {SG_FN[fr]}"
    if ty == "acc":
        what = "السيولة تدخل والسعر لم يتحرك بعد"
    elif ty == "dist":
        what = "السيولة تخرج والسعر لم ينزل بعد"
    else:
        what = (f"اتفقت {_sg_ar(len(keys), 'sig')}: " if len(keys) > 1 else "") + _sg_keys_txt(keys, side)
    L = [head, what]
    if len(ents) > 1 and len(top["k"]) < len(keys):
        L.append("أقواها: " + " + ".join(_sg_name(k, side) for k in top["k"]))
    L.append(_sg_rec_line(top, r, cat, rare))
    b = (cat.get("base") or {}).get(f"{top['f']}|{top['s']}") or {}
    if r["h"] <= float(b.get("ht") or 0) or r["m"] <= float(b.get("mt") or 0):
        L.append("⚠️ تاريخياً ليست أفضل من العشوائي")
    if rare:
        L.append("⚠️ عدد المرات قليل — قد تكون صدفة")
    if px > 0:
        inv = ""
        if ty in ("buy", "up") and x.get("lo"):
            inv = f" · ❌ تبطل إذا أُغلقت {'شمعة اليوم' if fr == '1D' else 'شمعة 4 ساعات'} تحت {_px_s(x['lo'])}"
        elif ty in ("sell", "down") and x.get("hi"):
            inv = f" · ❌ تبطل إذا أُغلقت {'شمعة اليوم' if fr == '1D' else 'شمعة 4 ساعات'} فوق {_px_s(x['hi'])}"
        L.append(f"💵 السعر الآن {_px_s(px)}{inv}")
    if comp and comp.get("s"):
        L.append("🧭 السوق: " + {"up": "صاعد", "flat": "مختلط", "down": "نازل"}[comp["s"]])
    if ty in ("buy", "sell", "up", "down"):
        L.append("⚠️ ليست ضماناً — القرار لك")
    return {"sym": sym, "ty": ty, "f": fr, "t": L[0], "b": "\n".join(L[1:]), "ids": [e["id"] for e in ents], "h": round(r["h"], 1)}


def _sg_tg(text, cfg, go="sig"):
    if TG_MUTED["v"]:
        journal("notify", "🔕 لم يُرسَل إشعار إشارات (الكتم مفعّل): " + text[:300], "info")
        return False
    ok = True
    if cfg["ch"] in ("both", "tg"):
        ok = bool(tg_send(text, plain=True)) and ok
    if cfg["ch"] in ("both", "app"):
        _safe(app_feed_push, text, go, "ind", default=None)     # 📱 قناة «📊 تنبيهات المؤشرات» · الضغط يفتح 🎯
    return ok


def _sg_local_h(now):
    return datetime.fromtimestamp(now).hour


def _sg_quiet(cfg, now):
    q = cfg.get("quiet")
    if not q or q[0] == q[1]:
        return False
    h = _sg_local_h(now)
    return (q[0] <= h < q[1]) if q[0] < q[1] else (h >= q[0] or h < q[1])


def _sg_deliver(blocks, st, cfg, now, send=True):
    """📨 كل ما طلع في الجولة برسالة وحدة · الحد اليومي (الزائد للوحة فقط) · ساعات الهدوء (تنتظر) · الملخص اليومي (يتجمّع)"""
    if not blocks:
        return []
    day = datetime.fromtimestamp(now).strftime("%Y-%m-%d")
    if st.get("day") != day:
        st.update(day=day, n=0, capped=False)
    log = st.setdefault("log", [])
    for b in blocks:
        log.insert(0, {"ts": round(now), "sym": b["sym"], "ty": b["ty"], "f": b.get("f", ""), "t": b["t"], "b": b["b"]})
        _safe(_dash_event, b["sym"], b["t"] + " · " + b["b"].split("\n")[0], default=None)
    del log[120:]
    if cfg.get("sum") is not None:
        st.setdefault("sumq", []).extend({"t": b["t"], "b": b["b"]} for b in blocks)
        del st["sumq"][:-60]
        return []
    if _sg_quiet(cfg, now):
        st.setdefault("qq", []).extend({"t": b["t"], "b": b["b"]} for b in blocks)
        del st["qq"][:-60]
        return []
    out, note = blocks, ""
    if cfg["cap"] > 0:
        room = cfg["cap"] - int(st.get("n") or 0)
        if len(blocks) > max(0, room):
            out = blocks[:max(0, room)]
            if not st.get("capped"):
                st["capped"] = True
                note = f"🔕 وصلت حد إشعارات الإشارات اليوم ({cfg['cap']}) — الباقي في اللوحة فقط (🎯)"
    st["n"] = int(st.get("n") or 0) + len(out)
    if not out and not note:
        return []
    if len(out) == 1:
        text = out[0]["t"] + "\n" + out[0]["b"]
    else:
        text = f"🎯 إشارات جديدة ({len(out)})\n\n" + "\n\n".join(b["t"] + "\n" + b["b"] for b in out)
    text += ("\n\n" + note) if note else ""
    if send:
        _sg_tg(text, cfg)
    return out


def _sg_flush(st, cfg, now, send=True):
    """🌙 بعد ساعات الهدوء: ما انتظر برسالة وحدة · 🗓️ الملخص اليومي بساعته"""
    sent = None
    if st.get("qq") and not _sg_quiet(cfg, now):
        q = st.pop("qq")
        text = f"🌙 إشارات وصلت أثناء ساعات الهدوء ({len(q)})\n\n" + "\n\n".join(x["t"] + "\n" + x["b"] for x in q[:15]) + \
            (f"\n\n… و{len(q) - 15} غيرها في اللوحة (🎯)" if len(q) > 15 else "")
        if send:
            _sg_tg(text, cfg)
        sent = text
    if cfg.get("sum") is not None:
        day = datetime.fromtimestamp(now).strftime("%Y-%m-%d")
        if _sg_local_h(now) >= cfg["sum"] and st.get("sum_day") != day:
            st["sum_day"] = day
            q = st.pop("sumq", [])
            text = f"🗓️ ملخص الإشارات اليوم ({len(q)})" + ("\n\n" + "\n\n".join(x["t"] + "\n" + x["b"] for x in q[:20]) if q else "\nلا توجد إشارات جديدة اليوم بإعداداتك")
            if len(q) > 20:
                text += f"\n\n… و{len(q) - 20} غيرها في اللوحة (🎯)"
            if send:
                _sg_tg(text, cfg)
            sent = text
    elif st.get("sumq"):
        st.pop("sumq", None)
    return sent


# ───────────── 🧭 البوصلة ─────────────
def _sg_compass(cdb, cat=None):
    """🧭 حالة السوق الآن من الشموع اليومية (منعّمة) + ماذا أعطى الشراء فيها تاريخياً"""
    bd = ((cdb.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    if len(bd) < 260:
        return None
    dailies = []
    for sym, e in (cdb.get("c") or {}).items():
        rows = (e or {}).get("d") or []
        if len(rows) >= 60:
            dailies.append(_sg_D(rows[-320:], True))
    seq = _sg_compass_states(_sg_D(bd[-520:], True), dailies)
    if not seq:
        return None
    t, raw, s, since, sh, ab, n, k = seq[-1]
    H = ((cat or {}).get("compass") or {}).get(s) or {}
    return {"s": s, "raw": raw, "since": since, "days": int((t - since) // 86400) + 1, "share": sh, "btc": ab, "n": n, "k": k, "t": t,
            "m14": H.get("m14"), "h14": H.get("h14"), "run": H.get("run"), "hist": [[x[0], x[1], x[2]] for x in seq[-60:]]}


def _sg_comp_block(c):
    nm = {"up": "صاعد 🟢", "flat": "مختلط 🟡", "down": "نازل 🔴"}[c["s"]]
    L = [f"🧭 السوق الآن: {nm} (منذ {_sg_ar(c['days'], 'day')})",
         f"البيتكوين {'فوق' if c['btc'] else 'تحت'} متوسط 200 يوم · {c['k']} من {_sg_ar(c['n'], 'coin')} فوق متوسطها (50 يوماً)"]
    if c.get("m14") is not None:
        L.append(f"تاريخياً: متوسط الشراء بعد أسبوعين {_sg_pct(c['m14'])} في هذا الوضع" + (" — أسوأ وضع للشراء" if c["s"] == "flat" else ""))
    return {"sym": "السوق", "ty": "mkt", "f": "1D", "t": L[0], "b": "\n".join(L[1:])}


# ───────────── 🔄 الجولة ─────────────
def _sg_refresh(coins, frs, cdb, prog=None):
    """🕯️ الشموع المسكّرة لكل عملة (التاريخ كله أول مرة صفحة صفحة · بعدها الجديد فقط) — قراءة عامة"""
    bad = []
    for k, sym in enumerate(coins):
        for fr in frs:
            sec, bar, ib = SG_BAR[fr]
            if prog:
                prog(k, len(coins), sym, fr)
            r = _safe(_fc_cache, sym, cdb, sec, bar, ib, SG_N[fr], default=None)
            if not r or not r[0]:
                bad.append(sym)
            time.sleep(0.15)
    keep = set(coins)
    for sec in ("c", "c4"):
        for s in list((cdb.get(sec) or {}).keys()):
            if s not in keep:
                cdb[sec].pop(s, None)
    os.makedirs(SG_DIR, exist_ok=True)
    save_json_atomic(SG_CFILE, cdb)
    return bad


def _sg_grade(st, cdb, cat, now):
    """✅ السجل الحي: كل إشارة أُطلقت تُحكم وحدها بعد وقتها (صافي بعد العمولة) · نتائج ما وصلك إشعاره"""
    rec = st.setdefault("rec", {})
    keep, res = [], []
    T = {}
    for it in st.get("pend") or []:
        try:
            eid, sym, ts, px, flag = it[0], it[1], int(it[2]), float(it[3]), int(it[4])
        except Exception:
            continue
        fr, side = eid.split("|")[0], int(eid.split("|")[1])
        sec = SG_BAR[fr][0]
        if (sym, sec) not in T:
            rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
            T[(sym, sec)] = ([int(r[0]) for r in rows], [float(r[4]) for r in rows])
        ts_, cs = T[(sym, sec)]
        tgt = ts + SG_HZ[fr] * SG_SEC[fr]
        j = bisect.bisect_left(ts_, tgt)
        if j < len(ts_) and ts_[j] == tgt and px > 0:
            c1 = cs[j]
            x = (c1 / px - 1.0 if side > 0 else px / c1 - 1.0) - SG_FEE
            r = rec.setdefault(eid, [0, 0, 0.0])
            r[0] += 1
            r[1] += 1 if x > 0 else 0
            r[2] = round(r[2] + x, 6)
            if flag:
                res.append((eid, sym, x))
            hist = st.setdefault("done", [])
            hist.insert(0, [eid, sym, ts, round(x, 5), flag])
            del hist[400:]
        elif now - ts < SG_HZ[fr] * SG_SEC[fr] + 20 * 86400:
            keep.append(it)
    st["pend"] = keep
    return res


def _sg_res_block(res, st, cat):
    L = []
    for eid, sym, x in res[:12]:
        e = (cat.get("idx") or {}).get(eid)
        if not e:
            continue
        r = _sg_rec(e, st)
        nm = SG_TY.get(e["ty"], ("", "إشارة"))[1]
        ok = x > 0
        L.append(f"{'✅' if ok else '❌'} نتيجة إشارة {nm} {sym.split('-')[0]} قبل {SG_HZN[e['f']]}: {_sg_pct(x)}\nالسجل الآن: {r['w']} من {_sg_ar(r['n'], 'time')} ({r['h']:.0f}%)")
    if not L:
        return None
    return {"sym": "النتائج", "ty": "res", "f": "", "t": L[0].split("\n")[0] if len(L) == 1 else f"✅ نتائج إشارات سابقة ({len(L)})",
            "b": L[0].split("\n", 1)[1] if len(L) == 1 else "\n".join(L)}


def _sg_process(scan, frs, st, cfg, cat, cdb, now, send=True):
    """🔍 ⇒ ما أُطلق الآن من الدليل لكل عملة (للسجل الحي كلها · وللإشعار ما يمر بإعداداتك) + 🌊 + 😨 + 🗞️ + 🧭"""
    mine = set(sg_coins(cfg))
    byf = {}
    for e in cat["e"]:
        byf.setdefault(e["f"], []).append(e)
    lastf = st.setdefault("lastf", {})
    pend = st.setdefault("pend", [])
    nowv = st.setdefault("now", {})
    comp = st.get("comp")
    groups = {}
    mk_fired = {}
    for sym, F in (scan.get("c") or {}).items():
        for fr in frs:
            x = F.get(fr)
            if not x:
                continue
            A1, A0 = set(x["a1"]), set(x["a0"])
            fired, alive = [], []
            for e in byf.get(fr, []):
                ks = [f"{k}:{e['s']}" for k in e["k"]]
                if not all(k in A1 for k in ks):
                    continue
                alive.append(e["id"])
                if all(k in A0 for k in ks):
                    continue
                lk = f"{e['id']}@{sym}"
                if x["t"] - int(lastf.get(lk) or 0) < SG_LK[fr] * SG_SEC[fr]:
                    continue
                lastf[lk] = x["t"]
                fired.append(e)
            nowv.setdefault(sym, {})[fr] = {"t": x["t"], "px": x["px"], "alive": alive, "fired": [e["id"] for e in fired], "lo": x.get("lo"), "hi": x.get("hi")}
            for e in fired:
                ok = sym in mine and _sg_pass(e, st, cfg, cat)
                pend.append([e["id"], sym, x["t"], x["px"], 1 if ok else 0])
                if e["ty"] in ("crash", "fng", "eco"):
                    if e["ty"] != "crash" or fr == "4H":
                        mk_fired.setdefault((e["ty"], e["k"][0], e["s"]), e)
                    continue
                if ok:
                    groups.setdefault((sym, e["ty"], fr), []).append(e)
    for k in [k for k, v in lastf.items() if now - float(v) > 30 * 86400]:
        lastf.pop(k, None)
    blocks = []
    sent = st.setdefault("sent", {})
    for (sym, ty, fr), ents in groups.items():
        sk = f"{sym}|{ty}|{fr}"
        h = max(_sg_rec(e, st)["h"] for e in ents)
        prev = sent.get(sk) or [0, 0]
        if now - float(prev[0]) < (86400 if fr == "4H" else 3 * 86400) and h < float(prev[1]) + 10:
            continue                                          # نفس العملة ونفس النوع ما يتكرر (إلا لو طلعت أقوى بوضوح)
        sent[sk] = [round(now), round(h, 1)]
        blocks.append(_sg_block(sym, ty, fr, ents, st, cat, ((scan.get("c") or {}).get(sym) or {}).get(fr), comp))
    for k in [k for k, v in sent.items() if now - float(v[0]) > 30 * 86400]:
        sent.pop(k, None)
    # 🌊 · 😨 · 🗞️ — مرة لكل حدث (من سجل الإشارة نفسها في الدليل)
    for (ty, code, side), e in mk_fired.items():
        if not cfg["types"].get(ty, True):
            continue
        if ty == "crash" and _safe(ina_cfg, default={}).get("on"):
            continue                                          # 🌊 يصلك أصلاً من «📊 تنبيهات المؤشرات»
        sk = f"mk|{code}|{side}"
        if now - float((sent.get(sk) or [0])[0]) < 86400:
            continue
        sent[sk] = [round(now), 0]
        blocks.append(_sg_mkt_block(ty, code, side, e, st, cat, scan))
    blocks = [b for b in blocks if b]
    blocks.sort(key=lambda b: (b["ty"] not in ("buy", "up", "sell", "down"), -float(b.get("h") or 0)))
    return blocks


def _sg_mkt_block(ty, code, side, e, st, cat, scan):
    r = _sg_rec(e, st)
    b = (cat.get("base") or {}).get(f"{e['f']}|{e['s']}") or {}
    rec = f"📊 تاريخياً: {'الشراء' if side > 0 else 'البيع'} بعده صدق {r['h']:.0f}% من {_sg_ar(r['n'], 'time')} (العشوائي {float(b.get('ht') or 0):.0f}%) · المتوسط بعد {SG_HZN[e['f']]} {_sg_pct(r['m'] if side > 0 else -r['m'])}"
    if ty == "crash":
        cr = scan.get("crash") or {}
        L = [f"🌊 انهيار في السوق كله · 4 ساعات", f"{cr.get('k', 0)} من {_sg_ar(cr.get('n', 0) or 0, 'coin')} هبطت بقوة في الساعات الأربع الأخيرة", rec]
        mine = set(sg_coins())
        dn = sorted(((F.get("4H") or {}).get("ch", 0), s) for s, F in (scan.get("c") or {}).items() if s in mine)
        dn = [s.split("-")[0] for ch, s in dn[:3] if ch < 0]
        if dn:
            L.append("عملاتك الأكثر هبوطاً الآن: " + " · ".join(dn))
    elif ty == "fng":
        L = [("😨 خوف في السوق" if side > 0 else "🤑 طمع في السوق"), _sg_name(code, side), rec]
    else:
        L = ["🗞️ " + _sg_name(code, side).split(" ", 1)[-1], "قراءة اقتصادية عامة تؤثر في الكريبتو كله", rec]
    if r["h"] <= float(b.get("ht") or 0):
        L.append("⚠️ تاريخياً لم تكن وحدها إشارة — انتظر إشارة ثانية معها")
    return {"sym": "السوق", "ty": ty, "f": e["f"], "t": L[0], "b": "\n".join(L[1:]), "h": r["h"]}


def _sg_cidx(cdb=None):
    """فهرس خفيف (كم شمعة لكل عملة) — ملف الشموع الكبير لا يبقى في الذاكرة"""
    if cdb is None and _SG.get("cidx") is None:
        cdb = _safe(load_json, SG_CFILE, default={}) or {}
    if cdb is not None:
        _SG["cidx"] = {sec: {s: len((e or {}).get("d") or []) for s, e in (cdb.get(sec) or {}).items()} for sec in ("c", "c4")}
    return _SG["cidx"]


def sg_tick(now=None, send=True):
    """⏱️ كل 5 دقائق: 🕯️ الشموع حين تُغلق شمعة · 🏗️ الدليل (أول مرة ثم كل أسبوع أو عملة جديدة) · 🔍 الفحص · ✅ السجل · 📨 الإشعارات"""
    now = float(now if now is not None else time.time())
    if _SG["busy"]:
        return None
    _SG["busy"] = True
    try:
        cfg = sg_cfg()
        st = _sg_st()
        st0 = json.dumps(st, sort_keys=True, ensure_ascii=False)
        uni = _sg_universe()
        cat = _sg_cat()
        bj = _SG.get("build")
        if bj and _sg_job_done(bj):
            o = _sg_job_out(bj) or {}
            _SG["build"] = None
            _SG["err"] = "" if o.get("ok") else ("🏗️ " + str(o.get("err") or "تعذّر بناء الدليل"))
            cat = _sg_cat()
        T = {fr: int(now // SG_SEC[fr]) * SG_SEC[fr] - SG_SEC[fr] for fr in SG_FR}
        due = [fr for fr in SG_FR if st.get("t_" + fr) != T[fr] and now - (T[fr] + SG_SEC[fr]) >= 90]
        if due and now - float(st.get("t_fail") or 0) < 1800:
            due = []                                          # فحص فشل قبل قليل ⇒ محاولة بعد نصف ساعة (لا نُثقل المنصة)
        ci = _sg_cidx()
        bad, bad_ok = set(st.get("bad") or []), now - float(st.get("bad_t") or 0) > 6 * 3600
        missing = [s for s in uni if (s not in ci["c4"] or s not in ci["c"]) and (s not in bad or bad_ok)]
        full = lambda s: ci["c4"].get(s, 0) >= SG_MIN["4H"] and ci["c"].get(s, 0) >= SG_MIN["1D"]
        need_cat = (not cat or now - float(cat.get("ts") or 0) > SG_CAT_AGE or bool(st.get("cat_force"))
                    or any(s not in (cat.get("coins") or []) and full(s) for s in sg_coins(cfg)))
        build_now = need_cat and not _SG.get("build") and now - float(st.get("cat_try") or 0) > (6 * 3600 if cat and not st.get("cat_force") else 600)
        cdb = None
        if missing or due or build_now:
            cdb = _safe(load_json, SG_CFILE, default={}) or {}
            _SG.update(phase="fetch", msg="📥 تجهيز تاريخ الشموع" if missing else "🕯️ الشموع الجديدة", pct=0)

            def pg(k, n, sym, fr):
                _SG.update(pct=round(100.0 * k / max(1, n)), msg=(f"📥 تاريخ {sym.split('-')[0]} ({k + 1} من {n}) — أول مرة فقط" if missing else
                                                                  f"🕯️ {sym.split('-')[0]} ({k + 1} من {n})"))
            bd_ = _sg_refresh(uni, list(SG_FR), cdb, pg)
            ci = _sg_cidx(cdb)
            st["bad"] = sorted(set(bd_))
            if bd_:
                st["bad_t"] = now
        if build_now:
            coins = [s for s in uni if full(s)]
            if len(coins) >= 3:
                st["cat_try"] = now
                st.pop("cat_force", None)
                _SG["build"] = _sg_spawn("build", {"coins": coins})
        if cdb is not None:
            comp = _safe(_sg_compass, cdb, cat, default=None)
            prev_c = st.get("comp") or {}
            if comp:
                if prev_c.get("s") and comp["s"] != prev_c.get("s") and comp["since"] != prev_c.get("since"):
                    st["comp_new"] = comp["s"]
                st["comp"] = comp
        blocks = []
        if cat and due:
            have = [s for s in uni if ci["c4"].get(s, 0) >= 300 and ci["c"].get(s, 0) >= 220]
            _SG.update(phase="scan", msg="🔍 فحص الإشارات على آخر شمعة", pct=0)
            sj = _sg_spawn("scan", {"coins": have, "frs": due})
            t1 = time.time()
            while not _sg_job_done(sj) and time.time() - t1 < 1500:
                time.sleep(2)
                _SG["pct"] = int(_sg_job_prog(sj).get("pct") or 0)
            if not _sg_job_done(sj):
                _sg_job_stop(sj)
            sc = _sg_job_out(sj) or {}
            if sc.get("ok"):
                for fr in due:
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
                for s in [s for s in (st.get("now") or {}) if s not in uni]:
                    st["now"].pop(s, None)
                _SG["err"] = ""
            else:
                st["t_fail"] = now
                _SG["err"] = "🔍 " + str(sc.get("err") or "تعذّر فحص الإشارات")
        cdb = None
        if cfg["on"]:
            _sg_deliver(blocks, st, cfg, now, send=send)
            _sg_flush(st, cfg, now, send=send)
        if json.dumps(st, sort_keys=True, ensure_ascii=False) != st0:
            _sg_save(st)
        _SG.update(phase="", msg="", pct=0)
        return blocks
    finally:
        _SG["busy"] = False


def sg_loop():
    """⏱️ حلقة مستقلة (كل 5 دقائق) — تعمل مع المؤشرات أو مع إشعارات الإشارات"""
    time.sleep(150)
    while True:
        try:
            if indic_cfg()["on"] or sg_cfg()["on"]:
                sg_tick()
        except Exception as ex:
            _SG.update(busy=False, err=f"{type(ex).__name__}")
        time.sleep(SG_EVERY)


# ───────────── 🖥️ العرض ─────────────
def _sg_row(e, st, cat, cfg):
    r = _sg_rec(e, st)
    b = (cat.get("base") or {}).get(f"{e['f']}|{e['s']}") or {}
    return {"id": e["id"], "f": e["f"], "s": e["s"], "ty": e["ty"], "k": e["k"], "nm": [_sg_name(k, e["s"]) for k in e["k"]],
            "n": r["n"], "w": r["w"], "h": round(r["h"], 1), "m": round(r["m"] if e["s"] > 0 else -r["m"], 5), "ln": r["ln"], "lw": r["lw"],
            "nt": e["nt"], "ht": round(e["wt"] / e["nt"] * 100.0, 1) if e["nt"] else None, "nl": e["nl"],
            "hl": round(e["wl"] / e["nl"] * 100.0, 1) if e["nl"] else None, "rare": bool(e.get("rare")),
            "rh": float(b.get("ht") or 0), "ok": _sg_pass(e, st, cfg, cat),
            "better": r["h"] > float(b.get("ht") or 0) and r["m"] > float(b.get("mt") or 0)}


def sg_view():
    cfg = sg_cfg()
    st = _sg_st()
    cat = _sg_cat()
    bj = _SG.get("build")
    bp = _sg_job_prog(bj) if bj else {}
    v = {"ok": True, "cfg": cfg, "types": {k: list(x) for k, x in SG_TY.items()}, "ch": SG_CH, "fn": SG_FN, "hzn": SG_HZN,
         "mine": sg_coins(cfg), "tick": ticker_cfg()["coins"], "uni": _sg_universe(),
         "busy": {"phase": "build" if bj else _SG.get("phase") or "", "pct": int(bp.get("pct") or 0) if bj else int(_SG.get("pct") or 0),
                  "msg": (bp.get("msg") or "🏗️ بناء دليل الإشارات") if bj else _SG.get("msg") or ""},
         "err": _SG.get("err") or "", "comp": st.get("comp"), "crash": st.get("crash"), "scan_ts": st.get("scan_ts"),
         "on": indic_cfg()["on"] or cfg["on"], "log": (st.get("log") or [])[:60]}
    if not cat:
        v.update(cat=None, now=[], est=None)
        return v
    idx = cat["idx"]
    v["cat"] = {"ts": cat.get("ts"), "coins": cat.get("coins"), "n": len(cat["e"]), "secs": cat.get("secs"), "wk": cat.get("wk"),
                "base": cat.get("base"), "comp": cat.get("compass"), "span": cat.get("span"),
                "nrare": sum(1 for e in cat["e"] if e.get("rare")), "ncombo": sum(1 for e in cat["e"] if len(e["k"]) > 1)}
    now_ = []
    mine = sg_coins(cfg)
    for sym, F in (st.get("now") or {}).items():
        it = {"sym": sym, "base": sym.split("-")[0], "mine": sym in mine, "fr": {}}
        for fr, x in F.items():
            rows = [_sg_row(idx[i], st, cat, cfg) for i in x.get("alive") or [] if i in idx]
            rows = [dict(r, new=r["id"] in (x.get("fired") or [])) for r in rows]
            rows.sort(key=lambda r: (not r["ok"], -r["h"], -r["n"]))
            it["fr"][fr] = {"t": x.get("t"), "px": x.get("px"), "rows": rows[:80], "nb": sum(1 for r in rows if r["s"] > 0 and r["ok"]),
                            "ns": sum(1 for r in rows if r["s"] < 0 and r["ok"])}
        now_.append(it)
    now_.sort(key=lambda x: (not x["mine"], x["sym"]))
    v["now"] = now_
    v["est"] = sg_estimate(cfg, st)
    v["live"] = {"pend": len(st.get("pend") or []), "done": len(st.get("done") or []),
                 "recent": [{"id": d[0], "sym": d[1], "ts": d[2], "x": d[3], "nt": d[4], "ty": (idx.get(d[0]) or {}).get("ty"),
                             "nm": " + ".join(_sg_name(k, (idx.get(d[0]) or {}).get("s", 1)) for k in (idx.get(d[0]) or {}).get("k", []))}
                            for d in (st.get("done") or []) if d[4]][:40]}
    return v


def sg_catlist(q):
    """📒 تصفّح الدليل: الفريم · الجهة · العدد · 💎 · بحث · الترتيب"""
    cat = _sg_cat()
    if not cat:
        return {"ok": False, "rows": [], "msg": "الدليل لم يُبنَ بعد"}
    cfg, st = sg_cfg(), _sg_st()
    fr, side, sz, rare, txt, srt, ty = (q.get(k, [""])[0] for k in ("fr", "side", "size", "rare", "q", "sort", "ty"))
    rows = []
    for e in cat["e"]:
        if fr in SG_FR and e["f"] != fr:
            continue
        if side in ("1", "-1") and e["s"] != int(side):
            continue
        if sz and sz.isdigit() and (len(e["k"]) != int(sz) if int(sz) < 4 else len(e["k"]) < 4):
            continue
        if rare == "1" and not e.get("rare"):
            continue
        if ty and e["ty"] != ty:
            continue
        r = _sg_row(e, st, cat, cfg)
        if txt and txt.strip() and txt.strip().lower() not in (" ".join(r["nm"]) + " " + " ".join(e["k"])).lower():
            continue
        rows.append(r)
    key = {"n": lambda r: -r["n"], "m": lambda r: -r["m"], "live": lambda r: -r["ln"]}.get(srt, lambda r: (-r["h"], -r["n"]))
    rows.sort(key=key)
    return {"ok": True, "rows": rows[:250], "total": len(rows), "base": cat.get("base")}


def sg_test():
    cfg = sg_cfg()
    if TG_MUTED["v"]:
        return {"ok": False, "msg": "🔕 الكتم مفعّل (زر 🔔 في الأعلى) — لن يُرسَل شيء حتى تلغيه"}
    sym = (sg_coins(cfg) or ["BTC-USDT"])[0]
    text = (f"🧪 تجربة — 🟢 شراء — {sym} · يومي\nاتفقت 3 إشارات: Supertrend انقلب أخضر فوق EMA 150 · تقاطع MACD صاعد فوق EMA 20 · 💧 تدفق السيولة (CMF): صاعد\n"
            f"📊 هكذا يصلك السجل: كم مرة صدقت من كم مرة · والعشوائي للمقارنة · والمتوسط بعد المدة\n"
            f"⚙️ إعداداتك: {cfg['thr']}% فأكثر · {_sg_ar(cfg['min'], 'time')} فأكثر · {SG_CH[cfg['ch']]}")
    ok = _sg_tg(text, cfg)
    return {"ok": True, "msg": "🧪 أُرسلت التجربة" + ("" if ok or cfg["ch"] == "app" else " — لم يستلمها تيليغرام (تأكد من التوكن ومن Chat ID)")}


def sg_rebuild():
    """🏗️ «أعد البحث الآن» — يُعاد بناء الدليل في الجولة التالية"""
    if _SG.get("build"):
        return {"ok": True, "msg": "🏗️ البناء جارٍ أصلاً — تتابعه هنا"}
    st = _sg_st()
    st["cat_try"] = 0
    st["cat_force"] = True
    _sg_save(st)
    if not _SG["busy"]:
        threading.Thread(target=_safe, args=(sg_tick,), daemon=True).start()
    return {"ok": True, "msg": "🏗️ يُعاد بناء دليل الإشارات بالخلفية — دقائق (تتابعه هنا)"}


def sg_api():
    v = sg_view()
    if v["on"] and not _SG["busy"] and (not v.get("cat") or not v.get("now")) and not _SG.get("build"):
        threading.Thread(target=_safe, args=(sg_tick,), daemon=True).start()
    return v


'''
