# 🏦 the owner (9-11): «ايهم يربح اكثر» — OKX Simple Earn (lending the coin itself) against funding arbitrage. REAL OKX public data
#   (GitHub · no keys · no orders): the lending-rate summary now and the hourly lending-rate history of the last ~3 months for XRP and
#   USDT (and a few more) · yearly % and what 6000 XRP / 6,900$ would earn per month.
#   python3 ci/earn_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYEARN
import importlib.machinery, importlib.util, json, os, shutil, statistics, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="earn_")
json.dump({"port": 8102}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYEARN", *a, flush=True)


px = float(((m._okx_pub("/api/v5/market/ticker?instId=XRP-USDT") or {}).get("data") or [{}])[0].get("last") or 0)
P_(f"XRP price {px}")
for ccy in ("XRP", "USDT", "BTC", "ETH", "DOGE", "SOL"):
    r = m._okx_pub(f"/api/v5/finance/savings/lending-rate-summary?ccy={ccy}")
    P_(f"summary {ccy}: {json.dumps((r or {}).get('data'), ensure_ascii=False)[:400]} code={(r or {}).get('code')} msg={(r or {}).get('msg')}")
    h, after = {}, None
    for _ in range(30):
        q = f"/api/v5/finance/savings/lending-rate-history?ccy={ccy}&limit=100" + (f"&after={after}" if after else "")
        d = ((m._okx_pub(q) or {}).get("data")) or []
        if not d:
            break
        for x in d:
            try:
                h[int(x["ts"])] = float(x["rate"])
            except Exception:
                pass
        after = min(int(x["ts"]) for x in d)
        if time.time() * 1000 - after > 95 * 86400000:
            break
        time.sleep(0.25)
    if not h:
        P_(f"history {ccy}: none"); continue
    ts = sorted(h)
    rates = [h[t] for t in ts]
    days = (ts[-1] - ts[0]) / 86400000.0
    mo = {}
    for t in ts:
        mo.setdefault(time.strftime("%Y-%m", time.gmtime(t / 1000)), []).append(h[t])
    avg = statistics.mean(rates)
    P_(f"history {ccy}: {len(rates)} points over {days:.0f} days · yearly rate avg {avg * 100:.2f}% · median {statistics.median(rates) * 100:.2f}% · "
       f"min {min(rates) * 100:.2f}% · max {max(rates) * 100:.2f}% · last {rates[-1] * 100:.2f}% · by month "
       + " ".join(f"{k}:{statistics.mean(v) * 100:.2f}%" for k, v in sorted(mo.items())))
    if ccy == "XRP":
        P_(f"6000 XRP at the average: {6000 * avg / 12:.1f} XRP/month ≈ {6000 * avg / 12 * px:.1f}$ · per year {6000 * avg:.0f} XRP")
    if ccy == "USDT":
        P_(f"{6000 * px:.0f}$ USDT at the average: {6000 * px * avg / 12:.1f}$/month")
P_("RESULT done")
shutil.rmtree(R, ignore_errors=True)
