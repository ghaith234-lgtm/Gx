# 💵 patch 70 (dashboard v3.36.44 · the dollar outage) — the owner (14-11): «عند نزول السعر ونفاذ الدولار يضل البوتات تصرخ تريد دولار …
#   فشنوو انسوي» ⇒ three options shown ⇒ «ثلاثتهم طبقهم · ايقاف الشراء اعلى بشوي حتى لو مسوي ايقاف شراء قبل وبوت اخر اخذ الدولار او
#   نصرف يتحرك · نافذه اعتقد موجوده تظهر تنبيه بشكل ايموجي بالكرت».
#   ① one message per wallet: «💵 نفد الدولار الحر» once (which bots wait · what each needs) and «✅ عاد الدولار الحر» once — the
#      guard's old «رصيد USDT الحر أقل من أمر شراء واحد» opened again with every 1$ the balance moved (a Telegram each time) ⇒ now it
#      closes only after the dollars covered a buy for 30 minutes · a reminder at most once a day · the recurring and value-path bots'
#      «تخطّى … الرصيد لا يكفي» at every schedule ⇒ the first one, then quiet until a buy goes through (a reminder once a day) ·
#      the engines' own dollar lines leave the 🔔 centre while the wallet message is open (they stay in the bot's 📜 log)
#   ② ⏸ auto pause-buy (🛡️ الرقابة ⇒ a switch, on by default): a grid-family bot (♾️ ➕ 🎚️ 🪜) whose wallet's free dollars stay under
#      its next buy for two scans (10 minutes) gets the same ⏸ the card's button writes — the floor a little ABOVE the price (half a
#      grid step), so the level under the price waits too · the floor follows the price up while the dollars are gone (another bot
#      took them / they were spent) · the owner's own floor is kept and comes back when the dollars do · dollars back for 30
#      minutes ⇒ buying resumes (the stored levels are bought in one order, as many as the dollars cover — the engine's own resume) ·
#      the dollars the paused bots' pulled orders free up are not counted as «dollars back» (they belong to those stored levels) ·
#      the owner touches the floor ⇒ the system lets that bot alone until the dollars come back. Only control fields, written the
#      way the ⏸ button writes them — the dashboard places and cancels no order.
#   ③ the card: «🟠 ينتظر دولار — يحتاج X$» (the title says whether its buying was paused automatically)
#   python3 devtests/step/patches/p70_cash_watch.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── the guard's bot snapshot knows the bot's folder and the size of its next buy ──
    ('''                "base": base, "quote": quote, "tracked": n_tr, "ids": _gd_bot_ids(b),
                "rungs": _gd_rungs(st, is_dca, bt == "dca_buy")}
''',
     '''                "base": base, "quote": quote, "tracked": n_tr, "ids": _gd_bot_ids(b),
                "rungs": _gd_rungs(st, is_dca, bt == "dca_buy")}
            snap["bots"][name].update(dir=b["dir"], usd=((float(cfg.get("amount") or 0) if bt == "rec_buy" else 0.0) if is_dca
                                                         else float(usd or 0)))   # 💵 v3.36.44: أمر الشراء القادم (رسالة المحفظة · الإيقاف التلقائي)
'''),
    # ── ① the wallet message ──
    ('''            key = f"low:{wid}:{q}"
            if rec["min_next"] > 0 and av < rec["min_next"]:
                _gd_event(g, key, "🟡", f"💵 رصيد {q} الحر أقل من أمر شراء واحد",
                          f"المتاح {av:.2f} {q} · أصغر أمر شراء {rec['min_next']:.2f} {q} — "
                          f"لا يستطيع السلّم الامتداد للأسفل، وسترفض المنصة أي أمر شراء جديد.",
                          wid=wid, sym=q, kind="low_quote")
            else:
                _gd_resolve(g, key)
''',
     '''            _cw_low(g, wid, q, rec, snap, now)          # 💵 v3.36.44: رسالة واحدة حين ينفد وأخرى حين يعود (كانت تنفتح مع كل دولار يتحرك)
'''),
    # ── a daily reminder is sent (its age counts from the reminder, not from the event's birth) ──
    ('''        if now - float(e.get("ts") or now) > 86400 or float(e.get("snooze_until") or 0) > now:
            e["tg"] = True                   # قديم أو مؤجّل ⇒ ما نرسل متأخراً''',
     '''        if now - float(e.get("rem_ts") or e.get("ts") or now) > 86400 or float(e.get("snooze_until") or 0) > now:
            e["tg"] = True                   # قديم أو مؤجّل ⇒ ما نرسل متأخراً (⏰ v3.36.44: التذكير يُحسب من وقته)'''),
    # ── ② the auto pause runs with every guard scan ──
    ('''            _safe(_gd_acc_scan, g, now, default=None)      # 🪙 المُراكِم: جولته · توزيعه · أوامره المعلّقة''',
     '''            _safe(_cash_watch, g, now, snaps, default=None)   # 💵 v3.36.44: ⏸ إيقاف الشراء تلقائياً حين ينفد الدولار (حقول التحكم فقط)
            _safe(_gd_acc_scan, g, now, default=None)      # 🪙 المُراكِم: جولته · توزيعه · أوامره المعلّقة'''),
    ('''def guard_scan(force=False):
    """🛡️ فحص كامل لكل المحافظ.''',
     '''# ═══════════════ 💵 v3.36.44: نفاد الدولار — رسالة واحدة للمحفظة · ⏸ إيقاف الشراء تلقائياً · شارة الكرت ═══════════════
#   المالك (14-11): «ثلاثتهم طبقهم · ايقاف الشراء اعلى بشوي حتى لو مسوي ايقاف شراء قبل وبوت اخر اخذ الدولار او نصرف يتحرك».
#   اللوحة تكتب حقول التحكم فقط (مثل زر ⏸ بالكرت بالضبط) — المحرك وحده يضع الأوامر ويلغيها.
CASHW_FILE = os.path.join(ROOT, "Holy_CashWatch.json")
CW_BACK_S = 1800              # الدولار يغطي أمر الشراء نصف ساعة متواصلة ⇒ «عاد» (قبلها كل دولار يتحرك كان يفتح التنبيه من جديد)
CW_SEEN = 2                   # فحصان متتاليان (10 دقائق) بلا دولار قبل أول إيقاف تلقائي
_CW_TYPES = ("grid", "grid_plus", "grid_range", "grid_step")
_CW_LOCK = threading.RLock()
_CW_LOWQ = set()              # عملات التسعير اللي رسالة نفادها مفتوحة (مركز 🔔 يخفي أسطر الدولار المكررة)
_CW_CACHE = {"sig": None, "d": None}
_CW_FEED = ("ما يكفي ولا درجة", "[رفض أمر شراء] الدولار الحر", "Insufficient", "[تهدئة تجميع شراء]")


def _cw_load():
    d = load_json(CASHW_FILE)
    d = d if isinstance(d, dict) else {}
    for k in ("bots", "seen", "ok"):
        if not isinstance(d.get(k), dict):
            d[k] = {}
    return d


def _cw_cached():
    """قراءة للعرض (الكرت) — من الذاكرة ما دام الملف ما تغيّر"""
    try:
        _s = os.stat(CASHW_FILE)
        sig = (_s.st_mtime_ns, _s.st_size)
    except Exception:
        return {"bots": {}, "seen": {}, "ok": {}}
    if _CW_CACHE["sig"] != sig:
        _CW_CACHE.update(sig=sig, d=_cw_load())
    return _CW_CACHE["d"]


def _cw_key(d):
    return os.path.relpath(os.path.abspath(str(d)), ROOT)


def _cw_lbl(i):
    return (str(i.get("sym") or "").split("-")[0] + " " + str((_BOT_KINDS.get(i.get("type") or "grid") or {}).get("ico") or "")).strip()


def _cw_recs(wid, q, d=None):
    d = d if d is not None else _cw_cached()
    return [r for r in (d.get("bots") or {}).values() if r.get("wid") == wid and r.get("q") == q and not r.get("hands_off")]


def _cw_held(wid, q, d=None):
    """الدولار اللي حرّرته أوامر البوتات الموقوفة تلقائياً — ملك مخزنها، مو «دولار رجع»"""
    return sum(float(r.get("freed") or 0) for r in _cw_recs(wid, q, d))


def _cw_low(g, wid, q, rec, snap, now):
    """① رسالة واحدة للمحفظة: «💵 نفد الدولار الحر» (من ينتظر وكم يحتاج) · تذكير مرة باليوم على الأكثر · «✅ عاد» بعد نصف ساعة متواصلة"""
    key = f"low:{wid}:{q}"
    av = float(rec.get("avail") or 0)
    held = _cw_held(wid, q)
    eff = av - held
    rec["held"], rec["eff"] = round(held, 6), round(eff, 6)
    mn = float(rec.get("min_next") or 0)
    who = sorted(((float(i.get("usd") or 0), i) for i in (snap.get("bots") or {}).values()
                  if i.get("quote") == q and float(i.get("usd") or 0) > 0 and not i.get("destruct")), key=lambda t: t[0])
    op = next((e for e in g.get("events") or [] if e.get("key") == key and e.get("status") == "open"), None)
    if mn > 0 and eff < mn:
        rec.pop("ok_since", None)
        rec.setdefault("low_since", now)
        wait = [(u, i) for u, i in who if eff < u]
        names = " · ".join(f"{_cw_lbl(i)} ({u:g}$)" for u, i in wait[:8]) + (f" · و{len(wait) - 8} غيرها" if len(wait) > 8 else "")
        paused = [_cw_lbl(r) for r in _cw_recs(wid, q)]
        det = (f"المتاح {av:.2f} {q}" + (f" (منه {held:.2f} للمستويات المحفوظة في البوتات الموقوفة)" if held > 0.005 else "")
               + f" · أصغر أمر شراء {mn:.2f} {q}\\n"
               + (f"⏳ تنتظر الدولار: {names}\\n" if names else "")
               + (f"⏸ أُوقف شراؤها تلقائياً فوق السعر بقليل: {' · '.join(paused)} — كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار\\n"
                  if paused else "")
               + "البوتات تكمل البيع، ويعود الشراء وحده حين يتوفر الدولار — رسالة الآن وأخرى حين يعود (وتذكير مرة في اليوم على الأكثر).")
        e = _gd_event(g, key, "🟡", f"💵 نفد الدولار الحر — {q}", det, wid=wid, sym=q, kind="low_quote")
        if e.get("tg") is True and now - float(e.get("rem_ts") or e.get("ts") or now) >= 86400:
            e["rem_ts"], e["tg"], e["rem"] = now, False, int(e.get("rem") or 0) + 1      # ⏰ تذكير مرة باليوم
        if e.get("rem"):
            e["title"] = f"⏰ تذكير: 💵 الدولار الحر ما زال لا يكفي — {q}"
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
    _gd_event(g, f"back:{wid}:{q}:{int(now)}", "🟢", f"✅ عاد الدولار الحر — {q}",
              f"المتاح {av:.2f} {q} يغطي أمر الشراء ({mn:.2f} {q}) منذ {CW_BACK_S // 60} دقيقة — تعود البوتات إلى الشراء"
              + (" ويُستأنف الشراء الموقوف تلقائياً (المستويات المحفوظة تُشترى بأمر واحد بقدر الدولار)" if _cw_recs(wid, q) else ""),
              wid=wid, sym=q, kind="quote_back", status="info")


def _cw_bot(d):
    return (bot_dirs() or {}).get(os.path.abspath(str(d))) or (bot_dirs() or {}).get(str(d))


def _cw_live_buys(st):
    s = 0.0
    for i in (st.get("limit_buys") or {}).values():
        try:
            s += float(i.get("target_price") or 0) * float(i.get("locked_qty") or 0)
        except Exception:
            pass
    return s


def _cw_pause(k, i, r, d, wid, q, eff, now):
    """⏸ أرضية فوق السعر بنصف درجة (أول مرة) · تلحق السعر لو صعد · لمسة المالك ⇒ نتركه"""
    b = _cw_bot(i["dir"])
    if not b:
        return False
    sp = paths_of(b)[0]
    st = read_retry(sp)
    if not isinstance(st, dict):
        return False
    cur = float(st.get("buy_floor") or 0)
    cp = float(i.get("cp") or st.get("current_price") or 0)
    if cp <= 0:
        return False
    g_ = float(i.get("g") or 0.008) or 0.008
    tgt = float(f"{cp * (1 + g_ / 2):.10g}")
    need = float(i.get("usd") or 0)
    if r is None:
        new = max(cur, tgt)
        freed = 0.0
        if new > cur * (1 + 1e-9):
            freed = _cw_live_buys(st)                    # أوامر الشراء الحية تنسحب للمخزن ⇒ دولارها يتحرر (ملك المخزن)
            if not save_state_keys(sp, {"buy_floor": new, "pause_buy": False}):
                return False
        d["bots"][k] = {"wid": wid, "q": q, "sym": i.get("sym"), "type": i.get("type"), "orig": cur, "set": new,
                        "ts": now, "need": need, "freed": round(freed, 6), "moves": 0}
        _dash_event(i.get("sym") or "", f"⏸💵 أُوقف الشراء تلقائياً — الدولار الحر ({max(0.0, eff):.2f}$) لا يكفي أمر الشراء ({need:g}$) · "
                                        f"الأرضية {_px_s(new)} فوق السعر بقليل: كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار"
                                        + (f" · أرضيتك {_px_s(cur)} تعود بعدها" if cur > 0 else ""))
        return True
    if abs(cur - float(r.get("set") or 0)) > max(1e-12, float(r.get("set") or 0) * 1e-7):
        r["hands_off"], r["off_ts"] = True, now          # 👤 المالك غيّر الأرضية (استأنف أو كتب غيرها) ⇒ ما نعانده
        journal("notify", f"👤 {i.get('sym')}: غُيّرت أرضية الشراء يدوياً — الإيقاف التلقائي يترك هذا البوت حتى يعود الدولار", "info", sym=i.get("sym") or "")
        return True
    if tgt > cur * (1 + g_ / 4):                        # السعر صعد ⇒ الأرضية تلحقه (ولا شراء يُرفض فوقها)
        add = _cw_live_buys(st)
        if not save_state_keys(sp, {"buy_floor": tgt, "pause_buy": False}):
            return False
        r["set"], r["freed"], r["moves"] = tgt, round(float(r.get("freed") or 0) + add, 6), int(r.get("moves") or 0) + 1
        return True
    return False


def _cw_restore(k, r, d, why):
    """▶️ عاد الدولار (أو أُطفئ الإيقاف التلقائي) ⇒ أرضية المالك كما كانت (أو بلا أرضية) — والمحرك يشتري المحفوظ بأمر واحد"""
    b = _cw_bot(os.path.join(ROOT, k))
    if b and not r.get("hands_off"):
        sp = paths_of(b)[0]
        st = read_retry(sp)
        if not isinstance(st, dict):
            return False
        cur = float(st.get("buy_floor") or 0)
        if abs(cur - float(r.get("set") or 0)) <= max(1e-12, float(r.get("set") or 0) * 1e-7):
            o = float(r.get("orig") or 0)
            if abs(cur - o) > 1e-15 and not save_state_keys(sp, {"buy_floor": o, "pause_buy": False}):
                return False
            _dash_event(r.get("sym") or "", (f"▶️💵 {why} — استؤنف الشراء تلقائياً"
                                             + (f" · عادت أرضيتك {_px_s(o)}" if o > 0 else
                                                " · المستويات المحفوظة تُشترى بأمر واحد بقدر الدولار الحر")))
    d["bots"].pop(k, None)
    return True


def _cash_watch(g, now, snaps):
    """② ⏸ إيقاف الشراء تلقائياً لبوتات الشبكة اللي دولار محفظتها ما يغطي أمرها القادم (فحصان متتاليان) · ▶️ رجوعه بعد نصف ساعة من عودة الدولار"""
    on = g.get("cash_pause", True) is not False
    with _CW_LOCK:
        d = _cw_load()
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
                eff = float(rec.get("eff", rec.get("avail") or 0) or 0)
                bots = sorted([(float(i.get("usd") or 0), _cw_key(i["dir"]), i) for i in (s.get("bots") or {}).values()
                               if i.get("type") in _CW_TYPES and i.get("dir") and i.get("quote") == q and float(i.get("usd") or 0) > 0
                               and not i.get("destruct")], key=lambda t: t[0])
                wq = f"{wid}|{q}"
                recs = sorted([(k, r) for k, r in d["bots"].items() if r.get("wid") == wid and r.get("q") == q],
                              key=lambda t: float(t[1].get("need") or 0))
                if recs:
                    if (not on) or eff >= min(float(r.get("need") or 0) for _, r in recs):
                        d["ok"].setdefault(wq, now)
                    else:
                        d["ok"].pop(wq, None)
                    if (not on) or now - float(d["ok"].get(wq) or now) >= CW_BACK_S:
                        left = eff
                        for j, (k, r) in enumerate(recs):
                            if on and j and left < float(r.get("need") or 0):
                                break                   # عاد قليل ⇒ الأصغر أولاً (البقية بالجولة الجاية)
                            if _cw_restore(k, r, d, "عاد الدولار" if on else "أُطفئ الإيقاف التلقائي"):
                                left -= float(r.get("need") or 0)
                                ch = True
                        if not any(r.get("wid") == wid and r.get("q") == q for r in d["bots"].values()):
                            d["ok"].pop(wq, None)
                else:
                    d["ok"].pop(wq, None)
                for u, k, i in bots:
                    if eff < u and i.get("alive"):
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": int(sv.get("n") or 0) + 1, "need": u, "ts": now}
                        seen_now.add(k)
                        ch = True
                    else:
                        continue
                    if not on:
                        continue
                    r = d["bots"].get(k)
                    if r is not None and r.get("hands_off"):
                        continue
                    if r is None and d["seen"][k]["n"] < CW_SEEN:
                        continue                        # تأكيد بفحصين قبل أول إيقاف
                    if _cw_pause(k, i, r, d, wid, q, eff, now):
                        ch = True
        for k in list(d["seen"]):
            if k not in seen_now:
                d["seen"].pop(k, None)
                ch = True
        for k in list(d["bots"]):
            if not os.path.isdir(os.path.join(ROOT, k)):
                d["bots"].pop(k, None)                  # البوت انحذف
                ch = True
        if ch:
            save_json_atomic(CASHW_FILE, d)
    _CW_LOWQ.clear()
    _CW_LOWQ.update(str(e.get("sym") or "") for e in g.get("events") or [] if e.get("kind") == "low_quote" and e.get("status") == "open")


def _cw_card(bdir):
    """③ شارة الكرت: {need, auto} — ينتظر دولار (والإيقاف تلقائي أو لا)"""
    try:
        d = _cw_cached()
        k = _cw_key(bdir)
        r = (d.get("bots") or {}).get(k)
        if r and not r.get("hands_off"):
            return {"need": round(float(r.get("need") or 0), 4), "auto": True}
        sv = (d.get("seen") or {}).get(k)
        if isinstance(sv, dict) and time.time() - float(sv.get("ts") or 0) < 3 * GUARD_EVERY:
            return {"need": round(float(sv.get("need") or 0), 4), "auto": False}
    except Exception:
        pass
    return None


def guard_scan(force=False):
    """🛡️ فحص كامل لكل المحافظ.'''),
    # ── the switch in 🛡️ الرقابة ──
    ('''def guard_cfg(auto_fix=None, paused=None, by=""):
    """⚙️ مفاتيح الرقابة: التصحيح التلقائي · الإيقاف المؤقت."""
    with _GUARD_IO:
        g = _gd_load()
        msg = []''',
     '''def guard_cfg(auto_fix=None, paused=None, by="", cash_pause=None):
    """⚙️ مفاتيح الرقابة: التصحيح التلقائي · الإيقاف المؤقت · 💵 إيقاف الشراء تلقائياً حين ينفد الدولار (v3.36.44)."""
    with _GUARD_IO:
        g = _gd_load()
        msg = []
        if cash_pause is not None:
            g["cash_pause"] = bool(cash_pause)
            msg.append("⏸💵 إيقاف الشراء تلقائياً حين ينفد الدولار " + ("مفعّل" if g["cash_pause"] else
                                                                       "معطّل — البوتات الموقوفة تلقائياً تُستأنف بالفحص القادم"))'''),
    ('''                return self._json(guard_cfg(auto_fix=v.get("auto_fix"), paused=v.get("paused"), by=_by))''',
     '''                return self._json(guard_cfg(auto_fix=v.get("auto_fix"), paused=v.get("paused"), by=_by, cash_pause=v.get("cash_pause")))'''),
    ('''            "auto_fix": bool(g.get("auto_fix")), "paused": bool(g.get("paused")), "busy": busy,''',
     '''            "auto_fix": bool(g.get("auto_fix")), "paused": bool(g.get("paused")), "busy": busy,
            "cash_pause": g.get("cash_pause", True) is not False,                       # 💵 v3.36.44'''),
    ('''    <button onclick="guardCfg({auto_fix:${V.auto_fix?'false':'true'}})" class="${V.auto_fix?'on':''}" style="font-size:12px;padding:6px 12px">${V.auto_fix?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;''',
     '''    <button onclick="guardCfg({auto_fix:${V.auto_fix?'false':'true'}})" class="${V.auto_fix?'on':''}" style="font-size:12px;padding:6px 12px">${V.auto_fix?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;
  h+=`<div id="gv_cash" style="${box};display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between">
    <div style="font-size:12px;line-height:1.8">⏸💵 <b>إيقاف الشراء تلقائياً حين ينفد الدولار:</b> <b style="color:${V.cash_pause?'var(--green)':'var(--mut2)'}">${V.cash_pause?'مفعّل':'متوقف'}</b><br>
      <span style="color:var(--mut2);font-size:11px">حين لا يكفي الدولار الحر أمر الشراء القادم لبوت شبكة (فحصان متتاليان) يُوقف شراءه فوق السعر بقليل — كل مستوى ينزل إليه السعر
      يُحفظ، والأرضية تتبع السعر إن صعد · وحين يعود الدولار نصف ساعة يُستأنف الشراء (يُشترى المحفوظ بأمر واحد) وتعود أرضيتك إن كانت لك أرضية.
      رسالة واحدة للمحفظة حين ينفد وأخرى حين يعود.</span></div>
    <button onclick="guardCfg({cash_pause:${V.cash_pause?'false':'true'}})" class="${V.cash_pause?'on':''}" style="font-size:12px;padding:6px 12px">${V.cash_pause?'⏹️ أطفِه':'▶️ شغّله'}</button></div>`;'''),
    # ── ③ the card ──
    ('''            "accx": _safe(_accx_snap, b, st, default=None),   # 📦 v3.21.2: عدّاد الإيقاف = اللي قطعها السعر بس (يبدي من صفر)''',
     '''            "accx": _safe(_accx_snap, b, st, default=None),   # 📦 v3.21.2: عدّاد الإيقاف = اللي قطعها السعر بس (يبدي من صفر)
            "cashw": _safe(_cw_card, b["dir"], default=None),  # 💵 v3.36.44: 🟠 ينتظر دولار'''),
    ('''function accChipsOf(b){
  const AX=b.accx||{};let c='';''',
     '''function accChipsOf(b){
  const AX=b.accx||{};let c='';
  const CW=b.cashw;if(CW&&+CW.need>0)c+=`<span class="chip cashw" style="color:var(--amber);border-color:rgb(var(--amber2-rgb)/.45);background:rgb(var(--amber2-rgb)/.08)"
    title="${CW.auto?'⏸ أُوقف الشراء تلقائياً فوق السعر بقليل لأن الدولار الحر في المحفظة لا يكفي أمر الشراء — كل مستوى ينزل إليه السعر يُحفظ ويُشترى بأمر واحد حين يعود الدولار (وتعود أرضيتك إن كانت لك أرضية) · زر الاستئناف يلغي الإيقاف التلقائي لهذا البوت':'الدولار الحر في المحفظة لا يكفي أمر الشراء القادم — يكمل البوت البيع وينتظر الدولار'}">🟠 ينتظر دولار — يحتاج $${(+CW.need).toFixed(2)}${CW.auto?' · ⏸':''}</span>`;'''),
    # ── ① the 🔔 centre: the engines' dollar lines stay in the bot's 📜 log while the wallet message is open ──
    ('''                if any(x in str(e.get("msg")) for x in _FEED_SKIP):
                    continue                            # 🔕 v3.21.10 (ب٣٠): سطر عبور/حجز الإيقاف — إشعاره «📦 عبر N درجة» يطلع مرة وحدة من اللوحة''',
     '''                if any(x in str(e.get("msg")) for x in _FEED_SKIP):
                    continue                            # 🔕 v3.21.10 (ب٣٠): سطر عبور/حجز الإيقاف — إشعاره «📦 عبر N درجة» يطلع مرة وحدة من اللوحة
                if _CW_LOWQ and b["symbol"].split("-")[-1] in _CW_LOWQ and any(x in str(e.get("msg")) for x in _CW_FEED):
                    continue                            # 💵 v3.36.44: رسالة نفاد الدولار مفتوحة ⇒ أسطر «ما يكفي» المكررة تبقى بسجل البوت'''),
    # ── ① the recurring and value-path bots: the first «not enough dollars» skip, then quiet until a buy goes through ──
    ('''        sent = more = 0
        for e in new:
            txt = _safe(_rec_msg, b, st, e, default="")''',
     '''        sent = more = 0
        _nbk = key + "|nobal"                 # 💵 v3.36.44: «الرصيد لا يكفي» — أول مرة ثم صمت حتى يمر شراء (وتذكير مرة باليوم)
        for e in new:
            if e.get("k") == "open":
                d.pop(_nbk, None)
            if e.get("k") == "skip" and e.get("why") == "balance":
                if now - float(d.get(_nbk) or 0) < 86400:
                    continue
                d[_nbk] = now
            txt = _safe(_rec_msg, b, st, e, default="")'''),
    ('''APP_VERSION = "3.36.43"''', '''APP_VERSION = "3.36.44"'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
