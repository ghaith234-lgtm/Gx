# ⚡ patch 91 (dashboard v3.36.56 · DCA+) — a NEW engine `dca_plus.py`, made from the sell DCA `dca.py` (which stays byte for byte).
#   The owner (15-11): «اختر ج١ فقط … لا اتعدل او اتضيف واحد اخر وانسميه dca+ بس لازم انجربه … واريد انا اتحكم فيه ويظهر لي
#   بالجدول والمخطط وانا اختار الخروج». ج1 = the layered exit: a filled safety order exits ALONE when the price comes back a little
#   below the price it was sold at (lx_pct, default 0.5%) — a small profit, the exposure gone, instead of waiting for the whole cycle's
#   target (4.37% away in the example). The base and the safety orders before `lx_from` keep the normal target.
#   · one IOC buy per layer, capped at that layer's break-even (never a loss) — exactly once (the send journal · key «X<fid>») ·
#     recovery after a restart (pending_lx) · a partial fill exits that part (the rest stays, same price)
#   · the layer re-opens (lx_reopen): its planned level goes back to the store ⇒ sold again if the price returns (grid-like)
#   · every exit is its own entry in cycles_log (id · profit in coin · px) ⇒ the dashboard's books count it like a closed cycle
#   · control from the card (state fields): lx_on · lx_pct · lx_from · lx_reopen · lx_off (layers you switched off) ·
#     lx_now (exit this layer now — your decision: no cap)
#   python3 devtests/step/patches/p91_dca_plus_engine.py devtests/step/eng/dca.py devtests/step/eng/dca_plus.py
import sys

LX = r'''

# ═══════════ ⚡ DCA+ (v3.36.56 · ج1 — المالك 15-11): الخروج بالطبقات ═══════════
#   كل أمر أمان منفّذ (من lx_from) يطلع وحده لما السعر يرجع تحت سعر بيعه بـlx_pct — يشتري كميته بدولاره الصافي بأمر حد فوري سقفه
#   نقطة التعادل لهالطبقة (ولا خسارة) · ربحه بالعملة ينسجل دورة بسجل الدورات · الطبقة ترجع للمخزون (lx_reopen) وتنباع إذا رجع السعر
LX_MIN = 0.3            # % أقل ارتداد: عمولة البيع + الشراء ≈ 0.18–0.2% + هامش
LX_MAX = 10.0


def _lx_cfg(cfg, state):
    """إعدادات الخروج بالطبقات: من الكرت (ملف الحالة) أولاً ثم من الإعدادات"""
    def pick(k, d):
        v = state.get(k)
        return cfg.get(k, d) if v is None else v
    try:
        pct = min(LX_MAX, max(LX_MIN, float(pick("lx_pct", 0.5))))
    except Exception:
        pct = 0.5
    try:
        frm = max(1, int(float(pick("lx_from", 1))))
    except Exception:
        frm = 1
    off = set()
    for x in (state.get("lx_off") or []):
        try:
            off.add(int(x))
        except Exception:
            pass
    return bool(pick("lx_on", True)), pct / 100.0, frm, bool(pick("lx_reopen", True)), off


def _lx_ns(f):
    """مستويات الخطة اللي بهالتنفيذ (أمر أمان واحد · أو أمر مجمّع بعدة مستويات)"""
    try:
        return [int(x) for x in (f.get("ns") or [])] if int(f.get("n", 0)) < 0 else [int(f.get("n", 0))]
    except Exception:
        return []


def _lx_ok(f, frm, off):
    ns = _lx_ns(f)
    return bool(ns) and min(ns) >= frm and not (set(ns) & off)


def _lx_px(f, pct):
    return float(f["price"]) * (1 - pct)


def _lx_fids(state):
    for f in state.get("filled") or []:
        if not f.get("fid"):
            state["_fid"] = int(state.get("_fid", 0)) + 1
            f["fid"] = state["_fid"]


def _lx_reopen(state, ns):
    """الطبقة طلعت ⇒ مستوياتها ترجع للمخزون بخطتها (إذا مو موجودة بالمخزون ولا على المنصة ولا بتنفيذ باقي)"""
    if state.get("phase") != "selling":
        return []
    plan = {int(l["n"]): l for l in (state.get("planned_levels") or []) if isinstance(l, dict)}
    busy = {int(l.get("n", -9)) for l in state.get("pending_levels") or []}
    busy |= {int(v.get("n", -9)) for v in (state.get("active_sells") or {}).values()}
    for f in state.get("filled") or []:
        busy |= set(_lx_ns(f))
    back = []
    for n in ns:
        if n in plan and n not in busy:
            _pend_put(state, plan[n]["price"], plan[n]["qty"], n)
            back.append(n)
    _pend_sort(state)
    return back


def _lx_n_txt(n):
    """عدد الطبقات بالفصحى"""
    n = int(n)
    return "طبقة واحدة" if n == 1 else "طبقتان" if n == 2 else f"{n} طبقات" if 3 <= n <= 10 else f"{n} طبقة"


def lx_settle(trade_api, symbol, cfg, state):
    """يثبّت نتيجة أمر خروج طبقة (بعد الإرسال أو بالتعافي) — True لو انحسم"""
    p = state.get("pending_lx")
    if not p:
        return True
    chk = confirm_order(trade_api, p["oid"], symbol)
    if chk is None:
        return False
    state.pop("pending_lx", None)
    fid = int(p.get("fid") or 0)
    manual = bool(p.get("manual"))
    if manual:
        state["lx_now"] = [x for x in (state.get("lx_now") or []) if str(x) != str(fid)]
    f = next((x for x in state.get("filled") or [] if int(x.get("fid") or 0) == fid), None)
    gq, apx = float(chk.get("fillSz") or 0), float(chk.get("avgPx") or 0)
    if f is None or gq <= 0 or apx <= 0:
        if f is not None:
            f["lx_try"] = int(f.get("lx_try", 0)) + 1
        save_json(STATE_FILE, state)
        return True
    base = _ccy(symbol)[0]
    u, q = _f_net(f), float(f["qty"])
    spent = gq * apx
    got = _fee_net(chk, gq, base)
    frac = min(1.0, spent / u) if u > 0 else 1.0
    left_u = u - spent
    ns = _lx_ns(f)
    if frac >= 0.999 or fmt_qty(left_u / apx) <= 0:
        q_out = q
        state["filled"] = [x for x in state["filled"] if x is not f]
        state["dust_usdt"] = round(float(state.get("dust_usdt", 0)) + max(0.0, left_u), 8)
        back = _lx_reopen(state, ns) if (_lx_cfg(cfg, state)[3] and not manual) else []
        whole = True
    else:
        q_out = q * frac
        f["qty"] = round(q - q_out, 10)
        f["net"] = round(left_u, 10)
        back, whole = [], False
    profit = got - q_out
    ts = time.time()
    state["total_coin_profit"] = state.get("total_coin_profit", 0) + profit
    state["lx_count"] = int(state.get("lx_count", 0)) + 1
    state["lx_profit"] = round(float(state.get("lx_profit", 0)) + profit, 10)
    state["lx_cycle_n"] = int(state.get("lx_cycle_n", 0)) + 1
    state["lx_cycle_p"] = round(float(state.get("lx_cycle_p", 0)) + profit, 10)
    lg = list(state.get("cycles_log") or [])
    lg.append({"id": f"{BOT_ID}-x{fid}-{int(ts)}-{state['lx_count']}", "n": int(state.get("cycles_done", 0)), "ts": ts,
               "profit": round(profit, 10), "px": apx, "out": round(q_out, 8), "in": round(got, 8), "manual": manual, "lx": ns})
    state["cycles_log"] = lg[-600:]
    xl = list(state.get("lx_log") or [])
    xl.append({"ts": ts, "ns": ns, "sold": float(f["price"]), "px": apx, "out": round(q_out, 8), "in": round(got, 8),
               "profit": round(profit, 10), "manual": manual, "whole": whole, "back": back})
    state["lx_log"] = xl[-100:]
    avg, target = _recalc(state, cfg)
    _lbl = ("أمان " + str(ns[0])) if len(ns) == 1 else f"أمان {min(ns)}-{max(ns)}"
    log_history(symbol, f"⚡ {'خروج يدوي' if manual else 'خروج الطبقة'} {_lbl} — شراء {round(got, 4)} {base} بسعر {fmt_price(apx)} "
                        f"(بيعت بسعر {fmt_price(f['price'])}){'' if whole else ' (جزء منها)'} | الربح {profit:+.6f} {base}"
                        + (" | عادت إلى المخزون" if back else "")
                        + (f" | المتوسط {fmt_price(avg)} · الهدف {fmt_price(target)}" if state.get("filled") else ""))
    save_json(STATE_FILE, state)
    return True


def lx_run(trade_api, market_api, symbol, cfg, state, cp):
    """⚡ يخرج الطبقات اللي وصلها السعر (الأعلى أولاً) + طلبات «أخرجها الآن» من الكرت — False لو أمر ما انحسم بعد"""
    _lx_fids(state)
    on, pct, frm, reopen, off = _lx_cfg(cfg, state)
    want = []
    for x in (state.get("lx_now") or []):
        try:
            want.append(int(x))
        except Exception:
            pass
    have = {int(f.get("fid") or 0) for f in state.get("filled") or []}
    if want and any(w not in have for w in want):
        state["lx_now"] = [w for w in want if w in have]
        want = state["lx_now"]
    if not want and not on:
        return True
    bid, ask = get_book(symbol, market_api, cp)
    if ask <= 0:
        return True
    todo = [(f, True) for f in state.get("filled") or [] if int(f.get("fid") or 0) in want]
    if on:
        todo += [(f, False) for f in sorted(state.get("filled") or [], key=lambda x: -float(x["price"]))
                 if int(f.get("fid") or 0) not in want and _lx_ok(f, frm, off) and ask <= _lx_px(f, pct) and not f.get("lx_small")]
    for f, manual in todo:
        u, q = _f_net(f), float(f["qty"])
        if u <= 0 or q <= 0:
            continue
        if manual:
            lim = ask * (1 + CLOSE_SLIP)
        else:
            cap = u * (1 - FEE_FALLBACK) / q                    # نقطة التعادل لهالطبقة (ولا خسارة)
            lim = min(ask * (1 + (CLOSE_SLIP if f.get("lx_try") else 0.0)), cap)
            if lim < ask:
                continue
        lim = fmt_price(lim)
        if lim <= 0:
            continue
        lot = INSTRUMENT_SPEC.get("lotSz")
        qb = (math.floor((u / lim) / lot + 1e-9) * lot) if lot else u / lim    # لتحت: ولا سنت أكثر من دولار هالطبقة
        if fmt_qty(qb) <= 0:
            f["lx_small"] = 1                                     # أصغر من أقل كمية بالمنصة ⇒ تبقى لهدف الدورة
            continue
        fid = int(f.get("fid") or 0)
        oid = place_ioc(trade_api, symbol, "buy", lim, qb, f"X{fid}", {"fid": fid, "manual": manual})
        if not oid:
            return True
        state["pending_lx"] = {"oid": oid, "fid": fid, "manual": manual}
        save_json(STATE_FILE, state)                          # 🔒 قبل التأكيد — لو انطفى، التعافي يعرف الأمر وما يشتري مرتين
        if not lx_settle(trade_api, symbol, cfg, state):
            return False
        bid, ask = get_book(symbol, market_api, cp)
    return True


def run_cycle(trade_api, market_api, cfg, state):'''

R = [
    ('''  The Holy DCA Bot — محرك التداول البيعي (نمط 3Commas معكوس)''',
     '''  The Holy DCA+ Bot — البيعي + ⚡ الخروج بالطبقات (v3.36.56 · نسخة من dca.py — الأصل ما تغيّر)'''),
    ('''_CTL_KEYS = ("paused", "self_destruct", "manual_buy_now", "trail_on", "trail_pct", "status", "stop_after_cycle")''',
     '''_CTL_KEYS = ("paused", "self_destruct", "manual_buy_now", "trail_on", "trail_pct", "status", "stop_after_cycle",
             "lx_on", "lx_pct", "lx_from", "lx_reopen", "lx_off", "lx_now")         # ⚡ DCA+: الخروج بالطبقات من الكرت'''),
    # every fill gets a stable id (the card's «exit this layer now» names it)
    ('''    e = {"price": px, "qty": q, "n": n, "net": round(_fee_net(chk, px * q, _ccy(symbol)[1]), 10)}
    if extra:
        e.update(extra)
    state.setdefault("filled", []).append(e)''',
     '''    e = {"price": px, "qty": q, "n": n, "net": round(_fee_net(chk, px * q, _ccy(symbol)[1]), 10)}
    if extra:
        e.update(extra)
    state["_fid"] = int(state.get("_fid", 0)) + 1          # ⚡ DCA+: رقم ثابت لكل تنفيذ (الكرت يسمّي به الطبقة)
    e["fid"] = state["_fid"]
    state.setdefault("filled", []).append(e)'''),
    # a lost reply of a layer exit ⇒ found by its id before anything else
    ('''    for key in [k for k in list(_xs()) if k.startswith("L") or k == "grp"]:''',
     '''    for key in [k for k in list(_xs()) if k.startswith("L") or k == "grp" or k.startswith("X")]:'''),
    ('''        if key == "grp":
            lv = list((rec or {}).get("levels") or [])''',
     '''        if key.startswith("X"):                            # ⚡ DCA+: أمر خروج طبقة ضاع رده ⇒ ينحسم بمعرّفه
            state["pending_lx"] = {"oid": oid, "fid": int((rec or {}).get("fid") or key[1:] or 0), "manual": bool((rec or {}).get("manual"))}
        elif key == "grp":
            lv = list((rec or {}).get("levels") or [])'''),
    ('''    state["cycles_log"] = lg[-300:]''', '''    state["cycles_log"] = lg[-600:]'''),
    # the layer exits of this cycle in the closing line
    ('''    state["last_cycle"] = {"sold": round(sold, 4), "bought": round(got, 4), "profit": round(profit, 6),
                           "ts": time.time(), "net": True, "dust": round(dust, 6), "manual": bool(cl.get("manual"))}''',
     '''    state["last_cycle"] = {"sold": round(sold, 4), "bought": round(got, 4), "profit": round(profit, 6),
                           "ts": time.time(), "net": True, "dust": round(dust, 6), "manual": bool(cl.get("manual")),
                           "lx_n": int(state.get("lx_cycle_n", 0)), "lx_p": round(float(state.get("lx_cycle_p", 0)), 10)}'''),
    ('''                        f" | الإجمالي {round(state['total_coin_profit'], 4)}" + (f" · باقي {dust:.4f}$ غبار بالمحفظة" if dust >= 0.0001 else ""))''',
     '''                        f" | الإجمالي {round(state['total_coin_profit'], 4)}" + (f" · باقي {dust:.4f}$ غبار بالمحفظة" if dust >= 0.0001 else "")
                        + (f" · ⚡ خرجت {_lx_n_txt(state.get('lx_cycle_n', 0))} في هذه الدورة بربح {float(state.get('lx_cycle_p', 0)):+.6f} {base}"
                           if state.get("lx_cycle_n") else ""))'''),
    ('''def run_cycle(trade_api, market_api, cfg, state):''', LX.lstrip("\n")),
    # a new cycle: this cycle's layer counters start again
    ('''            for k in ("close", "pending_grp", "trail_s", "trail_t", "_manual_close"):
                state.pop(k, None)''',
     '''            for k in ("close", "pending_grp", "trail_s", "trail_t", "_manual_close", "pending_lx", "lx_cycle_n", "lx_cycle_p", "lx_now"):
                state.pop(k, None)'''),
    # selling: settle a layer exit first · then the layers the price reached (before the cycle's target)
    ('''            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue

            # افحص الأوامر الحقيقية على المنصة (مزامنة)''',
     '''            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue
            if state.get("pending_lx") and not lx_settle(trade_api, symbol, cfg, state):   # ⚡ DCA+
                time.sleep(4)
                continue

            # افحص الأوامر الحقيقية على المنصة (مزامنة)'''),
    ('''            # 🎯 الهدف (لازم يكون باع شيئاً)
            tgt = state.get("target_price", 0)''',
     '''            # ⚡ DCA+: الطبقات اللي رجع لها السعر تطلع وحدها (قبل هدف الدورة)
            if not lx_run(trade_api, market_api, symbol, cfg, state, cp):
                time.sleep(4)
                continue

            # 🎯 الهدف (لازم يكون باع شيئاً)
            tgt = state.get("target_price", 0)'''),
    # buying (closing the cycle): no layer exit left half-known
    ('''        elif phase == "buying":
            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue''',
     '''        elif phase == "buying":
            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue
            if any(k.startswith("X") for k in _xs()) and not _xs_settle(trade_api, symbol, state):   # ⚡ DCA+
                time.sleep(4)
                continue
            if state.get("pending_lx") and not lx_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue'''),
    ('''    print("  The Holy DCA Bot — محرك التداول البيعي")''', '''    print("  The Holy DCA+ Bot — البيعي + الخروج بالطبقات")'''),
    ('''    log_history(SYMBOL, "⚡ بوت DCA انطلق")''', '''    log_history(SYMBOL, "⚡ بوت DCA+ انطلق (الخروج بالطبقات)")'''),
]

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    s = open(src, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, out, "exec")
    open(out, "w", encoding="utf-8").write(s)
    print(f"✅ {len(R)} replacements · {out} ({len(s.splitlines())} lines) from {src} (unchanged)")
