# 🪜♾️ the pair test the owner asked for (7-11): a graded grid and an infinite grid with the SAME settings, both REAL engines taken from
#   the dashboard, on the same mock OKX and the same price path — the price climbs the same levels and comes back (and dips and comes back):
#     ① no cut: what each bot ends with (coins · dollars · booked profit) — each bot's books = its wallet · both back to their coins
#     ② with power cuts (the process dies at chosen moments and starts again from its files) and the internet down (every call fails
#        for minutes) — compared with the same bot on the same path with no cut: the same coins and dollars left (nothing lost)
#   The same settings: 25$ per order · 0.6% between buys · sells 0.6% above their buy (🪜 one part = the grid's own rule) · floor 0.9
#   · 4 sells from the wallet above the start · 4 orders per side on OKX (the grid's 4/4 · 🪜 step_window 4).
#   python3 devtests/step/t_pair.py [Holy_Dashboard.pyw] [-q]
import ast, base64, contextlib, importlib.util, io, json, os, queue, random, sys, tempfile, types, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okxsim
from okxsim import Clock, Ex, Bot, walk, D, Cut, Stop, _Trade, _Market, _Requests, _FakeTime, _FakeSocketMod, _fake_dt

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def extract(var):
    src = open(DASH, encoding="utf-8").read()
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == var for t in n.targets):
            return zlib.decompress(base64.b64decode(ast.literal_eval(n.value))).decode("utf-8")
    raise SystemExit(f"{var} not in the dashboard")


TMP = tempfile.mkdtemp(prefix="t_pair_")
GRID_ENG, STEP_ENG = os.path.join(TMP, "main_grid.py"), os.path.join(TMP, "main_step.py")
open(GRID_ENG, "w", encoding="utf-8").write(extract("_ENGINE_B64"))
open(STEP_ENG, "w", encoding="utf-8").write(extract("_GRIDS_B64"))
okxsim.ENGINE = STEP_ENG                                   # 🪜 from the dashboard itself


class _Q:
    """the grid's websocket queue: nothing arrives (no websocket in the test) · waiting `timeout` = the fake clock moves (a loop)"""

    def __init__(self, clock):
        self.c = clock

    def get(self, timeout=None, block=True):
        self.c.sleep(float(timeout or 1.0), "start_bot")
        raise queue.Empty

    def put(self, *a, **k):
        pass


class _Fut:
    def __init__(self, fn, a, k):
        self.fn, self.a, self.k = fn, a, k

    def result(self, timeout=None):
        return self.fn(*self.a, **self.k)


class _Pool:                                               # the grid's order checks one after another (a power cut is a real stop)
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def submit(self, fn, *a, **k):
        return _Fut(fn, a, k)


class _GReq(_Requests):
    """OKX's REST as the grid reads it: + the open orders list (`/trade/orders-pending` — the grid asks it before selling wallet coins)"""

    def get(self, url, headers=None, timeout=None, **k):
        import urllib.parse
        if urllib.parse.urlparse(url).path.endswith("/trade/orders-pending"):
            ex = self.ex
            return okxsim._Resp(ex.call("list", {}, lambda: {"code": "0", "msg": "", "data": [ex.rec(o) for o in ex.pending()]}))
        return super().get(url, headers=headers, timeout=timeout, **k)


class GBot(Bot):
    """the infinite grid (main.py from the dashboard) on the same runner: the same clock, mock OKX, power cuts and internet faults"""

    def _load(self):
        ex, me = self.ex, self
        okx = types.ModuleType("okx")
        okx.Trade = types.ModuleType("okx.Trade")
        okx.MarketData = types.ModuleType("okx.MarketData")
        okx.Trade.TradeAPI = lambda *a, **k: _Trade(ex)

        class M(_Market):
            def get_instruments(self, instType=None, instId="", **k):
                return ex.call("spec", {}, lambda: okxsim._spec_resp(ex))
        okx.MarketData.MarketAPI = lambda *a, **k: M(ex)
        ws = types.ModuleType("websocket")
        ws.enableTrace = lambda *a, **k: None
        sys.modules.update({"okx": okx, "okx.Trade": okx.Trade, "okx.MarketData": okx.MarketData, "websocket": ws})
        name = f"grid_engine_{abs(hash(self.dir))}_{self.restarts}"
        spec = importlib.util.spec_from_file_location(name, GRID_ENG)
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
        m.requests = _GReq(ex)
        m.event_queue = _Q(self.clock)
        m.ws_thread_target = lambda: None
        cf = types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=_Pool, as_completed=lambda fs: list(fs)))
        m.concurrent = cf
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
            if str(msg).startswith(("🟢", "🔴", "💠")):
                me.fill_lines.append(msg)
            me._moment("log", "after")
        m.save_json, m.log_trade_history = save_json, log_trade_history
        ex.cut = lambda op, when: me._moment(op, when)
        self.m = m
        return m


P0, G, QV, FLOOR = 1.0, 0.006, 25.0, 0.9
GRID = {"bot_type": "grid", "grid_percentage": G, "usd_value": QV, "min_price": FLOOR, "forced_base_price": P0, "knife_guard": False,
        "fee_rate": 0.0008}                                   # (the dashboard writes the real maker fee into every bot's settings)
NF = (G - 2 * 0.0008 - G * 0.0008) / (G * 0.999)            # the dashboard's net_factor: the grid books its profit before the fees
STEP = {"bot_type": "grid_step", "grid_percentage": G, "usd_value": QV, "min_price": FLOOR, "forced_base_price": P0, "step_parts": 1,
        "step_first": G, "step_sell": G, "up_groups": 4, "step_window": 4, "fee_rate": 0.0008, "taker_rate": 0.001}
COINS, USD = 150.0, 1000.0
HOLD = 600


def path():
    """up 4 levels and back · down 4 levels and back — every level held 10 minutes (each order fills; the bot answers)"""
    up = [round(P0 * (1 + G) ** k * 1.0012, 4) for k in range(1, 5)]
    dn = [round(P0 / (1 + G) ** k * 0.9988, 4) for k in range(1, 5)]
    seq = [P0, P0] + up + up[::-1][1:] + [P0] + dn + dn[::-1][1:] + [P0, P0]
    return walk(seq, HOLD)


def run(kind, cuts=(), down=()):
    c = Clock()
    ex = Ex(c, sym="XRP-USDT", price=P0, base=COINS, quote=USD)
    ex.latency = 0.002                                       # every call takes 2 ms (the grid's order ids are its clock in ms — a
    b = (GBot if kind == "grid" else Bot)(ex, dict(GRID if kind == "grid" else STEP))
    b.audit_on = kind == "step"                             # 🪜's own audit (books = wallet) every loop
    steps = path()
    for at in sorted(down, reverse=True):                    # 🌐 the internet down 3 minutes after step `at`
        steps[at + 1:at + 1] = [("do", lambda bb: setattr(bb.ex, "down", True)), ("wait", 180), ("do", lambda bb: setattr(bb.ex, "down", False))]
    b.run(steps, cuts=cuts, off=90.0)
    st = b.disk()
    rungs = sorted((d[-5:], round(float(v.get("target_price") or 0), 4), round(float(v.get("locked_qty") or 0), 6))
                   for d in ("limit_buys", "virtual_buys", "accum_buys", "limit_sells", "virtual_sells", "accum_sells") for v in (st.get(d) or {}).values()
                   if isinstance(v, dict))
    rungs = sorted((("buys" if "buy" in d else "sells"), px, q) for d, px, q in rungs)
    return {"bot": b, "coins": ex.bal["XRP"], "usd": ex.bal["USDT"], "tp": D(str(st.get("total_profit") or 0)), "fills": len(ex.fills), "rungs": rungs,
            "open": sorted((o["side"], str(o["px"]), str(o["sz"])) for o in b.mine_open()), "moments": b.moments, "cuts": b.cuts,
            "errors": list(b.errors)}


def fmt(r):
    return (f"coins {float(r['coins']):.6f} ({float(r['coins'] - D(COINS)):+.6f}) · dollars {float(r['usd']):.6f} ({float(r['usd'] - D(USD)):+.6f}) · "
            f"booked profit {float(r['tp']):.6f}$ · {r['fills']} fills")


# ── ① no cut: the round trip
A = {k: run(k) for k in ("grid", "step")}
for k, nm in (("grid", "♾️ grid"), ("step", "🪜 graded (1 part)")):
    r = A[k]
    print(f"   {nm}: {fmt(r)}")
for k, nm in (("grid", "♾️"), ("step", "🪜")):
    r = A[k]
    gain = (r["usd"] - D(USD)) + (r["coins"] - D(COINS)) * D(P0)          # what the wallet gained, valued at the start price
    net = r["tp"] * D(str(NF if k == "grid" else 1.0))                     # the profit the dashboard books (the grid's after its fee factor)
    back = abs(r["coins"] - D(COINS)) < (D("0.1") if k == "grid" else D("0.00001"))
    ok(f"① {nm} no cut — the price climbed 4 levels and came back, dipped 4 and came back ({r['fills']} fills): the wallet gained "
       f"{float(gain):.6f}$ = the profit the dashboard books {float(net):.6f}$ (Δ {float(gain - net):+.6f}) · its coins back "
       f"(Δ {float(r['coins'] - D(COINS)):+.6f}{' — the grid pays its buy fee in coins and rounds to 2 decimals' if k == 'grid' else ''})"
       + (" · books = wallet every loop" if k == "step" else ""),
       back and r["tp"] > 0 and abs(gain - net) < D("0.005") and not r["errors"] and r["fills"] == 16, (fmt(r), float(gain), float(net), r["errors"][:2]))
g, s = A["grid"], A["step"]
gv = (g["usd"] - D(USD)) + (g["coins"] - D(COINS)) * D(P0)
sv = (s["usd"] - D(USD)) + (s["coins"] - D(COINS)) * D(P0)
gp = sorted(float(f[3]) for f in g["bot"].ex.fills)
sp_ = sorted(float(f[3]) for f in s["bot"].ex.fills)
tick = max(abs(x - y) for x, y in zip(gp, sp_)) if len(gp) == len(sp_) else 1.0
ok(f"① side by side: the same 16 fills at the same levels (within one price tick: {tick:.4f}) · the wallets gained ♾️ {float(gv):.4f}$ · 🪜 "
   f"{float(sv):.4f}$ (Δ {float(gv - sv):+.4f}$ — the grid builds each level from the previous ROUNDED one and rounds quantities to 2 decimals "
   "with its buy fee paid in coins; 🪜 prices every level from the exact formula, rounds its sells UP and sells exactly the coins its buy received)",
   g["fills"] == s["fills"] == 16 and tick <= 0.00011 and abs(gv - sv) < D("0.03"), (fmt(g), fmt(s), gp, sp_))

# ── ② power cuts and the internet down vs the same bot with no cut
for k, nm in (("grid", "♾️"), ("step", "🪜")):
    ref = A[k]
    n = ref["moments"]
    rng = random.Random(7 if k == "grid" else 11)
    cuts = sorted(rng.sample(range(60, max(61, n - 300)), 10))
    r = run(k, cuts=cuts, down=(3, 9, 14))
    same = r["coins"] == ref["coins"] and r["usd"] == ref["usd"] and r["tp"] == ref["tp"] and r["rungs"] == ref["rungs"]
    live = r["open"] == ref["open"]
    ok(f"② {nm} with {r['cuts']} power cuts (off 90 s each) and the internet down 3 times × 3 min — exactly the same coins, dollars, booked "
       f"profit and ladder (every level, live or in memory) as the same bot with no cut — nothing lost · nothing doubled: {fmt(r)}"
       + ("" if live else " · ℹ️ live/memory split differs (one level swapped — see REVIEW)"),
       same and r["cuts"] >= 8 and not r["errors"] and (live or k == "grid"),
       (fmt(r), fmt(ref), sorted(set(r["rungs"]) ^ set(ref["rungs"]))[:4], r["errors"][:2]))

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_pair: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
