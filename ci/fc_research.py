# 🔬 v3.28.0: which direction signal really beats guessing on REAL prices? (same walk-forward test as the dashboard · no look-ahead)
#   compares, per horizon, on 20 coins: the dashboard's «similar past events» · the same with stronger shrink · conditional base rates on
#   momentum · TradingView rating · trend (200 days) · trend+momentum. Output lines start with HOLYRS.  python3 ci/fc_research.py Holy_Dashboard.pyw
import os, sys, json, time, math, shutil, tempfile, importlib.machinery, importlib.util
DASH = os.path.abspath(sys.argv[1])
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT"]
R = tempfile.mkdtemp(prefix="fc_rs_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = m.app_feed_push = lambda *a, **k: True
db = {}
btc = m.fc_candles("BTC-USDT", db)[0]
MODELS = ["knn", "knn_shrink", "mom", "tv", "trend", "trend_mom"]
TOT = {k: {mm: [0, 0, 0.0, 0.0, 0] for mm in MODELS} for k, _, _ in m.FC_H}   # hits · calls · brier · brier_base · coins with skill>0


def bucket(model, F, i, k, h):
    X, C = F["X"], F["C"]
    x = X[i]
    if x is None:
        return None
    L = max(7, h)
    mom = (C[i] / C[i - L] - 1) if i >= L and C[i - L] else 0.0
    if model == "mom":
        return 1 if mom > 0 else 0
    if model == "tv":
        v = x[{"d": 0, "w": 1, "m": 2, "q": 2}[k]]
        return 0 if v < -0.5 else 1 if v < -0.1 else 2 if v <= 0.1 else 3 if v <= 0.5 else 4
    if model == "trend":
        return 1 if x[3] > 0 else 0
    if model == "trend_mom":
        return (1 if x[3] > 0 else 0) * 2 + (1 if mom > 0 else 0)


for sym in COINS:
    try:
        rows = m.fc_candles(sym, db)[0]
    except Exception as e:
        print("HOLYRS", sym, "error", e); continue
    if len(rows) < 600:
        print("HOLYRS", sym, "short", len(rows)); continue
    is_btc = sym.startswith("BTC")
    F = m._fc_features(rows, None if is_btc else btc)
    X, C = F["X"], F["C"]
    n = len(C)
    first = next(i for i, x in enumerate(X) if x)
    line = [sym, str(n)]
    for k, nm, h in m.FC_H:
        t0 = max(first + 260, int(n * 0.45))
        step = {"d": 2, "w": 3, "m": 6, "q": 12}[k]
        sd = m._fc_scale(X, t0)
        st = {mm: [0, 0, 0.0, 0.0] for mm in MODELS}
        B = {mm: [bucket(mm, F, i, k, h) if X[i] is not None else None for i in range(n)] for mm in ("mom", "tv", "trend", "trend_mom")}
        up_i = [1 if (i + h < n and C[i + h] > C[i]) else 0 for i in range(n)]
        cnt = {mm: {} for mm in B}
        tot = [0, 0]
        nxt = first                                         # the next past day whose outcome becomes known
        for t in range(t0, n - h, step):
            while nxt <= t - h:
                if X[nxt] is not None:
                    tot[0] += 1; tot[1] += up_i[nxt]
                    for mm in B:
                        c = cnt[mm].setdefault(B[mm][nxt], [0, 0]); c[0] += 1; c[1] += up_i[nxt]
                nxt += 1
            if tot[0] < 60:
                continue
            r = math.log(C[t + h] / C[t]); y = 1.0 if r > 0 else 0.0
            base = tot[1] / tot[0]
            preds = {}
            pr = m._fc_predict(F, t, k, h, sd, not is_btc)
            if pr:
                preds["knn"] = pr["p"]
                preds["knn_shrink"] = base + 0.5 * (pr["p"] - base)
            for mm in B:
                c = cnt[mm].get(B[mm][t], [0, 0])
                preds[mm] = (c[1] + 20 * base) / (c[0] + 20)
            for mm, p in preds.items():
                s_ = st[mm]
                s_[2] += (p - y) ** 2; s_[3] += (base - y) ** 2
                if abs(p - 0.5) >= 0.03:
                    s_[1] += 1; s_[0] += 1 if (p > 0.5) == (r > 0) else 0
        cell = []
        for mm in MODELS:
            s = st[mm]; T = TOT[k][mm]
            sk = 1 - s[2] / s[3] if s[3] else 0.0
            T[0] += s[0]; T[1] += s[1]; T[2] += s[2]; T[3] += s[3]; T[4] += 1 if sk > 0 else 0
            cell.append(f"{mm}:{round(s[0] / s[1] * 100) if s[1] else '-'}%/{sk:+.3f}")
        line.append(f"{k}[" + " ".join(cell) + "]")
    print("HOLYRS", " ".join(line), flush=True)
for k, nm, h in m.FC_H:
    print("HOLYRS TOTAL", k, nm, " · ".join(f"{mm}: right {round(T[0] / T[1] * 100) if T[1] else '-'}% of {T[1]} · skill {1 - T[2] / T[3]:+.4f} · {T[4]} coins better than guessing"
                                           for mm, T in TOT[k].items()))
print("HOLYRS done")
