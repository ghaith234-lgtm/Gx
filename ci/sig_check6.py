# 🔬 sixth pass — the owner (20-11) sent gunbot.com/features (36 signal systems) and asked: «اني اريد اتضيف كل الاشارات واتسوي فحص
#   واتشوف واتسويه اشارة وحده». Every system written from its public description (standard indicators — no code copied), measured on REAL
#   OKX prices before anything reaches the dashboard (GitHub · public data · no keys · no orders · no notifications):
#   · 28 coins · 1-hour (~1 year) · 4-hour (~2 years) · daily (~3 years) candles · every signal sees only the candles before it
#   · a BUY = the system's long entry · a SELL = the same system on the mirrored price (1/price: up ⇄ down — the exact mirror)
#   · judged after a fixed time (1H: 4 · 12 · 24 candles · 4H: 3 · 6 · 18 · 1D: 1 · 3 · 7) · net after 0.2% fees (0.1% in + 0.1% out)
#   · compared with ANY candle of the same coin and time (the «random» entry) · the first 60% of time to learn · the last 40% apart (test)
#   · one signal from all of them: each system's weight = its edge on the first 60% only · the vote of every system that fired in the last
#     few candles · judged on the last 40% · and a «families» vote (trend · momentum · volatility · pattern/levels · volume)
#   python3 ci/sig_check6.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYSIG6
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "BNB-USDT", "LTC-USDT", "LINK-USDT", "TRX-USDT",
         "AVAX-USDT", "DOT-USDT", "BCH-USDT", "ETC-USDT", "XLM-USDT", "ATOM-USDT", "FIL-USDT", "UNI-USDT", "NEAR-USDT", "AAVE-USDT",
         "SUI-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "HBAR-USDT", "ICP-USDT", "INJ-USDT", "SHIB-USDT"]
TFS = {"1H": (8760, (4, 12, 24), 24), "4H": (4400, (3, 6, 18), 6), "1Dutc": (1100, (1, 3, 7), 5)}   # (candles · horizons · a «day» block)
if FAKE:
    COINS = COINS[:3]
    TFS = {"1H": (1500, (4, 12, 24), 24), "4H": (900, (3, 6, 18), 6), "1Dutc": (500, (1, 3, 7), 5)}
FEE = 0.002
R = tempfile.mkdtemp(prefix="sig6_real_")
json.dump({"port": 8112}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))


def P_(*a):
    print("HOLYSIG6", *a, flush=True)


if FAKE:
    _SER = {}

    def _series(sym, bar):
        k = (sym, bar)
        if k not in _SER:
            dt = {"1H": 3600, "4H": 14400, "1Dutc": 86400}[bar]
            n = TFS[bar][0] + 50
            rnd = random.Random(hash(k) % 1000)
            t1 = int(time.time()) // dt * dt
            p, out = 1.0 + rnd.random(), []
            for i in range(n):
                o = p; p = max(1e-6, p * math.exp(rnd.gauss(0, 0.01 * math.sqrt(dt / 3600))))
                out.append([t1 - (n - 1 - i) * dt, o, max(o, p) * 1.003, min(o, p) * 0.997, p, 1000 * (1 + rnd.random())])
            _SER[k] = out
        return _SER[k]

    def _fake_pub(path):
        import urllib.parse as up
        q = dict(up.parse_qsl(path.split("?", 1)[1])) if "?" in path else {}
        if "candles" not in path:
            return None
        s = _series(q["instId"], q["bar"])
        after = int(q.get("after") or 0) // 1000
        rows = [r for r in s if (not after or r[0] < after)][-int(q.get("limit") or 100):]
        return {"code": "0", "data": [[str(r[0] * 1000), repr(r[1]), repr(r[2]), repr(r[3]), repr(r[4]), repr(r[5]), "0", "0", "1"] for r in reversed(rows)]}
    m._okx_pub = _fake_pub
    m._http_json = lambda *a, **k: None


def hist(sym, bar, maxn):
    rows = {}
    for c in m._fc_okx_rows(sym, bar, hist=False, limit=100):
        if c[6]:
            rows[c[0]] = c[:6]
    oldest = min(rows) if rows else None
    while oldest and len(rows) < maxn:
        pg = [c for c in m._fc_okx_rows(sym, bar, after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
        if not pg:
            break
        for c in pg:
            rows[c[0]] = c[:6]
        oldest = min(rows)
        if not FAKE:
            time.sleep(0.11)
    return [rows[k] for k in sorted(rows)][-maxn:]


# ───────────────────────── indicators (oldest → newest · None until enough candles) ─────────────────────────
def sma(x, n):
    out, s, q = [None] * len(x), 0.0, 0
    for i, v in enumerate(x):
        if v is None:
            s, q = 0.0, 0; continue
        s += v; q += 1
        if q > n:
            s -= x[i - n]; q = n
        if q == n:
            out[i] = s / n
    return out


def ema(x, n):
    out, a, e, buf = [None] * len(x), 2.0 / (n + 1), None, []
    for i, v in enumerate(x):
        if v is None:
            continue
        if e is None:
            buf.append(v)
            if len(buf) == n:
                e = sum(buf) / n; out[i] = e
            continue
        e = e + a * (v - e); out[i] = e
    return out


def rma(x, n):
    out, e, buf = [None] * len(x), None, []
    for i, v in enumerate(x):
        if v is None:
            continue
        if e is None:
            buf.append(v)
            if len(buf) == n:
                e = sum(buf) / n; out[i] = e
            continue
        e = (e * (n - 1) + v) / n; out[i] = e
    return out


def rsi(c, n=14):
    up = [None] + [max(c[i] - c[i - 1], 0.0) if c[i] is not None and c[i - 1] is not None else None for i in range(1, len(c))]
    dn = [None] + [max(c[i - 1] - c[i], 0.0) if c[i] is not None and c[i - 1] is not None else None for i in range(1, len(c))]
    au, ad = rma(up, n), rma(dn, n)
    return [None if a is None or b is None else (100.0 if b == 0 else 100.0 - 100.0 / (1.0 + a / b)) for a, b in zip(au, ad)]


def macd(c, f=12, s=26, g=9):
    ef, es = ema(c, f), ema(c, s)
    ln = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    sg = ema(ln, g)
    return ln, sg, [None if a is None or b is None else a - b for a, b in zip(ln, sg)]


def true_range(D):
    H, L, C = D["H"], D["L"], D["C"]
    return [H[0] - L[0]] + [max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])) for i in range(1, len(C))]


def adx(D, n=14):
    H, L = D["H"], D["L"]
    tr = true_range(D)
    pdm = [0.0] + [(H[i] - H[i - 1]) if (H[i] - H[i - 1]) > (L[i - 1] - L[i]) and (H[i] - H[i - 1]) > 0 else 0.0 for i in range(1, len(H))]
    ndm = [0.0] + [(L[i - 1] - L[i]) if (L[i - 1] - L[i]) > (H[i] - H[i - 1]) and (L[i - 1] - L[i]) > 0 else 0.0 for i in range(1, len(H))]
    a, p, q = rma(tr, n), rma(pdm, n), rma(ndm, n)
    pdi = [None if x is None or y is None or x == 0 else 100 * y / x for x, y in zip(a, p)]
    ndi = [None if x is None or y is None or x == 0 else 100 * y / x for x, y in zip(a, q)]
    dx = [None if x is None or y is None or x + y == 0 else 100 * abs(x - y) / (x + y) for x, y in zip(pdi, ndi)]
    return rma(dx, n), pdi, ndi


def supertrend(D, n=10, k=3.0):
    H, L, C = D["H"], D["L"], D["C"]
    at = rma(true_range(D), n)
    d, line = [None] * len(C), [None] * len(C)
    fu = fl = None; dr = 1
    for i in range(len(C)):
        if at[i] is None:
            continue
        hl = (H[i] + L[i]) / 2
        bu, bl = hl + k * at[i], hl - k * at[i]
        if fu is None:
            fu, fl = bu, bl
        else:
            fu = bu if (bu < fu or C[i - 1] > fu) else fu
            fl = bl if (bl > fl or C[i - 1] < fl) else fl
        if dr == 1 and C[i] < fl:
            dr = -1
        elif dr == -1 and C[i] > fu:
            dr = 1
        d[i], line[i] = dr, (fl if dr == 1 else fu)
    return d, line


def boll(c, n=20, k=2.0):
    mid = sma(c, n)
    up, lo = [None] * len(c), [None] * len(c)
    for i in range(len(c)):
        if mid[i] is None:
            continue
        w = c[i - n + 1:i + 1]
        sd = math.sqrt(sum((x - mid[i]) ** 2 for x in w) / n)
        up[i], lo[i] = mid[i] + k * sd, mid[i] - k * sd
    return mid, up, lo


def keltner(D, n=20, k=2.0, an=10):
    mid, at = ema(D["C"], n), rma(true_range(D), an)
    return mid, [None if a is None or b is None else a + k * b for a, b in zip(mid, at)], [None if a is None or b is None else a - k * b for a, b in zip(mid, at)]


def psar(D, st=0.02, mx=0.2):
    H, L = D["H"], D["L"]
    n = len(H)
    sar, dr = [None] * n, [None] * n
    if n < 3:
        return sar, dr
    up = H[1] >= H[0]; af = st; ep = H[1] if up else L[1]; s = L[0] if up else H[0]
    for i in range(2, n):
        s = s + af * (ep - s)
        if up:
            s = min(s, L[i - 1], L[i - 2])
            if L[i] < s:
                up, s, ep, af = False, ep, L[i], st
            elif H[i] > ep:
                ep, af = H[i], min(mx, af + st)
        else:
            s = max(s, H[i - 1], H[i - 2])
            if H[i] > s:
                up, s, ep, af = True, ep, H[i], st
            elif L[i] < ep:
                ep, af = L[i], min(mx, af + st)
        sar[i], dr[i] = s, (1 if up else -1)
    return sar, dr


def cci(D, n=20):
    tp = [(h + l + c) / 3 for h, l, c in zip(D["H"], D["L"], D["C"])]
    ma = sma(tp, n)
    out = [None] * len(tp)
    for i in range(len(tp)):
        if ma[i] is None:
            continue
        md = sum(abs(x - ma[i]) for x in tp[i - n + 1:i + 1]) / n
        out[i] = 0.0 if md == 0 else (tp[i] - ma[i]) / (0.015 * md)
    return out


def stoch_raw(H, L, C, n):
    out = [None] * len(C)
    for i in range(n - 1, len(C)):
        if any(v is None for v in (C[i],)) or any(x is None for x in H[i - n + 1:i + 1]) or any(x is None for x in L[i - n + 1:i + 1]):
            continue
        hh, ll = max(H[i - n + 1:i + 1]), min(L[i - n + 1:i + 1])
        out[i] = 50.0 if hh == ll else 100 * (C[i] - ll) / (hh - ll)
    return out


def stoch(D, n=14, ks=3, ds=3):
    k = sma(stoch_raw(D["H"], D["L"], D["C"], n), ks)
    return k, sma(k, ds)


def stochrsi(c, rn=14, sn=14, ks=3, ds=3):
    r = rsi(c, rn)
    k = sma(stoch_raw(r, r, r, sn), ks)
    return k, sma(k, ds)


def ao(D):
    md = [(h + l) / 2 for h, l in zip(D["H"], D["L"])]
    a, b = sma(md, 5), sma(md, 34)
    return [None if x is None or y is None else x - y for x, y in zip(a, b)]


def willr(D, n=14):
    s = stoch_raw(D["H"], D["L"], D["C"], n)
    return [None if v is None else v - 100.0 for v in s]


def lsma(c, n=25):
    out = [None] * len(c)
    xs = list(range(n)); mx = (n - 1) / 2; vx = sum((x - mx) ** 2 for x in xs)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1:i + 1]
        my = sum(w) / n
        b = sum((x - mx) * (y - my) for x, y in zip(xs, w)) / vx
        out[i] = my + b * (n - 1 - mx)
    return out


def dss(D, n=13, e=8):
    s1 = stoch_raw(D["H"], D["L"], D["C"], n)
    e1 = ema(s1, e)
    s2 = stoch_raw(e1, e1, e1, n)
    return ema(s2, e)


def fractals(H, L, k=2):
    hi, lo = [False] * len(H), [False] * len(L)
    for i in range(k, len(H) - k):
        if all(H[i] > H[j] for j in range(i - k, i)) and all(H[i] >= H[j] for j in range(i + 1, i + k + 1)):   # a tie on the right side counts
            hi[i] = True
        if all(L[i] < L[j] for j in range(i - k, i)) and all(L[i] <= L[j] for j in range(i + 1, i + k + 1)):
            lo[i] = True
    return hi, lo       # a fractal at i is known only at i + k


def pivots_prev(D, blk):
    """classic pivot of the previous «day» (block of blk candles): P · R1 · S1 — known from the block's first candle"""
    H, L, C = D["H"], D["L"], D["C"]
    n = len(C)
    P, R1, S1 = [None] * n, [None] * n, [None] * n
    for i in range(blk * 2, n):
        b0 = (i // blk) * blk
        a = b0 - blk
        if a < 0:
            continue
        hh, ll, cc = max(H[a:b0]), min(L[a:b0]), C[b0 - 1]
        p = (hh + ll + cc) / 3
        P[i], R1[i], S1[i] = p, 2 * p - ll, 2 * p - hh
    return P, R1, S1


def rising(x, i, k=1):
    return i - k >= 0 and x[i] is not None and x[i - k] is not None and x[i] > x[i - k]


def xup(a, b, i):
    """a crosses above b at i (b may be a number)"""
    if i < 1:
        return False
    a0, a1 = a[i - 1], a[i]
    b0, b1 = (b, b) if isinstance(b, (int, float)) else (b[i - 1], b[i])
    return None not in (a0, a1, b0, b1) and a0 <= b0 and a1 > b1


def ok(*v):
    return all(x is not None for x in v)


# ───────────────────────── the systems (BUY events · the SELL = the same on the mirrored price) ─────────────────────────
def build(D):
    """every series the systems need — once per coin and time frame"""
    C, H, L, O, V = D["C"], D["H"], D["L"], D["O"], D["V"]
    S = {}
    for n in (3, 5, 8, 9, 10, 12, 13, 15, 20, 21, 25, 30, 34, 35, 40, 45, 50, 60, 100, 150, 200):
        S[f"e{n}"] = ema(C, n)
    for n in (20, 50, 100):
        S[f"s{n}"] = sma(C, n)
    S["rsi"] = rsi(C, 14)
    S["rsioma"] = rsi(ema(C, 14), 14); S["rsioma_ma"] = ema(S["rsioma"], 14)
    S["ml"], S["ms"], S["mh"] = macd(C)
    S["ml2"], S["ms2"], S["mh2"] = macd(C, 15, 26, 9)
    S["adx"], S["pdi"], S["ndi"] = adx(D)
    S["st"], S["stl"] = supertrend(D)
    S["bm"], S["bu"], S["bl"] = boll(C, 20, 2.0)
    S["bm25"], S["bu25"], S["bl25"] = boll(C, 20, 2.5)
    S["km"], S["ku"], S["kl"] = keltner(D)
    S["sar"], S["sard"] = psar(D)
    S["cci14"], S["cci50"], S["cci20"] = cci(D, 14), cci(D, 50), cci(D, 20)
    S["k"], S["d"] = stoch(D)
    S["kma"] = sma(S["k"], 9)
    S["srk"], S["srd"] = stochrsi(C)
    S["ao"] = ao(D)
    S["mom10"] = [None] + [None] * 9 + [C[i] - C[i - 10] for i in range(10, len(C))]
    S["mom14"] = [None] * 14 + [C[i] - C[i - 14] for i in range(14, len(C))]
    S["wr"] = willr(D)
    S["ghh"], S["ghl"] = sma(H, 10), sma(L, 10)
    S["lsma"] = lsma(C, 25)
    S["dss"] = dss(D)
    S["atr"] = rma(true_range(D), 14)
    S["v20"] = sma(V, 20)
    S["fh"], S["fl"] = fractals(H, L, 2)
    S["fh3"], S["fl3"] = fractals(H, L, 3)
    S["P"], S["R1"], S["S1"] = pivots_prev(D, D["blk"])
    S["hh10"] = [None] * 10 + [max(H[i - 10:i]) for i in range(10, len(H))]
    return S


def gmma_up(S, i):
    sh = [S[f"e{n}"][i] for n in (3, 5, 8, 10, 12, 15)]
    lg = [S[f"e{n}"][i] for n in (30, 35, 40, 45, 50, 60)]
    return None not in sh + lg and min(sh) > max(lg)


def engulf_up(D, i):
    O, C = D["O"], D["C"]
    return i >= 1 and C[i - 1] < O[i - 1] and C[i] > O[i] and C[i] >= O[i - 1] and O[i] <= C[i - 1]


def hammer(D, i):
    O, H, L, C = D["O"][i], D["H"][i], D["L"][i], D["C"][i]
    body = abs(C - O); rng = H - L
    return rng > 0 and body <= rng * 0.35 and min(O, C) - L >= 2 * body and H - max(O, C) <= body


def ev_first(cond, n):
    """edge-triggered: the candle where the condition becomes true"""
    out, prev = [], False
    for i in range(n):
        c = bool(cond(i))
        if c and not prev:
            out.append(i)
        prev = c
    return out


SYS = {}   # code → (name, family, fn(D, S) → list of buy candles)


def sysdef(code, name, fam):
    def deco(fn):
        SYS[code] = (name, fam, fn)
        return fn
    return deco


@sysdef("08", "Double CCI + RSIOMA", "momentum")
def s08(D, S):
    return ev_first(lambda i: ok(S["cci14"][i], S["cci50"][i], S["rsioma"][i], S["rsioma_ma"][i]) and S["cci14"][i] > 0 and S["cci50"][i] > 0
                    and S["rsioma"][i] > S["rsioma_ma"][i] and S["rsioma"][i] > 50, D["n"])


@sysdef("09", "Scalp with EMA Predictive", "trend")
def s09(D, S):
    return [i for i in range(D["n"]) if xup(S["e5"], S["e13"], i) and rising(S["e34"], i, 3)]


@sysdef("10", "Neptune (BB · EMA · AO)", "momentum")
def s10(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(C, S["bm"], i) and ok(S["e50"][i], S["ao"][i]) and C[i] > S["e50"][i] and S["ao"][i] > 0 and rising(S["ao"], i)]


@sysdef("11", "Hybrid FX Framework", "momentum")
def s11(D, S):
    return [i for i in range(D["n"]) if xup(S["rsi"], 50, i) and ok(S["e21"][i], S["e50"][i], S["mom10"][i]) and S["e21"][i] > S["e50"][i] and S["mom10"][i] > 0]


@sysdef("12", "SuperTrend + EMA 150", "trend")
def s12(D, S):
    C = D["C"]
    return [i for i in range(1, D["n"]) if S["st"][i] == 1 and S["st"][i - 1] == -1 and ok(S["e150"][i]) and C[i] > S["e150"][i]]


@sysdef("13", "EMA Bands / Guppy", "trend")
def s13(D, S):
    return ev_first(lambda i: gmma_up(S, i), D["n"])


@sysdef("14", "Bollinger + RSI + ADX (reversion)", "volatility")
def s14(D, S):
    C = D["C"]
    return [i for i in range(1, D["n"]) if ok(S["bl"][i - 1], S["adx"][i]) and C[i - 1] < S["bl"][i - 1] and xup(S["rsi"], 30, i) and S["adx"][i] < 25]


@sysdef("15", "Keltner + EMA (breakout)", "volatility")
def s15(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(C, S["ku"], i) and ok(S["e50"][i]) and C[i] > S["e50"][i]]


@sysdef("16", "Parabolic SAR + Fibonacci", "pattern")
def s16(D, S):
    H, L, C = D["H"], D["L"], D["C"]
    out, n = [], D["n"]
    for i in range(30, n):
        if not (S["sard"][i] == 1 and S["sard"][i - 1] == -1):
            continue
        lo = min(L[i - 20:i + 1])
        for j in range(i + 1, min(n, i + 11)):
            hi = max(H[i:j + 1])
            if hi <= lo:
                break
            f38, f62 = hi - 0.382 * (hi - lo), hi - 0.618 * (hi - lo)
            if L[j] <= f38 and L[j] >= f62 and C[j] > D["O"][j]:
                out.append(j); break
            if L[j] < f62:
                break
    return sorted(set(out))


@sysdef("17", "Levels + GMMA slow filter", "pattern")
def s17(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(C, S["R1"], i) and ok(S["e30"][i], S["e60"][i]) and S["e30"][i] > S["e60"][i] and rising(S["e30"], i)]


@sysdef("18", "Bollinger Band extreme scalp", "volatility")
def s18(D, S):
    C = D["C"]
    return [i for i in range(1, D["n"]) if ok(S["bl25"][i - 1], S["bl25"][i]) and C[i - 1] < S["bl25"][i - 1] and C[i] > S["bl25"][i]]


@sysdef("19", "Keltner scalping (MACD · stoch)", "volatility")
def s19(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(C, S["km"], i) and ok(S["s50"][i], S["mh"][i], S["k"][i], S["d"][i]) and C[i] > S["s50"][i]
            and S["mh"][i] > 0 and S["k"][i] > S["d"][i]]


@sysdef("20", "Scalp pattern (engulfing)", "pattern")
def s20(D, S):
    return [i for i in range(D["n"]) if engulf_up(D, i)]


@sysdef("21", "Anti (stochastic over its MA)", "momentum")
def s21(D, S):
    return [i for i in range(D["n"]) if xup(S["k"], S["kma"], i) and S["k"][i - 1] is not None and S["k"][i - 1] < 30]


@sysdef("22", "Extreme scalping modified", "momentum")
def s22(D, S):
    C = D["C"]
    def cnd(i):
        return (i >= 1 and ok(S["ghh"][i - 1], S["dss"][i], S["dss"][i - 1], S["lsma"][i], S["mom10"][i]) and C[i] > S["ghh"][i - 1]
                and S["dss"][i] > S["dss"][i - 1] and C[i] > S["lsma"][i] and S["mom10"][i] > 0)
    return ev_first(cnd, D["n"])


@sysdef("23", "Action trade (double CCI · ribbon)", "momentum")
def s23(D, S):
    return ev_first(lambda i: ok(S["cci14"][i], S["cci50"][i], S["e8"][i], S["e13"][i], S["e21"][i]) and S["cci14"][i] > 0 and S["cci50"][i] > 0
                    and S["e8"][i] > S["e13"][i] > S["e21"][i], D["n"])


@sysdef("24", "1-candle scalper (EMA · Stoch RSI)", "momentum")
def s24(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(S["srk"], S["srd"], i) and S["srk"][i - 1] is not None and S["srk"][i - 1] < 20
            and ok(S["e50"][i]) and C[i] > S["e50"][i]]


@sysdef("25", "Parabolic SAR trend scalper", "trend")
def s25(D, S):
    C = D["C"]
    return ev_first(lambda i: S["sard"][i] == 1 and ok(S["e100"][i], S["mh"][i]) and C[i] > S["e100"][i] and S["mh"][i] > 0, D["n"])


@sysdef("26", "EMA band scalp (EMA 50/100 · stoch)", "trend")
def s26(D, S):
    C, L = D["C"], D["L"]
    return [i for i in range(D["n"]) if xup(S["k"], S["d"], i) and S["k"][i - 1] is not None and S["k"][i - 1] < 30
            and ok(S["e50"][i], S["e100"][i]) and C[i] > S["e100"][i] and L[i] <= S["e50"][i] * 1.003 and C[i] > S["e50"][i]]


@sysdef("27", "Parabolic SAR + CCI", "trend")
def s27(D, S):
    C = D["C"]
    return [i for i in range(1, D["n"]) if S["sard"][i] == 1 and S["sard"][i - 1] == -1 and ok(S["s50"][i], S["cci20"][i])
            and C[i] > S["s50"][i] and S["cci20"][i] > 0]


@sysdef("28", "Intraday (EMA angle · pullback)", "trend")
def s28(D, S):
    C, L = D["C"], D["L"]
    return [i for i in range(5, D["n"]) if ok(S["e21"][i], S["e21"][i - 5], S["s50"][i], S["s50"][i - 5]) and S["e21"][i] > S["e21"][i - 5] * 1.001
            and S["s50"][i] > S["s50"][i - 5] and L[i] <= S["e21"][i] and C[i] > S["e21"][i]]


@sysdef("29", "Simple scalper (EMA · pivot)", "pattern")
def s29(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(S["e8"], S["e21"], i) and ok(S["P"][i]) and C[i] > S["P"][i]]


@sysdef("30", "Williams trade modified", "momentum")
def s30(D, S):
    return [i for i in range(D["n"]) if xup(S["wr"], -50, i) and ok(S["e13"][i], S["e34"][i]) and S["e13"][i] > S["e34"][i]]


@sysdef("31", "Super scalping (fractal · pivot)", "pattern")
def s31(D, S):
    C = D["C"]
    return [i for i in range(2, D["n"]) if S["fl"][i - 2] and ok(S["P"][i]) and C[i] > S["P"][i]]


@sysdef("32", "Pocket rocket (momentum burst)", "volume")
def s32(D, S):
    C, V = D["C"], D["V"]
    return [i for i in range(D["n"]) if ok(S["hh10"][i], S["v20"][i], S["rsi"][i]) and C[i] > S["hh10"][i] and V[i] > 1.5 * S["v20"][i] and S["rsi"][i] > 55]


@sysdef("33", "Forex profit (EMA 10/25/50 · SAR)", "trend")
def s33(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(S["e10"], S["e25"], i) and ok(S["e50"][i]) and S["e10"][i] > S["e50"][i] and S["e25"][i] > S["e50"][i]
            and S["sard"][i] == 1]


@sysdef("34", "Cross EMA (full candle · RSI)", "trend")
def s34(D, S):
    C, O = D["C"], D["O"]
    return [i for i in range(2, D["n"]) if xup(S["e9"], S["e21"], i - 1) and ok(S["e9"][i], S["rsi"][i]) and min(O[i], C[i]) > S["e9"][i]
            and 50 < S["rsi"][i] < 70]


@sysdef("35", "Simple MACD + EMA 20", "momentum")
def s35(D, S):
    C = D["C"]
    return [i for i in range(D["n"]) if xup(S["ml"], S["ms"], i) and ok(S["e20"][i]) and C[i] > S["e20"][i]]


@sysdef("36", "SMA 100 + MACD 15/26/9", "trend")
def s36(D, S):
    C, L = D["C"], D["L"]
    return [i for i in range(D["n"]) if xup(S["ml2"], S["ms2"], i) and ok(S["s100"][i]) and C[i] > S["s100"][i] and min(L[max(0, i - 5):i + 1]) <= S["s100"][i] * 1.01]


@sysdef("37", "EMA 10/21 fire zone (ADX)", "trend")
def s37(D, S):
    C, L = D["C"], D["L"]
    return [i for i in range(5, D["n"]) if ok(S["e10"][i], S["e21"][i], S["s50"][i], S["s50"][i - 5], S["adx"][i]) and S["e10"][i] > S["e21"][i]
            and S["s50"][i] > S["s50"][i - 5] and S["adx"][i] > 20 and S["e21"][i] <= L[i] <= S["e10"][i] and C[i] > S["e10"][i]]


@sysdef("38", "Tom Demark (EMA · momentum · trendline)", "pattern")
def s38(D, S):
    H, C = D["H"], D["C"]
    out, sw = [], []
    for i in range(D["n"]):
        if i >= 2 and S["fh"][i - 2]:
            sw.append(i - 2); sw = sw[-2:]
        if len(sw) == 2 and H[sw[1]] < H[sw[0]] and i > sw[1] + 2:
            a, b = sw
            line = H[a] + (H[b] - H[a]) * (i - a) / (b - a)
            prev = H[a] + (H[b] - H[a]) * (i - 1 - a) / (b - a)
            if C[i] > line and C[i - 1] <= prev and ok(S["e9"][i], S["e30"][i], S["mom14"][i]) and S["e9"][i] > S["e30"][i] and S["mom14"][i] > 0:
                out.append(i); sw = []
    return out


@sysdef("39", "CI system (candles · stoch · EMA 5/13)", "pattern")
def s39(D, S):
    return [i for i in range(D["n"]) if (engulf_up(D, i) or hammer(D, i)) and ok(S["k"][i], S["d"][i], S["e5"][i], S["e13"][i])
            and S["k"][i] > S["d"][i] and S["k"][i] < 40 and S["e5"][i] >= S["e13"][i] * 0.998]


@sysdef("40", "Brahmos confluence", "momentum")
def s40(D, S):
    C = D["C"]
    return ev_first(lambda i: ok(S["e20"][i], S["e50"][i], S["rsi"][i], S["mh"][i]) and C[i] > S["e20"][i] > S["e50"][i] and S["rsi"][i] > 55
                    and S["mh"][i] > 0, D["n"])


@sysdef("41", "CCI · stochastic · GMMA", "momentum")
def s41(D, S):
    return [i for i in range(D["n"]) if gmma_up(S, i) and xup(S["k"], S["d"], i) and S["k"][i - 1] is not None and S["k"][i - 1] < 40
            and ok(S["cci20"][i]) and S["cci20"][i] > -100]


@sysdef("42", "Supertrend breakout zone", "trend")
def s42(D, S):
    H, C = D["H"], D["C"]
    out = []
    for i in range(1, D["n"]):
        if S["st"][i] == 1 and S["st"][i - 1] == -1:
            z = H[i]
            for j in range(i + 1, min(D["n"], i + 11)):
                if S["st"][j] != 1:
                    break
                if C[j] > z:
                    out.append(j); break
    return out


@sysdef("43", "QFL (base crack)", "pattern")
def s43(D, S):
    H, L, C = D["H"], D["L"], D["C"]
    out, bases, used = [], [], set()
    for i in range(D["n"]):
        j = i - 3
        if j >= 0 and S["fl3"][j]:
            hi = max(H[j:i + 1])
            if hi >= L[j] * 1.03:
                bases.append(j)
        bases = [b for b in bases if i - b <= 300]
        for b in bases:
            if b not in used and C[i] < L[b] * 0.96:
                out.append(i); used.add(b); break
    return out


# ───────────────────────── measuring ─────────────────────────
def mirror(D):
    """1/price: every rise is a fall and back — the same system on it = its SELL"""
    return {"O": [1 / x for x in D["O"]], "H": [1 / x for x in D["L"]], "L": [1 / x for x in D["H"]], "C": [1 / x for x in D["C"]],
            "V": D["V"], "n": D["n"], "blk": D["blk"]}


def fwd(C, i, h, side):
    if i + h >= len(C):
        return None
    r = C[i + h] / C[i] - 1 if side > 0 else C[i] / C[i + h] - 1
    return r - FEE


def mean(v):
    return sum(v) / len(v) if v else 0.0


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else 0.0


T0 = time.time()
P_("dashboard", m.APP_VERSION, "· coins", len(COINS), "· systems", len(SYS), "· fake" if FAKE else "· REAL OKX")
RES = {}          # tf → {(code, side): {"tr": [...], "te": [...]}} per horizon index (list of nets)
BASE = {}         # tf → {side: {"tr": [[...]*3], "te": [...]}}
STATES = {}       # tf → list of (sym, D, events{(code, side): set(candles)}, split)
for tf, (maxn, HS, blk) in TFS.items():
    RES[tf] = {}
    BASE[tf] = {s: {"tr": [[] for _ in HS], "te": [[] for _ in HS]} for s in (1, -1)}
    STATES[tf] = []
    nco = 0
    for sym in COINS:
        try:
            rows = hist(sym, tf, maxn)
        except Exception as ex:
            P_(f"{tf} {sym}: fetch error {ex}"); continue
        if len(rows) < 400:
            continue
        nco += 1
        D = {"O": [float(r[1]) for r in rows], "H": [float(r[2]) for r in rows], "L": [float(r[3]) for r in rows], "C": [float(r[4]) for r in rows],
             "V": [float(r[5]) for r in rows], "n": len(rows), "blk": blk}
        C = D["C"]
        split = int(D["n"] * 0.6)
        S1, Dm = build(D), mirror(D)
        Sm = build(Dm)
        evs = {}
        for code, (name, fam, fn) in SYS.items():
            for side, DD, SS in ((1, D, S1), (-1, Dm, Sm)):
                try:
                    ev = [i for i in fn(DD, SS) if 210 <= i]
                except Exception as ex:
                    P_(f"{tf} {sym} {code}: error {type(ex).__name__} {ex}"); ev = []
                evs[(code, side)] = set(ev)
                R_ = RES[tf].setdefault((code, side), {"tr": [[] for _ in HS], "te": [[] for _ in HS], "coins": {}})
                for i in ev:
                    part = "tr" if i < split else "te"
                    for hi, h in enumerate(HS):
                        x = fwd(C, i, h, side)
                        if x is not None:
                            R_[part][hi].append(x)
                    if part == "te":
                        x = fwd(C, i, HS[1], side)
                        if x is not None:
                            R_["coins"].setdefault(sym, []).append(x)
        for side in (1, -1):
            for i in range(210, D["n"]):
                part = "tr" if i < split else "te"
                for hi, h in enumerate(HS):
                    x = fwd(C, i, h, side)
                    if x is not None:
                        BASE[tf][side][part][hi].append(x)
        STATES[tf].append((sym, D, evs, split))
    P_(f"{tf}: {nco} coins measured · {time.time() - T0:.0f}s")


def hit(v):
    return sum(1 for x in v if x > 0) / len(v) * 100 if v else 0.0


def pct(x):
    return f"{x * 100:+.2f}%"


GOOD = {}
for tf, (maxn, HS, blk) in TFS.items():
    P_(f"══ {tf} · judged after {HS[1]} candles (also {HS[0]} · {HS[2]}) · net after fees · TEST = the last 40% · random = any candle ══")
    for side in (1, -1):
        bt = BASE[tf][side]["te"][1]; btr = BASE[tf][side]["tr"][1]
        P_(f"{tf} {'BUY ' if side > 0 else 'SELL'} random: hit {hit(bt):.1f}% · mean {pct(mean(bt))} · median {pct(med(bt))} (n {len(bt)}) · learn-part mean {pct(mean(btr))}")
        rows = []
        for code, (name, fam, fn) in SYS.items():
            R_ = RES[tf].get((code, side))
            if not R_:
                continue
            te, tr = R_["te"][1], R_["tr"][1]
            e_te, e_tr = mean(te) - mean(bt), mean(tr) - mean(btr)
            cpos = sum(1 for v in R_["coins"].values() if len(v) >= 3 and mean(v) > mean(bt))
            cn = sum(1 for v in R_["coins"].values() if len(v) >= 3)
            good = len(te) >= 40 and len(tr) >= 40 and e_te > 0 and e_tr > 0 and hit(te) > hit(bt) + 2
            GOOD[(tf, code, side)] = (good, e_tr, len(tr))
            rows.append((e_te, f"{tf} {'BUY ' if side > 0 else 'SELL'} {code} {name[:34]:34s} [{fam[:4]}] n {len(te):5d} · hit {hit(te):5.1f}% (rand {hit(bt):.1f}) · "
                         f"mean {pct(mean(te))} · edge {pct(e_te)} (learn {pct(e_tr)}) · {HS[0]}: {pct(mean(R_['te'][0]) - mean(BASE[tf][side]['te'][0]))} · "
                         f"{HS[2]}: {pct(mean(R_['te'][2]) - mean(BASE[tf][side]['te'][2]))} · coins better {cpos}/{cn} {'✅' if good else '—'}"))
        for _, ln in sorted(rows, key=lambda r: -r[0]):
            P_(ln)

# ───────────────────────── one signal from all of them ─────────────────────────
P_("══ ONE SIGNAL — weights from the first 60% only · judged on the last 40% ══")
for tf, (maxn, HS, blk) in TFS.items():
    LOOK = max(2, HS[1] // 2)
    W = {}
    for code in SYS:
        for side in (1, -1):
            R_ = RES[tf].get((code, side))
            if not R_ or len(R_["tr"][1]) < 40:
                continue
            e = mean(R_["tr"][1]) - mean(BASE[tf][side]["tr"][1])
            W[(code, side)] = max(0.0, e) * 100           # only the systems that helped while learning
    nW = sum(1 for v in W.values() if v > 0)
    sc_tr, sc_te = [], []                                 # (score, net long at HS[1], i, sym)
    fam_te = []
    for sym, D, evs, split in STATES[tf]:
        C = D["C"]; n = D["n"]
        last = {k: -10 ** 9 for k in evs}
        evl = {k: sorted(v) for k, v in evs.items()}
        ptr = {k: 0 for k in evs}
        for i in range(210, n - HS[2] - 1):
            for k, lst in evl.items():
                while ptr[k] < len(lst) and lst[ptr[k]] <= i:
                    last[k] = lst[ptr[k]]; ptr[k] += 1
            s = 0.0
            fam = {}
            for (code, side), w in W.items():
                if i - last[(code, side)] < LOOK:
                    s += side * w
                    if w > 0:
                        f = SYS[code][1]
                        fam[f] = fam.get(f, 0) + side
            xl = fwd(C, i, HS[1], 1)
            if xl is None:
                continue
            (sc_tr if i < split else sc_te).append((s, xl, i, sym))
            if i >= split:
                fam_te.append((sum(1 for v in fam.values() if v > 0) - sum(1 for v in fam.values() if v < 0), xl))
    if not sc_tr or not sc_te:
        continue
    base_te = mean([x for _, x, _, _ in sc_te]); base_hit = hit([x for _, x, _, _ in sc_te])
    P_(f"{tf}: {nW} system-sides with weight · random buy here: mean {pct(base_te)} · hit {base_hit:.1f}%")
    srt = sorted(s for s, _, _, _ in sc_tr)
    for q in (0.80, 0.90, 0.95, 0.98):
        thr = srt[int(len(srt) * q)]
        if thr <= 0:
            P_(f"{tf} BUY score ≥ top {100 - q * 100:.0f}% (learn) — threshold {thr:.3f} ≤ 0 · skipped"); continue
        tr_ = [x for s, x, _, _ in sc_tr if s >= thr]; te_ = [x for s, x, _, _ in sc_te if s >= thr]
        P_(f"{tf} ONE-BUY score ≥ {thr:.3f} (top {100 - q * 100:.0f}% while learning): TEST n {len(te_)} · hit {hit(te_):.1f}% (rand {base_hit:.1f}) · "
           f"mean {pct(mean(te_))} · edge {pct(mean(te_) - base_te)} · learn edge {pct(mean(tr_) - mean([x for _, x, _, _ in sc_tr]))}")
    lo_ = sorted(s for s, _, _, _ in sc_tr)
    for q in (0.20, 0.10, 0.05, 0.02):
        thr = lo_[int(len(lo_) * q)]
        if thr >= 0:
            P_(f"{tf} SELL score ≤ bottom {q * 100:.0f}% — threshold {thr:.3f} ≥ 0 · skipped"); continue
        te_ = [-x - 2 * FEE for s, x, _, _ in sc_te if s <= thr]          # a fall after (a holder selling and buying back)
        rnd = [-x - 2 * FEE for _, x, _, _ in sc_te]
        P_(f"{tf} ONE-SELL score ≤ {thr:.3f} (bottom {q * 100:.0f}%): TEST n {len(te_)} · fell {hit(te_):.1f}% (rand {hit(rnd):.1f}) · "
           f"mean drop {pct(mean(te_))} · edge {pct(mean(te_) - mean(rnd))}")
    for k in (2, 3, 4):
        te_ = [x for f, x in fam_te if f >= k]
        dn_ = [-x - 2 * FEE for f, x in fam_te if f <= -k]
        rnd = [-x - 2 * FEE for _, x in fam_te]
        P_(f"{tf} FAMILIES ≥ {k} agree BUY: n {len(te_)} · hit {hit(te_):.1f}% · edge {pct(mean(te_) - base_te)} · "
           f"≥ {k} agree SELL: n {len(dn_)} · fell {hit(dn_):.1f}% · edge {pct(mean(dn_) - mean(rnd))}")
P_(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
