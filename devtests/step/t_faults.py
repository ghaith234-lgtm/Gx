# 🪜 the graded-grid engine when OKX or the network misbehave — answers lost · requests that never arrive · orders that land
#   late · internet down · rejections (balance, rate limit, ambiguous) · lost cancels · someone cancels our order on OKX ·
#   a flaky API all the time — books = wallet at every loop, no order twice, nothing sold under / bought over its price
#   python3 devtests/step/t_faults.py [-q] [--only=name,name]
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:600]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


def live(b, side=None):
    return [o for o in b.mine() if o["state"] in ("live", "partially_filled") and (side is None or o["side"] == side)]


# (an order sent twice for one slot is caught by the runner's audit: the extra one belongs to no slot ⇒ «stray» if it lives
#  3 loops, or wallet ≠ books if it filled before the sweep canceled it)


def first_n(op_name, n, kind):
    cnt = [0]

    def f(op, p):
        if op == op_name and cnt[0] < n:
            cnt[0] += 1
            return kind
        return None
    return f


def run_case(fault=None, prices=(1.0, 1.0, 0.97, 0.97, 1.0, 1.0101, 1.0, 1.0), hold=30.0, cfg=None, base=100, quote=1000, partial=0.0, before=None):
    c = Clock(); ex = Ex(c, base=base, quote=quote, partial=partial)
    ex.fault = fault
    b = Bot(ex, cfg)
    steps = ([("do", before)] if before else []) + walk(list(prices), hold=hold)
    b.run(steps)
    return b, ex


# ── answers lost after OKX took the order: the order is found by our id, never sent twice
if want("lost"):
    b, ex = run_case(first_n("place", 5, "lost"))
    ok("lost answers (5 orders placed, answers lost) ⇒ each found by its id · none sent twice · books = wallet",
       not b.errors and len(ex.orders) == len(set(o["cl"] for o in ex.orders.values())) and live(b), (b.errors, len(ex.orders)))

# ── requests that never reached OKX: the bot waits 120 s (they might still arrive) then sends them again — once
if want("drop"):
    b, ex = run_case(first_n("place", 5, "drop"), hold=60.0)
    ok("dropped sends (5 never reached OKX) ⇒ resent after the 120 s wait, once each · books = wallet",
       not b.errors and live(b) and all(n == 1 for n in __import__("collections").Counter(o["cl"] for o in ex.orders.values()).values()),
       (b.errors, len(ex.orders)))

# ── an order that reaches OKX 60 s late (inside the 120 s wait): adopted when it lands, not sent twice
if want("late"):
    b, ex = run_case(first_n("place", 4, ("late", 60.0)), hold=60.0)
    ok("orders landing 60 s late ⇒ found when they land · none sent twice · books = wallet",
       not b.errors and len(ex.orders) >= 4, (b.errors))

# ── internet down 5 minutes while the price moves: no new orders while down · everything settles after · books fine
if want("down"):
    def go_down(bb):
        bb.ex.down = True

    def come_back(bb):
        bb.ex.down = False
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex)
    b.run(walk([1.0, 1.0], 30) + [("do", go_down)] + walk([0.97, 0.95, 0.98, 1.01, 1.0], 60) + [("do", come_back)] + walk([1.0, 1.0101, 1.0, 1.0], 60))
    ok("internet down 5 min while the price moves ⇒ the bot waits · back online it syncs (fills that happened meanwhile processed once) · "
       "books = wallet · the log says it went offline and came back",
       not b.errors and any("انقطع الاتصال" in m for m in b.hist()) and any("عاد الاتصال" in m for m in b.hist()), (b.errors, b.hist()[:4]))

# ── not enough USDT: buys rejected (51008) ⇒ that side calms down (no order after order) · money arrives ⇒ buys go on
if want("balance"):
    c = Clock(); ex = Ex(c, base=100, quote=8)
    b = Bot(ex)
    b.run(walk([1.0, 0.99, 0.99, 0.99, 0.99, 0.99], 60))
    n_rej = sum(1 for m in b.hist() if m.startswith("⚠️ [رفض أمر شراء"))
    calls = ex.calls["place"]

    def deposit(bb):
        bb.ex.bal["USDT"] += D(2000)
        bb.usd0 += D(2000)                     # money from outside (a deposit) — the books start from it too
    b.run([("do", deposit)] + walk([0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99], 120))
    ok(f"8 USDT for 5$ parts ⇒ rejections calm the buy side (≤ 1 log line / 5 min, {calls} sends in 6 min) · USDT arrives ⇒ the buys are placed",
       n_rej <= 2 and calls < 30 and len(live(b, "buy")) >= 4 and not b.errors, (n_rej, calls, len(live(b, "buy")), b.errors))

# ── rate limit (50011) and «service unavailable» (50001 — the order may or may not be in): no order twice
if want("codes"):
    import itertools
    seq = itertools.cycle([("code", "50011"), None, ("ambig", True), None, ("ambig", False), None])
    b, ex = run_case(lambda op, p: next(seq) if op == "place" else None, hold=60.0)
    ok("rate limit (50011) and ambiguous answers (50001, placed or not) ⇒ settled by our id · nothing sent twice · books = wallet",
       not b.errors and live(b), (b.errors))

# ── cancels whose answer is lost or that never arrive (the window pulls far orders back to memory)
if want("cancel"):
    rng = random.Random(7)
    b, ex = run_case(lambda op, p: rng.choice(["lost", "drop", None, None]) if op == "cancel" else None,
                     prices=[1.0, 0.97, 0.94, 0.91, 0.88, 0.91, 0.94, 0.97, 1.0, 1.0101, 1.0], hold=30.0, cfg={"step_window": 3})
    ok("cancels lost or never arriving while the window moves ⇒ the bot re-checks OKX before moving an order to memory · books = wallet",
       not b.errors, (b.errors))

# ── someone cancels the bot's order on OKX (by hand): the slot goes back to memory and its order is placed again
if want("manual"):
    def kill_some(bb):
        for o in live(bb)[:3]:
            bb.ex._cancel(o["ordId"])
    b, ex = run_case(before=None, prices=[1.0, 1.0, 1.0, 1.0], hold=20.0)
    n0 = len(live(b))
    b.run([("do", kill_some)] + walk([1.0, 1.0, 1.0], 20))
    ok("3 orders canceled by hand on OKX ⇒ seen as canceled without a fill · placed again · books = wallet",
       not b.errors and len(live(b)) == n0, (n0, len(live(b)), b.errors))

# ── a partial fill and then the order is canceled (STP / by hand): the part done is booked, the rest is ordered again
if want("partial_cancel"):
    c = Clock(); ex = Ex(c, base=100, quote=1000, partial=0.5)
    b = Bot(ex)
    b.run(walk([1.0, 1.0101], 20))

    def kill_partial(bb):
        for o in live(bb, "sell"):
            if o["acc"] > 0:
                bb.ex._cancel(o["ordId"])
    b.run([("do", kill_partial)] + walk([1.0101, 1.0101, 1.0101, 1.0], 20))
    S = b.st["slots"]
    ok("a sell half filled then canceled ⇒ the half is booked · the rest is ordered again and sold · the part buys back · books = wallet",
       not b.errors and S["0:1"]["n"] >= 1, (S["0:1"], b.errors))

# ── an API that fails all the time (10% of every kind of call, in every way) over a random market
if want("flaky"):
    bad = []
    for seed in range(6):
        rng = random.Random(500 + seed)

        def flaky(op, p, rng=rng):
            if rng.random() > 0.10:
                return None
            if op == "place":
                return rng.choice(["drop", "lost", ("late", rng.uniform(2, 90)), ("code", "50011"), ("ambig", rng.random() < 0.5)])
            return rng.choice(["drop", "lost"]) if op == "cancel" else "drop"
        p, prices = 1.0, []
        for _ in range(120):
            p = max(0.6, min(1.6, p * math.exp(rng.gauss(0, 0.012))))
            prices.append(p)
        b, ex = run_case(flaky, prices=prices, hold=rng.choice([6.0, 15.0]), partial=rng.choice([0, 0.5]),
                         cfg={"step_parts": rng.randint(1, 4), "step_sell": rng.choice([0.006, 0.01, 0.015])})
        sells = [m for m in b.hist() if m.startswith("🔴")]
        if b.errors or not sells:
            bad.append((seed, b.errors[:2], len(sells)))
    ok("flaky API (10% of all calls dropped / answer lost / late up to 90 s / rate-limited / ambiguous) × 6 random markets ⇒ "
       "books = wallet at every loop · nothing twice · it still trades", not bad, bad[:2])

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
