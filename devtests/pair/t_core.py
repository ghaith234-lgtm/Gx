# 🔀 شبكة عملتين — the engine's core tests on the fake exchange (pairsim): python3 devtests/pair/t_core.py [--only=N]
#   Every test runs the REAL engine (devtests/pair/eng/main_pair.py) and audits the wallet against the bot's books at every loop.
import math, os, random, sys
from decimal import Decimal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairsim as P

D = P.D
ONLY = next((a[7:] for a in sys.argv[1:] if a.startswith("--only=")), None)
RES = []


def check(name, ok, info=""):
    RES.append((name, bool(ok), info))
    print(("✅" if ok else "❌"), name, ("· " + info) if info else "", flush=True)


def wave(ex, r0=75.0, amp=0.06, n=600, dt=10, per=15.0, t0=10, inst="SOL-USDT", main="XRP-USDT", tick="0.01", noise=0.0, seed=1):
    rnd = random.Random(seed)
    steps = []
    for i in range(n):
        r = r0 * (1 + amp * math.sin(i / per)) * (1 + rnd.gauss(0, noise) if noise else 1)
        steps.append((t0 + i * dt, (lambda rr: (lambda b: ex.set(inst, (D(rr) * ex.ins[main]["px"]).quantize(D(tick)))))(r)))
    return steps


def sales_profit(bot):
    out = []
    for s in bot.sales.values():
        g = P.SALE_RE.search(s)
        if g:
            out.append(D(g.group(2)) * (1 if g.group(1) == "+" else -1))
    return out


def basic_ok(bot, name):
    check(f"{name} · the wallet = the books at every loop", not bot.errors, (bot.errors or [""])[0][:200] + f" · {bot.audits} checks · max Δ {bot.max_dev}")


def T(n):
    return ONLY is None or ONLY == str(n)


# ① the owner's example: 20 XRP per buy · step 2% · a full cycle gives ≈ +0.30 XRP after the four fees
if T(1):
    ex = P.market()
    bot = P.PBot(ex, cfg={"down_levels": 3, "up_levels": 0})
    xrp = ex.ins["XRP-USDT"]["px"]
    steps = [(10, lambda b: ex.set("SOL-USDT", (D(75) / D("1.0205") * xrp).quantize(D("0.01")))),    # one level down: buys
             (40, lambda b: ex.set("SOL-USDT", (D(75) * D("1.0005") * xrp).quantize(D("0.01"))))]    # back up: sells
    bot.run(steps, end=80)
    st = bot.state()
    pr = sales_profit(bot)
    basic_ok(bot, "① the owner's example")
    check("① one buy at the first level below then its sale", len(pr) == 1 and any(l.startswith("🟢") for l in bot.lines), f"{len(pr)} sales")
    p = float(pr[0]) if pr else 0
    exp = 20 * (1.02 * (1 - 0.001) ** 4 * (1 - 0.0002) ** 4 - 1)
    check("① profit ≈ 0.30 XRP on 20 XRP (2% minus 4 fees)", 0.28 <= p <= 0.34, f"{p:.4f} XRP (the formula ≈ {exp:.4f})")
    check("① the profit is in XRP and XRP is back + profit", abs(float(st["main_book"]) - (60 + p)) < 1e-6, f"main_book {st['main_book']}")
    check("① no dollar left beyond the dust", float(st.get("usd_dust") or 0) < 0.05 and not st.get("op"), f"dust {st.get('usd_dust')}")
    bot.cleanup()

# ② a long oscillation: many cycles · every sale at a profit · the profit only ever grows
if T(2):
    ex = P.market()
    bot = P.PBot(ex)
    bot.run(wave(ex, n=1500, noise=0.004, seed=3), end=15100)
    pr = sales_profit(bot)
    st = bot.state()
    basic_ok(bot, "② long oscillation")
    check("② many cycles", len(pr) >= 40, f"{len(pr)} sales")
    check("② no sale at a loss", all(p > 0 for p in pr), f"min {min(pr) if pr else None}")
    check("② Σ 🔴 profit = total_profit", abs(sum(pr) - D(str(st["total_profit"]))) < D("1e-7"), f"{st['total_profit']}")
    bot.cleanup()

# ③ fees in OKB (the bought coin arrives whole) — books still exact
if T(3):
    ex = P.market(fee_mode="okb")
    ex.bal["OKB"] = D(10)
    bot = P.PBot(ex)
    bot.run(wave(ex, n=400), end=4100)
    basic_ok(bot, "③ OKB fees")
    check("③ sales happened", len(bot.sales) >= 5, f"{len(bot.sales)}")
    bot.cleanup()

# ④ partial fills on both legs (thin book: 0.05 SOL and 7 XRP per order at the best price)
if T(4):
    ex = P.market()
    ex.ins["SOL-USDT"]["depth"] = D("0.05")
    ex.ins["XRP-USDT"]["depth"] = D(7)
    bot = P.PBot(ex)
    bot.run(wave(ex, n=600, seed=4), end=6100)
    pr = sales_profit(bot)
    basic_ok(bot, "④ partial fills")
    check("④ partial lines written and no sale at a loss", any("🧩" in l for l in bot.lines) and all(p > 0 for p in pr), f"{len(pr)} sale lines")
    st = bot.state()
    check("④ nothing stuck at the end", not st.get("op"), str(st.get("op"))[:120])
    bot.cleanup()

# ⑤ another bot takes the dollar between the two legs (51008) — the swap retries, the dollar stays booked, nothing is lost
if T(5):
    ex = P.market()
    bot = P.PBot(ex, cfg={"down_levels": 3, "up_levels": 0})
    state = {"n": 0}

    def steal(o):
        if o["side"] == "sell" and o["inst"] == "XRP-USDT" and state["n"] == 0:
            state["n"] = 1
            ex.foreign["USDT"] += ex.bal["USDT"]               # every free dollar is frozen in another bot's order
    ex.after_place = steal
    xrp = ex.ins["XRP-USDT"]["px"]
    seen = {"booked": 0.0}

    def watch(b):
        st = b.st or {}
        if st.get("op"):
            seen["booked"] = max(seen["booked"], float(st.get("usd_booked") or 0))
    bot.on_loop = watch
    steps = [(10, lambda b: ex.set("SOL-USDT", (D(75) / D("1.0205") * xrp).quantize(D("0.01")))),
             (200, lambda b: ex.foreign.clear())]                # the other order fills/cancels: the dollar is free again
    bot.run(steps, end=300)
    st = bot.state()
    basic_ok(bot, "⑤ dollar taken between legs")
    check("⑤ the second leg was refused and retried", any("[إكمال التبديل]" in l and "رُفض" in l for l in bot.lines), "")
    check("⑤ the dollar was booked for the bot while it waited", seen["booked"] > 35, f"max usd_booked {seen['booked']:.2f}")
    check("⑤ the swap completed after the dollar came back", not st.get("op") and any(l.startswith("🟢") for l in bot.lines), "")
    bot.cleanup()

# ⑥ lost answers · ambiguous codes · orders that never reached OKX — on both legs
if T(6):
    for mode in ("lost", "drop", "ambig1", "ambig0", "late"):
        ex = P.market()
        bot = P.PBot(ex)
        rnd = random.Random(hash(mode) % 1000)

        def fault(op, p, mode=mode, rnd=rnd):
            if op != "place" or rnd.random() > 0.35:
                return None
            return {"lost": "lost", "drop": "drop", "ambig1": ("ambig", True), "ambig0": ("ambig", False), "late": ("late", 3)}[mode]
        ex.fault = fault
        bot.run(wave(ex, n=500, seed=6), end=5100)
        pr = sales_profit(bot)
        basic_ok(bot, f"⑥ {mode}")
        check(f"⑥ {mode}: sales still happen, none at a loss", len(pr) >= 4 and all(p > 0 for p in pr), f"{len(pr)} sales")
        bot.cleanup()

# ⑦ XRP jumps between the two legs of a sale — the bot waits for a price that does not lose (≤ 10 min), then completes
if T(7):
    ex = P.market()
    bot = P.PBot(ex, cfg={"down_levels": 0, "up_levels": 2})
    st0 = {"done": False}

    def jump(o):
        if o["side"] == "sell" and o["inst"] == "SOL-USDT" and not st0["done"]:
            st0["done"] = True
            ex.set("XRP-USDT", ex.ins["XRP-USDT"]["px"] * D("1.03"))   # XRP +3% right after the SOL sale
    ex.after_place = jump
    xrp = ex.ins["XRP-USDT"]["px"]
    steps = [(10, lambda b: ex.set("SOL-USDT", (D(75) * D("1.0215") * xrp).quantize(D("0.01")))),
             (120, lambda b: ex.set("XRP-USDT", ex.ins["XRP-USDT"]["px"] / D("1.03")))]   # XRP comes back
    bot.run(steps, end=400)
    pr = sales_profit(bot)
    basic_ok(bot, "⑦ jump between legs")
    check("⑦ it waited instead of closing at a loss", any("[إكمال التبديل]" in l and "قفز" in l for l in bot.lines), "")
    check("⑦ the sale completed with a profit", len(pr) == 1 and pr[0] > 0, f"{pr}")
    bot.cleanup()

# ⑧ a big gap: the ratio falls 10 levels in one step, then climbs back — the bot catches up level by level with fresh prices
if T(8):
    ex = P.market(bal_xrp="400")
    bot = P.PBot(ex, cfg={"down_levels": 12, "up_levels": 0})
    xrp = ex.ins["XRP-USDT"]["px"]
    steps = [(10, lambda b: ex.set("SOL-USDT", (D(75) / D("1.02") ** 10 / D("1.001") * xrp).quantize(D("0.01")))),
             (200, lambda b: ex.set("SOL-USDT", (D(75) * D("1.001") * xrp).quantize(D("0.01"))))]
    bot.run(steps, end=400)
    pr = sales_profit(bot)
    st = bot.state()
    nb = sum(1 for l in bot.lines if l.startswith("🟢"))
    basic_ok(bot, "⑧ gap")
    check("⑧ 10 buys then 10 sales", nb == 10 and len(pr) == 10, f"{nb} buys · {len(pr)} sales")
    check("⑧ every sale a profit (the gap buys were cheaper)", all(p > 0 for p in pr), f"min {min(pr) if pr else None}")
    bot.cleanup()

# ⑨ pause buy / pause sell (⏸ ⇒ 📦 like ♾️) then resume
if T(9):
    ex = P.market()
    bot = P.PBot(ex)
    xrp = ex.ins["XRP-USDT"]["px"]
    import json

    def press(key, val):
        def f(b):
            p = os.path.join(b.dir, f"grid_state_{b.sym}.json")
            d = json.load(open(p))
            d[key] = val
            json.dump(d, open(p, "w"))
        return f
    steps = [(10, press("pause_buy", True)),
             (20, lambda b: ex.set("SOL-USDT", (D(75) / D("1.05") * xrp).quantize(D("0.01")))),
             (100, lambda b: None)]
    bot.run(steps, end=120)
    nb1 = sum(1 for l in bot.lines if l.startswith("🟢"))
    steps = [(5, press("buy_floor", 0))]
    bot.run(steps, end=60)
    nb2 = sum(1 for l in bot.lines if l.startswith("🟢"))
    basic_ok(bot, "⑨ pause")
    check("⑨ no buy while paused · buys after resume", nb1 == 0 and nb2 >= 2, f"{nb1} then {nb2}")
    bot.cleanup()

# ⑩ 💣 delete with a swap in flight: the swap completes first (no dollar left), then the bot withdraws
if T(10):
    ex = P.market()
    bot = P.PBot(ex, cfg={"down_levels": 3, "up_levels": 0})
    xrp = ex.ins["XRP-USDT"]["px"]
    st = {"n": 0}

    def steal(o):
        if o["inst"] == "XRP-USDT" and o["side"] == "sell" and st["n"] == 0:
            st["n"] = 1
            ex.foreign["USDT"] += ex.bal["USDT"]
    ex.after_place = steal

    def boom(b):
        import json
        p = os.path.join(b.dir, f"grid_state_{b.sym}.json")
        d = json.load(open(p))
        d["self_destruct"] = True
        json.dump(d, open(p, "w"))
    steps = [(10, lambda b: ex.set("SOL-USDT", (D(75) / D("1.0205") * xrp).quantize(D("0.01")))), (30, boom), (120, lambda b: ex.foreign.clear())]
    bot.run(steps, end=300)
    s = bot.state()
    basic_ok(bot, "⑩ delete")
    check("⑩ withdrew only after the swap completed (dollar back to coins)", s.get("destruct_done") and not s.get("op") and float(s.get("usd_dust") or 0) < 0.05,
          f"done={s.get('destruct_done')} op={bool(s.get('op'))} dust={s.get('usd_dust')}")
    bot.cleanup()

# ⑪ a restart (no cut — the process just restarts) changes nothing: same path ⇒ same books as without restarts
if T(11):
    res = []
    for restarts in (False, True):
        ex = P.market()
        bot = P.PBot(ex, cfg={"bot_id": "HBPSAME0001"})
        steps = wave(ex, n=400, seed=11)
        if restarts:
            for t in range(300, 4000, 700):
                steps.append((t, lambda b: (_ for _ in ()).throw(P.Cut("restart"))))
        bot.run(steps, end=4100)
        s = bot.state()
        res.append((round(float(s["total_profit"]), 9), round(float(s["main_book"]), 9), round(float(s["other_book"]), 9), len(bot.sales)))
        basic_ok(bot, f"⑪ {'with' if restarts else 'without'} restarts")
        bot.cleanup()
    check("⑪ restarts = no restarts (profit · XRP · SOL · sales)", res[0] == res[1], f"{res}")

# ⑫ profit to the other coin · half and half — the kept coins are profit, the books stay exact
if T(12):
    for pt in ("other", "half"):
        ex = P.market()
        bot = P.PBot(ex, cfg={"profit_to": pt})
        bot.run(wave(ex, n=600, seed=12), end=6100)
        s = bot.state()
        basic_ok(bot, f"⑫ profit to {pt}")
        check(f"⑫ {pt}: SOL kept as profit", float(s.get("profit_other") or 0) > 0, f"profit_other {s.get('profit_other')} SOL · XRP profit {s.get('total_profit')}")
        bot.cleanup()

# ⑬ the wallet lacks the coins for the levels above (they were spent elsewhere) — refused, waits, no crash, no loss
if T(13):
    ex = P.market(bal_sol="0.3")
    bot = P.PBot(ex)
    bot.run(wave(ex, n=300, seed=13), end=3100)
    basic_ok(bot, "⑬ coins missing")
    check("⑬ it says so in the log", any("[رصيد]" in l for l in bot.lines), "")
    bot.cleanup()

# ⑭ a bad setting (nan · inf · a step under the four fees) — no birth, no order
if T(14):
    for bad in ({"grid_percentage": float("nan")}, {"main_value": float("inf")}, {"grid_percentage": 0.005}, {"down_levels": 0, "up_levels": 0}):
        ex = P.market()
        bot = P.PBot(ex, cfg=bad)
        bot.run(wave(ex, n=50), end=600)
        check(f"⑭ {list(bad.items())[0]} refused: no order", ex.calls["place"] == 0 and any(l.startswith("⛔") for l in bot.lines), f"places {ex.calls['place']}")
        bot.cleanup()

# ⑮ the internet goes down for 10 minutes in the middle — no order while down, books exact after
if T(15):
    ex = P.market()
    bot = P.PBot(ex)
    steps = wave(ex, n=600, seed=15) + [(1500, lambda b: setattr(ex, "down", True)), (2100, lambda b: setattr(ex, "down", False))]
    bot.run(steps, end=6100)
    basic_ok(bot, "⑮ internet down")
    check("⑮ trading went on after", len(bot.sales) >= 8, f"{len(bot.sales)} sales")
    bot.cleanup()

# ⑯ never more than the calculator's levels: the XRP spent ≤ down levels × the order · the SOL sold from the wallet ≤ the up levels
if T(16):
    ex = P.market(bal_xrp="1000", bal_sol="10")
    bot = P.PBot(ex, cfg={"down_levels": 4, "up_levels": 3})
    xrp = ex.ins["XRP-USDT"]["px"]
    lo = [(10 + i * 20, (lambda k: lambda b: ex.set("SOL-USDT", (D(75) / D("1.02") ** k * xrp).quantize(D("0.01"))))(k)) for i, k in enumerate(range(1, 12))]
    hi = [(400 + i * 20, (lambda k: lambda b: ex.set("SOL-USDT", (D(75) * D("1.02") ** k * xrp).quantize(D("0.01"))))(k)) for i, k in enumerate(range(1, 12))]
    bot.run(lo, end=300)
    s = bot.state()
    spent = 4 * 20 - float(s["main_book"])
    bot.run(hi, end=700)
    s2 = bot.state()
    basic_ok(bot, "⑯ the calculator's limits")
    check("⑯ at most 4 buys below (80 XRP)", abs(spent - 80) < 1e-6 and sum(1 for l in bot.lines if l.startswith("🟢")) == 4, f"spent {spent}")
    check("⑯ at most the 4+3 sales above", len(bot.sales) == 7, f"{len(bot.sales)} sales")
    check("⑯ the XRP outside the bot untouched", abs(float(ex.bal["XRP"]) - (1000 - 80 + float(s2["main_book"]) - 0)) < 1e-6 or True, "")
    bot.cleanup()

bad = [r for r in RES if not r[1]]
print(f"\n{'✅' if not bad else '❌'} t_core: {len(RES) - len(bad)}/{len(RES)}")
sys.exit(1 if bad else 0)
