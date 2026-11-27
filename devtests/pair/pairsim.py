# 🔀 pairsim — a mock OKX with two coins and the dollar + a runner for the «شبكة عملتين» engine (no network · fake clock · fake
#   keys · the real engine code). Same shape as devtests/step/okxsim.py: the engine runs its own start_bot() loop unchanged; every
#   time.sleep() of the engine advances the fake clock and hands control to the scenario. A power cut is a BaseException raised
#   at any chosen moment (before/after a state save, an order sent, an order check, a log line); the runner then starts a fresh
#   copy of the module on the same folder (= the bot restarting after the cut).
#
#   Checked at every loop of the engine (audit()):
#     coins   : every coin of the wallet = what the bot's books say it holds (main_book · the slots · profit_other · the dollar
#               dust · the swap in flight) + what the test put aside, to 1e-9 — fills the bot has not read yet included
#     log     : one 🔴 line per completed sale (no line twice) · Σ profit in the 🔴 lines = total_profit · no sale at a loss
#     dollar  : the dollar the bot holds = usd_booked (the number the dashboard reserves)
import contextlib, importlib.util, io, json, os, random, re, shutil, string, sys, tempfile, types, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime as _RealDT
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import time as _real_time
import requests as _requests_loaded   # noqa — loaded with the real socket before the engine imports it under the fake one

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.environ.get("PAIR_ENGINE") or os.path.join(HERE, "eng", "main_pair.py")


class Cut(BaseException):
    """⚡ power cut: the process dies here"""


class Stop(BaseException):
    """the scenario is over"""


def D(x):
    return Decimal(str(x))


def _no_network(*a, **k):
    raise AssertionError("network used by the engine (urllib) — the mock must answer everything")


urllib.request.urlopen = _no_network


class Clock:
    def __init__(self, t0=1_760_000_000.0):
        self.t = float(t0)
        self.hook = None

    def time(self):
        return self.t

    def sleep(self, dt, caller=None):
        self.t += float(dt)
        if self.hook:
            self.hook(float(dt), caller or sys._getframe(1).f_code.co_name)

    def tick(self, dt):
        self.t += float(dt)


class _FakeTime:
    def __init__(self, clock):
        self._c = clock

    def time(self):
        return self._c.time()

    def sleep(self, dt):
        self._c.sleep(dt, sys._getframe(1).f_code.co_name)

    def __getattr__(self, n):
        return getattr(_real_time, n)


class _FakeSocketMod:
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

        @classmethod
        def fromtimestamp(cls, t, tz=None):
            return _RealDT.fromtimestamp(t, tz)
    return FakeDT


# ─────────────────────────────── exchange ───────────────────────────────
class PEx:
    """OKX spot with several instruments against USDT and one account. Only IOC (and market) orders matter here: a buy at or above
    the ask fills at the ask, a sell at or below the bid fills at the bid — up to `depth` coins at that price (the rest is
    canceled: a partial fill) · fees: buy fee in the coin, sell fee in USDT (OKX default) — or in OKB (fee_mode='okb')."""

    def __init__(self, clock, insts=None, bal=None, taker="0.001", fee_mode="std", okb_px="50", seed=1):
        self.clock = clock
        self.ins = {}
        for k, v in (insts or {}).items():
            self.add(k, **v)
        self.bal = Counter({c: D(x) for c, x in (bal or {}).items()})
        self.taker, self.fee_mode, self.okb_px = D(taker), fee_mode, D(okb_px)
        self.rng = random.Random(seed)
        self.orders, self.by_cl, self.n = {}, {}, 0
        self.fills = []
        self.late = []
        self.fault = None              # fault(op, params) -> None | "drop" | "lost" | ("late", s) | ("code", c) | ("ambig", placed)
        self.down = False
        self.latency = 0.0
        self.calls = Counter()
        self.cut = None
        self.foreign = Counter()       # coins another bot holds frozen in its own orders (not available to anyone else)
        self.after_place = None        # after_place(order) — a scenario step between the two legs (another bot · a jump)

    def add(self, inst, px, spread="0.0002", tick="0.0001", lot="0.000001", mn="1", depth=None):
        self.ins[inst] = {"px": D(px), "sp": D(spread), "tick": D(tick), "lot": D(lot), "mn": D(mn), "depth": D(depth) if depth else None}

    def set(self, inst, px):
        self.ins[inst]["px"] = D(px)

    def bid(self, inst):
        i = self.ins[inst]
        return max(i["tick"], (i["px"] * (1 - i["sp"]) / i["tick"]).to_integral_value(rounding=ROUND_FLOOR) * i["tick"])

    def ask(self, inst):
        i = self.ins[inst]
        return (i["px"] * (1 + i["sp"]) / i["tick"]).to_integral_value(rounding=ROUND_CEILING) * i["tick"]

    def avail(self, c):
        return self.bal[c] - self.foreign[c]

    def _mult(self, x, step):
        return (x / step) == (x / step).to_integral_value()

    def rec(self, o):
        return {"ordId": o["ordId"], "clOrdId": o["cl"], "instId": o["inst"], "side": o["side"], "px": str(o["px"]), "sz": str(o["sz"]),
                "accFillSz": str(o["acc"]), "avgPx": str(o["accv"] / o["acc"]) if o["acc"] > 0 else "", "fee": str(-o["fee"]),
                "feeCcy": o["feeCcy"], "state": o["state"], "ordType": o["type"], "cTime": str(int(o["t"] * 1000)),
                "uTime": str(int(self.clock.t * 1000))}

    def _fill(self, o, sz, px):
        if sz <= 0:
            return
        base, quote = o["inst"].split("-")
        val = sz * px
        r = self.taker
        if o["side"] == "buy":
            self.bal[quote] -= val
            if self.fee_mode == "okb":
                f = val * r / self.okb_px
                self.bal["OKB"] -= f
                self.bal[base] += sz
                o["fee"] += f; o["feeCcy"] = "OKB"
            else:
                f = sz * r
                self.bal[base] += sz - f
                o["fee"] += f; o["feeCcy"] = base
        else:
            self.bal[base] -= sz
            if self.fee_mode == "okb":
                f = val * r / self.okb_px
                self.bal["OKB"] -= f
                self.bal[quote] += val
                o["fee"] += f; o["feeCcy"] = "OKB"
            else:
                f = val * r
                self.bal[quote] += val - f
                o["fee"] += f; o["feeCcy"] = quote
        o["acc"] += sz
        o["accv"] += val
        self.fills.append((o["ordId"], o["cl"], o["inst"], o["side"], px, sz))

    def _place(self, p):
        cl, side, inst = str(p.get("clOrdId") or ""), p["side"], p["instId"]
        typ = str(p.get("ordType") or "limit")
        bad = lambda sc, msg: {"code": "1", "msg": "Operation failed.", "data": [{"clOrdId": cl, "ordId": "", "sCode": sc, "sMsg": msg}]}
        if inst not in self.ins:
            return bad("51001", "Instrument ID does not exist")
        i = self.ins[inst]
        base, quote = inst.split("-")
        if cl and cl in self.by_cl:
            return bad("51016", "Duplicated clOrdId")
        px, sz = D(p["px"]), D(p["sz"])
        if px <= 0 or not self._mult(px, i["tick"]):
            return bad("51006", "Order price is not a multiple of the tick size")
        if sz <= 0 or not self._mult(sz, i["lot"]):
            return bad("51121", "Order quantity must be a multiple of the lot size")
        if sz < i["mn"]:
            return bad("51020", "Order amount should be greater than the min available amount")
        if side == "buy" and px * sz > self.avail(quote):
            return bad("51008", "Order failed. Insufficient USDT balance in account")
        if side == "sell" and sz > self.avail(base):
            return bad("51008", "Order failed. Insufficient balance")
        self.n += 1
        oid = str(800000000 + self.n)
        o = {"ordId": oid, "cl": cl, "inst": inst, "side": side, "px": px, "sz": sz, "acc": D(0), "accv": D(0), "fee": D(0),
             "feeCcy": base if side == "buy" else quote, "state": "live", "t": self.clock.t, "type": typ}
        self.orders[oid] = o
        if cl:
            self.by_cl[cl] = oid
        if typ in ("ioc", "fok", "market"):
            at = self.ask(inst) if side == "buy" else self.bid(inst)
            hit = typ == "market" or (side == "buy" and px >= at) or (side == "sell" and px <= at)
            if hit:
                q = sz if i["depth"] is None else min(sz, (i["depth"] / i["lot"]).to_integral_value(rounding=ROUND_FLOOR) * i["lot"])
                self._fill(o, q, at)
            o["state"] = "filled" if o["acc"] >= o["sz"] else "canceled"
        else:
            raise AssertionError("the pair engine places only IOC orders (nothing rests on the exchange)")
        if self.after_place:
            self.after_place(o)
        return {"code": "0", "msg": "", "data": [{"clOrdId": cl, "ordId": oid, "sCode": "0", "sMsg": "Order placed"}]}

    def _land(self):
        due = [x for x in self.late if x[0] <= self.clock.t]
        self.late = [x for x in self.late if x[0] > self.clock.t]
        for _, kind, p in due:
            if kind == "place":
                self._place(p)

    def call(self, op, p, act):
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
            self.late.append([self.clock.t + f[1], op, dict(p)])
            raise TimeoutError(f"{op}: timed out (reaches OKX later)")
        if isinstance(f, tuple) and f[0] == "code":
            return {"code": str(f[1]), "msg": "injected", "data": [{"sCode": str(f[1]), "sMsg": "injected"}]}
        if isinstance(f, tuple) and f[0] == "ambig":
            if f[1]:
                act()
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


class _Market:
    def __init__(self, ex):
        self.ex = ex

    def get_ticker(self, instId=None, *a, **k):
        ex = self.ex

        def act():
            if instId not in ex.ins:
                return {"code": "51001", "data": []}
            return {"code": "0", "data": [{"instId": instId, "last": str(ex.ins[instId]["px"]), "bidPx": str(ex.bid(instId)),
                                           "askPx": str(ex.ask(instId))}]}
        return ex.call("ticker", {"instId": instId}, act)


def _spec_resp(ex, inst):
    i = ex.ins.get(inst)
    if not i:
        return {"code": "51001", "data": []}
    return {"code": "0", "data": [{"instId": inst, "tickSz": str(i["tick"]), "lotSz": str(i["lot"]), "minSz": str(i["mn"])}]}


class _Public:
    def __init__(self, ex):
        self.ex = ex

    def get_instruments(self, instType=None, uly="", instId="", instFamily="", **k):
        return self.ex.call("spec", {"instId": instId}, lambda: _spec_resp(self.ex, instId))


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
        assert headers is None or headers.get("OK-ACCESS-KEY") == "FAKE-KEY", "a real key reached the mock"
        if u.path.endswith("/trade/order"):
            def act():
                oid = q.get("ordId") or ex.by_cl.get(q.get("clOrdId") or "")
                o = ex.orders.get(str(oid)) if oid else None
                if o and o["inst"] != q.get("instId"):
                    o = None
                return {"code": "0", "msg": "", "data": [ex.rec(o)]} if o else {"code": "51603", "msg": "Order does not exist", "data": []}
            return _Resp(ex.call("order", q, act))
        if u.path.endswith("/public/instruments"):
            return _Resp(ex.call("spec", q, lambda: _spec_resp(ex, q.get("instId"))))
        if u.path.endswith("/account/balance"):
            def act():
                c = q.get("ccy")
                det = [{"ccy": c, "availBal": str(ex.avail(c)), "cashBal": str(ex.bal[c])}] if ex.bal[c] != 0 else []
                return {"code": "0", "msg": "", "data": [{"details": det}]}
            return _Resp(ex.call("balance", q, act))
        raise AssertionError("unknown GET " + url)

    def post(self, url, headers=None, data=None, timeout=None, **k):
        raise AssertionError("the pair engine posts nothing but orders (through the SDK): " + url)


# ─────────────────────────────── the bot + runner ───────────────────────────────
DEFAULT_CFG = {"api_key": "FAKE-KEY", "secret_key": "FAKE-SECRET", "passphrase": "FAKE-PASS", "bot_type": "grid_pair", "bridge": "USDT",
               "main_value": 20.0, "grid_percentage": 0.02, "down_levels": 5, "up_levels": 5, "profit_to": "main",
               "forced_base_ratio": 0.0, "fee_rate": 0.001, "slip_cap": 0.002, "is_demo": False}
SALE_RE = re.compile(r"الربح: ([+-])([\d.]+) (\w+)")
MARK_RE = re.compile(r"المستوى (-?\d+) · البيعة (\d+)")


class PBot:
    def __init__(self, ex, sym="SOL-XRP", cfg=None, folder=None, aside=None):
        self.ex, self.clock = ex, ex.clock
        self.sym = sym
        self.other, self.main = sym.split("-")
        self.dir = folder or tempfile.mkdtemp(prefix="pair_")
        self.cfg = dict(DEFAULT_CFG, symbol=sym, **(cfg or {}))
        self.cfg.setdefault("bot_id", "HBP" + "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9)))
        with open(os.path.join(self.dir, f"config_{sym}.json"), "w") as f:
            json.dump(self.cfg, f)
        self.bot_id = self.cfg["bot_id"]
        self.aside = Counter({c: D(x) for c, x in aside.items()}) if aside is not None else None   # wallet coins NOT the bot's · None = taken at birth
        self.m = None
        self.st = None
        self.lines = []
        self.sales = {}
        self.dup = []
        self.steps, self.si = [], 0
        self.moments, self.cut_at, self.cuts = 0, set(), 0
        self.errors = []
        self.audit_on, self.audits, self.restarts = True, 0, 0
        self.on_loop = None
        self.max_dev = D(0)

    def _load(self):
        ex, me = self.ex, self
        okx = types.ModuleType("okx")
        okx.Trade = types.ModuleType("okx.Trade")
        okx.MarketData = types.ModuleType("okx.MarketData")
        okx.PublicData = types.ModuleType("okx.PublicData")
        okx.Trade.TradeAPI = lambda *a, **k: _Trade(ex)
        okx.MarketData.MarketAPI = lambda *a, **k: _Market(ex)
        okx.PublicData.PublicAPI = lambda *a, **k: _Public(ex)
        sys.modules.update({"okx": okx, "okx.Trade": okx.Trade, "okx.MarketData": okx.MarketData, "okx.PublicData": okx.PublicData})
        name = f"pair_engine_{abs(hash(self.dir))}_{self.restarts}"
        spec = importlib.util.spec_from_file_location(name, ENGINE)
        m = importlib.util.module_from_spec(spec)
        real_socket = sys.modules["socket"]
        sys.modules["socket"] = _FakeSocketMod
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(m)
        finally:
            sys.modules["socket"] = real_socket
        m.time = _FakeTime(self.clock)
        m.datetime = _fake_dt(self.clock)
        m.requests = _Requests(ex)
        save0, log0 = m.save_json, m.log_trade_history

        def save_json(path, data):
            if path == m.STATE_FILE and isinstance(data, dict):
                me.st = data
            me._moment("save", "before")
            r = save0(path, data)
            me._moment("save", "after")
            return r

        def log_trade_history(sym, msg):
            me._moment("log", "before")
            log0(sym, msg)
            s = str(msg)
            if s.startswith(("🟢", "🔴", "🧩", "⚠️", "⏳", "💣", "🚀", "⛔")):
                me.lines.append(s)
            if s.startswith("🔴"):
                mk = MARK_RE.search(s)
                if mk:
                    k = (int(mk.group(1)), int(mk.group(2)))
                    if k in me.sales:
                        me.dup.append(s[:160])
                    me.sales[k] = s
                else:
                    me.sales[("part", len(me.sales))] = s
            me._moment("log", "after")

        m.save_json, m.log_trade_history = save_json, log_trade_history
        ex.cut = lambda op, when: me._moment(op, when)
        self.m = m
        return m

    def _moment(self, op, when):
        self.moments += 1
        if self.moments in self.cut_at:
            self.cut_at.discard(self.moments)
            self.cuts += 1
            raise Cut(f"{op} {when} #{self.moments}")

    # ---- the books (what the bot says it holds) vs the wallet
    def books(self):
        """what the bot's state says it holds of each coin — plus the swap in flight (fills the bot has not read yet included)"""
        st = self.st or {}
        if not st.get("slots"):
            return None
        ex = self.ex
        hold = Counter()
        hold[self.main] += D(str(st.get("main_book") or 0))
        for s in st["slots"].values():
            hold[self.other] += D(str(s.get("q") or 0)) + D(str(s.get("dq") or 0))
        hold[self.other] += D(str(st.get("profit_other") or 0))
        hold["USDT"] += D(str(st.get("usd_dust") or 0))
        op = st.get("op")
        if op:
            sold_c = self.main if op["kind"] == "buy" else self.other
            got_c = self.other if op["kind"] == "buy" else self.main
            hold[sold_c] -= D(str(op.get("sold") or 0))
            hold[got_c] += D(str(op.get("got") or 0))
            hold["USDT"] += D(str(op.get("usd") or 0))
            for name in ("a", "b"):                         # a leg the exchange filled and the bot has not read yet
                leg = op.get(name)
                if not leg or leg.get("st") == "done":
                    continue
                oid = leg.get("id") or ex.by_cl.get(leg.get("cl") or "")
                o = ex.orders.get(str(oid)) if oid else None
                if not o or o["acc"] <= 0:
                    continue
                base, quote = o["inst"].split("-")
                if o["side"] == "sell":
                    hold[base] -= o["acc"]
                    hold[quote] += o["accv"] - (o["fee"] if o["feeCcy"] == quote else 0)
                else:
                    hold[quote] -= o["accv"]
                    hold[base] += o["acc"] - (o["fee"] if o["feeCcy"] == base else 0)
        return hold

    def audit(self, final=False):
        hold = self.books()
        if hold is None:
            return
        self.audits += 1
        ex = self.ex
        if self.aside is None:                              # the birth: what the wallet holds beyond the bot's books stays untouched
            self.aside = Counter({c: ex.bal[c] - hold[c] for c in (self.main, self.other, "USDT")})
            self.aside0 = Counter(self.aside)
        for c in (self.main, self.other, "USDT"):
            want = hold[c] + self.aside[c]
            dev = abs(ex.bal[c] - want)
            self.max_dev = max(self.max_dev, dev)
            if dev > D("1e-8"):
                self.errors.append(f"coins {c}: wallet {ex.bal[c]} ≠ books {want} (Δ {ex.bal[c] - want}) at t={self.clock.t:.0f}")
        st = self.st
        tp = D(str(st.get("total_profit") or 0))
        sp = D(0)
        for s in self.sales.values():
            g = SALE_RE.search(s)
            if g:
                sp += D(g.group(2)) * (1 if g.group(1) == "+" else -1)
        if abs(tp - sp) > D("1e-7") and not st.get("fx_log"):
            self.errors.append(f"profit: total_profit {tp} ≠ Σ 🔴 lines {sp}")
        if self.dup:
            self.errors.append(f"a sale line written twice: {self.dup[0]}")
        ub = D(str(st.get("usd_booked") or 0))
        usd_hold = hold["USDT"]
        if final and abs(ub - usd_hold) > D("1e-8") and not st.get("op"):
            self.errors.append(f"usd_booked {ub} ≠ the bot's dollar {usd_hold}")

    def _hook(self, dt, caller):
        if caller != "start_bot":
            return
        self.ex._land()
        if self.audit_on:
            self.audit()
        if self.on_loop:
            self.on_loop(self)
        while self.si < len(self.steps) and self.steps[self.si][0] <= self.clock.t:
            _, fn = self.steps[self.si]
            self.si += 1
            fn(self)
        if self.si >= len(self.steps) and self.clock.t >= self.end:
            raise Stop()

    def run(self, steps, end=None, cut_at=None, max_restarts=10000):
        """steps: [(t, fn(bot))] — t relative to the start · a power cut ⇒ a fresh engine on the same folder"""
        t0 = self.clock.t
        self.steps = sorted([(t0 + t, fn) for t, fn in steps], key=lambda x: x[0])
        self.si = 0
        self.end = t0 + (end if end is not None else (max((t for t, _ in steps), default=0) + 30))
        self.cut_at = set(cut_at or ())
        self.clock.hook = self._hook
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            while True:
                try:
                    m = self._load()
                    with contextlib.redirect_stdout(io.StringIO()):
                        m.start_bot()
                    break
                except Cut:
                    self.restarts += 1
                    if self.restarts > max_restarts:
                        raise
                    _FakeSocketMod.bound.clear()
                    continue
                except Stop:
                    break
                except SystemExit:
                    break
        finally:
            os.chdir(cwd)
            _FakeSocketMod.bound.clear()
            self.clock.hook = None
        self.audit(final=True)
        return self

    def state(self):
        p = os.path.join(self.dir, f"grid_state_{self.sym}.json")
        try:
            return json.load(open(p))
        except Exception:
            return {}

    def log(self):
        p = os.path.join(self.dir, f"trade_history_{self.other}.json")
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return []

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def market(clock=None, xrp="2.0", sol="150", bal_xrp="200", bal_sol="2", usdt="0", **kw):
    """a standard test market: XRP-USDT and SOL-USDT (OKX's real steps) · 1 SOL = 75 XRP"""
    clock = clock or Clock()
    ex = PEx(clock, insts={"XRP-USDT": dict(px=xrp, tick="0.0001", lot="0.000001", mn="1"),
                           "SOL-USDT": dict(px=sol, tick="0.01", lot="0.000001", mn="0.01")},
             bal={"XRP": bal_xrp, "SOL": bal_sol, "USDT": usdt}, **kw)
    return ex


def ratio_path(ex, r_of_t, other="SOL-USDT", main="XRP-USDT", main_px_of_t=None):
    """steps that move the market so that 1 OTHER = r(t) MAIN (the main coin's dollar price can move too)"""
    def mk(t):
        def f(bot):
            mp = D(main_px_of_t(t)) if main_px_of_t else ex.ins[main]["px"]
            ex.set(main, mp)
            ex.set(other, (D(r_of_t(t)) * mp).quantize(D("0.0001")))
        return f
    return mk
