# ⚡ patch 94 (dashboard v3.36.57 · the NEW DCA+ — replaces the layered exit of patches 91–93): a free ladder.
#   The owner (15-11), after the example: «سويه بدل وسميه هو بلس» · «انا اتحكم بالجدول البياني في وضع الاوردرات» · «اقدر اضيفه يدوي
#   لكل اوردر واقدر اضيف عبر الرسم البياني». His aim: «هدفي ازيد العملات ما اريد ابيع عملات باسعار واطية او اتضل معلقة».
#   The engine `dca_plus.py` is made from the sell DCA `dca.py` (which stays byte for byte). What changes:
#   · the ladder comes from the owner's own rows `plus_rows` = [{d: distance % from the order before, q: its size, x: its exit %}, …]
#     (row 0 = the base order, d = 0) — every order its own distance, size and exit
#   · the cycle's target = the weighted average × (1 − x of the DEEPEST order filled) — the average is the normal one and the whole
#     position is bought back at once, exactly as the sell DCA (so small early orders keep a good profit and the late big ones can
#     take a small one and get out sooner)
#   · edits from the table or the chart while it runs (`plus_edit` {seq, rows}): orders not filled yet move to their new price/size
#     (the live ones are cancelled — whatever filled before the cancel is booked — and placed again), filled orders stay as they are
#     (their exit % may change), the target follows at once. During the close (buying) or between cycles the rows wait for the next cycle.
#   · no rows (an older DCA+ config) ⇒ the classic fields build the ladder (the sell DCA's own formula)
#   python3 devtests/step/patches/p94_dca_plus_ladder.py devtests/step/eng/dca.py devtests/step/eng/dca_plus.py
import sys

ROWS = r'''

# ═══════════ ⚡ DCA+ (v3.36.57): السلّم الحر — كل أمر بمسافته وكميته ونسبة خروجه (الجدول أو الرسم البياني) ═══════════
PLUS_MAX_ROWS = 101          # الأساس + 100 أمر أمان (نفس حد اللوحة)
PLUS_MIN_X = 0.20            # % أقل نسبة خروج يقبلها المحرك (عمولة البيع + الشراء)


def plus_rows_ok(rows):
    """الصفوف سليمة؟ ⇒ (صفوف نظيفة، "") أو (None، السبب)"""
    if not isinstance(rows, list) or not (1 <= len(rows) <= PLUS_MAX_ROWS):
        return None, "عدد الأوامر غير صالح"
    out = []
    for i, r in enumerate(rows):
        try:
            d, q, x = float((r or {}).get("d") or 0), float((r or {}).get("q") or 0), float((r or {}).get("x") or 0)
        except Exception:
            return None, f"أرقام الصف {i + 1} غير صالحة"
        if not all(v == v and abs(v) != float("inf") for v in (d, q, x)):
            return None, f"أرقام الصف {i + 1} غير صالحة"
        if q <= 0 or x <= 0 or x > 50 or (i > 0 and not (0 < d <= 50)):
            return None, f"الصف {i + 1}: الكمية > 0 · المسافة بين 0 و50% · نسبة الخروج بين 0 و50%"
        out.append({"d": 0.0 if i == 0 else round(d, 6), "q": q, "x": round(x, 6)})
    return out, ""


def plus_levels(rows, base_price):
    """مستويات السلّم من الصفوف: كل أمر = الذي قبله × (1 + مسافته) — البيعي: فوق"""
    levels, p = [], float(base_price)
    for i, r in enumerate(rows):
        if i:
            p = p * (1 + float(r["d"]) / 100.0)
        levels.append({"n": i, "price": p, "qty": float(r["q"])})
    return levels


def _deepest_n(filled):
    n = 0
    for f in filled or []:
        try:
            k = int(f.get("n", 0))
            n = max([n] + ([int(x) for x in (f.get("ns") or [])] if k < 0 else [k]))
        except Exception:
            pass
    return n


def _locked_ns(state):
    """أوامر هذه الدورة اللي نفّذت (كلها أو جزء منها) — ثابتة لا تتحرك"""
    out = set()
    for f in state.get("filled") or []:
        try:
            k = int(f.get("n", 0))
            out |= set(int(x) for x in (f.get("ns") or [])) if k < 0 else {k}
        except Exception:
            pass
    return out


def plus_tp(cfg, filled):
    """نسبة خروج أعمق أمر منفّذ (%) — بلا صفوف ⇒ هدف الإعدادات"""
    rows = cfg.get("plus_rows")
    if isinstance(rows, list) and rows:
        try:
            return float(rows[min(_deepest_n(filled), len(rows) - 1)]["x"])
        except Exception:
            pass
    return float(cfg.get("take_profit_pct") or 0)


def plus_apply_rows(cfg, rows):
    cfg["plus_rows"] = rows
    cfg["base_order_qty"] = rows[0]["q"]
    cfg["max_safety_orders"] = len(rows) - 1
    cfg["take_profit_pct"] = rows[0]["x"]


def plus_edit_apply(trade_api, symbol, cfg, state):
    """✏️ تعديل من الجدول/الرسم والبوت شغّال — True لو انطبق (أو ما في شي) · False لو ننتظر (شبكة)"""
    pe = state.get("plus_edit")
    if not isinstance(pe, dict) or pe.get("seq") is None or str(pe.get("seq")) == str(state.get("plus_seq")):
        return True
    rows, why = plus_rows_ok(pe.get("rows"))
    if rows is None:
        state["plus_seq"] = pe.get("seq")
        state["plus_edit_err"] = why
        log_history(symbol, f"⚠️ تعديل الأوامر لم يُطبَّق: {why}")
        save_json(STATE_FILE, state)
        return True
    phase = state.get("phase")
    if phase != "selling":
        plus_apply_rows(cfg, rows)                        # بين الدورات أو وقت الإغلاق ⇒ الصفوف للدورة الجاية
        state["plus_seq"] = pe.get("seq")
        state.pop("plus_edit_err", None)
        log_history(symbol, f"✏️ حُفظت الأوامر الجديدة ({len(rows) - 1} أمر أمان) — تبدأ بها الدورة القادمة")
        save_json(STATE_FILE, state)
        return True
    if state.get("pending_grp"):
        return False                                     # أمر مجمّع ما انحسم بعد ⇒ ننتظره
    if _locked_ns(state) and max(_locked_ns(state)) >= len(rows):
        state["plus_seq"] = pe.get("seq")                # ما نحذف أمراً نفّذ في هذه الدورة
        state["plus_edit_err"] = "لا يمكن حذف أمر نُفّذ في هذه الدورة"
        log_history(symbol, "⚠️ تعديل الأوامر لم يُطبَّق: يحذف أمراً نُفّذ في هذه الدورة")
        save_json(STATE_FILE, state)
        return True
    if state.get("active_sells") and not cancel_ladder(trade_api, symbol, state):
        return False                                     # ما تأكدنا من الإلغاء (شبكة) ⇒ نعيد بالدورة الجاية
    plus_apply_rows(cfg, rows)
    locked = _locked_ns(state)                           # بعد الإلغاء: اللي نفّذ قبله مباشرة صار منفّذاً أيضاً
    old_plan = {int(l["n"]): l for l in (state.get("planned_levels") or []) if isinstance(l, dict)}
    new_lv = plus_levels(rows, float(state.get("base_price") or (old_plan.get(0) or {}).get("price") or 0))
    state["planned_levels"] = ([dict(old_plan[l["n"]]) if l["n"] in locked and l["n"] in old_plan else l for l in new_lv]
                               + [dict(old_plan[k]) for k in sorted(locked) if k >= len(new_lv) and k in old_plan])
    keep = [l for l in (state.get("pending_levels") or []) if int(l.get("n", -1)) in locked]   # بقية أمر نفّذ جزء منه — بسعره
    state["pending_levels"] = keep + [dict(l) for l in new_lv if l["n"] >= 1 and l["n"] not in locked]
    _pend_sort(state)
    avg, target = _recalc(state, cfg)
    state["plus_seq"] = pe.get("seq")
    state.pop("plus_edit_err", None)
    moved = len([l for l in new_lv if l["n"] >= 1 and l["n"] not in locked])
    log_history(symbol, f"✏️ عُدّلت الأوامر من الجدول/الرسم — {moved} أمر بأسعاره الجديدة · المنفّذة ثابتة ({max(0, len(locked) - 1)})"
                        + (f" | المتوسط {fmt_price(avg)} · الهدف {fmt_price(target)}" if state.get("filled") else ""))
    save_json(STATE_FILE, state)
    return True
'''

R = [
    ('''  The Holy DCA Bot — محرك التداول البيعي (نمط 3Commas معكوس)''',
     '''  The Holy DCA+ Bot — البيعي بسلّم حر: كل أمر بمسافته وكميته ونسبة خروجه (v3.36.57 · نسخة من dca.py — الأصل ما تغيّر)'''),
    ('''_CTL_KEYS = ("paused", "self_destruct", "manual_buy_now", "trail_on", "trail_pct", "status", "stop_after_cycle")''',
     '''_CTL_KEYS = ("paused", "self_destruct", "manual_buy_now", "trail_on", "trail_pct", "status", "stop_after_cycle",
             "plus_edit")                                  # ⚡ DCA+: تعديل الأوامر من الجدول/الرسم'''),
    # the ladder from the rows
    ('''def compute_sell_levels(cfg, base_price):
    """يحسب مستويات البيع التدريجي من الإعدادات — بيعي (فوق)"""''',
     '''def compute_sell_levels(cfg, base_price):
    """يحسب مستويات البيع التدريجي من الإعدادات — بيعي (فوق) · ⚡ DCA+: من صفوف المالك (plus_rows) لو موجودة"""
    if isinstance(cfg.get("plus_rows"), list) and cfg.get("plus_rows"):
        return plus_levels(cfg["plus_rows"], base_price)'''),
    # the target: the deepest filled order's exit %
    ('''    tp_raw = float(cfg["take_profit_pct"])''', '''    tp_raw = plus_tp(cfg, filled)                    # ⚡ DCA+: نسبة خروج أعمق أمر منفّذ'''),
    ('''def run_cycle(trade_api, market_api, cfg, state):''', ROWS.lstrip("\n") + '''

def run_cycle(trade_api, market_api, cfg, state):'''),
    # selling: an edit from the table/chart is applied after the lost replies and the grouped order are settled
    ('''            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue

            # افحص الأوامر الحقيقية على المنصة (مزامنة)''',
     '''            if state.get("pending_grp") and not grp_settle(trade_api, symbol, cfg, state):
                time.sleep(4)
                continue
            if not plus_edit_apply(trade_api, symbol, cfg, state):    # ⚡ DCA+: تعديل من الجدول/الرسم
                time.sleep(4)
                continue

            # افحص الأوامر الحقيقية على المنصة (مزامنة)'''),
    # between cycles / waiting / finished: the edit is kept for the next cycle
    ('''        # ═══ المرحلة: تهيئة دورة جديدة ═══
        if phase == "init" and state.get("stop_after_cycle") and not state.get("pending_base_id"):''',
     '''        if phase in ("init", "waiting", "finished") and not state.get("pending_base_id"):
            plus_edit_apply(trade_api, symbol, cfg, state)       # ⚡ DCA+: الصفوف الجديدة للدورة القادمة

        # ═══ المرحلة: تهيئة دورة جديدة ═══
        if phase == "init" and state.get("stop_after_cycle") and not state.get("pending_base_id"):'''),
    ('''    print("  The Holy DCA Bot — محرك التداول البيعي")''', '''    print("  The Holy DCA+ Bot — البيعي بسلّم حر")'''),
    ('''    log_history(SYMBOL, "⚡ بوت DCA انطلق")''', '''    log_history(SYMBOL, "⚡ بوت DCA+ انطلق (سلّم حر: كل أمر بمسافته وكميته ونسبة خروجه)")'''),
    # the rows (and their edits) are read from the config at start
    ('''    cfg = config
    cfg["symbol"] = SYMBOL
''', '''    cfg = config
    cfg["symbol"] = SYMBOL
    if cfg.get("plus_rows"):                                       # ⚡ DCA+: صفوف المالك (من الإعدادات)
        _pr, _pw = plus_rows_ok(cfg.get("plus_rows"))
        if _pr:
            plus_apply_rows(cfg, _pr)
        else:
            cfg.pop("plus_rows", None)
            log_history(SYMBOL, f"⚠️ صفوف الأوامر غير صالحة ({_pw}) — يعمل بإعدادات DCA العادية")
'''),
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
