# 🔀 شبكة عملتين — ⚡ a power cut at EVERY moment of a trading scenario: before/after every state save, every order sent, every
#   order check, every ticker, every balance read, every log line. After each cut the engine restarts on the same folder.
#   Each run must end with: the wallet = the books at every loop · no sale line twice · Σ 🔴 = total_profit · and the SAME end
#   (profit · XRP · SOL · sales) as the run without any cut.        python3 devtests/pair/t_cut.py [--scen=a|b|c] [--every=N]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairsim as P

D = P.D
SCEN = next((a[7:] for a in sys.argv[1:] if a.startswith("--scen=")), "all")
EVERY = int(next((a[8:] for a in sys.argv[1:] if a.startswith("--every=")), "1"))


def scen_a(ex):
    """3 levels down (buys) · back up 3 levels above the start (sales of the bought coins and of the wallet's)"""
    xrp = ex.ins["XRP-USDT"]["px"]
    lv = lambda k: (lambda b: ex.set("SOL-USDT", (D(75) * D("1.02") ** k * (D("1.001") if k > 0 else D("0.999")) * xrp).quantize(D("0.01"))))
    return [(10, lv(-1)), (400, lv(-2)), (800, lv(-3)), (1200, lv(-1)), (1600, lv(1)), (2000, lv(3))], 2400, {"down_levels": 3, "up_levels": 3}


def scen_b(ex):
    """a thin book (partial fills on both legs) + a jump of three levels"""
    ex.ins["SOL-USDT"]["depth"] = D("0.1")
    ex.ins["XRP-USDT"]["depth"] = D(9)
    xrp = ex.ins["XRP-USDT"]["px"]
    lv = lambda k: (lambda b: ex.set("SOL-USDT", (D(75) * D("1.02") ** k * (D("1.001") if k > 0 else D("0.999")) * xrp).quantize(D("0.01"))))
    return [(10, lv(-3)), (600, lv(2))], 1200, {"down_levels": 3, "up_levels": 2}


def scen_c(ex):
    """another bot takes the dollar between the two legs (the second leg is refused until the dollar comes back)"""
    st = {"n": 0}

    def steal(o):
        if o["inst"] == "XRP-USDT" and o["side"] == "sell" and st["n"] == 0:
            st["n"] = 1
            ex.foreign["USDT"] += ex.bal["USDT"]
    ex.after_place = steal
    xrp = ex.ins["XRP-USDT"]["px"]
    lv = lambda k: (lambda b: ex.set("SOL-USDT", (D(75) * D("1.02") ** k * (D("1.001") if k > 0 else D("0.999")) * xrp).quantize(D("0.01"))))
    return [(10, lv(-1)), (300, lambda b: ex.foreign.clear()), (700, lv(1))], 1200, {"down_levels": 2, "up_levels": 1}


def one(scen, cut=None):
    ex = P.market(bal_xrp="300", bal_sol="3")
    steps, end, cfg = scen(ex)
    bot = P.PBot(ex, cfg=dict(cfg, bot_id="HBPCUT000001"))
    bot.run(steps, end=end, cut_at=[cut] if cut else None)
    st = bot.state()
    key = (round(float(st.get("total_profit") or 0), 9), round(float(st.get("main_book") or 0), 9),
           round(float(st.get("other_book") or 0), 9), len(bot.sales), bool(st.get("op")))
    out = (key, bot.errors[:1], bot.dup[:1], bot.cuts, bot.moments)
    bot.cleanup()
    return out


tot = bad = 0
for name, scen in (("a", scen_a), ("b", scen_b), ("c", scen_c)):
    if SCEN not in ("all", name):
        continue
    base, e0, d0, _, M = one(scen)
    print(f"── scenario {name}: {M} moments · end without a cut {base} · {'ok' if not e0 and not d0 else e0 or d0}", flush=True)
    if e0 or d0:
        bad += 1
    fails = []
    for k in range(1, M + 1, EVERY):
        key, e, d, cuts, _ = one(scen, k)
        tot += 1
        why = e[0] if e else (d[0] if d else ("" if key == base else f"end {key} ≠ {base}"))
        if why:
            bad += 1
            fails.append((k, why[:200]))
    print(f"   cuts at {len(range(1, M + 1, EVERY))} moments: {'✅ all identical' if not fails else '❌ ' + str(len(fails)) + ' differ'}", flush=True)
    for k, w in fails[:8]:
        print(f"     #{k}: {w}")
print(f"\n{'✅' if not bad else '❌'} t_cut: {tot - bad}/{tot}")
sys.exit(1 if bad else 0)
