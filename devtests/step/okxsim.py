# 🪜 okxsim — a mock OKX + a runner for the graded-grid engine (no network · fake clock · fake keys · real engine code)
#
#   The engine (devtests/step/eng/main_step.py — extract_engine.py writes it from the dashboard) runs its own start_bot() loop
#   unchanged. The runner owns the clock: every time.sleep() of the engine advances the fake clock and hands control to the
#   scenario (price moves, button presses, faults). A power cut is a BaseException raised at any chosen moment (before/after
#   a state save, an order sent, a cancel, a log line) — nothing in the engine catches it, like a real process death; the
#   runner then starts a fresh copy of the module on the same folder (= the bot restarting after the cut).
#
#   Checked at every loop of the engine (audit()):
#     coins   : wallet coins = what the bot's slots hold (+ fee dust · partial fills · fills not yet processed)
#     dollars : wallet dollars = start + booked profit − what the held coins cost (+ partial fills · fills not yet processed)
#     orders  : every live order with the bot's id belongs to exactly one slot · no slot points at an order OKX doesn't have
#     cross   : the bot's own buys stay under its own sells
#     log     : one 🟢 line per completed buy · one 🔴 line per completed sell · Σ profit in the 🔴 lines = booked profit
import contextlib, importlib.util, io, json, os, random, shutil, string, sys, tempfile, types, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime as _RealDT, timezone
from decimal import Decimal, ROUND_FLOOR
import time as _real_time
import requests as _requests_loaded   # loaded here with the real socket, before the engine imports it under the fake one  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.environ.get("STEP_ENGINE") or os.path.join(HERE, "eng", "main_step.py")   # STEP_ENGINE=… tests another copy


class Cut(BaseException):
    """⚡ power cut: the process dies here (no `except Exception` in the engine can catch it)"""


class Stop(BaseException):
    """the scenario is over"""


def D(x):
    return Decimal(str(x))


def _no_network(*a, **k):
    raise AssertionError("network used by the engine (urllib) — the mock must answer everything")


urllib.request.urlopen = _no_network          # 🔒 nothing reaches the internet from any test


# ─────────────────────────────── clock ───────────────────────────────
class Clock:
    def __init__(self, t0=1_760_000_000.0):
        self.t = float(t0)
        self.hook = None                       # hook(dt, caller) — the runner's scenario step

    def time(self):
        return self.t

    def sleep(self, dt, caller=None):
        self.t += float(dt)
        if self.hook:
            self.hook(float(dt), caller or sys._getframe(1).f_code.co_name)

    def tick(self, dt):                        # time passes inside a call (latency) — no scenario step
        self.t += float(dt)


class _FakeTime:
    def __init__(self, clock):
        self._c = clock

    def time(self):
        return self._c.time()

    def sleep(self, dt):
        self._c.sleep(dt, sys._getframe(1).f_code.co_name)    # the engine function that slept (start_bot = a loop boundary)

    def __getattr__(self, n):
        return getattr(_real_time, n)


class _FakeSocketMod:
    """the engine's `socket`: its «already running» lock binds a port per bot id — real ports would collide between test
    processes running in parallel, so the lock is kept per process (a second copy of the SAME bot in one process still fails)"""
    AF_INET, SOCK_STREAM, error, timeout = 2, 1, OSError, TimeoutError
    bound = set()

    class socket:
        def __init__(self, *a, **k):
            self.port = None

        def bind(self, addr):
            if addr in _FakeSocketMod.bound:
                raise OSError("address in use")
            _FakeSocketMod.bound.add(addr)
            self.port = addr

        def close(self):
            _FakeSocketMod.bound.discard(self.port)

    @staticmethod
    def setdefaulttimeout(t):
        pass


def _fake_dt(clock):
    class FakeDT(_RealDT):
        @classmethod
        def now(cls, tz=None):
            return _RealDT.fromtimestamp(clock.t, tz)
    return FakeDT


# ─────────────────────────────── exchange ───────────────────────────────
class Ex:
    """OKX spot, one instrument, one account. Resting buys fill when the price falls to them, sells when it rises to them
    (maker, at their own price); an order that crosses the price fills at once at the price (taker). Fees: buy fee in the
    coin, sell fee in USDT (OKX default) — or everything in OKB (fee_mode='okb')."""

    def __init__(self, clock, sym="XRP-USDT", price=1.0, tick="0.0001", lot="0.000001", mn="0.1", base=0, quote=0,
                 maker="0.0008", taker="0.001", fee_mode="std", okb=0, okb_px="50", partial=0.0, seed=1):
        self.clock, self.sym = clock, sym
        self.base, self.quote = sym.split("-")
        self.price = D(price)
        self.tick, self.lot, self.mn = D(tick), D(lot), D(mn)
        self.bal = Counter({self.base: D(base), self.quote: D(quote), "OKB": D(okb)})
        self.maker, self.taker, self.fee_mode, self.okb_px = D(maker), D(taker), fee_mode, D(okb_px)
        self.partial = float(partial)          # >0: a resting order touched by the price fills only this share (≥ 1 lot)
        self.rng = random.Random(seed)
        self.orders, self.by_cl, self.n = {}, {}, 0
        self.fills = []                        # (ordId, clOrdId, side, px, sz, maker)
        self.late = []                         # [t_land, kind, params]
        self.fault = None                      # fault(op, params) -> None | "drop" | "lost" | ("late", s) | ("code", c) | ("ambig", placed)
        self.down = False                      # internet down: every call raises
        self.latency = 0.0                     # seconds every call takes (clock moves, no scenario step)
        self.calls = Counter()
        self.cut = None                        # cut(op, when) — the runner's power-cut hook ('before'/'after' an action)

    # ---- helpers
    def _mult(self, x, step):
        return (x / step) == (x / step).to_integral_value()

    def _rem(self, o):
        return o["sz"] - o["acc"]

    def locked(self, ccy):
        t = D(0)
        for o in self.orders.values():
            if o["state"] in ("live", "partially_filled"):
                if o["side"] == "buy" and ccy == self.quote:
                    t += self._rem(o) * o["px"]
                if o["side"] == "sell" and ccy == self.base:
                    t += self._rem(o)
        return t

    def avail(self, ccy):
        return self.bal[ccy] - self.locked(ccy)

    def pending(self):
        return [o for o in self.orders.values() if o["state"] in ("live", "partially_filled")]

    def rec(self, o):                          # the order as OKX's JSON shows it
        return {"ordId": o["ordId"], "clOrdId": o["cl"], "instId": self.sym, "side": o["side"], "px": str(o["px"]),
                "sz": str(o["sz"]), "accFillSz": str(o["acc"]), "avgPx": str(o["accv"] / o["acc"]) if o["acc"] > 0 else "",
                "fee": str(-o["fee"]), "feeCcy": o["feeCcy"], "state": o["state"], "ordType": "limit",
                "cTime": str(int(o["t"] * 1000)), "uTime": str(int(self.clock.t * 1000))}

    # ---- fills
    def _fill(self, o, sz, px, maker):
        if sz <= 0:
            return
        rate = self.maker if maker else self.taker
        val = sz * px
        if o["side"] == "buy":
            self.bal[self.quote] -= val
            if self.fee_mode == "okb":
                f = val * rate / self.okb_px
                self.bal["OKB"] -= f
                self.bal[self.base] += sz
                o["fee"] += f; o["feeCcy"] = "OKB"
            else:
                f = sz * rate
                self.bal[self.base] += sz - f
                o["fee"] += f; o["feeCcy"] = self.base
        else:
            self.bal[self.base] -= sz
            if self.fee_mode == "okb":
                f = val * rate / self.okb_px
                self.bal["OKB"] -= f
                self.bal[self.quote] += val
                o["fee"] += f; o["feeCcy"] = "OKB"
            else:
                f = val * rate
                self.bal[self.quote] += val - f
                o["fee"] += f; o["feeCcy"] = self.quote
        o["acc"] += sz
        o["accv"] += val
        o["state"] = "filled" if o["acc"] >= o["sz"] else "partially_filled"
        self.fills.append((o["ordId"], o["cl"], o["side"], px, sz, maker))

    def move(self, price):
        """the market goes to `price`: resting orders it reaches fill at their own price (maker)"""
        self.price = D(price)
        self._land()
        for o in sorted(self.pending(), key=lambda o: o["t"]):
            hit = (o["side"] == "buy" and self.price <= o["px"]) or (o["side"] == "sell" and self.price >= o["px"])
            if not hit or o.get("foreign_frozen"):
                continue
            sz = self._rem(o)
            if self.partial > 0 and o["acc"] == 0:      # the first touch fills a share, the next one the rest
                part = (sz * D(self.partial) / self.lot).to_integral_value(rounding=ROUND_FLOOR) * self.lot
                sz = max(min(sz, self.lot), min(sz, part)) if part > 0 else min(sz, self.lot)
            self._fill(o, sz, o["px"], True)

    # ---- actions
    def _place(self, p):
        cl, side = str(p.get("clOrdId") or ""), p["side"]
        px, sz = D(p["px"]), D(p["sz"])
        bad = lambda sc, msg: {"code": "1", "msg": "Operation failed.", "data": [{"clOrdId": cl, "ordId": "", "sCode": sc, "sMsg": msg}]}
        if cl and cl in self.by_cl:
            return bad("51016", "Duplicated clOrdId")
        if px <= 0 or not self._mult(px, self.tick):
            return bad("51006", "Order price is not a multiple of the tick size")      # a 51xxx rejection
        if sz <= 0 or not self._mult(sz, self.lot):
            return bad("51121", "Order quantity must be a multiple of the lot size")
        if sz < self.mn:
            return bad("51020", "Order amount should be greater than the min available amount")
        if side == "buy" and px * sz > self.avail(self.quote):
            return bad("51008", "Order failed. Insufficient USDT balance in account")
        if side == "sell" and sz > self.avail(self.base):
            return bad("51008", "Order failed. Insufficient balance")
        if p.get("stpMode") == "cancel_maker":       # self-trade prevention: our resting orders it would meet are canceled
            for o in self.pending():
                if o["side"] != side and ((side == "buy" and o["px"] <= px) or (side == "sell" and o["px"] >= px)):
                    o["state"] = "canceled"; o["stp"] = True
        self.n += 1
        oid = str(700000000 + self.n)
        o = {"ordId": oid, "cl": cl, "side": side, "px": px, "sz": sz, "acc": D(0), "accv": D(0), "fee": D(0),
             "feeCcy": self.base if side == "buy" else self.quote, "state": "live", "t": self.clock.t}
        self.orders[oid] = o
        if cl:
            self.by_cl[cl] = oid
        if (side == "buy" and px >= self.price) or (side == "sell" and px <= self.price):   # crosses the price ⇒ taker now
            self._fill(o, self._rem(o), self.price, False)
        return {"code": "0", "msg": "", "data": [{"clOrdId": cl, "ordId": oid, "sCode": "0", "sMsg": "Order placed"}]}

    def _cancel(self, oid):
        o = self.orders.get(str(oid))
        if not o:
            return {"code": "1", "data": [{"ordId": oid, "sCode": "51400", "sMsg": "Cancellation failed as the order does not exist"}]}
        if o["state"] in ("filled", "canceled"):
            return {"code": "1", "data": [{"ordId": oid, "sCode": "51400", "sMsg": "Cancellation failed as the order is already completed"}]}
        o["state"] = "canceled"
        return {"code": "0", "data": [{"ordId": oid, "sCode": "0"}]}

    def _land(self):
        due = [x for x in self.late if x[0] <= self.clock.t]
        self.late = [x for x in self.late if x[0] > self.clock.t]
        for _, kind, p in due:
            if kind == "place":
                self._place(p)
            elif kind == "cancel":
                self._cancel(p)

    def call(self, op, p, act):
        """every API call goes through here: latency · internet down · injected faults · power cut before/after"""
        self.calls[op] += 1
        if self.latency:
            self.clock.tick(self.latency)
        self._land()
        if self.down:
            raise ConnectionError("network down")
        f = self.fault(op, p) if self.fault else None
        if self.cut:
            self.cut(op, "before")
        if f == "drop":
            raise TimeoutError(f"{op}: no answer (never reached OKX)")
        if isinstance(f, tuple) and f[0] == "late":
            self.late.append([self.clock.t + f[1], op, dict(p) if op == "place" else p])
            raise TimeoutError(f"{op}: timed out (reaches OKX later)")
        if isinstance(f, tuple) and f[0] == "code":
            return {"code": str(f[1]), "msg": "injected", "data": []}
        if isinstance(f, tuple) and f[0] == "ambig":
            r = act() if f[1] else None
            return {"code": "50001", "msg": "Service temporarily unavailable", "data": []}
        r = act()
        if self.cut:
            self.cut(op, "after")
        if f == "lost":
            raise TimeoutError(f"{op}: done at OKX, the answer was lost")
        return r


class _Trade:
    def __init__(self, ex):
        self.ex = ex

    def place_order(self, **p):
        return self.ex.call("place", p, lambda: self.ex._place(p))

    def get_order_list(self, **p):
        ex = self.ex
        return ex.call("list", p, lambda: {"code": "0", "msg": "", "data": [ex.rec(o) for o in
                       sorted(ex.pending(), key=lambda o: -o["t"])[:100]]})


class _Market:
    def __init__(self, ex):
        self.ex = ex

    def get_ticker(self, instId=None, *a, **k):
        ex = self.ex
        return ex.call("ticker", {}, lambda: {"code": "0", "data": [{"instId": ex.sym, "last": str(ex.price)}]})

    def get_instruments(self, instType=None, instId=None, **k):
        ex = self.ex
        return ex.call("spec", {}, lambda: {"code": "0", "data": [{"instId": ex.sym, "tickSz": str(ex.tick),
                                                                   "lotSz": str(ex.lot), "minSz": str(ex.mn)}]})


class _Resp:
    def __init__(self, j):
        self._j = j

    def json(self):
        return self._j


class _Requests:
    def __init__(self, ex):
        self.ex = ex

    def get(self, url, headers=None, timeout=None, **k):
        ex = self.ex
        u = urllib.parse.urlparse(url)
        q = dict(urllib.parse.parse_qsl(u.query))
        if u.path.endswith("/trade/order"):
            def act():
                oid = q.get("ordId") or ex.by_cl.get(q.get("clOrdId") or "")
                o = ex.orders.get(str(oid)) if oid else None
                return {"code": "0", "msg": "", "data": [ex.rec(o)]} if o else {"code": "51603", "msg": "Order does not exist", "data": []}
            return _Resp(ex.call("order", q, act))
        if u.path.endswith("/account/balance"):
            def act():
                c = q.get("ccy")
                det = [{"ccy": c, "availBal": str(ex.avail(c)), "cashBal": str(ex.bal[c])}] if ex.bal[c] != 0 else []
                return {"code": "0", "msg": "", "data": [{"details": det}]}
            return _Resp(ex.call("balance", q, act))
        raise AssertionError("unknown GET " + url)

    def post(self, url, headers=None, data=None, timeout=None, **k):
        ex = self.ex
        if url.endswith("/trade/cancel-order"):
            b = json.loads(data)
            return _Resp(ex.call("cancel", b["ordId"], lambda: ex._cancel(b["ordId"])))
        raise AssertionError("unknown POST " + url)


# ─────────────────────────────── the bot + runner ───────────────────────────────
DEFAULT_CFG = {"api_key": "FAKE-KEY", "secret_key": "FAKE-SECRET", "passphrase": "FAKE-PASS", "bot_type": "grid_step",
               "usd_value": 15.0, "step_parts": 3, "step_sell": 0.01, "grid_percentage": 0.03, "min_price": 0.7,
               "up_groups": 2, "forced_base_price": 1.0, "fee_rate": 0.0008, "step_window": 8, "is_demo": False}
DEFAULT_CFG.update(json.loads(os.environ.get("STEP_CFG") or "{}"))   # STEP_CFG='{"step_first": 0.008}' runs every test with it


class Bot:
    """one graded-grid bot folder + the runner that drives the real engine against an Ex"""

    def __init__(self, ex, cfg=None, folder=None):
        self.ex, self.clock = ex, ex.clock
        self.dir = folder or tempfile.mkdtemp(prefix="step_")
        self.cfg = dict(DEFAULT_CFG, symbol=ex.sym, **(cfg or {}))
        self.cfg.setdefault("bot_id", "HBT" + "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9)))
        with open(os.path.join(self.dir, f"config_{ex.sym}.json"), "w") as f:
            json.dump(self.cfg, f)
        self.bot_id = self.cfg["bot_id"]
        self.m = None
        self.st = None                          # the engine's live state dict (captured at its first save)
        self.coin0, self.usd0 = ex.bal[ex.base], ex.bal[ex.quote]
        self.W0 = None                          # coins the wallet slots took at birth
        self.fill_lines = []                    # every 🟢/🔴 line the engine wrote (its file trims to 1000)
        self.legacy, self.V0 = True, D(0)       # v3.36.17 engines: the wallet slots' «as if bought» basis at birth
        self.virt = {}                          # (slot, cyc) → virtual basis booked for a wallet slot's first sell
        self.unbooked = {}                      # (slot, cyc) → basis not booked when a sell ended short (coins went to fee dust)
        self.steps, self.si, self.next_t = [], 0, 0.0
        self.moments, self.cut_at, self.cuts = 0, set(), 0
        self.errors, self.orphan_seen = [], {}
        self.audit_on, self.audits = True, 0
        self.restarts = 0
        self.on_loop = None

    # ---- the engine as a fresh process
    def _load(self):
        ex, me = self.ex, self
        okx = types.ModuleType("okx")
        okx.Trade = types.ModuleType("okx.Trade")
        okx.MarketData = types.ModuleType("okx.MarketData")
        okx.Trade.TradeAPI = lambda *a, **k: _Trade(ex)
        okx.MarketData.MarketAPI = lambda *a, **k: _Market(ex)
        sys.modules.update({"okx": okx, "okx.Trade": okx.Trade, "okx.MarketData": okx.MarketData})
        name = f"step_engine_{abs(hash(self.dir))}_{self.restarts}"
        spec = importlib.util.spec_from_file_location(name, ENGINE)
        m = importlib.util.module_from_spec(spec)
        real_socket = sys.modules["socket"]
        sys.modules["socket"] = _FakeSocketMod      # only while the engine imports: it keeps this one, nothing else does
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(m)
        finally:
            sys.modules["socket"] = real_socket
        m.time = _FakeTime(self.clock)
        m.datetime = _fake_dt(self.clock)
        m.requests = _Requests(ex)
        save0, log0, fin0 = m.save_json, m.log_trade_history, m._finish
        me._fin = None

        def save_json(path, data):
            if path == m.STATE_FILE and isinstance(data, dict):
                me.st = data
                if me.W0 is None and data.get("slots"):      # the birth save: the wallet slots, untouched yet
                    me.W0 = sum(D(s["sq"]) for s in data["slots"].values() if s["j"] >= 0 and s["side"] == "sell" and not s["cyc"])
                    me.legacy = not any("spent" in s for s in data["slots"].values())     # (an engine before v3.36.17)
                    me.V0 = sum(D(str(s.get("spent") or 0)) for s in data["slots"].values() if s["j"] >= 0 and s["side"] == "sell")
            me._moment("save", "before")
            r = save0(path, data)
            if r is True and me._fin and path == m.STATE_FILE:   # the save that writes a sale: book it now (a cut right after
                fk, fpre, fod = me._fin                          # it must not lose it — the engine won't process it again)
                if fpre.get("side") == "sell" and ((data.get("slots") or {}).get(fk) or {}).get("side") == "buy":
                    _book(fk, fpre, fod)
            me._moment("save", "after")
            return r

        def log_trade_history(sym, msg):
            me._moment("log", "before")
            log0(sym, msg)
            if str(msg).startswith(("🟢", "🔴")):     # every fill line as written — the engine's file keeps only its newest 1000
                me.fill_lines.append(msg)
            me._moment("log", "after")

        def _book(key, pre, od):                  # a sale's basis the books need: wallet coins «as if bought» · coins kept back
            sq = float(pre.get("sq") or 0)
            sold = float(pre.get("acc") or 0) + float(od.get("accFillSz") or 0)
            basis = float(pre.get("spent") or 0) if float(pre.get("cost") or 0) > 0 else float(pre["q"]) * float(pre["bp"])
            used = basis * (min(1.0, sold / sq) if sq > 0 else 1.0)
            if float(pre.get("cost") or 0) > 0:
                me.unbooked[(key, pre.get("cyc"))] = basis - used
            else:
                me.virt[(key, pre.get("cyc"))] = used

        def _finish(state, key, s, od):           # (only to book the wallet slots' virtual basis — the engine's own maths runs)
            pre = dict(s)
            me._fin = (key, pre, od)
            try:
                r = fin0(state, key, s, od)
            finally:
                me._fin = None
            if pre.get("side") == "sell" and s.get("side") == "buy":
                _book(key, pre, od)                # (same key as the save's booking — once)
            return r

        m.save_json, m.log_trade_history, m._finish = save_json, log_trade_history, _finish
        ex.cut = lambda op, when: me._moment(op, when)
        self.m = m
        return m

    def _moment(self, op, when):
        self.moments += 1
        if self.moments in self.cut_at:
            self.cut_at.discard(self.moments)
            self.cuts += 1
            raise Cut(f"{op} {when} #{self.moments}")

    def _hook(self, dt, caller):
        if caller != "start_bot":               # a sleep inside a save/destruct retry — not a loop boundary
            return
        self.ex._land()
        if self.audit_on:
            self.audit()
        if self.on_loop:
            self.on_loop(self)
        while self.si < len(self.steps) and self.clock.t >= self.next_t:
            self._apply(self.steps[self.si])
            self.si += 1
        if self.si >= len(self.steps) and self.clock.t >= self.next_t:
            raise Stop()

    def _apply(self, step):
        kind = step[0]
        if kind == "px":                         # ("px", price, hold_seconds)
            self.ex.move(step[1])
            self.next_t = self.clock.t + step[2]
        elif kind == "do":                       # ("do", fn) — fn(bot)
            step[1](self)
        elif kind == "wait":
            self.next_t = self.clock.t + step[1]

    def run(self, steps, cuts=(), off=0.0, off_steps=()):
        """run the engine through `steps`; a power cut at each moment number in `cuts` (the bot is off `off` seconds and
        `off_steps` happen while it is off, then it starts again from its files)"""
        self.steps = list(steps); self.si = 0; self.next_t = self.clock.t
        self.cut_at = set(cuts)
        self.clock.hook = self._hook
        cwd0 = os.getcwd()
        os.chdir(self.dir)                       # the engine reads/writes its files in the folder it runs in
        try:
            self._run_loop(off, off_steps)
        finally:
            os.chdir(cwd0)
            self.clock.hook = None
        if self.audit_on and self.st is not None:
            self.audit()
        return self

    def _run_loop(self, off, off_steps):
        while True:
            m = self._load()
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    m.start_bot()
            except Stop:
                break
            except Cut:
                self.restarts += 1
                try:
                    m.global_lock_socket.close()
                except Exception:
                    pass
                self.st = None
                for st in off_steps:
                    if st[0] == "px":
                        self.ex.move(st[1])
                self.clock.t += off
                self.ex._land()
                continue
            except SystemExit:                    # 💣 destruct ends the process
                break
        try:
            self.m.global_lock_socket.close()
        except Exception:
            pass

    # ---- reading the engine's books
    def disk(self):
        try:
            with open(os.path.join(self.dir, f"grid_state_{self.ex.sym}.json")) as f:
                return json.load(f)
        except Exception:
            return {}

    def hist(self):
        try:
            with open(os.path.join(self.dir, f"trade_history_{self.ex.base}.json"), encoding="utf-8") as f:
                return [e.get("msg", "") for e in json.load(f)]
        except Exception:
            return []

    def mine(self):
        return [o for o in self.ex.orders.values() if o["cl"].startswith(self.bot_id)]

    def _ex_of(self, o):
        if o.get("id"):
            return self.ex.orders.get(str(o["id"]))
        oid = self.ex.by_cl.get(o.get("cl") or "")
        return self.ex.orders.get(oid) if oid else None

    def audit(self):
        st = self.st
        if not st or not st.get("slots"):
            return
        self.audits += 1
        S = st["slots"]
        ex = self.ex
        if self.W0 is None:
            self.err("the birth save was never seen (W0 unknown)")
            return
        L = D(st.get("fee_dust") or 0)
        U = D(st.get("total_profit") or 0)
        if not self.legacy:                      # v3.36.17: every basis dollar is either still held (a selling slot's spent ·
            U += self.V0                         # any slot's leftover dc) or was used by a sale ⇒ usd = usd0 + profit + V0 − held
        refd = {}
        for k, s in S.items():
            acc, accv, accf = D(s.get("acc") or 0), D(s.get("accv") or 0), D(s.get("accf") or 0)
            if not self.legacy:
                L += D(str(s.get("dq") or 0))
                U -= D(str(s.get("dc") or 0))
            if s["side"] == "sell":
                L += D(s["sq"]) - acc
                U += accv - accf
                if not self.legacy or float(s.get("cost") or 0) > 0:
                    U -= D(str(s.get("spent") or 0))
            else:
                L += acc - accf
                U -= accv
            o = s.get("o") or {}
            if o:
                eo = self._ex_of(o)
                if o.get("st") == "live" and not eo:
                    self.err(f"ghost: slot {k} points at order {o.get('id')} OKX doesn't have")
                if eo:
                    if eo["ordId"] in refd:
                        self.err(f"two slots on one order {eo['ordId']}: {refd[eo['ordId']]} · {k}")
                    refd[eo["ordId"]] = k
                    if eo["acc"] > 0:              # fills OKX did and the engine hasn't processed yet
                        if eo["side"] == "buy":
                            L += eo["acc"] - (eo["fee"] if eo["feeCcy"] == ex.base else 0)
                            U -= eo["accv"]
                        else:
                            L -= eo["acc"]
                            U += eo["accv"] - (eo["fee"] if eo["feeCcy"] == ex.quote else 0)
        if self.legacy:
            for (key, cyc), v in self.virt.items():
                U += D(v)
            for (key, cyc), v in self.unbooked.items():
                U -= D(v)
        coins, usd = ex.bal[ex.base], ex.bal[ex.quote]
        tol_c = max(D("1e-9"), abs(coins) * D("1e-10")) + ex.lot * D("1e-6")
        if abs(coins - (self.coin0 - self.W0 + L)) > tol_c:
            self.err(f"coins: wallet {coins} ≠ books {self.coin0 - self.W0 + L} (Δ {coins - (self.coin0 - self.W0 + L)})")
        if abs(usd - (self.usd0 + U)) > D("1e-6") + abs(usd) * D("1e-10"):
            self.err(f"dollars: wallet {usd} ≠ books {self.usd0 + U} (Δ {usd - (self.usd0 + U)})")
        for o in self.mine():                    # every live order of the bot belongs to a slot
            if o["state"] in ("live", "partially_filled") and o["ordId"] not in refd:
                n = self.orphan_seen.get(o["ordId"], 0) + 1
                self.orphan_seen[o["ordId"]] = n
                if n >= 3:
                    self.err(f"stray order {o['ordId']} {o['side']} {o['sz']}@{o['px']} survives {n} loops")
        live = [o for o in self.mine() if o["state"] in ("live", "partially_filled")]
        hb = max((o["px"] for o in live if o["side"] == "buy"), default=None)
        ls = min((o["px"] for o in live if o["side"] == "sell"), default=None)
        if hb is not None and ls is not None and hb >= ls:
            self.err(f"self-cross: own buy {hb} ≥ own sell {ls}")
        if not st.get("fx_log"):
            h = self.fill_lines                  # (not the file: it keeps its newest 1000 lines only)
            nb = sum(1 for x in h if x.startswith("🟢 [شراء"))
            ns = sum(1 for x in h if x.startswith("🔴 [بيع"))
            cyc = sum(int(s.get("cyc") or 0) for s in S.values())
            sells = sum(int(s.get("n") or 0) for s in S.values())
            if ns != sells or nb != cyc - sells:
                self.err(f"log: 🟢 {nb} / 🔴 {ns} lines ≠ slots {cyc - sells} buys / {sells} sells")

    def err(self, msg):
        if len(self.errors) < 20:
            self.errors.append(f"t+{int(self.clock.t - 1_760_000_000)}s {msg}")


def walk(prices, hold=6.0):
    return [("px", p, hold) for p in prices]
