# 🪜🪟🛡️🪙 v3.36.19 — the owner's 7-11 live findings, and only these:
#   ① the window is strict like ♾️ (enforce_max_four): never more than step_window orders per side on OKX — checked at EVERY order
#      placed (live · partly filled · in flight) · a sale that opens a buy ⇒ the farthest buy goes to memory in the same cycle
#      (the owner: «باع وفتح شراء ما مسح الي تحت وصار ٩ منشورات») · a partly filled order outside the window stays and counts ·
#      no live order outside the window but a partly filled one
#   ② the dashboard's REAL guard (gather · apply · trade scan · qty audit — every 10 minutes like the server) on the 🪜 engine and the
#      mock OKX: the owner's settings (25$ · 0.6% · floor 0.9 · 3 parts) 6 hours, plain timing · the bot's file read one cycle before
#      OKX · reinvest 60% ⇒ no alert at all · «💵 free USDT under one buy» measured by the 🪜's own order (25$ ÷ 3 parts) ·
#      «☠️ the price moved … no fill» not when the price only ran above the 🪜's top sell · still raised for a hung 🪜
#   ③ the accumulator: a 🪜 coin handoff (➖ coin profit · 🔓 release) received by the dashboard (accum_coin_handoff) at its real
#      cost · exactly once · the guard's coin book = the wallet before, in transit and after · a 50% accumulator ⇒ the rest is the
#      wallet's (counted by the guard)
#   python3 devtests/step/t_win.py [Holy_Dashboard.pyw] [-q] [--only=window,owner,partial,guard,quote,stall,acc]
#   (STEP_ENGINE=… runs another engine copy · tests never touch the network: fake keys, the mock answers everything)
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time as _rt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D, _fake_dt

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


# ─────────────── the owner's settings ───────────────
P0, G, QV, FLOOR = 1.1698, 0.006, 25.0, 0.9
OWNER = {"usd_value": QV, "step_parts": 3, "step_first": 0.0045, "step_sell": 0.0015, "grid_percentage": G, "min_price": FLOOR,
         "up_groups": 0, "forced_base_price": P0, "step_window": 8, "fee_rate": 0.0008, "taker_rate": 0.001}


def strict(b, W, bad):
    """every order the bot places: its side on OKX stays ≤ W right after (an order that crosses fills at once — not counted)"""
    ex = b.ex
    p0 = ex._place

    def place(p):
        r = p0(p)
        if str(p.get("clOrdId") or "").startswith(b.bot_id):
            n = sum(1 for o in ex.pending() if o["cl"].startswith(b.bot_id) and o["side"] == p["side"])
            if n > W:
                bad.append(("okx", p["side"], n, round(b.clock.t)))
        return r
    ex._place = place


def in_window(b, W, bad):
    """at every loop: per side ≤ W orders in the book (live · partly filled · in flight) · no live order outside the nearest W
    eligible slots unless it is partly filled"""
    st = b.st or {}
    S = st.get("slots") or {}
    for side in ("buy", "sell"):
        rows = [(k, s) for k, s in S.items() if s.get("side") == side]
        rows.sort(key=(lambda t: (-t[1]["bp"], -t[1]["j"], t[1]["k"])) if side == "buy" else (lambda t: (t[1]["sp"], t[1]["j"], t[1]["k"])))
        near = {k for k, _ in rows[:W]}
        on = [k for k, s in rows if s.get("o")]
        if len(on) > W:
            bad.append(("book", side, len(on), round(b.clock.t)))
        for k, s in rows:
            o = s.get("o") or {}
            if o.get("st") == "live" and k not in near:
                eo = b.ex.orders.get(str(o.get("id")))
                if not (eo and eo["acc"] > 0):
                    bad.append(("outside", side, k, round(b.clock.t)))


def chop(seed, hours, p0=P0, wave=0.03, amp=0.004, noise=0.0008):
    rng = random.Random(seed)
    out = []
    for i in range(int(hours * 3600 / 10)):
        t = i * 10
        slow = p0 * (1 - wave * 0.66 + wave * math.sin(2 * math.pi * t / 21600.0))
        out.append(round(max(FLOOR * 1.01, slow * (1 + amp * math.sin(2 * math.pi * t / 1800.0)) * math.exp(rng.gauss(0, noise))), 4))
    return out


# ─────────────── ① the window ───────────────
if want("owner"):
    c = Clock()
    ex = Ex(c, sym="XRP-USDT", price=P0, base=0, quote=2000)
    b = Bot(ex, OWNER)
    bad = []
    strict(b, 8, bad)
    M = {}

    def keep(name):
        def f(bb):
            st = bb.st
            M[name] = {"slots": json.loads(json.dumps(st["slots"])), "buys": sorted((o["px"], o["ordId"]) for o in bb.mine_open() if o["side"] == "buy"),
                       "lb": dict(st.get("limit_buys") or {}), "vb": dict(st.get("virtual_buys") or {})}
        return ("do", f)
    bp1 = float(D(P0) / D(1.006))
    b.run(walk([P0, P0], 20) + [keep("a")] + walk([round(bp1 * 0.9995, 4), round(bp1 * 0.9995, 4)], 20) + [keep("b")]
          + walk([round(bp1 * 1.0047, 4), round(bp1 * 1.0047, 4)], 20) + [keep("c")] + walk([round(bp1 * 1.0047, 4)] * 4, 20) + [keep("d")])
    a, bb, cc, dd = M["a"], M["b"], M["c"], M["d"]
    far_b = sorted(bb["slots"].items(), key=lambda t: (-t[1]["bp"], -t[1]["j"], t[1]["k"]))
    buys_b = [k for k, s in far_b if s["side"] == "buy" and (s.get("o") or {}).get("st") == "live"]
    last = buys_b[-1] if buys_b else None
    ok("the owner's case: 8 buys on OKX · level −1 buys (3 parts) ⇒ its 3 sells · the window takes the next 8 buys",
       len(a["buys"]) == 8 and len(bb["buys"]) == 8 and all(bb["slots"][f"-1:{k}"]["side"] == "sell" for k in (1, 2, 3)),
       (len(a["buys"]), len(bb["buys"]), {k: bb["slots"][k]["side"] for k in ("-1:1", "-1:2", "-1:3")}))
    sold = cc["slots"]["-1:1"]
    eo = ex.orders.get(str(((bb["slots"].get(last) or {}).get("o") or {}).get("id")))
    ok("«باع وفتح شراء»: part −1:1 sold ⇒ its buy at the top · STILL 8 buys on OKX (was 9) · the farthest buy "
       f"({last}) went to memory in the same cycle (its order canceled at OKX · the card's memory list has it)",
       sold["side"] == "buy" and len(cc["buys"]) == 8 and cc["slots"][last].get("o") is None and eo and eo["state"] == "canceled"
       and last in cc["vb"] and not bad,
       (sold["side"], len(cc["buys"]), last, cc["slots"].get(last, {}).get("o"), eo and eo["state"], bad[:3]))
    ok("… and it stays 8 (the next cycles neither re-send it nor add a 9th) · books = wallet every loop", len(dd["buys"]) == 8
       and dd["slots"][last].get("o") is None and not b.errors and not bad, (len(dd["buys"]), b.errors[:3], bad[:3]))

if want("window"):
    worst, n_pull = [], 0
    for seed in range(1, 13):
        rng = random.Random(seed)
        W = rng.choice([2, 4, 8])
        N = rng.choice([1, 2, 3, 4])
        cfg = dict(OWNER, step_parts=N, step_window=W, step_first=rng.choice([0.003, 0.0045, 0.006]),
                   step_sell=rng.choice([0.0015, 0.002, 0.004]), up_groups=rng.choice([0, 1, 2]))
        if rng.random() < 0.35:
            cfg.update(reinvest=True, reinvest_pct=rng.choice([60, 100]))
        c = Clock()
        ex = Ex(c, sym="XRP-USDT", price=P0, base=400, quote=3000, partial=rng.choice([0, 0, 0.4]), seed=seed)
        b = Bot(ex, cfg)
        bad = []
        strict(b, W, bad)
        b.on_loop = lambda bb, W=W, bad=bad: in_window(bb, W, bad)
        b.run(walk(chop(seed, 3, wave=rng.choice([0.01, 0.03]), amp=rng.choice([0.002, 0.006])), 10))
        n_pull += ex.calls["cancel"]
        if bad or b.errors:
            worst.append((seed, {k: cfg[k] for k in ("step_parts", "step_window", "up_groups")}, cfg.get("reinvest_pct"), bad[:3], b.errors[:2]))
    ok(f"random: 12 markets × window 2/4/8 × 1–4 parts × wallet sells 0–2 × partial fills × reinvest — never W+1 orders on a side "
       f"at OKX (checked at every order placed) · the book never W+1 · no live order outside the nearest W but a partly filled one · "
       f"books = wallet every loop ({n_pull} orders moved to memory)", not worst, worst[:2])

if want("partial"):
    c = Clock()
    ex = Ex(c, sym="XRP-USDT", price=1.0, base=0, quote=2000, partial=0.4)
    b = Bot(ex, {"usd_value": 30.0, "step_parts": 1, "step_sell": 0.03, "grid_percentage": 0.01, "min_price": 0.8, "up_groups": 0,
                 "forced_base_price": 1.0, "step_window": 3})
    bad = []
    strict(b, 3, bad)
    M = {}

    def keep2(name):
        def f(bb):
            M[name] = {"slots": json.loads(json.dumps(bb.st["slots"])),
                       "live": sorted((float(o["px"]), float(o["acc"]) > 0) for o in bb.mine_open() if o["side"] == "buy")}
        return ("do", f)
    # three buys at −1 −2 −3 · the price touches −3 (40% of it fills) and comes back up · −1 fills and sells ⇒ its buy comes back:
    # the window wants −1 −2 −3 … −3 is partly filled (stays, counts) ⇒ still 3 at OKX
    p = [1.0, 0.98, 0.9705, 0.98, 0.99, 0.99, 0.9895, 0.995, 1.0, 1.0193, 1.022, 1.022]
    b.run(walk(p, 20) + [keep2("x")] + walk([1.022] * 3, 20) + [keep2("y")])
    x = M["x"]
    part = [k for k, s in x["slots"].items() if s["side"] == "buy" and (s.get("o") or {}).get("id")
            and (ex.orders.get(str(s["o"]["id"])) or {}).get("acc", 0) > 0]
    ok("a partly filled buy far from the price stays on OKX and counts: the side is still ≤ 3 orders at OKX at every placement · "
       "the nearest buys are the others", not bad and len(x["live"]) <= 3 and len(M["y"]["live"]) <= 3 and not b.errors,
       (bad[:3], x["live"], M["y"]["live"], part, b.errors[:2]))


# ─────────────── the dashboard (its real guard) on the mock OKX ───────────────
R = tempfile.mkdtemp(prefix="t_win_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
_cwd = os.getcwd(); os.chdir(R)
_ld = importlib.machinery.SourceFileLoader("hd_twin", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_twin", _ld)); _a0 = sys.argv; sys.argv = ["x"]; _ld.exec_module(m); sys.argv = _a0
os.chdir(_cwd)
m.ROOT = R
m._okx_pub = lambda p: {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the guard placed/canceled an order"))
TG = []
m.tg_send = lambda t, *a, **k: TG.append(str(t)) or True


class DT:
    def __init__(self, c):
        self.c = c

    def time(self):
        return self.c.t

    def sleep(self, s):
        pass

    def __getattr__(self, n):
        return getattr(_rt, n)


class Guard:
    """the dashboard's guard round on one 🪜 bot folder and one mock OKX (the fills · balance · open orders · order details)"""

    def __init__(self, b, acc=None):
        self.b, self.ex, self.c = b, b.ex, b.clock
        m.time, m.datetime = DT(self.c), _fake_dt(self.c)
        self.B = {"dir": b.dir, "symbol": b.ex.sym, "cfg": dict(b.cfg)}
        m.bot_dirs = lambda: {os.path.basename(b.dir): self.B}
        self.keys = (b.cfg["api_key"], b.cfg["secret_key"], b.cfg["passphrase"])
        self.wid = m._gd_wid(self.keys[0])
        cfgs = {"wallets": [{"name": "main", "api": self.keys[0], "sec": self.keys[1], "pass": self.keys[2]}]}
        if acc:
            cfgs["accumulators"] = [dict({"id": "acc1", "name": "XRP acc", "symbol": b.ex.sym, "enabled": True, "coin_pct": 100,
                                          "wid": self.wid}, **acc)]
        json.dump(cfgs, open(m.APP_CFG, "w"))
        for f in (m.ACCUM_FILE, m.GUARD_FILE if hasattr(m, "GUARD_FILE") else None):
            if f and os.path.exists(f):
                os.remove(f)
        self.acc = bool(acc)
        self.g = m._gd_empty()
        self.fl = []
        self.ev, self.coin_al, self.diffs, self.why = [], [], [], []
        f0 = self.ex._fill

        def fill(o, sz, px, maker):
            fee0 = o["fee"]
            f0(o, sz, px, maker)
            if sz > 0:
                self.fl.append((int(self.c.t * 1000), o["ordId"], o["cl"], o["side"], px, sz, o["fee"] - fee0, o["feeCcy"], len(self.fl) + 1))
        self.ex._fill = fill
        self.next = self.c.t
        self.race, self.copy = False, None
        m._okx_get = self.get

    def get(self, path, *k):
        import urllib.parse as up
        ex = self.ex
        u = up.urlparse(path)
        q = dict(up.parse_qsl(u.query))
        if u.path.endswith("/trade/fills"):
            beg = int(q.get("begin") or 0)
            rows = sorted((f for f in self.fl if f[0] > beg), key=lambda f: -f[0])
            if q.get("after"):
                rows = [f for f in rows if f[8] < int(q["after"])]
            return {"code": "0", "data": [{"ordId": f[1], "clOrdId": f[2], "instId": ex.sym, "side": f[3], "fillSz": str(f[5]),
                                           "fillPx": str(f[4]), "fee": str(-f[6]), "feeCcy": f[7], "tradeId": str(f[8]),
                                           "billId": str(f[8]), "ts": str(f[0])} for f in rows[:100]]}
        if u.path.endswith("/account/bills"):
            return {"code": "0", "data": []}
        if u.path.endswith("/account/balance"):
            det = [{"ccy": cc, "cashBal": str(ex.bal[cc]), "availBal": str(ex.avail(cc)), "frozenBal": str(ex.locked(cc))}
                   for cc in q.get("ccy", "").split(",") if ex.bal[cc] != 0]
            return {"code": "0", "data": [{"details": det}]}
        if u.path.endswith("/trade/orders-pending"):
            return {"code": "0", "data": [ex.rec(o) for o in ex.pending()][:100]}
        if u.path.endswith("/trade/order"):
            o = ex.orders.get(q.get("ordId"))
            if not o:
                return {"code": "51603", "data": []}
            r = ex.rec(o)
            if o["state"] == "canceled":
                r["cancelSource"] = "32" if o.get("stp") else "1"
            return {"code": "0", "data": [r]}
        raise AssertionError("the guard asked OKX for " + path)

    def scan(self):
        now = self.c.t
        m.PX[self.ex.sym] = float(self.ex.price)
        W = {"wid": self.wid, "keys": self.keys, "bots": [self.B], "acc": self.acc, "label": "main"}
        po = m.paths_of
        if self.race and self.copy:
            m.paths_of = lambda bb: (self.copy,) + tuple(po(bb)[1:])
        try:
            snap = m._gd_gather(W, self.g, now)
        finally:
            m.paths_of = po
        m._gd_apply(self.g, snap, now)
        m._safe(m._gd_acc_scan, self.g, now, default=None)
        m._safe(m._gd_ri_scan, self.g, now, default=None)
        m._safe(m._gd_trade_scan, self.g, now, [snap], default=None)
        m._gd_qty_audit(self.g, now, [snap])
        seen = {e[0] for e in self.ev}
        for e in self.g.get("events") or []:
            if e.get("status") == "open" and e.get("id") not in seen:
                self.ev.append((e.get("id"), e.get("kind"), e.get("title"), str(e.get("detail"))[:300], round((now - 1_760_000_000) / 3600, 2)))
        for B in (self.g.get("bots") or {}).values():          # ☠️ the bot's reasons this round (one event per bot — its text grows)
            self.why += [r for r in (B.get("reasons") or []) if r not in self.why]
        C = (((self.g.get("wallets") or {}).get(self.wid) or {}).get("coins") or {}).get(self.ex.base) or {}
        if C.get("diff") is not None:
            self.diffs.append((round(now), float(C["diff"]), float(C.get("tol") or 0)))
        if (C.get("alert") or {}).get("confirmed"):
            self.coin_al.append((round(now), C["alert"]["diff"]))
        return snap

    def every(self, sec=600):
        def loop(bb):
            if self.c.t >= self.next:
                self.next = self.c.t + sec
                self.scan()
            if self.race:                          # the guard reads the bot's file one cycle before OKX (the bot ran in between)
                sp = os.path.join(bb.dir, f"grid_state_{bb.ex.sym}.json")
                cp = os.path.join(R, "race_copy.json")
                try:
                    shutil.copy(sp, cp)
                    self.copy = cp
                except Exception:
                    pass
        self.b.on_loop = loop
        return self


# ─────────────── ② the guard ───────────────
if want("guard"):
    for name, extra, race in (("plain", {}, False), ("race", {}, True), ("reinvest 60%", {"reinvest": True, "reinvest_pct": 60}, True),
                              ("20 parts · 0.3% then 1% · 💠100%", {"usd_value": 100.0, "step_parts": 20, "step_first": 0.003, "step_sell": 0.01,
                                                                   "reinvest": True, "reinvest_pct": 100}, True)):
        c = Clock()
        ex = Ex(c, sym="XRP-USDT", price=P0, base=0, quote=2000)
        b = Bot(ex, dict(OWNER, **extra))
        b.audit_on = False
        bad = []
        strict(b, 8, bad)
        gd = Guard(b).every()
        gd.race = race
        b.run(walk(chop(5, 6), 10))
        sales = sum(int(s.get("n") or 0) for s in (b.disk().get("slots") or {}).values())
        qa = ((gd.g.get("qa") or {}).get("view") or {}).get("coins") or []
        ok(f"the guard on the owner's 🪜 6 h ({name}): {sales} sales · {len(gd.diffs)} guard rounds — NO alert at all (✂️ 👻 📏 ☠️ 💵 🧮 🪙) · "
           "the coin book = the wallet every round · never 9 orders on a side",
           sales > 20 and not gd.ev and not gd.coin_al and len(gd.diffs) >= 30 and all(abs(d) <= t for _t, d, t in gd.diffs)
           and not any(r.get("st") == "alert" or r.get("q2") == "alert" for r in qa) and not bad,
           (sales, gd.ev[:3], gd.coin_al[:2], [x for x in gd.diffs if abs(x[1]) > x[2]][:2], bad[:2]))

if want("quote"):
    out = {}
    for free in (15.0, 5.0):
        c = Clock()
        ex = Ex(c, sym="XRP-USDT", price=P0, base=0, quote=round(8 * QV / 3 + free, 2))
        b = Bot(ex, OWNER)
        b.audit_on = False
        gd = Guard(b).every()
        b.run(walk([P0] * 400, 10))
        out[free] = [e for e in gd.ev if e[1] == "low_quote"]
    ok("«💵 free USDT under one buy»: 8 buys of 25$÷3 = 8.33$ locked · 15$ free ⇒ no alert (the next 🪜 buy is 8.33$, it fits — was "
       "«under 25$» before) · 5$ free ⇒ the alert, naming the 🪜's real order «8.33»",
       not out[15.0] and len(out[5.0]) == 1 and "8.33" in out[5.0][0][3], out)

if want("stall"):
    c = Clock()
    ex = Ex(c, sym="XRP-USDT", price=P0, base=0, quote=2000)
    b = Bot(ex, OWNER)
    b.audit_on = False
    gd = Guard(b).every()
    bp1 = P0 / 1.006
    b.run(walk([P0, round(bp1 * 0.999, 4), round(bp1 * 0.999, 4)], 30) + walk([round(bp1 * 1.0080, 4)] * 3, 30)
          + walk([round(P0 * 1.02, 4)] * 400, 10))
    st = b.disk()
    allbuy = all(s["side"] == "buy" for s in st["slots"].values())
    ok("«☠️ … السعر تحرك X درجة … وما صار ولا تنفيذ» — the 🪜 sold all it had and opened its buys, the price ran 2% above its start "
       "for an hour: nothing above it to fill ⇒ NO alert (it waits — it is not dead)",
       allbuy and not [e for e in gd.ev if e[1] == "bot"] and not gd.why and len(gd.diffs) >= 6, (allbuy, gd.ev[:3], gd.why, len(gd.diffs)))
    c = Clock()
    ex = Ex(c, sym="XRP-USDT", price=P0, base=0, quote=2000)
    b = Bot(ex, OWNER)
    b.audit_on = False
    gd = Guard(b).every()

    def hang(bb):
        bb.m.monitor_and_recover = lambda *a, **k: None       # the process alive, its loop doing nothing
    b.run(walk([P0, round(bp1 * 0.999, 4), round(bp1 * 0.999, 4)], 30) + [("do", hang)]
          + walk([round(bp1 * 1.0080, 4)] * 3, 30) + walk([round(P0 * 1.02, 4)] * 400, 10))
    stall = [r for r in gd.why if "تحرك" in r]
    ok("… a hung 🪜 (alive, its loop doing nothing) while the price crossed its 3 sells: still caught ⇒ «☠️ … ما يشتغل صح» "
       "(its orders filled at OKX and not handled · the price moved past its sells and nothing filled)",
       len([e for e in gd.ev if e[1] == "bot"]) == 1 and stall and any("ما عالجها" in r for r in gd.why), (gd.ev[:3], gd.why))


# ─────────────── ③ the accumulator ───────────────
def stp(fname, items, rid):
    def f(b):
        with open(os.path.join(b.dir, fname), "w", encoding="utf-8") as fh:
            json.dump({"id": rid, "ts": b.clock.t, "items": items}, fh)
    return ("do", f)


def off_flag(b):
    p = os.path.join(b.dir, f"config_{b.ex.sym}.json")
    cf = json.load(open(p)); cf["reinvest"] = False; json.dump(cf, open(p, "w"))
    open(os.path.join(b.dir, "reinvest_release.flag"), "w").close()


DN = [1.0, 0.99, 0.98, 0.9709, 0.97, 0.9806, 0.9903, 1.0, 1.0]
GROWN = walk(DN * 2 + [1.0, 0.99, 0.98, 0.9709, 0.97, 0.97], 20)      # level −1's grown buys fill ⇒ its parts are grown sells
RCFG = {"step_window": 8, "step_first": 0.01, "step_sell": 0.01, "grid_percentage": 0.03, "min_price": 0.7, "up_groups": 0,
        "forced_base_price": 1.0, "usd_value": 15.0, "step_parts": 3, "reinvest": True, "reinvest_pct": 100}

if want("acc"):
    for how, pct in (("➖ coin profit", 100), ("🔓 release", 100), ("➖ coin profit", 50)):
        c = Clock()
        ex = Ex(c, sym="XRP-USDT", price=1.0, base=0, quote=1000)
        b = Bot(ex, RCFG)
        gd = Guard(b, acc={"coin_pct": pct}).every()     # the guard's rounds from the start (as on the server) + the looks below
        M = {}

        def look(name):
            def f(bb):
                gd.scan()
                M[name] = {"ho": [dict(h) for h in m._ri_handoffs_of(bb.disk())], "acc": json.loads(json.dumps(m.acc_state())),
                           "d": gd.diffs[-1] if gd.diffs else None}
            return ("do", f)

        def receive(name):
            def f(bb):
                M[name] = m.accum_coin_handoff()
            return ("do", f)
        act = (stp("reinvest_withdraw.json", [{"k": f"-1:{k}", "gain_q": 1000.0} for k in (1, 2, 3)], "w1") if how.startswith("➖")
               else ("do", off_flag))
        b.run(GROWN + [look("a"), act, ("wait", 10), look("b"), receive("n1"), look("c"), receive("n2"), look("d")]
              + walk([1.0, 1.0, 0.99], 20) + [look("e")])
        hos = M["b"]["ho"]
        coin = sum(float(h["coin"]) for h in hos)
        cost = sum(float(h["usd"]) for h in hos)
        e = (M["c"]["acc"].get("acc1") or {})
        e2 = (M["d"]["acc"].get("acc1") or {})
        left = float(((M["c"]["acc"].get("_ri_left_w") or {}).get(gd.wid) or {}).get("XRP") or 0)
        want_c = round(coin * pct / 100.0, 10)
        ok(f"{how} → the accumulator ({pct}%): {len(hos)} handoff(s) {coin:.6f} XRP at their real cost {cost:.6f}$ · the dashboard "
           "receives them once (coin · cost · its line) · " + ("the rest stays the wallet's (counted)" if pct < 100 else "all of it"),
           hos and not M["a"]["ho"] and M["n1"] >= 1 and abs(float(e.get("coin") or 0) - want_c) < 1e-9
           and abs(float(e.get("spent") or 0) - round(cost * pct / 100.0, 6)) < 2e-6 * len(hos)
           and abs(left - (coin - want_c)) < 1e-9 and set(h["id"] for h in hos) <= set(M["c"]["acc"].get("_ri_seen") or [])
           and M["n2"] == 0 and e2 == e and any("🪙" in t for t in TG),
           (how, pct, hos, e, left, M["n1"], M["n2"]))
        ds = [M[k]["d"] for k in "abcde"]
        ok(f"… the guard's coin book = the wallet before · in transit · received · after the next trades ({how} {pct}%) · no alert",
           all(d and abs(d[1]) <= 1e-6 for d in ds) and not gd.coin_al and not [x for x in gd.ev if x[1] not in ("acc_run",)]
           and not b.errors, (ds, gd.coin_al[:2], gd.ev[:3], b.errors[:2]))

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_win: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
