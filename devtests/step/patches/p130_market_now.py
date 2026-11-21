# 📈 patch 130 (dashboard v3.36.75 · the market now and next — the new analyst, rebuilt from scratch as a trader). The owner (21-11):
#   «كله اريدك تصيغه من جديد واتسوي عليه اختبار حتى لو يطول ساعات … سويه انت كانما خبير تداول … اريد يقلي شديصير بالسوق بالحاضر وشراح
#   يصير للسوق بشكل عام وبالعملات بشكل خاص».
#   The evidence (HANDOFF §٧ر١٦٢): check 13 — every row's next-candle call 1H 47.4% · 4H 47.2% (shuffled 50%) · combos chosen on the past
#   fail unseen · Gemini's four never proven · check 14 — one pooled model on 31 features: direction and vs-Bitcoin Brier skill ≤ 0 for the
#   next 4 hours, tomorrow and the week (said 72% ⇒ was 48%) · THE RANGE 10–90% held the price 80.7–82.0% of the time ✅.
#   · 🔎 the present (facts, measured): the market (Bitcoin's trend and since when · coins above their 50-day mean · alts vs Bitcoin · calm
#     or stormy · fear & greed · the dollar · the stocks' fear) and every coin (daily trend and since when · the short term · vs Bitcoin and
#     its rank · volatility · unusual volume · nearest support, resistance and the busiest price area · accumulation / distribution ·
#     overbought / oversold) — computed in the scan worker (no network) every hour
#   · 🔮 the range: between what and what the price will be after 4 hours, tomorrow and the week (80%) · its live record (every band issued
#     at its frame's close is graded at its end) · NO direction call
#   · facts notifications (the owner turns each on/off): trend change · strength vs Bitcoin · unusual volume · support break / resistance
#     breakout · a move outside the expected range · accumulation / distribution · the market's trend · stormy / calm · a crash · extreme
#     fear / greed — once per event · quiet hours and channel as before · the daily cap inside (12)
#   · the window «📈 السوق — الآن والمتوقع»: 🌐 السوق · 🪙 العملات · 📋 المؤشرات (the tables) · 📜 السجل · ⚙️ الإشعارات — removed: 🧠 المحلل,
#     📚 المجموعات, the % slider, the weekly estimate, the daily summary, the cap and frame buttons, the old analyst notifications and its
#     weekly catalog build · 🔮 loses its «🧠 المحلل» and «🎯» lines (not proven)
#   · display only: no keys, no orders
#   python3 devtests/step/patches/p130_market_now.py Holy_Dashboard.pyw
import os, re, sys

R = [
    ('''APP_VERSION = "3.36.74"''',
     '''APP_VERSION = "3.36.75"'''),
    ('''def sg_loop():
    """''',
     '''# ───────────── 🔎 v3.36.75: الآن في السوق — حقائق تُقاس (لا تنبؤ): السوق كله وكل عملة ─────────────
#   المالك (21-11): «اريد يقلي شديصير بالسوق بالحاضر … للسوق بشكل عام وبالعملات بشكل خاص» — كل سطر رقم من الشموع المحفوظة وقراءات
#   اللوحة (بلا شبكة · في عامل الفحص): الاتجاه ومنذ متى · القوة مقابل البيتكوين · الهدوء والهيجان · الحجم · أقرب دعم ومقاومة ومنطقة أكثر
#   تداول · التجميع والتصريف · التشبع · المزاج والدولار والأسهم · العقود — وكل سطر بحالة (p صعود · n هبوط · z محايد · w انتباه)
AN_TREND = {"up": ("📈", "صاعد"), "down": ("📉", "نازل"), "side": ("↔️", "عرضي")}


def _an_ema(x, n):
    a, out, e = 2.0 / (n + 1), [], None
    for v in x:
        e = v if e is None else e + a * (v - e)
        out.append(e)
    return out


def _an_sd(r):
    if len(r) < 3:
        return 0.0
    m = sum(r) / len(r)
    return math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1))


def _an_lr(C):
    return [math.log(C[i] / C[i - 1]) if C[i] > 0 and C[i - 1] > 0 else 0.0 for i in range(1, len(C))]


def _an_trend_seq(C):
    """حالة الاتجاه لكل يوم: صاعد = فوق متوسط 200 ومتوسط 50 فوقه وصاعد · نازل = العكس · غير ذلك عرضي — وتثبت يومين قبل أن تتغير"""
    e50, e200 = _an_ema(C, 50), _an_ema(C, 200)
    seq, cur, cand, cnt = [], None, None, 0
    for i in range(len(C)):
        if i < 200:
            seq.append(None)
            continue
        sl = e50[i] / e50[i - 10] - 1.0
        raw = "up" if C[i] > e200[i] and e50[i] > e200[i] and sl > 0 else "down" if C[i] < e200[i] and e50[i] < e200[i] and sl < 0 else "side"
        if cur is None:
            cur = raw
        elif raw != cur:
            cand, cnt = (raw, cnt + 1) if raw == cand else (raw, 1)
            if cnt >= 2:
                cur, cand, cnt = raw, None, 0
        else:
            cand, cnt = None, 0
        seq.append(cur)
    return seq, e50, e200


def _an_since(seq):
    s = seq[-1]
    k = 0
    for x in reversed(seq):
        if x != s:
            break
        k += 1
    return s, k


def _an_volstate(C, w=30, look=365):
    """🎢 تذبذب آخر 30 يوماً مقارنةً بأيام السنة: أين يقع (0…100) ⇒ هادئ · عادي · هائج"""
    lr = _an_lr(C)
    if len(lr) < w + 60:
        return None
    vols = [_an_sd(lr[i - w:i]) for i in range(w, len(lr) + 1)][-look:]
    cur = vols[-1]
    pct = 100.0 * sum(1 for v in vols if v < cur) / len(vols)
    return {"pct": round(pct), "ann": round(cur * math.sqrt(365) * 100, 1), "k": "calm" if pct < 25 else "storm" if pct > 75 else "normal"}


def _an_levels(H, L, C, V, px=None, look=30):
    """🧱 أقرب دعم ومقاومة (قيعان وقمم واضحة خلال الشهر — كل واحدة أدنى/أعلى من يومين قبلها وبعدها) + منطقة أكثر تداول"""
    n = len(C)
    if n < look + 5:
        return None
    px = px or C[-1]
    lows, highs = [], []
    for i in range(max(2, n - look), n - 2):
        if L[i] <= min(L[i - 2:i + 3]):
            lows.append(L[i])
        if H[i] >= max(H[i - 2:i + 3]):
            highs.append(H[i])
    sup = max([x for x in lows if x < px * 0.998] or [min(L[-look:])])
    res = min([x for x in highs if x > px * 1.002] or [max(H[-look:])])
    lo, hi = min(L[-look:]), max(H[-look:])
    poc = None
    if hi > lo:
        bins = [0.0] * 24
        for i in range(n - look, n):
            k = min(23, int((C[i] - lo) / (hi - lo) * 24))
            bins[k] += V[i]
        b = max(range(24), key=lambda j: bins[j])
        poc = lo + (b + 0.5) * (hi - lo) / 24
    return {"sup": sup, "res": res, "poc": poc, "lo": lo, "hi": hi,
            "ds": round((sup / px - 1) * 100, 1) if sup < px else None, "dr": round((res / px - 1) * 100, 1) if res > px else None}


def _an_rsi(C, n=14):
    if len(C) < n * 3:
        return None
    up = dn = 0.0
    a = 1.0 / n
    for i in range(1, len(C)):
        d = C[i] - C[i - 1]
        up += a * (max(d, 0.0) - up)
        dn += a * (max(-d, 0.0) - dn)
    return 100.0 - 100.0 / (1.0 + up / max(dn, 1e-12))


def _an_coin(sym, cdb, btc_d, uni_rs):
    """🪙 العملة الآن: [(الأيقونة · السطر · الحالة)] + الأرقام"""
    d = ((cdb.get("c") or {}).get(sym) or {}).get("d") or []
    h1 = ((cdb.get("c1") or {}).get(sym) or {}).get("d") or []
    if len(d) < 220:
        return None
    T, O, H, L, C, V = ([float(r[k]) for r in d] for k in range(6))
    px = float(h1[-1][4]) if h1 else C[-1]
    ch24 = (px / float(h1[-25][4]) - 1) * 100 if len(h1) >= 25 else (C[-1] / C[-2] - 1) * 100
    ch7 = (px / C[-8] - 1) * 100
    seq, e50, e200 = _an_trend_seq(C)
    tr, days = _an_since(seq)
    out = {"sym": sym, "px": px, "ch24": round(ch24, 2), "ch7": round(ch7, 2), "trend": tr, "days": days, "lines": []}
    ic, nm = AN_TREND.get(tr, ("↔️", "عرضي"))
    where = "فوق" if C[-1] > e200[-1] else "تحت"
    out["lines"].append((ic, f"الاتجاه اليومي: {nm} منذ {_sg_ar(days, 'day')} — السعر {where} متوسط 200 يوم", {"up": "p", "down": "n"}.get(tr, "z")))
    h4 = ((cdb.get("c4") or {}).get(sym) or {}).get("d") or []
    if len(h4) >= 60:
        c4 = [float(r[4]) for r in h4]
        e20 = _an_ema(c4, 20)
        s4 = "صاعد" if c4[-1] > e20[-1] and e20[-1] > e20[-6] else "نازل" if c4[-1] < e20[-1] and e20[-1] < e20[-6] else "متردد"
        out["short"] = s4
        out["lines"].append(("⏱", f"على المدى القصير (4 ساعات): {s4}", {"صاعد": "p", "نازل": "n"}.get(s4, "z")))
    if btc_d and not sym.startswith("BTC-"):
        bm = {int(r[0]): float(r[4]) for r in btc_d}
        b7, b30 = bm.get(int(T[-8])), bm.get(int(T[-31])) if len(T) > 31 else None
        bn = bm.get(int(T[-1]))
        if b7 and b30 and bn:
            r7 = (C[-1] / C[-8] - bn / b7) * 100
            r30 = (C[-1] / C[-31] - bn / b30) * 100
            rk = None
            if uni_rs:
                rk = round(100.0 * sum(1 for x in uni_rs if x < r30) / len(uni_rs))
            out.update(rs7=round(r7, 1), rs30=round(r30, 1), rsk=rk)
            k = "p" if r7 > 0 and r30 > 0 else "n" if r7 < 0 and r30 < 0 else "z"
            word = "أقوى من" if k == "p" else "أضعف من" if k == "n" else "قريبة من"
            out["lines"].append(("💪", f"مقابل البيتكوين: {word} البيتكوين — أسبوع {r7:+.1f}% · شهر {r30:+.1f}%"
                                 + (f" · أقوى من {rk}% من العملات خلال الشهر" if rk is not None else ""), k))
    vs = _an_volstate(C)
    if vs:
        out["vol"] = vs
        word = {"calm": "هادئة", "storm": "هائجة", "normal": "عادية الحركة"}[vs["k"]]
        out["lines"].append(("🎢", f"التذبذب: {word} — أهدأ من {100 - vs['pct']}% من أيام السنة" if vs["k"] != "storm" else
                             f"التذبذب: {word} — أعلى من {vs['pct']}% من أيام السنة", "w" if vs["k"] == "storm" else "z"))
    if len(h1) >= 24 and len(V) >= 22:
        v24 = sum(float(r[5]) for r in h1[-24:])
        avg = sum(V[-21:-1]) / 20.0
        if avg > 0:
            x = v24 / avg
            out["volx"] = round(x, 2)
            if x >= 1.6 or x <= 0.5:
                out["lines"].append(("📊", f"الحجم: آخر 24 ساعة ×{x:.1f} من المعتاد" + (" — نشاط غير عادي" if x >= 1.6 else " — تداول خفيف"),
                                     "w" if x >= 1.6 else "z"))
    lv = _an_levels(H, L, C, V, px)
    if lv:
        out["lv"] = lv
        bits = []
        if lv["ds"] is not None:
            bits.append(f"أقرب دعم {_px_s(lv['sup'])} ({lv['ds']:+.1f}%)")
        if lv["dr"] is not None:
            bits.append(f"أقرب مقاومة {_px_s(lv['res'])} ({lv['dr']:+.1f}%)")
        if lv["poc"]:
            bits.append(f"منطقة أكثر تداول {_px_s(lv['poc'])}")
        out["lines"].append(("🧱", " · ".join(bits), "z"))
    try:
        S = _xc_ad(T, H, L, C, V)
        q = _xc_ad_at(len(C) - 1, S, C)
        if q and q[0] in ("acc", "dist", "up", "down"):
            txt = {"acc": "تجميع — السيولة تدخل والسعر لم يتحرك بعد", "dist": "تصريف — السيولة تخرج والسعر لم ينزل بعد",
                   "up": "صعود مدعوم بدخول السيولة", "down": "نزول مدعوم بخروج السيولة"}[q[0]]
            out["ad"] = q[0]
            out["lines"].append(("🧲", f"السيولة: {txt}", {"acc": "p", "up": "p", "dist": "n", "down": "n"}[q[0]]))
    except Exception:
        pass
    r = _an_rsi(C)
    if r is not None:
        out["rsi"] = round(r)
        if r >= 70 or r <= 30:
            out["lines"].append(("🌡️", f"قوة الشراء اليومية {round(r)} من 100 — " + ("مشتراة بكثرة (قد تهدأ)" if r >= 70 else "مبيعة بكثرة (قد ترتد)"), "w"))
    return out


def an_present(cdb, pdb=None, fdb=None, coins=None):
    """🔎 الآن في السوق كله ولكل عملة — من الشموع المحفوظة وقراءات اللوحة (لا شبكة)"""
    allc = [s for s, e in (cdb.get("c") or {}).items() if len((e or {}).get("d") or []) >= 220]
    btc_d = ((cdb.get("c") or {}).get("BTC-USDT") or {}).get("d") or []
    uni_rs = []
    if btc_d:
        bm = {int(r[0]): float(r[4]) for r in btc_d}
        for s in allc:
            d = (cdb["c"][s] or {}).get("d") or []
            if len(d) > 31 and not s.startswith("BTC-"):
                b0, b1 = bm.get(int(d[-31][0])), bm.get(int(d[-1][0]))
                if b0 and b1:
                    uni_rs.append((float(d[-1][4]) / float(d[-31][4]) - b1 / b0) * 100)
    out = {"t": round(time.time()), "coins": {}, "mkt": None}
    for s in (coins or allc):
        c = _safe(_an_coin, s, cdb, btc_d, uni_rs, default=None)
        if c:
            out["coins"][s] = c
    M = {"lines": []}
    b = _safe(_an_coin, "BTC-USDT", cdb, None, None, default=None) if btc_d else None
    if b:
        M.update(btc=b["px"], ch24=b["ch24"], ch7=b["ch7"], trend=b["trend"], days=b["days"])
        ic, nm = AN_TREND.get(b["trend"], ("↔️", "عرضي"))
        M["lines"].append((ic, f"اتجاه السوق (البيتكوين): {nm} منذ {_sg_ar(b['days'], 'day')} · 24 ساعة {b['ch24']:+.2f}% · أسبوع {b['ch7']:+.2f}%",
                           {"up": "p", "down": "n"}.get(b["trend"], "z")))
    up24, above, n_ = 0, 0, 0
    beat = 0
    movers = []
    for s in allc:
        d = cdb["c"][s]["d"]
        h1 = ((cdb.get("c1") or {}).get(s) or {}).get("d") or []
        C = [float(r[4]) for r in d]
        n_ += 1
        m50 = sum(C[-50:]) / 50.0
        above += 1 if C[-1] > m50 else 0
        ch = (float(h1[-1][4]) / float(h1[-25][4]) - 1) * 100 if len(h1) >= 25 else (C[-1] / C[-2] - 1) * 100
        up24 += 1 if ch > 0 else 0
        movers.append((ch, s))
    if n_ >= 5:
        M.update(n=n_, above=above, up24=up24)
        sh = above / n_
        M["lines"].append(("📊", f"العملات: {above} من {_sg_ar(n_, 'coin')} فوق متوسط 50 يوماً ({round(100 * sh)}%) · {up24} منها صعدت خلال 24 ساعة",
                           "p" if sh >= 0.6 else "n" if sh <= 0.4 else "z"))
        if uni_rs:
            beat = sum(1 for x in uni_rs if x > 0)
            M["beat"] = beat
            M["lines"].append(("💪", f"البيتكوين مقابل العملات: {beat} من {_sg_ar(len(uni_rs), 'coin')} أقوى منه خلال الشهر — "
                               + ("موسم العملات البديلة" if beat / len(uni_rs) >= 0.7 else "البيتكوين يقود" if beat / len(uni_rs) <= 0.3 else "متوازن"), "z"))
        movers.sort()
        M["top"] = [[s, round(c, 2)] for c, s in movers[-3:][::-1]]
        M["bottom"] = [[s, round(c, 2)] for c, s in movers[:3]]
    if b and b.get("vol"):
        v = b["vol"]
        word = {"calm": "هادئ", "storm": "هائج", "normal": "عادي"}[v["k"]]
        M["vk"] = v["k"]
        M["lines"].append(("🎢", f"حركة السوق: {word} — تذبذب البيتكوين أعلى من {v['pct']}% من أيام السنة", "w" if v["k"] == "storm" else "z"))
    try:
        f = ((fdb or {}).get("fng") or {}).get("d") or {}
        ks = sorted(int(x) for x in f)
        if ks:
            v, v7 = float(f[str(ks[-1])]), float(f[str(ks[-8])]) if len(ks) >= 8 else None
            word = "خوف شديد" if v <= 20 else "خوف" if v <= 40 else "طمع شديد" if v >= 80 else "طمع" if v >= 60 else "محايد"
            M["fng"] = v
            M["lines"].append(("😨" if v < 45 else "🤑" if v > 55 else "😐", f"مزاج السوق: {word} ({round(v)} من 100)" + (f" · قبل أسبوع {round(v7)}" if v7 is not None else ""),
                               "w" if v <= 20 or v >= 80 else "z"))
    except Exception:
        pass
    for k, nm, good in (("dxy", "مؤشر الدولار", -1), ("vix", "مقياس خوف الأسهم الأمريكية", -1)):
        try:
            ks, vs = _pro_sorted((pdb or {}).get(k))
            if len(vs) >= 6:
                ch = (vs[-1] / vs[-6] - 1) * 100
                M["lines"].append(("💱" if k == "dxy" else "😱", f"{nm}: {vs[-1]:.2f} ({ch:+.1f}% خلال 5 أيام)"
                                   + (" — يضغط على العملات الرقمية عادة" if ch * good < -1 else " — يساعد العملات الرقمية عادة" if ch * good > 1 else ""),
                                   "n" if ch * good < -1 else "p" if ch * good > 1 else "z"))
        except Exception:
            pass
    out["mkt"] = M
    return out


AN_TY = {   # 📈 v3.36.75: تنبيهات الحقائق — (الأيقونة · الاسم · المجموعة) · لا توقّع اتجاه (لم يغلب الصدفة في الفحصين 13 و14)
    "trend": ("📈", "تغيّر الاتجاه", "coin"), "rs": ("💪", "القوة مقابل البيتكوين", "coin"), "vol": ("📊", "حجم غير عادي", "coin"),
    "lvl": ("🧱", "كسر دعم أو اختراق مقاومة", "coin"), "out": ("⚡", "حركة خارج المدى المتوقع", "coin"), "ad": ("🧲", "التجميع والتصريف", "coin"),
    "mtrend": ("🧭", "تغيّر اتجاه السوق", "mkt"), "storm": ("🎢", "السوق هاج أو هدأ", "mkt"), "wave": ("🌊", "انهيار السوق كله", "mkt"),
    "fng": ("😨", "خوف أو طمع شديد", "mkt")}


# ───────────── 🔮 المدى المتوقع (المثبت بالفحص 14: احتوى السعر 80–82% من المرات) + سجله الحي ─────────────
AN_FILE = os.path.join(ROOT, "Holy_Market.json")
AN_HZ = (("4h", "c1", 4, 3600, "الساعات الأربع القادمة"), ("1d", "c4", 6, 14400, "غداً"), ("1w", "c", 7, 86400, "الأسبوع القادم"))
AN_Z = 1.2816                                   # 80% (10% … 90%)
_AN = {"lock": threading.Lock()}


def _an_range(cdb, sym, px):
    """لكل مدة: التذبذب (آخر 48 شمعة من إطارها) × √المدة ⇒ بين كم وكم بثقة 80% — {مفتاح: {lo, hi, w%}}"""
    out = {}
    for k, sec, h, step, _nm in AN_HZ:
        rows = ((cdb.get(sec) or {}).get(sym) or {}).get("d") or []
        if len(rows) < 60 or not px:
            continue
        C = [float(r[4]) for r in rows[-49:]]
        sd = _an_sd(_an_lr(C))
        if sd <= 0:
            continue
        w = AN_Z * sd * math.sqrt(h)
        out[k] = {"lo": px * math.exp(-w), "hi": px * math.exp(w), "w": round((math.exp(w) - 1) * 100, 2), "t": int(rows[-1][0]) + step}
    return out


def an_scan(cdb, pdb, fdb, coins):
    """🔎 + 🔮 في عامل الفحص (بلا شبكة): الآن لكل عملة وللسوق + المدى المتوقع لكل مدة"""
    P = an_present(cdb, pdb, fdb, coins)
    for s, c in P["coins"].items():
        c["rng"] = _an_range(cdb, s, c["px"])
    if P.get("mkt") and P["mkt"].get("btc"):
        P["mkt"]["rng"] = _an_range(cdb, "BTC-USDT", P["mkt"]["btc"])
    return P


def _an_load():
    A = _safe(load_json, AN_FILE, default=None)
    if not isinstance(A, dict) or A.get("v") != 1:
        A = {"v": 1, "since": round(time.time()), "rec": {}, "pend": [], "now": None, "sent": {}}
    for k, d in (("rec", {}), ("pend", []), ("sent", {})):
        if not isinstance(A.get(k), type(d)):
            A[k] = d
    return A


def _an_grade(A, cdb, now):
    """✅ كل مدى سُجّل يُحكم عند نهاية مدته (إغلاق شمعة الساعة التي تنتهي فيها): السعر داخله ⇒ صدق · خارجه ⇒ خرج"""
    keep, T = [], {}
    for it in A["pend"]:
        try:
            sym, k, lo, hi, t_end = str(it[0]), str(it[1]), float(it[2]), float(it[3]), int(it[4])
        except Exception:
            continue
        if sym not in T:
            rows = ((cdb.get("c1") or {}).get(sym) or {}).get("d") or []
            T[sym] = {int(r[0]) + 3600: float(r[4]) for r in rows[-400:]}
        px = T[sym].get(t_end)
        if px is None:
            if now - t_end < 3 * 86400:
                keep.append(it)
            continue
        r = A["rec"].setdefault(k, [0, 0])
        r[0 if lo <= px <= hi else 1] += 1
        if sym == "BTC-USDT":
            rb = A["rec"].setdefault("btc_" + k, [0, 0])
            rb[0 if lo <= px <= hi else 1] += 1
    A["pend"] = keep[-4000:]


def _an_issue(A, P, frs, now):
    """📝 يُسجَّل المدى عند إغلاق شمعة إطاره فقط (4 ساعات ⇐ شمعة 4 ساعات · غداً ⇐ اليومية · الأسبوع ⇐ يومية الاثنين) — مدد لا تتداخل"""
    want = {"4h": "4H" in frs, "1d": "1D" in frs, "1w": "1D" in frs and datetime.utcfromtimestamp(now).weekday() == 0}
    have = {(p[0], p[1], p[4]) for p in A["pend"]}
    for s, c in (P.get("coins") or {}).items():
        for k, band in (c.get("rng") or {}).items():
            h = {"4h": 4 * 3600, "1d": 86400, "1w": 7 * 86400}[k]
            if not want.get(k):
                continue
            t_end = int(now) // 3600 * 3600 + h
            if (s, k, t_end) not in have:
                A["pend"].append([s, k, band["lo"], band["hi"], t_end])


def _an_facts(prev, P, rng_prev, mine, types, crash, lvd=None):
    """📨 إشعارات الحقائق: ما تغيّر بين لقطتين (الاتجاه · القوة · الحجم · كسر المستويات · الخروج عن المدى · السيولة · السوق) —
    [(مفتاح التكرار، كتلة)]"""
    out = []
    pc = (prev or {}).get("coins") or {}
    for s in mine:
        c, o = (P.get("coins") or {}).get(s), pc.get(s)
        if not c or not o:
            continue
        b = s.split("-")[0]
        if types.get("trend", True) and c.get("trend") != o.get("trend") and c.get("trend") in ("up", "down"):
            ic, nm = AN_TREND[c["trend"]]
            out.append((f"trend|{s}|{c['trend']}", {"sym": s, "ty": "trend", "t": f"{ic} {b}: الاتجاه اليومي أصبح {nm}",
                        "b": next((x[1] for x in c["lines"] if x[0] in ("📈", "📉", "↔️")), "")}))
        if types.get("rs", True) and o.get("rs7") is not None and c.get("rs7") is not None and c.get("rs30") is not None:
            was, now_ = (o["rs7"] > 0 and (o.get("rs30") or 0) > 0) - (o["rs7"] < 0 and (o.get("rs30") or 0) < 0), (c["rs7"] > 0 and c["rs30"] > 0) - (c["rs7"] < 0 and c["rs30"] < 0)
            if now_ and now_ != was:
                out.append((f"rs|{s}|{now_}", {"sym": s, "ty": "rs", "t": f"💪 {b}: أصبحت {'أقوى' if now_ > 0 else 'أضعف'} من البيتكوين",
                            "b": f"خلال أسبوع {c['rs7']:+.1f}% · خلال شهر {c['rs30']:+.1f}% مقارنةً بالبيتكوين"}))
        if types.get("vol", True) and (c.get("volx") or 0) >= 2.0 and (o.get("volx") or 0) < 2.0:
            out.append((f"vol|{s}", {"sym": s, "ty": "vol", "t": f"📊 {b}: حجم تداول غير عادي ×{c['volx']:.1f}",
                        "b": f"تداول آخر 24 ساعة ×{c['volx']:.1f} من المعتاد · السعر {_px_s(c['px'])} ({c['ch24']:+.2f}% خلال 24 ساعة)"}))
        lv = (lvd or {}).get(s) or {}                        # الكسر يُحسب على إغلاق اليوم فقط ومن مستويات أمس (لا ذيول الساعة)
        if types.get("lvl", True) and lvd is not None and lv.get("px"):
            if lv.get("res") and c["px"] > float(lv["res"]) * 1.003 and float(lv["px"]) <= float(lv["res"]):
                out.append((f"lvl|{s}|r|{lv['res']:.6g}", {"sym": s, "ty": "lvl", "t": f"🧱 {b}: اخترق المقاومة {_px_s(lv['res'])}",
                            "b": f"أغلق اليوم على {_px_s(c['px'])} — فوق أعلى قمة واضحة خلال الشهر"}))
            if lv.get("sup") and c["px"] < float(lv["sup"]) * 0.997 and float(lv["px"]) >= float(lv["sup"]):
                out.append((f"lvl|{s}|s|{lv['sup']:.6g}", {"sym": s, "ty": "lvl", "t": f"🧱 {b}: كسر الدعم {_px_s(lv['sup'])}",
                            "b": f"أغلق اليوم على {_px_s(c['px'])} — تحت أدنى قاع واضح خلال الشهر"}))
        rp = ((rng_prev or {}).get(s) or {}).get("4h")
        if types.get("out", True) and rp and (c["px"] > rp["hi"] or c["px"] < rp["lo"]):
            up = c["px"] > rp["hi"]
            out.append((f"out|{s}|{rp['t']}", {"sym": s, "ty": "out", "t": f"⚡ {b}: {'صعد' if up else 'نزل'} أكثر من المتوقع",
                        "b": f"السعر {_px_s(c['px'])} خارج المدى المتوقع للساعات الأربع ({_px_s(rp['lo'])} – {_px_s(rp['hi'])}) — حركة غير عادية"}))
        if types.get("ad", True) and c.get("ad") in ("acc", "dist") and c.get("ad") != o.get("ad"):
            out.append((f"ad|{s}|{c['ad']}", {"sym": s, "ty": "ad", "t": f"🧲 {b}: {'تجميع' if c['ad'] == 'acc' else 'تصريف'}",
                        "b": next((x[1] for x in c["lines"] if x[0] == "🧲"), "")}))
    M, Mo = P.get("mkt") or {}, (prev or {}).get("mkt") or {}
    if types.get("mtrend", True) and M.get("trend") and Mo.get("trend") and M["trend"] != Mo["trend"] and M["trend"] in ("up", "down"):
        ic, nm = AN_TREND[M["trend"]]
        out.append((f"mtrend|{M['trend']}", {"sym": "السوق", "ty": "mtrend", "t": f"{ic} السوق: اتجاه البيتكوين اليومي أصبح {nm}",
                    "b": M["lines"][0][1] if M.get("lines") else ""}))
    if types.get("storm", True) and M.get("vk") and Mo.get("vk") and (M["vk"] == "storm") != (Mo["vk"] == "storm"):
        out.append((f"storm|{M['vk']}", {"sym": "السوق", "ty": "storm", "t": "🎢 السوق " + ("هاج" if M["vk"] == "storm" else "هدأ"),
                    "b": next((x[1] for x in M.get("lines") or [] if x[0] == "🎢"), "")}))
    if types.get("wave", True) and crash and crash.get("on"):
        out.append((f"wave|crash|{crash.get('t')}", {"sym": "السوق", "ty": "wave", "t": "🌊 انهيار في السوق كله",
                    "b": f"{crash.get('k')} من {_sg_ar(crash.get('n') or 0, 'coin')} هبطت بقوة غير معتادة في الشمعة نفسها (4 ساعات)"}))
    f, fo = M.get("fng"), Mo.get("fng")
    if types.get("fng", True) and f is not None and fo is not None and ((f <= 20 < fo) or (f >= 80 > fo)):
        out.append((f"fng|{'f' if f <= 20 else 'g'}", {"sym": "السوق", "ty": "fng", "t": f"{'😨' if f <= 20 else '🤑'} مزاج السوق: {'خوف شديد' if f <= 20 else 'طمع شديد'} ({round(f)})",
                    "b": "الخوف الشديد سبق ارتدادات في الماضي أحياناً، والطمع الشديد سبق تراجعات — قراءة للمزاج لا أمر"}))
    return out


def an_feed(sc, frs, cdb, now, cfg, st, send=True):
    """📈 بعد كل فحص: يحفظ «الآن» والمدى · يحكم المدى القديم · ويرسل إشعارات ما تغيّر (مرة لكل حدث · ساعات الهدوء والقناة كالمعتاد)"""
    P = (sc or {}).get("an")
    if not isinstance(P, dict) or not P.get("coins"):
        return []
    with _AN["lock"]:
        A = _an_load()
        _an_grade(A, cdb, now)
        prev, rng_prev = A.get("now"), {s: c.get("rng") for s, c in ((A.get("now") or {}).get("coins") or {}).items()}
        _an_issue(A, P, frs, now)
        daily = "1D" in frs
        facts = _an_facts(prev, P, rng_prev, sg_coins(cfg), cfg.get("atypes") or {}, (sc or {}).get("crash") if "4H" in frs else None,
                          (A.get("lvd") or {}) if daily else None) if prev else []
        A["now"] = P
        if daily:                                            # مستويات إغلاق اليوم — مرجع كسر الغد
            A["lvd"] = {s: {"px": c.get("px"), "res": (c.get("lv") or {}).get("res"), "sup": (c.get("lv") or {}).get("sup")}
                        for s, c in (P.get("coins") or {}).items() if c.get("px")}
        blocks = []
        for key, b in facts:
            if now - float(A["sent"].get(key) or 0) < 20 * 3600:
                continue
            A["sent"][key] = round(now)
            blocks.append(dict(b, f=""))
        for k in [k for k, v in A["sent"].items() if now - float(v) > 7 * 86400]:
            A["sent"].pop(k, None)
        A["ts"] = round(now)
        save_json_atomic(AN_FILE, A)
    return blocks


def an_view():
    """📈 GET /api/market — الآن والمدى لكل عملة من عملاتك وللسوق + صدق المدى الحي"""
    A = _an_load()
    P = A.get("now") or {}
    mine = sg_coins()
    rec = {k: {"in": v[0], "out": v[1], "p": round(100.0 * v[0] / max(1, v[0] + v[1]), 1)} for k, v in (A.get("rec") or {}).items()}
    return {"ok": True, "t": P.get("t"), "since": A.get("since"), "mkt": P.get("mkt"), "coins": [P["coins"][s] for s in mine if s in (P.get("coins") or {})],
            "mine": mine, "missing": [s for s in mine if s not in (P.get("coins") or {})], "rec": rec,
            "hz": [[k, nm] for k, _sec, _h, _st, nm in AN_HZ], "z": 80}


def sg_loop():
    """'''),
    ("""    return {"ok": True, "c": res, "crash": crash, "ts": time.time()}""",
     """    an = _safe(an_scan, cdb, pdb, fdb, coins, default=None)          # 📈 v3.36.75: الآن والمدى المتوقع لكل عملة وللسوق
    return {"ok": True, "c": res, "crash": crash, "ts": time.time(), "an": an}"""),
    ("""                cf = cfg if cfg["on"] else dict(cfg, types={k: False for k in SG_TY})
                if cat and any(f in SG_FR for f in due):
                    res = _sg_grade(st, cdb or {}, cat, now)
                    blocks = _sg_process(sc, [f for f in due if f in SG_FR], st, cf, cat, cdb, now)
                    if res and cf["types"].get("res", True):
                        rb = _sg_res_block(res, st, cat)
                        if rb:
                            blocks.append(rb)
                comp = st.get("comp")
                if st.pop("comp_new", None) and comp and cf["types"].get("mkt", True):
                    blocks.insert(0, _sg_comp_block(comp))""",
     """                blocks = _safe(an_feed, sc, due, cdb or {}, now, cfg, st, default=[]) or []     # 📈 v3.36.75: تنبيهات الحقائق (بدل المحلل القديم)
                st.pop("comp_new", None)"""),
    ("""        build_now = need_cat and not _SG.get("build") and now - float(st.get("cat_try") or 0) > (6 * 3600 if cat and not st.get("cat_force") else 600)""",
     """        build_now = False                                    # 📈 v3.36.75: دليل المحلل القديم لا يُبنى (المحلل الجديد: حقائق + المدى المثبت)"""),
    ('''note = f"🔕 وصلت حد إشعارات المحلل اليوم ({cfg['cap']}) — الباقي في نافذة 📊 المؤشرات"''',
     '''note = f"🔕 وصلت حد تنبيهات السوق اليوم ({cfg['cap']}) — الباقي في نافذة 📈 السوق"'''),
    ('text = f"🧠 المحلل — إشعارات جديدة ({len(out)})\\n\\n"',
     'text = f"📈 السوق — تنبيهات جديدة ({len(out)})\\n\\n"'),
    ('text = f"🌙 إشعارات المحلل أثناء ساعات الهدوء ({len(q)})\\n\\n"',
     'text = f"🌙 تنبيهات السوق أثناء ساعات الهدوء ({len(q)})\\n\\n"'),
    ("""غيرها في نافذة 📊 المؤشرات" if len(q) > 15""",
     """غيرها في نافذة 📈 السوق" if len(q) > 15"""),
    ("""<div class="mbtns"><button onclick="openInd('ind')">🎯 المؤشرات</button><button onclick="openGuide('','fc')">""",
     """<div class="mbtns"><button onclick="openInd('coins')">📈 السوق</button><button onclick="openInd('ind')">📋 المؤشرات</button><button onclick="openGuide('','fc')">"""),
    ("""  if(k==='sig')return openSig('ind');                            // 🎯 v3.36.66 · v3.36.71: «🎯 المؤشرات»""",
     """  if(k==='sig')return openSig('coins');                          // 📈 v3.36.75: تنبيهات السوق ⇒ عملاتك الآن (قبلها 🎯 v3.36.66 · v3.36.71)"""),
    ('''"coins": coins, "cap": iv("sg_cap", 8, 0, 100),''',
     '''"coins": coins, "cap": 12,      # 📈 v3.36.75: الحد اليومي داخلي'''),
    ('''"quiet": qh, "sum": (int(sm) % 24) if isinstance(sm, (int, float)) and not isinstance(sm, bool) else None,''',
     '''"quiet": qh, "sum": None,      # 📈 v3.36.75: لا ملخص يومي'''),
    ('''"ch": ch if ch in SG_CH else "both", "fr": {f: bool(fr.get(f, True)) for f in SG_FR}}''',
     '''"ch": ch if ch in SG_CH else "both", "fr": {f: bool(fr.get(f, True)) for f in SG_FR},
            "atypes": {k: bool((c.get("an_types") if isinstance(c.get("an_types"), dict) else {}).get(k, True)) for k in AN_TY}}'''),
    ("""    if isinstance(v.get("fr"), dict):
        f = dict(c.get("sg_fr") or {})""",
     """    if isinstance(v.get("atypes"), dict):                                   # 📈 v3.36.75: تنبيهات الحقائق
        t = dict(c.get("an_types") or {})
        t.update({k: bool(x) for k, x in v["atypes"].items() if k in AN_TY})
        c["an_types"] = t
    if isinstance(v.get("fr"), dict):
        f = dict(c.get("sg_fr") or {})"""),
    ("""    msg = ((f"🎯 إشعارات المحلل مفعّلة — لا يصلك إلا ما صدق في {p['thr']}% من المرات أو أكثر · " + SG_CH[p["ch"]]) if p["on"]
           else "🔕 إشعارات المحلل متوقفة")""",
     '''    msg = ("📈 تنبيهات السوق مفعّلة · " + SG_CH[p["ch"]]) if p["on"] else "🔕 تنبيهات السوق متوقفة"'''),
    ('''        msg = "↩️ عملات إشعارات المحلل الآن نفس عملات الشريط"''',
     '''        msg = "↩️ عملات تنبيهات السوق الآن نفس عملات الشريط"'''),
    ('''" — تُجلب بياناتها بالخلفية وتظهر إشاراتها بعد إغلاق الشمعة القادمة"''',
     '''" — تُجلب بياناتها بالخلفية وتظهر في «📈 السوق» بعد الفحص القادم"'''),
    ("""    v = {"ok": True, "cfg": cfg, "types": {k: list(x) for k, x in SG_TY.items()},""",
     """    v = {"ok": True, "cfg": cfg, "types": {k: list(x) for k, x in SG_TY.items()}, "atypes": {k: list(x) for k, x in AN_TY.items()},"""),
    ('    text = (f"🧪 تجربة — 🟢 شراء — {sym} · يومي\\nاتفقت 3 إشارات: Supertrend انقلب أخضر فوق EMA 150 · تقاطع MACD صاعد فوق EMA 20 · 💧 تدفق السيولة (CMF): صاعد\\n"\n            f"📊 هكذا يصلك السجل: كم مرة صدقت من كم مرة · والعشوائي للمقارنة · والمتوسط بعد المدة\\n"\n            f"⚙️ إعداداتك: {cfg[\'thr\']}% فأكثر · {_sg_ar(cfg[\'min\'], \'time\')} فأكثر · {SG_CH[cfg[\'ch\']]}")',
     '    text = (f"🧪 تجربة — 🧱 {sym.split(\'-\')[0]}: اخترق المقاومة\\nهكذا يصلك التنبيه: ما حدث فعلاً بالأرقام — لا توقّع اتجاه ولا أمر\\n"\n            f"⚙️ {SG_CH[cfg[\'ch\']]}")'),
    ("""        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح""",
     """        if u.path == "/api/market":                       # 📈 v3.36.75: السوق — الآن والمدى المتوقع (من الملف · لا ينتظر الحساب)
            return self._json(_safe(an_view, default={"ok": False, "msg": "تعذّر تحميل السوق"}))
        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح"""),
    (""".sb-tabs,.sb-sort{""",
     """.an-card{border:1px solid var(--bd);border-radius:12px;padding:8px 10px;margin:8px 0;background:var(--bg1)}.an-coin{cursor:pointer}
.an-h{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:4px}.an-h small{color:var(--mut)}
.an-l{display:flex;gap:6px;align-items:flex-start;font-size:12.5px;line-height:1.7;padding:1px 0}.an-ic{min-width:20px;text-align:center}
.an-l.up{color:var(--green)}.an-l.dn{color:var(--red)}.an-l.warn{color:var(--amber)}
.an-rng{margin-top:6px;border-top:1px dashed var(--bd);padding-top:6px}.an-rh{font-size:12px;color:var(--mut);margin-bottom:2px}
.an-rr{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;font-size:12.5px;padding:2px 0}.an-rr span{min-width:120px;color:var(--mut)}.an-rr small{color:var(--mut)}
.an-mvs{display:flex;gap:6px;flex-wrap:wrap;margin:3px 0}.an-mv{border:1px solid var(--bd);border-radius:999px;padding:2px 8px;font-size:12px}.an-mv.up{color:var(--green)}.an-mv.dn{color:var(--red)}
.sb-tabs,.sb-sort{"""),
    ("""async function openInd(tab){SGTAB=tab==='now'?'ind':(tab||'an');""",
     """async function openInd(tab){SGTAB=({now:'coins',an:'mkt',cat:'ind'})[tab]||tab||'mkt';     // 📈 v3.36.75: السوق — الآن والمتوقع"""),
    ("""showModal(`<h2>📊 المؤشرات — المحلل</h2>""",
     """showModal(`<h2>📈 السوق — الآن والمتوقع</h2>"""),
    ("""let SGV=null,SGT=null,SGTAB='an',""",
     """let SGV=null,SGT=null,SGTAB='mkt',"""),
    ("""async function openSig(tab){return openInd(tab==='now'?'ind':(tab||'an'))}""",
     """async function openSig(tab){return openInd(tab)}"""),
    ("""sgRender();if(SGTAB==='cat')sgCat();if(SGTAB==='ind'){if(!INDV)sgIndLoad();if(!SBV)sbLoad()}""",
     """sgRender();anLoad();if(SGTAB==='ind'){if(!INDV)sgIndLoad();if(!SBV)sbLoad()}"""),
    ("""function sgTab(t){SGTAB=t==='now'?'ind':t;sgRender();if(SGTAB==='cat')sgCat();if(SGTAB==='ind'){sgIndLoad();sbLoad()}}""",
     """function sgTab(t){SGTAB=({now:'coins',an:'mkt',cat:'ind'})[t]||t;sgRender();if(['mkt','coins','log'].includes(SGTAB))anLoad();if(SGTAB==='ind'){sgIndLoad();sbLoad()}}"""),
    ("""  if(tb)tb.innerHTML=[['an','🧠 المحلل'],['ind','🎯 المؤشرات'],['cat','📚 المجموعات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']].map(""",
     """  if(tb)tb.innerHTML=[['mkt','🌐 السوق'],['coins','🪙 العملات'],['ind','📋 المؤشرات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']].map("""),
    ("""  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل المحلل';return}""",
     """  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل السوق';return}"""),
    ("""  el.innerHTML=SGTAB==='an'?sgAn(V):SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgInd(V)}""",
     """  el.innerHTML=SGTAB==='mkt'?anMkt():SGTAB==='coins'?anCoins():SGTAB==='log'?anLog(V):SGTAB==='cfg'?sgCfg(V):sgInd(V)}"""),
    ("""+L('🎯','المؤشرات وإشعارات المحلل',"openSig('cfg')",'شراء · بيع · تجميع · صعود · نزول · السوق — بنسبتك'))}""",
     """+L('📈','تنبيهات السوق',"openSig('cfg')",'الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · السوق'))}"""),
    ("""<span class="ind-chip">🎯 نفس المؤشرات بأسمائها في «🎯 المؤشرات» + 🧠 المحلل</span>""",
     """<span class="ind-chip">🎯 نفس المؤشرات بأسمائها</span>"""),
]
FN = {
    'sgFcTop': """function sgFcTop(S){return `<button class="sg-go" onclick="openInd('coins')">📈 <b>السوق الآن</b> — الحقائق والمدى المتوقع لكل عملة ←</button>`}     // 📈 v3.36.75""",
    'sgFcAn': """function sgFcAn(r){return ''}                                          // 📈 v3.36.75: المحلل القديم أُزيل (لم يغلب الصدفة)""",
    'sgFc': """function sgFc(r){return ''}""",
    'fcAn': """function fcAn(r,k){return ''}                                         // 📈 v3.36.75: لا توقّع اتجاه (لم يثبت في الفحصين 13 و14)""",
    'sgMini': """function sgMini(){return `<div class="ind-al" style="margin-top:10px"><div class="ind-al-h"><b>🔔 تنبيهات السوق — الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · السوق</b>
  <span style="display:flex;gap:6px"><button onclick="openSig('cfg')">⚙️ الإعدادات</button><button onclick="openInd('mkt')">📈 السوق</button></span></div>
  <div class="ind-sub" style="margin-top:6px">تنبيهات بما يحدث فعلاً بالأرقام — لا توقّع اتجاه ولا أوامر · كل حدث مرة واحدة · لعملاتك وللسوق كله</div></div>`}""",
}
PAGE = """/* 📈 v3.36.75: السوق — الآن والمتوقع (المحلل الجديد بعد الفحصين 13 و14): 🔎 حقائق الآن للسوق ولكل عملة · 🔮 المدى المتوقع (المثبت 80–82%)
   · لا توقّع للاتجاه (لم يغلب الصدفة على سنتين) · تنبيهات الحقائق · عرض فقط */
let ANV=null;const ANO={};
async function anLoad(){try{ANV=await api('/api/market')}catch(e){ANV={ok:false}}if(['mkt','coins','log'].includes(SGTAB)&&$('#sg_body'))sgRender()}
function anCls(k){return {p:'up',n:'dn',w:'warn'}[k]||''}
function anLines(L){return (L||[]).map(x=>`<div class="an-l ${anCls(x[2])}"><span class="an-ic">${x[0]}</span><span>${gEsc(x[1])}</span></div>`).join('')}
function anRng(R,rec){const H=(ANV&&ANV.hz)||[];if(!R)return '';
  return `<div class="an-rng"><div class="an-rh">🔮 المتوقع — بين كم وكم سيكون السعر بثقة 80%</div>${H.map(([k,nm])=>{const b=R[k];if(!b)return '';const r=(rec||{})[k];
    return `<div class="an-rr"><span>${gEsc(nm)}</span><b class="num">${fmtPx(b.lo)} – ${fmtPx(b.hi)}</b><small>±${b.w}%${r&&r.in+r.out>=5?` · صدق ${r.p}% (${r.in} من ${r.in+r.out})`:''}</small></div>`}).join('')}</div>`}
function anHelp(){return `<details class="ind-help"><summary>كيف أقرأ هذه النافذة؟</summary>
  <div>• <b>🔎 الآن</b>: حقائق تُقاس من الأسعار — الاتجاه ومنذ متى · القوة مقابل البيتكوين · الهدوء والهيجان · الحجم · أقرب دعم ومقاومة · التجميع والتصريف · المزاج والدولار.</div>
  <div>• <b>🔮 المتوقع</b>: بين كم وكم سيكون السعر بعد كل مدة بثقة 80% — فُحص على سنتين من الأسعار الحقيقية لـ38 عملة فاحتوى السعر 80–82% من المرات، وصدقه الحي يظهر بجانبه.</div>
  <div>• <b>لا تخمين للاتجاه</b>: الفحص نفسه أثبت أن لا مؤشر ولا مجموعة مؤشرات تغلب الصدفة في صعود أو نزول الساعات والأيام القادمة.</div>
  <div style="color:var(--amber);margin-top:6px">⚠️ معلومات لا توصيات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`}
function anWait(){const B=(SGV&&SGV.busy)||{};return B.phase?`<div class="sg-busy">${gEsc(B.msg||'…')}<div class="sg-pb"><i style="width:${Math.max(3,+B.pct||0)}%"></i></div></div>`:''}
function anMkt(){const A=ANV;if(!A)return `<div class="sg-empty">${LDR('جاري التحميل…')}</div>`;const M=A.mkt;
  if(!M)return anWait()+'<div class="sg-empty">🔍 أول قراءة للسوق بعد أول فحص (كل ساعة) — يُجلب تاريخ الشموع مرة واحدة أولاً</div>';
  const rb={'4h':(A.rec||{}).btc_4h,'1d':(A.rec||{}).btc_1d,'1w':(A.rec||{}).btc_1w};
  const mv=x=>(x||[]).map(([s,v])=>`<span class="an-mv ${v>=0?'up':'dn'}">${gEsc(s.split('-')[0])} ${v>=0?'+':''}${(+v).toFixed(1)}%</span>`).join('');
  return anWait()+`<div class="an-card"><div class="an-h"><b>🌐 السوق الآن</b>${A.t?`<small>🔄 ${gAgo(A.t)}</small>`:''}</div>${anLines(M.lines)}</div>
    <div class="an-card"><div class="an-h"><b>₿ البيتكوين</b><span class="num">${M.btc?fmtPx(M.btc):''}</span></div>${anRng(M.rng,rb)}</div>
    ${(M.top||[]).length?`<div class="an-card"><div class="an-h"><b>🏁 أكثر حركة خلال 24 ساعة</b></div><div class="an-mvs">${mv(M.top)}</div><div class="an-mvs">${mv(M.bottom)}</div></div>`:''}${anHelp()}`}
function anCoin(c){const op=!!ANO[c.sym],b=c.sym.split('-')[0];
  return `<div class="an-card an-coin${op?' open':''}" data-s="${gEsc(c.sym)}" onclick="ANO['${gEsc(c.sym)}']=!ANO['${gEsc(c.sym)}'];sgRender()"><div class="an-h"><b>${gEsc(b)}</b><span class="num">${fmtPx(c.px)}</span>
     <span class="chg ${c.ch24>=0?'up':'dn'}">${c.ch24>=0?'▲':'▼'}${Math.abs(+c.ch24).toFixed(2)}%</span><small style="margin-inline-start:auto">${op?'▲':'التفاصيل ▼'}</small></div>
    ${anLines(op?c.lines:(c.lines||[]).slice(0,2))}${op?anRng(c.rng,ANV.rec):''}</div>`}
function anCoins(){const A=ANV;if(!A)return `<div class="sg-empty">${LDR('جاري التحميل…')}</div>`;
  let h=anWait()+((A.coins||[]).map(anCoin).join('')||'<div class="sg-empty">🔍 تظهر عملاتك بعد أول فحص (كل ساعة)</div>');
  if((A.missing||[]).length&&(A.coins||[]).length)h+=`<div class="ind-sub">⏳ ${A.missing.map(s=>gEsc(s.split('-')[0])).join(' · ')} — تظهر بعد جلب تاريخها</div>`;
  return h+anHelp()}
function anLog(V){const L=V.log||[],R=(ANV&&ANV.rec)||{},H=(ANV&&ANV.hz)||[];
  return `<div class="an-card"><div class="an-h"><b>📏 صدق المدى المتوقع (حي)</b></div>${H.map(([k,nm])=>{const r=R[k];return `<div class="an-rr"><span>${gEsc(nm)}</span><b>${r&&r.in+r.out?`${r.p}%`:'—'}</b><small>${r?`${r.in} داخله · ${r.out} خارجه`:'يبدأ العدّ مع أول مدى يكتمل'}</small></div>`}).join('')}
      <div class="ind-sub">الهدف 80% — أكثر منه يعني أن المدى أوسع قليلاً من اللازم، وأقل منه يعني أن الحركة أعنف من المعتاد.</div></div>
    <div class="an-card"><div class="an-h"><b>🔔 آخر التنبيهات</b></div>${L.map(x=>`<div class="ind-sub">${new Date(x.ts*1000).toLocaleString('ar',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})} · <b>${gEsc(x.t)}</b> — ${gEsc(x.b)}</div>`).join('')||'<div class="ind-sub">لا تنبيهات بعد</div>'}</div>`}
async function sgSet(v){try{const r=await api('/api/control',{action:'sg_set',value:v});toast(r&&r.msg?r.msg:'تم',!!(r&&r.ok));if(r&&r.cfg&&SGV)SGV.cfg=r.cfg}catch(e){toast('تعذر الاتصال',false)}sgRender()}
function sgCfg(V){const c=V.cfg||{},A=c.atypes||{},ty=V.atypes||{},hrs=[...Array(24).keys()];
  const hsel=(id,val,fn)=>`<select id="${id}" onchange="${fn}">${hrs.map(h=>`<option value="${h}"${val===h?' selected':''}>${String(h).padStart(2,'0')}:00</option>`).join('')}</select>`;
  const q=c.quiet||null,mine=c.coins||V.tick||[];
  const grp=(g,t)=>`<div class="sg-sh">${t}</div><div class="sg-flt">${Object.entries(ty).filter(([k,x])=>x[2]===g).map(([k,x])=>`<button data-k="${k}" class="${A[k]!==false?'on':''}" onclick="sgSet({atypes:{${k}:${A[k]===false}}})">${x[0]} ${gEsc(x[1])}</button>`).join('')}</div>`;
  return `<div class="ind-al${c.on?'':' off'}"><div class="ind-al-h"><b>🔔 تنبيهات السوق <small style="color:var(--mut2);font-weight:400">${c.on?gEsc((V.ch||{})[c.ch]||''):'متوقفة'}</small></b>
      <span style="display:flex;gap:6px"><button id="sg_on" class="${c.on?'on':''}" onclick="sgSet({on:${c.on?'false':'true'}})">${c.on?'✅ مفعّلة':'⏸️ متوقفة'}</button></span></div>
    <div class="sg-set">${grp('coin','🪙 عملاتك')}${grp('mkt','🌐 السوق كله')}
      <div class="ind-sub">تنبيهات بما يحدث فعلاً — لا توقّع اتجاه ولا أوامر · كل حدث مرة واحدة · الحد اليومي تضبطه اللوحة وحدها</div></div>
    <div class="sg-set" id="sg_coins"><div class="sg-sh">🪙 عملات تنبيهاتك <small>(${mine.length})</small> ${c.coins?`<button onclick="sgSet({coins:null})">↩️ مثل الشريط</button>`:'<small>· الآن نفس عملات الشريط (📊)</small>'}</div>
      <div class="sg-flt">${mine.map(s=>`<button class="on sg-cn" data-c="${gEsc(s)}" onclick="sgCoinTog('${gEsc(s)}')" title="اضغط لإزالتها من تنبيهاتك">${gEsc(s.split('-')[0])}${(V.bad||[]).includes(s)?' ⚠️':''} <b>✕</b></button>`).join('')||'<span class="ind-sub">لا عملات — أضف واحدة</span>'}</div>
      <div class="sg-add"><input id="sg_cadd" placeholder="أضف عملة — مثل BTC أو DOGE أو PEPE" autocomplete="off" onkeydown="if(event.key==='Enter')sgCoinAdd()"><button onclick="sgCoinAdd()">➕ أضف</button></div>
      ${(V.bad||[]).length?`<div class="ind-sub" style="color:var(--amber)">⚠️ لم تُعثر على بيانات من المنصة لـ ${(V.bad||[]).map(s=>gEsc(s.split('-')[0])).join(' · ')} — تأكد من الاسم</div>`:''}</div>
    <div class="sg-set"><div class="sg-sh">🌙 ساعات الهدوء <small>(تنتظر ثم تصلك برسالة واحدة)</small></div>
      <button class="${q?'on':''}" onclick="sgSet({quiet:${q?'null':'[0,8]'}})">${q?'مفعّلة':'متوقفة'}</button> ${q?`من ${hsel('sg_q0',q[0],`sgSet({quiet:[+this.value,${q[1]}]})`)} إلى ${hsel('sg_q1',q[1],`sgSet({quiet:[${q[0]},+this.value]})`)}`:''}</div>
    <div class="sg-set"><div class="sg-sh">📨 أين تصل</div><div class="sg-flt">${Object.entries(V.ch||{}).map(([k,t])=>`<button class="${c.ch===k?'on':''}" onclick="sgSet({ch:'${k}'})">${gEsc(t)}</button>`).join('')}</div></div>
    <div class="sg-set sg-flt"><button onclick="sgTest()">🧪 جرّب تنبيهاً</button></div></div>`}
"""

KEEP = ("sgCoinAdd", "sgCoinTog", "sgTest")


def fn_span(s, name, a=0):
    m = re.search(r"\n(?:async )?function " + re.escape(name) + r"\(", s[a:])
    if not m:
        return None
    i = a + m.start() + 1
    n = re.search(r"\n(?:async function |function |const |let |/\*)", s[i + 1:])
    return i, (i + 1 + n.start() + 1) if n else len(s)


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for name, new in FN.items():
        sp = fn_span(s, name)
        if not sp:
            print(f"❌ function {name} not found"); sys.exit(1)
        s = s[:sp[0]] + new + "\n" + s[sp[1]:]
    # the old analyst window's functions (🧠 · 📚 · the slider · the old log and settings) ⇒ the new market window
    a0 = s.index("\nfunction sgCatUI(V)") + 1
    a1 = s.index("\nfunction sgRender(){") + 1
    old = s[a0:a1]
    keep = []
    for name in KEEP:
        sp = fn_span("\n" + old, name)
        if not sp:
            print(f"❌ {name} not in the old block"); sys.exit(1)
        keep.append(("\n" + old)[sp[0]:sp[1]].rstrip("\n") + "\n")
    s = s[:a0] + PAGE + "".join(keep) + s[a1:]
    s = s.replace("const SGCOMP={up:['صاعد','🟢','p'],flat:['مختلط','🟡','z'],down:['نازل','🔴','n']};\n", "", 1)
    for name in ("sgRow", "sgHead"):                       # used only by the removed tabs
        sp = fn_span(s, name)
        if sp:
            s = s[:sp[0]] + s[sp[1]:]
    for gone in ("SGCOMP", "function sgRow(", "function sgHead(", "function sgAn(", "function sgCatUI(", "function sgCat(", "function sgLog(", "function sgEst(", "function sgEstTxt(", "function sgRecDl(",
                 "function sgRebuild(", "function sgAnCoin(", "function sgAnMkt(", "function sgHz("):
        if gone in s:
            print(f"❌ still there: {gone}"); sys.exit(1)
    # help text of 🔮 without the analyst
    hs = "    <div>• المؤشرات هنا هي نفسها في «🎯 المؤشرات» بأسمائها ومعانيها · وفي «يوم» و«شهر» يأتي أولاً <b>🧠 المحلل</b>"
    if s.count(hs) == 1:
        i = s.index(hs)
        j = s.index("</div>", i) + len("</div>")
        s = s[:i] + "    <div>• المؤشرات هنا هي نفسها في «📋 المؤشرات» بأسمائها ومعانيها — وصف للحال لا توقّع · الحقائق والمدى المتوقع لكل عملة في «📈 السوق».</div>" + s[j:]
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + len(FN) + 1} replacements · 📈 the market now and next · compiles · {p}")
