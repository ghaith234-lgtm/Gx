# 🪜➖ patch 14 (engine · reinvest phase C — partial withdrawal, the grid's apply_withdrawals per slot · REINVEST_PLAN.md rule ٩)
#   a request from the dashboard (reinvest_withdraw.json — the grid's file) takes from ONE slot's pot by its side, and the order
#   shrinks now (published: amend-order · memory: the state) — the base never touched, nothing taken that isn't really there:
#     buy side (dollars) {"k", "cap", "gain"}: the pot's dollars first, then the growth inside the buy ⇒ reinvested profit → the
#                released profit (total_profit — the daily profit · the accumulator takes its share in its time) · capital → wallet
#     sell side (coins) {"k", "cap_q", "gain_q"}: coins above the base inside the sell ⇒ reinvested profit → the accumulator at
#                their real cost (the grid's handoff queue) · capital → the wallet as coins
#               (dollars) {"k", "cap_d", "gain_d"}: the pot's dollars + growth not inside the sell yet ⇒ as on the buy side
#   exactly once: as the injection (the request's id in the book · resizes written before sent · the books change only when
#   OKX shows the new size). The books: out_usd · out_gain · out_coin(_basis) · cap_coin_out(_basis) — real profit = total_profit
#   − out_usd + credited · pots = credited + injected − taken out.
#   python3 devtests/step/patches/p14_ri_withdraw.py ENGINE.py
import os, sys

R = [
    # the tick handles withdrawals after injections
    ('''    _ri_inject(state, b)
    if b.get("on"):
        _ri_sweep(state, b)
''',
     '''    _ri_inject(state, b)
    _ri_withdraw(state, b)
    if b.get("on"):
        _ri_sweep(state, b)
'''),
    ('''    if os.path.exists(INJECT_FILE):
            _ri_drop(INJECT_FILE, "⚠️ [حقن] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        return
''',
     '''    if os.path.exists(INJECT_FILE):
            _ri_drop(INJECT_FILE, "⚠️ [حقن] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        if os.path.exists(WITHDRAW_FILE):
            _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        return
'''),
    # the withdraw kinds in the book of a resize
    ('''    usd = float(op.get("usd") or 0)
    if op["kind"] == "inj_usd":''',
     '''    if op["kind"] in ("wd_buy", "wd_sell", "wd_usd"):
        return _ri_book_wd(state, b, key, s, lv, px, op)
    usd = float(op.get("usd") or 0)
    if op["kind"] == "inj_usd":'''),
    ('''    if op["kind"] == "inj_coin":
        return [f"⚠️ [حقن] الخانة {key}: لم تُضف {_n(op['add'])} عملة إلى أمر البيع ({why}) — لم يتغيّر شيء"]
    return []
''',
     '''    if op["kind"] == "inj_coin":
        return [f"⚠️ [حقن] الخانة {key}: لم تُضف {_n(op['add'])} عملة إلى أمر البيع ({why}) — لم يتغيّر شيء"]
    if op["kind"] in ("wd_buy", "wd_sell"):
        return [f"⚠️ [سحب] الخانة {key}: لم يصغر أمر {'الشراء' if op['kind'] == 'wd_buy' else 'البيع'} ({why}) — لم يتغيّر شيء"]
    return []
'''),
    # the machinery, before _ri_sweep
    ('''def _ri_sweep(state, b):
''',
     '''# ================= ➖ السحب الجزئي — نفس فكرة الشبكي (apply_withdrawals) لكل خانة · حسب جهتها =================
WITHDRAW_FILE = "reinvest_withdraw.json"     # ➖ طلب من اللوحة (نفس ملف الشبكي)


def _ri_base_sell(state, s):
    """🪙 الأساس داخل أمر البيع = اللي يتركه شراء الأساس بعد عمولته (مثل sq خانة المحفظة بالتخطيط) — ما ينلمس"""
    fr = float((state.get("step") or {}).get("f") or 0.001)
    return _lot_floor(float(s["q"]) * (1.0 - fr))


def _ri_split(lv):
    """يفصل محتوى الحصّالة لجيبين (مثل الشبكي): رأس مالك المحقون · والربح المعاد استثماره (بسعر الخانة)"""
    px = float(lv.get("px") or 0)
    total = float(lv.get("usd_book") or 0) + float(lv.get("grown_qty") or 0) * px
    cap = min(max(0.0, float(lv.get("inj_book") or 0) + float(lv.get("inj_grown") or 0)), max(0.0, total))
    return {"total": total, "cap": cap, "gain": max(0.0, total - cap)}


def _ri_out(state, b, cap, gain):
    """💵 دولار يطلع من الحصّالات: رأس المال ⇒ محفظتك (ينزل من المحقون) · الربح ⇒ الربح المحرر (total_profit)"""
    for f in ("out_usd", "out_gain"):
        b.setdefault(f, 0.0)
    b["inj_total"] = round(float(b.get("inj_total") or 0) - cap, 10)
    if gain > 0:
        state["total_profit"] = round(float(state.get("total_profit") or 0) + gain, 10)
        b["out_usd"] = round(float(b["out_usd"]) + gain, 10)
        b["out_gain"] = round(float(b["out_gain"]) + gain, 10)


def _ri_handoff(state, b, coin, cost_usd, why, key):
    """🪙 تسليم عملة للمُراكِم بكلفتها الحقيقية (طابور الشبكي نفسه — اللوحة تستلمه خلال ثوانٍ) · يرجّع السطر"""
    coin, cost_usd = round(float(coin), 12), float(cost_usd)
    if coin <= 1e-12 or cost_usd <= 0:
        return None
    q = list(b.get("handoffs") or [])
    ent = {"id": f"{SYMBOL}-{int(time.time() * 1000)}-{int(b.get('ho_n') or 0)}", "symbol": SYMBOL, "coin": coin,
           "avg_px": round(cost_usd / coin, 12), "usd": round(cost_usd, 10), "ts": time.time(), "why": str(why), "level": key}
    b["ho_n"] = int(b.get("ho_n") or 0) + 1
    q.append(ent)
    b["handoffs"] = q[-200:]
    b["handoff"] = ent
    b["handoff_total"] = round(float(b.get("handoff_total") or 0) + cost_usd, 10)
    return f"🪙 [تسليم للمُراكِم] {_n(coin)} عملة @ {_n(ent['avg_px'])}$ = {_n(cost_usd)}$ — {why}"


def _ri_book_wd(state, b, key, s, lv, px, op):
    """📒 أثر بند سحب على الخانة ودفترها — بعد ما يتأكد (المنصة بيّنت الحجم الجديد · أو بالذاكرة) · يرجّع أسطر السجل"""
    out = []
    if op["kind"] == "wd_buy":                            # 💵 النمو داخل أمر الشراء ⇒ دولار (رأس مال · ربح)
        q, c_part = float(op["q"]), float(op["c"])
        g_part = round(q * px - c_part, 10)
        lv["grown_qty"] = round(max(0.0, float(lv["grown_qty"]) - q), 12)
        s["g"] = float(lv["grown_qty"])
        lv["inj_grown"] = round(max(0.0, float(lv.get("inj_grown") or 0) - c_part), 10)
        _ri_out(state, b, c_part, g_part)
        out.append(f"➖ [سحب] الخانة {key} (شراء): " + " · ".join(
            ([f"رأس مال {_n(c_part)}$ → محفظتك"] if c_part > 1e-12 else []) + ([f"ربح {_n(g_part)}$ → الربح المحرر"] if g_part > 1e-12 else [])
            + [f"أمر الشراء {'المنشور' if op.get('live') else 'في الذاكرة'} صغر الآن ({_n(q)} عملة)"]))
    elif op["kind"] == "wd_sell":                         # 🪙 عملة فوق الأساس داخل أمر البيع ⇒ ربح للمُراكِم · رأس مال لمحفظتك
        tot, gq, cq = float(op["tot"]), float(op["gq"]), float(op["cq"])
        sq0 = float(s.get("sq") or 0)
        basis_t = round(float(s.get("spent") or 0) * (tot / sq0), 10) if sq0 > 0 else 0.0
        s["sq"] = round(sq0 - tot, 12)
        s["spent"] = round(float(s.get("spent") or 0) - basis_t, 10)
        lv["grown_qty"] = round(max(0.0, float(lv["grown_qty"]) - tot), 12)
        s["g"] = float(lv["grown_qty"])
        lv["inj_grown"] = round(max(0.0, float(lv.get("inj_grown") or 0) - cq * px), 10)
        for f in ("out_coin", "out_coin_basis", "cap_coin_out", "cap_coin_out_basis", "out_gain"):
            b.setdefault(f, 0.0)
        g_cost = round(basis_t * (gq / tot), 10) if tot > 0 else 0.0
        b["inj_total"] = round(float(b.get("inj_total") or 0) - cq * px, 10)
        b["out_gain"] = round(float(b["out_gain"]) + gq * px, 10)
        b["out_coin"] = round(float(b["out_coin"]) + gq, 12)
        b["out_coin_basis"] = round(float(b["out_coin_basis"]) + g_cost, 10)
        b["cap_coin_out"] = round(float(b["cap_coin_out"]) + cq, 12)
        b["cap_coin_out_basis"] = round(float(b["cap_coin_out_basis"]) + basis_t - g_cost, 10)
        out.append(f"➖ [سحب] الخانة {key} (بيع): " + " · ".join(
            ([f"ربح {_n(gq)} عملة → المُراكِم"] if gq > 1e-12 else []) + ([f"رأس مال {_n(cq)} عملة → محفظتك"] if cq > 1e-12 else [])
            + [f"أمر البيع {'المنشور' if op.get('live') else 'في الذاكرة'} صغر الآن"]))
        ho = _ri_handoff(state, b, gq, g_cost, f"سحب ربح من جهة البيع — الخانة {key}", key) if gq > 1e-12 else None
        if ho:
            out.append(ho)
    else:                                                 # wd_usd — دولار الحصّالة + نمو ما دخل الأمر بعد (بلا أي أمر)
        c_part, g_part = float(op["c"]), float(op["g"])
        lv["usd_book"] = round(float(op["ub"]), 10)
        lv["inj_book"] = round(float(op["ib"]), 10)
        lv["grown_qty"] = round(float(op["gq"]), 12)
        s["g"] = float(lv["grown_qty"])
        lv["inj_grown"] = round(float(op["ig"]), 10)
        _ri_out(state, b, c_part, g_part)
        out.append(f"➖ [سحب] الخانة {key}: " + " · ".join(
            ([f"رأس مال {_n(c_part)}$ → محفظتك"] if c_part > 1e-12 else []) + ([f"ربح {_n(g_part)}$ → الربح المحرر"] if g_part > 1e-12 else [])
            + ["من الحصّالة (لا يتغيّر أي أمر)"]))
    gain_usd = (round(float(op["q"]) * px - float(op["c"]), 10) if op["kind"] == "wd_buy"
                else float(op.get("g") or 0) if op["kind"] == "wd_usd" else 0.0)
    if gain_usd > 1e-12:                                  # (مثل الشبكي: ربح محرر بسحب ⇒ آخر صفقة للوحة)
        state["last_trade"] = {"buy": 0, "sell": 0, "qty": 0.0, "profit": round(gain_usd, 6), "ts": time.time(),
                               "n": int((state.get("last_trade") or {}).get("n") or 0) + 1, "reinvest_release": True,
                               "partial": True, "withdraw": True, "release_capital": round(float(op.get("c") or 0), 6), "slot": key}
    return out


def _ri_take_usd(lv, px, want_c, want_g, coins_cap):
    """💵 من الحصّالة أولاً (رأس المال من حصة المحقون) ثم من النمو اللي **ما دخل أي أمر** (coins_cap عملة بالأكثر) ⇒
    (رأس مال، ربح، الدفتر الجديد) — بلا ما يغيّر الدفتر نفسه"""
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    ub, ib = float(lv.get("usd_book") or 0), float(lv.get("inj_book") or 0)
    gq, ig = float(lv.get("grown_qty") or 0), float(lv.get("inj_grown") or 0)
    got_c = got_g = 0.0
    t = min(want_c, ib, ub)
    if t > 0:
        ub, ib, got_c = ub - t, ib - t, got_c + t
    t = min(want_g, max(0.0, ub - ib))
    if t > 0:
        ub, got_g = ub - t, got_g + t
    room = max(0.0, min(gq, coins_cap))
    rc = max(0.0, want_c - got_c)
    if rc > 1e-12 and px > 0 and room > 0:
        q = _step_round(min(room, rc / px, ig / px if px > 0 else 0) + 1e-12, lot, ROUND_FLOOR)
        if q > 0:
            gq, ig, room, got_c = gq - q, max(0.0, ig - q * px), room - q, got_c + q * px
    rg = max(0.0, want_g - got_g)
    if rg > 1e-12 and px > 0 and room > 0:
        q = _step_round(min(room, rg / px) + 1e-12, lot, ROUND_FLOOR)
        if q > 0:
            gq, room, got_g = gq - q, room - q, got_g + q * px
    return got_c, got_g, {"ub": ub, "ib": ib, "gq": gq, "ig": ig}


def _ri_withdraw(state, b):
    """➖ طلب السحب من اللوحة: كل بند لخانة وحدة حسب جهتها · الأساس ما ينلمس · ينطبق مرة وحدة بالضبط"""
    if not os.path.exists(WITHDRAW_FILE):
        return 0
    req = load_json(WITHDRAW_FILE)
    if not isinstance(req, dict):
        _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] طلب تالف — تم تجاهله")
        return 0
    rid = "w:" + str(req.get("id") or req.get("ts") or "")
    done = b.setdefault("reqs", [])
    if rid != "w:" and rid in done:
        _ri_drop(WITHDRAW_FILE)
        return 0
    if not b.get("on"):
        _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] إعادة الاستثمار متوقفة — أُلغي الطلب")
        return 0
    try:
        age = time.time() - float(req.get("ts") or 0)
    except Exception:
        age = float("inf")
    if not age <= 86400:
        _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] الطلب قديم (أكثر من يوم) — أُلغي")
        return 0
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    S = _slots(state)
    lines, sends, n = [], [], 0

    def num(it, k):
        v = float(it.get(k) or 0)
        if not math.isfinite(v) or v < 0:
            raise ValueError(k)
        return v

    for it in (req.get("items") or [])[:64]:
        try:
            key = str(it.get("k") or "").strip()
            s, lv = S.get(key), (b.get("levels") or {}).get(key)
            cap, gain = num(it, "cap"), num(it, "gain")
            cq_w, gq_w, cd, gd = num(it, "cap_q"), num(it, "gain_q"), num(it, "cap_d"), num(it, "gain_d")
            if s is None or lv is None:
                lines.append(f"⚠️ [سحب] الخانة {key}: لا يوجد فيها شيء معاد استثماره — تم تجاهل البند")
                continue
            if s.get("am"):
                lines.append(f"⚠️ [سحب] الخانة {key}: تعديل سابق لأمرها لم يكتمل — أعد المحاولة بعد قليل")
                continue
            px = float(lv.get("px") or s["bp"])
            gq, ig = float(lv.get("grown_qty") or 0), float(lv.get("inj_grown") or 0)
            st_o = (s.get("o") or {}).get("st")
            n0, k0 = len(lines), len(sends)
            if s["side"] == "buy" and cap + gain <= 0 and cq_w + gq_w + cd + gd > 0:   # (انكتب لجهة البيع والخانة صارت شراء ⇒ دولار)
                cap, gain = cq_w * px + cd, gq_w * px + gd
            if s["side"] == "sell":
                if cq_w + gq_w + cd + gd <= 0 and cap + gain > 0:       # (طلب بالدولار بس ⇒ عملة بسعر الخانة — مثل الشبكي)
                    cq_w, gq_w = cap / px, gain / px
                inord = max(0.0, min(gq, float(s.get("sq") or 0) - float(s.get("acc") or 0) - _ri_base_sell(state, s)))
                cap_av = min(ig / px, gq) if px > 0 else 0.0
                wc, wg = min(cq_w, cap_av), min(gq_w, max(0.0, gq - cap_av))
                tot = _step_round(min(wc + wg, inord) + 1e-12, lot, ROUND_FLOOR)
                if wc + wg > 1e-12:
                    if tot <= 0:
                        lines.append(f"⚠️ [سحب] الخانة {key}: لا توجد عملة معاد استثمارها داخل أمر البيع الآن")
                    else:
                        g_t = _step_round(min(wg, tot) + 1e-12, lot, ROUND_FLOOR)
                        op = {"kind": "wd_sell", "tot": tot, "gq": g_t, "cq": round(tot - g_t, 12)}
                        if _o_live(s):
                            op["live"] = True
                            s["am"] = {"oid": str(s["o"]["id"]), "old": float(s["o"].get("sz") or 0),
                                       "new": round(float(s["o"].get("sz") or 0) - tot, 12), "ts": time.time(), "n": 0, "op": op}
                            sends.append(key)
                        elif st_o == "send":
                            lines.append(f"⚠️ [سحب] الخانة {key}: أمرها في الطريق إلى المنصة — أعد المحاولة بعد قليل")
                        else:
                            lines += _ri_book(state, b, key, s, op)
                            n += 1
                if cd + gd > 1e-12:                                   # 💵 الحصّالة + نمو ما دخل أمر البيع بعد
                    inord2 = max(0.0, min(float(lv.get("grown_qty") or 0), float(s.get("sq") or 0) - float(s.get("acc") or 0) - _ri_base_sell(state, s)))
                    if s.get("am"):
                        inord2 = max(0.0, inord2 - float(s["am"]["op"].get("tot") or 0))
                    av = _ri_split(lv)
                    c, g_, nb = _ri_take_usd(lv, px, min(cd, av["cap"]), min(gd, av["gain"]),
                                             float(lv.get("grown_qty") or 0) - inord2 - (float(s["am"]["op"].get("tot") or 0) if s.get("am") else 0))
                    if c + g_ > 1e-12:
                        lines += _ri_book(state, b, key, s, dict(nb, kind="wd_usd", c=round(c, 10), g=round(g_, 10)))
                        n += 1
                if len(lines) == n0 and len(sends) == k0:
                    lines.append(f"⚠️ [سحب] الخانة {key}: لا يوجد ما يُسحب الآن من هذا الجيب — لم يتغيّر شيء")
                continue
            # 💵 جهة الشراء: الحصّالة أولاً ثم النمو داخل أمر الشراء
            av = _ri_split(lv)
            want_c, want_g = min(cap, av["cap"]), min(gain, av["gain"])
            if want_c + want_g <= 1e-12:
                lines.append(f"⚠️ [سحب] الخانة {key}: لا يوجد ما يُسحب الآن من هذا الجيب — لم يتغيّر شيء")
                continue
            c, g_, nb = _ri_take_usd(lv, px, want_c, want_g, 0.0)       # الحصّالة (بلا نمو)
            if c + g_ > 1e-12:
                lines += _ri_book(state, b, key, s, dict(nb, kind="wd_usd", c=round(c, 10), g=round(g_, 10)))
                n += 1
            rc, rg = max(0.0, want_c - c), max(0.0, want_g - g_)
            gq = float(lv.get("grown_qty") or 0)
            if rc + rg > 1e-12 and gq > 0 and px > 0:
                q = _step_round(min(gq, (rc + rg) / px) + 1e-12, lot, ROUND_FLOOR)
                if q > 0:
                    c_part = round(min(q * px * rc / (rc + rg), float(lv.get("inj_grown") or 0)), 10)
                    op = {"kind": "wd_buy", "q": q, "c": c_part}
                    if _o_live(s):
                        new = round(float(s["o"].get("sz") or 0) - q, 12)
                        if new <= 0:
                            lines.append(f"⚠️ [سحب] الخانة {key}: أمر الشراء نُفّذ أغلبه — لا يمكن تصغيره الآن")
                            continue
                        op["live"] = True
                        s["am"] = {"oid": str(s["o"]["id"]), "old": float(s["o"].get("sz") or 0), "new": new, "ts": time.time(), "n": 0, "op": op}
                        sends.append(key)
                    elif st_o == "send":
                        lines.append(f"⚠️ [سحب] الخانة {key}: أمرها في الطريق إلى المنصة — أعد المحاولة بعد قليل")
                    else:
                        lines += _ri_book(state, b, key, s, op)
                        n += 1
        except Exception as e:
            lines.append(f"⚠️ [سحب] بند فاشل: {type(e).__name__}")
    if rid != "w:":
        done.append(rid)
        del done[:-32]
    if not _commit(state, lines):
        for key in sends:
            S[key].pop("am", None)
        return 0
    _ri_drop(WITHDRAW_FILE)
    out = []
    for key in sends:
        _ri_am_send(state, key, S[key])
        out += _ri_am_check(state, key, S[key], tries=5)
    if sends:
        _commit(state, out)
    return n + len(sends)


def _ri_sweep(state, b):
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
