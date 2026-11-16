# 🧪 patch 100 (dashboard v3.36.59 · the demo). The owner (16-11): «الديمو خلي الربح داخل الكرتات … وما اريد اشعارات لانه حساب ديمو».
#   What was found on a live demo (three demo bots · a moving price · the dashboard's own loops):
#   · notifications: the watchdog sent Telegram for demo bots («🤖 الحارس — SOL-USDT طاح وأعدت تشغيله» · «أعاد إطلاق … عند الإقلاع» ·
#     «الحارس أوقف»), and so did the card's buttons (▶️ تشغيل · ⏹ إيقاف · 🗑 حذف · ♻️ إعادة بناء · 💠 …) and «🏁 آخر دورة انتهت» —
#     every one of them also went to the phone app (tg_send ⇒ app_feed_push)
#     ⇒ `_demo_quiet(b)`: inside it no notification leaves (no Telegram · no phone app) — around the card's buttons (`control`), delete,
#       rebuild · the watchdog and «🏁 آخر دورة» skip a demo's message · the counts in «⚡ فتح التطبيق — انطلق N بوت» / «⏻ توقف N بوت» /
#       «🛑 إغلاق مركز التحكم» / «🧬 تحديث المحرك» are the real bots only
#   · the card's profit: the grid family's «اليوم» came from the books (the demo is outside them on purpose) ⇒ always 0 · the daily /
#     monthly / yearly rates came from the books too ⇒ 0 · «متوسط البوتات» compared it with the real bots
#     ⇒ a demo card: «اليوم» from its own log (today's profits × the net factor — the card's own) · the rates from its own profit counter ·
#       «متوسط البوتات» among the demo bots only. The totals, books, reports and accumulators stay without the demo (as before).
#   python3 devtests/step/patches/p100_demo_quiet.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── the quiet context + tg_send obeys it
    ('''TG_DIAG = {"last": "لم يُرسل شيء بعد"}

def tg_send(text, force=False, plain=False):
''', '''TG_DIAG = {"last": "لم يُرسل شيء بعد"}
_TG_DEMO = threading.local()


class _demo_quiet:
    """🧪 v3.36.59 (المالك 16-11: «ما اريد اشعارات لانه حساب ديمو»): داخل هذا السياق لا يخرج أي إشعار يخص بوت الديمو —
    لا تيليغرام ولا تطبيق الموبايل · لبوت حقيقي لا يغيّر شيئاً"""
    def __init__(self, b):
        self.on = bool(((b or {}).get("cfg") or {}).get("is_demo")) if isinstance(b, dict) else False

    def __enter__(self):
        self.prev = getattr(_TG_DEMO, "on", False)
        if self.on:
            _TG_DEMO.on = True
        return self

    def __exit__(self, *a):
        _TG_DEMO.on = self.prev
        return False


def _tg_b(b, text, **k):
    """🧪 v3.36.59: إشعار يخص بوتاً — بوت الديمو بلا إشعار"""
    if ((b or {}).get("cfg") or {}).get("is_demo"):
        return False
    return tg_send(text, **k)


def tg_send(text, force=False, plain=False):
    if getattr(_TG_DEMO, "on", False):                 # 🧪 v3.36.59: فعل يخص بوت ديمو ⇒ ولا إشعار (ولا حتى «إجباري»)
        return False
'''),
    # ── the card's buttons
    ('''def control(d_rel, action, value):
    bots = bot_dirs()''', '''def control(d_rel, action, value):
    """🧪 v3.36.59: أزرار بطاقة الديمو تعمل مثل الحقيقي — بلا إشعار"""
    try:
        _b = bot_dirs().get(os.path.realpath(os.path.join(ROOT, str(d_rel or ""))))
    except Exception:
        _b = None
    with _demo_quiet(_b):
        return _control_do(d_rel, action, value)


def _control_do(d_rel, action, value):
    bots = bot_dirs()'''),
    # ── delete · rebuild
    ('''def delete_bot(b):
    stop_bot(b)''', '''def delete_bot(b):
    with _demo_quiet(b):                                 # 🧪 v3.36.59: حذف الديمو بلا إشعار
        return _delete_bot_do(b)


def _delete_bot_do(b):
    stop_bot(b)'''),
    ('''    tg_send(f"♻️ *إعادة بناء* — `{b['symbol']}` سيرسم شبكة جديدة من السعر الحالي")''',
     '''    _tg_b(b, f"♻️ *إعادة بناء* — `{b['symbol']}` سيرسم شبكة جديدة من السعر الحالي")'''),
    # ── the watchdog
    ('''                if ok:
                    tg_send(f"🤖 *الحارس* — أعاد إطلاق `{b['symbol']}` عند الإقلاع")''',
     '''                if ok:
                    _tg_b(b, f"🤖 *الحارس* — أعاد إطلاق `{b['symbol']}` عند الإقلاع")'''),
    ('''                        tg_send(f"⚠️ *الحارس أوقف* `{b['symbol']}`\\nالسبب: {why}\\nأصلح المشكلة ثم اضغط ▶️ تشغيل")''',
     '''                        _tg_b(b, f"⚠️ *الحارس أوقف* `{b['symbol']}`\\nالسبب: {why}\\nأصلح المشكلة ثم اضغط ▶️ تشغيل")'''),
    ('''                        tg_send(f"🤖 *الحارس* — `{b['symbol']}` طاح وأعدت تشغيله ({len(hist)}/4)")''',
     '''                        _tg_b(b, f"🤖 *الحارس* — `{b['symbol']}` طاح وأعدت تشغيله ({len(hist)}/4)")'''),
    # ── 🏁 the last cycle
    ('''        tg_send(f"🏁 *آخر دورة انتهت — `{b['symbol']}`*\\nتوقف البوت ولم يفتح دورة جديدة (أُطفئ الحارس عليه)\\n"''',
     '''        _tg_b(b, f"🏁 *آخر دورة انتهت — `{b['symbol']}`*\\nتوقف البوت ولم يفتح دورة جديدة (أُطفئ الحارس عليه)\\n"'''),
    # ── the counts: real bots only
    ('''    n = 0
    for b in bot_dirs().values():
        sp, _, _ = paths_of(b)
        if not is_alive(b["dir"], sp)[0]:
            if b["cfg"].get("bot_type") in ("dca", "dca_buy"):''', '''    n = 0
    _START_N["real"] = 0
    for b in bot_dirs().values():
        sp, _, _ = paths_of(b)
        if not is_alive(b["dir"], sp)[0]:
            if b["cfg"].get("bot_type") in ("dca", "dca_buy"):'''),
    ('''                ok2, _m = launch(b)
                if ok2:
                    n += 1
            except Exception:
                pass
    return n
''', '''                ok2, _m = launch(b)
                if ok2:
                    n += 1
                    if not b["cfg"].get("is_demo"):
                        _START_N["real"] += 1           # 🧪 v3.36.59: رسالة «فتح التطبيق» تعدّ الحقيقية فقط
            except Exception:
                pass
    return n


_START_N = {"real": 0}
'''),
    ('''            n = start_all_bots()
            if n:
                tg_send(f"⚡ *فتح التطبيق* — انطلق {n} بوت 🤖")''', '''            n = start_all_bots()
            if n and _START_N["real"]:
                tg_send(f"⚡ *فتح التطبيق* — انطلق {_START_N['real']} بوت 🤖")'''),
    ('''def stop_all_bots(reason=""):
    n = 0
    for b in bot_dirs().values():
        try:
            sp, _, _ = paths_of(b)
            if is_alive(b["dir"], sp)[0]:
                stop_bot(b, disable_auto=True)
                n += 1
        except Exception:
            pass
    if n and reason:
        tg_send(f"⏻ {reason} — توقف {n} بوت بأمان (أوامرهم المحددة باقية على المنصة)")''', '''def stop_all_bots(reason=""):
    n = nr = 0
    for b in bot_dirs().values():
        try:
            sp, _, _ = paths_of(b)
            if is_alive(b["dir"], sp)[0]:
                stop_bot(b, disable_auto=True)
                n += 1
                nr += 0 if b["cfg"].get("is_demo") else 1      # 🧪 v3.36.59: الرسالة تعدّ الحقيقية فقط
        except Exception:
            pass
    if nr and reason:
        tg_send(f"⏻ {reason} — توقف {nr} بوت بأمان (أوامرهم المحددة باقية على المنصة)")'''),
    ('''    n = 0
    for b in bot_dirs().values():
        sp, _, _ = paths_of(b)
        if is_alive(b["dir"], sp)[0]:
            stop_bot(b); n += 1
    tg_send(f"🛑 *[إغلاق مركز التحكم]*\\nتم إيقاف `{n}` بوت.''', '''    n = nr = 0
    for b in bot_dirs().values():
        sp, _, _ = paths_of(b)
        if is_alive(b["dir"], sp)[0]:
            stop_bot(b); n += 1
            nr += 0 if b["cfg"].get("is_demo") else 1          # 🧪 v3.36.59: الرسالة تعدّ الحقيقية فقط
    tg_send(f"🛑 *[إغلاق مركز التحكم]*\\nتم إيقاف `{nr}` بوت.'''),
    ('''def upgrade_engines():
    upd, restarted, skipped = [], [], []''', '''def upgrade_engines():
    upd, restarted, skipped, upd_real = [], [], [], []'''),
    ('''            upd.append(b["symbol"])
            if was:
                launch(b); restarted.append(b["symbol"])''', '''            upd.append(b["symbol"])
            if not b["cfg"].get("is_demo"):
                upd_real.append(b["symbol"])                   # 🧪 v3.36.59: الرسالة بالحقيقية فقط
            if was:
                launch(b); restarted.append(b["symbol"])'''),
    ('''    tg_send(f"🧬 *تحديث المحرك*\\n" + (", ".join(upd) if upd else "—"))''',
     '''    if upd_real or not upd:
        tg_send(f"🧬 *تحديث المحرك*\\n" + (", ".join(upd_real) if upd_real else "—"))'''),
    # ── the card's profit: a demo's «اليوم» from its own log (the books leave the demo out on purpose)
    ('''    else:
        # 💵 الجرد: نقرأ من سجل الأرباح مباشرة — دقيق ولا يتأثر بعدد الأحداث''', '''    elif b["cfg"].get("is_demo"):
        # 🧪 v3.36.59 (المالك 16-11: «الديمو خلي الربح داخل الكرتات»): الدفاتر لا تعرف الديمو (عن قصد) ⇒ ربح اليوم من سجله هو × معامل البطاقة
        _nf0 = _safe(net_factor, b, default=1.0)
        for e in hist:
            if not isinstance(e, dict):
                continue
            if str(e.get("time", "")).startswith(today):
                m = PROFIT_RE.search(e.get("msg", ""))
                if m:
                    today_profit += float(m.group(1)) * _nf0
            elif str(e.get("time", "")) < today:
                break
    else:
        # 💵 الجرد: نقرأ من سجل الأرباح مباشرة — دقيق ولا يتأثر بعدد الأحداث'''),
    ('''    else:
        unit = "$"
        if ta is not None and b.get("dir") in ta:
            tot = float(ta[b["dir"]])''', '''    else:
        unit = "$"
        if b.get("demo"):                                # 🧪 v3.36.59: الديمو خارج الدفاتر ⇒ معدله من عدّاد ربحه هو
            tot = float((b.get("rec") or {}).get("profit") or 0) if bt in _REC_T else float(b.get("profit") or 0)
        elif ta is not None and b.get("dir") in ta:
            tot = float(ta[b["dir"]])'''),
    # ── «متوسط البوتات» on a demo card: among the demo bots
    ('''  let profits=allBots.filter(x=>!x.demo).map(x=>x.profit);   // 🧪 v3.36.46: الديمو خارج المقارنة
  const bench={max:Math.max(0,...profits),avg:profits.length?profits.reduce((a,c)=>a+c,0)/profits.length:0};''',
     '''  let profits=allBots.filter(x=>!x.demo).map(x=>x.profit);   // 🧪 v3.36.46: الديمو خارج المقارنة
  const bench={max:Math.max(0,...profits),avg:profits.length?profits.reduce((a,c)=>a+c,0)/profits.length:0};
  const dprof=allBots.filter(x=>x.demo).map(x=>+x.profit||0);   // 🧪 v3.36.59: كرت الديمو يُقارَن بالديمو فقط
  const benchD={max:Math.max(0,...dprof),avg:dprof.length?dprof.reduce((a,c)=>a+c,0)/dprof.length:0};'''),
    ('''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});''',
     '''    updCard(el,b,b.demo?benchD:bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});'''),
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
    print(f"✅ {len(R)} replacements · the demo: no notification (buttons · watchdog · last cycle · counts) · its card's profit from its own log · compiles · {p}")
