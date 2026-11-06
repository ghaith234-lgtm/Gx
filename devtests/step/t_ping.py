# 🪜 📶 high ping on the graded-grid engine: every call to OKX takes `delay` (the clock moves while it waits). A call slower
#   than its timeout (5 s) fails on our side while OKX still does it: an order / a cancel lands later — possibly after the
#   bot already asked «do you know it?» and heard «no». Profiles: steady 0.3 · 1 · 3 · 4.9 s and spiky (~1 s, 8% of the calls
#   6–70 s) over random markets with jumps. Audited at every loop: books = wallet · no order twice · every live order belongs
#   to one slot · own buys under own sells; at the end: it traded, never bought over / sold under its price, every sell paid.
#   python3 devtests/step/t_ping.py [-q]
import math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk

Q = "-q" in sys.argv
TIMEOUT = 5.0
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:600]}"), flush=True)


LINE = re.compile(r"^(🟢|🔴) \[(?:شراء|بيع) فوري\] السعر: ([0-9.e+-]+) \| الكمية: ([0-9.e+-]+)(?: \| الربح: ([+-][0-9.e+-]+)\$)?.* المستوى (-?\d+) · الجزء (\d+)/")


def discipline(b):
    S, bad = b.st["slots"], []
    for msg in b.hist():
        m = LINE.match(msg)
        if not m:
            continue
        s = S.get(f"{m.group(5)}:{m.group(6)}")
        px = float(m.group(2))
        if m.group(1) == "🟢" and px > s["bp"] * (1 + 1e-9):
            bad.append(("bought over", msg[:80]))
        if m.group(1) == "🔴" and (px < s["sp"] * (1 - 1e-9) or float(m.group(4)) <= 0):
            bad.append(("sold under / no profit", msg[:80]))
    return bad


def pinger(clock, rng, prof):
    def f(op, p):
        if prof == "spiky":
            d = rng.uniform(6, 70) if rng.random() < 0.08 else rng.uniform(0.6, 1.4)
        else:
            d = prof * rng.uniform(0.85, 1.0)
        clock.tick(min(d, TIMEOUT))           # we wait at most the timeout
        if d <= TIMEOUT:
            return None
        if op in ("place", "cancel"):
            return ("late", d - TIMEOUT)          # OKX does it later; we heard nothing
        return "drop"
    return f


PROFILES = [0.3, 1.0, 3.0, 4.9, "spiky"]
for prof in PROFILES:
    bad = []
    for seed in range(4):
        rng = random.Random(900 + seed * 7 + int(PROFILES.index(prof)))
        c = Clock(); ex = Ex(c, base=150, quote=1500, partial=rng.choice([0, 0.5]))
        ex.fault = pinger(c, rng, prof)
        b = Bot(ex, {"step_parts": rng.randint(1, 4), "step_sell": rng.choice([0.006, 0.01, 0.015]),
                     "grid_percentage": rng.choice([0.02, 0.03]), "step_window": rng.choice([3, 8])})
        p, prices = 1.0, []
        for _ in range(110):
            r = rng.gauss(0, 0.012) + (rng.choice([-1, 1]) * 0.06 if rng.random() < 0.03 else 0)
            p = max(0.65, min(1.5, p * math.exp(r)))
            prices.append(p)
        b.run(walk(prices, hold=rng.choice([9.0, 20.0])))
        sells = sum(1 for m in b.hist() if m.startswith("🔴"))
        dis = discipline(b)
        if b.errors or dis or sells == 0:
            bad.append((seed, b.errors[:2], dis[:2], sells))
    name = f"{prof} s" if prof != "spiky" else "spiky (~1 s, 8% 6–70 s)"
    ok(f"ping {name} × 4 random markets ⇒ books = wallet every loop · nothing twice · trades · never over/under its price · every sell paid",
       not bad, bad[:2])

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
