# 🧲💪🌐 v3.32.0: measure the new indicators on REAL prices (GitHub runner — public data, no keys, no orders, no notifications)
#   The dashboard's own code: 🧲 accumulation/distribution and 💪 strength vs BTC on 20 coins (OKX daily candles, years), and
#   🌐 the market-wide readings (DefiLlama stablecoins · Coinbase premium · CoinGecko global) with 💵/🇺🇸 checked on BTC 7 days later.
#   Every past day (no look-ahead) ⇒ how often the reading was right vs CHANCE (same up/down mix) · CPU time.
#   python3 ci/x32_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYX
import os, sys, json, time, shutil, tempfile, importlib.machinery, importlib.util
DASH = os.path.abspath(sys.argv[1])
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT"]
R = tempfile.mkdtemp(prefix="x32_real_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
print("HOLYX dashboard", m.APP_VERSION, flush=True)
db = {}
bd, bl = m.fc_candles("BTC-USDT", db)
btc = {int(r[0]): float(r[4]) for r in list(bd) + ([bl] if bl else [])}
print("HOLYX BTC daily candles:", len(bd), flush=True)
P = {"div": [0.0, 0.0, 0], "trn": [0.0, 0.0, 0], "rs": [0.0, 0.0, 0]}       # hits · chance hits · calls (pooled over coins)
G = {k: {"g": 0, "y": 0, "n": 0, "r": 0, "short": 0} for k in P}
NOW = {}
cpu = []
for sym in COINS:
    try:
        d1, l1 = m.fc_candles(sym, db)
        c0 = time.process_time()
        x = m.xc_coin(sym, d1, l1, btc)
        cpu.append(time.process_time() - c0)
    except Exception as ex:
        print(f"HOLYX {sym}: error {type(ex).__name__}: {ex}", flush=True)
        continue
    if not x:
        print(f"HOLYX {sym}: short history ({len(d1)} days)", flush=True)
        continue
    a, rs = x.get("ad") or {}, x.get("rs") or {}
    parts = []
    for key, acc in (("div", a.get("acc_div")), ("trn", a.get("acc_trn")), ("rs", None if rs.get("ref") else rs.get("acc"))):
        if not acc:
            continue
        G[key][acc.get("g", "short")] += 1
        if acc.get("n") and acc.get("hit") is not None:
            P[key][0] += acc["hit"] * acc["n"] / 100.0
            P[key][1] += acc.get("ch", 50) * acc["n"] / 100.0
            P[key][2] += acc["n"]
        parts.append(f"{key} {acc.get('hit', '—')}% vs {acc.get('ch', '—')}% ({acc.get('n', 0)}) {acc.get('g')}")
    NOW[a.get("k", "?")] = NOW.get(a.get("k", "?"), 0) + 1
    rs_t = "" if rs.get("ref") else f" (7d {rs.get('r7')}% · 30d {rs.get('r30')}%)"
    print(f"HOLYX {sym}: {len(d1)} days · now 🧲 {a.get('k')} (flow {a.get('flow')}% · price {a.get('pc')}%) · 💪 {rs.get('k')}{rs_t} · " + " · ".join(parts), flush=True)
    time.sleep(0.3)
for key, nm in (("div", "🧲 accumulation/distribution (acc ⇒ up · dist ⇒ down, 14 days later)"), ("trn", "🧲 money-backed move (up/down continues, 14 days)"),
                ("rs", "💪 stronger/weaker than BTC (still stronger/weaker 14 days later)")):
    h, ch, n = P[key]
    print(f"HOLYX POOLED {nm}: right {h / n * 100 if n else 0:.1f}% vs chance {ch / n * 100 if n else 0:.1f}% over {n} calls · coins "
          + " ".join(f"{g}={G[key][g]}" for g in ("g", "y", "n", "r", "short")), flush=True)
print("HOLYX now:", json.dumps(NOW), flush=True)
print(f"HOLYX CPU xc_coin per coin: avg {sum(cpu) / len(cpu) if cpu else 0:.3f}s · max {max(cpu) if cpu else 0:.3f}s", flush=True)
# 🌐 market-wide
v = m.mkt_tick()
for r in (v or {}).get("rows") or []:
    print(f"HOLYX market {r['ico']} {r['name']}: {r['val']} · {r['txt']} · {r.get('sub', '')}", flush=True)
print(f"HOLYX market mood: {(v or {}).get('mood_t')} ({(v or {}).get('up')} up · {(v or {}).get('dn')} down of {(v or {}).get('n')})", flush=True)
md = m._mkt_db()
print("HOLYX stablecoin history days:", len(((md.get("st") or {}).get("d") or {})), "· coinbase daily closes:", len(((md.get("cb") or {}).get("d") or {})), flush=True)
rel = m._mkt_rel(db)
for k, nm in (("st", "💵 stablecoin liquidity (in ⇒ BTC up 7 days later)"), ("cb", "🇺🇸 Coinbase premium (positive ⇒ BTC up 7 days later)")):
    g = rel.get(k) or {}
    print(f"HOLYX market reliability {nm}: right {g.get('hit', '—')}% vs chance {g.get('ch', '—')}% over {g.get('n', 0)} calls (independent ≈{g.get('neff', '—')}) · grade {g.get('g')}", flush=True)
print("HOLYX notifications sent:", len(sent), flush=True)
print("HOLYX done", flush=True)
