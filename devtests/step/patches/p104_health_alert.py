# 🚨 patch 104 (dashboard v3.36.60 · the «فشل أوامر متكرر» alert). The owner (16-11) sent the phone notification:
#   «🚨 [فشل أوامر متكرر] XRP-USDT — مرفوضة آخر ساعة: 0 · متتالية: 21 · آخر خطأ: ⚠️ [رفض أمر شراء] الكمية 2.002192 بسعر 0.9586
#   (المستوى -13 · الجزء 1): Order f…» — «ما مشكلة هذه». Read in the code:
#   · the 🪜 bot tried to buy its level −13 and OKX refused it — the English reason cut at 100 characters («Order f…» = «Order failed.
#     Insufficient USDT balance» — 51008: the free dollars ran out) · the engine backs off (up to an hour on that side) and tries again
#   · the alert's «bad» = 3 refusals in a row since the last success — however OLD they are: no new refusal in the last hour («0») and it
#     still came back every hour until a trade succeeded (the bot «calls» for dollars — what the owner meant earlier by «ينادي») · the
#     card's 🩺 showed «🚨 0 أمر مرفوض آخر ساعة» the same way
#   ⇒ «bad» needs a refusal in the last hour (the streak's newest is recent) or 5 in the hour · a BUY refused because the dollars ran out
#     sends no 🚨: that case has its own notices since v3.36.58 (⏳ the temporary pause closes buying · 💵 «توفر دولار» at most every 10 h ·
#     🛡️ «نفد الدولار الحر») · the alert gives the reason in Arabic (OKX's code) instead of the cut English
#   python3 devtests/step/patches/p104_health_alert.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            "state": ("bad" if streak >= 3 or fails_1h >= 5 else
                      "warn" if fails_1h >= 1 else "ok")}''',
     '''            "state": ("bad" if (streak >= 3 and fails_1h >= 1) or fails_1h >= 5 else      # 🚨 v3.36.60: رفض قديم بلا جديد ⇒ ما يرجع «سيئ» كل ساعة
                      "warn" if fails_1h >= 1 else "ok")}'''),
    ('''def health_alert_tick():
    """🚨 تنبيه تليجرام عند فشل أوامر متكرر (مرة كل ساعة لكل بوت)"""
    now = time.time()
    for b in bot_dirs().values():
        try:
            if b["cfg"].get("is_demo"): continue
            h = health_of(b)
            if h["state"] != "bad": 
                _ALERT_SENT.pop(b["dir"], None); continue
            if now - _ALERT_SENT.get(b["dir"], 0) < 3600: continue
            _ALERT_SENT[b["dir"]] = now
            tg_send(f"🚨 *[فشل أوامر متكرر]* `{b['symbol']}`\\n"
                    f"مرفوضة آخر ساعة: `{h['fails_1h']}` · متتالية: `{h['streak']}`\\n"
                    f"آخر خطأ: `{h['last_err_msg'][:100]}`")
        except Exception:
            pass''', '''_REJ_WHY = (("51008", ("insufficient",), "الرصيد لا يكفي"), ("51020", ("minimum",), "الكمية أقل من حد المنصة"),
            ("51006", ("price limit", "out of range"), "السعر خارج حدود المنصة"), ("50011", ("too many",), "طلبات كثيرة — المنصة طلبت التمهّل"),
            ("51000", ("parameter",), "قيمة غير مقبولة في الأمر"))


def _rej_why(msg):
    """🚨 v3.36.60: سبب الرفض بالعربي من رمز OKX أو رسالتها الإنجليزية ⇒ (السبب، الرمز) أو ("", "")"""
    m = str(msg or "")
    low = m.lower()
    for code, keys, why in _REJ_WHY:
        if code in m or any(k in low for k in keys):
            return why, code
    return "", ""


def _rej_short(msg):
    """🚨 v3.36.60: «⚠️ [رفض أمر شراء] … (المستوى -13 · الجزء 1) — الرصيد لا يكفي (51008)» بدل الإنجليزي المقطوع"""
    m = str(msg or "").strip()
    why, code = _rej_why(m)
    head = m.split("): ", 1)[0] + ")" if "): " in m else m
    return (head[:120] + (f" — {why} ({code})" if why else (" — " + m.split("): ", 1)[1][:90] if "): " in m else "")))[:220]


def _rej_cash(msg):
    """🚨 v3.36.60: أمر شراء رُفض لأن الدولار نفد — له إشعاراته الخاصة (⏳ المؤقت · 💵 توفر دولار · 🛡️ نفد الدولار الحر)"""
    m = str(msg or "")
    return ("شراء" in m) and _rej_why(m)[1] == "51008"


def health_alert_tick():
    """🚨 تنبيه تليجرام عند فشل أوامر متكرر (مرة كل ساعة لكل بوت) · v3.36.60: الرفض الحديث فقط · نفاد الدولار له إشعاراته · السبب بالعربي"""
    now = time.time()
    for b in bot_dirs().values():
        try:
            if b["cfg"].get("is_demo"): continue
            h = health_of(b)
            if h["state"] != "bad" or _rej_cash(h.get("last_err_msg")):
                _ALERT_SENT.pop(b["dir"], None); continue
            if now - _ALERT_SENT.get(b["dir"], 0) < 3600: continue
            _ALERT_SENT[b["dir"]] = now
            tg_send(f"🚨 *[فشل أوامر متكرر]* `{b['symbol']}`\\n"
                    f"مرفوضة آخر ساعة: `{h['fails_1h']}` · متتالية: `{h['streak']}`\\n"
                    f"آخر خطأ: `{_rej_short(h['last_err_msg'])}`")
        except Exception:
            pass'''),
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
    print(f"✅ {len(R)} replacements · 🚨 recent refusals only · no alarm for a buy refused for dollars · the reason in Arabic · compiles · {p}")
