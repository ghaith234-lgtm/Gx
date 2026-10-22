# 🛤️ v3.34.0: the value-path bot's math on a price series — the SAME rules as the engine (vpath.py, embedded in the dashboard):
#   target path (start + step × n) · band · max order · budget (cost of the coin held) · sell above cost only · crash brake (24 h high)
#   · skipped steps do NOT advance the target · fees (buy: from the coins · sell: from the dollars) · spread (buy at ask · sell at bid)
#   Checked against the real engine on the mock exchange (devkit p3340/v4_model.py) — same trades, same books.
FLOOR_M = 0.001
MIN_USD = 1.0


def roll_max(C, w=24):
    """R[i] = highest price in the last w hours up to i (the engine samples every 5 minutes for 24 h)"""
    from collections import deque
    out, dq = [], deque()
    for i, x in enumerate(C):
        while dq and C[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        while dq[0] < i - w:
            dq.popleft()
        out.append(C[dq[0]])
    return out


def va_sim(C, i0, i1, p, R=None, fee=0.001, spread=0.0005, track=False):
    """C: hourly prices · steps every p['every_h'] hours from i0 (inclusive) to i1 (exclusive) ⇒ results dict"""
    start, step = float(p["start"]), float(p["step"])
    bp = float(p.get("band", 2.0)) / 100.0
    mo, cap = float(p.get("max_order", 0) or 0), float(p.get("cap", 0) or 0)
    floor_on, brake = bool(p.get("floor", True)), float(p.get("brake", 0) or 0)
    every = int(p["every_h"])
    if R is None:
        R = roll_max(C)
    Q = Cst = buy = sell = fees = realized = 0.0
    n, tgt = 0, None
    trades = sells = frozen = steps = cap_full = brakes = 0
    peak = pl_min = 0.0
    rows = []
    last_px = C[i0]
    for i in range(i0, i1, every):
        px = C[i]
        last_px = px
        ask, bid = px * (1 + spread / 2), px * (1 - spread / 2)
        steps += 1
        T = start if n == 0 or tgt is None else tgt + step
        V = Q * px
        gap = T - V
        act = None
        if T <= 0:
            continue
        if abs(gap) <= max(bp * T, 0.01):
            n, tgt, act = n + 1, T, "hold"
        elif gap > 0:
            if brake > 0 and (1 - px / R[i]) * 100 >= brake:
                frozen += 1; brakes += 1; act = "brake"
            else:
                amt = gap
                if mo > 0:
                    amt = min(amt, mo)
                if cap > 0:
                    amt = min(amt, cap - Cst)
                amt = int(max(0.0, amt) * 100 + 1e-9) / 100.0
                if cap > 0 and cap - Cst < MIN_USD:
                    frozen += 1; cap_full += 1; act = "cap"
                elif amt < MIN_USD:
                    n, tgt, act = n + 1, T, "small"
                else:
                    q = amt / ask * (1 - fee)
                    Q += q; Cst += amt; buy += amt; fees += amt * fee; trades += 1
                    n, tgt, act = n + 1, T, "buy"
        else:
            q = min(-gap / bid, Q)
            if q * bid < MIN_USD:
                n, tgt, act = n + 1, T, "small"
            elif floor_on and Q > 0 and Cst > 0 and bid < (Cst / Q) * (1 + FLOOR_M) / (1 - fee):
                n, tgt, act = n + 1, T, "floor"
            else:
                usd = q * bid * (1 - fee)
                cost = Cst * q / Q if Q > 0 else 0.0
                realized += usd - cost
                Q -= q; Cst -= cost; sell += usd; fees += q * bid * fee; trades += 1; sells += 1
                if Q <= 1e-12:
                    Q, Cst = 0.0, 0.0
                n, tgt, act = n + 1, T, "sell"
        net = buy - sell
        peak = max(peak, net)
        pl = sell - buy + Q * px
        pl_min = min(pl_min, pl)
        if track:
            rows.append((i, act, round(Q, 10), round(Cst, 8), round(T, 6)))
    pl = sell - buy + Q * last_px
    out = {"pl": pl, "peak": peak, "ret": (pl / peak * 100) if peak > 0 else 0.0, "pl_min": pl_min, "trades": trades, "sells": sells,
           "fees": fees, "realized": realized, "Q": Q, "C": Cst, "buy": buy, "sell": sell, "steps": steps, "frozen": frozen,
           "cap_full": cap_full, "brakes": brakes, "n": n}
    if track:
        out["rows"] = rows
    return out


def dca_sim(C, i0, i1, every, start, step, cap, fee=0.001, spread=0.0005):
    """plain DCA with the same steps: buys the step amount each step until the budget is spent, never sells"""
    Q = spent = 0.0
    first = True
    for i in range(i0, i1, every):
        amt = start if first else step
        first = False
        if cap > 0:
            amt = min(amt, cap - spent)
        if amt < MIN_USD:
            continue
        Q += amt / (C[i] * (1 + spread / 2)) * (1 - fee)
        spent += amt
    pl = Q * C[i1 - 1] - spent
    return {"pl": pl, "peak": spent, "ret": (pl / spent * 100) if spent > 0 else 0.0}


def hold_sim(C, i0, i1, cap, fee=0.001, spread=0.0005):
    """buy the whole budget on day one and hold"""
    Q = cap / (C[i0] * (1 + spread / 2)) * (1 - fee)
    pl = Q * C[i1 - 1] - cap
    return {"pl": pl, "peak": cap, "ret": pl / cap * 100}
