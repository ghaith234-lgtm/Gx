# 🔎 v3.33.0: probe the public sources planned for the new indicators (GitHub runner — the dev sandbox cannot reach them).
#   Public GETs only · no keys · no orders · no notifications. Prints status, size, how far back the history goes, first/last rows.
#   python3 ci/x33_probe.py  ⇒ lines starting with HOLYP
import json, time, requests
NOW = int(time.time() * 1000); DAY = 86400000
H = {"User-Agent": "Mozilla/5.0 (HolyDashboard probe)"}
def show(tag, url, n=420):
    try:
        r = requests.get(url, headers=H, timeout=40)
        b = r.text
        info = ""
        try:
            j = r.json()
            d = j.get("data") if isinstance(j, dict) else j
            if isinstance(d, dict) and "data" in d: d = d["data"]
            if isinstance(j, dict) and "result" in j:
                d = j["result"]; d = d.get("data", d) if isinstance(d, dict) else d
            if isinstance(j, dict) and "timeline" in j:
                tl = j["timeline"]; d = (tl[0].get("data") if tl else [])
            if isinstance(d, list):
                info = f" rows={len(d)} first={json.dumps(d[0])[:160] if d else '-'} last={json.dumps(d[-1])[:160] if d else '-'}"
        except Exception:
            lines = b.strip().splitlines()
            info = f" lines={len(lines)} first={lines[1][:80] if len(lines) > 1 else '-'} last={lines[-1][:80] if lines else '-'}"
        print(f"HOLYP {tag}: {r.status_code} {r.headers.get('content-type','')[:40]} {len(b)}B{info}", flush=True)
        print(f"HOLYP {tag} body: {b[:n]!r}", flush=True)
    except Exception as e:
        print(f"HOLYP {tag}: ERROR {type(e).__name__}: {e}", flush=True)
    time.sleep(1.2)
O = "https://www.okx.com/api/v5/rubik/stat"
show("okx support-coin", f"{O}/trading-data/support-coin", 900)
for p in ("5m", "1H", "1D"):
    show(f"okx ls-account ccy BTC {p}", f"{O}/contracts/long-short-account-ratio?ccy=BTC&period={p}")
show("okx ls-account ccy BTC 1D old (end=-400d)", f"{O}/contracts/long-short-account-ratio?ccy=BTC&period=1D&end={NOW - 400 * DAY}")
show("okx ls-account ccy XRP 1D", f"{O}/contracts/long-short-account-ratio?ccy=XRP&period=1D")
show("okx ls-account-contract BTC 1D", f"{O}/contracts/long-short-account-ratio-contract?instId=BTC-USDT-SWAP&period=1D&limit=100")
show("okx ls-account-contract BTC 1D old", f"{O}/contracts/long-short-account-ratio-contract?instId=BTC-USDT-SWAP&period=1D&limit=100&end={NOW - 300 * DAY}")
show("okx ls-top-trader-acct BTC 1D", f"{O}/contracts/long-short-account-ratio-contract-top-trader?instId=BTC-USDT-SWAP&period=1D&limit=100")
show("okx ls-top-trader-pos BTC 1D", f"{O}/contracts/long-short-position-ratio-contract-top-trader?instId=BTC-USDT-SWAP&period=1D&limit=100")
show("okx taker SPOT BTC 1D", f"{O}/taker-volume?ccy=BTC&instType=SPOT&period=1D")
show("okx taker CONTRACTS BTC 1D", f"{O}/taker-volume?ccy=BTC&instType=CONTRACTS&period=1D")
show("okx taker CONTRACTS BTC 1D old", f"{O}/taker-volume?ccy=BTC&instType=CONTRACTS&period=1D&end={NOW - 400 * DAY}")
show("okx taker-contract BTC 1D", f"{O}/taker-volume-contract?instId=BTC-USDT-SWAP&period=1D&limit=100")
show("okx taker-contract BTC 1D old", f"{O}/taker-volume-contract?instId=BTC-USDT-SWAP&period=1D&limit=100&end={NOW - 300 * DAY}")
show("okx option oi-vol-ratio BTC 1D", f"{O}/option/open-interest-volume-ratio?ccy=BTC&period=1D")
show("okx option oi-vol-ratio BTC 1D old", f"{O}/option/open-interest-volume-ratio?ccy=BTC&period=1D&end={NOW - 400 * DAY}")
show("okx option oi-vol-ratio ETH 1D", f"{O}/option/open-interest-volume-ratio?ccy=ETH&period=1D")
show("okx option oi-vol BTC 1D", f"{O}/option/open-interest-volume?ccy=BTC&period=1D")
show("okx contracts oi-vol BTC 1D", f"{O}/contracts/open-interest-volume?ccy=BTC&period=1D")
D = "https://www.deribit.com/api/v2/public"
show("deribit dvol BTC 1D since 2021", f"{D}/get_volatility_index_data?currency=BTC&start_timestamp=1609459200000&end_timestamp={NOW}&resolution=1D")
show("deribit dvol BTC 3600 last", f"{D}/get_volatility_index_data?currency=BTC&start_timestamp={NOW - 3 * DAY}&end_timestamp={NOW}&resolution=3600")
show("deribit dvol ETH 1D", f"{D}/get_volatility_index_data?currency=ETH&start_timestamp={NOW - 30 * DAY}&end_timestamp={NOW}&resolution=1D")
show("deribit book options BTC", f"{D}/get_book_summary_by_currency?currency=BTC&kind=option", 300)
C = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
show("coinmetrics MVRV btc,eth", f"{C}?assets=btc,eth&metrics=CapMVRVCur&frequency=1d&page_size=5")
show("coinmetrics MVRV btc since 2018", f"{C}?assets=btc&metrics=CapMVRVCur&frequency=1d&page_size=10000&start_time=2018-01-01")
show("coinmetrics MVRV alts", f"{C}?assets=xrp,sol,doge,ada,ltc,link,bnb,trx&metrics=CapMVRVCur&frequency=1d&page_size=5")
show("ff calendar this week", "https://nfs.faireconomy.media/ff_calendar_thisweek.json", 700)
show("ff calendar next week", "https://nfs.faireconomy.media/ff_calendar_nextweek.json", 300)
F = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
for s in ("VIXCLS", "DTWEXBGS", "DGS10", "USEPUINDXD", "T10Y2Y", "DEXUSEU"):
    show(f"fred {s}", F + s, 200)
G = "https://www.matteoiacoviello.com/gpr_files/"
for f in ("data_gpr_daily_recent.xls", "data_gpr_daily_recent.csv", "data_gpr_export.xls", "data_gpr_export.csv", "data_gpr_daily_recent.dta"):
    show(f"gpr {f}", G + f, 120)
GD = "https://api.gdeltproject.org/api/v2/doc/doc?format=json&query=%28bitcoin%20OR%20cryptocurrency%20OR%20crypto%29"
show("gdelt tone 3months", GD + "&mode=timelinetone&timespan=3months")
time.sleep(6)
show("gdelt volraw 3months", GD + "&mode=timelinevolraw&timespan=3months")
time.sleep(6)
show("gdelt tone since 2020", GD + "&mode=timelinetone&startdatetime=20200101000000&enddatetime=20201231000000")
time.sleep(6)
show("gdelt tone 1y", GD + "&mode=timelinetone&timespan=1y")
show("yahoo DXY", "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=1mo&interval=1d", 300)
print("HOLYP done", flush=True)
