# 🔎 v3.33.0: probe #3 — DXY from ECB rates (Frankfurter) · GPR daily via the dashboard's own Stata reader · MVRV per coin (CoinMetrics)
#   Public GETs only · no keys · no orders · no notifications. ⇒ lines HOLYP
import json, time, math, requests, datetime as dt
H = {"User-Agent": "Mozilla/5.0 (HolyDashboard probe)"}
def _dta_read(b, want=None):
    """📦 قارئ ملفات Stata 118/119 (dta) بلا مكتبات — يرجع {اسم المتغير: [القيم]} للأرقام فقط (المفقود None)"""
    import struct
    if not b.startswith(b"<stata_dta><header><release>"):
        return None
    rel = int(b[28:31])
    if rel not in (118, 119):
        return None
    le = b"<byteorder>LSF" in b[:80]
    E = "<" if le else ">"
    p = b.index(b"<K>") + 3
    K = struct.unpack(E + ("I" if rel == 119 else "H"), b[p:p + (4 if rel == 119 else 2)])[0]
    p = b.index(b"<N>") + 3
    N = struct.unpack(E + "Q", b[p:p + 8])[0]
    p = b.index(b"<map>") + 5
    mp = struct.unpack(E + "14Q", b[p:p + 112])
    p = mp[2] + len(b"<variable_types>")
    ty = struct.unpack(E + f"{K}H", b[p:p + 2 * K])
    p = mp[3] + len(b"<varnames>")
    names = [b[p + 129 * i:p + 129 * (i + 1)].split(b"\x00")[0].decode("utf-8", "replace") for i in range(K)]
    fmt = {65526: ("d", 8), 65527: ("f", 4), 65528: ("i", 4), 65529: ("h", 2), 65530: ("b", 1), 32768: (None, 8)}
    lay, off = [], 0
    for t in ty:
        f, w = fmt.get(t, (None, t if t <= 2045 else 8))
        lay.append((f, w, off))
        off += w
    miss = {"d": 8.988465674311579e307, "f": 1.7014117e38, "i": 2147483620, "h": 32740, "b": 100}
    out = {}
    base = mp[9] + len(b"<data>")
    for j, nm in enumerate(names):
        f, w, o = lay[j]
        if f is None or (want and nm not in want):
            continue
        col = []
        st = struct.Struct(E + f)
        for r in range(N):
            v = st.unpack_from(b, base + r * off + o)[0]
            col.append(None if v >= miss[f] else v)
        out[nm] = col
    return out


def j(url, t=40):
    r = requests.get(url, headers=H, timeout=t)
    return r.status_code, r
for url in ("https://api.frankfurter.app/2026-09-01..?from=USD&to=EUR,JPY,GBP,CAD,SEK,CHF",
            "https://api.frankfurter.dev/v1/2026-09-01..?base=USD&symbols=EUR,JPY,GBP,CAD,SEK,CHF",
            "https://api.frankfurter.app/2015-01-01..2015-03-01?from=USD&to=EUR,JPY,GBP,CAD,SEK,CHF"):
    try:
        c, r = j(url); d = r.json(); rt = d.get("rates") or {}
        ks = sorted(rt)
        last = rt[ks[-1]] if ks else {}
        dxy = None
        if last:
            dxy = 50.14348112 * (1 / last["EUR"]) ** -0.576 * last["JPY"] ** 0.136 * (1 / last["GBP"]) ** -0.119 * last["CAD"] ** 0.091 * last["SEK"] ** 0.042 * last["CHF"] ** 0.036
        print(f"HOLYP frankfurter {url[8:40]}: {c} days={len(ks)} first={ks[0] if ks else '-'} last={ks[-1] if ks else '-'} {last} DXY≈{dxy}", flush=True)
    except Exception as e:
        print(f"HOLYP frankfurter {url[8:40]}: ERROR {type(e).__name__}: {e}", flush=True)
    time.sleep(1)
try:
    c, r = j("https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.dta", 60)
    d = _dta_read(r.content)
    print(f"HOLYP gpr dta: {c} {len(r.content)}B vars={list(d.keys()) if d else None}", flush=True)
    if d:
        dk = "date" if "date" in d else list(d.keys())[0]
        n = len(d[dk])
        for i in (0, n - 3, n - 2, n - 1):
            row = {k: d[k][i] for k in d}
            dd = row.get(dk)
            print(f"HOLYP gpr row {i}: {row} ⇒ {dt.date(1960,1,1) + dt.timedelta(days=int(dd)) if dd is not None and dd < 40000 else dd}", flush=True)
except Exception as e:
    print(f"HOLYP gpr dta: ERROR {type(e).__name__}: {e}", flush=True)
for a in ("btc", "eth", "sol", "xrp", "doge", "ada", "bnb", "ltc", "link", "trx", "avax", "dot", "bch", "etc", "xlm", "atom", "fil", "uni", "near", "aave"):
    try:
        c, r = j(f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={a}&metrics=CapMVRVCur&frequency=1d&page_size=10000&start_time=2019-01-01")
        d = (r.json().get("data") or []) if c == 200 else []
        print(f"HOLYP mvrv {a}: {c} rows={len(d)} first={d[0]['time'][:10] if d else '-'} last={(d[-1]['time'][:10] + ' ' + d[-1]['CapMVRVCur'][:5]) if d else '-'}", flush=True)
    except Exception as e:
        print(f"HOLYP mvrv {a}: ERROR {e}", flush=True)
    time.sleep(0.7)
time.sleep(30)
try:
    c, r = j("https://api.gdeltproject.org/api/v2/doc/doc?format=json&mode=timelinetone&timespan=3months&query=bitcoin")
    print(f"HOLYP gdelt single after 30s: {c} {r.text[:300]!r}", flush=True)
except Exception as e:
    print(f"HOLYP gdelt: ERROR {e}", flush=True)
print("HOLYP done", flush=True)
