# p134 — v3.36.76 🔔 the market notices organised (the owner 21-11: «مشكلتي الاشعارات كيف راح اتنظمه» · «لا ما اريد ملخص يومي» · approved the
#   models one by one — «ابدي بالتحديث الاول»)
#   · every type has a level: 📲 now (Telegram + the app) · 👁 view (the window's 📜 log only) · ⛔ off — the owner picks each one (an_lv)
#   · 🔴 urgent: 🌊 the whole market crashed · 🚀 a mass surge · ⚡ Bitcoin moved ≥ 3% in an hour — sent at once even in quiet hours, outside
#     the daily cap, and they stop the coins' cards in their round (one market message instead of a storm of notices)
#   · one card per coin per round (everything that happened to it + 🔮 tomorrow's range with its record) · a coin's next card waits 6 hours
#     unless its daily trend turned · one card for the market's changes · the daily cap = 12 cards · quiet hours wait, then one message
#   · new types: 🎯 the daily tendency (only champions — p131) · 🪙 money moving to the altcoins / back to Bitcoin · the three urgent ones
#   · the texts in plain Arabic with the numbers (صاعداً / هابطاً …) · the log says what reached you and why the rest did not
#   python3 devtests/step/patches/p134_notify_cards.py Holy_Dashboard.pyw
import sys, os, re

AN_TY_OLD = '''AN_TY = {   # 📈 v3.36.75: تنبيهات الحقائق — (الأيقونة · الاسم · المجموعة) · لا توقّع اتجاه (لم يغلب الصدفة في الفحصين 13 و14)
    "trend": ("📈", "تغيّر الاتجاه", "coin"), "rs": ("💪", "القوة مقابل البيتكوين", "coin"), "vol": ("📊", "حجم غير عادي", "coin"),
    "lvl": ("🧱", "كسر دعم أو اختراق مقاومة", "coin"), "out": ("⚡", "حركة خارج المدى المتوقع", "coin"), "ad": ("🧲", "التجميع والتصريف", "coin"),
    "mtrend": ("🧭", "تغيّر اتجاه السوق", "mkt"), "storm": ("🎢", "السوق هاج أو هدأ", "mkt"), "wave": ("🌊", "انهيار السوق كله", "mkt"),
    "fng": ("😨", "خوف أو طمع شديد", "mkt")}
'''
AN_TY_NEW = '''AN_TY = {   # 📈 v3.36.75 · 🔔 v3.36.76: (الأيقونة · الاسم · المجموعة · المستوى الافتراضي) — now 📲 فوري · view 👁 بالنافذة · off ⛔ مطفي
    "wave": ("🌊", "انهيار السوق كله", "urgent", "now"), "surge": ("🚀", "صعود جماعي في السوق", "urgent", "now"),
    "bstorm": ("⚡", "البيتكوين يتحرك بعنف (3% خلال ساعة)", "urgent", "now"),
    "trend": ("📈", "تغيّر الاتجاه اليومي", "coin", "now"), "lvl": ("🧱", "كسر دعم أو اختراق مقاومة", "coin", "now"),
    "out": ("⚡", "حركة أكثر من المتوقع", "coin", "now"), "vol": ("📊", "حجم تداول غير عادي", "coin", "now"),
    "tend": ("🎯", "الميل اليومي (حين يثبت)", "coin", "now"), "rs": ("💪", "القوة مقابل البيتكوين", "coin", "view"),
    "ad": ("🧲", "التجميع والتصريف", "coin", "view"),
    "mtrend": ("🧭", "تغيّر اتجاه السوق", "mkt", "now"), "storm": ("🎢", "السوق هاج أو هدأ", "mkt", "now"),
    "season": ("🪙", "السيولة بين البيتكوين والعملات", "mkt", "view"), "fng": ("😨", "خوف أو طمع شديد", "mkt", "view")}
AN_LV = ("now", "view", "off")
AN_DUP = {"bstorm": 6 * 3600, "wave": 12 * 3600, "surge": 12 * 3600}     # منع التكرار لكل نوع (الباقي 20 ساعة)
AN_COOL = 6 * 3600                                                      # بطاقة العملة التالية بعد 6 ساعات إلا إذا انقلب اتجاهها
'''

FACTS = '''def _an_mv(cdb, sym, n):
    """تغيّر السعر % خلال آخر n ساعات (شموع الساعة المحفوظة)"""
    rows = (((cdb or {}).get("c1") or {}).get(sym) or {}).get("d") or []
    if len(rows) <= n:
        return None
    a, b = float(rows[-1 - n][4]), float(rows[-1][4])
    return (b / a - 1) * 100 if a > 0 else None


def _an_mine_mv(cdb, mine, n):
    xs = [(s, _an_mv(cdb, s, n)) for s in mine if not s.startswith("BTC-")]
    xs = sorted((x for x in xs if x[1] is not None), key=lambda x: -abs(x[1]))
    return " · ".join(f"{s.split('-')[0]} {v:+.1f}%" for s, v in xs[:6])


def _an_facts(prev, P, rng_prev, mine, lv, sc=None, lvd=None, cdb=None, td=None):
    """📨 ما تغيّر بين لقطتين ⇒ [(مفتاح التكرار, {sym · ty · lv · urg · ln (سطر البطاقة) · t (للسجل) · b})] — المطفي لا يُحسب أصلاً"""
    out = []
    cdb = cdb or {}

    def add(key, sym, ty, ln, b=""):
        L = (lv or {}).get(ty) or AN_TY[ty][3]
        if L not in ("now", "view"):
            return
        head = ln.split("\\n")[0]
        out.append((key, {"sym": sym, "ty": ty, "lv": L, "urg": AN_TY[ty][2] == "urgent", "ln": ln,
                          "t": (f"{sym.split('-')[0]}: " if "-" in sym else "") + head, "b": b or " · ".join(ln.split("\\n")[1:])}))
    pc = (prev or {}).get("coins") or {}
    for s in mine:
        c, o = (P.get("coins") or {}).get(s), pc.get(s)
        if not c or not o:
            continue
        tr = c.get("trend")
        if tr != o.get("trend") and tr in ("up", "down"):
            where = ((c.get("lines") or [("", "")])[0][1].split(" — ") + [""])[1]
            add(f"trend|{s}|{tr}", s, "trend", f"{'📈' if tr == 'up' else '📉'} الاتجاه اليومي أصبح {'صاعداً' if tr == 'up' else 'هابطاً'}" + (f" — {where}" if where else ""))
        if o.get("rs7") is not None and c.get("rs7") is not None and c.get("rs30") is not None:
            was = (o["rs7"] > 0 and (o.get("rs30") or 0) > 0) - (o["rs7"] < 0 and (o.get("rs30") or 0) < 0)
            now_ = (c["rs7"] > 0 and c["rs30"] > 0) - (c["rs7"] < 0 and c["rs30"] < 0)
            if now_ and now_ != was:
                add(f"rs|{s}|{now_}", s, "rs", f"💪 أصبحت {'أقوى' if now_ > 0 else 'أضعف'} من البيتكوين — أسبوع {c['rs7']:+.1f}% · شهر {c['rs30']:+.1f}%")
        if (c.get("volx") or 0) >= 2.0 and (o.get("volx") or 0) < 2.0:
            add(f"vol|{s}", s, "vol", f"📊 حجم تداول غير عادي: ×{c['volx']:.1f} من المعتاد خلال 24 ساعة · السعر {c['ch24']:+.1f}%")
        L_ = (lvd or {}).get(s) or {}                        # الكسر على إغلاق اليوم ومن مستويات أمس (لا ذيول الساعة)
        if lvd is not None and L_.get("px"):
            vx = c.get("volx") or 0
            vt = f" — الحجم ×{vx:.1f} من المعتاد" if vx >= 1.2 else ""
            if L_.get("res") and c["px"] > float(L_["res"]) * 1.003 and float(L_["px"]) <= float(L_["res"]):
                add(f"lvl|{s}|r|{L_['res']:.6g}", s, "lvl", f"🧱 اخترق المقاومة {_px_s(L_['res'])} بإغلاق اليوم ({_px_s(c['px'])}){vt}")
            if L_.get("sup") and c["px"] < float(L_["sup"]) * 0.997 and float(L_["px"]) >= float(L_["sup"]):
                add(f"lvl|{s}|s|{L_['sup']:.6g}", s, "lvl", f"🧱 كسر الدعم {_px_s(L_['sup'])} بإغلاق اليوم ({_px_s(c['px'])}){vt}")
        rp = ((rng_prev or {}).get(s) or {}).get("4h")           # خارج المدى: مرة لكل جهة باليوم (لا كل ساعة في موجة قوية)
        if rp and (c["px"] > rp["hi"] or c["px"] < rp["lo"]):
            up = c["px"] > rp["hi"]
            add(f"out|{s}|{'u' if up else 'd'}", s, "out", f"⚡ {'صعد' if up else 'نزل'} أكثر من المتوقع: {_px_s(c['px'])} {'فوق' if up else 'تحت'} "
                f"المدى المتوقع للساعات الأربع ({_px_s(rp['lo'])} – {_px_s(rp['hi'])})")
        if c.get("ad") in ("acc", "dist") and c.get("ad") != o.get("ad"):
            add(f"ad|{s}|{c['ad']}", s, "ad", "🧲 تجميع: السيولة تدخل والسعر لم يصعد بعد" if c["ad"] == "acc" else "🔻 تصريف: السيولة تخرج والسعر لم ينزل بعد")
    if td:                                                   # 🎯 الميل اليومي — أبطال الجداول المجمّعة فقط (p131)
        rec = td.get("rec") or [0, 0]
        for s in mine:
            x = (td.get("now") or {}).get(s)
            if not x or not x[0]:
                continue
            side, codes = int(x[0]), list(x[1] or [])
            pct = f" — صدق هذا الميل {round(100.0 * rec[0] / rec[1])}% من {rec[1]:,} مرة" if rec[1] >= 30 else ""
            add(f"tend|{s}|{side}|{td.get('t')}", s, "tend", f"🎯 ميل يومي {'للصعود' if side > 0 else 'للنزول'}{pct}\\n"
                f"المؤشرات: {' · '.join(SB_NM.get(c_, c_) for c_ in codes[:3])}\\nميل ضعيف يتأخر عن الحركة — ليس ضماناً")
    M, Mo = P.get("mkt") or {}, (prev or {}).get("mkt") or {}
    if M.get("trend") and Mo.get("trend") and M["trend"] != Mo["trend"] and M["trend"] in ("up", "down"):
        up = M["trend"] == "up"
        add(f"mtrend|{M['trend']}", "السوق", "mtrend", f"{'📈' if up else '📉'} السوق: اتجاه البيتكوين اليومي أصبح {'صاعداً' if up else 'هابطاً'}"
            + (f" · {M['above']} من {_sg_ar(M['n'], 'coin')} فوق متوسطها" if M.get("n") else ""))
    if M.get("vk") and Mo.get("vk") and (M["vk"] == "storm") != (Mo["vk"] == "storm"):
        tail = next(((x[1].split(" — ") + [""])[1] for x in M.get("lines") or [] if x[0] == "🎢"), "")
        add(f"storm|{M['vk']}", "السوق", "storm", ("🎢 هاج السوق" if M["vk"] == "storm" else "🎢 هدأ السوق") + (f": {tail}" if tail else ""))
    if M.get("season") in ("alt", "btc") and Mo.get("season") and M["season"] != Mo["season"]:
        k, n_ = M.get("beat") or 0, M.get("rsn") or 0
        add(f"season|{M['season']}", "السوق", "season", f"🪙 السيولة تتجه إلى العملات البديلة: {k} من {_sg_ar(n_, 'coin')} أقوى من البيتكوين خلال الشهر"
            if M["season"] == "alt" else f"🪙 السيولة تعود إلى البيتكوين: {n_ - k} من {_sg_ar(n_, 'coin')} أضعف منه خلال الشهر")
    f, fo = M.get("fng"), Mo.get("fng")
    if f is not None and fo is not None and ((f <= 20 < fo) or (f >= 80 > fo)):
        add(f"fng|{'f' if f <= 20 else 'g'}", "السوق", "fng", f"{'😨' if f <= 20 else '🤑'} مزاج السوق: {'خوف شديد' if f <= 20 else 'طمع شديد'} ({round(f)} من 100)")
    # 🔴 الطوارئ
    e1h = [((x or {}).get("1H") or {}).get("e1") or [] for x in ((sc or {}).get("c") or {}).values()]
    b1 = _an_mv(cdb, "BTC-USDT", 1)
    btc = f"\\nالبيتكوين: {b1:+.1f}% خلال ساعة ({_px_s(M['btc'])})" if b1 is not None and M.get("btc") else ""
    crash = (sc or {}).get("crash")
    if (crash and crash.get("on")) or any("W-crash:-1" in e for e in e1h):
        k4 = (f"هبطت {crash.get('k')} من {_sg_ar(crash.get('n') or 0, 'coin')} بقوة غير معتادة خلال الساعات الأربع الأخيرة" if crash and crash.get("on")
              else "هبطت عملات كثيرة بقوة غير معتادة في الساعة نفسها")
        mm = _an_mine_mv(cdb, mine, 4)
        add("wave", "السوق", "wave", f"🌊 انهيار في السوق كله الآن\\n{k4}{btc}" + (f"\\nمن عملاتك (4 ساعات): {mm}" if mm else ""))
    if any("W-surge:1" in e for e in e1h):
        mm = _an_mine_mv(cdb, mine, 1)
        add("surge", "السوق", "surge", f"🚀 صعود جماعي في السوق الآن\\nقفزت عملات كثيرة بقوة غير معتادة في الساعة نفسها{btc}" + (f"\\nمن عملاتك: {mm}" if mm else ""))
    if b1 is not None and abs(b1) >= 3.0:
        rb = ((Mo.get("rng") or {}).get("4h")) or {}
        mm = _an_mine_mv(cdb, mine, 1)
        add(f"bstorm|{'u' if b1 > 0 else 'd'}", "السوق", "bstorm", f"⚡ البيتكوين يتحرك بعنف: {b1:+.1f}% خلال ساعة ({_px_s(M.get('btc') or 0)})"
            + (f"\\nالمدى المتوقع لهذه الساعات كان {_px_s(rb['lo'])} – {_px_s(rb['hi'])}" if rb.get("lo") else "") + (f"\\nمن عملاتك: {mm}" if mm else ""))
    return out
'''

FEED = '''def an_feed(sc, frs, cdb, now, cfg, st, send=True):
    """📈 بعد كل فحص: يحفظ «الآن» والمدى والميل · يحكم المدى القديم · ويعيد ما تغيّر (مرة لكل حدث) — التسليم في _sg_deliver"""
    P = (sc or {}).get("an")
    if not isinstance(P, dict) or not P.get("coins"):
        return []
    with _AN["lock"]:
        A = _an_load()
        _an_grade(A, cdb, now)
        prev, rng_prev = A.get("now"), {s: c.get("rng") for s, c in ((A.get("now") or {}).get("coins") or {}).items()}
        _an_issue(A, P, frs, now)
        daily = "1D" in frs
        td = (sc or {}).get("td") if daily else None
        if isinstance(td, dict):
            A["td"] = td                                     # 🎯 الميل اليومي وأبطاله (للنافذة و🔮)
        scx = {"crash": (sc or {}).get("crash") if "4H" in frs else None, "c": (sc or {}).get("c") or {}}
        facts = _an_facts(prev, P, rng_prev, sg_coins(cfg), cfg.get("alv") or {}, scx, (A.get("lvd") or {}) if daily else None, cdb,
                          td if isinstance(td, dict) else None) if prev else []
        A["now"] = P
        if daily:                                            # مستويات إغلاق اليوم — مرجع كسر الغد
            A["lvd"] = {s: {"px": c.get("px"), "res": (c.get("lv") or {}).get("res"), "sup": (c.get("lv") or {}).get("sup")}
                        for s, c in (P.get("coins") or {}).items() if c.get("px")}
        r1 = (A.get("rec") or {}).get("1d") or [0, 0]
        out = []
        for key, f in facts:
            if now - float(A["sent"].get(key) or 0) < AN_DUP.get(f["ty"], 20 * 3600):
                continue
            A["sent"][key] = round(now)
            rg = (((P.get("coins") or {}).get(f["sym"]) or {}).get("rng") or {}).get("1d")
            if rg:                                           # 🔮 سطر الغد في بطاقة العملة (مع صدق المدى الحي)
                f["rng"] = f"🔮 المتوقع غداً: بين {_px_s(rg['lo'])} و{_px_s(rg['hi'])}" + (
                    f" (صدق هذا المدى {round(100.0 * r1[0] / (r1[0] + r1[1]))}% من {r1[0] + r1[1]:,} مرة)" if r1[0] + r1[1] >= 20 else "")
            out.append(f)
        for k in [k for k, v in A["sent"].items() if now - float(v) > 7 * 86400]:
            A["sent"].pop(k, None)
        A["ts"] = round(now)
        save_json_atomic(AN_FILE, A)
    return out
'''

DELIVER = '''def _sg_deliver(facts, st, cfg, now, send=True):
    """📨 v3.36.76: كل نوع بمستواه (📲 فوري · 👁 بالنافذة) · 🔴 الطارئ فوراً (حتى بساعات الهدوء · خارج الحد) ويوقف بطاقات العملات في جولته ·
    بطاقة واحدة لكل عملة (التالية بعد 6 ساعات إلا إذا انقلب اتجاهها) + بطاقة للسوق · الحد 12 بطاقة باليوم · ساعات الهدوء تنتظر ثم رسالة واحدة"""
    if not facts:
        return []
    day = datetime.fromtimestamp(now).strftime("%Y-%m-%d")
    if st.get("day") != day:
        st.update(day=day, n=0, capped=False)
    for f in facts:
        f["st"] = "view" if f["lv"] != "now" else "urgent" if f.get("urg") else "sent"
    urg = [f for f in facts if f["st"] == "urgent"]
    norm = [f for f in facts if f["st"] == "sent"]
    cards, cool = [], st.setdefault("cool", {})
    if urg:
        for f in norm:
            f["st"] = "storm"                                # 🌊 ضمن رسالة العاصفة — لا بطاقات منفردة في جولتها
        if send:
            _sg_tg("\\n\\n".join(f["ln"] for f in urg), cfg)
    else:
        by = {}
        for f in norm:
            by.setdefault(f["sym"], []).append(f)
        for sym, fs in by.items():
            if sym == "السوق":
                cards.append((sym, fs[0]["ln"] if len(fs) == 1 else "🌐 السوق — تغيّر الآن\\n" + "\\n".join(f["ln"] for f in fs), fs))
                continue
            if now - float(cool.get(sym) or 0) < AN_COOL and not any(f["ty"] == "trend" for f in fs):
                for f in fs:
                    f["st"] = "cool"                         # ⏱ بعد بطاقة قريبة لهذه العملة
                continue
            rg = next((f["rng"] for f in fs if f.get("rng")), "")
            cards.append((sym, f"📈 {sym.split('-')[0]} — حدث الآن\\n" + "\\n".join(f["ln"] for f in fs) + (f"\\n{rg}" if rg else ""), fs))
    out, note = [], ""
    if cards and _sg_quiet(cfg, now):
        st.setdefault("qq", []).extend({"t": tx, "b": ""} for _s, tx, _fs in cards)
        del st["qq"][:-40]
        for sym, _tx, fs in cards:
            cool[sym] = round(now)
            for f in fs:
                f["st"] = "quiet"
        cards = []
    if cards and cfg["cap"] > 0:
        room = max(0, cfg["cap"] - int(st.get("n") or 0))
        for _sym, _tx, fs in cards[room:]:
            for f in fs:
                f["st"] = "cap"
        if len(cards) > room and not st.get("capped"):
            st["capped"] = True
            note = f"🔕 بلغت تنبيهات السوق حدّها اليوم ({cfg['cap']}) — البقية في نافذة 📈 السوق"
        cards = cards[:room]
    if cards or note:
        st["n"] = int(st.get("n") or 0) + len(cards)
        for sym, _tx, _fs in cards:
            cool[sym] = round(now)
        text = cards[0][1] if len(cards) == 1 else (f"📈 السوق — تنبيهات جديدة ({len(cards)})\\n\\n" + "\\n\\n".join(tx for _s, tx, _fs in cards)) if cards else ""
        text = (text + ("\\n\\n" if text else "") + note) if note else text
        if send and text:
            _sg_tg(text, cfg)
    for k in [k for k, v in cool.items() if now - float(v) > 2 * 86400]:
        cool.pop(k, None)
    log = st.setdefault("log", [])
    for f in facts:
        log.insert(0, {"ts": round(now), "sym": f["sym"], "ty": f["ty"], "t": f["t"], "b": f.get("b") or "", "st": f["st"]})
        _safe(_dash_event, f["sym"], f["t"] + (" · " + f["b"] if f.get("b") else ""), default=None)
        if f["st"] in ("sent", "urgent"):
            out.append(f)
    del log[150:]
    return out


def _sg_flush(st, cfg, now, send=True):
    """🌙 بعد ساعات الهدوء: ما انتظر برسالة واحدة (بطاقاته كما هي)"""
    if st.get("qq") and not _sg_quiet(cfg, now):
        q = st.pop("qq")
        text = f"🌙 تنبيهات السوق أثناء ساعات الهدوء ({len(q)})\\n\\n" + "\\n\\n".join(x["t"] + (("\\n" + x["b"]) if x.get("b") else "") for x in q[:15]) + \\
            (f"\\n\\n… و{len(q) - 15} غيرها في نافذة 📈 السوق" if len(q) > 15 else "")
        if send:
            _sg_tg(text, cfg)
        return text
    st.pop("sumq", None)
    return None
'''

R = [
    (AN_TY_OLD, AN_TY_NEW),
    ('            M["beat"] = beat\n',
     '            M["beat"] = beat\n            M["rsn"] = len(uni_rs)                       # 🪙 v3.36.76: لتنبيه «السيولة بين البيتكوين والعملات»\n'
     '            M["season"] = "alt" if beat / len(uni_rs) >= 0.7 else "btc" if beat / len(uni_rs) <= 0.3 else "mix"\n'),
    ('            "atypes": {k: bool((c.get("an_types") if isinstance(c.get("an_types"), dict) else {}).get(k, True)) for k in AN_TY}}\n',
     '            "alv": _an_lv_cfg(c), "atypes": {k: v != "off" for k, v in _an_lv_cfg(c).items()}}     # 🔔 v3.36.76: مستوى كل نوع\n'),
    ('''    if isinstance(v.get("atypes"), dict):                                   # 📈 v3.36.75: تنبيهات الحقائق
        t = dict(c.get("an_types") or {})
        t.update({k: bool(x) for k, x in v["atypes"].items() if k in AN_TY})
        c["an_types"] = t
''',
     '''    if isinstance(v.get("alv"), dict) or isinstance(v.get("atypes"), dict):     # 🔔 v3.36.76: 📲 فوري · 👁 بالنافذة · ⛔ مطفي لكل نوع
        t = _an_lv_cfg(c)
        t.update({k: x for k, x in (v.get("alv") or {}).items() if k in AN_TY and x in AN_LV})
        t.update({k: (AN_TY[k][3] if x else "off") for k, x in (v.get("atypes") or {}).items() if k in AN_TY and not isinstance(v.get("alv"), dict)})
        c["an_lv"] = {k: x for k, x in t.items() if x != AN_TY[k][3]}
        c.pop("an_types", None)
'''),
    ('''    text = (f"🧪 تجربة — 🧱 {sym.split('-')[0]}: اخترق المقاومة\\nهكذا يصلك التنبيه: ما حدث فعلاً بالأرقام — لا توقّع اتجاه ولا أمر\\n"
            f"⚙️ {SG_CH[cfg['ch']]}")
''',
     '''    text = (f"🧪 تجربة: هكذا تصلك تنبيهات السوق\\n📈 {sym.split('-')[0]} — حدث الآن\\n🧱 اخترق المقاومة بإغلاق اليوم\\n"
            f"بطاقة واحدة لكل عملة · والطارئ فوراً حتى في ساعات الهدوء — لا توقّع اتجاه ولا أوامر\\n⚙️ {SG_CH[cfg['ch']]}")
'''),
    (".an-mvs{display:flex;gap:6px;flex-wrap:wrap;margin:3px 0}",
     ".an-ty{display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap;padding:4px 0;border-bottom:1px dashed var(--bd);font-size:12.5px}"
     ".an-seg{display:flex;gap:4px;flex-wrap:wrap}.an-seg button{font-size:11px;padding:3px 8px;border-radius:999px}"
     ".an-seg button.on{border-color:var(--vio);color:var(--vio);background:rgb(var(--vio-rgb)/.12)}"
     ".an-tag{font-size:10.5px;color:var(--mut);border:1px solid var(--bd);border-radius:999px;padding:0 6px;margin-inline-start:4px;white-space:nowrap}\n"
     ".an-mvs{display:flex;gap:6px;flex-wrap:wrap;margin:3px 0}"),
]

LVCFG = '''def _an_lv_cfg(c):
    """🔔 v3.36.76: مستوى كل نوع — المحفوظ (an_lv) · وإلا القديم (an_types: مطفي ⇒ ⛔) · وإلا الافتراضي"""
    lv = c.get("an_lv") if isinstance(c.get("an_lv"), dict) else {}
    old = c.get("an_types") if isinstance(c.get("an_types"), dict) else {}
    return {k: (lv[k] if lv.get(k) in AN_LV else "off" if old.get(k) is False else x[3]) for k, x in AN_TY.items()}


'''

JS_CFG = r'''function sgCfg(V){const c=V.cfg||{},A=c.alv||{},ty=V.atypes||{},hrs=[...Array(24).keys()];     // 🔔 v3.36.76: مستوى لكل نوع
  const hsel=(id,val,fn)=>`<select id="${id}" onchange="${fn}">${hrs.map(h=>`<option value="${h}"${val===h?' selected':''}>${String(h).padStart(2,'0')}:00</option>`).join('')}</select>`;
  const q=c.quiet||null,mine=c.coins||V.tick||[],LB={now:'📲 فوري',view:'👁 بالنافذة',off:'⛔ متوقف'};
  const row=([k,x])=>{const cur=A[k]||x[3];return `<div class="an-ty" data-k="${k}"><span>${x[0]} ${gEsc(x[1])}</span><span class="an-seg">${['now','view','off'].map(l=>`<button data-l="${l}" class="${cur===l?'on':''}" onclick="sgSet({alv:{${k}:'${l}'}})">${LB[l]}</button>`).join('')}</span></div>`};
  const grp=(g,t)=>`<div class="sg-sh">${t}</div>${Object.entries(ty).filter(([k,x])=>x[2]===g).map(row).join('')}`;
  return `<div class="ind-al${c.on?'':' off'}"><div class="ind-al-h"><b>🔔 تنبيهات السوق <small style="color:var(--mut2);font-weight:400">${c.on?gEsc((V.ch||{})[c.ch]||''):'متوقفة'}</small></b>
      <span style="display:flex;gap:6px"><button id="sg_on" class="${c.on?'on':''}" onclick="sgSet({on:${c.on?'false':'true'}})">${c.on?'✅ مفعّلة':'⏸️ متوقفة'}</button></span></div>
    <div class="sg-set">${grp('urgent','🔴 طوارئ — تصل فوراً حتى في ساعات الهدوء')}${grp('coin','🪙 عملاتك')}${grp('mkt','🌐 السوق كله')}
      <div class="ind-sub">📲 فوري: يصلك على تيليغرام والتطبيق · 👁 بالنافذة: في 📜 السجل فقط · ⛔ متوقف — بطاقة واحدة لكل عملة (التالية بعد 6 ساعات إلا إذا انقلب اتجاهها) · الحد 12 بطاقة في اليوم والطارئ خارجه · لا توقّع اتجاه ولا أوامر</div></div>
    <div class="sg-set" id="sg_coins"><div class="sg-sh">🪙 عملات تنبيهاتك <small>(${mine.length})</small> ${c.coins?`<button onclick="sgSet({coins:null})">↩️ مثل الشريط</button>`:'<small>· الآن نفس عملات الشريط (📊)</small>'}</div>
      <div class="sg-flt">${mine.map(s=>`<button class="on sg-cn" data-c="${gEsc(s)}" onclick="sgCoinTog('${gEsc(s)}')" title="اضغط لإزالتها من تنبيهاتك">${gEsc(s.split('-')[0])}${(V.bad||[]).includes(s)?' ⚠️':''} <b>✕</b></button>`).join('')||'<span class="ind-sub">لا عملات — أضف واحدة</span>'}</div>
      <div class="sg-add"><input id="sg_cadd" placeholder="أضف عملة — مثل BTC أو DOGE أو PEPE" autocomplete="off" onkeydown="if(event.key==='Enter')sgCoinAdd()"><button onclick="sgCoinAdd()">➕ أضف</button></div>
      ${(V.bad||[]).length?`<div class="ind-sub" style="color:var(--amber)">⚠️ لم تُعثر على بيانات من المنصة لـ ${(V.bad||[]).map(s=>gEsc(s.split('-')[0])).join(' · ')} — تأكد من الاسم</div>`:''}</div>
    <div class="sg-set"><div class="sg-sh">🌙 ساعات الهدوء <small>(تنتظر ثم تصلك برسالة واحدة · الطارئ لا ينتظر)</small></div>
      <button class="${q?'on':''}" onclick="sgSet({quiet:${q?'null':'[0,8]'}})">${q?'مفعّلة':'متوقفة'}</button> ${q?`من ${hsel('sg_q0',q[0],`sgSet({quiet:[+this.value,${q[1]}]})`)} إلى ${hsel('sg_q1',q[1],`sgSet({quiet:[${q[0]},+this.value]})`)}`:''}</div>
    <div class="sg-set"><div class="sg-sh">📨 أين تصل</div><div class="sg-flt">${Object.entries(V.ch||{}).map(([k,t])=>`<button class="${c.ch===k?'on':''}" onclick="sgSet({ch:'${k}'})">${gEsc(t)}</button>`).join('')}</div></div>
    <div class="sg-set sg-flt"><button onclick="sgTest()">🧪 جرّب تنبيهاً</button></div></div>`}
'''

JS_LOG = r'''function anLog(V){const L=V.log||[],R=(ANV&&ANV.rec)||{},H=(ANV&&ANV.hz)||[];
  const TG={sent:'📲 وصلك',urgent:'🔴 طارئ — وصلك',view:'👁 بالنافذة',quiet:'🌙 بعد ساعات الهدوء',storm:'🌊 ضمن رسالة العاصفة',cool:'⏱ بعد بطاقة قريبة',cap:'🔕 بعد الحد اليومي'};
  return `<div class="an-card"><div class="an-h"><b>📏 صدق المدى المتوقع (حي)</b></div>${H.map(([k,nm])=>{const r=R[k];return `<div class="an-rr"><span>${gEsc(nm)}</span><b>${r&&r.in+r.out?`${r.p}%`:'—'}</b><small>${r?`${r.in} داخله · ${r.out} خارجه`:'يبدأ العدّ مع أول مدى يكتمل'}</small></div>`}).join('')}
      <div class="ind-sub">الهدف 80% — أكثر منه يعني أن المدى أوسع قليلاً من اللازم، وأقل منه يعني أن الحركة أعنف من المعتاد.</div></div>
    <div class="an-card"><div class="an-h"><b>🔔 آخر التنبيهات</b></div>${L.map(x=>`<div class="ind-sub">${new Date(x.ts*1000).toLocaleString('ar',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})} · <b>${gEsc(x.t)}</b>${x.b?` — ${gEsc(x.b)}`:''}${TG[x.st]?`<span class="an-tag">${TG[x.st]}</span>`:''}</div>`).join('')||'<div class="ind-sub">لا تنبيهات بعد</div>'}</div>`}
'''


def py_span(s, name):
    i = s.index("\ndef " + name + "(") + 1
    j = s.index("\n\n\n", i)
    return i, j


def js_span(s, name):
    m = re.search(r"\n(?:async )?function " + re.escape(name) + r"\(", s)
    i = m.start() + 1
    n = re.search(r"\n(?:async function |function |const |let |/\*)", s[i + 1:])
    return i, i + 1 + n.start() + 1


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a, b = py_span(s, "_an_facts")
    s = s[:a] + FACTS.rstrip("\n") + s[b:]
    a, b = py_span(s, "an_feed")
    s = s[:a] + FEED.rstrip("\n") + s[b:]
    a, _b = py_span(s, "_sg_deliver")
    _a, b = py_span(s, "_sg_flush")
    s = s[:a] + DELIVER.rstrip("\n") + s[b:]
    a = s.index("\ndef sg_cfg():\n") + 1
    s = s[:a] + LVCFG + s[a:]
    for name, new in (("sgCfg", JS_CFG), ("anLog", JS_LOG)):
        a, b = js_span(s, name)
        s = s[:a] + new + s[b:]
    for need in ("def _an_mv(", "def _an_mine_mv(", "def _an_lv_cfg(", "AN_COOL = ", "an-seg", "🌙 تنبيهات السوق أثناء ساعات الهدوء"):
        if need not in s:
            print(f"❌ missing after patch: {need}"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + 6} replacements · 🔔 the market notices organised (levels · urgent · one card per coin) · compiles · {p}")
