# 💵 patch 85 (engines dca.py · the buy DCA — changed with the owner's yes, 14-11: «صلح الاثنين ويا تحذير النموذج») — the full audit,
#   batch 2: an order the exchange refused for lack of balance (51008) was sent again on the next loop, every 4–5 seconds, for as long
#   as the balance was short — about 17,000 refused orders a day (the log line was already quiet, the requests were not).
#   ⇒ after such a refusal the same side rests: 20 seconds, then 40, then 60 (it stays 60 — about 1,400 a day at the very most, 12 times
#     fewer; a longer rest was tried (5 minutes) and made the bot enter the next cycle late after the balance came back, so it lost
#     trades) · the first order that goes through clears it ·
#     the other side is not held (a sell is never delayed because a buy was refused) · nothing else changes — the order goes out
#     exactly once as before
#   python3 devtests/step/patches/p85_dca_nocash_rest.py devtests/step/eng/dca.py     (the same for dca_buy.py)
import os, sys

R = [
    ('''def _xs_send(trade_api, symbol, key, cl, rec, what, **kw):''',
     '''_NOCASH = {}   # 💵 v3.36.51: جهة (buy/sell) رفضتها المنصة لنقص الرصيد ⇒ تهدأ 20 ⇐ 40 ⇐ 60 ثانية (كانت تُعاد كل 4–5 ثوانٍ)


def _xs_send(trade_api, symbol, key, cl, rec, what, **kw):'''),
    ('''    if not NET_STATE["online"]:
        return None, None
    _xs()[key] = {"cl": cl, "ts": time.time(), "r": dict(rec or {})}''',
     '''    if not NET_STATE["online"]:
        return None, None
    _sd = str(kw.get("side") or "")
    _nc = _NOCASH.get(_sd)
    if _nc and time.time() < _nc["until"]:
        return None, None                                # 💵 v3.36.51: الجهة تهدأ بعد رفض لنقص الرصيد
    _xs()[key] = {"cl": cl, "ts": time.time(), "r": dict(rec or {})}'''),
    ('''        _xs().pop(key, None)
        _xs_save()
        return str(d["ordId"]), dict(rec or {})''',
     '''        _xs().pop(key, None)
        _xs_save()
        _NOCASH.pop(_sd, None)
        return str(d["ordId"]), dict(rec or {})'''),
    ('''    _xs().pop(key, None)
    _xs_save()
    log_history(symbol, f"❌ رفض {what}: {sm}")
    return None, None''',
     '''    _xs().pop(key, None)
    _xs_save()
    if sc == "51008":                                    # 💵 v3.36.51: نقص رصيد ⇒ الجهة تهدأ 20 ⇐ 40 ⇐ 60 ثانية
        _w = {0: 20.0, 20.0: 40.0}.get((_nc or {}).get("wait", 0), 60.0)
        _NOCASH[_sd] = {"until": time.time() + _w, "wait": _w}
    log_history(symbol, f"❌ رفض {what}: {sm}")
    return None, None'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:80]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p, "w", encoding="utf-8").write(s)
    print(f"✅ {len(R)} replacements · compiles · {p}")
