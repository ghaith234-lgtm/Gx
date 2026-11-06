# 🪜 patch 05 (engine + dashboard · F8) — 💣 while the cancels don't reach OKX: the bot still wrote «destruct_done», logged
#   «أُلغي 14 أمر» and exited ⇒ the dashboard trusted it ⇒ the orders stayed live on OKX with no bot.
#   Engine: after each cancel the bot asks OKX for the order's state · filled meanwhile ⇒ booked (_finish) · still live / unknown
#   ⇒ no «destruct_done», no new orders, retried every loop · a bot that already withdrew never trades again (the watchdog may
#   start it: it exits at once).  Dashboard (🪜 only): neither the bot nor the dashboard could confirm that no order of the
#   bot is left ⇒ the delete is refused (auto-restart off · the bot keeps trying) — never «deleted» with live orders.
#   python3 devtests/step/patches/p05_f8_destruct_confirm.py ENGINE.py Holy_Dashboard.pyw     (both checked before either is written)
import ast, os, sys

ENG = [
    ('''def destruct_now(state, symbol):
    """💣 الحذف النهائي: البوت يلغي أوامره هو فقط (بأرقامها) ثم ينسحب"""
    n = 0
    for key, s in list(_slots(state).items()):
        o = s.get("o") or {}
        if o.get("id"):
            try:
                cancel_order_direct(o["id"], symbol)
                n += 1
            except Exception:
                pass
        elif o.get("cl"):
            d = _check_cl(o["cl"], symbol)
            if d and d.get("ordId"):
                cancel_order_direct(str(d["ordId"]), symbol)
                n += 1
        s["o"] = None
    state["status"] = "💣 انسحب — أوامره ملغاة"
    state["self_destruct"] = False
    state["destruct_done"] = True
    log_trade_history(symbol, f"💣 أُلغي {n} أمر من المنصة قبل الحذف النهائي")
    save_json(STATE_FILE, state)
    time.sleep(0.4)
    sys.exit(0)
''',
     '''def destruct_now(state, symbol):
    """💣 الحذف النهائي: البوت يلغي أوامره هو فقط (بأرقامها) و**يتأكد من المنصة** إن كل أمر انلغى · نفّذ قبل الإلغاء ⇒ ينحسب
    بالدفتر · أمر باقي حي أو حالته مجهولة (الاتصال) ⇒ ما ينسحب: يعيد كل دورة وما يضع أوامر جديدة (F8 — كان ينسحب ويكتب
    «أُلغي» والأوامر باقية حية بالمنصة بلا بوت)."""
    now = time.time()
    if now - float(state.get("destruct_try") or 0) < LOOP_S:
        return False
    state["destruct_try"] = now
    state["self_destruct"] = True
    n, left = int(state.get("destruct_n") or 0), 0
    for key, s in list(_slots(state).items()):
        o = s.get("o") or {}
        if not o:
            continue
        oid = str(o.get("id") or "")
        if not oid:                                       # بالطريق (ردّه ضاع): نسأل بمعرّفنا
            d = _check_cl(o.get("cl"), symbol) if o.get("cl") else {}
            if d is None:
                left += 1
                continue
            if d and d.get("ordId"):
                oid = str(d["ordId"])
                o.update(id=oid, st="live")
            elif now - float(o.get("ts") or 0) >= SEND_WAIT:
                s["o"] = None                             # ما وصل المنصة أبداً
                continue
            else:
                left += 1                                 # ممكن بعده يوصل ⇒ ننتظر المهلة
                continue
        cancel_order_direct(oid, symbol)
        h = check_order_direct(oid, symbol)
        d = h["data"][0] if str(h.get("code")) == "0" and h.get("data") else None
        if d and str(d.get("state") or "") in ("filled", "canceled", "mmp_canceled"):
            _finish(state, key, s, d)                     # (نفّذ كله أو جزء قبل الإلغاء ⇒ بالدفتر)
            s["o"] = None
            n += 1
        elif str(h.get("code")) == "51603":
            s["o"] = None                                 # المنصة ما تعرفه (ملغى بلا تنفيذ من زمان)
            n += 1
        else:
            left += 1
    state["destruct_n"] = n
    if left:
        state["status"] = f"💣 يلغي أوامره — باقي {left}"
        if now - float(state.get("destruct_log") or 0) > 60:
            state["destruct_log"] = now
            log_trade_history(symbol, f"💣 الحذف ينتظر: {left} أمر لم يتأكد إلغاؤه من المنصة — يعيد المحاولة كل {int(LOOP_S)} ثوانٍ "
                                      f"ولا يضع أوامر جديدة")
        save_json(STATE_FILE, state)
        return False
    state["status"] = "💣 انسحب — أوامره ملغاة"
    state["self_destruct"] = False
    state["destruct_done"] = True
    log_trade_history(symbol, f"💣 أُلغي {n} أمر من المنصة (كلها تأكد إلغاؤها) قبل الحذف النهائي")
    save_json(STATE_FILE, state)
    time.sleep(0.4)
    sys.exit(0)
'''),
    ('''    if state.get("self_destruct") and not state.get("destruct_done"):
        destruct_now(state, SYMBOL)
    if not _born(state):
        return
''',
     '''    if state.get("self_destruct") and not state.get("destruct_done"):
        destruct_now(state, SYMBOL)
        return                                            # 💣 لحد ما يتأكد ⇒ بلا تداول
    if not _born(state):
        return
'''),
    ('''    state = load_state_with_backup() or {"total_profit": 0.0}
    _ctl_note(state, _ctl_sig(STATE_FILE))
''',
     '''    state = load_state_with_backup() or {"total_profit": 0.0}
    if state.get("destruct_done"):                       # 💣 انسحب قبل ⇒ ما يتداول أبداً (لو الحارس شغّله)
        print("💣 This bot withdrew (destruct_done) — it does not trade again.")
        sys.exit(0)
    _ctl_note(state, _ctl_sig(STATE_FILE))
'''),
]

DASH = [
    ('''    res = delete_bot(b)
    extra = " — البوت ألغى أوامره " + via if cancelled == -1 else (f" — ألغيت {cancelled} أمر {via}" if cancelled > 0 else "")
''',
     '''    if cancelled != -1 and str(cfg.get("bot_type") or "") == "grid_step" and not cfg.get("is_demo"):   # 🪜 v3.36.17 (F8)
        left = _step_left_orders(b)
        if left is None or left:
            write_cfg_keys(b["cfg_path"], {"auto_restart": False})
            return {"ok": False, "msg": "⛔ لم يُحذف: تعذّر التأكد من إلغاء أوامر البوت على المنصة"
                                        + (f" ({left} أمر باقٍ)" if left else " (لا اتصال بالمنصة)")
                                        + " — البوت يواصل محاولة الإلغاء ولا يضع أوامر جديدة · أعد الحذف بعد قليل"}
    res = delete_bot(b)
    extra = " — البوت ألغى أوامره " + via if cancelled == -1 else (f" — ألغيت {cancelled} أمر {via}" if cancelled > 0 else "")
'''),
    ('''def delete_purge(b):
''',
     '''def _step_left_orders(b):
    """🪜 v3.36.17 (F8): كم أمر للبوت (ببصمته) باقٍ مفتوحاً على المنصة · None = تعذّر السؤال (لا اتصال / لا مفاتيح)"""
    cfg = b["cfg"]
    k, s, p = cfg.get("api_key", ""), cfg.get("secret_key", ""), cfg.get("passphrase", "")
    bid = str(cfg.get("bot_id") or "")
    if not bid:
        return 0                                          # ما اشتغل أبداً ⇒ ما عنده أوامر
    if not (k and s and p):
        return None
    r = _okx_get(f"/api/v5/trade/orders-pending?instType=SPOT&instId={b['symbol']}", k, s, p)
    if not r or str(r.get("code")) != "0" or not isinstance(r.get("data"), list):
        return None
    return sum(1 for d in r["data"] if str(d.get("clOrdId") or "").startswith(bid))


def delete_purge(b):
'''),
]
ALLOWED = {"delete_purge", "_step_left_orders"}


def tops(src):
    out, cnt = {}, {}
    for n in ast.parse(src).body:
        nm = getattr(n, "name", None)
        if nm is None and isinstance(n, ast.Assign) and len(n.targets) == 1:
            nm = ast.unparse(n.targets[0])
        if nm is None:
            cnt[type(n).__name__] = cnt.get(type(n).__name__, 0) + 1
            nm = f"<{type(n).__name__}#{cnt[type(n).__name__]}>"
        out.setdefault(nm, []).append(ast.dump(n))
    return out


def patch(path, R, allowed=None):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        if src.count(a) != 1:
            print(f"❌ {os.path.basename(path)} replacement {i}: found {src.count(a)} times — nothing written"); sys.exit(1)
        src = src.replace(a, b)
    compile(src, path, "exec")
    if allowed is not None:
        t0, t1 = tops(src0), tops(src)
        changed = {k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k)}
        if changed - allowed:
            print(f"❌ unexpected top-level changes: {sorted(changed - allowed)} — nothing written"); sys.exit(1)
    return src


if __name__ == "__main__":
    e = sys.argv[1]
    d = sys.argv[2] if len(sys.argv) > 2 else None
    out = [(e, patch(e, ENG))] + ([(d, patch(d, DASH, ALLOWED))] if d else [])
    for p, s in out:
        with open(p + ".tmp", "w", encoding="utf-8") as fh:
            fh.write(s)
        os.replace(p + ".tmp", p)
    print(f"✅ engine {len(ENG)}" + (f" · dashboard {len(DASH)}" if d else "") + " replacements · compile")
