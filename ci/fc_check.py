# 🔮 v3.29.0: measure the forecast on REAL OKX prices (GitHub runner — public market data, no keys, no orders, no notifications)
#   The dashboard's own engine: the 📊 indicators on 4H / 1D / 3D / 1W candles + Lorentzian · Nadaraya-Watson · Fear & Greed · funding.
#   For 20 coins, every past candle (no look-ahead) ⇒ how often each indicator and their vote called the direction right vs CHANCE
#   (the same up/down mix of calls) · how often the price ended inside the 80% range · CPU time (first run vs the next one).
#   python3 ci/fc_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYFC
import os, sys, json, time, math, shutil, tempfile, importlib.machinery, importlib.util
DASH = os.path.abspath(sys.argv[1])
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT"]
R = tempfile.mkdtemp(prefix="fc_real_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
sent = []
m.tg_send = lambda *a, **k: sent.append(a) or True
m.app_feed_push = lambda *a, **k: sent.append(a) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
print("HOLYFC dashboard", m.APP_VERSION, flush=True)
db = {}
fng = m._fc_fng(db)
print("HOLYFC fear & greed history:", len(fng[0]) if fng else 0, "days", flush=True)
KEYS = [k for k, _, _, _, _ in m.FC_H]
IND = [x[0] for x in m._IND2_K] + [x[0] for x in m._FC_X] + ["vote"]
TOT = {k: {i: [0, 0.0, 0, 0] for i in IND} for k in KEYS}      # hits · expected hits by chance · calls · coins
GR = {k: {"g": 0, "y": 0, "n": 0, "r": 0, "short": 0} for k in KEYS}
COV = {k: [] for k in KEYS}
cpu1, cpu2 = [], []
for sym in COINS:
    c0 = time.process_time(); w0 = time.time()
    try:
        r = m.fc_coin(sym, db, fng)
    except Exception as ex:
        print(f"HOLYFC {sym}: error {type(ex).__name__}: {ex}", flush=True); continue
    c1 = time.process_time() - c0
    if not r:
        print(f"HOLYFC {sym}: no data", flush=True); continue
    if r.get("short"):
        print(f"HOLYFC {sym}: short history ({r.get('days')} days)", flush=True); continue
    cpu1.append(c1)
    print(f"HOLYFC {sym} px {r['px']:.6g} · {r['days']} days · first run cpu {c1:.2f}s (wall {time.time() - w0:.1f}s)", flush=True)
    B = (db.get("bt") or {}).get(sym) or {}
    for k in KEYS:
        z = r["h"].get(k) or {}
        if z.get("short"):
            print(f"HOLYFC    {k}: short ({z.get('have')} candles)", flush=True); GR[k]["short"] += 1; continue
        rel = z["rel"]
        GR[k][rel.get("g", "short")] += 1
        if z["rng"].get("cov") is not None:
            COV[k].append(z["rng"]["cov"])
        e = B.get(k) or {}
        u = (e.get("U", 0) / e["N"]) if e.get("N") else 0.5
        for i in IND:
            a = (e.get("a") or {}).get(i)
            if not a or a[0] + a[1] == 0:
                continue
            T = TOT[k][i]
            T[0] += a[2] + a[3]; T[1] += a[0] * u + a[1] * (1 - u); T[2] += a[0] + a[1]; T[3] += 1
        parts = " ".join(f"{p['k']}:{p['acc'].get('g')}{p['acc'].get('hit', '')}" for p in z["sig"])
        print(f"HOLYFC    {k} {z['tf']}: now {z['vt']} ({z['up']}↑ {z['dn']}↓ of {z['n']}) · vote right {rel.get('hit')}% of {rel.get('n')} vs chance {rel.get('ch')}% "
              f"[{rel.get('g')} · independent {rel.get('neff')}] · range {z.get('lo')}–{z.get('hi')} held {z['rng'].get('cov')}% · squeeze {z['sq']} | {parts}", flush=True)
    c0 = time.process_time()
    m.fc_coin(sym, db, fng)                                    # ⏱️ the next run (what happens every 30 min)
    cpu2.append(time.process_time() - c0)
print("HOLYFC ===== totals (all coins · every past candle · right% vs chance% with the same up/down mix of calls)", flush=True)
for k, nm, tf, H, dd in m.FC_H:
    print(f"HOLYFC TOTAL {k} {nm} ({tf} candles, {H} ahead): vote badges {GR[k]} · range held {min(COV[k]) if COV[k] else '-'}–{max(COV[k]) if COV[k] else '-'}% "
          f"(avg {round(sum(COV[k]) / len(COV[k])) if COV[k] else '-'}%)", flush=True)
    rows = []
    for i in IND:
        h, ex, n, nc = TOT[k][i]
        if n:
            rows.append((round((h - ex) / n * 100, 1), f"{i}: {h / n * 100:.1f}% vs {ex / n * 100:.1f}% ({'+' if h >= ex else ''}{(h - ex) / n * 100:.1f}) of {n} · {nc} coins"))
    for _, txt in sorted(rows, reverse=True):
        print(f"HOLYFC    {txt}", flush=True)
print(f"HOLYFC cpu per coin: first run avg {sum(cpu1) / max(1, len(cpu1)):.2f}s max {max(cpu1 or [0]):.2f}s · next runs avg {sum(cpu2) / max(1, len(cpu2)):.3f}s max {max(cpu2 or [0]):.3f}s", flush=True)
print("HOLYFC notifications sent:", len(sent), flush=True)
print("HOLYFC done", flush=True)
