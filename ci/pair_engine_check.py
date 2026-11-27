# 🔀 «شبكة عملتين» — the REAL engine (devtests/pair/eng/main_pair.py) on REAL OKX prices (the owner 27-11: «وسوي تجربه xrp عملة رىيسية
#   وخلي معها sol xlm وlink وbtc وeth النسبة ٢ بالمائة»). The engine runs unchanged against the fake exchange (devtests/pair/pairsim.py)
#   whose two prices follow OKX's real 5-minute closes (90 days) or 15-minute closes (a year) · OKX's real lot/tick/min · a 0.02% spread ·
#   0.1% fee every order · 200$ of XRP + 200$ of the other coin · step 2% · every buy = 20$ of XRP (in XRP at the start) · the calculator's
#   levels (all the XRP below · all the other coin above) · all the profit to XRP. The wallet is audited against the bot's books at
#   every loop. Public data only (no keys · no orders).   python3 ci/pair_engine_check.py Holy_Dashboard.pyw [5m|15m]
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "devtests", "pair"))
DASH = os.path.abspath(sys.argv[1])
BAR = sys.argv[2] if len(sys.argv) > 2 else "5m"
R_ = tempfile.mkdtemp(prefix="pairchk_")
shutil.copy(DASH, os.path.join(R_, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd()
os.chdir(R_)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R_, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
argv0 = sys.argv
sys.argv = ["x"]
ld.exec_module(m)
sys.argv = argv0
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
os.chdir(cwd0)
T0 = time.time()
OUT = {"runs": []}


def Pr(*a):
    print("HOLYPAIR", *a, flush=True)


DT, N = {"5m": (300, 25920), "15m": (900, 35040)}[BAR]
DRY = os.environ.get("PAIR_DRY") == "1"
if DRY:
    N = 2000


def fetch(sym):
    if DRY:                                          # (a local run: a synthetic walk — the CI run reads OKX)
        import random
        rnd, base = random.Random(abs(hash(sym)) % 997), random.Random(5)
        p, out, t = {"XRP": 2.0, "SOL": 150.0, "XLM": 0.3, "LINK": 15.0, "BTC": 90000.0, "ETH": 3000.0}[sym.split("-")[0]], [], 1_760_000_000
        for i in range(N):
            p *= math.exp(base.gauss(0, 0.004) * (1.3 if "XRP" not in sym else 1) + rnd.gauss(0, 0.003))
            out.append([t + i * DT, p, p, p, p, 1])
        return out
    rows = [c[:6] for c in m._fc_okx_rows(sym, BAR, hist=False, limit=100) if c[6]]
    oldest = min((c[0] for c in rows), default=None)
    while oldest and len(rows) < N:
        pg = [c[:6] for c in m._fc_okx_rows(sym, BAR, after=oldest * 1000, hist=True, limit=100) if c[6] and c[0] < oldest]
        if not pg:
            break
        rows += pg
        oldest = min(c[0] for c in pg)
        time.sleep(0.12)
    return sorted({c[0]: c for c in rows}.values())[-N:]


def spec(sym):
    if DRY:
        return {"XRP": ("0.0001", "0.000001", "1"), "SOL": ("0.01", "0.000001", "0.01"), "XLM": ("0.00001", "0.000001", "10"),
                "LINK": ("0.001", "0.000001", "0.1"), "BTC": ("0.1", "0.00000001", "0.00001"), "ETH": ("0.01", "0.000001", "0.0001")}[sym.split("-")[0]]
    r = m._okx_pub(f"/api/v5/public/instruments?instType=SPOT&instId={sym}")
    d = ((r or {}).get("data") or [{}])[0]
    return str(d.get("tickSz") or "0.0001"), str(d.get("lotSz") or "0.000001"), str(d.get("minSz") or "1")


CX = fetch("XRP-USDT")
SX = spec("XRP-USDT")
COINS = ("SOL", "XLM", "LINK", "BTC", "ETH")
DATA = {o: (fetch(f"{o}-USDT"), spec(f"{o}-USDT")) for o in COINS}       # every price first — pairsim then blocks the network
Pr(f"fetched XRP + {len(DATA)} coins · {BAR} · in {time.time() - T0:.0f}s")
import pairsim as P
D = P.D
for OTH in COINS:
    t1 = time.time()
    inst = f"{OTH}-USDT"
    CO, so = DATA[OTH]
    tb = {c[0]: c[4] for c in CO}
    rows = [(c[0], c[4], tb[c[0]]) for c in CX if c[0] in tb]
    if len(rows) < 500:
        Pr(f"XRP/{OTH}: too few candles")
        continue
    pm0, po0 = rows[0][1], rows[0][2]
    clock = P.Clock(float(rows[0][0]))
    ex = P.PEx(clock, insts={"XRP-USDT": dict(px=str(pm0), tick=SX[0], lot=SX[1], mn=SX[2]), inst: dict(px=str(po0), tick=so[0], lot=so[1], mn=so[2])},
               bal={"XRP": repr(200.0 / pm0), OTH: repr(200.0 / po0), "USDT": "0"})
    tm, to = D(SX[0]), D(so[0])

    def mk(pm, po):
        def f(b):
            ex.set("XRP-USDT", (D(repr(pm)) / tm).to_integral_value() * tm)
            ex.set(inst, (D(repr(po)) / to).to_integral_value() * to)
        return f
    r0 = po0 / pm0
    mv = 20.0 / pm0
    a_other = 200.0 / po0 * 0.999                     # (a hair under the wallet: the calculator never plans more than there is)
    up, need = 0, 0.0
    while up < 2000:
        q = mv / (r0 * 1.02 ** up)
        if need + q > a_other:
            break
        need += q
        up += 1
    dn = int(math.floor((200.0 / pm0) / mv + 1e-9))
    cfg = {"main_value": mv, "grid_percentage": 0.02, "down_levels": dn, "up_levels": up, "forced_base_ratio": r0, "profit_to": "main",
           "bot_id": "HBPREAL" + OTH[:4].ljust(4, "X")}
    bot = P.PBot(ex, sym=f"{OTH}-XRP", cfg=cfg)
    bot.ff = True
    t0 = rows[0][0]
    steps = [(r[0] - t0 + 1, mk(r[1], r[2])) for r in rows[1:]]
    bot.run(steps, end=rows[-1][0] - t0 + 30)
    st = bot.state()
    days = (rows[-1][0] - rows[0][0]) / 86400
    pmx, pox = rows[-1][1], rows[-1][2]
    w0 = 400.0 / pm0
    w1 = float(ex.bal["XRP"]) + float(ex.bal[OTH]) * pox / pmx + float(ex.bal["USDT"]) / pmx
    hold = 200.0 / pm0 * pmx + 200.0 / po0 * pox
    val = float(ex.bal["XRP"]) * pmx + float(ex.bal[OTH]) * pox + float(ex.bal["USDT"])
    prof = float(st.get("total_profit") or 0)
    rec = {"pair": f"XRP/{OTH}", "bar": BAR, "days": round(days, 1), "levels_down": dn, "levels_up": up, "sales": len(bot.sales),
           "profit_xrp": round(prof, 6), "xrp_per_day": round(prof / days, 6), "wallet_in_xrp_pct": round(100 * (w1 / w0 - 1), 3),
           "value": round(val, 2), "hold": round(hold, 2), "vs_hold_pct": round(100 * (val / hold - 1), 3), "audits": bot.audits,
           "max_dev": str(bot.max_dev), "errors": bot.errors[:3], "dups": bot.dup[:2], "usd_left": float(ex.bal["USDT"]),
           "places": ex.calls["place"], "secs": round(time.time() - t1)}
    OUT["runs"].append(rec)
    Pr(f"XRP/{OTH} {BAR} · {days:.0f} days · {dn} levels below · {up} above · {len(bot.sales)} sales · profit {prof:.4f} XRP ({prof / days:.4f} XRP/day ≈ "
       f"{prof / days * pmx:.4f}$/day at today's XRP) · wallet in XRP {100 * (w1 / w0 - 1):+.2f}% · {val:.2f}$ vs hold {hold:.2f}$ "
       f"({100 * (val / hold - 1):+.2f}%) · dollar left {float(ex.bal['USDT']):.4f}$ · orders {ex.calls['place']} · audits {bot.audits} "
       f"(max Δ {bot.max_dev}) · {'✅ books = wallet' if not bot.errors and not bot.dup else '❌ ' + str((bot.errors or bot.dup)[0])[:160]} · {time.time() - t1:.0f}s")
    bot.cleanup()
json.dump(OUT, open("/tmp/holypair.json", "w"), ensure_ascii=False)
Pr(f"DONE · {time.time() - T0:.0f}s")
