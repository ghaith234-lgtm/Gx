# ⏳ patch 105 (dashboard v3.36.61 · the temporary buy pause closes on the exchange's own refusal). The owner (16-11), after the
#   «🚨 فشل أوامر متكرر» of his 🪜 XRP bot (21 buys refused — 51008 · the dollars ran out): «طيب احنه قلنا اذا ماكو دولار يتفعل ايقاف
#   الشراء المؤقت». Read in the code: the guard decides «short» from its own estimate of the bot's next order — the level's dollars
#   (`usd_value` — 🪜 ÷ its parts). The real order can be bigger: 💠 reinvest grows it, the lot rounding, a 🪜 window placing several
#   parts at once ⇒ the estimate says «enough», OKX says «Insufficient USDT balance», the pause never closes and the bot keeps trying.
#   ⇒ the exchange's word counts too: a BUY of this bot refused for dollars (51008 · «insufficient») in its own log — in the last 15
#     minutes, after its last close/opening — makes it short at once (no second scan) with that order's real dollars as its need. The
#     rest is v3.36.58's own path (closing from the gap start · the notice · «🔓 افتح» by the owner). The engines are untouched.
#   python3 devtests/step/patches/p105_tp_on_refusal.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''def _tp_kind(b):''', '''_TP_REJ_RE = re.compile(r"(?:كمية \\(|الكمية |أمر \\()([0-9.eE+-]+)\\)?\\s*بسعر \\(?([0-9.eE+-]+)")


def _tp_rej_line(msg):
    """سطر شراء رفضته المنصة لنفاد الدولار؟ (🪜 «⚠️ [رفض أمر شراء] …: Order failed. Insufficient USDT» · ♾️ ➕ 🎚️ «💵 [رفض أمر شراء] الدولار الحر ما يكفي»)"""
    m = str(msg or "")
    if "شراء" not in m:
        return False
    if "الدولار الحر ما يكفي" in m:
        return True
    return ("رفض" in m or "فشل" in m) and _rej_why(m)[1] == "51008"


def _tp_rej_usd(msg):
    m_ = _TP_REJ_RE.search(str(msg or ""))
    try:
        v = float(m_.group(1)) * float(m_.group(2)) if m_ else -1.0
    except Exception:
        v = -1.0
    return v if v > 0 else -1.0


def _tp_rej(b, since, now=None):
    """⏳ v3.36.61: المنصة نفسها رفضت أمر شراء لهذا البوت لأن الدولار لا يكفي — بعد `since` (غلقه أو فتحه الأخير) وخلال 15 دقيقة ⇒
    دولار ذلك الأمر (من سطر سجله) · -1 لو ما عُرف حجمه · 0 لا رفض. محركات الشبكة تكتب السطر بأول رفض فقط ⇒ وعدّاد «nocash» بحالتها
    (until = وقت الرفض + انتظار ≤ 10 دقائق) يقول إنها ما زالت ترفض"""
    now = float(now if now is not None else time.time())
    lim = max(float(since or 0), now - 900)
    try:
        hist = [e for e in (load_json(paths_of(b)[1]) or [])[:300] if isinstance(e, dict)]
    except Exception:
        hist = []
    for e in hist:                                        # الأحدث أولاً
        if _parse_ts(e.get("time")) < lim:
            break
        if _tp_rej_line(e.get("msg")):
            return _tp_rej_usd(e.get("msg"))
    try:
        st = load_json(paths_of(b)[0]) or {}
        nc = st.get("nocash") if isinstance(st.get("nocash"), dict) else {}
        u_ = float(nc.get("until") or 0)
        if int(nc.get("n") or 0) >= 1 and u_ - 600 > float(since or 0) and u_ > now - 900:
            return next((_tp_rej_usd(e.get("msg")) for e in hist if _tp_rej_line(e.get("msg"))), -1.0)
    except Exception:
        pass
    return 0.0


def _tp_kind(b):'''),
    ('''                    r = d["bots"].get(k)
                    short = un < u and i.get("alive")
                    if short:
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": int(sv.get("n") or 0) + 1, "need": u, "ts": now}''',
     '''                    r = d["bots"].get(k)
                    rj = (_safe(_tp_rej, b, max(float(d["opened"].get(k) or 0), float(r.get("ts") or 0) if isinstance(r, dict) else 0.0), now, default=0.0)
                          if i.get("alive") else 0.0)
                    if rj:                                      # ⏳ v3.36.61: المنصة نفسها رفضت شراءه لنفاد الدولار ⇒ قاصر مهما قال التقدير
                        u = max(u, rj)
                    short = (un < u or bool(rj)) and i.get("alive")
                    if short:
                        sv = d["seen"].get(k) if isinstance(d["seen"].get(k), dict) else {}
                        d["seen"][k] = {"n": max(int(sv.get("n") or 0) + 1, CW_SEEN if rj else 0), "need": u, "ts": now}   # رفض المنصة ⇒ بلا فحص ثانٍ'''),
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
    print(f"✅ {len(R)} replacements · ⏳ the temporary pause also closes on OKX's own «not enough dollars» for the bot's buy · compiles · {p}")
