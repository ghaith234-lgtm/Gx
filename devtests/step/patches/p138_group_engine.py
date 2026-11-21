# p138 — v3.36.77 🧩 the indicators rebuilt as GROUPS (the owner 21-11: «قسمين للعملات وللسوق … كل مجموعه تختص باشعار … تصنف التجارب على
#   اختباراتك ما نبدي من الجديد … يكون المصدر مفتوح … عندما ياتي توليفة او مؤشر تنضاف مع شغل جماعتها ويختبر قبل ما يدخل … ساعه ٤ ساعات يوم»)
#   · the engine only (not wired yet): the registry (🪙 8 coin groups · 🌐 7 market groups · each = one job = one notification · members by
#     family + by name, open to new indicators · combos of two inside a group) · gp_walk (every member graded on its group's job at the next
#     candle of 1H / 4H / 1D, in time order, pooled over the coins · the usual removes the market's drift · champions with a safety gap ·
#     at most two per group) · gp_pack · gp_build (the whole history, three frames, market-wide readings on the whole history) · gp_now
#     (the live check — the same _gp_keys as the history) · the same functions run in ci/sig_check16.py
#   python3 devtests/step/patches/p138_group_engine.py Holy_Dashboard.pyw
import sys, os

ENGINE = r'''# ───────────── 🧩 v3.36.77: المؤشرات من جديد — مجاميع للعملة وللسوق · كل مجموعة بشغلها وإشعارها · تُختبر على التاريخ ─────────────
#   المالك (21-11): «قسمين للعملات وللسوق … كل مجموعه تختص باشعار … تصنف التجارب على اختباراتك ما نبدي من الجديد … يكون المصدر مفتوح اذا
#   اضفنا مؤشرات جديدة … عندما ياتي توليفة او مؤشر تنضاف مع شغل جماعتها ويختبر قبل ما يدخل … الاشعارات فقط ساعه ٤ ساعات يوم»
#   · قسمان: 🪙 العملة (يُحكم بسعر كل عملة · السجل لكل العملات معاً ولكل عملة من عملاتك) و🌐 السوق (يُحكم بسعر البيتكوين ومعه قراءات
#     السوق كله والاقتصاد)
#   · المجموعة = شغل واحد (GP_JOBS) ⇒ إشعار واحد · أعضاؤها: كل مؤشر من أسرها (مؤشر جديد بأسرته يدخل وحده) + ما يُضاف بالاسم +
#     التوليفات: اثنان من المجموعة نفسها بالجهة نفسها (الثاني انطلق الآن والأول خلال آخر شموع «معاً»)
#   · كل عضو يُحكم على شغل مجموعته بالشمعة التالية من إطاره (ساعة · 4 ساعات · يوم) على التاريخ كله بترتيب الزمن (لا نتيجة قبل وقتها)
#     ⇒ البطل: ≥ dmin يوماً مختلفاً · صدقه ≥ العادي + lift · وحدّ ويلسون الأدنى فوق العادي ⇒ يبقى حتى ينزل تحت العادي + gap · cap أبطال
#     لكل مجموعة بكل إطار · «العادي» = ما يصيبه تنبؤ عشوائي بالجهات نفسها على شموع ذلك الوقت (يزيل أثر صعود السوق الطويل)
#   · الإشعار من الأبطال فقط: ما سيحدث بشغل المجموعة + صدق العضو وعدد مراته والعادي + اسمه · سجل المجموعة = ما كان سيصل وحكمه
#   · عرض وإشعارات فقط — لا أوامر · الحساب في عامل الفحص (بلا شبكة) · الدوال نفسها في ci/sig_check16.py
GP_FR = ("1H", "4H", "1D")
GP_FRN = {"1H": ("⏱", "ساعة", "خلال الساعة القادمة"), "4H": ("🕓", "4 ساعات", "خلال الساعات الأربع القادمة"), "1D": ("📅", "يوم", "خلال اليوم القادم")}
GP_HIST = {"1H": 2160, "4H": 3000, "1D": 2600}           # كم شمعة يُختبر عليها كل إطار (~3 أشهر · ~16 شهراً · ~7 سنوات)
GP_MV = 0.002                                            # حركة أصغر من 0.2% (عمولة الذهاب والعودة) لا تُحسب
GP_BIGX = 1.5                                            # «حركة كبيرة» = ≥ 1.5 × وسيط حركة آخر 20 شمعة
GP_P = {"dmin": 30, "lift": 0.05, "gap": 0.02, "cap": 2, "combo": 1}
GP_SAY = 0.03                                            # 📲 يصل فوراً فقط إذا كان سجل المجموعة نفسه (ما كان سيصل) ≥ العادي + 3% على 30 مرة فأكثر
GP_ONE = {"W-crash": -1, "W-surge": 1}                   # أحداث تُقرأ بجهة واحدة
GP_JOBS = {   # الشغل ⇒ (اسمه · كيف يُحكم)
    "dir": ("الجهة", "السعر تحرك بجهة التنبؤ في الشمعة التالية (أكثر من 0.2%)"),
    "big": ("حجم الحركة", "الشمعة التالية تحركت 1.5 ضعف حركتها المعتادة فأكثر (أي جهة)"),
    "rs": ("مقابل البيتكوين", "العملة سبقت البيتكوين بجهة التنبؤ في الشمعة التالية (بفارق أكثر من 0.2%)"),
}
GP_GROUPS = {   # 🧩 المفتاح ⇒ القسم · الأيقونة · الاسم · الشغل · ما يقوله الإشعار (صعود · هبوط) · الأسر · المضاف بالاسم · المستبعد · المستوى الافتراضي
    "c_trend": {"sec": "coin", "ic": "📈", "nm": "الاتجاه", "job": "dir", "say": ("يُتوقع أن يكمل الصعود", "يُتوقع أن يكمل الهبوط"), "fam": ("trend",),
                "lv": "now"},
    "c_mom": {"sec": "coin", "ic": "⚡", "nm": "قوة الحركة", "job": "dir", "say": ("يُتوقع اندفاع صاعد", "يُتوقع اندفاع هابط"), "fam": ("momentum",),
              "no": ("X-rs",), "lv": "view"},
    "c_big": {"sec": "coin", "ic": "💥", "nm": "حركة كبيرة قادمة", "job": "big", "say": ("يُتوقع حركة أكبر من المعتاد", "يُتوقع حركة أكبر من المعتاد"),
              "fam": ("volatility",), "no": ("O-bottom",), "lv": "now"},
    "c_rev": {"sec": "coin", "ic": "🟢", "nm": "الارتداد من القاع", "job": "dir", "say": ("يُتوقع ارتداد صاعد", "يُتوقع تراجع"), "add": ("O-bottom", "O-botv"),
              "lv": "now"},
    "c_brk": {"sec": "coin", "ic": "🧱", "nm": "الكسر والاختراق", "job": "dir", "say": ("يُتوقع أن يكمل الاختراق صعوداً", "يُتوقع أن يكمل الكسر هبوطاً"),
              "fam": ("pattern",), "lv": "view"},
    "c_flow": {"sec": "coin", "ic": "🧲", "nm": "السيولة والحجم", "job": "dir", "say": ("السيولة تدفع للصعود", "السيولة تدفع للهبوط"), "fam": ("volume",),
               "no": ("O-botv",), "lv": "view"},
    "c_rs": {"sec": "coin", "ic": "💪", "nm": "مقابل البيتكوين", "job": "rs", "say": ("يُتوقع أن تسبق البيتكوين", "يُتوقع أن تتأخر عن البيتكوين"),
             "add": ("X-rs", "O-trend", "O-st", "O-macd", "O-rsi"), "lv": "view"},
    "c_pro": {"sec": "coin", "ic": "🏦", "nm": "العقود والمحترفون", "job": "dir", "say": ("المحترفون يدفعون للصعود", "المحترفون يدفعون للهبوط"), "fam": ("pro",),
              "lv": "view"},
    "m_trend": {"sec": "mkt", "ic": "🧭", "nm": "اتجاه السوق", "job": "dir", "say": ("يُتوقع صعود السوق", "يُتوقع هبوط السوق"), "fam": ("trend",),
                "add": ("W-breadth", "W-comp"), "lv": "now"},
    "m_mom": {"sec": "mkt", "ic": "⚡", "nm": "زخم السوق", "job": "dir", "say": ("يُتوقع اندفاع صاعد للسوق", "يُتوقع اندفاع هابط للسوق"), "fam": ("momentum",),
              "no": ("X-rs",), "lv": "view"},
    "m_shock": {"sec": "mkt", "ic": "🌊", "nm": "صدمات السوق", "job": "dir", "say": ("بعد الصدمة: يُتوقع صعود", "بعد الصدمة: يُتوقع هبوط"),
                "add": ("W-crash", "W-surge"), "lv": "now"},
    "m_mood": {"sec": "mkt", "ic": "😨", "nm": "مزاج السوق", "job": "dir", "say": ("المزاج يدفع للصعود", "المزاج يدفع للهبوط"), "add": ("M-fng",), "lv": "view"},
    "m_macro": {"sec": "mkt", "ic": "🗞️", "nm": "الاقتصاد", "job": "dir", "say": ("الاقتصاد يدفع للصعود", "الاقتصاد يدفع للهبوط"),
                "add": ("M-vix", "M-dxy", "M-us10", "M-epu", "M-gpr", "M-tone"), "lv": "view"},
    "m_vol": {"sec": "mkt", "ic": "🎢", "nm": "هدوء أو هيجان", "job": "big", "say": ("يُتوقع حركة كبيرة للسوق", "يُتوقع حركة كبيرة للسوق"), "fam": ("volatility",),
              "no": ("O-bottom",), "add": ("W-crash", "W-surge"), "lv": "now"},
    "m_pro": {"sec": "mkt", "ic": "🏦", "nm": "العقود والسيولة الكبيرة", "job": "dir", "say": ("المحترفون والسيولة يدفعون للصعود", "المحترفون والسيولة يدفعون للهبوط"),
              "fam": ("pro",), "lv": "view"},
}
GP_SECN = {"coin": ("🪙", "العملات"), "mkt": ("🌐", "السوق")}
GP_MKTWIDE = ("market",)                                  # أسرة قراءات السوق كله — لا تدخل مجاميع العملة (هي نفسها لكل العملات)
GP_FILE = os.path.join(ROOT, "Holy_Groups.json")         # آخر بناء (السجل · الأبطال · الأعضاء) — يُعاد كل يوم
GP_VER = 1


def _gp_codes():
    """كل رمز معروف (الأنظمة الـ36 + القراءات) ⇒ أسرته — مؤشر جديد يُضاف إلى _SG_NM أو _SG_XNM يظهر هنا وحده"""
    L = _sg_lib()
    out = {}
    for c in list(L.SYS) + list(_SG_XNM):
        p = _sg_plain(c)
        if p:
            out[c] = p[0]
    return out


def gp_members(g, codes=None):
    """أعضاء المجموعة (المؤشرات): كل رمز من أسرها + المضاف بالاسم − المستبعد · قراءات السوق كله خارج مجاميع العملة"""
    G = GP_GROUPS[g]
    codes = codes if codes is not None else _gp_codes()
    out = {c for c, f in codes.items() if f in G.get("fam", ()) and c not in G.get("no", ()) and not (G["sec"] == "coin" and f in GP_MKTWIDE)}
    out.update(c for c in G.get("add", ()) if c in codes)
    return sorted(out)


def _gp_fires(E, allowed):
    """كل شمعة ⇒ {الرمز: الجهة} (الجهتان معاً على الشمعة نفسها ⇒ لا شيء · أحداث الجهة الواحدة بجهتها)"""
    f = {}
    for (code, s), lst in E.items():
        if code not in allowed or (code in GP_ONE and s != GP_ONE[code]):
            continue
        for i in lst:
            d = f.setdefault(i, {})
            d[code] = s if d.get(code, s) == s else 0
    return {i: {c: s for c, s in d.items() if s} for i, d in f.items()}


def _gp_keys(FI, i, mem, lk, job, combo=True):
    """ما انطلق في المجموعة على الشمعة i ⇒ {العضو: الجهة}: المؤشرات + التوليفات (اثنان بالجهة نفسها · الثاني انطلق الآن والأول خلال lk شمعة)
    · شغل «حجم الحركة» بلا جهة (كل الأعضاء ⇒ +1) — الدالة نفسها للتاريخ وللفحص الحي"""
    now = {c: s for c, s in (FI.get(i) or {}).items() if c in mem}
    if not now:
        return {}
    keys = dict(now)
    if combo:
        for c, s in now.items():
            for k in range(lk):
                for c2, s2 in (FI.get(i - k) or {}).items():
                    if c2 != c and s2 == s and c2 in mem and (k > 0 or c2 > c):
                        keys.setdefault("+".join(sorted((c, c2))), s)
    if job == "big":
        keys = {k_: 1 for k_ in keys}
    return keys


def _gp_med(C, w=20):
    """وسيط حركة آخر w شمعة (|عائد|) حتى كل شمعة"""
    n = len(C)
    r = [0.0] + [abs(C[i] / C[i - 1] - 1.0) if C[i - 1] else 0.0 for i in range(1, n)]
    med = [None] * n
    for i in range(w, n):
        med[i] = sorted(r[i - w + 1:i + 1])[w // 2]
    return med


def _gp_outs(job, D, B=None):
    """نتيجة كل شمعة لشغل المجموعة (للحكم وللعادي): +1 · −1 · None (حركة صغيرة · لا شمعة بعدها · لا سعر بيتكوين)
    dir: جهة إغلاق الشمعة التالية · big: هل تحركت ≥ 1.5 × المعتاد · rs: هل سبقت العملة البيتكوين"""
    C, T, n = D["C"], D["T"], D["n"]
    out = [None] * n
    med = _gp_med(C) if job == "big" else None
    for i in range(n - 1):
        if not C[i]:
            continue
        r = C[i + 1] / C[i] - 1.0
        if job == "big":
            if med[i]:
                out[i] = 1 if abs(r) >= GP_BIGX * med[i] else -1
            continue
        if job == "rs":
            b0, b1 = (B or {}).get(T[i]), (B or {}).get(T[i + 1])
            if not b0 or not b1:
                continue
            r -= b1 / b0 - 1.0
        if abs(r) >= GP_MV:
            out[i] = 1 if r > 0 else -1
    return out


def _gp_pb(nup, n, u):
    """العادي لعضو: لو أُطلق التنبؤ عشوائياً بالجهات نفسها (نصيب الصعود q) على شموع نصيب «+1» فيها u ⇒ q·u + (1−q)(1−u)"""
    q = nup / n if n else 0.5
    return q * u + (1 - q) * (1 - u)


def gp_walk(F, sec, fr, B=None, p=None, keep=(), codes=None, groups=None):
    """🧩 F = {العملة: (الشموع, الإشارات)} لإطار واحد (العملات: كل العملات · السوق: البيتكوين وحده ومعه قراءات السوق كله) ⇒ بترتيب الزمن:
    سجل كل عضو (مؤشر أو توليفة) على شغل مجموعته للعملات معاً (ولكل عملة في keep) · الأبطال بما عُرف وقتها فقط · ما كان سيصل وحكمه
    rec[المجموعة][العضو] = [صدق · أخطأ · أيام مختلفة · آخر يوم · مرات الصعود] · B = {وقت الشمعة: إغلاق البيتكوين} لشغل «مقابل البيتكوين»
    sent[المجموعة] = [(الوقت, العملة, الجهة, النتيجة 1 صدق · 0 أخطأ · None حركة صغيرة · -1 لم تُغلق التالية, العادي وقتها, الأبطال)]"""
    p = dict(GP_P, **(p or {}))
    codes = codes if codes is not None else _gp_codes()
    groups = [g for g in (groups or GP_GROUPS) if GP_GROUPS[g]["sec"] == sec]
    mem = {g: set(gp_members(g, codes)) for g in groups}
    allowed = set().union(*mem.values()) if mem else set()
    jobs = sorted({GP_GROUPS[g]["job"] for g in groups})
    lk = SG_LK.get(fr, 2)
    FI, OUT, times, known = {}, {}, {}, []
    for sym, (D, E) in F.items():
        FI[sym] = fi = _gp_fires(E, allowed)
        OUT[sym] = {j: _gp_outs(j, D, B) for j in jobs if not (j == "rs" and sym.startswith("BTC-"))}
        for i in fi:
            times.setdefault(D["T"][i], []).append((sym, i))
        for j, o in OUT[sym].items():
            known.extend((D["T"][i + 1], j, o[i]) for i in range(D["n"] - 1) if o[i] is not None)
    known.sort(key=lambda x: x[0])
    U = {j: [0, 0] for j in jobs}                         # لكل شغل: [مرات +1 · كل المحكوم] حتى الآن (للعادي)
    ku = 0
    rec, rc, on, champ = {g: {} for g in groups}, {g: {} for g in groups}, {g: set() for g in groups}, {g: [] for g in groups}
    pend, pk, sent, now = {}, [], {g: [] for g in groups}, {g: {} for g in groups}
    tl = max((D["T"][D["n"] - 1] for D, E in F.values()), default=0)

    def u_(j):
        x = U[j]
        return x[0] / x[1] if x[1] else 0.5

    def sc(r):
        return r[0] / (r[0] + r[1]) if r[0] + r[1] else 0.0
    for t in sorted(times):
        while ku < len(known) and known[ku][0] <= t:
            _k, j, o = known[ku]
            U[j][0] += o > 0
            U[j][1] += 1
            ku += 1
        moved = set()
        while pk and pk[0] <= t:
            k = heapq.heappop(pk)
            for g, key, sym, win, s, d in pend.pop(k, ()):
                r = rec[g].get(key)
                if r is None:
                    r = rec[g][key] = [0, 0, 0, -1, 0]
                r[0 if win else 1] += 1
                r[4] += s > 0
                if d != r[3]:
                    r[2] += 1
                    r[3] = d
                if sym in keep:
                    x = rc[g].setdefault(sym, {}).setdefault(key, [0, 0])
                    x[0 if win else 1] += 1
                moved.add(g)
        for g in moved:
            u = u_(GP_GROUPS[g]["job"])
            for key, r in rec[g].items():
                n_ = r[0] + r[1]
                pb = _gp_pb(r[4], n_, u)
                if key in on[g]:
                    if sc(r) < pb + p["gap"]:
                        on[g].discard(key)
                elif r[2] >= p["dmin"] and sc(r) >= pb + p["lift"] and _sg_wlb(r[0], n_) / 100.0 > pb and (p["combo"] or "+" not in key):
                    on[g].add(key)
            champ[g] = sorted(on[g], key=lambda k_: (-sc(rec[g][k_]), -(rec[g][k_][0] + rec[g][k_][1]), k_))[:p["cap"]]
        d = t // 86400
        for sym, i in times[t]:
            D = F[sym][0]
            for g in groups:
                j = GP_GROUPS[g]["job"]
                o = OUT[sym].get(j)
                if o is None:
                    continue
                keys = _gp_keys(FI[sym], i, mem[g], lk, j, combo=bool(p["combo"]))
                if not keys:
                    continue
                oi = o[i]
                if oi is not None:
                    kn = D["T"][i + 1]
                    if kn not in pend:
                        pend[kn] = []
                        heapq.heappush(pk, kn)
                    pend[kn].extend((g, key, sym, oi == s, s, d) for key, s in keys.items())
                cs = [k_ for k_ in champ[g] if k_ in keys]
                sides = {keys[k_] for k_ in cs}
                if len(sides) == 1:                      # ما كان سيصل: أبطال المجموعة انطلقوا بجهة واحدة (لا بطل بالجهة المعاكسة)
                    s = sides.pop()
                    u = u_(j)
                    res = (-1 if i + 1 >= D["n"] else None) if oi is None else (1 if oi == s else 0)
                    sent[g].append((t, sym, s, res, round(u if s > 0 else 1 - u, 4), cs))
                    if t == tl:
                        now[g][sym] = [s, cs]
    return {"sec": sec, "fr": fr, "p": p, "U": {j: u_(j) for j in jobs}, "rec": rec, "rc": rc, "on": on, "champ": champ, "sent": sent, "now": now,
            "t": tl, "mem": {g: sorted(mem[g]) for g in groups}, "keep": list(keep)}


def gp_score(sent, t_from=0, t_to=None, sym=None):
    """سجل ما كان سيصل: [صدق · المحكوم · مجموع العادي] (الحركة الصغيرة والتي لم تُغلق بعد لا تُحسب)"""
    w = n = 0
    b = 0.0
    for x in sent:
        if x[0] >= t_from and (t_to is None or x[0] < t_to) and x[3] in (0, 1) and (sym is None or x[1] == sym):
            w += x[3]
            n += 1
            b += x[4]
    return [w, n, round(b, 2)]


def gp_pack(W, top=10):
    """🧩 للوحة: لكل مجموعة — سجلها (ما كان سيصل: كله · آخر ربع · لكل عملة من عملاتك) مع العادي · الأعضاء (كل المؤشرات + أفضل التوليفات)
    بحالتهم (2 ⭐ بطل · 1 ✅ مثبت خارج الحد · 0 🧪 قيد الاختبار · −1 لم يثبت) · الأبطال · ما انطلق الآن
    m = [العضو · صدق · أخطأ · أيام · الحالة · العادي]"""
    tl = W["t"]
    out = {"sec": W["sec"], "fr": W["fr"], "t": tl, "U": {j: round(u, 4) for j, u in W["U"].items()}, "p": W["p"], "g": {}}
    for g, R in W["rec"].items():
        u = W["U"].get(GP_GROUPS[g]["job"], 0.5)
        rows = []
        for key, r in R.items():
            n_ = r[0] + r[1]
            pb = _gp_pb(r[4], n_, u)
            st = 2 if key in W["champ"][g] else 1 if key in W["on"][g] else 0 if r[2] < W["p"]["dmin"] else -1
            rows.append([key, r[0], r[1], r[2], st, round(pb, 4)])
        rows.sort(key=lambda x: (-max(0, x[4]), -(_sg_wlb(x[1], x[1] + x[2]) / 100.0 - x[5] if x[1] + x[2] else -1)))
        singles = [x for x in rows if "+" not in x[0]]
        combos = [x for x in rows if "+" in x[0]]
        combos = [x for x in combos if x[4] > 0] + [x for x in combos if x[4] <= 0][:top]
        known = {x[0] for x in singles}
        singles += [[c, 0, 0, 0, 0, 0.5] for c in W["mem"][g] if c not in known]          # عضو لم ينطلق بعد ⇒ 🧪
        S = W["sent"][g]
        span = tl - S[0][0] if S else 0
        out["g"][g] = {"rec": gp_score(S), "rec1": gp_score(S, tl - span // 4) if span else [0, 0, 0.0], "m": singles + combos, "ch": list(W["champ"][g]),
                       "now": W["now"][g], "nm": len(W["mem"][g]), "nc": len(combos),
                       "coin": {s: {"rec": gp_score(S, sym=s), "m": W["rc"][g].get(s) or {}} for s in W["keep"]}}
    return out


def _gp_surge(F, Z, k0):
    """🚀 الصعود المفاجئ للسوق كله: ≥ 30% من العملات (10 فأكثر) صعدت ≥ 2.5× حركتها المعتادة في الشمعة نفسها (مرآة 🌊 الانهيار)"""
    UP = {t for t, z in Z.items() if len(z) >= 10 and sum(1 for x in z if x >= 2.5) / len(z) >= 0.3}
    for sym, (D, E) in F.items():
        idx = [i for i in range(max(210, k0), D["n"]) if D["T"][i] in UP]
        if idx:
            E[("W-surge", 1)] = idx


def _gp_wide(FF, full=False):
    """🌐 قراءات السوق كله لكل إطار ⇒ تُضاف لكل عملة: 🌊 الانهيار و🚀 الصعود المفاجئ (10 عملات فأكثر) · 📊 عدد العملات فوق متوسط آخر
    50 شمعة (60% ⇒ صعود · 40% ⇒ هبوط · لا ترجع إلا بعد أن تعبر المنتصف) · 🧭 البوصلة على اليومي (انقلبت إلى صاعد أو نازل)
    full: على التاريخ كله (البناء اليومي) · وإلا على آخر الشموع (الفحص)"""
    for fr, F in FF.items():
        if len(F) < 10:
            continue
        k0 = 210 if full else min(D["n"] for D, E in F.values()) - 8
        CR, Z = _sg_crash(F, k0=k0)
        _gp_surge(F, Z, k0)
        AB = {}
        for sym, (D, E) in F.items():
            C, n = D["C"], D["n"]
            if n < 100:
                continue
            cs = [0.0]
            for x in C:
                cs.append(cs[-1] + x)
            for i in range(49 if full else n - 40, n):
                AB.setdefault(D["T"][i], []).append(C[i] > (cs[i + 1] - cs[i - 49]) / 50.0)
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
            for i in range(210 if full else max(210, D["n"] - 4), D["n"]):
                s = ev.get(D["T"][i])
                if s:
                    E.setdefault(("W-breadth", s), []).append(i)
        if fr == "1D" and "BTC-USDT" in F:
            seq = _sg_compass_states(F["BTC-USDT"][0], [D for D, E in F.values()])
            for k in range(1 if full else max(1, len(seq) - 4), len(seq)):
                if seq[k][2] != seq[k - 1][2] and seq[k][2] in ("up", "down"):
                    t, s = seq[k][0], 1 if seq[k][2] == "up" else -1
                    for sym, (D, E) in F.items():
                        i = bisect.bisect_left(D["T"], t)
                        if i < D["n"] and D["T"][i] == t and i >= (210 if full else max(210, D["n"] - 4)):
                            E.setdefault(("W-comp", s), []).append(i)


def gp_build(cdb, coins, keep, pdb, fdb, prog=None, p=None):
    """🏗️ (العامل · بلا شبكة · مرة باليوم بعد إغلاق اليوم) كل عملة بكل إطار على تاريخها (GP_HIST) بالكود نفسه ⇒ قراءات السوق كله على التاريخ
    كله ⇒ مشي العملات (كل العملات معاً · ولكل عملة من عملاتك) ومشي السوق (البيتكوين) ⇒ ما تعرضه اللوحة وأبطال الإشعارات"""
    mkt, fng = _sg_mkt(pdb, fdb), _sg_fng_raw(fdb)
    bd = ((cdb.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    btcd = {int(r[0]): float(r[4]) for r in bd}
    codes = _gp_codes()
    out = {"v": GP_VER, "ts": round(time.time()), "p": dict(GP_P, **(p or {})), "f": {}, "n": {}}
    for k, fr in enumerate(GP_FR):
        sec_ = SG_BAR[fr][0]
        F = {}
        for j, sym in enumerate(coins):
            if prog:
                prog(100.0 * (k * len(coins) + j) / max(1, 3 * len(coins)), f"🧩 {GP_FRN[fr][1]} · {sym.split('-')[0]}")
            rd = ((cdb.get("c") or {}).get(sym) or {}).get("d") or []
            rows = (((cdb.get(sec_) or {}).get(sym) or {}).get("d") or [])[-GP_HIST[fr]:]
            if len(rows) < 300 or len(rd) < 220:
                continue
            F[sym] = _sg_events(rows, fr == "1D", _sg_ctx(sym, rd, pdb, mkt, fng, btcd), t0=210, dx=SG_SEC[fr])
        if "BTC-USDT" not in F:
            continue
        _gp_wide({fr: F}, full=True)
        Db = F["BTC-USDT"][0]
        B = {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}
        out["f"][fr] = {"coin": gp_pack(gp_walk(F, "coin", fr, B=B, p=p, keep=[s for s in keep if s in F], codes=codes)),
                        "mkt": gp_pack(gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=p, codes=codes))}
        out["n"][fr] = [len(F), min(D["T"][0] for D, E in F.values()), Db["T"][-1]]
        F = None
    return out


def gp_now(FF, G, p=None):
    """🔔 الفحص الحي (كل شمعة مغلقة): على آخر شمعة لكل عملة وإطار ⇒ ما انطلق من أبطال كل مجموعة (المحفوظين في آخر بناء) بجهة واحدة
    ⇒ {الإطار: {القسم: {المجموعة: {العملة: [الجهة, الأبطال]}}}} — الدالة نفسها (_gp_keys) التي يُبنى بها السجل"""
    p = dict(GP_P, **(p or {}))
    codes = _gp_codes()
    out = {}
    for fr, F in (FF or {}).items():
        Gf = ((G or {}).get("f") or {}).get(fr) or {}
        for sec in ("coin", "mkt"):
            Gs = (Gf.get(sec) or {}).get("g") or {}
            for g, x in Gs.items():
                if g not in GP_GROUPS or not x.get("ch"):
                    continue
                mem, job = set(gp_members(g, codes)), GP_GROUPS[g]["job"]
                for sym, (D, E) in F.items():
                    if (sec == "mkt" and sym != "BTC-USDT") or (job == "rs" and sym.startswith("BTC-")):
                        continue
                    keys = _gp_keys(_gp_fires(E, mem), D["n"] - 1, mem, SG_LK.get(fr, 2), job, combo=bool(p["combo"]))
                    cs = [k_ for k_ in x["ch"] if k_ in keys]
                    sides = {keys[k_] for k_ in cs}
                    if len(sides) == 1:
                        out.setdefault(fr, {}).setdefault(sec, {}).setdefault(g, {})[sym] = [sides.pop(), cs, D["T"][D["n"] - 1]]
    return out
'''

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    a = "\ndef sg_loop():"
    if s.count(a) != 1 or "def gp_walk(" in s:
        print("❌ anchor not found once (or the engine is already in) — nothing written"); sys.exit(1)
    s = s.replace(a, "\n" + ENGINE + "\n" + a, 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ 🧩 the group engine inserted ({ENGINE.count(chr(10))} lines) · compiles · {p}")
