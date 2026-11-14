# ➕🎚️ patch 65 (engines · ➕ plus and 🎚️ range — the same grid code) — the owner (14-11, a screenshot of «📦 SOL [استئناف الشراء] تنفيذ 2
#   مستويات مخزنة بأمر مجمع واحد عند السعر 75.6» at 05:30 · 05:40 · 05:50): «بوت البلس يسوي تنبيهات … افحص البوت البلس كليا» and
#   «عند نزول السعر ونفاذ الدولار يضل البوتات تصرخ تريد دولار». Reproduced in the trial sandbox (devtests/t_plus_cash.py):
#   ① the resume line was written BEFORE the dollar check: «تنفيذ 11 مستويات …» every 10 minutes while the dollars covered no level
#      and no order went out ⇒ now execute_catchup_batch writes it after _cu_afford, with the count actually bought (and «من N» when
#      the dollars cover only part) · the price rounded (it printed 74.02282658541093)
#   ② «💵 … ما يكفي ولا درجة» came back every 10 minutes when the count flipped 11 ⇄ 12 with the price ⇒ once per outage (+ one reminder
#      every 6 hours)
#   ③ a limit buy refused for dollars (51008 · 51119 · 51131) was sent again every cycle (a line every minute) ⇒ the new buys rest
#      1 ⇒ 2 ⇒ 4 ⇒ 8 ⇒ 10 minutes, a line at the 1st refusal, then every 36th (~6 hours, like ②) · a sell that fills ends the rest at once
#   The sacred ♾️ engine (main.py) has the same three spots — not touched here (rule: only with the owner's yes).
#   python3 devtests/step/patches/p65_grid_cash.py devtests/step/eng/grid_plus.py devtests/step/eng/grid_range.py
import sys

R = [
    ('''        if ioc_levels and _cu_ready(state, "buy"):
            log_trade_history(symbol, f"📦 [استئناف الشراء] تنفيذ {len(ioc_levels)} مستويات مخزنة بأمر مجمع واحد عند السعر {cp}")
            if execute_catchup_batch(symbol, 'buy', ioc_levels, cp, grid_perc, state):''',
     '''        if ioc_levels and _cu_ready(state, "buy"):
            # 💵 v3.36.44: السطر ينكتب بعد فحص الدولار (داخل الأمر المجمّع) بعدد الدرجات اللي تنشرى فعلاً — كان ينكتب قبله:
            #    «تنفيذ N» كل 10 دقايق والدولار ما يغطي ولا درجة ⇒ ولا أمر
            if execute_catchup_batch(symbol, 'buy', ioc_levels, cp, grid_perc, state, note="📦 [استئناف الشراء]"):'''),
    ('''            log_trade_history(symbol, f"📦 [استئناف البيع] تنفيذ {len(ioc_levels)} مستويات مخزنة بأمر مجمع واحد عند السعر {cp}")''',
     '''            log_trade_history(symbol, f"📦 [استئناف البيع] تنفيذ {len(ioc_levels)} مستويات مخزنة بأمر مجمع واحد عند السعر {round(float(cp), 6)}")'''),
    ('''def execute_catchup_batch(symbol, side, level_qtys, cp, grid_perc, state):''',
     '''def execute_catchup_batch(symbol, side, level_qtys, cp, grid_perc, state, note=None):'''),
    ('''    if side == 'buy':
        level_qtys = _cu_afford(symbol, level_qtys, cp, state)   # 💵 v3.21.8 (ب٢٤): بقدر الدولار الحر — أمر واحد
        if not level_qtys:
            return True                                    # ولا درجة يغطيها الدولار ⇒ ولا أمر (التهدئة انحفظت)''',
     '''    if side == 'buy':
        _n0 = len(level_qtys)
        level_qtys = _cu_afford(symbol, level_qtys, cp, state)   # 💵 v3.21.8 (ب٢٤): بقدر الدولار الحر — أمر واحد
        if not level_qtys:
            return True                                    # ولا درجة يغطيها الدولار ⇒ ولا أمر (التهدئة انحفظت)
        if note:                                           # 💵 v3.36.44: بعد فحص الدولار — العدد اللي ينرسل فعلاً
            log_trade_history(symbol, f"{note} تنفيذ {len(level_qtys)} مستويات مخزنة بأمر مجمع واحد عند السعر {round(float(cp), 6)}"
                                      + (f" (من {_n0} — بقدر الدولار الحر)" if len(level_qtys) < _n0 else ""))'''),
    ('''    if _lg.get("k") != k or _lg.get("n") != n or time.time() - float(_lg.get("t") or 0) > 1800:''',
     '''    if (_lg.get("k") != k or (k and _lg.get("n") != n)                   # 💵 v3.36.44: ولا درجة ⇒ سطر بأول مرة (+ تذكير كل 6 ساعات) —
            or time.time() - float(_lg.get("t") or 0) > (21600 if k == 0 else 1800)):   # كان يرجع كل 10 دقايق لما العدد يتقلّب 11 ⇄ 12'''),
    ('''        _owp = not _ad and not _fixd
        if _owp and not _ow_put(cl_ord_id, "buy",''',
     '''        if not _ad and not _fixd and time.time() < float((state.get("nocash") or {}).get("until") or 0):
            return False                          # 💵 v3.36.44: الدولار ما كفى قبل شوية ⇒ ما نرسل لحد موعد التهدئة (أو أول بيع يتنفّذ)
        _owp = not _ad and not _fixd
        if _owp and not _ow_put(cl_ord_id, "buy",'''),
    ('''        # 📢 كسر الصمت: تسجيل سبب رفض المنصة (رصيد غير كافٍ، كمية/سعر غير صالح...) بدل التجاهل
        try: s_msg = (order.get('data') or [{}])[0].get('sMsg') or order.get('msg', '')
        except Exception: s_msg = ''
        if time.time() - state.get("last_order_fail_log", 0) > 60:
            state["last_order_fail_log"] = time.time()
            log_trade_history(symbol, f"⚠️ [رفض أمر شراء] كمية ({qty_rounded}) بسعر ({safe_target}): {s_msg or 'سبب غير معروف'}")
        return False''',
     '''        # 📢 كسر الصمت: تسجيل سبب رفض المنصة (رصيد غير كافٍ، كمية/سعر غير صالح...) بدل التجاهل
        try: s_msg = (order.get('data') or [{}])[0].get('sMsg') or order.get('msg', '')
        except Exception: s_msg = ''
        try: s_code = str((order.get('data') or [{}])[0].get('sCode') or order.get('code') or '')
        except Exception: s_code = ''
        if s_code in ("51008", "51119", "51131"):
            # 💵 v3.36.44: الدولار ما يكفي ⇒ ما نلح على المنصة كل دورة: الشراء الجديد يهدأ 1 ⇐ 2 ⇐ 4 ⇐ 8 ⇐ 10 دقايق
            #    (أول بيع يتنفّذ يرجّعه فوراً) · سطر بأول رفض وبعدها كل 36 رفض (~6 ساعات — مثل تذكير الأمر المجمّع)
            _w = state.setdefault("nocash", {"n": 0, "until": 0})
            _w["n"] = int(_w.get("n") or 0) + 1
            _wt = int(min(600, 60 * 2 ** (min(_w["n"], 5) - 1)))
            _w["until"] = time.time() + _wt
            if _w["n"] == 1 or _w["n"] % 36 == 0:
                log_trade_history(symbol, f"💵 [رفض أمر شراء] الدولار الحر ما يكفي أمر ({qty_rounded} بسعر {safe_target}) — "
                                          f"ما نلح على المنصة: نعيد بعد {_wt} ثانية (أو أول ما يتنفّذ بيع)")
            return False
        if time.time() - state.get("last_order_fail_log", 0) > 60:
            state["last_order_fail_log"] = time.time()
            log_trade_history(symbol, f"⚠️ [رفض أمر شراء] كمية ({qty_rounded}) بسعر ({safe_target}): {s_msg or 'سبب غير معروف'}")
        return False'''),
    ('''def process_sell_fill(ord_id, exec_price, real_qty, state):
    info = state["limit_sells"].get(ord_id)
    if not info: return''',
     '''def process_sell_fill(ord_id, exec_price, real_qty, state):
    info = state["limit_sells"].get(ord_id)
    if not info: return
    state.pop("nocash", None)             # 💵 v3.36.44: بيع تنفّذ = دولار وصل ⇒ الشراء يرجع يحاول فوراً'''),
]

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = open(p, encoding="utf-8").read()
        for i, (a, b) in enumerate(R):
            if s.count(a) != 1:
                print(f"❌ {p} · replacement {i}: found {s.count(a)} times — nothing written: {a[:80]!r}"); sys.exit(1)
            s = s.replace(a, b)
        compile(s, p, "exec")
        open(p, "w", encoding="utf-8").write(s)
        print(f"✅ {len(R)} replacements · compiles · {p}")
