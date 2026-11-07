# 🪜💠 patch 11 (engine · reinvest phase A — the same idea as the grid's reinvest.py, per slot · REINVEST_PLAN.md rules ١–٧ · ١٢)
#   a slot (level · part) = one pot: its sale's real profit × the percentage (reinvest_pct, live: kept in the book, «⚖️» line when it
#   changes) goes to the slot's pot · the rest is
#   ordinary profit · the pot turns into quantity only in whole lots at the slot's buy price · the slot's next buy = base + growth ·
#   «💠 [ربح داخلي]» line for the reinvested share · no sale line when the ordinary share is nothing (as the grid) · the reinvested
#   money stays out of total_profit (locked in the orders) · a broken pot stops the accumulating · all in the fill's one save.
#   Every sale line carries its number («البيعة n») so a test can count each sale once.
#   python3 devtests/step/patches/p11_ri_core.py ENGINE.py
import os, sys

R = [
    # _views: the dashboard's view of a buy = base + growth
    ('''                   "locked_qty": round(max(0.0, float(s["q"]) - acc), 10), "is_recovery": False, "slot": key}
''',
     '''                   "locked_qty": round(max(0.0, float(s["q"]) + float(s.get("g") or 0) - acc), 10), "is_recovery": False, "slot": key}
'''),
    # _rem: a buy is base + growth
    ('''def _rem(s):
    tgt = float(s["q"]) if s["side"] == "buy" else float(s.get("sq") or 0)
''',
     '''def _rem(s):
    tgt = float(s["q"]) + float(s.get("g") or 0) if s["side"] == "buy" else float(s.get("sq") or 0)   # 💠 الشراء = الأساس + النمو
'''),
    # the percentage, every loop (after the pending fill lines)
    ('''        _fx_log_flush(state)
        save_json(STATE_FILE, state)
    try:
        r = trade_api.get_order_list(instId=SYMBOL)
''',
     '''        _fx_log_flush(state)
        save_json(STATE_FILE, state)
    _ri_tick(state)                                       # 💠 النسبة حيّة
    try:
        r = trade_api.get_order_list(instId=SYMBOL)
'''),
    # the reinvest book, before _send
    ('''def _send(state, key, s, cp):
''',
     '''# ================= 💠 إعادة الاستثمار — نفس فكرة الشبكي (reinvest.py) لكل خانة =================
# كل خانة (المستوى · الجزء) صندوق مستقل: ربح بيعتها الحقيقي × النسبة يرجع لحصّالتها · الحصّالة تتحول كمية بوحدات كاملة بسعر شرائها ·
# شراؤها الجاي = الأساس + النمو · المعاد محبوس بالأوامر (ما يدخل total_profit) · الكل بحفظة التنفيذ نفسها
def _ri(state):
    """دفتر إعادة الاستثمار (نفس حقول الشبكي) — بس إذا مفعّلة بالإعداد أو الدفتر موجود"""
    if not state.get("reinvest") and not config.get("reinvest"):
        return None
    b = state.setdefault("reinvest", {})
    b.setdefault("on", bool(config.get("reinvest")))
    b.setdefault("started_ts", time.time())
    b.setdefault("levels", {})
    b.setdefault("cycles", 0)
    b.setdefault("credited", 0.0)                         # كل ربح انعاد استثماره (الربح الحقيقي = total_profit + هذا)
    return b


def _ri_pct(b):
    """⚖️ نسبة الربح اللي ترجع لنفس الخانة (0..1) — من الدفتر (الافتراضي 100) · _ri_tick يحدّثها من الإعداد حيّاً"""
    try:
        v = b.get("pct")
        v = 100.0 if v is None else float(v)
    except Exception:
        v = 100.0
    if not math.isfinite(v):
        v = 100.0
    return max(0.0, min(100.0, v)) / 100.0


def _ri_tick(state):
    """⚖️ النسبة (reinvest_pct بالإعداد) تنحفظ بالدفتر بكل دورة — حيّة بلا إعادة تشغيل · لمن تتغيّر سطر بالسجل (مثل الشبكي)"""
    b = _ri(state)
    if b is None or not b.get("on"):
        return
    p = config.get("reinvest_pct")
    if p in (None, ""):
        return
    try:
        p = float(p)
    except Exception:
        return
    if not math.isfinite(p):
        return
    p = max(0.0, min(100.0, p))
    old = b.get("pct")
    old = 100.0 if old is None else float(old)
    if abs(old - p) > 1e-9:
        b["pct"] = p
        _commit(state, [f"⚖️ [إعادة الاستثمار] النسبة صارت {p:.0f}% للأمر نفسه · {100.0 - p:.0f}% ربح عادي"])


def _ri_lv(b, key, s):
    return b["levels"].setdefault(key, {"base_qty": float(s["q"]), "grown_qty": 0.0, "usd_book": 0.0, "px": float(s["bp"]),
                                        "inj_book": 0.0, "inj_grown": 0.0, "cycles": 0})


def _ri_convert(state, b, key, s):
    """🐖 الحصّالة تتحول كمية بس لمن تتجمع وحدة كاملة (خطوة المنصة) بسعر شراء الخانة — ولا سنت يضيع"""
    lv = _ri_lv(b, key, s)
    px = float(lv.get("px") or s["bp"])
    lot = INSTRUMENT_SPEC.get("lotSz") or 1e-6
    if px <= 0:
        return 0.0
    add = _step_round(float(lv["usd_book"]) / px + 1e-12, lot, ROUND_FLOOR)
    if add > 0:
        drained = add * px
        before = float(lv["usd_book"])
        lv["usd_book"] = round(before - drained, 10)
        lv["grown_qty"] = round(float(lv["grown_qty"]) + add, 12)
        ib = float(lv.get("inj_book") or 0.0)             # 💉 حصة رأس المال المحقون تنتقل بالتناسب
        if ib > 0 and before > 0:
            moved = min(ib, ib * (drained / before))
            lv["inj_book"] = round(ib - moved, 10)
            lv["inj_grown"] = round(float(lv.get("inj_grown") or 0.0) + moved, 10)
    s["g"] = float(lv["grown_qty"])
    if lv["usd_book"] < -1e-9 or lv["usd_book"] >= 2.0 * lot * px + 1e-6:      # خلل ⇒ يوقف التراكم (مثل الشبكي)
        b["on"] = False
        log_trade_history(SYMBOL, f"🛑 [إعادة الاستثمار] خلل بحصّالة الخانة {key} ({_n(lv['usd_book'])}$) — أوقفت التراكم")
    return add


def _ri_pot(state, b):
    """💠 المتراكم الحالي (مثل pot_of بالشبكي): دولار = الحصّالات + نمو خانات الشراء بسعرها · عملة = نمو خانات البيع (ماسكة عملة)"""
    usd, coin = 0.0, 0.0
    S = state.get("slots") or {}
    for k, lv in b["levels"].items():
        usd += float(lv.get("usd_book") or 0)
        gq = float(lv.get("grown_qty") or 0)
        if gq > 0:
            if (S.get(k) or {}).get("side") == "sell":
                coin += gq
            else:
                usd += gq * float(lv.get("px") or 0)
    return {"usd": round(usd, 10), "coin": round(coin, 12)}


def _send(state, key, s, cp):
'''),
    # the sale: the split, the pot, the lines
    ('''        state["total_profit"] = round(float(state.get("total_profit") or 0) + profit, 10)
        cb = round(cost / sold, 10) if sold > 0 else s["bp"]
        state["last_trade"] = {"buy": round(float(s.get("cost") or 0) or float(s["bp"]), 10), "sell": round(gross / sold, 10),
                               "qty": round(sold, 10), "profit": round(profit, 6), "ts": time.time(),
                               "n": int((state.get("last_trade") or {}).get("n") or 0) + 1, "slot": key}
        s.update(side="buy", sq=0.0, spent=0.0, cost=0.0, bq=0.0, acc=0.0, accv=0.0, accf=0.0,
                 cyc=int(s.get("cyc") or 0) + 1, n=int(s.get("n") or 0) + 1)
        s.pop("w", None); s.pop("wn", None)
        sgn = "+" if profit >= 0 else "-"
        lines.append(f"🔴 [بيع فوري] السعر: {_n(gross / sold)} | الكمية: {_n(sold)} | الربح: {sgn}{_n(abs(profit))}$"
                     f" -> تم تجهيز شراء بسعر: {_px_str(_px_round(s['bp']))} · 🪜 المستوى {s['j']} · الجزء {s['k']}/{N} (كلفة {_n(cb)})")
''',
     '''        rb = _ri(state)
        pc = _ri_pct(rb) if rb is not None and rb.get("on") else 0.0
        credit = round(profit * pc, 10) if profit > 0 else 0.0           # 💠 حصة الخانة · الباقي ربح عادي
        normal = round(profit - credit, 10)
        state["total_profit"] = round(float(state.get("total_profit") or 0) + normal, 10)
        cb = round(cost / sold, 10) if sold > 0 else s["bp"]
        n_sale = int(s.get("n") or 0) + 1
        state["last_trade"] = {"buy": round(float(s.get("cost") or 0) or float(s["bp"]), 10), "sell": round(gross / sold, 10),
                               "qty": round(sold, 10), "profit": round(credit if credit > 0 else profit, 6), "ts": time.time(),
                               "n": int((state.get("last_trade") or {}).get("n") or 0) + 1, "slot": key}
        if credit > 0:
            state["last_trade"].update(internal=True, split_pct=round(pc * 100, 2), split_normal=round(normal, 6))
        s.update(side="buy", sq=0.0, spent=0.0, cost=0.0, bq=0.0, acc=0.0, accv=0.0, accf=0.0,
                 cyc=int(s.get("cyc") or 0) + 1, n=n_sale)
        s.pop("w", None); s.pop("wn", None)
        if credit <= 0 or normal > 1e-12:                 # (حصة عادية صفر ⇒ بلا سطر بيع — مثل الشبكي)
            sgn = "+" if normal >= 0 else "-"
            lines.append(f"🔴 [بيع فوري] السعر: {_n(gross / sold)} | الكمية: {_n(sold)} | الربح: {sgn}{_n(abs(normal))}$"
                         f" -> تم تجهيز شراء بسعر: {_px_str(_px_round(s['bp']))} · 🪜 المستوى {s['j']} · الجزء {s['k']}/{N} (كلفة {_n(cb)})"
                         f" · البيعة {n_sale}")
        if credit > 0:
            lv = _ri_lv(rb, key, s)
            lv["usd_book"] = round(float(lv["usd_book"]) + credit, 10)
            lv["cycles"] = int(lv.get("cycles") or 0) + 1
            rb["cycles"] = int(rb.get("cycles") or 0) + 1
            rb["credited"] = round(float(rb.get("credited") or 0) + credit, 10)
            _ri_convert(state, rb, key, s)
            pot = _ri_pot(state, rb)
            state["last_trade"].update(pot_usd=round(pot["usd"], 6), pot_coin=round(pot["coin"], 10), cycles=rb["cycles"])
            lines.append(f"💠 [ربح داخلي] السعر: {_n(gross / sold)} | الربح: +{_n(credit)}$ "
                         + (f"({pc * 100:.0f}% من {_n(profit)}$) " if pc < 0.9999 else "")
                         + f"· معاد استثمارها | المتراكم: {_n(pot['usd'])}$"
                         + (f" · {_n(pot['coin'])} عملة" if pot["coin"] > 0 else "")
                         + f" · 🪜 المستوى {s['j']} · الجزء {s['k']}/{N} · البيعة {n_sale}")
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
