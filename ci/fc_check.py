# 🔮 v3.28.0: measure the forecast on REAL OKX prices (GitHub runner — public market data, no keys, no orders, no notifications)
#   python3 ci/fc_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYFC (per coin: days · each horizon's verdict, how often it was right, the range check)
import os, sys, json, time, shutil, tempfile, importlib.machinery, importlib.util
DASH = os.path.abspath(sys.argv[1])
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT"]
R = tempfile.mkdtemp(prefix="fc_real_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
print("HOLYFC dashboard", m.APP_VERSION)
db = {}
t0 = time.time()
btc = m.fc_candles("BTC-USDT", db)[0]
print(f"HOLYFC BTC history: {len(btc)} days ({time.strftime('%Y-%m-%d', time.gmtime(btc[0][0])) if btc else '—'} → {time.strftime('%Y-%m-%d', time.gmtime(btc[-1][0])) if btc else '—'}) in {time.time() - t0:.1f}s")
summ = {k: [0, 0, 0] for k, _, _ in m.FC_H}            # hits · calls · coins graded 🟢
for sym in COINS:
    t1 = time.time()
    r = m.fc_coin(sym, db, None if sym.startswith("BTC") else btc)
    dt = time.time() - t1
    if not r:
        print(f"HOLYFC {sym}: no data"); continue
    if r.get("short"):
        print(f"HOLYFC {sym}: short history ({r.get('days')} days)"); continue
    print(f"HOLYFC {sym} px {r['px']:.6g} · {r['days']} days · {dt:.1f}s")
    for k, nm, h in m.FC_H:
        z = r["h"][k]; a = z.get("acc") or {}
        print(f"HOLYFC    {k} {nm:7} now: {z.get('txt', 'short')} up {round((z.get('p') or 0) * 100)}% range {z.get('lo')}–{z.get('hi')} · TV {(z.get('tv') or {}).get('txt')} "
              f"| past: right {a.get('hit')}% of {a.get('n')} · always-up/down {a.get('base')}% · skill {a.get('skill')} · range held {a.get('cov')}% · indep {a.get('indep')} · grade {a.get('grade')}")
        if a.get("n"):
            summ[k][0] += round(a["hit"] * a["n"] / 100); summ[k][1] += a["n"]; summ[k][2] += 1 if a.get("grade") == "g" else 0
    time.sleep(0.3)
for k, nm, h in m.FC_H:
    s = summ[k]
    print(f"HOLYFC TOTAL {k} {nm}: right {round(s[0] / s[1] * 100) if s[1] else '—'}% of {s[1]} past calls · {s[2]} coins 🟢")
print("HOLYFC notifications sent:", len(sent))
print("HOLYFC done", round(time.time() - t0, 1), "s")
