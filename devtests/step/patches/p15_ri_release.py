# 🪜🔓 patch 15 (engine · reinvest phase D — release + unwind, the grid's release / _unwind_step per slot · REINVEST_PLAN.md ١٠ · ١١ · ج)
#   the release (reinvest_release.flag — the grid's flag — or the setting switched off): everything reinvested and injected is
#   released NOW — dollars ⇒ the released profit (total_profit) · coins ⇒ the accumulator at their real cost (one handoff) ·
#   capital ⇒ your wallet (dollars, or coins) · the grown published orders shrink back to their base at OKX now (amend-order,
#   decision ج — the grid's way: no order cancelled) · the pots' dollars and anything not inside a published order at once.
#   What OKX refuses to shrink (it filled that moment · partly filled) ⇒ an unwind entry that finishes its way (the grid's
#   machine): retried every 60 s · the grown buy filled ⇒ it is a grown sell now (its coins → the accumulator when it shrinks) ·
#   the grown sell filled ⇒ its growth came back as dollars ⇒ released as profit at that sale · moved to memory ⇒ released there.
#   After the release every sale is ordinary profit and every buy its base · the setting on again ⇒ reinvesting again (what is
#   still unwinding goes back to reinvesting, as the grid). Exactly once: the release is written before anything is sent and
#   finishes after a power cut · the flag is deleted only after the save that took it.
#   python3 devtests/step/patches/p15_ri_release.py ENGINE.py
import os, sys

R = [
    # the tick: the release · the unwind · the switch back on
    ('''    _ri_am_tick(state, b)
    if b.get("on"):
        _ri_pct_sync(state, b)
    _ri_inject(state, b)
''',
     '''    _ri_am_tick(state, b)
    if b.get("rel_open"):
        _ri_release_end(state, b)                         # (انقطاع بنص التحرير ⇒ يكمل)
    want = bool(config.get("reinvest"))
    if os.path.exists(RELEASE_FLAG) or (b.get("on") and not want):
        if b.get("on") or b.get("broken") or _ri_has(b):
            _ri_release(state, b)
        _ri_drop(RELEASE_FLAG)
    elif want and not b.get("on") and not b.get("broken") and not b.get("rel_open"):
        _ri_back_on(state, b)
    if not b.get("on") and b.get("unwind"):
        _ri_unwind(state, b)
    if b.get("on"):
        _ri_pct_sync(state, b)
    _ri_inject(state, b)
'''),
    ('''        if os.path.exists(WITHDRAW_FILE):
            _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        return
''',
     '''        if os.path.exists(WITHDRAW_FILE):
            _ri_drop(WITHDRAW_FILE, "⚠️ [سحب] إعادة الاستثمار غير مفعّلة لهذا البوت — أُلغي الطلب")
        if os.path.exists(RELEASE_FLAG):
            _ri_drop(RELEASE_FLAG)
        return
'''),
    # a broken pot is remembered (never switched back on by itself)
    ('''        b["on"] = False
        log_trade_history(SYMBOL, f"🛑 [إعادة الاستثمار] خلل بحصّالة الخانة {key} ({_n(lv['usd_book'])}$) — أوقفت التراكم")''',
     '''        b["on"] = False
        b["broken"] = time.time()
        log_trade_history(SYMBOL, f"🛑 [إعادة الاستثمار] خلل بحصّالة الخانة {key} ({_n(lv['usd_book'])}$) — أوقفت التراكم")'''),
    # the release's resizes book quietly (one summary) · after it, each writes its own unwind line
    ('''    out = []
    if op["kind"] == "wd_buy":                            # 💵 النمو داخل أمر الشراء ⇒ دولار (رأس مال · ربح)''',
     '''    if op.get("rel"):
        return _ri_book_rel(state, b, key, s, lv, px, op)
    out = []
    if op["kind"] == "wd_buy":                            # 💵 النمو داخل أمر الشراء ⇒ دولار (رأس مال · ربح)'''),
    ('''    if op["kind"] in ("wd_buy", "wd_sell"):
        return [f"⚠️ [سحب] الخانة {key}: لم يصغر أمر {'الشراء' if op['kind'] == 'wd_buy' else 'البيع'} ({why}) — لم يتغيّر شيء"]
    return []
''',
     '''    if op.get("rel"):                                     # 🔓 المنصة ما صغّرته ⇒ يكمل طريقه (تفكيك)
        e = b.setdefault("unwind", {}).setdefault(key, {"side": s.get("side"), "ts": time.time(), "tries": 0})
        e["side"] = s.get("side")
        e["why"] = str(why)
        n = int(e.get("tries") or 0)
        if not b.get("rel_open") and (n in (1, 5, 20) or (n and n % 100 == 0)):
            return [f"⏳ [إيقاف] الخانة {key}: المنصة لم تقبل تصغير الأمر بعد ({why} · محاولة {n}) — نعيد تلقائياً كل دقيقة حتى ينجح أو يُنفَّذ"]
        return []
    if op["kind"] in ("wd_buy", "wd_sell"):
        return [f"⚠️ [سحب] الخانة {key}: لم يصغر أمر {'الشراء' if op['kind'] == 'wd_buy' else 'البيع'} ({why}) — لم يتغيّر شيء"]
    return []
'''),
    # a sale while released / unwinding: its growth came back as dollars ⇒ released at that sale (the next buy = its base)
    ('''                         + f" · 🪜 المستوى {s['j']} · الجزء {s['k']}/{N} · البيعة {n_sale}")
    elif acc > 0:''',
     '''                         + f" · 🪜 المستوى {s['j']} · الجزء {s['k']}/{N} · البيعة {n_sale}")
        if rb is not None and not rb.get("on") and not rb.get("broken") and key in (rb.get("levels") or {}):
            lv = rb["levels"][key]
            if float(lv.get("grown_qty") or 0) > 0 or float(lv.get("usd_book") or 0) > 0:
                lines += _ri_unwind_free(state, rb, key, s, lv, float(lv.get("grown_qty") or 0), "بيع مكبّر نفّذ")
    elif acc > 0:'''),
    # the machinery, before _ri_sweep
    ('''def _ri_sweep(state, b):
''',
     '''# ================= 🔓 التحرير والتفكيك — نفس فكرة الشبكي (release · _unwind_step) لكل خانة =================
RELEASE_FLAG = "reinvest_release.flag"    # 🔓 علم من اللوحة (نفس علم الشبكي)
RETRY_SEC = 60.0                          # ⏳ أمر رفضت المنصة تصغيره ⇒ نعيد كل دقيقة


def _ri_has(b):
    return any(float(lv.get("usd_book") or 0) > 1e-12 or float(lv.get("grown_qty") or 0) > 1e-12 for lv in (b.get("levels") or {}).values())


def _ri_cap_of(lv, coins):
    """💉 حصة رأس المال المحقون من `coins` من النمو (بالتناسب) — بسعر الخانة"""
    g = float(lv.get("grown_qty") or 0)
    ig = float(lv.get("inj_grown") or 0)
    return round(ig * min(1.0, coins / g), 10) if g > 0 else 0.0


def _ri_rel_free(state, b, key, s, lv, coins):
    """💵 الحصّالة + `coins` من نمو ما داخل أي أمر ⇒ يتحرر هسه: رأس المال ⇒ محفظتك · الربح ⇒ الربح المحرر · يرجّع (رأس مال، ربح)"""
    px = float(lv.get("px") or s["bp"])
    coins = max(0.0, min(float(coins), float(lv.get("grown_qty") or 0)))
    c_g = _ri_cap_of(lv, coins)
    ub, ib = float(lv.get("usd_book") or 0), float(lv.get("inj_book") or 0)
    total = round(ub + coins * px, 10)
    cap = round(min(max(0.0, ib + c_g), total), 10)
    gain = round(total - cap, 10)
    lv["usd_book"], lv["inj_book"] = 0.0, 0.0
    lv["grown_qty"] = round(max(0.0, float(lv.get("grown_qty") or 0) - coins), 12)
    lv["inj_grown"] = round(max(0.0, float(lv.get("inj_grown") or 0) - c_g), 10)
    if lv["grown_qty"] <= 1e-12:
        lv["grown_qty"], lv["inj_grown"] = 0.0, 0.0
    s["g"] = float(lv["grown_qty"])
    _ri_out(state, b, cap, gain)
    ro = b.get("rel_open")
    if ro:
        ro["cap_usd"] = round(float(ro.get("cap_usd") or 0) + cap, 10)
    return cap, gain


def _ri_unwind_free(state, b, key, s, lv, coins, why):
    """🔓 التفكيك: النمو صار دولار (ما انشرى · أو رجع ببيعة) ⇒ يتحرر هسه · سطر بالسجل"""
    cap, gain = _ri_rel_free(state, b, key, s, lv, coins)
    (b.get("unwind") or {}).pop(key, None)
    if cap + gain <= 1e-12:
        return []
    return [f"🔓 [تفكيك] الخانة {key} — {why} · تحرّر ربح {_n(gain)}$ (دولار)"
            + (f" · رأس مال {_n(cap)}$ عاد إلى المحفظة" if cap > 1e-12 else "") + f" · باقي {len(b.get('unwind') or {})} أمر"]


def _ri_book_rel(state, b, key, s, lv, px, op):
    """📒 تصغير أمر منشور بالتحرير انطبق (المنصة بيّنته): النمو اللي داخله يتحرر — الشراء دولار · البيع عملة للمُراكِم"""
    ro = b.get("rel_open")
    if op["kind"] == "wd_buy":
        q = float(op["q"])
        c_g = _ri_cap_of(lv, q)
        val = round(q * px, 10)
        cap = round(min(c_g, val), 10)
        gain = round(val - cap, 10)
        lv["grown_qty"] = round(max(0.0, float(lv["grown_qty"]) - q), 12)
        lv["inj_grown"] = round(max(0.0, float(lv.get("inj_grown") or 0) - c_g), 10)
        if lv["grown_qty"] <= 1e-12:
            lv["grown_qty"], lv["inj_grown"] = 0.0, 0.0
        s["g"] = float(lv["grown_qty"])
        _ri_out(state, b, cap, gain)
        if s["g"] <= 1e-12:
            (b.get("unwind") or {}).pop(key, None)
        if ro:
            ro["cap_usd"] = round(float(ro.get("cap_usd") or 0) + cap, 10)
            ro["now"] = int(ro.get("now") or 0) + (1 if op.get("live") else 0)
            return []
        return [f"🔓 [تفكيك] الخانة {key} — تصغّر أمر الشراء في وقت مناسب · تحرّر ربح {_n(gain)}$ (دولار)"
                + (f" · رأس مال {_n(cap)}$ عاد إلى المحفظة" if cap > 1e-12 else "") + f" · باقي {len(b.get('unwind') or {})} أمر"]
    tot = float(op["tot"])                                # wd_sell: العملة فوق الأساس داخل البيع
    c_g = _ri_cap_of(lv, tot)
    cq = min(tot, _lot_floor(c_g / px)) if px > 0 else 0.0
    gq = round(tot - cq, 12)
    sq0 = float(s.get("sq") or 0)
    basis_t = round(float(s.get("spent") or 0) * (tot / sq0), 10) if sq0 > 0 else 0.0
    g_cost = round(basis_t * (gq / tot), 10) if tot > 0 else 0.0
    s["sq"] = round(sq0 - tot, 12)
    s["spent"] = round(float(s.get("spent") or 0) - basis_t, 10)
    lv["grown_qty"] = round(max(0.0, float(lv["grown_qty"]) - tot), 12)
    lv["inj_grown"] = round(max(0.0, float(lv.get("inj_grown") or 0) - c_g), 10)
    s["g"] = float(lv["grown_qty"])
    for f in ("out_coin", "out_coin_basis", "cap_coin_out", "cap_coin_out_basis", "out_gain"):
        b.setdefault(f, 0.0)
    b["inj_total"] = round(float(b.get("inj_total") or 0) - c_g, 10)        # (رأس المال بقيمته بالحصّالة)
    b["out_gain"] = round(float(b["out_gain"]) + tot * px - c_g, 10)
    b["out_coin"] = round(float(b["out_coin"]) + gq, 12)
    b["out_coin_basis"] = round(float(b["out_coin_basis"]) + g_cost, 10)
    b["cap_coin_out"] = round(float(b["cap_coin_out"]) + cq, 12)
    b["cap_coin_out_basis"] = round(float(b["cap_coin_out_basis"]) + basis_t - g_cost, 10)
    if s["g"] <= 1e-12 or op.get("last"):
        (b.get("unwind") or {}).pop(key, None)
    if ro:
        hb = ro.setdefault("ho", {"coin": 0.0, "cost": 0.0})
        hb["coin"] = round(float(hb["coin"]) + gq, 12)
        hb["cost"] = round(float(hb["cost"]) + g_cost, 10)
        ro["cap_coin"] = round(float(ro.get("cap_coin") or 0) + cq, 12)
        ro["now"] = int(ro.get("now") or 0) + (1 if op.get("live") else 0)
        return []
    out = []
    if gq > 1e-12:
        ho = _ri_handoff(state, b, gq, g_cost, f"تحرير — الخانة {key} تصغّرت في وقت مناسب", key)
        if ho:
            out.append(ho)
    out.insert(0, f"🔓 [تفكيك] الخانة {key} — تصغّر أمر البيع في وقت مناسب"
               + (f" · {_n(gq)} عملة للمُراكِم" if gq > 1e-12 else "") + (f" · {_n(cq)} عملة رأس مال بقيت في المحفظة" if cq > 1e-12 else "")
               + f" · باقي {len(b.get('unwind') or {})} أمر")
    return out


def _ri_rel_plan(state, b, key, s, lv):
    """خانة وحدة بالتحرير/التفكيك: اللي برّه الأوامر يتحرر هسه · اللي داخل أمر منشور ⇒ قيد تصغير · يرجّع (ينرسل؟، أسطر)"""
    g = float(lv.get("grown_qty") or 0)
    o = s.get("o") or {}
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    wait = lambda: b.setdefault("unwind", {}).setdefault(key, {"side": s.get("side"), "ts": time.time(), "tries": 0})
    if s.get("side") == "buy":
        if not o:
            _ri_rel_free(state, b, key, s, lv, g)
            return False, []
        _ri_rel_free(state, b, key, s, lv, 0.0)                      # الحصّالة (دولار) هسه
        if g <= 1e-12:
            return False, []
        take = _lot_floor(min(g, float(o.get("sz") or 0) - lot))
        if o.get("st") != "live" or take <= 0:
            wait()
            return False, []
        s["am"] = {"oid": str(o["id"]), "old": float(o.get("sz") or 0), "new": round(float(o.get("sz") or 0) - take, 12), "ts": time.time(),
                   "n": 0, "op": {"kind": "wd_buy", "q": take, "c": 0.0, "rel": True, "live": True}}
        wait()
        return True, []
    inord = _lot_floor(max(0.0, min(g, float(s.get("sq") or 0) - float(s.get("acc") or 0) - _ri_base_sell(state, s))))
    _ri_rel_free(state, b, key, s, lv, max(0.0, g - inord))         # الحصّالة + نمو ما دخل البيع ⇒ دولار هسه
    if inord <= 0:
        return False, []
    op = {"kind": "wd_sell", "tot": inord, "rel": True, "last": True}
    if not o:
        return False, _ri_book_rel(state, b, key, s, lv, float(lv.get("px") or s["bp"]), op)
    if o.get("st") != "live":
        wait()
        return False, []
    op["live"] = True
    s["am"] = {"oid": str(o["id"]), "old": float(o.get("sz") or 0), "new": round(float(o.get("sz") or 0) - inord, 12), "ts": time.time(),
               "n": 0, "op": op}
    wait()
    return True, []


def _ri_release(state, b):
    """🔓 التحرير (الزر · أو الإعداد انطفى): كل المعاد استثماره والمحقون يتحرر **الآن** — مثل الشبكي بالضبط"""
    b["on"] = False
    b.pop("broken", None)
    b["rel_open"] = {"ts": time.time(), "out_usd0": float(b.get("out_usd") or 0), "cycles": int(b.get("cycles") or 0),
                     "days": round(max(0.0, (time.time() - float(b.get("started_ts") or time.time())) / 86400.0), 2)}
    if not _commit(state, []):                             # أول شي: ما بيه تراكم جديد
        return
    S = _slots(state)
    sends = []
    for key, lv in list((b.get("levels") or {}).items()):
        s = S.get(key)
        if s is None or s.get("am"):
            if s is not None:
                b.setdefault("unwind", {}).setdefault(key, {"side": s.get("side"), "ts": time.time(), "tries": 0})
            continue
        if _ri_rel_plan(state, b, key, s, lv)[0]:
            sends.append(key)
    if not _commit(state, []):                             # القيود + اللي تحرر هسه — على القرص قبل أي طلب للمنصة
        return
    _ri_drop(RELEASE_FLAG)
    for key in sends:
        _ri_am_send(state, key, S[key])
        _ri_am_check(state, key, S[key], tries=5)
    _ri_release_end(state, b)


def _ri_release_end(state, b):
    """🔓 نهاية التحرير: اللي ما انحسم من المنصة ⇒ تفكيك · تسليم العملة مرة وحدة · سطر الملخّص · آخر صفقة للوحة"""
    ro = b.get("rel_open")
    if not ro:
        return
    S = _slots(state)
    for key, s in S.items():                              # تصغير ما انحسم بعد ⇒ يكمل كتفكيك (التسوية تحسمه لاحقاً)
        if s.get("am") and (s["am"].get("op") or {}).get("rel"):
            b.setdefault("unwind", {}).setdefault(key, {"side": s.get("side"), "ts": time.time(), "tries": 0})
    gain = round(float(b.get("out_usd") or 0) - float(ro.get("out_usd0") or 0), 10)
    cap = round(float(ro.get("cap_usd") or 0), 10)
    hb = ro.get("ho") or {}
    coin, cost = float(hb.get("coin") or 0), float(hb.get("cost") or 0)
    capcoin = float(ro.get("cap_coin") or 0)
    left = len(b.get("unwind") or {})
    lines = []
    if coin > 1e-12 and cost > 0:
        ho = _ri_handoff(state, b, coin, cost, "إطفاء إعادة الاستثمار", None)
        if ho:
            lines.append(ho)
    avg = cost / coin if coin > 0 else 0.0
    lines.insert(0, f"🔄 [تحرير ربح داخلي] الربح: +{_n(gain)}$"
                 + (f" · رأس مال محقون: {_n(cap)}$ (عاد إلى المحفظة لا إلى الربح)" if cap > 1e-12 else "")
                 + (f" · عملة رأس مال {_n(capcoin)} بقيت في المحفظة" if capcoin > 1e-12 else "")
                 + f" · معاد استثمارها تحرّرت | عملة: {_n(coin)} @ {_n(avg)}$ (للمُراكِم) | {int(ro.get('now') or 0)} أمر منشور تصغّر فوراً"
                 + (f" · {left} رفضت المنصة تصغيره فينتظر مصيره" if left else "")
                 + f" | المدة: {ro.get('days', 0)} يوم · {int(ro.get('cycles') or 0)} دورة")
    if gain > 1e-12 or cap > 1e-12 or coin > 1e-12:
        state["last_trade"] = {"buy": 0, "sell": 0, "qty": round(coin, 10), "profit": round(gain, 6), "ts": time.time(),
                               "n": int((state.get("last_trade") or {}).get("n") or 0) + 1, "reinvest_release": True,
                               "release_coin": round(coin, 10), "release_avg": round(avg, 12), "unwind_left": left,
                               "release_capital": round(cap, 6)}
    b["released"] = {"usd": gain, "capital": cap, "coin": round(coin, 12), "avg_px": round(avg, 12), "capital_coin": round(capcoin, 12),
                     "ts": time.time(), "days": ro.get("days", 0), "cycles": int(ro.get("cycles") or 0), "unwind": left,
                     "resized_now": int(ro.get("now") or 0)}
    b["cycles"] = 0
    b.pop("rel_open", None)
    _commit(state, lines)


def _ri_unwind(state, b):
    """🔓 كل دورة بعد التحرير: الأوامر اللي رفضت المنصة تصغيرها تكمل طريقها (مثل الشبكي) — تصغير بوقت مناسب كل دقيقة ·
    الشراء نفّذ ⇒ صار بيع مكبّر · خرج للذاكرة ⇒ يتحرر هناك · (البيع نفّذ ⇒ ينحرر ببيعته نفسها — _finish)"""
    S = _slots(state)
    lines, changed, sends = [], False, []
    for key, e in list((b.get("unwind") or {}).items()):
        s, lv = S.get(key), (b.get("levels") or {}).get(key)
        if s is None or lv is None or (float(lv.get("grown_qty") or 0) <= 1e-12 and float(lv.get("usd_book") or 0) <= 1e-12):
            b["unwind"].pop(key, None)
            changed = True
            continue
        if s.get("am"):
            continue
        if e.get("side") != s.get("side"):
            e["side"] = s.get("side")                     # الشراء المكبّر نفّذ ⇒ صار بيعاً مكبّراً
            changed = True
        o = s.get("o") or {}
        if not o:                                         # خرج من المنصة للذاكرة ⇒ يتحرر هناك
            if s["side"] == "buy":
                lines += _ri_unwind_free(state, b, key, s, lv, float(lv.get("grown_qty") or 0), "شراء مكبّر خرج من المنصة للذاكرة — ما انشرى")
            else:
                lines += _ri_rel_plan(state, b, key, s, lv)[1]
                b["unwind"].pop(key, None)
            changed = True
            continue
        if o.get("st") != "live" or time.time() - float(e.get("retry_ts") or 0) < RETRY_SEC:
            continue
        e["retry_ts"] = time.time()
        e["tries"] = int(e.get("tries") or 0) + 1
        changed = True
        if _ri_rel_plan(state, b, key, s, lv)[0]:
            sends.append(key)
    if changed or lines:
        if not _commit(state, lines):
            for key in sends:
                S[key].pop("am", None)
            return
    out = []
    for key in sends:
        _ri_am_send(state, key, S[key])
        out += _ri_am_check(state, key, S[key], tries=3)
    if sends:
        _commit(state, out)


def _ri_back_on(state, b):
    """🔁 الإعداد رجع يشتغل: تشغيل جديد — اللي لسه يتفكّك يرجع لإعادة الاستثمار كأن التحرير ما صار (مثل الشبكي)"""
    b["on"] = True
    b["started_ts"] = time.time()
    uw = b.get("unwind") or {}
    n = len(uw)
    back = sum(float((b.get("levels") or {}).get(k, {}).get("grown_qty") or 0) * float((b.get("levels") or {}).get(k, {}).get("px") or 0) for k in uw)
    b["unwind"] = {}
    _commit(state, [f"🔁 [إعادة الاستثمار] شُغّلت من جديد"
                    + (f" — {n} أمر مكبّر لم يكتمل تفكيكه عاد لإعادة الاستثمار كأن الإطفاء لم يحدث ({_n(back)}$ نمو يكمل)" if n else "")])


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
