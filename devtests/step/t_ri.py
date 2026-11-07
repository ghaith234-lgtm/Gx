# 🪜💠 reinvest on the graded grid — the grid's reinvest.py rules, per slot (REINVEST_PLAN.md ١–٧ · ١٢), on the real engine + mock OKX
#   100%  every sale's real profit goes to its slot's pot · «💠 [ربح داخلي]» line, no sale line · total_profit untouched ·
#         the pot turns into quantity in whole lots at the slot's buy price · the slot's next buy = base + growth (the order OKX
#         gets) · its sale sells all of it at its real cost ⇒ a bigger profit
#   50%   both lines · the sale line carries the ordinary half · the 💠 line «(50% من …)» · ordinary + reinvested = real profit
#   0%    = no reinvest: the same fills and profit as a bot without it · no 💠 line · growth frozen
#   live  the percentage changes while it runs (no restart) · 0 freezes (growth stays, the buy keeps its size)
#   DOGE  whole-coin lots: the pot carries its cents over sales until one whole coin · not a cent lost
#   off   a bot without reinvest has no book at all
#   cut   a power cut between a sale's two lines ⇒ each written once after the restart
#   random markets (partial fills, both sides, wallet levels) · books = wallet at every loop (okxsim's audit: real profit =
#   total_profit + credited · pots = credited · each sale's lines once)
#   python3 devtests/step/t_ri.py [-q] [--only=name,...] [--seeds=N]          (STEP_ENGINE=… tests another engine copy)
import os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D, Cut

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
SEEDS = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--seeds=")), "8"))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


RED = re.compile(r"^🔴 \[بيع فوري\] السعر: ([0-9.]+) \| الكمية: ([0-9.]+) \| الربح: ([+-][0-9.]+)\$.* المستوى (-?\d+) · الجزء (\d+)/\d+.*· البيعة (\d+)$")
RI = re.compile(r"^💠 \[ربح داخلي\] السعر: ([0-9.]+) \| الربح: \+([0-9.]+)\$ (?:\((\d+)% من ([0-9.]+)\$\) )?· معاد استثمارها \| "
                r"المتراكم: ([0-9.]+)\$(?: · ([0-9.]+) عملة)? · 🪜 المستوى (-?\d+) · الجزء (\d+)/\d+ · البيعة (\d+)$")


def lines(b):
    red, ri = {}, {}
    for m in b.fill_lines:
        r = RED.match(m)
        if r:
            red[(int(r.group(4)), int(r.group(5)), int(r.group(6)))] = float(r.group(3))
        r = RI.match(m)
        if r:
            ri[(int(r.group(7)), int(r.group(8)), int(r.group(9)))] = {"credit": float(r.group(2)),
                                                                       "pct": int(r.group(3)) if r.group(3) else 100,
                                                                       "of": float(r.group(4)) if r.group(4) else None}
    return red, ri


def sales(b):
    return sum(int(s.get("n") or 0) for s in b.st["slots"].values())


class SizeWatch:
    """at every loop: a buy order OKX holds for a slot = its base + growth (minus what it already bought) on OKX's lot"""

    def __init__(self):
        self.bad, self.grown_orders = [], 0

    def __call__(self, b):
        st = b.st or {}
        for k, s in (st.get("slots") or {}).items():
            o = s.get("o") or {}
            if s.get("side") != "buy" or o.get("st") != "live":
                continue
            eo = b._ex_of(o)
            if not eo or eo["acc"] > 0 or float(s.get("acc") or 0) > 0:
                continue
            want_ = b.m.fmt_qty(float(s["q"]) + float(s.get("g") or 0))
            if abs(float(eo["sz"]) - want_) > 1e-12:
                self.bad.append((k, str(eo["sz"]), want_, s.get("g")))
            if float(s.get("g") or 0) > 0:
                self.grown_orders += 1


DOWN_UP = [1.0, 0.99, 0.98, 0.9709, 0.97, 0.9806, 0.9903, 1.0, 1.0]      # level −1 (0.97087): buy · its 3 parts sell


def bot(pct=None, cfg=None, ex=None, **kw):
    c = Clock()
    ex = ex or Ex(c, base=100, quote=1000, **kw)
    cf = {"step_window": 8, "step_first": 0.01}
    if pct is not None:
        cf.update(reinvest=True, reinvest_pct=pct)
    cf.update(cfg or {})
    b = Bot(ex, cf)
    b.on_loop = SizeWatch()
    return b


def run(b, prices, hold=20.0):
    return b.run(walk(prices, hold=hold))


# ── 100%: the owner's case
if want("p100"):
    b = run(bot(100), DOWN_UP * 3)
    st, rb = b.st, b.st.get("reinvest") or {}
    red, ri = lines(b)
    n = sales(b)
    ok("100%: every sale has its «💠 [ربح داخلي]» line and no sale line · total_profit stays 0", n >= 9 and len(ri) == n and not red
       and abs(float(st.get("total_profit") or 0)) < 1e-12, (n, len(ri), len(red), st.get("total_profit")))
    ok("100%: the pots hold the whole real profit (credited = Σ the 💠 lines) · books = wallet at every loop",
       abs(float(rb.get("credited") or 0) - sum(v["credit"] for v in ri.values())) < 1e-8 and not b.errors and rb.get("on"),
       (rb.get("credited"), sum(v["credit"] for v in ri.values()), b.errors[:3]))
    lv = (rb.get("levels") or {}).get("-1:1") or {}
    s = st["slots"]["-1:1"]
    ok("100%: the pot turns into quantity in whole lots at the slot's buy price — the cents stay in the pot (none lost)",
       lv and lv["grown_qty"] > 0 and 0 <= lv["usd_book"] < 0.000001 * s["bp"] + 1e-12 and abs(s.get("g", 0) - lv["grown_qty"]) < 1e-12,
       (lv, s.get("g")))
    ok("100%: the slot's next buy order at OKX = base + growth (every loop, every slot)", b.on_loop.grown_orders > 0 and not b.on_loop.bad,
       (b.on_loop.grown_orders, b.on_loop.bad[:3]))
    seq = sorted((key[2], v["credit"]) for key, v in ri.items() if key[:2] == (-1, 1))
    ok("100%: a grown slot sells everything it bought ⇒ each round's profit bigger than the last", len(seq) >= 3 and all(
        seq[i][1] > seq[i - 1][1] for i in range(1, len(seq))), seq)
    hist = [m for m in b.hist() if m.startswith(("🔴", "💠", "🛑"))]
    ok("100%: no «🛑» (the pots never broke)", not any(m.startswith("🛑") for m in hist), hist[:3])

# ── 50%: both lines, split
if want("p50"):
    b = run(bot(50), DOWN_UP * 3)
    st, rb = b.st, b.st.get("reinvest") or {}
    red, ri = lines(b)
    n = sales(b)
    pair = all(k in red for k in ri) and all(k in ri for k in red)
    split = all(abs(ri[k]["of"] - (ri[k]["credit"] + red[k])) < 2e-10 and abs(ri[k]["credit"] - red[k]) < 2e-10 and ri[k]["pct"] == 50
                for k in ri if k in red)
    ok("50%: every sale has a sale line with the ordinary half and a 💠 line «(50% من …)» · the halves add up to its profit",
       n >= 9 and len(ri) == n and pair and split, (n, len(ri), len(red), list(ri.items())[:2], list(red.items())[:2]))
    ok("50%: total_profit = Σ the sale lines · credited = Σ the 💠 lines · books = wallet",
       abs(float(st["total_profit"]) - sum(red.values())) < 1e-8 and abs(float(rb["credited"]) - sum(v["credit"] for v in ri.values())) < 1e-8
       and not b.errors and not b.on_loop.bad, (st["total_profit"], sum(red.values()), rb.get("credited"), b.errors[:3], b.on_loop.bad[:2]))

# ── 0% = no reinvest
if want("p0"):
    b0 = run(bot(0), DOWN_UP * 3)
    bo = run(bot(None), DOWN_UP * 3)
    red, ri = lines(b0)
    same = [(x[2], str(x[3]), str(x[4])) for x in b0.ex.fills] == [(x[2], str(x[3]), str(x[4])) for x in bo.ex.fills]
    ok("0%: the same fills and the same profit as a bot without reinvest · no 💠 line · no growth",
       same and abs(float(b0.st["total_profit"]) - float(bo.st["total_profit"])) < 1e-12 and not ri
       and not any(float(s.get("g") or 0) for s in b0.st["slots"].values()) and not b0.errors,
       (same, b0.st["total_profit"], bo.st["total_profit"], len(ri), b0.errors[:2]))
    ok("off: a bot without reinvest has no reinvest book · its sale lines as before (one per sale)",
       "reinvest" not in bo.st and len(lines(bo)[0]) == sales(bo) and not bo.errors, (list(bo.st)[:30], bo.errors[:2]))

# ── the percentage changes while it runs
if want("live"):
    b = bot(100)

    def setpct(v):
        def f(bb):
            import json
            p = os.path.join(bb.dir, f"config_{bb.ex.sym}.json")
            c = json.load(open(p)); c["reinvest_pct"] = v; json.dump(c, open(p, "w"))
        return ("do", f)

    marks = {}

    def snap(name):
        def f(bb):
            marks[name] = (float(bb.st["total_profit"]), float(bb.st["reinvest"]["credited"]),
                           {k: float(s.get("g") or 0) for k, s in bb.st["slots"].items()}, sales(bb))
        return ("do", f)

    steps = (walk(DOWN_UP, 20.0) + [snap("a"), setpct(0), ("wait", 10)] + walk(DOWN_UP, 20.0) + [snap("b"), setpct(40), ("wait", 10)]
             + walk(DOWN_UP, 20.0) + [snap("c")])
    b.run(steps)
    a, bb_, c = marks.get("a"), marks.get("b"), marks.get("c")
    ok("live 0%: no restart · nothing more reinvested · the growth stays and the buys keep their size · the profit is ordinary",
       a and bb_ and bb_[3] > a[3] and abs(bb_[1] - a[1]) < 1e-12 and bb_[2] == a[2] and bb_[0] > a[0] + 1e-9 and any(a[2].values()),
       (a, bb_))
    red, ri = lines(b)
    p40 = [v for k, v in ri.items() if v["pct"] == 40]
    lg = [m for m in b.hist() if m.startswith("⚖️")]
    ok("live: each change of the percentage written once in the log «⚖️ … النسبة صارت 0% · 100% ربح عادي» (as the grid)",
       sorted(lg) == sorted(["⚖️ [إعادة الاستثمار] النسبة صارت 0% للأمر نفسه · 100% ربح عادي",
                             "⚖️ [إعادة الاستثمار] النسبة صارت 40% للأمر نفسه · 60% ربح عادي"]) and b.st["reinvest"].get("pct") == 40.0, lg)
    ok("live 40%: reinvesting again at the new share («(40% من …)») · books = wallet · buy sizes right at every loop",
       c and c[1] > bb_[1] + 1e-9 and c[0] > bb_[0] + 1e-9 and p40 and all(abs(v["credit"] - 0.4 * v["of"]) < 1e-9 for v in p40)
       and not b.errors and not b.on_loop.bad, (c, len(p40), b.errors[:3], b.on_loop.bad[:2]))

# ── DOGE: whole coins
if want("doge"):
    c = Clock()
    ex = Ex(c, sym="DOGE-USDT", price=0.2, tick="0.00001", lot="1", mn="1", base=2000, quote=1000)
    b = bot(100, {"usd_value": 30.0, "forced_base_price": 0.2, "min_price": 0.12}, ex=ex)
    P = [0.2, 0.198, 0.196, 0.1942, 0.194, 0.1962, 0.1981, 0.2, 0.2]
    b.run(walk(P * 8, hold=20.0))
    rb = b.st.get("reinvest") or {}
    red, ri = lines(b)
    lv = (rb.get("levels") or {}).get("-1:1") or {}
    s = b.st["slots"]["-1:1"]
    whole = all(abs(float(x.get("grown_qty") or 0) - round(float(x.get("grown_qty") or 0))) < 1e-12 for x in (rb.get("levels") or {}).values())
    ok("DOGE (whole coins): the pot carries its cents over the sales until a whole coin · growth only in whole coins · books = wallet",
       len(ri) >= 8 and whole and lv and lv["grown_qty"] >= 1 and 0 <= lv["usd_book"] < s["bp"] + 1e-12 and not b.errors and not b.on_loop.bad,
       (len(ri), lv, b.errors[:3], b.on_loop.bad[:2]))
    pot = sum(float(x["usd_book"]) + float(x["grown_qty"]) * float(x["px"]) for x in rb["levels"].values())
    ok("DOGE: not a cent lost — the pots (cents + whole coins at their buy price) = everything reinvested",
       abs(pot - float(rb["credited"])) < 1e-9 and abs(float(rb["credited"]) - sum(v["credit"] for v in ri.values())) < 1e-8,
       (pot, rb.get("credited")))

# ── a power cut between a sale's two lines (60%: the sale line, then the 💠 line) — again inside the rewrite after the restart
if want("cut"):
    b = bot(60)
    _orig, ph = b._load, {"n": 0}

    def _load_cut(_orig=_orig):
        m = _orig()
        lg = m.log_trade_history

        def l2(sym, msg):
            if str(msg).startswith("💠") and ph["n"] < 3:
                ph["n"] += 1
                raise Cut("cut between a sale's two lines")
            lg(sym, msg)
        m.log_trade_history = l2
        return m
    b._load = _load_cut
    run(b, DOWN_UP * 2)
    red, ri = lines(b)
    n = sales(b)
    ok("cut between a sale's two lines (×3, once inside the rewrite): each line written once after the restart · both lines of every"
       " sale · books = wallet", ph["n"] == 3 and n >= 6 and len(red) == n and len(ri) == n and not b.errors,
       (ph["n"], n, len(red), len(ri), b.errors[:2]))


# ── random markets: both sides, wallet levels, partial fills
if want("random"):
    bad = []
    for seed in range(SEEDS):
        rng = random.Random(seed)
        pct = rng.choice([100, 100, 60, 25, 0])
        c = Clock()
        ex = Ex(c, base=100, quote=1000, partial=(0.5 if seed % 2 else 0), seed=seed)
        b = bot(pct, {"step_parts": rng.choice([2, 3, 4]), "grid_percentage": rng.choice([0.01, 0.02, 0.03]),
                      "step_sell": rng.choice([0.005, 0.01]), "step_first": rng.choice([0.004, 0.01]), "up_groups": 2}, ex=ex)
        px, P = 1.0, []
        for _ in range(260):
            px = max(0.75, min(1.12, px * (1 + rng.gauss(0, 0.006)) + 0.04 * (1.0 - px)))   # (around the start: both sides trade)
            P.append(round(px, 4))
        b.run(walk(P, hold=rng.choice([6.0, 12.0])))
        rb = b.st.get("reinvest") or {}
        red, ri = lines(b)
        n = sales(b)
        ln = len(set(red) | set(ri))
        if b.errors or b.on_loop.bad or ln != n or (pct == 100 and red) or (pct == 0 and ri) or not rb.get("on"):
            bad.append((seed, pct, n, ln, len(red), len(ri), b.errors[:2], b.on_loop.bad[:1]))
        if pct and n and float(rb.get("credited") or 0) <= 0:
            bad.append((seed, pct, "sold but nothing reinvested", n))
    ok(f"random markets × {SEEDS} (both sides · wallet levels · partial fills · 0–100%): books = wallet every loop · each sale's lines once ·"
       " buy = base + growth", not bad, bad[:3])

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
