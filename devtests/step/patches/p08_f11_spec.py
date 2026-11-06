# 🪜 patch 08 (engine · F11) — the bot is born only once it has the coin's spec (price step · quantity step · minimum). It read it
#   with market_api.get_instruments — the real python-okx 0.4.4 MarketAPI has NO such method (it is in PublicData.PublicAPI) — so it
#   always fell back to urllib, which Cloudflare blocks (the project's rule 1) ⇒ on the real OKX the bot waited for ever, silently.
#   Now: the ways in order — MarketAPI.get_instruments if it exists (the trial path's box has it) · the library's PublicData.PublicAPI
#   · requests (rule 1) · none answered ⇒ a log line every 10 minutes (it waits and places no order).
#   python3 devtests/step/patches/p08_f11_spec.py ENGINE.py      (in place · the old text must be found once)
import os, sys

R = [
    ('''def load_instrument_spec(symbol):
    """مواصفات العملة من OKX مرة واحدة: خطوة السعر · خطوة الكمية · أدنى حجم"""
    if INSTRUMENT_SPEC["loaded"]:
        return
    try:
        r = market_api.get_instruments(instType="SPOT", instId=symbol) if hasattr(market_api, "get_instruments") else None
        if not r:
            import urllib.request
            with urllib.request.urlopen(f"https://www.okx.com/api/v5/public/instruments?instType=SPOT&instId={symbol}", timeout=8) as resp:
                r = json.loads(resp.read().decode("utf-8"))
        if r and r.get("code") == "0" and r.get("data"):
            d = r["data"][0]
            INSTRUMENT_SPEC["tickSz"] = float(d.get("tickSz") or 0) or None
            INSTRUMENT_SPEC["lotSz"] = float(d.get("lotSz") or 0) or None
            INSTRUMENT_SPEC["minSz"] = float(d.get("minSz") or 0) or None
            INSTRUMENT_SPEC["loaded"] = True
    except Exception as e:
        print(f"⚠️ تعذّر جلب مواصفات العملة: {e}")
''',
     '''SPEC_LOG = {"t": 0.0}


def load_instrument_spec(symbol):
    """مواصفات العملة من OKX: خطوة السعر · خطوة الكمية · أدنى حجم — بلاها البوت ما يولد (F11: مكتبة okx الحقيقية ما بيها
    MarketAPI.get_instruments والطريق القديم urllib يحجبه Cloudflare ⇒ كان ينتظر للأبد بصمت) · الطرق بالترتيب: MarketAPI إذا موجودة ·
    PublicData.PublicAPI (المكتبة) · requests (قاعدة المشروع) · ما ردّت ⇒ سطر بالسجل كل 10 دقائق (ينتظر ولا يضع أي أمر)"""
    if INSTRUMENT_SPEC["loaded"]:
        return

    def _pub():
        import okx.PublicData as _PD
        return _PD.PublicAPI(flag=FLAG).get_instruments(instType="SPOT", instId=symbol)
    ways = ([lambda: market_api.get_instruments(instType="SPOT", instId=symbol)] if hasattr(market_api, "get_instruments") else []) + [
        _pub, lambda: requests.get(f"https://www.okx.com/api/v5/public/instruments?instType=SPOT&instId={symbol}", timeout=8).json()]
    why = ""
    for way in ways:
        try:
            r = way()
            if r and str(r.get("code")) == "0" and r.get("data"):
                d = r["data"][0]
                INSTRUMENT_SPEC["tickSz"] = float(d.get("tickSz") or 0) or None
                INSTRUMENT_SPEC["lotSz"] = float(d.get("lotSz") or 0) or None
                INSTRUMENT_SPEC["minSz"] = float(d.get("minSz") or 0) or None
                INSTRUMENT_SPEC["loaded"] = True
                return
            why = str((r or {}).get("msg") or (r or {}).get("code") or "رد فارغ")
        except Exception as e:
            why = f"{type(e).__name__}"
    if time.time() - SPEC_LOG["t"] > 600:
        SPEC_LOG["t"] = time.time()
        log_trade_history(SYMBOL, f"⏳ [الشبكي المتدرج] تعذّر جلب مواصفات العملة من المنصة ({why[:60]}) — ينتظر ولا يضع أي أمر")
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
    print(f"✅ {len(R)} replacement · compiles · {p}")
