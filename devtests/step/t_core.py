# 🪜 the graded-grid engine on the mock OKX — the owner's rules, price discipline, books, buttons (audited at every loop)
#   python3 devtests/step/t_core.py [-q] [--only=name,name] [--seeds=N]
import json, math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
SEEDS = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--seeds=")), "16"))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:600]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


LINE = re.compile(r"^(🟢|🔴) \[(?:شراء|بيع) فوري\] السعر: ([0-9.e+-]+) \| الكمية: ([0-9.e+-]+)(?: \| الربح: ([+-][0-9.e+-]+)\$)?.* المستوى (-?\d+) · الجزء (\d+)/")


def trades(b):
    out = []
    for msg in reversed(b.hist()):
        m = LINE.match(msg)
        if m:
            out.append({"side": "buy" if m.group(1) == "🟢" else "sell", "px": float(m.group(2)), "qty": float(m.group(3)),
                        "profit": float(m.group(4)) if m.group(4) else None, "key": f"{m.group(5)}:{m.group(6)}"})
    return out


DUST = []      # sells booked under zero only because OKX's coarse quantity step kept coins back (finding F2) — counted, not failed


def discipline(b, fee=0.001):
    """every buy at or under its slot's fixed buy price · every sell at or over its sell price · every sell made money
    (v3.36.17 — F2: also on a coin with a coarse quantity step: the coins kept back carry their own cost)"""
    S, bad = b.st["slots"], []
    for t in trades(b):
        s = S.get(t["key"])
        if not s:
            bad.append(("unknown slot", t)); continue
        if t["side"] == "buy" and t["px"] > s["bp"] * (1 + 1e-9):
            bad.append(("bought above its price", t["key"], t["px"], s["bp"]))
        if t["side"] == "sell" and t["px"] < s["sp"] * (1 - 1e-9):
            bad.append(("sold under its price", t["key"], t["px"], s["sp"]))
        if t["side"] == "sell" and t["profit"] is not None and t["profit"] <= 0:      # v3.36.17 (F2): no exception any more —
            bad.append(("sell without profit", t["key"], t["profit"]))                  # the leftover coins carry their cost
    return bad


def press(b, **kv):
    """what the dashboard's buttons do: write keys into the bot's state file"""
    p = os.path.join(b.dir, f"grid_state_{b.ex.sym}.json")
    d = json.load(open(p))
    d.update(kv)
    tmp = p + ".dash"
    json.dump(d, open(tmp, "w"))
    os.replace(tmp, p)


def mine_live(b, side=None, fresh=False):
    """the bot's open orders on OKX · fresh=True: only those nothing filled yet (a partly filled one is never canceled on purpose)"""
    return [o for o in b.mine() if o["state"] in ("live", "partially_filled") and (side is None or o["side"] == side)
            and not (fresh and o["acc"] > 0)]


# ── 1. the owner's example: 15$ per buy split into 3 by coins · each sold part buys back the same coins at its fixed price
if want("owner"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex).run(walk([1.0, 1.0101, 1.0101, 1.0, 1.0, 0.97, 0.9705, 0.98, 0.99, 1.0, 1.0001]))
    S = b.st["slots"]
    f = [(x[2], float(x[3]), float(x[4])) for x in ex.fills]
    ok("owner: the start — 12 fixed buy levels down to the floor 0.7 (3 parts each) · 2 levels sold from the wallet (3 parts each)",
       sum(1 for s in S.values() if s["j"] < 0) == 36 and sum(1 for s in S.values() if s["j"] >= 0) == 6
       and min(s["bp"] for s in S.values()) >= 0.7, (len(S), min(s["bp"] for s in S.values())))
    ok("owner: price 1.0101 ⇒ the first part of level 0 sells 4.996 coins (5 × (1 − fee), from the wallet) at 1.01",
       f[0] == ("sell", 1.01, 4.996), f[:2])
    ok("owner: back to 1.00 ⇒ that part buys back THE SAME 5 coins at its fixed price 1.00 (not dollars)", f[1] == ("buy", 1.0, 5.0), f[:3])
    lv1 = [x for x in f if x[0] == "buy" and abs(x[1] - 0.9708) < 1e-9]
    ok("owner: 0.97 ⇒ level −1 buys its 3 parts as 3 separate orders at 0.9708, equal coins", len(lv1) == 3 and len({x[2] for x in lv1}) == 1, lv1)
    s1 = [x for x in f if x[0] == "sell" and x[1] in (0.9806, 0.9903, 1.0)]
    ok("owner: the way back up sells level −1 part by part at 0.9806 · 0.9903 · 1.00 (1% steps of 0.9708), each the bought coins less the fee",
       [x[1] for x in s1] == [0.9806, 0.9903, 1.0] and all(abs(x[2] - math.floor(lv1[0][2] * 0.9992 * 1e6) / 1e6) < 1e-9 for x in s1), s1)
    t = trades(b)
    ok("owner: every sell made money after both fees · the log's profits add up to the booked profit",
       all(x["profit"] > 0 for x in t if x["side"] == "sell")
       and abs(sum(x["profit"] for x in t if x["side"] == "sell") - b.st["total_profit"]) < 1e-5, (b.st["total_profit"], t))
    ok("owner: books = wallet at every loop (coins · dollars · orders · no self-cross · log)", not b.errors and b.audits > 20, b.errors)


# ── 2. random markets on four kinds of coin: every loop audited · price discipline · every sell profitable
COINS = [("XRP-USDT", "0.0001", "0.000001", "0.1", 1.0),
         ("BTC-USDT", "0.1", "0.00000001", "0.00001", 65000.0),
         ("DOGE-USDT", "0.00001", "1", "10", 0.15),
         ("PEPE-USDT", "0.00000001", "1", "100000", 0.0000123)]


def market(rng, p0, n, vol, jumps=True):
    p, out = p0, []
    for _ in range(n):
        r = rng.gauss(0, vol)
        if jumps and rng.random() < 0.03:
            r += rng.choice([-1, 1]) * rng.uniform(0.04, 0.12)
        p = max(p0 * 0.35, min(p0 * 2.5, p * math.exp(r)))
        out.append(p)
    return out


def rnd_cfg(rng, p0, spec):
    N = rng.randint(1, 5)
    d = rng.choice([0.004, 0.006, 0.01, 0.015, 0.02])
    G = rng.choice([0.01, 0.02, 0.03, 0.05])
    Qv = max(2.5 * N, rng.choice([10, 15, 30, 60])) * (3 if spec[0] == "PEPE-USDT" else 1)
    return {"step_parts": N, "step_sell": d, "grid_percentage": G, "usd_value": float(Qv),
            "min_price": p0 * rng.uniform(0.45, 0.8), "up_groups": rng.randint(0, 3), "forced_base_price": p0,
            "step_window": rng.choice([4, 8])}


if want("random"):
    worst = []
    for seed in range(SEEDS):
        rng = random.Random(1000 + seed)
        sym, tick, lot, mn, p0 = COINS[seed % 4]
        cfg = rnd_cfg(rng, p0, COINS[seed % 4])
        c = Clock()
        coins = (cfg["usd_value"] * 4 / p0) * rng.choice([0.3, 1.0, 3.0])
        ex = Ex(c, sym=sym, price=p0, tick=tick, lot=lot, mn=mn, base=round(coins, 6), quote=4000 * (3 if sym == "PEPE-USDT" else 1),
                partial=rng.choice([0, 0, 0.4]), seed=seed)
        b = Bot(ex, cfg)
        live_max = [0]
        b.on_loop = lambda bb: live_max.__setitem__(0, max(live_max[0], len(mine_live(bb, "buy", True)), len(mine_live(bb, "sell", True))))
        b.run(walk(market(rng, p0, 160, rng.choice([0.004, 0.01, 0.02])), hold=rng.choice([3.0, 6.0, 12.0])))
        dis = discipline(b)
        W = cfg["step_window"]
        okk = not b.errors and not dis and live_max[0] <= W + 2 and b.audits > 50
        if not okk:
            worst.append((seed, sym, cfg, b.errors[:3], dis[:3], live_max[0]))
    ok(f"random: {SEEDS} markets × 4 coin kinds (XRP · BTC · DOGE lot 1 · PEPE) · N 1–5 · partial fills · short/plenty coins — "
       "books = wallet every loop · buys never above their price · sells never under · every sell profitable · window ≤ W+2 "
       "(orders nothing filled yet)", not worst, worst[:2])
    if DUST:
        print(f"ℹ️  finding F2: {len(DUST)} sells booked under zero only by the coarse quantity step (coins kept back, sold later) — e.g. {DUST[:2]}")


# ── 3. above everything: the bot doesn't chase the price · it waits with its fixed buys
if want("chase"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex).run(walk([1.0, 1.02, 1.05, 1.08, 1.12, 1.2, 1.3, 1.3, 1.3]))
    S = b.st["slots"]
    ok("chase: the price runs away up ⇒ every wallet sell done, no sell order left, no new order above the old prices",
       all(s["side"] == "buy" for s in S.values()) and not mine_live(b, "sell")
       and max((o["px"] for o in mine_live(b, "buy")), default=0) <= 1.03 + 1e-9, [(k, s["side"]) for k, s in S.items() if s["j"] >= 0])
    b.run(walk([1.02, 1.0, 1.0]))
    ok("chase: the price comes back ⇒ the sold parts buy back at their fixed prices (1.03 · 1.00), not at the top",
       all(float(x[3]) <= 1.03 + 1e-9 for x in ex.fills if x[2] == "buy") and not b.errors and not discipline(b), (ex.fills[-6:], b.errors))


# ── 4. the floor: no buy under it, whatever the price does
if want("floor"):
    c = Clock(); ex = Ex(c, base=100, quote=2000)
    b = Bot(ex, {"min_price": 0.85}).run(walk([1.0, 0.95, 0.9, 0.85, 0.8, 0.7, 0.6, 0.6]))
    buys = [float(x[3]) for x in ex.fills if x[2] == "buy"]
    ok("floor 0.85: the price falls to 0.6 ⇒ no slot under the floor · nothing bought under 0.85 · books fine",
       min(s["bp"] for s in b.st["slots"].values()) >= 0.85 and min(buys) >= 0.85 - 1e-9 and not b.errors, (min(buys), b.errors))


# ── 5. not enough coins in the wallet for the levels above ⇒ the nearest sells are kept, the far ones dropped (and said so)
if want("short"):
    c = Clock(); ex = Ex(c, base=7, quote=1000)
    b = Bot(ex).run(walk([1.0, 1.0]))
    S = b.st["slots"]
    up = sorted((s["sp"], k) for k, s in S.items() if s["j"] >= 0)
    ok("short: 7 coins for 6 wallet sells of ~4.9 ⇒ one kept (the nearest: 1.01) · the log says the far ones were dropped",
       [k for _, k in up] == ["0:1"] and any("كفت" in m for m in b.hist()) and not b.errors, (up, b.hist()[:3]))


# ── 6. the buttons: ⏸ buying (a floor at the price) · ⏸ selling (a ceiling) · ▶️ back · 💣 delete cancels only its own orders
if want("buttons"):
    c = Clock(); ex = Ex(c, base=100, quote=2000)
    b = Bot(ex)
    b.run(walk([1.0, 1.0]) + [("do", lambda bb: press(bb, pause_buy=True))] + walk([0.99, 0.97, 0.95, 0.95]))
    nb = sum(1 for x in ex.fills if x[2] == "buy")
    ok("⏸ buying at 0.99 ⇒ a floor at the price · the price falls to 0.95 · nothing bought · no buy order left on OKX",
       abs(float(b.st.get("buy_floor") or 0) - 0.99) < 1e-9 and nb == 0 and not mine_live(b, "buy") and not b.errors,
       (b.st.get("buy_floor"), nb, len(mine_live(b, "buy")), b.errors))
    b.run([("do", lambda bb: press(bb, buy_floor=0))] + walk([0.95, 0.95]))
    ok("▶️ buying again ⇒ the levels the price passed buy at once (at the market, under their prices)",
       sum(1 for x in ex.fills if x[2] == "buy") >= 3 and not discipline(b) and not b.errors, (len(ex.fills), b.errors))
    b.run([("do", lambda bb: press(bb, pause_sell=True))] + walk([1.0, 1.02, 1.05, 1.05]))
    ns = sum(1 for x in ex.fills if x[2] == "sell")
    b.run([("do", lambda bb: press(bb, sell_ceiling=0))] + walk([1.05, 1.05]))
    ok("⏸ selling at the price ⇒ a ceiling · the price rises · no sell above it · ▶️ ⇒ the sells happen (at or over their prices)",
       sum(1 for x in ex.fills if x[2] == "sell") > ns and not discipline(b) and not b.errors, (ns, b.errors))
    fx = ex._place({"side": "sell", "px": "1.5", "sz": "1", "clOrdId": "OTHERBOT1s1", "stpMode": ""})["data"][0]["ordId"]
    b.run([("do", lambda bb: press(bb, self_destruct=True)), ("wait", 6)])
    ok("💣 delete ⇒ every order of the bot canceled on OKX · another bot's order untouched · the bot stops",
       not mine_live(b) and ex.orders[fx]["state"] == "live" and b.disk().get("destruct_done") is True,
       (len(mine_live(b)), ex.orders[fx]["state"], b.disk().get("status")))


# ── 7. a stray order with the bot's id (e.g. landed after the bot gave it up) is canceled · other bots' orders are not
if want("orphan"):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex)
    b.run(walk([1.0]))
    stray = ex._place({"side": "buy", "px": "0.5", "sz": "3", "clOrdId": b.bot_id + "bzzzz", "stpMode": ""})["data"][0]["ordId"]
    other = ex._place({"side": "buy", "px": "0.5", "sz": "3", "clOrdId": "HBOTHERbzzzz", "stpMode": ""})["data"][0]["ordId"]
    b.audit_on = False
    b.run(walk([1.0, 1.0]))
    ok("orphan: a stray order with the bot's id ⇒ canceled within a loop · another bot's order stays",
       ex.orders[stray]["state"] == "canceled" and ex.orders[other]["state"] == "live", (ex.orders[stray]["state"], ex.orders[other]["state"]))


print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
