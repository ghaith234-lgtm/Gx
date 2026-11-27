# 🔀 a fast copy of the «شبكة عملتين» engine (devtests/pair/eng/main_pair.py) for long runs on real 1-minute prices — checked against
#   the real engine (pairsim) on random and real-spec markets: the same sales, profit and wallet to 6 decimals. Used by ci/pair_replay.py.
# A fast copy of the «شبكة عملتين» engine (devtests/pair/eng/main_pair.py) for long random runs — same slots, same pick order,
# same two IOC legs through USDT (sell at the bid, buy at the ask, 0.1% each order, buy fee in the coin, sell fee in USDT),
# same caps (leg A 0.2% · leg B 0.05%), same «sell only with profit at the worst price», same profit split (main / half / other),
# same dust (USDT left under the minimum stays the bot's with its cost and joins the next sale), OKX lot/tick/min.
# Fills are whole (IOC at the touch, deep book) and both legs happen at the same quote (the real bot does them within a second).
import math


def floor_step(x, st):
    return math.floor(x / st + 1e-9) * st if st > 0 else x


def ceil_step(x, st):
    return math.ceil(x / st - 1e-9) * st if st > 0 else x


class PairModel:
    def __init__(self, r0, g, mv, dn, up, pt, so, sm, fee=0.001, cap=0.002, capb=0.0005, spread=0.0002):
        """so / sm = (tick, lot, min) of OTHER-USDT / MAIN-USDT"""
        self.g, self.mv, self.pt, self.fee, self.cap, self.capb, self.sp = g, mv, pt, fee, cap, capb, spread
        self.so, self.sm = so, sm
        self.S = []
        for j in range(-dn, up):
            bp = r0 * (1 + g) ** j
            s = {"j": j, "bp": bp, "sp": bp * (1 + g), "side": "buy", "q": 0.0, "c": 0.0, "dq": 0.0, "dc": 0.0, "n": 0}
            if j >= 0:
                s.update(side="sell", q=mv / bp, c=mv)
            self.S.append(s)
        self.main_book = dn * mv
        self.main_start = self.main_book
        self.other_start = sum(s["q"] for s in self.S)
        self.total_profit = 0.0
        self.profit_other = 0.0
        self.usd_dust = 0.0
        self.dust_cost = 0.0
        self.sales = 0
        self.buys = 0
        self.fees_usd = 0.0
        # the bot's coins (what the wallet holds for it)
        self.w_main, self.w_other, self.w_usd = self.main_book, self.other_start, 0.0
        import heapq
        self._hq = heapq
        self.j0 = -dn                                     # slot index = j - j0
        self.hs = [s["j"] for s in self.S if s["side"] == "sell"]    # lowest sell first
        self.hb = [-s["j"] for s in self.S if s["side"] == "buy"]    # highest buy first
        heapq.heapify(self.hs)
        heapq.heapify(self.hb)

    def _top(self, h, side, sign):
        while h:
            j = sign * h[0]
            if self.S[j - self.j0]["side"] == side:
                return self.S[j - self.j0]
            self._hq.heappop(h)
        return None

    def _set_side(self, s, side):
        s["side"] = side
        self._hq.heappush(self.hs if side == "sell" else self.hb, s["j"] if side == "sell" else -s["j"])

    # quotes as pairsim makes them from a mid price
    def _q(self, px, spec):
        tick = spec[0]
        bid = max(tick, math.floor(px * (1 - self.sp) / tick + 1e-9) * tick)
        ask = math.ceil(px * (1 + self.sp) / tick - 1e-9) * tick
        return bid, ask

    def _fmt(self, q, spec):
        q = floor_step(q + 1e-12, spec[1])
        return 0.0 if q < spec[2] - 1e-12 else q

    def _leg_b(self, usd, ask, spec):
        """buy with the held dollar until what is left is under one lot / the minimum ⇒ (coins got after the fee, dollar left)"""
        got = 0.0
        px = ceil_step(ask * (1 + self.capb), spec[0])
        for _ in range(4):
            qty = self._fmt(usd / px * (1 - 1e-9), spec)
            if qty <= 0:
                break
            usd -= qty * ask
            got += qty * (1 - self.fee)
            self.fees_usd += qty * self.fee * ask
        return got, usd

    def step(self, pm, po, max_ops=400):
        """one look at the prices (the real bot looks every 2 seconds and swaps at once) ⇒ every swap the prices allow"""
        bo, ao = self._q(po, self.so)
        bm, am = self._q(pm, self.sm)
        r_buy, r_sell = ao / bm, bo / am
        f, cap = self.fee, self.cap
        w = bo * (1 - cap) * (1 - f) / (am * (1 + cap)) * (1 - f)          # main per other at the worst price the caps allow
        min_usd_m = 1.5 * self.sm[2] * am
        n = 0
        while n < max_ops:
            n += 1
            # ── the nearest sell above (lowest sp) with profit at the worst price
            pick = None
            best = None
            top = self._top(self.hs, "sell", 1)
            if top is not None and r_sell >= top["sp"] - 1e-15:
                def ok_(s):
                    qt = s["q"] + s["dq"]
                    return not (self._fmt(qt, self.so) <= 0 or qt * bo < min_usd_m or qt * w <= s["c"] + 1e-12)
                if ok_(top):
                    best = top
                else:                                     # (rare) the nearest one can't sell yet ⇒ the next ones in order
                    for s in sorted((x for x in self.S if x["side"] == "sell" and r_sell >= x["sp"] - 1e-15), key=lambda x: x["sp"]):
                        if ok_(s):
                            best = s
                            break
            if best is not None:
                pick = (best, "sell")
            elif self.main_book > 0:
                top = self._top(self.hb, "buy", -1)
                if top is not None and r_buy <= top["bp"] + 1e-15 and self._fmt(min(self.mv, self.main_book), self.sm) > 0:
                    pick = (top, "buy")
            if pick is None:
                return
            s, kind = pick
            if kind == "buy":
                sz = self._fmt(min(self.mv, self.main_book), self.sm)
                usd = sz * bm * (1 - f)
                self.fees_usd += sz * bm * f
                got, usd = self._leg_b(usd, ao, self.so)
                self.w_main -= sz
                self.w_other += got
                self.main_book -= sz
                self.usd_dust += max(0.0, usd)
                self.w_usd += max(0.0, usd)
                if got > 0:
                    s.update(q=s["q"] + got, c=s["c"] + sz + s["dc"], dc=0.0)
                    self._set_side(s, "sell")
                    self.buys += 1
                else:
                    self.dust_cost += sz
            else:
                qt = s["q"] + s["dq"]
                qs = qt
                if self.pt in ("other", "half"):
                    want = s["c"] if self.pt == "other" else s["c"] + 0.5 * max(0.0, qt * w - s["c"])
                    qs = min(qt, ceil_step(want / w, self.so[1]))
                sz = self._fmt(qs, self.so)
                keep = max(0.0, qt - sz) if self.pt in ("other", "half") else 0.0
                if sz <= 0:
                    return
                usd = sz * bo * (1 - f)
                self.fees_usd += sz * bo * f
                usd += self.usd_dust
                dcost = self.dust_cost
                self.w_usd -= self.usd_dust
                self.usd_dust, self.dust_cost = 0.0, 0.0
                got, usd = self._leg_b(usd, am, self.sm)
                self.w_other -= sz
                self.w_main += got
                self.usd_dust += max(0.0, usd)
                self.w_usd += max(0.0, usd)
                if got <= 0:
                    self.dust_cost += s["c"] + dcost
                    s.update(q=max(0.0, qt - sz), dq=0.0, c=0.0)
                    if s["q"] <= self.so[1] * 0.5:
                        s.update(q=0.0, c=0.0)
                        self._set_side(s, "buy")
                    continue
                cost = s["c"] + dcost
                profit = got - cost
                self.main_book += got
                self.total_profit += profit
                left = max(0.0, qt - sz)
                kept = min(left, keep)
                self.profit_other += kept
                s.update(q=0.0, c=0.0, dq=max(0.0, left - kept), n=s["n"] + 1)
                self._set_side(s, "buy")
                self.sales += 1

    def _bounds(self):
        ts = self._top(self.hs, "sell", 1)
        tb = self._top(self.hb, "buy", -1) if self.main_book > 0 else None
        return (tb["bp"] if tb else 0.0), (ts["sp"] if ts else float("inf"))

    def run(self, PM, PO, margin=0.003):
        """every price look in order · a look where the ratio is far from the next buy and the next sell is skipped (nothing to do)"""
        lo, hi = self._bounds()
        for pm, po in zip(PM, PO):
            r = po / pm
            if lo * (1 + margin) < r < hi * (1 - margin):
                continue
            self.step(pm, po)
            lo, hi = self._bounds()
