# 🛤️ v3.34.0 (+ 📉📈 v3.35.0 «by percentage»): the value-path bot's math on a price series — the SAME rules as the engine (vpath.py, embedded in the dashboard):
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


def _pm_step(px, T, Q, Cst, mo, cap, floor_on, fee, spread):
    """one step of the «by percentage» mode — the engine's rules (same as a time step, no band: the level is the threshold)
    ⇒ (action, Q, cost, dollars bought, dollars received, realized, fee $)"""
    ask, bid = px * (1 + spread / 2), px * (1 - spread / 2)
    gap = T - Q * px
    if abs(gap) <= 0.01:
        return "hold", Q, Cst, 0.0, 0.0, 0.0, 0.0
    if gap > 0:
        amt = gap
        if mo > 0:
            amt = min(amt, mo)
        if cap > 0:
            amt = min(amt, cap - Cst)
        amt = int(max(0.0, amt) * 100 + 1e-9) / 100.0
        if cap > 0 and cap - Cst < MIN_USD:
            return "cap", Q, Cst, 0.0, 0.0, 0.0, 0.0
        if amt < MIN_USD:
            return "small", Q, Cst, 0.0, 0.0, 0.0, 0.0
        return "buy", Q + amt / ask * (1 - fee), Cst + amt, amt, 0.0, 0.0, amt * fee
    q = min(-gap / bid, Q)
    if q * bid < MIN_USD:
        return "small", Q, Cst, 0.0, 0.0, 0.0, 0.0
    if floor_on and Q > 0 and Cst > 0 and bid < (Cst / Q) * (1 + FLOOR_M) / (1 - fee):
        return "floor", Q, Cst, 0.0, 0.0, 0.0, 0.0
    usd = q * bid * (1 - fee)
    cost = Cst * q / Q if Q > 0 else 0.0
    Q2, C2 = Q - q, Cst - cost
    if Q2 <= 1e-12:
        Q2, C2 = 0.0, 0.0
    return "sell", Q2, C2, 0.0, usd, usd - cost, q * bid * fee


def va_sim_price(O, Hh, L, Cc, i0, i1, p, fee=0.001, spread=0.0005, track=False, ticks=None):
    """📉📈 v3.35.0 «by percentage»: a step each time the price crosses a level of the grid (every drop% down / rise% up from the last step)
    — first step at the close of hour i0 · inside each hour the price walks open → low → high → close (a green hour) or open → high → low → close
    (a red one) and every level it crosses is one step at the level price (the engine looks every few seconds) · growing target: + step per
    level down, − step per level up (never under the first) · budget full ⇒ the level is not counted (the anchor still moves)"""
    start, step = float(p["start"]), float(p["step"])
    d, u = float(p["drop"]) / 100.0, float(p.get("rise", p["drop"])) / 100.0
    mo, cap, floor_on = float(p.get("max_order", 0) or 0), float(p.get("cap", 0) or 0), bool(p.get("floor", True))
    Q = Cst = buy = sell = fees = realized = 0.0
    trades = sells = steps = cap_full = 0
    peak = pl_min = 0.0
    rows = []
    a, Q, Cst, b_, s_, r_, f_ = _pm_step(Cc[i0], start, 0.0, 0.0, mo, cap, floor_on, fee, spread)
    buy += b_; fees += f_; trades += a == "buy"; steps += 1
    anchor, lvl, cur = Cc[i0], 0, Cc[i0]
    peak = buy
    if ticks is not None:                                   # (checks: the price ticks the engine would see, in order)
        ticks.append(Cc[i0])
    for i in range(i0 + 1, i1):
        o, h, l, c = O[i], Hh[i], L[i], Cc[i]
        for tgt_px in ((o, l, h, c) if c >= o else (o, h, l, c)):
            while True:
                if tgt_px < cur and tgt_px <= anchor * (1 - d) * (1 + 1e-12):
                    px, lv2 = anchor * (1 - d), lvl + 1
                elif tgt_px > cur and tgt_px >= anchor * (1 + u) * (1 - 1e-12):
                    px, lv2 = anchor * (1 + u), max(0, lvl - 1)
                else:
                    break
                a, Q, Cst, b_, s_, r_, f_ = _pm_step(px, start + step * lv2, Q, Cst, mo, cap, floor_on, fee, spread)
                steps += 1
                if a == "cap":
                    cap_full += 1
                else:
                    lvl = lv2
                buy += b_; sell += s_; realized += r_; fees += f_
                trades += a in ("buy", "sell"); sells += a == "sell"
                anchor, cur = px, px
                if ticks is not None:
                    ticks.append(px)
                if track:
                    rows.append((i, a, round(px, 10), round(Q, 10), round(Cst, 8), lvl))
            cur = tgt_px
            if ticks is not None:
                ticks.append(tgt_px)
        peak = max(peak, buy - sell)
        pl_min = min(pl_min, sell - buy + Q * c)
    pl = sell - buy + Q * Cc[i1 - 1]
    out = {"pl": pl, "peak": peak, "ret": (pl / peak * 100) if peak > 0 else 0.0, "pl_min": pl_min, "trades": trades, "sells": sells,
           "fees": fees, "realized": realized, "Q": Q, "C": Cst, "buy": buy, "sell": sell, "steps": steps, "frozen": cap_full,
           "cap_full": cap_full, "brakes": 0, "n": steps, "lvl": lvl}
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
