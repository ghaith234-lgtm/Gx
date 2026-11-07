# 🪜💉 patch 13 (engine · reinvest phase B — injection, the grid's apply_injections per slot · REINVEST_PLAN.md rule ٨ · decision أ)
#   a request from the dashboard (reinvest_inject.json — the grid's file · items {"k": "j:k", "usd" | "coin"}) goes into ONE slot
#   (level · part) by its side, and into the order now:
#     sell side ⇒ coins from the wallet join the sell (a published order: its size changed at OKX with amend-order · in memory: in
#                 the state, if the free coins cover it) · their basis «as if bought» at the slot's price (the wallet slots' rule)
#     buy side  ⇒ dollars grow the buy now (published: amend-order · memory: if the free dollars cover it) · the part under one lot
#                 and anything that can't go in now ⇒ the slot's pot (it grows in its cycle)
#   the injected money is the owner's capital, kept apart in the pot (inj_book · inj_grown) — it grows the profits reinvested and
#   comes back as capital, never as profit.
#   Exactly once: the request is taken (its id in the book) in the same save as its effects / its pending resizes · a resize is
#   written before it is sent (an absolute size ⇒ sending it again never doubles) · the books change only when OKX shows the new
#   size (amend lands later, its answer lost, a power cut — the order decides) · not shown within AM_WAIT / OKX refused / the
#   order finished first ⇒ nothing changed (dollars ⇒ the pot).
#   + the sweep (the grid's sweep): a pot holding a whole lot turns into quantity without waiting for a sale (a slot selling, or a
#   buy with no published order — a published order never changes size from the sweep).
#   python3 devtests/step/patches/p13_ri_inject.py ENGINE.py
import os, sys

R = [
    # the signed POST + amend-order, after balance_direct
    ('''# ================= 🧾 أسطر السجل مرة واحدة (من ♾️) =================
''',
     '''def _signed_post(endpoint, payload):
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    body = json.dumps(payload)
    mac = hmac.new(bytes(config["secret_key"], encoding='utf8'), bytes(timestamp + "POST" + endpoint + body, encoding='utf8'), digestmod='sha256')
    headers = {"OK-ACCESS-KEY": config["api_key"], "OK-ACCESS-SIGN": base64.b64encode(mac.digest()).decode('utf-8'),
               "OK-ACCESS-TIMESTAMP": timestamp, "OK-ACCESS-PASSPHRASE": config["passphrase"], "Content-Type": "application/json"}
    return requests.post("https://www.okx.com" + endpoint, headers=headers, data=body, timeout=5).json()


def amend_order_direct(ord_id, new_sz):
    """✏️ حجم أمر منشور بالمنصة (amend-order — مثل الشبكي) · الحجم الجديد كامل (يشمل المنفّذ) · None = ما وصل رد"""
    try:
        r = _signed_post("/api/v5/trade/amend-order", {"instId": SYMBOL, "ordId": str(ord_id), "newSz": _sz_str(new_sz)})
        _net_mark(True)
        return r
    except Exception:
        _net_mark(False)
        return None


# ================= 🧾 أسطر السجل مرة واحدة (من ♾️) =================
'''),
    # the tick: pending resizes · the percentage · the requests · the sweep
    ('''def _ri_tick(state):
    """⚖️ النسبة (reinvest_pct بالإعداد) تنحفظ بالدفتر بكل دورة — حيّة بلا إعادة تشغيل · لمن تتغيّر سطر بالسجل (مثل الشبكي)"""
    b = _ri(state)
    if b is None or not b.get("on"):
        return
    p = config.get("reinvest_pct")
''',
     '''def _ri_tick(state):
    """💠 بكل دورة قبل الأوامر: ✏️ تعديلات الحجم المعلّقة تنحسم · ⚖️ النسبة من الإعداد · 💉 طلبات الحقن · 🧹 الحصّالات الجاهزة"""
    b = _ri(state)
    if b is None:
        if os.path.exists(INJECT_FILE):
            _ri_drop(INJECT_FILE, "⚠️ [حقن] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        return
    _ri_am_tick(state, b)
    if b.get("on"):
        _ri_pct_sync(state, b)
    _ri_inject(state, b)
    if b.get("on"):
        _ri_sweep(state, b)


def _ri_pct_sync(state, b):
    """⚖️ النسبة (reinvest_pct بالإعداد) تنحفظ بالدفتر بكل دورة — حيّة بلا إعادة تشغيل · لمن تتغيّر سطر بالسجل (مثل الشبكي)"""
    p = config.get("reinvest_pct")
'''),
    # the injection machinery, before _send
    ('''def _send(state, key, s, cp):
''',
     '''# ================= 💉 الحقن — نفس فكرة الشبكي (apply_injections) لكل خانة · حسب جهتها =================
INJECT_FILE = "reinvest_inject.json"     # 💉 طلب من اللوحة (نفس ملف الشبكي) · {"id", "ts", "items": [{"k": "j:k", "usd" | "coin"}]}
AM_WAIT = 60.0                           # ثواني: تعديل حجم ما بيّنته المنصة بعدها ⇒ ما صار


def _ri_drop(path, msg=None):
    try:
        os.remove(path)
    except Exception:
        pass
    if msg:
        log_trade_history(SYMBOL, msg)


def _ri_free(state, side):
    """💰 الحر بالمنصة ناقص اللي خانات الذاكرة حاجزته (مثل الشبكي) — بيع ⇒ عملة · شراء ⇒ دولار · None = ما وصلنا"""
    base, quote = SYMBOL.split("-")
    av = balance_direct(base if side == "sell" else quote, zero_ok=True)
    if av is None:
        return None
    claims = 0.0
    for s in _slots(state).values():
        if s.get("side") == side and not _o_live(s):
            claims += _rem(s) * (1.0 if side == "sell" else float(s["bp"]))
    return av - claims


def _ri_book(state, b, key, s, op):
    """📒 أثر بند حقن على الخانة ودفترها — بعد ما يتأكد (المنصة بيّنت الحجم الجديد · أو بالذاكرة) · يرجّع أسطر السجل"""
    lv = _ri_lv(b, key, s)
    px = float(lv.get("px") or s["bp"])
    add = float(op.get("add") or 0)
    where = "المنشور" if op.get("live") else "في الذاكرة"
    for f in ("inj_total", "inj_coin", "inj_coin_basis"):
        b.setdefault(f, 0.0)
    if op["kind"] == "inj_coin":                          # 🪙 عملة من المحفظة ⇒ أمر البيع · كلفتها «كأنها اشتُريت» بسعر الخانة
        fr = float((state.get("step") or {}).get("f") or 0.001)
        basis = round(add * float(s["bp"]) / (1.0 - fr), 10)
        if float(s.get("spent") or 0) <= 0:               # (خانة من بوت قبل v3.36.17: كلفتها كانت q × السعر)
            s["spent"] = round(float(s["q"]) * float(s["bp"]), 10)
        s["sq"] = round(float(s.get("sq") or 0) + add, 12)
        s["spent"] = round(float(s.get("spent") or 0) + basis, 10)
        lv["grown_qty"] = round(float(lv["grown_qty"]) + add, 12)
        s["g"] = float(lv["grown_qty"])
        lv["inj_grown"] = round(float(lv.get("inj_grown") or 0) + add * px, 10)
        b["inj_total"] = round(float(b["inj_total"]) + add * px, 10)
        b["inj_coin"] = round(float(b["inj_coin"]) + add, 12)
        b["inj_coin_basis"] = round(float(b["inj_coin_basis"]) + basis, 10)
        return [f"💉 [حقن] الخانة {key} (بيع): أُضيفت {_n(add)} عملة من محفظتك إلى أمر البيع {where} الآن · رأس مال {_n(add * px)}$"]
    usd = float(op.get("usd") or 0)
    if op["kind"] == "inj_usd":                           # 💵 دولار ⇒ أمر الشراء يكبر الآن · كسر الوحدة ⇒ الحصّالة
        lv["grown_qty"] = round(float(lv["grown_qty"]) + add, 12)
        s["g"] = float(lv["grown_qty"])
        lv["inj_grown"] = round(float(lv.get("inj_grown") or 0) + add * px, 10)
        rest = round(usd - add * px, 10)
        if rest > 0:
            lv["usd_book"] = round(float(lv["usd_book"]) + rest, 10)
            lv["inj_book"] = round(float(lv.get("inj_book") or 0) + rest, 10)
        b["inj_total"] = round(float(b["inj_total"]) + usd, 10)
        return [f"💉 [حقن] الخانة {key} (شراء): {_n(usd)}$ رأس مال كبّرت أمر الشراء {where} الآن (+{_n(add)} عملة)"]
    lv["usd_book"] = round(float(lv["usd_book"]) + usd, 10)        # inj_pot
    lv["inj_book"] = round(float(lv.get("inj_book") or 0) + usd, 10)
    b["inj_total"] = round(float(b["inj_total"]) + usd, 10)
    return [f"💉 [حقن] الخانة {key}: {_n(usd)}$ رأس مال إلى حصّالتها — يكبر أمرها في دورته"
            + (f" ({op['why']})" if op.get("why") else "")]


def _ri_fail(state, b, key, s, op, why):
    """تعديل الحجم ما صار ⇒ ولا شي تغيّر بالدفتر · الدولار يروح للحصّالة (مثل الشبكي) · العملة تبقى بمحفظتك"""
    if op["kind"] == "inj_usd":
        return _ri_book(state, b, key, s, {"kind": "inj_pot", "usd": op["usd"], "why": f"تعذّر تكبير الأمر الآن: {why}"})
    if op["kind"] == "inj_coin":
        return [f"⚠️ [حقن] الخانة {key}: لم تُضف {_n(op['add'])} عملة إلى أمر البيع ({why}) — لم يتغيّر شيء"]
    return []


def _ri_am_settle(state, key, s, od, final=False):
    """✏️ الأمر كما تبيّنه المنصة يحسم التعديل المعلّق: حجمه = الجديد ⇒ الدفتر يتغيّر هسه · القديم ويا (خلص الأمر · المنصة رفضت ·
    مرّت AM_WAIT) ⇒ ما صار · غير هيچ ينتظر. يرجّع أسطر السجل (المتصل يحفظ)."""
    am = s.get("am")
    b = _ri(state)
    if not am or b is None:
        return []
    try:
        sz = float(od.get("sz") or 0)
    except Exception:
        return []
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    if abs(sz - float(am["new"])) <= lot * 0.5:
        s.pop("am", None)
        if s.get("o"):
            s["o"]["sz"] = float(am["new"])
        op = dict(am["op"])
        old, new = float(am.get("old") or 0), float(am["new"])
        try:
            fx = float(od.get("accFillSz") or 0)
        except Exception:
            fx = 0.0
        if new < old and fx > new + lot * 0.5:            # تصغير وأمر منفّذ أكثر من الحجم الجديد ⇒ المنصة كمّلته: انشال بس اللي ما انفّذ
            eff = _lot_floor(max(0.0, old - fx))
            full = old - new
            if eff <= lot * 0.5:
                return _ri_fail(state, b, key, s, am["op"], "الأمر نُفّذ قبل التصغير")
            if op.get("kind") == "wd_buy":
                op["c"] = round(float(op.get("c") or 0) * eff / float(op["q"]), 10) if float(op["q"]) > 0 else 0.0
                op["q"] = eff
            elif op.get("kind") == "wd_sell":
                op["tot"] = eff
                if "gq" in op:
                    op["gq"] = min(float(op["gq"]), eff)
                    op["cq"] = round(eff - op["gq"], 12)
            op["part"] = round(eff / full, 6) if full > 0 else 1.0
        return _ri_book(state, b, key, s, op)
    fin = str(od.get("state") or "") in ("filled", "canceled", "mmp_canceled")
    if final or fin or am.get("rej") or time.time() - float(am.get("ts") or 0) >= AM_WAIT:
        s.pop("am", None)
        why = am.get("rej") or ("الأمر اكتمل قبل التعديل" if fin or final else "المنصة لم تُظهر الحجم الجديد")
        return _ri_fail(state, b, key, s, am["op"], why)
    return []


def _ri_am_send(state, key, s):
    """يرسل التعديل المقيَّد (حجم مطلق) · رد رفض أكيد ⇒ يتعلّم «rej» · بلا رد ⇒ المنصة تحسم بالسؤال"""
    am = s["am"]
    am["n"] = int(am.get("n") or 0) + 1
    r = amend_order_direct(am["oid"], am["new"])
    if not isinstance(r, dict):
        return
    d0 = (r.get("data") or [{}])[0] or {}
    sc = str(d0.get("sCode") or "")
    if str(r.get("code")) == "0" and sc in ("0", ""):
        am["ok"] = True
    elif _rejected(r) and sc != "51508":                  # (51508 = الحجم نفسه ⇒ ممكن انطبق قبل — السؤال يحسم)
        am["rej"] = f"{sc or r.get('code')}: {d0.get('sMsg') or r.get('msg') or ''}".strip()


def _ri_am_check(state, key, s, tries=1):
    """يسأل المنصة عن الأمر ويحسم (بلا حفظ) · لسه القديم وما انرد ⇒ يعيد الإرسال (حجم مطلق ⇒ ما يتضاعف)"""
    out = []
    for i in range(tries):
        am = s.get("am")
        if not am:
            break
        h = check_order_direct(am["oid"], SYMBOL)
        if str(h.get("code")) == "0" and h.get("data"):
            out += _ri_am_settle(state, key, s, h["data"][0])
            if not s.get("am"):
                break
            if not am.get("ok") and not am.get("rej") and int(am.get("n") or 0) < 3 \\
                    and str(h["data"][0].get("state") or "") in ("live", "partially_filled"):
                _ri_am_send(state, key, s)
        elif str(h.get("code")) == "51603" and time.time() - float(am.get("ts") or 0) >= AM_WAIT:
            s.pop("am", None)
            out += _ri_fail(state, _ri(state), key, s, am["op"], "المنصة لا تعرف الأمر")
            break
        if i + 1 < tries:
            time.sleep(0.3)
    return out


def _ri_am_tick(state, b):
    """✏️ تعديلات معلّقة (رد ضاع · المنصة تطبّق بعدين · انقطاع بعد القيد) ⇒ تنحسم بالسؤال عن الأمر · حفظة وحدة"""
    lines, any_ = [], False
    pend = sorted(((k, s) for k, s in _slots(state).items() if s.get("am")),
                  key=lambda t: (float(t[1]["am"].get("ts") or 0), int(t[1]["am"].get("seq") or 0)))
    for key, s in pend:
        if s.get("am"):
            any_ = True
            n0 = int(s["am"].get("n") or 0)
            lines += _ri_am_check(state, key, s)
            if s.get("am") and int(s["am"].get("n") or 0) != n0:
                any_ = True
    if any_:
        _commit(state, lines)


def _ri_inject(state, b):
    """💉 طلب الحقن من اللوحة: كل بند لخانة وحدة حسب جهتها (قرار المالك أ: كل جزء على حدة) · ينطبق مرة وحدة بالضبط"""
    if not os.path.exists(INJECT_FILE):
        return 0
    req = load_json(INJECT_FILE)
    if not isinstance(req, dict):
        _ri_drop(INJECT_FILE, "⚠️ [حقن] طلب تالف — تم تجاهله")
        return 0
    rid = str(req.get("id") or req.get("ts") or "")
    done = b.setdefault("reqs", [])
    if rid and rid in done:                               # (انطبق قبل انقطاع — الملف بس ما انمسح)
        _ri_drop(INJECT_FILE)
        return 0
    if not b.get("on"):
        _ri_drop(INJECT_FILE, "⚠️ [حقن] إعادة الاستثمار متوقفة — أُلغي الطلب")
        return 0
    try:
        age = time.time() - float(req.get("ts") or 0)
    except Exception:
        age = float("inf")
    if not age <= 86400:
        _ri_drop(INJECT_FILE, "⚠️ [حقن] الطلب قديم (أكثر من يوم) — أُلغي")
        return 0
    uv = float(config.get("usd_value") or 0) or 1.0
    S = _slots(state)
    lines, sends, free, n, tot = [], [], {}, 0, 0.0

    def _free(side):
        if side not in free:
            free[side] = _ri_free(state, side)
        return free[side]

    for it in (req.get("items") or [])[:64]:
        try:
            key = str(it.get("k") or "").strip()
            usd, cn = float(it.get("usd") or 0), float(it.get("coin") or 0)
            if not (math.isfinite(usd) and math.isfinite(cn)) or usd < 0 or cn < 0 or (usd <= 0 and cn <= 0):
                continue
            s = S.get(key)
            if s is None:
                lines.append(f"⚠️ [حقن] الخانة {key} غير موجودة — تم تجاهل البند")
                continue
            px = float(s["bp"])
            if usd > uv * 1000 or cn * px > uv * 1000:         # حارس الإصبع الثقيل
                lines.append(f"⚠️ [حقن] مبلغ غير معقول في الخانة {key} — تم تجاهله")
                continue
            if s.get("am"):
                lines.append(f"⚠️ [حقن] الخانة {key}: تعديل سابق لأمرها لم يكتمل — أعد المحاولة بعد قليل")
                continue
            if cn > 0:
                add = _lot_floor(cn)
                st_o = (s.get("o") or {}).get("st")
                if s["side"] != "sell":
                    lines.append(f"⚠️ [حقن] الخانة {key} ليس لها أمر بيع الآن — العملة تُحقن في أمر بيع فقط")
                elif add <= 0:
                    lines.append(f"⚠️ [حقن] الخانة {key}: الكمية {_n(cn)} أصغر من وحدة المنصة — لم يتغيّر شيء")
                elif _o_live(s):
                    s["am"] = {"oid": str(s["o"]["id"]), "old": float(s["o"].get("sz") or 0), "new": float(s["o"].get("sz") or 0) + add,
                               "ts": time.time(), "n": 0, "seq": len(sends), "op": {"kind": "inj_coin", "add": add, "live": True}}
                    sends.append(key)
                elif st_o == "send":
                    lines.append(f"⚠️ [حقن] الخانة {key}: أمرها في الطريق إلى المنصة — أعد المحاولة بعد قليل")
                else:
                    fr = _free("sell")
                    if fr is None or fr + 1e-12 < add:
                        lines.append(f"⚠️ [حقن] الخانة {key}: رصيد العملة الحر لا يكفي "
                                     f"({'غير معروف' if fr is None else _n(max(0.0, fr))} مقابل {_n(add)}) — لم يتغيّر شيء")
                    else:
                        free["sell"] = fr - add
                        lines += (_ri_book(state, b, key, s, {"kind": "inj_coin", "add": add}))
                        n += 1
                        tot += add * px
            if usd > 0:
                add = _lot_floor(usd / px)
                if s["side"] == "buy" and _o_live(s) and add > 0:
                    s["am"] = {"oid": str(s["o"]["id"]), "old": float(s["o"].get("sz") or 0), "new": float(s["o"].get("sz") or 0) + add,
                               "ts": time.time(), "n": 0, "seq": len(sends), "op": {"kind": "inj_usd", "add": add, "usd": usd, "live": True}}
                    sends.append(key)
                    continue
                if s["side"] == "buy" and not s.get("o") and add > 0:
                    fr = _free("buy")
                    if fr is not None and fr + 1e-9 >= add * px:
                        free["buy"] = fr - add * px
                        lines += (_ri_book(state, b, key, s, {"kind": "inj_usd", "add": add, "usd": usd}))
                    else:
                        lines += (_ri_book(state, b, key, s, {"kind": "inj_pot", "usd": usd, "why": "الرصيد الحر لا يكفي الآن"}))
                else:
                    lines += (_ri_book(state, b, key, s, {"kind": "inj_pot", "usd": usd}))
                n += 1
                tot += usd
        except Exception as e:
            lines.append(f"⚠️ [حقن] بند فاشل: {type(e).__name__}")
    if n or sends:
        lines.append(f"💉 [حقن] الطلب: {n} بند طُبّق · {_n(tot)}$ رأس مال" + (f" · {len(sends)} بند ينتظر تأكيد المنصة" if sends else "")
                     + " — يعود رأس مال لا ربحاً")
    if rid:
        done.append(rid)
        del done[:-32]
    if not _commit(state, lines):                         # ✋ ما انحفظ ⇒ ولا شي انرسل · الطلب يبقى للدورة الجاية
        for key in sends:
            S[key].pop("am", None)
        return 0
    _ri_drop(INJECT_FILE)
    out = []
    for key in sends:                                     # ✏️ القيد على القرص ⇒ هسه التعديل بالمنصة ويتأكد منها
        _ri_am_send(state, key, S[key])
        out += _ri_am_check(state, key, S[key], tries=5)
    if sends:
        _commit(state, out)
    return n + len(sends)


def _ri_sweep(state, b):
    """🧹 الحصّالة اللي بيها وحدة كاملة تتحول كمية بلا ما تنتظر بيعة (مثل الشبكي) — خانة تبيع · أو شراء بلا أمر منشور
    (أمر منشور ما يتغيّر حجمه من الكنس)"""
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    S, n = _slots(state), 0
    for key, lv in list(b["levels"].items()):
        s = S.get(key)
        if not s or s.get("am") or float(lv.get("usd_book") or 0) < lot * float(lv.get("px") or s["bp"]) - 1e-12:
            continue
        if s.get("side") == "buy" and s.get("o"):
            continue
        if _ri_convert(state, b, key, s) > 0:
            n += 1
    if n:
        _commit(state, [f"🐖 [إعادة الاستثمار] تحوّلت حصّالات {n} خانة إلى كمية"])
    return n


def _send(state, key, s, cp):
'''),
    # a fill settles a pending resize first (the order itself shows its size)
    ('''    stv = str(od.get("state") or "")
    side = s["side"]
    N = int((state.get("step") or {}).get("N") or 1)
    lines = []
''',
     '''    stv = str(od.get("state") or "")
    side = s["side"]
    N = int((state.get("step") or {}).get("N") or 1)
    lines = []
    if s.get("am"):                                       # ✏️ تعديل حجم معلّق ⇒ الأمر نفسه يحسم (قبل حساب التنفيذ)
        lines += _ri_am_settle(state, key, s, od, final=True)
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
