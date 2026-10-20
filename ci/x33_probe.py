# 🔎 v3.33.0: probe #2 — alternatives for the sources that failed (FRED blocked from GitHub · GDELT rate limit · GPR only xls)
#   and how deep the paginated OKX/Deribit history goes. Public GETs only · no keys · no orders · no notifications. ⇒ lines HOLYP
import json, time, requests
NOW = int(time.time() * 1000); DAY = 86400000
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
def get(url, t=40):
    return requests.get(url, headers=H, timeout=t)
def show(tag, url, n=300):
    try:
        r = get(url); b = r.text
        lines = b.strip().splitlines()
        print(f"HOLYP {tag}: {r.status_code} {r.headers.get('content-type','')[:40]} {len(b)}B lines={len(lines)}", flush=True)
        print(f"HOLYP {tag} head: {b[:n]!r}", flush=True)
        if len(lines) > 3:
            print(f"HOLYP {tag} tail: {lines[-1][:200]!r}", flush=True)
    except Exception as e:
        print(f"HOLYP {tag}: ERROR {type(e).__name__}: {e}", flush=True)
    time.sleep(1.5)
# GDELT first (fresh, one call, then a long gap)
GD = "https://api.gdeltproject.org/api/v2/doc/doc?format=json&query=%28bitcoin%20OR%20cryptocurrency%29"
show("gdelt tone 3months", GD + "&mode=timelinetone&timespan=3months", 500)
time.sleep(25)
show("gdelt volraw 3months", GD + "&mode=timelinevolraw&timespan=3months", 300)
time.sleep(25)
show("gdelt tone 2020", GD + "&mode=timelinetone&startdatetime=20200101000000&enddatetime=20200301000000", 300)
show("cboe VIX history", "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv", 200)
show("treasury yields 2026", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv", 400)
show("treasury yields 2020", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2020/all?type=daily_treasury_yield_curve&field_tdr_date_value=2020&page&_format=csv", 200)
show("epu daily", "https://www.policyuncertainty.com/media/All_Daily_Policy_Data.csv", 200)
for f in ("data_gpr_daily_recent.xlsx", "data_gpr_export.xlsx"):
    show(f"gpr {f}", "https://www.matteoiacoviello.com/gpr_files/" + f, 80)
show("fred VIXCLS txt", "https://fred.stlouisfed.org/data/VIXCLS.txt", 200)
show("fred VIXCLS csv cosd", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd=2025-01-01", 200)
Y = "https://query1.finance.yahoo.com/v8/finance/chart/"
for s in ("%5EVIX", "DX-Y.NYB", "%5ETNX"):
    try:
        r = get(Y + s + "?range=10y&interval=1d"); j = r.json()["chart"]["result"][0]
        ts, cl = j["timestamp"], j["indicators"]["quote"][0]["close"]
        print(f"HOLYP yahoo {s}: {r.status_code} rows={len(ts)} first={ts[0]},{cl[0]} last={ts[-1]},{cl[-1]}", flush=True)
    except Exception as e:
        print(f"HOLYP yahoo {s}: ERROR {type(e).__name__}: {e}", flush=True)
    time.sleep(1.5)
# OKX: how deep does the paginated contract long/short ratio go?
O = "https://www.okx.com/api/v5/rubik/stat"
for inst in ("BTC-USDT-SWAP", "XRP-USDT-SWAP"):
    for ep in ("long-short-account-ratio-contract", "long-short-account-ratio-contract-top-trader", "long-short-position-ratio-contract-top-trader"):
        end, rows, pages = None, 0, 0
        oldest = None
        while pages < 30:
            u = f"{O}/contracts/{ep}?instId={inst}&period=1D&limit=100" + (f"&end={end}" if end else "")
            try:
                d = get(u).json().get("data") or []
            except Exception as e:
                print(f"HOLYP okx {ep} {inst}: ERROR {e}", flush=True); break
            d = [x for x in d if float(x[1] or 0) > 0]
            if not d:
                break
            rows += len(d); pages += 1
            oldest = int(d[-1][0]); end = oldest - 1
            time.sleep(0.25)
        print(f"HOLYP okx {ep} {inst} 1D: rows={rows} pages={pages} oldest={time.strftime('%Y-%m-%d', time.gmtime((oldest or 0) / 1000))}", flush=True)
    # taker contract: depth
    end, rows, pages, oldest = None, 0, 0, None
    while pages < 30:
        u = f"{O}/taker-volume-contract?instId={inst}&period=1D&limit=100" + (f"&end={end}" if end else "")
        d = [x for x in (get(u).json().get("data") or []) if float(x[1] or 0) + float(x[2] or 0) > 0]
        if not d:
            break
        rows += len(d); pages += 1; oldest = int(d[-1][0]); end = oldest - 1
        time.sleep(0.25)
    print(f"HOLYP okx taker-volume-contract {inst} 1D: rows={rows} oldest={time.strftime('%Y-%m-%d', time.gmtime((oldest or 0) / 1000))}", flush=True)
# OKX options: put/call open interest + volume by expiry/strike? (for history: only the 72-day endpoint)
show("okx option taker-block-volume BTC", f"{O}/option/taker-block-volume?ccy=BTC&period=1D", 200)
# Deribit DVOL: paginate with continuation to the start
end, rows, first = NOW, 0, None
for _ in range(10):
    j = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&start_timestamp=1577836800000&end_timestamp={end}&resolution=1D").json()["result"]
    d = j.get("data") or []
    if not d:
        break
    rows += len(d); first = d[0][0]
    c = j.get("continuation")
    if not c:
        break
    end = int(c)
    time.sleep(0.5)
print(f"HOLYP deribit dvol BTC 1D total rows={rows} first={time.strftime('%Y-%m-%d', time.gmtime((first or 0) / 1000))}", flush=True)
show("coinmetrics MVRV xrp,ltc,doge,ada,link,bnb", "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=xrp,ltc,doge,ada,link&metrics=CapMVRVCur&frequency=1d&page_size=3", 300)
show("coinmetrics catalog btc", "https://community-api.coinmetrics.io/v4/catalog-v2/asset-metrics?assets=btc&page_size=200", 200)
print("HOLYP done", flush=True)
