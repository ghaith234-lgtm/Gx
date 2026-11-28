# 🛑 XRP: «sell on the way down, buy back on the way up» — measured on REAL OKX prices before anything is built (the owner 28-11:
#   «العملات اذا نزلت بحد او نسبة معينه يبيع حتى ما ينزل بعد اكثر واذا نزل وصعد مره اخرى للسعر الي باع يشتري حتى ما يضيع الصعود
#   ونستغل النزول للشراء بأسعار ارخص» · «شنو حل السعر البيع» · «سويها للxrp»).
#   The rule: a stop X% under the highest price since the last full buy (it follows the top) — confirmed on a closed bar (none ·
#   15 minutes · 1 hour) — sells at once (taker 0.1% + 0.1% worse price) · one part or three (−X · −1.5X · −2X) · each part is
#   bought back by a trigger when the price climbs back to its own sell price (taker 0.1% + 0.1% worse) · optional cheaper buys while
#   out: resting limit buys 10/20/30% under the deepest stop (maker 0.08%), 25% of the cash each · after a full buy back the stop
#   follows the new top (no second sale at the same price) · at most 2 first-sales a week.
#   ① the last year minute by minute · ② every year of the hourly history (bull and bear) · ③ 200 random years from real two-week
#   pieces of that history. Measured against holding: the XRP count · the dollar value · false alarms · the deepest fall.
#   Public data only (no keys · no orders · no wallet).   python3 ci/xrp_stop_check.py Holy_Dashboard.pyw
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, threading, time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import numpy as np

DASH = os.path.abspath(sys.argv[1])
R_ = tempfile.mkdtemp(prefix="xstop_")
shutil.copy(DASH, os.path.join(R_, "Holy_Dashboard.pyw"))
os.chdir(R_)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R_, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
T0 = time.time()
LOCK = threading.Lock()
DRY = os.environ.get("XSTOP_DRY") == "1"
SYM = "XRP-USDT"


def Pr(*a):
    with LOCK:
        print("HXS", *a, flush=True)


def fetch_back(bar, t_end, n, dt):
    """closed candles going back from t_end (seconds), oldest first"""
    if DRY:
        rnd = np.random.default_rng(int(t_end) % 9973)
        lp = np.log(2.0) + np.cumsum(rnd.normal(0, 0.0012 if dt == 60 else 0.009, n))
        return [[int(t_end - (n - i) * dt), float(np.exp(v))] for i, v in enumerate(lp)]
    rows = {}
    after = int(t_end) * 1000
    last_log = time.time()
    while len(rows) < n:
        pg = []
        for k in range(10):
            pg = [c for c in m._fc_okx_rows(SYM, bar, after=after, hist=True, limit=100) if c[6]]
            if pg:
                break
            time.sleep(1.0 + k)
        if not pg:
            break
        for c in pg:
            rows[c[0]] = c[4]
        after = min(c[0] for c in pg) * 1000
        if time.time() - last_log > 300:
            last_log = time.time()
            Pr(f"{bar}: {len(rows)} · {time.time() - T0:.0f}s")
        time.sleep(0.55)
    return sorted(rows.items())[-n:]


def sim(P, X, parts, ladder, every, cap_week=2, bars_week=None, slip=0.001, fee_t=0.001, fee_m=0.0008):
    """P = closes · every = the stop looks only at every n-th close (1 = any bar) ⇒ dict"""
    coins, cash = 1000.0, 0.0
    peak = P[0]
    mult = [1.0] if parts == 1 else [1.0, 1.5, 2.0]
    full_ref = coins
    pend = []                    # sell prices of the parts out (waiting to be bought back)
    nsold = 0                    # parts sold in this episode
    lad = []                     # resting cheaper buys: [price, used?]
    weeks = deque()
    ep, false_al, n_sell, n_rebuy, out_bars = 0, 0, 0, 0, 0
    ep_first = None
    ep_lad = False
    vmax, dd = 0.0, 0.0
    hmax, hdd = 0.0, 0.0
    for i in range(len(P)):
        p = P[i]
        # the cheaper buys (resting limits) fill when the price reaches them
        if lad and cash > 0 and nsold == len(mult):          # (after every part is out) — each level a quarter of the cash it had
            for L in lad:
                if not L[1] and p <= L[0]:
                    spend = cash / (sum(1 for x_ in lad if not x_[1]) + 1)
                    coins += spend / L[0] * (1 - fee_m)
                    cash -= spend
                    L[1] = True
                    ep_lad = True
        # buy back: each part when the price climbs back to its own sell price (a trigger order)
        if pend:
            hit = [s for s in pend if p >= s]
            if hit:
                for s in sorted(hit):
                    share = cash / len(pend)
                    if len(pend) == 1:
                        share = cash
                    coins += share / (p * (1 + slip)) * (1 - fee_t)
                    cash -= share
                    pend.remove(s)
                    n_rebuy += 1
                if not pend:
                    if ep_first is not None and p >= ep_first and not ep_lad:
                        false_al += 1
                    cash = max(0.0, cash)
                    if cash > 1e-9:            # (rounding) the rest goes in too
                        coins += cash / (p * (1 + slip)) * (1 - fee_t)
                        cash = 0.0
                    peak, full_ref, nsold, lad, ep_first, ep_lad = p, coins, 0, [], None, False
        if not pend and nsold == 0:
            peak = max(peak, p)
        # the stop (on a confirmed close)
        if (i + 1) % every == 0 and nsold < len(mult):
            lvl = peak * (1 - X * mult[nsold])
            if p <= lvl:
                if nsold == 0:
                    while weeks and i - weeks[0] > bars_week:
                        weeks.popleft()
                    if len(weeks) >= cap_week:
                        lvl = -1
                if lvl > 0:
                    q = full_ref / len(mult) if nsold < len(mult) - 1 else coins
                    q = min(q, coins)
                    cash += q * p * (1 - slip) * (1 - fee_t)
                    coins -= q
                    pend.append(p)
                    n_sell += 1
                    if nsold == 0:
                        ep += 1
                        weeks.append(i)
                        ep_first = p
                        if ladder:
                            deep = peak * (1 - X * mult[-1])
                            lad = [[deep * (1 - 0.1 * k), False] for k in (1, 2, 3)]
                    nsold += 1
        if cash > 0:
            out_bars += 1
        v = coins * p + cash
        vmax = max(vmax, v)
        dd = max(dd, 1 - v / vmax)
        h = 1000.0 * p
        hmax = max(hmax, h)
        hdd = max(hdd, 1 - h / hmax)
    pe = P[-1]
    val = coins * pe + cash
    return {"coins_end": coins + cash / pe, "vs_hold": val / (1000.0 * pe) - 1, "episodes": ep, "false": false_al, "sells": n_sell,
            "rebuys": n_rebuy, "out": out_bars / len(P), "dd": dd, "hold_dd": hdd, "chg": pe / P[0] - 1}


SETS = [(X, parts, lad) for X in (0.05, 0.10, 0.15, 0.20) for parts in (1, 3) for lad in (0, 1)]


def lab(X, parts, lad):
    return f"{int(X * 100)}%·{'3 دفعات' if parts == 3 else 'دفعة'}·{'+أرخص' if lad else '—'}"


OUT = {"minute": {}, "years": {}, "boot": {}}
now = int(time.time()) // 60 * 60
# ── ① the last year, minute by minute (4 pieces fetched together)
NM = 365 * 1440
segs = 4
seg_n = NM // segs + 1
with ThreadPoolExecutor(segs) as ex:
    parts_ = list(ex.map(lambda k: fetch_back("1m", now - k * seg_n * 60, seg_n, 60), range(segs)))
mrows = sorted({t: c for part in parts_ for t, c in part}.items())
Pr(f"1m: {len(mrows)} minutes · from {time.strftime('%Y-%m-%d', time.gmtime(mrows[0][0]))} · {time.time() - T0:.0f}s")
PMIN = np.array([c for _, c in mrows][-NM:])
for every, el in ((1, "بلا تأكيد"), (15, "15د"), (60, "ساعة")):
    for X, parts, lad in SETS:
        r = sim(PMIN, X, parts, lad, every, bars_week=7 * 1440)
        OUT["minute"][f"{el}|{lab(X, parts, lad)}"] = r
        Pr(f"MIN {el} {lab(X, parts, lad)}: XRP {r['coins_end']:.1f} (من 1000) · مقابل الاحتفاظ {r['vs_hold'] * 100:+.1f}% · مرات البيع {r['episodes']} · "
           f"إنذار كاذب {r['false']} · برا السوق {r['out'] * 100:.0f}% · أعمق نزول {r['dd'] * 100:.0f}% (الاحتفاظ {r['hold_dd'] * 100:.0f}%) · XRP {r['chg'] * 100:+.0f}%")
# ── ② the hourly history (as far back as OKX gives) · every calendar year
NH = 9 * 365 * 24
hrows = fetch_back("1H", now // 3600 * 3600, NH, 3600)
Pr(f"1H: {len(hrows)} hours · from {time.strftime('%Y-%m-%d', time.gmtime(hrows[0][0]))} · {time.time() - T0:.0f}s")
TH = np.array([t for t, _ in hrows])
PH = np.array([c for _, c in hrows])
years = sorted({time.gmtime(int(t)).tm_year for t in TH})
yidx = {y: np.where(np.array([time.gmtime(int(t)).tm_year for t in TH]) == y)[0] for y in years}
for X, parts, lad in SETS:
    row = {}
    for y in years:
        ix = yidx[y]
        if len(ix) < 24 * 60:
            continue
        r = sim(PH[ix], X, parts, lad, 1, bars_week=7 * 24)
        row[y] = r
    rall = sim(PH, X, parts, lad, 1, bars_week=7 * 24)
    OUT["years"][lab(X, parts, lad)] = {"all": rall, **{str(y): r for y, r in row.items()}}
    Pr(f"YRS {lab(X, parts, lad)}: كل الفترة {rall['vs_hold'] * 100:+.0f}% (XRP {rall['coins_end']:.0f}) · " + " · ".join(
        f"{y} {r['vs_hold'] * 100:+.0f}% (XRP {r['chg'] * 100:+.0f}% · بيع {r['episodes']} · كاذب {r['false']})" for y, r in row.items()))
# ── ③ 200 random years from real two-week pieces of the hourly history
B = 14 * 24
dL = np.diff(np.log(PH))
rng = np.random.default_rng(20261128)
Y = 365 * 24
paths = []
for k in range(200):
    st = rng.integers(0, len(dL) - B, size=Y // B + 1)
    sel = np.concatenate([np.arange(s, s + B) for s in st])[:Y]
    paths.append(np.exp(np.concatenate([[0.0], np.cumsum(dL[sel])])))
xc = [p_[-1] - 1 for p_ in paths]
for X, parts, lad in SETS:
    R = [sim(p_, X, parts, lad, 1, bars_week=7 * 24) for p_ in paths]
    vs = np.array([r["vs_hold"] for r in R])
    co = np.array([r["coins_end"] for r in R])
    up = [r["vs_hold"] for r, c in zip(R, xc) if c > 0.25]
    dn = [r["vs_hold"] for r, c in zip(R, xc) if c < -0.25]
    sd = [r["vs_hold"] for r, c in zip(R, xc) if -0.25 <= c <= 0.25]
    s = {"vs_p10_50_90": [float(np.percentile(vs, q)) for q in (10, 50, 90)], "mean": float(vs.mean()), "better": float((vs > 0).mean()),
         "coins_p10_50_90": [float(np.percentile(co, q)) for q in (10, 50, 90)], "up_med": float(np.median(up)) if up else None,
         "down_med": float(np.median(dn)) if dn else None, "side_med": float(np.median(sd)) if sd else None,
         "false_med": float(np.median([r["false"] for r in R])), "ep_med": float(np.median([r["episodes"] for r in R])),
         "dd_med": float(np.median([r["dd"] for r in R])), "hold_dd_med": float(np.median([r["hold_dd"] for r in R]))}
    OUT["boot"][lab(X, parts, lad)] = s
    Pr(f"BOOT {lab(X, parts, lad)}: مقابل الاحتفاظ وسط {s['vs_p10_50_90'][1] * 100:+.1f}% [{s['vs_p10_50_90'][0] * 100:+.0f}%..{s['vs_p10_50_90'][2] * 100:+.0f}%] · "
       f"المتوسط {s['mean'] * 100:+.1f}% · أحسن بـ{s['better'] * 100:.0f}% من السنين · XRP وسط {s['coins_p10_50_90'][1]:.0f} · "
       f"سنين الصعود {100 * (s['up_med'] or 0):+.0f}% · العرضية {100 * (s['side_med'] or 0):+.0f}% · النزول {100 * (s['down_med'] or 0):+.0f}% · "
       f"بيع {s['ep_med']:.0f}/سنة · كاذب {s['false_med']:.0f} · أعمق نزول {s['dd_med'] * 100:.0f}% (الاحتفاظ {s['hold_dd_med'] * 100:.0f}%)")
Pr(f"BOOT XRP over the year: median {np.median(xc) * 100:+.0f}% [{np.percentile(xc, 10) * 100:+.0f}%..{np.percentile(xc, 90) * 100:+.0f}%] · "
   f"up years {sum(1 for c in xc if c > 0.25)} · side {sum(1 for c in xc if -0.25 <= c <= 0.25)} · down {sum(1 for c in xc if c < -0.25)}")
json.dump(OUT, open("/tmp/holyxstop.json", "w"), ensure_ascii=False)
Pr(f"DONE · {time.time() - T0:.0f}s")
