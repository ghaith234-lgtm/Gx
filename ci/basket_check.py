# 🧺 the owner (9-11): «بوت وعاء فيه ثلاث عملات sui xrp xlm واي واحد يصعد يبيع يشتري الباقي … هل راح تكبر المحفظة مثلا كل واحدة ١٠٠ دولار»
#   REAL OKX public data (GitHub · no keys · no orders): 100$ in each coin · rebalance back to equal when one coin's value is X% away from its
#   share (5 · 10 · 20 · 30%) or every week · fee 0.1% on every dollar traded (each swap passes through USDT) · against simply holding ·
#   last year (1H closes) · 6 months · 3 months · and the same with other baskets for comparison
#   python3 ci/basket_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYBASKET
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="basket_")
json.dump({"port": 8104}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
P_ = lambda *a: print("HOLYBASKET", *a, flush=True)
FEE = 0.001
now = int(time.time())
t1 = now // 3600 * 3600
t0 = t1 - 365 * 86400
C = {}
for c in ("SUI", "XRP", "XLM", "SOL", "ADA", "DOGE", "BTC", "ETH", "LINK", "HBAR"):
    C[c] = {r_[0]: r_[4] for r_ in m._bt_hist(f"{c}-USDT", "1H", 3600, t0, t1)}
    P_(f"{c}: {len(C[c])} hourly closes")


def run(coins, days, th=None, weekly=False):
    ts = sorted(set.intersection(*[set(C[c]) for c in coins]))
    ts = [t for t in ts if t >= t1 - days * 86400]
    p0 = {c: C[c][ts[0]] for c in coins}
    q = {c: 100.0 / p0[c] for c in coins}
    hold = dict(q)
    n, fees, last_w = 0, 0.0, ts[0]
    peak, mdd = 0.0, 0.0
    for t in ts:
        v = {c: q[c] * C[c][t] for c in coins}
        V = sum(v.values())
        peak = max(peak, V); mdd = max(mdd, (peak - V) / peak)
        tgt = V / len(coins)
        due = (weekly and t - last_w >= 7 * 86400) or (th is not None and any(abs(v[c] - tgt) / tgt > th for c in coins))
        if due:
            traded = sum(abs(v[c] - tgt) for c in coins)          # sells + buys, each through USDT
            f = traded * FEE
            fees += f; n += 1; last_w = t
            V2 = V - f
            for c in coins:
                q[c] = V2 / len(coins) / C[c][t]
    te = ts[-1]
    Vb = sum(q[c] * C[c][te] for c in coins)
    Vh = sum(hold[c] * C[c][te] for c in coins)
    return Vb, Vh, n, fees, mdd, {c: (q[c] / hold[c] - 1) * 100 for c in coins}, {c: (C[c][te] / p0[c] - 1) * 100 for c in coins}


for coins in (("SUI", "XRP", "XLM"), ("XRP", "XLM", "HBAR"), ("SOL", "ADA", "DOGE"), ("BTC", "ETH", "XRP"), ("XRP", "SOL"), ("SUI", "XRP", "XLM", "LINK")):
    for days, lbl in ((365, "year"), (182, "6 months"), (91, "3 months")):
        try:
            base = run(coins, days)
        except Exception as e:
            P_(f"{'+'.join(coins)} {lbl}: {e}"); continue
        Vh = base[1]
        mv = " ".join(f"{c} {x:+.0f}%" for c, x in base[6].items())
        out = []
        for th, wk in ((0.05, False), (0.10, False), (0.20, False), (0.30, False), (None, True)):
            Vb, _, n, fees, mdd, dq, _ = run(coins, days, th, wk)
            out.append(f"{'weekly' if wk else f'{th * 100:g}%'}: {Vb:.0f}$ ({Vb - Vh:+.0f}$ vs hold · {n} rebalances · fees {fees:.1f}$ · coins "
                       + "/".join(f"{x:+.0f}%" for x in dq.values()) + ")")
        P_(f"{'+'.join(coins)} · {lbl} · start {100 * len(coins)}$ · prices {mv} · HOLD {Vh:.0f}$ · " + " | ".join(out))
P_("RESULT done")
shutil.rmtree(R, ignore_errors=True)
