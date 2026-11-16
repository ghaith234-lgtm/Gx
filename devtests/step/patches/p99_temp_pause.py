# ⏳ patch 99 (dashboard v3.36.58) — «وقف الشراء المؤقت». The owner (16-11), after several rounds:
#   «وقف الشراء المؤقت يظهر عندما ما يوجد اموال ، السبب حتى ما يضل ينادي والسبب الاخر حتى ما ياخذ دولار حق dca بيعي او ربح بوت اخر» ·
#   «يعني قصدي مثلا يطلب ١٧ مستوى شراى يعني المؤقت كلهم يشملهم ، وااذا رجع السعر عادي يبيع ويشتري ، يعني كانما موقفها سابق» ·
#   «اذا فتحت الاعتيادي الي مسويه اني الا يفتح المؤقت لا هو مثل الحنفية» · «حالي عندي بوتات اتنادي … التحديث الجديد يغلقهم وكانما
#   غالقهم سابقا كذلك يجيني تنبيه عند الغلق و توفر الاموال» · «ابدي وسوي عليه تجارب قوية».
#   Replaces the automatic resume of v3.36.44 (p70 · p71) and patch 97 (not applied — the owner chose this design instead):
#   · two valves on one pipe: the owner's ⏸ (his floor) and the temporary one (⏳). The engine has one buy_floor = the higher of the two
#     — buying only when both are open · neither opens the other (his ⏸/▶️ on the card move his valve only)
#   · it closes when the wallet's free dollars that are NOT reserved can't cover the bot's next buy (two guard rounds): the sell DCA's
#     (and DCA+'s) dollars from its sells — what it needs to buy its coins back — are reserved, and the dollars the closed bots' pulled
#     orders freed belong to their own stores
#   · where: the BEGINNING of the gap — above the highest level the bot wants and has no order for (its store · its memory the price
#     crossed · the catch-up levels above the price, the engine's own gap: ×(1+g)² · ➕ ×(1+g)^(n+1) · 🪜 the buy slots the price crossed)
#     — else just under its lowest live buy (funded — stays) — else the price. As if it had been closed before: every level it was
#     calling for is kept, none bought, no other bot's dollars, nothing by itself. The floor stays where it is (it no longer follows the
#     price): above it the bot sells and buys as usual with its own dollars · short again up there ⇒ it closes from the new beginning
#   · the update day: bots calling for dollars now close the same way within two rounds · records of the old automatic pause carry on
#     as temporary closes (they no longer resume by themselves)
#   · notices: «⏳ وقف شراء مؤقت» when bots close (which bot · from where · how many levels missing) · «💵 توفر دولار» when the unreserved
#     dollars cover at least one saved level of a waiting bot — at most once every 10 hours · the per-level 📦 lines stay quiet for a bot
#     that only the temporary valve holds · the wallet's «💵 نفد الدولار الحر» goes to 🛡️ without Telegram while the temporary pause is on
#   · the owner opens ONE bot («🔓 افتح المؤقت» on its card · control temp_open): the dashboard lowers the temporary floor exactly to the
#     levels the unreserved dollars cover from the beginning (the engine buys those in one order at the market price and keeps the rest
#     behind the new floor — it can't reach the DCA's dollars) · all covered ⇒ the valve opens fully and closes again by itself when the
#     dollars are short · nothing saved ⇒ it opens
#   · the guard paused / the switch off never open anything · 🪜 the step bot the same · the engines are unchanged (state fields only —
#     no order from the dashboard)
#   python3 devtests/step/patches/p99_temp_pause.py Holy_Dashboard.pyw
import os, sys

LOW = r'''def _cw_low(g, wid, q, rec, snap, now):
    """① رسالة واحدة للمحفظة حين لا يكفي الدولار الحر **غير المحجوز** أمر الشراء — ⏳ v3.36.58: دولار DCA البيعي (وDCA+) المحجوز لإعادة
    شراء عملته ما ينحسب · ولا تذكير · مع وقف الشراء المؤقت تبقى في 🛡️ بلا تيليغرام (رسالتا «⏳ وقف شراء مؤقت» و«💵 توفر دولار» تكفيان) ·
    «✅ عاد» بس لما ماكو بوت بالمؤقت (وإلا الشراء ينتظر قرارك)."""
    key = f"low:{wid}:{q}"
    av = float(rec.get("avail") or 0)
    held = _cw_held(wid, q)
    dh = float(rec.get("dca_hold") or 0)
    eff = av - held
    un = eff - dh
    rec["held"], rec["eff"], rec["free_u"] = round(held, 6), round(eff, 6), round(un, 6)
    mn = float(rec.get("min_next") or 0)
    who = sorted(((float(i.get("usd") or 0), i) for i in (snap.get("bots") or {}).values()
                  if i.get("quote") == q and float(i.get("usd") or 0) > 0 and not i.get("destruct")), key=lambda t: t[0])
    op = next((e for e in g.get("events") or [] if e.get("key") == key and e.get("status") == "open"), None)
    tp_on = g.get("cash_pause", True) is not False
    if mn > 0 and un < mn:
        rec.pop("ok_since", None)
        rec.setdefault("low_since", now)
        wait = [(u, i) for u, i in who if un < u]
        names = " · ".join(f"{_cw_lbl(i)} ({u:g}$)" for u, i in wait[:8]) + (f" · و{len(wait) - 8} غيرها" if len(wait) > 8 else "")
        paused = [_cw_lbl(r) for r in _cw_recs(wid, q)]
        det = (f"المتاح {av:.2f} {q}"
               + (f" · منه {dh:.2f} محجوز لـ DCA البيعي (لإعادة شراء عملته)" if dh > 0.005 else "")
               + (f" · و{held:.2f} للمستويات المحفوظة في البوتات المغلقة مؤقتاً" if held > 0.005 else "")
               + f" · أصغر أمر شراء {mn:.2f} {q}\n"
               + (f"⏳ تنتظر الدولار: {names}\n" if names else "")
               + (f"⏳ وقف الشراء المؤقت: {' · '.join(paused)} — المستويات تُحفظ ولا تُشترى، ولا تأخذ دولار غيرها، ولا تُفتح إلا بقرارك\n" if paused else "")
               + "البوتات تكمل البيع — وحين يتوفر دولار تصلك «💵 توفر دولار» (مرة كل 10 ساعات على الأكثر).")
        _gd_event(g, key, "🟡", f"💵 نفد الدولار الحر — {q}", det, wid=wid, sym=q, kind="low_quote", tg=not tp_on)
        return
    rec.pop("low_since", None)
    if not op:
        rec.pop("ok_since", None)
        return
    rec.setdefault("ok_since", now)
    if now - float(rec["ok_since"]) < CW_BACK_S:
        return                                          # يغطي الآن — ننتظر نصف ساعة قبل «عاد» (ما نفتح ونسكّر مع كل دولار)
    _gd_resolve(g, key, note=f"عاد الدولار: المتاح {av:.2f} {q}")
    rec.pop("ok_since", None)
    if _cw_recs(wid, q):
        return                                          # ⏳ بوتات بالمؤقت ⇒ «💵 توفر دولار» من _cash_watch (والفتح بقرارك)
    _gd_event(g, f"back:{wid}:{q}:{int(now)}", "🟢", f"✅ عاد الدولار الحر — {q}",
              f"المتاح {av:.2f} {q} يغطي أمر الشراء ({mn:.2f} {q}) منذ {CW_BACK_S // 60} دقيقة — تعود البوتات إلى الشراء",
              wid=wid, sym=q, kind="quote_back", status="info")


'''

TP = r'''def _tp_kind(b):
    return str(((b or {}).get("cfg") or {}).get("bot_type") or "grid")


def _tp_stored(b, st, cp):
    """⏳ المحفوظ خلف الأرضية [(سعر، كمية)] من الأعلى — ♾️ ➕ 🎚️ مخزن الإيقاف · 🪜 الخانات اللي قطعها السعر + نافذته (نفس عدّاد الكرت)"""
    out = []
    for v in (_accx_src(b, st, "buy", cp) or {}).values():
        try:
            p, q = float((v or {}).get("target_price") or 0), float((v or {}).get("locked_qty") or 0)
        except Exception:
            continue
        if p > 0 and q > 0 and _accx_ok(b, "buy", p):
            out.append((p, q))
    out.sort(key=lambda t: -t[0])
    return out


def _tp_cover(lv, cp, budget):
    """كم مستوى من البداية يغطيه الدولار (سعر الشراء ≤ السعر × 1.005 ولا فوق المستوى · هامش 0.2%) — المستويات بنفس السعر
    (أجزاء 🪜) ما تنقسم: الأرضية ما تفصل بينها ⇒ (العدد، الكلفة)"""
    cap = float(cp) * 1.005
    k, cost, i = 0, 0.0, 0
    while i < len(lv):
        p, j, gq = lv[i][0], i, 0.0
        while j < len(lv) and abs(lv[j][0] - p) <= p * 1e-9:
            gq += lv[j][1]
            j += 1
        c_ = gq * min(cap, p)
        if cost + c_ > max(0.0, budget) * 0.998 + 1e-12:
            break
        cost += c_
        k = i = j
    return k, round(cost, 6)


def _tp_gap_top(b, st, cp):
    """⏳ مكان الغلق = بداية الفجوة (كأنه مغلق من قبل): فوق أعلى مستوى شراء يريده البوت ولا أمر حي له — المحفوظ · ذاكرته اللي قطعها
    السعر · مستويات اللحاق فوق السعر (فجوة المحرك نفسها: أدنى بيع ÷ (1+g)² · ➕ ÷ (1+g)^(n+1)) · 🪜 خانات الشراء اللي قطعها السعر بلا أمر.
    والحد الأدنى: تحت أدنى شراء حي بنصف درجة (الحي ممول — يبقى) · ولا شراء حي ⇒ السعر الآن. ⇒ (الأرضية، المستويات الناقصة فوق السعر)"""
    c = (b or {}).get("cfg") or {}
    if cp <= 0:
        return 0.0, 0
    if _tp_kind(b) == "grid_step":
        G = float((st.get("step") or {}).get("G") or c.get("grid_percentage") or 0.03) or 0.03
        live, idle = [], []
        for s in (st.get("slots") or {}).values():
            if not isinstance(s, dict) or s.get("side") != "buy":
                continue
            try:
                p = float(s.get("bp") or 0)
            except Exception:
                continue
            if p <= 0:
                continue
            o = s.get("o") or {}
            (live if (o.get("id") and o.get("st") == "live") else idle).append(p)
        # 🪜 أجزاء المجموعة بنفس السعر: أول خانة بلا أمر (الأعلى) = بداية الفجوة ⇒ فوقها بقليل — أجزاء مجموعتها الحية تنزل تحت
        #    الأرضية معها (تنسحب · دولارها لمخزنه) ⇒ ولا جزء ينادي · المجموعات الأعلى الحية تبقى
        cand = [max(idle) * (1 + G / 8)] if idle else ([min(live) * (1 - G / 2)] if live else [cp])
        return float(f"{max(cand):.10g}"), len([x for x in idle if x >= cp])
    g = float(c.get("grid_percentage") or 0.008) or 0.008
    lb = []
    for i in (st.get("limit_buys") or {}).values():
        try:
            x = float((i or {}).get("target_price") or 0)
        except Exception:
            continue
        if x > 0:
            lb.append(x)
    want = []
    for v in (st.get("accum_buys") or {}).values():
        try:
            want.append(float((v or {}).get("target_price") or 0))
        except Exception:
            pass
    for k_, v in (st.get("virtual_buys") or {}).items():
        try:
            p = float((v or {}).get("target_price") or k_)
        except Exception:
            continue
        if p >= cp:
            want.append(p)
    sells = []
    for d_ in ("limit_sells", "virtual_sells", "accum_sells"):
        for v in (st.get(d_) or {}).values():
            try:
                x = float((v or {}).get("target_price") or 0)
            except Exception:
                continue
            if x > 0:
                sells.append(x)
    gap = 2
    if _tp_kind(b) == "grid_plus":
        try:
            off = float(c.get("buy_offset") or 0)
            if 0 < off < 0.9:
                gap = max(1, int(round(math.log(1.0 / (1.0 - off)) / math.log(1.0 + g)))) + 1
        except Exception:
            gap = 2
    if sells:
        p, n_ = min(sells) / (1 + g) ** gap, 0
        while p >= cp and n_ < 500:
            if not any(abs(p - x) <= p * g * 0.3 for x in lb) and _accx_ok(b, "buy", p):
                want.append(p)
            p /= (1 + g)
            n_ += 1
    want = [x for x in want if x > 0]
    cand = [max(want) * (1 + g / 8)] if want else []
    cand.append(min(lb) * (1 - g / 2) if lb else cp)
    return float(f"{max(cand):.10g}"), len([x for x in want if x >= cp])


def _tp_live_under(b, st, lim):
    """دولار أوامر الشراء الحية تحت الحد (تنسحب للمخزن ⇒ دولارها يتحرر — ملك مخزن هذا البوت)"""
    s = 0.0
    if _tp_kind(b) == "grid_step":
        for x in (st.get("slots") or {}).values():
            o = (x or {}).get("o") or {}
            if isinstance(x, dict) and x.get("side") == "buy" and o.get("id") and o.get("st") == "live":
                try:
                    p = float(x.get("bp") or 0)
                    if 0 < p < lim:
                        s += p * float(x.get("q") or 0)
                except Exception:
                    pass
        return s
    for i in (st.get("limit_buys") or {}).values():
        try:
            p = float(i.get("target_price") or 0)
            if 0 < p < lim:
                s += p * float(i.get("locked_qty") or 0)
        except Exception:
            pass
    return s


def _tp_close(k, i, b, wid, q, u, now, d):
    """⏳ يغلق المؤقت من بداية الفجوة — الأرضية بالمحرك = الأعلى من (أرضيتك · المؤقت) · حقول التحكم فقط"""
    sp = paths_of(b)[0]
    st = read_retry(sp)
    if not isinstance(st, dict):
        return None
    cp = float(i.get("cp") or st.get("current_price") or 0)
    if cp <= 0:
        return None
    own = float(st.get("buy_floor") or 0)                # إيقافك (إن كان) — حنفيتك تبقى كما هي
    if own <= 0 and st.get("pause_buy"):
        own = float(f"{cp:.10g}")                        # ضغطتَ ⏸ والمحرك لم يثبّته بعد ⇒ من السعر الآن
    fl, n = _tp_gap_top(b, st, cp)
    if fl <= 0:
        return None
    eng = max(own, fl)
    freed = _tp_live_under(b, st, eng)
    if abs(eng - float(st.get("buy_floor") or 0)) > max(1e-12, eng * 1e-9) or st.get("pause_buy"):
        if not save_state_keys(sp, {"buy_floor": eng, "pause_buy": False}):
            return None
    d["bots"][k] = {"v": 2, "wid": wid, "q": q, "sym": i.get("sym"), "type": i.get("type"), "temp": fl, "own": own, "need": u,
                    "ts": now, "freed": round(freed, 6), "n0": n}
    d["seen"].pop(k, None)
    (d.get("opened") or {}).pop(k, None)
    return (i, fl, n, own)


def _tp_sync(k, r, b, st):
    """🚰 الأرضية بالمحرك = الأعلى من الحنفيتين — تغيّرت من مكان ثاني ⇒ فوق المؤقت = حنفيتك · تحته = المؤقت يبقى مغلقاً"""
    cur = float(st.get("buy_floor") or 0)
    temp, own = float(r.get("temp") or 0), float(r.get("own") or 0)
    exp = max(own, temp)
    if abs(cur - exp) <= max(1e-12, exp * 1e-7):
        return False
    if cur > temp * (1 + 1e-7):
        r["own"] = cur                                  # رُفعت أو نزلت أرضيتك فوق المؤقت ⇒ هي حنفيتك
        return True
    r["own"] = 0.0
    if save_state_keys(paths_of(b)[0], {"buy_floor": temp, "pause_buy": False}):
        _dash_event(r.get("sym") or "", f"⏳ وقف الشراء المؤقت ما زال مغلقاً من {_px_s(temp)} — أُعيدت الأرضية (يُفتح بزر «🔓 افتح المؤقت» فقط)")
    return True


def _tp_rec(bdir):
    try:
        r = (_cw_cached().get("bots") or {}).get(_cw_key(bdir))
        return r if isinstance(r, dict) and r.get("v") == 2 else None
    except Exception:
        return None


def _tp_own_floor(bdir, eng):
    """🚰 أرضيتك أنت (حنفيتك) — للكرت وأزراره · بلا مؤقت = أرضية المحرك"""
    r = _tp_rec(bdir)
    return float(r.get("own") or 0) if r else eng


def _tp_temp_floor(bdir):
    r = _tp_rec(bdir)
    return float(r.get("temp") or 0) if r else 0.0


def _tp_silent(bdir):
    """📦 أسطر عبور الدرجات تسكت للبوت اللي يحبسه المؤقت وحده (ما ينادي)"""
    r = _tp_rec(bdir)
    return bool(r) and float(r.get("own") or 0) <= 0


def _tp_budget(r, d=None):
    """الدولار الحر غير المحجوز لهذا البوت = المتاح − المحجوز لـ DCA البيعي − ما حرّرته أوامر البوتات المغلقة الأخرى (ودولار مخزنه له)"""
    try:
        g = _gd_load()
        rec = ((((g.get("wallets") or {}).get(r.get("wid")) or {}).get("quotes") or {}).get(r.get("q")) or {})
        av = float(rec.get("avail") or 0)
        dh = float(rec.get("dca_hold") or 0)
    except Exception:
        return 0.0
    d = d if d is not None else _cw_load()
    held = sum(float(x.get("freed") or 0) for x in (d.get("bots") or {}).values()
               if isinstance(x, dict) and x.get("wid") == r.get("wid") and x.get("q") == r.get("q") and x is not r)
    return max(0.0, av - dh - held)


def _tp_owner(b, st, action, value, cp):
    """🚰 حنفيتان على أنبوب واحد: إيقافك (⏸) والمؤقت (⏳) — الشراء يمشي بس لما الثنتان مفتوحتان · ولا وحدة تفتح الثانية.
    None = البوت مو بالمؤقت (الأزرار تشتغل مثل قبل)"""
    with _CW_LOCK:
        d = _cw_load()
        k = _cw_key(b["dir"])
        r = d["bots"].get(k)
        if not isinstance(r, dict) or r.get("v") != 2:
            return None
        temp, own = float(r.get("temp") or 0), float(r.get("own") or 0)
        if action == "pause_buy":
            if own > 0:
                return {"ok": True, "msg": "⏸ الشراء موقوف أصلاً (إيقافك) — ووقف الشراء المؤقت مغلق أيضاً"}
            if cp <= 0:
                return {"ok": False, "msg": "سعر السوق غير متاح الآن — أعد المحاولة بعد ثوانٍ"}
            own = float(f"{cp:.10g}")
            msg = f"⏸ أُوقف الشراء من {_px_s(own)} (إيقافك) — ووقف الشراء المؤقت مغلق أيضاً من {_px_s(temp)}: لا شراء حتى يُفتح الاثنان"
        else:
            try:
                lim = float(value) if value not in (None, "", False) else 0.0
            except Exception:
                return {"ok": False, "msg": "اكتب سعراً صحيحاً"}
            if not (lim == lim) or lim < 0 or lim == float("inf"):
                return {"ok": False, "msg": "اكتب سعراً صحيحاً"}
            if lim > 0:
                if cp <= 0:
                    return {"ok": False, "msg": "سعر السوق غير متاح الآن — أعد المحاولة بعد ثوانٍ"}
                lim = min(lim, max(cp, own))             # 🔒 (ب٢٥) الأرضية لا تصعد فوق السوق
                own = float(f"{lim:.10g}")
                msg = f"⏸ أرضيتك {_px_s(own)} — ووقف الشراء المؤقت مغلق أيضاً من {_px_s(temp)}: لا شراء تحت الأعلى منهما"
            else:
                if own <= 0:
                    return {"ok": True, "msg": f"▶️ لا يوجد إيقاف منك — الشراء متوقف بوقف الشراء المؤقت من {_px_s(temp)}: افتحه من «🔓 افتح المؤقت» حين يتوفر دولار"}
                own = 0.0
                msg = f"▶️ رُفع إيقافك — ووقف الشراء المؤقت ما زال مغلقاً من {_px_s(temp)}: لا شراء تحته حتى تفتحه"
        if not save_state_keys(paths_of(b)[0], {"buy_floor": max(own, temp), "pause_buy": False}):
            return {"ok": False, "msg": "تعذّر حفظ ملف الحالة — أعد المحاولة بعد ثانية"}
        r["own"] = own
        save_json_atomic(CASHW_FILE, d)
    return {"ok": True, "msg": msg}


def _tp_open(b, st, cp, dry=False):
    """🔓 يفتح المؤقت لبوت واحد بقرار المالك: يشتري من البداية ما يغطيه الدولار غير المحجوز (+ دولار مخزنه هو) بأمر واحد — الأرضية
    تنزل بالضبط تحت آخر مستوى مغطى (المحرك يشتري اللي فوقها ويحفظ الباقي تحتها — ما يوصل دولار DCA) · الكل مغطى ⇒ يُفتح كلياً ويُغلق
    وحده حين يقصر الدولار · ولا محفوظ ⇒ يُفتح · dry = الأرقام فقط (نافذة التأكيد)"""
    now = time.time()
    with _CW_LOCK:
        d = _cw_load()
        k = _cw_key(b["dir"])
        r = d["bots"].get(k)
        if not isinstance(r, dict) or r.get("v") != 2:
            return {"ok": False, "msg": "البوت ليس في وقف الشراء المؤقت"}
        if cp <= 0:
            return {"ok": False, "msg": "سعر السوق غير متاح الآن — أعد المحاولة بعد ثوانٍ"}
        temp, own = float(r.get("temp") or 0), float(r.get("own") or 0)
        lv = _tp_stored(b, st, cp)
        av = _tp_budget(r, d)
        kc, cost = _tp_cover(lv, cp, av)
        first = round(lv[0][1] * min(cp * 1.005, lv[0][0]), 2) if lv else 0.0
        info = {"ok": True, "n": len(lv), "k": kc, "av": round(av, 2), "cost": round(cost, 2), "first": first, "own": own, "temp": temp,
                "one": _tp_kind(b) != "grid_step"}
        if dry:
            return info
        if lv and kc == 0:
            return {"ok": False, "msg": f"الدولار الحر غير المحجوز ({av:.2f}$) لا يكفي ولا مستوى واحداً (أول مستوى ≈ {first}$) — المؤقت يبقى مغلقاً"}
        new = 0.0 if kc >= len(lv) else float(f"{(lv[kc - 1][0] + lv[kc][0]) / 2:.10g}")
        if not save_state_keys(paths_of(b)[0], {"buy_floor": max(own, new), "pause_buy": False}):
            return {"ok": False, "msg": "تعذّر حفظ ملف الحالة — أعد المحاولة بعد ثانية"}
        if new <= 0:
            d["bots"].pop(k, None)
            d.setdefault("opened", {})[k] = now
        else:
            r["temp"], r["freed"], r["opened"] = new, round(max(0.0, float(r.get("freed") or 0) - cost), 6), now
            r["n"], r["k"] = len(lv) - kc, 0
        save_json_atomic(CASHW_FILE, d)
    sym = b.get("symbol") or ""
    one = "" if _tp_kind(b) == "grid_step" else "بأمر واحد "     # 🪜 يشتري خاناته واحدة واحدة (بسعر السوق)
    if not lv:
        msg = "🔓 فُتح وقف الشراء المؤقت — لا مستويات محفوظة: يعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار"
    elif new <= 0:
        msg = (f"🔓 فُتح وقف الشراء المؤقت — تُشترى المستويات المحفوظة كلها ({len(lv)}) من البداية {one}بسعر السوق (≈ {cost:.2f}$) · "
               "ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار")
    else:
        msg = (f"🔓 فُتح وقف الشراء المؤقت لـ {kc} من {len(lv)} — تُشترى من البداية {one}بسعر السوق (≈ {cost:.2f}$) · "
               f"والباقي ({len(lv) - kc}) يبقى محفوظاً والمؤقت مغلقاً تحته من {_px_s(new)}")
    if own > 0:
        msg += f" · إيقافك (⏸ {_px_s(own)}) كما هو: لا شراء تحته"
    _dash_event(sym, msg)
    return {"ok": True, "msg": msg}


def _cash_watch(g, now, snaps):
    """⏳ v3.36.58 — وقف الشراء المؤقت لبوتات الشبكة (♾️ ➕ 🎚️ 🪜): الدولار الحر غير المحجوز لا يكفي أمر البوت القادم (فحصان متتاليان ·
    فحص واحد لبوت فتحته خلال الساعتين الماضيتين) ⇒ يُغلق من بداية الفجوة · ولا يُفتح إلا بقرار المالك · «💵 توفر دولار» مرة كل 10 ساعات
    على الأكثر · بقي مغلقاً والدولار قصر فوقه ⇒ يُغلق من البداية الجديدة (المحفوظ يزيد)"""
    on = g.get("cash_pause", True) is not False
    with _CW_LOCK:
        d = _cw_load()
        d.setdefault("opened", {})
        d.setdefault("avail", {})
        ch = False
        seen_now = set()
        for s in snaps or []:
            if not s.get("ok_bal"):
                continue
            wid = s.get("wid")
            Wq = (((g.get("wallets") or {}).get(wid) or {}).get("quotes") or {})
            for q, rec in Wq.items():
                if now - float(rec.get("ts") or 0) > 120:
                    continue                            # ما انقرأ بهالجولة
                un = float(rec.get("free_u", rec.get("eff", rec.get("avail") or 0)) or 0)
                dh = float(rec.get("dca_hold") or 0)
                bots = sorted([(float(i.get("usd") or 0), _cw_key(i["dir"]), i) for i in (s.get("bots") or {}).values()
                               if i.get("type") in _CW_TYPES and i.get("dir") and i.get("quote") == q and float(i.get("usd") or 0) > 0
                               and not i.get("destruct")], key=lambda t: t[0])
                wq = f"{wid}|{q}"
                closed, waiting = [], []
                for u, k, i in bots:
                    b = _cw_bot(i["dir"])
                    if not b:
                        continue
                    r = d["bots"].get(k)
                    short = un < u and i.get("alive")
                    if short:
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": int(sv.get("n") or 0) + 1, "need": u, "ts": now}
                        seen_now.add(k)
                        ch = True
                    if isinstance(r, dict) and r.get("v") == 2:
                        st = read_retry(paths_of(b)[0])
                        if not isinstance(st, dict):
                            continue
                        if _tp_sync(k, r, b, st):
                            ch = True
                            st = read_retry(paths_of(b)[0]) or st
                        cp = float(i.get("cp") or st.get("current_price") or 0)
                        if on and short and d["seen"][k]["n"] >= CW_SEEN and cp > 0:
                            fl, n = _tp_gap_top(b, st, cp)    # ما زال قاصراً وهو فوق الأرضية ⇒ يُغلق من البداية الجديدة
                            if fl > float(r.get("temp") or 0) * (1 + max(0.001, float(i.get("g") or 0.006)) / 2):   # نصف درجة على الأقل (مستويات جديدة فوقه — لا زحف بالتقريب)
                                own = float(r.get("own") or 0)
                                add = _tp_live_under(b, st, max(own, fl)) - _tp_live_under(b, st, max(own, float(r.get("temp") or 0)))
                                if save_state_keys(paths_of(b)[0], {"buy_floor": max(own, fl), "pause_buy": False}):
                                    r["temp"], r["freed"] = fl, round(float(r.get("freed") or 0) + max(0.0, add), 6)
                                    closed.append((i, fl, n, own))
                                    ch = True
                                    st = read_retry(paths_of(b)[0]) or st
                        lv = _tp_stored(b, st, cp) if cp > 0 else []
                        kc, _c = _tp_cover(lv, cp, un + float(r.get("freed") or 0)) if lv else (0, 0.0)
                        if r.get("n") != len(lv) or r.get("k") != kc:
                            r["n"], r["k"] = len(lv), kc
                            ch = True
                        if lv:
                            waiting.append((i, r, lv, kc, cp))
                        continue
                    if not (on and short):
                        continue
                    recent = now - float(d["opened"].get(k) or 0) < 7200
                    if d["seen"][k]["n"] < CW_SEEN and not recent and dh <= 0.005:
                        continue                        # تأكيد بفحصين قبل الغلق — إلا دولار DCA محجوز بالمحفظة (يُغلق من أول فحص: لا يمسه)
                    res = _tp_close(k, i, b, wid, q, u, now, d)
                    if res:
                        closed.append(res)
                        ch = True
                if closed:
                    lines = []
                    for i, fl, n, own in closed:
                        lines.append(f"{_cw_lbl(i)} من {_px_s(fl)}" + (f" — ناقصه {n} مستوى" if n else "")
                                     + (f" (وإيقافك ⏸ {_px_s(own)})" if own > 0 else ""))
                        _dash_event(i.get("sym") or "", f"⏳ وقف شراء مؤقت من {_px_s(fl)}" + (f" — ناقصه {n} مستوى" if n else "")
                                    + f" · الدولار الحر غير المحجوز {max(0.0, un):.2f}$ لا يكفي أمر الشراء — المستويات تُحفظ ولا تُشترى، ولا يأخذ دولار غيره، ولا يُفتح إلا بقرارك")
                    _gd_event(g, f"tpc:{wid}:{q}:{int(now)}", "🟡", f"⏳ وقف شراء مؤقت — {q}",
                              "أُغلق الشراء مؤقتاً: " + " · ".join(lines) + "\n"
                              + f"الدولار الحر غير المحجوز {max(0.0, un):.2f} {q}" + (f" · محجوز لـ DCA البيعي {dh:.2f} {q}" if dh > 0.005 else "") + "\n"
                              + "كل مستوى تحت هذا الحد يُحفظ ولا يُشترى، ولا يأخذ دولار بوت آخر، ولا يُفتح وحده — وفوقه يبيع ويشتري كالمعتاد. "
                              + "حين يتوفر دولار تصلك رسالة، وتفتح البوت الذي تريده من «🔓 افتح المؤقت» في بطاقته.",
                              wid=wid, sym=q, kind="tp_close", status="info")
                if on and waiting and any(kc > 0 for *_, kc, _cp in waiting) and now - float(d["avail"].get(wq) or 0) >= TP_AVAIL_S:
                    rows = []
                    for i, r, lv, kc, cp in waiting:
                        need = round(sum(q_ * min(cp * 1.005, p) for p, q_ in lv), 2)
                        rows.append(f"{_cw_lbl(i)}: محفوظ {len(lv)} (≈ {need}$) — يكفي الدولار {kc} منها")
                    _gd_event(g, f"tpa:{wid}:{q}:{int(now)}", "🟢", f"💵 توفر دولار — {q}",
                              f"الدولار الحر غير المحجوز {un:.2f} {q}" + (f" (محجوز لـ DCA البيعي {dh:.2f})" if dh > 0.005 else "") + "\n"
                              + "⏳ في وقف الشراء المؤقت: " + " · ".join(rows) + "\n"
                              + "افتح البوت الذي تريده من «🔓 افتح المؤقت» في بطاقته — يشتري من البداية بأمر واحد بقدر الدولار، ويبقى الباقي محفوظاً. "
                              + "(رسالة كل 10 ساعات على الأكثر)", wid=wid, sym=q, kind="tp_avail", status="info")
                    d["avail"][wq] = now
                    ch = True
        for k in list(d["seen"]):
            if k not in seen_now:
                d["seen"].pop(k, None)
                ch = True
        for k in list(d["bots"]):
            if not os.path.isdir(os.path.join(ROOT, k)):
                d["bots"].pop(k, None)                  # البوت انحذف
                ch = True
        for k in list(d["opened"]):
            if now - float(d["opened"][k] or 0) > 86400:
                d["opened"].pop(k, None)
                ch = True
        if ch:
            save_json_atomic(CASHW_FILE, d)
    _CW_LOWQ.clear()
    _CW_LOWQ.update(str(e.get("sym") or "") for e in g.get("events") or [] if e.get("kind") == "low_quote" and e.get("status") == "open")


def _cw_release_all(why):
    """⏳ v3.36.58: وقف الشراء المؤقت يُفتح بقرار المالك فقط — إيقاف الرقابة أو إطفاء المفتاح لا يفتح شيئاً (يبقى مغلقاً حتى تفتحه)"""
    return 0


def _cw_card(bdir):
    """③ شارة الكرت: ⏳ بالمؤقت {tp, temp, own, n (المحفوظ), k (يغطيه الدولار)} · أو ينتظر دولاراً بلا غلق {need, auto: False}"""
    try:
        d = _cw_cached()
        k = _cw_key(bdir)
        r = (d.get("bots") or {}).get(k)
        if isinstance(r, dict) and r.get("v") == 2:
            return {"tp": True, "need": round(float(r.get("need") or 0), 4), "temp": float(r.get("temp") or 0),
                    "own": float(r.get("own") or 0), "n": int(r.get("n") or 0), "k": int(r.get("k") or 0)}
        sv = (d.get("seen") or {}).get(k)
        if isinstance(sv, dict) and time.time() - float(sv.get("ts") or 0) < 3 * GUARD_EVERY:
            return {"need": round(float(sv.get("need") or 0), 4), "auto": False}
    except Exception:
        pass
    return None


'''

R = [
    # ── the file: records of the old automatic pause carry on as temporary closes
    ('''def _cw_load():
    d = load_json(CASHW_FILE)
    d = d if isinstance(d, dict) else {}
    for k in ("bots", "seen", "ok"):
        if not isinstance(d.get(k), dict):
            d[k] = {}
    return d''', '''TP_AVAIL_S = 36000            # ⏳ v3.36.58: «💵 توفر دولار» مرة كل 10 ساعات على الأكثر (لكل محفظة وعملة تسعير)


def _cw_load():
    d = load_json(CASHW_FILE)
    d = d if isinstance(d, dict) else {}
    for k in ("bots", "seen", "ok", "opened", "avail"):
        if not isinstance(d.get(k), dict):
            d[k] = {}
    for k, r in list(d["bots"].items()):                # ⏳ v3.36.58: سجلات الإيقاف التلقائي القديم ⇒ وقف شراء مؤقت (ما يُستأنف وحده بعد)
        if not isinstance(r, dict):
            d["bots"].pop(k, None)
        elif r.get("v") != 2:
            if r.get("hands_off"):
                d["bots"].pop(k, None)                  # المالك كان تصرّف بنفسه ⇒ ما في مؤقت
            else:
                d["bots"][k] = {"v": 2, "wid": r.get("wid"), "q": r.get("q"), "sym": r.get("sym"), "type": r.get("type"),
                                "temp": float(r.get("set") or 0), "own": float(r.get("orig") or 0), "need": float(r.get("need") or 0),
                                "ts": float(r.get("ts") or time.time()), "freed": float(r.get("freed") or 0), "mig": True}
    return d'''),
    ('''def _cw_recs(wid, q, d=None):
    d = d if d is not None else _cw_cached()
    return [r for r in (d.get("bots") or {}).values() if r.get("wid") == wid and r.get("q") == q and not r.get("hands_off")]''',
     '''def _cw_recs(wid, q, d=None):
    d = d if d is not None else _cw_cached()
    return [r for r in (d.get("bots") or {}).values() if isinstance(r, dict) and r.get("wid") == wid and r.get("q") == q and r.get("v") == 2]'''),
    # ── the sell DCA's dollars are reserved (the guard's snapshot)
    ('''            if is_dca:
                side = "buy" if bt == "dca_buy" else "sell"''', '''            if bt == "dca" and st.get("phase") in ("selling", "buying"):       # ⏳ v3.36.58: دولار DCA البيعي (وDCA+) محجوز لإعادة شراء عملته
                try:
                    q["dca_hold"] = float(q.get("dca_hold") or 0) + max(0.0, float(st.get("total_net") or 0))
                except Exception:
                    pass
            if is_dca:
                side = "buy" if bt == "dca_buy" else "sell"'''),
    ('''                       bots_frozen=round(float(qi.get("bots_frozen") or 0), 6),
                       min_next=float(qi.get("min_next") or 0), ts=now)''',
     '''                       bots_frozen=round(float(qi.get("bots_frozen") or 0), 6),
                       min_next=float(qi.get("min_next") or 0), dca_hold=round(float(qi.get("dca_hold") or 0), 6), ts=now)'''),
    # ── the card: the owner's own floor (his valve) · the temporary floor apart
    ('''            "floor": float(st.get("buy_floor") or 0), "ceil": float(st.get("sell_ceiling") or 0),
            "n_buys": len(st.get("limit_buys") or {}), "n_sells": len(st.get("limit_sells") or {}),''',
     '''            "floor": _tp_own_floor(b["dir"], float(st.get("buy_floor") or 0)), "ceil": float(st.get("sell_ceiling") or 0),   # 🚰 v3.36.58: حنفيتك
            "tfloor": _tp_temp_floor(b["dir"]),                                                                              # ⏳ المؤقت
            "n_buys": len(st.get("limit_buys") or {}), "n_sells": len(st.get("limit_sells") or {}),'''),
    # ── the 📦 crossing lines stay quiet for a bot only the temporary valve holds
    ('''        lv = _accx_levels(b, st, side, cp)
        new = {f"{p:.10g}" for p, _ in lv} - set(seen)
        if not new:
            continue''', '''        lv = _accx_levels(b, st, side, cp)
        new = {f"{p:.10g}" for p, _ in lv} - set(seen)
        if not new:
            continue
        if side == "buy" and _tp_silent(b["dir"]):      # ⏳ v3.36.58: المؤقت وحده ⇒ ما ينادي (تنحسب بصمت · الإيقاف منك يبلّغ)
            rec["k"] = seen + sorted(new)
            _ACCX["dirty"] = True
            continue'''),
    # ── the guard's switch: closes only — never opens
    ('''            msg.append("⏸💵 إيقاف الشراء تلقائياً حين ينفد الدولار " + ("مفعّل" if g["cash_pause"] else
                                                                       "معطّل — البوتات الموقوفة تلقائياً تُستأنف بالفحص القادم"))''',
     '''            msg.append("⏳ وقف الشراء المؤقت حين ينفد الدولار " + ("مفعّل" if g["cash_pause"] else
                                                                  "معطّل — لا يُغلق بوت جديد، والمغلقة تبقى مغلقة حتى تفتحها"))'''),
    # ── the buttons: the owner's valve · the temporary one
    ('''    if action in ("pause_buy", "pause_sell"):
        _b = action == "pause_buy"
        _lk, _fk = ("buy_floor", "pause_buy") if _b else ("sell_ceiling", "pause_sell")''',
     '''    if action in ("pause_buy", "accum_buy"):              # 🚰 v3.36.58: البوت بالمؤقت ⇒ أزرارك تحرّك حنفيتك وحدها
        _tr = _tp_owner(b, st, action, value, _cpx)
        if _tr is not None:
            return _tr
    if action in ("temp_open", "temp_info"):              # 🔓 v3.36.58: فتح المؤقت بقرارك (حقول التحكم فقط — المحرك يشتري)
        return _tp_open(b, st, _cpx, dry=action == "temp_info")
    if action in ("pause_buy", "pause_sell"):
        _b = action == "pause_buy"
        _lk, _fk = ("buy_floor", "pause_buy") if _b else ("sell_ceiling", "pause_sell")'''),
    # ── the page: the chip · the open dialog · the owner's resume while the temporary valve is closed
    ('''  const CW=b.cashw;if(CW&&+CW.need>0)c+=`<span class="chip cashw"''',
     '''  const CW=b.cashw;
  if(CW&&CW.tp)c+=(+CW.k>0?`<span class="chip cashw tpo" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--green);border-color:rgb(var(--green-rgb)/.5);background:rgb(var(--green-rgb)/.10)"
    title="توفر دولار غير محجوز يكفي ${CW.k} من ${CW.n} محفوظة — اضغط لتفتح وقف الشراء المؤقت (يشتري من البداية بقدر الدولار)">🔓 افتح المؤقت (${+CW.n||0})</span>`
    :`<span class="chip cashw tpc" onclick="event.stopPropagation();tempOpen('${b.dir}')" style="cursor:pointer;color:var(--amber);border-color:rgb(var(--amber2-rgb)/.45);background:rgb(var(--amber2-rgb)/.08)"
    title="وقف الشراء المؤقت من ${f4(CW.temp)} — الدولار الحر غير المحجوز لا يكفي: المستويات تُحفظ ولا تُشترى، ولا يأخذ دولار غيره، ولا يُفتح إلا بقرارك · فوقه يبيع ويشتري كالمعتاد">⏳ مؤقت (${+CW.n||0})</span>`);
  else if(CW&&+CW.need>0)c+=`<span class="chip cashw"'''),
    ('''function accChipsOf(b){''', '''async function tempOpen(dir){const b=botOf(dir)||{};let I=null;      // 🔓 v3.36.58: فتح وقف الشراء المؤقت — بقرارك
  try{I=await api('/api/control',{dir,action:'temp_info'},true)}catch(e){}
  if(!I||!I.ok){toast((I&&I.msg)||'تعذر الاتصال',false);return}
  const all=I.k>=I.n,can=!I.n||I.k>0;
  const txt=!I.n?'لا توجد مستويات محفوظة — يعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار.'
    :!I.k?`الدولار الحر غير المحجوز (${I.av}$) لا يكفي ولا مستوى واحداً (أول مستوى ≈ ${I.first}$) — يبقى مغلقاً.`
    :all?`يكفي الكل: تُشترى المستويات المحفوظة (${I.n}) من البداية <b>${I.one?'بأمر واحد ':''}بسعر السوق</b> (≈ ${I.cost}$) ويعود البوت إلى الشراء العادي، ويُغلق المؤقت وحده إذا قصر الدولار.`
    :`يكفي ${I.k} من ${I.n}: تُشترى من البداية <b>${I.one?'بأمر واحد ':''}بسعر السوق</b> (≈ ${I.cost}$)، والباقي (${I.n-I.k}) يبقى محفوظاً والمؤقت مغلقاً تحته.`;
  showDialog(`<h2>🔓 وقف الشراء المؤقت — ${gEsc(b.symbol||'')}</h2>
    <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:10px">مغلق من <b class="num">${f4(I.temp)}</b> · المحفوظ <b>${I.n}</b> مستوى · الدولار الحر غير المحجوز (مع دولار مخزنه): <b>${I.av}$</b> — دولار DCA البيعي لا يُحسب.</p>
    <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:14px">${txt}${I.own>0?` · إيقافك (⏸ ${f4(I.own)}) يبقى كما هو: لا شراء تحته.`:''}</p>
    <div class="mbtns">${can?`<button class="primary" onclick="hideModal();ctl('${dir}','temp_open')">🔓 افتح</button>`:''}<button onclick="hideModal()">رجوع</button></div>`)}
function accChipsOf(b){'''),
    ('''  const buy=side==='buy',limOn=buy?b.floor>0:b.ceil>0,pend=buy?b.pause_buy:b.pause_sell;
  // ▶️ 🔐 v3.21.10 (ب٢٦): الاستئناف ينفّذ أمر سوق ⇒ نافذة تأكيد بالأرقام أول (لمسة غلط ما تصرف فلوس)
  if(limOn){resumeConfirm(b,side);return}''', '''  const buy=side==='buy',limOn=buy?b.floor>0:b.ceil>0,pend=buy?b.pause_buy:b.pause_sell;
  if(buy&&limOn&&b.cashw&&b.cashw.tp){                 // 🚰 v3.36.58: حنفيتك تنفتح والمؤقت مغلق ⇒ ولا أمر بالسوق
    showDialog(`<h2>▶️ رفع إيقافك — ${gEsc(b.symbol)}</h2>
      <p style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:14px">يُرفع إيقافك (⏸ ${f4(b.floor)}) — لكن وقف الشراء المؤقت ما زال مغلقاً من ${f4(b.cashw.temp)}، فلا يُشترى شيء تحته حتى تفتحه («🔓 افتح المؤقت»).</p>
      <div class="mbtns"><button class="primary" onclick="hideModal();ctl('${b.dir}','accum_buy')">▶️ ارفع إيقافي</button><button onclick="hideModal()">رجوع</button></div>`);return}
  // ▶️ 🔐 v3.21.10 (ب٢٦): الاستئناف ينفّذ أمر سوق ⇒ نافذة تأكيد بالأرقام أول (لمسة غلط ما تصرف فلوس)
  if(limOn){resumeConfirm(b,side);return}'''),
    ('''    <div style="font-size:12px;line-height:1.8">⏸💵 <b>إيقاف الشراء تلقائياً حين ينفد الدولار:</b> <b style="color:${V.cash_pause?'var(--green)':'var(--mut2)'}">${V.cash_pause?'مفعّل':'متوقف'}</b><br>
      <span style="color:var(--mut2);font-size:11px">حين لا يكفي الدولار الحر أمر الشراء القادم لبوت شبكة (فحصان متتاليان) يُوقف شراءه فوق السعر بقليل — كل مستوى ينزل إليه السعر
      يُحفظ، والأرضية تتبع السعر إن صعد · وحين يعود الدولار نصف ساعة يُستأنف الشراء (يُشترى المحفوظ بأمر واحد) وتعود أرضيتك إن كانت لك أرضية.
      رسالة واحدة للمحفظة حين ينفد وأخرى حين يعود.</span></div>''',
     '''    <div style="font-size:12px;line-height:1.8">⏳💵 <b>وقف الشراء المؤقت حين ينفد الدولار:</b> <b style="color:${V.cash_pause?'var(--green)':'var(--mut2)'}">${V.cash_pause?'مفعّل':'متوقف'}</b><br>
      <span style="color:var(--mut2);font-size:11px">حين لا يكفي الدولار الحر <b>غير المحجوز</b> (دولار DCA البيعي لا يُحسب) أمر الشراء القادم لبوت شبكة أو متدرج (فحصان متتاليان) يُغلق شراؤه مؤقتاً
      من بداية الفجوة — كأنه مغلق من قبل: كل مستوى ينقصه يُحفظ ولا يُشترى، ولا يأخذ دولار غيره، وفوق الحد يبيع ويشتري كالمعتاد · لا يُفتح وحده:
      حين يتوفر دولار تصلك رسالة (مرة كل 10 ساعات على الأكثر) وتفتح البوت الذي تريده من «🔓 افتح المؤقت» في بطاقته — يشتري من البداية بقدر الدولار ويبقى الباقي محفوظاً ·
      إيقافك (⏸) حنفية مستقلة: لا يفتح أحدهما الآخر.</span></div>'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    # the two regions: the wallet message · the watcher and the card chip
    a0, a1 = s.index("def _cw_low(g, wid, q, rec, snap, now):"), s.index("def _cw_bot(d):")
    s = s[:a0] + LOW + s[a1:]
    b0, b1 = s.index("def _cw_pause(k, i, r, d, wid, q, eff, now):"), s.index("def guard_scan(force=False):")
    s = s[:b0] + TP + s[b1:]
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for gone in ("_cw_pause(", "_cw_restore("):
        if gone in s:
            print(f"❌ {gone} still referenced"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ 2 regions + {len(R)} replacements · ⏳ the temporary buy pause (two valves · from the gap start · opened by the owner) · compiles · {p}")
