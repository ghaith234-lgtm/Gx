# p154 — v3.36.79 🔀 «شبكة عملتين» · ⑨ the balance refresh does not ask OKX for the pending orders of «SOL-XRP» (no such instrument —
#   the bot keeps no resting orders: its two legs are IOC on OTHER-USDT and MAIN-USDT and finish at once) · its balances are still read
#   python3 devtests/step/patches/p154_pair_nopending.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''        ro = _okx_get(f"/api/v5/trade/orders-pending?instType=SPOT&instId={sym}", k, s, p)
        if ro and ro.get("code") == "0":''',
     '''        ro = None if str(cfg.get("bot_type") or "") == "grid_pair" else \\
            _okx_get(f"/api/v5/trade/orders-pending?instType=SPOT&instId={sym}", k, s, p)   # 🔀 v3.36.79: لا زوج «SOL-XRP» بالمنصة ولا أوامر قاعدة له
        if ro and ro.get("code") == "0":'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 🔀 no pending-orders call for a pair symbol OKX does not have · {p}")
