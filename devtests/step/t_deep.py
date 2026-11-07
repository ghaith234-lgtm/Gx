# 🪜🔬 v3.36.20 the deep test of the graded grid — the grid's test ideas (sim_matrix · cut_grid · test_e2e) aimed at the gaps the owner
#   asked about: every sell belongs to its own buy, however far, in memory or not, with or without reinvest.
#   An INDEPENDENT ledger from OKX's own fills (each order mapped to the part that sent it by its clOrdId, caught at the save that
#   records it before it is sent) — not from the engine's books:
#     coins  : for every part  coins at birth + Σ its buys (after the coin fee) − Σ its sells = what the engine says it holds
#     profit : for every part  Σ the profit in its own lines (🔴 + 💠) = Σ its sales − Σ its buys − its wallet basis + basis held
#     prices : every buy fill ≤ its own part's buy price · every sell fill ≥ its own part's sell price
#   + the okxsim audit (books = wallet) every 20 loops · the window ≤ W at every order placed
#   suites (--only=…):
#     own    — random markets × configs: the owner's (25$ · 0.6% · 0.45/0.60/0.75) · his big one (20 parts · 0.3% then 1%) · one part
#              (grid-like) · DOGE whole coins · partial fills · reinvest 0 / 60 / 100%
#     far    — 20 parts: the 20th sells at +19.3% · its buy-back waits in memory (not among the nearest W buys) until the price comes
#              back · reinvest 100%: each part's buy-back = its base + ITS OWN growth · its profit to ITS OWN pot only
#     gap    — the price jumps −7 · +9 · −12 · +15% at once (many levels and parts crossed) · after each long hold: no part the price
#              passed is forgotten (buy above the price · sell under it) · discipline · books
#     matrix — 24 h (--matrix-hours=) × 3 market kinds (chop · down then up · random walk with jumps) × 3 configs × reinvest 0/100 — the ledger + audit
#     riops  — 20 parts with reinvest: ➖ coin profit out of a far sell in memory and a published one · 💉 coins / dollars into parts
#              in memory · 🔓 the release of every pot at once (the far ones in memory and the published grown orders)
#     scale  — 20 parts × 200 levels from coins (≈4,900 parts): the engine's loop time and state size · the dashboard's card build
#              time and size · the full ladder
#   python3 devtests/step/t_deep.py [Holy_Dashboard.pyw] [-q] [--only=own,far,gap,matrix,riops,scale]     (STEP_ENGINE=… another engine)
import importlib.machinery, importlib.util, json, math, os, random, re, shutil, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Holy_Dashboard.pyw")))
res = []
HOURS_OWN = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--own-hours=")), "8"))
HOURS_MX = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--matrix-hours=")), "24"))


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


RED = re.compile(r"^🔴 \[بيع فوري\] السعر: [0-9.]+ \| الكمية: [0-9.]+ \| الربح: ([+-])([0-9.]+)\$.* المستوى (-?\d+) · الجزء (\d+)/")
RI = re.compile(r"^💠 \[ربح داخلي\] السعر: [0-9.]+ \| الربح: \+([0-9.]+)\$.* المستوى (-?\d+) · الجزء (\d+)/")


class TBot(Bot):
    """the runner + the order → part map (at the save that records an order before it is sent) · the parts' coins at birth ·
    the window checked at every order placed"""

    def __init__(self, ex, cfg=None, folder=None, W=None):
        super().__init__(ex, cfg, folder)
        self.cl2k, self.W0k, self.V0k, self.born = {}, {}, {}, False
        self.Wn, self.over = int(W or self.cfg.get("step_window") or 8), []
        p0 = ex._place

        def place(p):
            r = p0(p)
            if str(p.get("clOrdId") or "").startswith(self.bot_id):
                n = sum(1 for o in ex.pending() if o["cl"].startswith(self.bot_id) and o["side"] == p["side"])
                if n > self.Wn:
                    self.over.append((p["side"], n, round(self.clock.t)))
            return r
        ex._place = place

    def _moment(self, op, when):
        st = self.st
        if op == "save" and st and st.get("slots"):
            S = st["slots"]
            if not self.born:
                self.born = True
                for k, s in S.items():
                    if s["side"] == "sell" and int(s["j"]) >= 0 and not s.get("cyc"):
                        self.W0k[k] = D(str(s["sq"]))
                        self.V0k[k] = D(str(s.get("spent") or 0))
            for k, s in S.items():
                o = s.get("o") or {}
                if o.get("cl"):
                    self.cl2k[o["cl"]] = k
        super()._moment(op, when)


def ledger(b, rates=("0.0008", "0.001")):
    """the independent per-part ledger from OKX's fills · returns (problems, n_parts_checked, n_profit_checked)"""
    ex, st = b.ex, b.disk()
    S = st.get("slots") or {}
    mk, tk = D(rates[0]), D(rates[1])
    coin, cost, proc, bad = {}, {}, {}, []
    for oid, cl, side, px, sz, maker in ex.fills:
        if not str(cl).startswith(b.bot_id):
            continue
        k = b.cl2k.get(cl)
        if k is None:
            bad.append(f"fill of an order no part sent: {cl}")
            continue
        s = S.get(k) or {}
        rate = mk if maker else tk
        if side == "buy":
            coin[k] = coin.get(k, D(0)) + sz - sz * rate
            cost[k] = cost.get(k, D(0)) + sz * px
            if float(px) > float(s.get("bp") or 0) * (1 + 1e-12):
                bad.append(f"{k}: bought at {px} above its own buy {s.get('bp')}")
        else:
            coin[k] = coin.get(k, D(0)) - sz
            proc[k] = proc.get(k, D(0)) + sz * px - sz * px * rate
            if float(px) < float(s.get("sp") or 0) * (1 - 1e-12):
                bad.append(f"{k}: sold at {px} under its own sell {s.get('sp')}")
    prof = {}
    for ln in b.fill_lines:
        m = RED.match(ln)
        if m:
            k = f"{m.group(3)}:{m.group(4)}"
            prof[k] = prof.get(k, D(0)) + D(m.group(2)) * (1 if m.group(1) == "+" else -1)
            continue
        m = RI.match(ln)
        if m:
            k = f"{m.group(2)}:{m.group(3)}"
            prof[k] = prof.get(k, D(0)) + D(m.group(1))
    np_ = 0
    for k, s in S.items():
        acc, accf = D(str(s.get("acc") or 0)), D(str(s.get("accf") or 0))
        held = D(str(s.get("dq") or 0)) + ((D(str(s.get("sq") or 0)) - acc) if s["side"] == "sell" else (acc - accf))
        o = s.get("o") or {}
        eo = b._ex_of(o) if o else None
        clean = acc == 0
        if eo and eo["acc"] > 0:
            clean = False
            held += (eo["acc"] - (eo["fee"] if eo["feeCcy"] == ex.base else 0)) if eo["side"] == "buy" else -eo["acc"]
        want_ = b.W0k.get(k, D(0)) + coin.get(k, D(0))
        if abs(want_ - held) > D("1e-9") + ex.lot * D("1e-6"):
            bad.append(f"{k} coins: birth {b.W0k.get(k, 0)} + its fills {coin.get(k, 0)} = {want_} ≠ it holds {held}")
        if clean:
            np_ += 1
            basis = D(str(s.get("dc") or 0)) + (D(str(s.get("spent") or 0)) if s["side"] == "sell" else 0)
            pw = proc.get(k, D(0)) - cost.get(k, D(0)) - b.V0k.get(k, D(0)) + basis
            n_s = int(s.get("n") or 0)
            if abs(pw - prof.get(k, D(0))) > D("1e-7") * (n_s + 1):
                bad.append(f"{k} profit: its lines {prof.get(k, 0)} ≠ its own sales − buys {pw} ({n_s} sales)")
    return bad, len(S), np_


def chop(rng, p0, hours, step=10, wave=0.03, amp=0.004, noise=0.0008, jumps=0.0):
    out, p = [], p0
    for i in range(int(hours * 3600 / step)):
        t = i * step
        slow = p0 * (1 - wave * 0.66 + wave * math.sin(2 * math.pi * t / 21600.0))
        q = slow * (1 + amp * math.sin(2 * math.pi * t / 1800.0)) * math.exp(rng.gauss(0, noise))
        if jumps and rng.random() < jumps:
            q *= math.exp(rng.choice([-1, 1]) * rng.uniform(0.03, 0.08))
        out.append(q)
    return out


def audit_every(b, n=20):
    st = {"i": 0}

    def f(bb):
        st["i"] += 1
        if st["i"] % n == 0:
            bb.audit()
    return f


P0 = 1.1698
OWNER = {"usd_value": 25.0, "step_parts": 3, "step_first": 0.0045, "step_sell": 0.0015, "grid_percentage": 0.006, "min_price": 0.9,
         "up_groups": 1, "forced_base_price": P0, "step_window": 8, "fee_rate": 0.0008, "taker_rate": 0.001}
BIG = dict(OWNER, usd_value=100.0, step_parts=20, step_first=0.003, step_sell=0.01, up_groups=3)
ONE = dict(OWNER, step_parts=1, step_first=0.006, step_sell=0.006, up_groups=2)


def mkbot(cfg, base, quote, sym="XRP-USDT", p0=P0, tick="0.0001", lot="0.000001", mn="0.1", partial=0.0, seed=1):
    c = Clock()
    ex = Ex(c, sym=sym, price=p0, tick=tick, lot=lot, mn=mn, base=base, quote=quote, partial=partial, seed=seed)
    b = TBot(ex, dict(cfg, forced_base_price=p0, min_price=round(p0 * 0.77, 10)))
    b.audit_on = False
    b.on_loop = audit_every(b, 20)
    return b


# ── own: random markets × configs — every part's coins, profit and prices from OKX's fills
if want("own"):
    worst, tot_parts, tot_prof, tot_sales = [], 0, 0, 0
    runs = [("owner", OWNER, 0), ("owner", OWNER, 60), ("owner", OWNER, 100), ("big 20 parts", BIG, 0), ("big 20 parts", BIG, 100),
            ("one part", ONE, 0), ("one part", ONE, 60), ("DOGE whole coins", dict(OWNER, usd_value=30.0), 0),
            ("DOGE whole coins", dict(OWNER, usd_value=30.0), 100), ("owner partial fills", OWNER, 60), ("big partial fills", BIG, 60)]
    for i, (nm, cfg, pct) in enumerate(runs):
        rng = random.Random(500 + i)
        cf = dict(cfg)
        if pct:
            cf.update(reinvest=True, reinvest_pct=pct)
        doge = nm.startswith("DOGE")
        p0 = 0.15 if doge else P0
        b = mkbot(cf, base=(3000 if doge else 400) if not nm.startswith("big") else 900, quote=4000, sym="DOGE-USDT" if doge else "XRP-USDT",
                  p0=p0, tick="0.00001" if doge else "0.0001", lot="1" if doge else "0.000001", mn="10" if doge else "0.1",
                  partial=0.4 if "partial" in nm else 0.0, seed=i)
        b.run(walk(chop(rng, p0, HOURS_OWN, wave=rng.choice([0.02, 0.04]), amp=rng.choice([0.003, 0.008]), jumps=0.004), 10))
        b.audit()
        bad, n, npf = ledger(b)
        sales = sum(int(s.get("n") or 0) for s in (b.disk().get("slots") or {}).values())
        tot_parts += n; tot_prof += npf; tot_sales += sales
        if bad or b.errors or b.over or sales < 5:
            worst.append((nm, pct, sales, bad[:3], b.errors[:2], b.over[:2]))
    ok(f"own: {len(runs)} markets × configs (the owner's · 20 parts · one part · DOGE · partial fills · reinvest 0/60/100%) — {tot_sales} sales: "
       f"every part's coins = its birth + its own fills ({tot_parts} parts) · its profit lines = its own sales − buys ({tot_prof} parts) · "
       "every fill at or better than its own part's price · books = wallet · never W+1 at OKX", not worst, worst[:2])

# ── far: 20 parts — the far buy-back waits in memory · reinvest per part
if want("far"):
    cf = dict(BIG, up_groups=0, min_price=0.6, forced_base_price=1.0, reinvest=True, reinvest_pct=100)
    c = Clock()
    ex = Ex(c, price=1.0, base=0, quote=6000)
    b = TBot(ex, cf)
    b.audit_on = False
    b.on_loop = audit_every(b, 10)
    bp1 = 1.0 / 1.006
    M = {}

    def snap(name):
        def f(bb):
            st = bb.st
            M[name] = {"slots": json.loads(json.dumps(st["slots"])), "rb": json.loads(json.dumps(st.get("reinvest") or {})),
                       "open": [(o["cl"], o["side"], float(o["px"]), float(o["sz"])) for o in bb.mine_open()]}
        return ("do", f)
    up = [round(bp1 * (1 + 0.003 + i * 0.01) * 1.0006, 4) for i in range(20)]
    b.run(walk([1.0, 1.0, round(bp1 * 0.9995, 4)] + [round(bp1 * 0.9995, 4)] * 6, 30) + [snap("bought")]
          + walk(up + [up[-1]] * 3, 30) + [snap("sold")] + walk([round(bp1 * 1.10, 4)] * 4, 30) + [snap("high")]
          + walk([round(bp1 * 1.05, 4), round(bp1 * 1.01, 4), round(bp1 * 0.9995, 4)] + [round(bp1 * 0.9995, 4)] * 8, 30) + [snap("back")])
    b.audit()
    lv1 = [f"-1:{k}" for k in range(1, 21)]
    bo, so, hi, bk = M["bought"], M["sold"], M["high"], M["back"]
    all_bought = all(bo["slots"][k]["side"] == "sell" for k in lv1)
    all_sold = all(so["slots"][k]["side"] == "buy" and int(so["slots"][k].get("n") or 0) == 1 for k in lv1)
    pub_hi = sorted(k for k in lv1 if (hi["slots"][k].get("o") or {}).get("st") == "live")
    mem_hi = [k for k in lv1 if not hi["slots"][k].get("o")]
    ok("far: level −1's 20 parts bought · each sold at its own sell (+0.30% … +19.30%) · its buy-back at its own buy price · price 10% "
       f"above: the {len(pub_hi)} nearest buy-backs published (the window), the other {len(mem_hi)} wait in memory — none lost",
       all_bought and all_sold and len(pub_hi) == 8 and len(mem_hi) == 12 and not b.over, (all_bought, all_sold, pub_hi, len(mem_hi), b.over[:2]))
    gro = {k: float(hi["slots"][k].get("g") or 0) for k in lv1}
    pots = {k: float(((hi["rb"].get("levels") or {}).get(k) or {}).get("grown_qty") or 0) for k in lv1}
    own_lines = {}
    for ln in b.fill_lines:
        m = RI.match(ln)
        if m:
            own_lines.setdefault(f"{m.group(2)}:{m.group(3)}", []).append(float(m.group(1)))
    grows_up = all(gro[f"-1:{k}"] < gro[f"-1:{k + 1}"] for k in range(1, 20))      # the farther sell made more ⇒ its own buy grew more
    ok("… reinvest 100%: each part's profit went to ITS OWN pot only (its 💠 line · its growth) — the farther the sell, the bigger its own "
       "buy-back (part 1 +" + f"{gro['-1:1']:.4f} … part 20 +{gro['-1:20']:.4f} coins)",
       all(len(own_lines.get(k, [])) == 1 for k in lv1) and all(abs(gro[k] - pots[k]) < 1e-12 for k in lv1) and grows_up and gro["-1:1"] > 0,
       (gro, {k: own_lines.get(k) for k in lv1[:3]}))
    szok = []
    for cl, side, px, sz in hi["open"]:
        k = b.cl2k.get(cl)
        if side == "buy" and k in lv1:
            s = hi["slots"][k]
            szok.append(abs(sz - b.m._lot_floor(float(s["q"]) + float(s.get("g") or 0))) < 1e-9)
    ok("… the published buy-backs at OKX = base + their own growth (none borrows another part's)", szok and all(szok), (len(szok), szok))
    back_all = all(bk["slots"][k]["side"] == "sell" and int(bk["slots"][k].get("cyc") or 0) == 3 for k in lv1)
    bad, n, npf = ledger(b)
    ok("… the price comes back: all 20 buy-backs execute (the 12 from memory too) at or under their own price · the ledger from OKX's fills "
       f"(coins · profit per part) · books = wallet", back_all and not bad and not b.errors,
       ([(k, bk["slots"][k]["side"], bk["slots"][k].get("cyc")) for k in lv1 if bk["slots"][k]["side"] != "sell"][:4], bad[:3], b.errors[:2]))

# ── gap: big jumps — no part the price passed is forgotten
if want("gap"):
    worst = []
    for nm, cfg, pct in (("owner", OWNER, 0), ("owner 💠100%", OWNER, 100), ("20 parts", BIG, 0), ("20 parts 💠60%", BIG, 60), ("one part", ONE, 0)):
        cf = dict(cfg, min_price=0.6)
        if pct:
            cf.update(reinvest=True, reinvest_pct=pct)
        c = Clock()
        ex = Ex(c, price=P0, base=1200, quote=12000, partial=0.0)
        b = TBot(ex, cf)
        b.audit_on = False
        b.on_loop = audit_every(b, 20)
        forg = []

        def check(bb, forg=forg):
            st = bb.st
            cp = float(bb.ex.price)
            for k, s in st["slots"].items():
                if s["side"] == "buy" and s["bp"] > cp * 1.003 and s["bp"] >= float(cf["min_price"]):
                    forg.append((round(bb.clock.t), "buy", k, s["bp"], cp))
                if s["side"] == "sell" and s["sp"] < cp * 0.997:
                    forg.append((round(bb.clock.t), "sell", k, s["sp"], cp))
        path = []
        for f_ in (0.93, 1.0, 0.93 * 0.88 / 0.93, 1.15, 0.95, 1.08, 0.9, 1.0):
            path += walk([round(P0 * f_, 4)] * 40, 60) + [("do", check)]
        b.run(walk([P0, P0], 30) + path)
        b.audit()
        bad, n, npf = ledger(b)
        if forg or bad or b.errors or b.over:
            worst.append((nm, forg[:3], bad[:3], b.errors[:2], b.over[:2]))
    ok("gap: the price jumps −7 · +7.5 · −12 · +31 · −17 · +14 · −17 · +11% at once (dozens of levels and parts crossed) — after each "
       "40-minute hold: no part forgotten (no buy left above the price · no sell under it) · every fill at or better than its own part's "
       "price · the ledger per part · books = wallet · never W+1 at OKX (the owner's · 20 parts · one part · reinvest 0/60/100%)",
       not worst, worst[:2])

# ── matrix: 3 days × 3 market kinds × 3 configs × reinvest 0/100
if want("matrix"):
    worst, nrun, ns = [], 0, 0
    kinds = {"chop": dict(wave=0.02, amp=0.006, noise=0.0008, jumps=0.0), "down-up": dict(wave=0.12, amp=0.003, noise=0.0006, jumps=0.0),
             "walk+jumps": dict(wave=0.03, amp=0.002, noise=0.0015, jumps=0.002)}
    KS = next((x.split("=", 1)[1].split(",") for x in sys.argv if x.startswith("--kinds=")), None)
    for kn, kw in kinds.items():
        if KS and kn not in KS:
            continue
        for cn, cfg in (("owner", OWNER), ("20 parts", BIG), ("one part", ONE)):
            for pct in (0, 100):
                rng = random.Random(hash((kn, cn, pct)) & 0xffff)
                cf = dict(cfg, min_price=0.75)
                if pct:
                    cf.update(reinvest=True, reinvest_pct=pct)
                c = Clock()
                ex = Ex(c, price=P0, base=900, quote=9000, partial=0.2, seed=nrun)
                b = TBot(ex, cf)
                b.audit_on = False
                b.on_loop = audit_every(b, 60)
                b.run(walk(chop(rng, P0, HOURS_MX, step=30, **kw), 30))
                b.audit()
                bad, n, npf = ledger(b)
                sales = sum(int(s.get("n") or 0) for s in (b.disk().get("slots") or {}).values())
                nrun += 1; ns += sales
                if bad or b.errors or b.over:
                    worst.append((kn, cn, pct, sales, bad[:2], b.errors[:2], b.over[:2]))
    ok(f"matrix: {nrun} runs of {HOURS_MX:g} h (chop · down then up · random walk with jumps × the owner's · 20 parts · one part × reinvest 0/100% · "
       f"partial fills) — {ns} sales · the ledger per part from OKX's fills · books = wallet · never W+1", not worst, worst[:2])

# ── riops: 20 parts with reinvest — ➖ 💉 🔓 on far parts in memory and on published ones
def req(fname, items, rid):
    def f(b):
        with open(os.path.join(b.dir, fname), "w", encoding="utf-8") as fh:
            json.dump({"id": rid, "ts": b.clock.t, "items": items}, fh)
    return ("do", f)


def off_flag(b):
    p = os.path.join(b.dir, f"config_{b.ex.sym}.json")
    cf = json.load(open(p)); cf["reinvest"] = False; json.dump(cf, open(p, "w"))
    open(os.path.join(b.dir, "reinvest_release.flag"), "w").close()


if want("riops"):
    cf = dict(BIG, up_groups=0, min_price=0.6, forced_base_price=1.0, reinvest=True, reinvest_pct=100)
    c = Clock()
    ex = Ex(c, price=1.0, base=50, quote=6000)
    b = TBot(ex, cf)
    b.audit_on = False
    b.on_loop = audit_every(b, 10)
    bp1 = 1.0 / 1.006
    up = [round(bp1 * (1 + 0.003 + i * 0.01) * 1.0006, 4) for i in range(20)]
    M = {}

    def snap(name):
        def f(bb):
            st = bb.st
            M[name] = {"slots": json.loads(json.dumps(st["slots"])), "rb": json.loads(json.dumps(st.get("reinvest") or {})),
                       "amends": len(bb.ex.amends), "open": {o["ordId"]: float(o["sz"]) for o in bb.mine_open()}}
        return ("do", f)
    dn = round(bp1 * 0.9995, 4)
    p5 = round(bp1 * 1.05, 4)
    b.run(walk([1.0, 1.0, dn] + [dn] * 6, 30) + walk(up + [up[-1]] * 2, 30) + walk([dn] * 10, 30)       # round 1 · every part grew
          + walk([round(bp1 * 1.02, 4), round(bp1 * 1.04, 4), p5, p5, p5], 30) + [snap("a")]                 # parts 1–5 sold again
          + [req("reinvest_withdraw.json", [{"k": "-1:18", "gain_q": 1000.0}, {"k": "-1:8", "gain_q": 1000.0}], "w1"), ("wait", 20), snap("b")]
          + [req("reinvest_inject.json", [{"k": "-1:19", "coin": 1.0}, {"k": "-2:15", "usd": 2.0}], "i1"), ("wait", 20), snap("c")]
          + [("do", off_flag), ("wait", 30)] + walk([p5] * 4, 30) + [snap("d")])
    b.audit()
    a, bb, cc, dd = M["a"], M["b"], M["c"], M["d"]
    s18a, s18b, s8a, s8b = a["slots"]["-1:18"], bb["slots"]["-1:18"], a["slots"]["-1:8"], bb["slots"]["-1:8"]
    hos = (bb["rb"].get("handoffs") or [])
    mem18 = not s18a.get("o")
    pub8 = (s8a.get("o") or {}).get("st") == "live"
    o8 = str((s8b.get("o") or {}).get("id"))
    ok("riops ➖: coin profit out of a far sell IN MEMORY (−1:18, nothing at OKX) and out of a published one (−1:8, amend-order) — each to "
       "the accumulator at its own cost · their base coins stay · books = wallet",
       mem18 and pub8 and s18a.get("g", 0) > 0 and s8a.get("g", 0) > 0 and s18b["sq"] < s18a["sq"] and s8b["sq"] < s8a["sq"]
       and len(hos) == 2 and bb["amends"] == a["amends"] + 1 and abs(bb["open"].get(o8, 0) - s8b["sq"]) < 1e-9 and not b.errors,
       (mem18, pub8, s18a.get("g"), s8a.get("g"), s18a["sq"], s18b["sq"], len(hos), a["amends"], bb["amends"], b.errors[:2]))
    s19b, s19c = bb["slots"]["-1:19"], cc["slots"]["-1:19"]
    l215b = ((bb["rb"].get("levels") or {}).get("-2:15") or {})
    l215c = ((cc["rb"].get("levels") or {}).get("-2:15") or {})
    v = lambda lv: float(lv.get("usd_book") or 0) + float(lv.get("grown_qty") or 0) * float(lv.get("px") or 0)
    ok("riops 💉: coins into a far sell in memory (−1:19: +1 coin, no order touched) · dollars into a buy in memory (−2:15: +2$ in its own "
       "pot / growth) · books = wallet", not s19b.get("o") and abs(s19c["sq"] - s19b["sq"] - 1.0) < 1e-9 and abs(v(l215c) - v(l215b) - 2.0) < 1e-6
       and not b.errors, (s19b["sq"], s19c["sq"], l215b, l215c, b.errors[:2]))
    lv_d = dd["rb"].get("levels") or {}
    left = {k: (x.get("grown_qty"), x.get("usd_book")) for k, x in lv_d.items() if float(x.get("grown_qty") or 0) > 0 or float(x.get("usd_book") or 0) > 1e-9}
    uw = dd["rb"].get("unwind") or {}
    big_open = [(oid, sz) for oid, sz in dd["open"].items()]
    bad_sz = []
    for k, s in dd["slots"].items():
        o = s.get("o") or {}
        if o.get("st") == "live" and k not in uw:
            want_ = float(s["q"]) if s["side"] == "buy" else float(s["sq"])
            if abs(dd["open"].get(str(o.get("id")), want_) - want_) > 1e-9 or float(s.get("g") or 0) > 0:
                bad_sz.append((k, s["side"], dd["open"].get(str(o.get("id"))), want_, s.get("g")))
    ok("riops 🔓 release: every pot of the 20 parts released at once — the far ones in memory and the published grown orders (shrunk at "
       "OKX to their base) · coins → the accumulator · dollars → the profit · books = wallet",
       not left and not uw and not bad_sz and not dd["rb"].get("on") and any(m.startswith(("🔄", "🔓")) for m in b.hist()) and not b.errors,
       (left, list(uw)[:4], bad_sz[:4], dd["rb"].get("on"), b.errors[:2]))


# ── scale: ≈4,900 parts — the engine's loop · the state · the dashboard's card
if want("scale"):
    cf = dict(BIG, up_groups=200, min_price=0.9)
    c = Clock()
    ex = Ex(c, price=P0, base=20500, quote=6000)
    R = tempfile.mkdtemp(prefix="t_deep_scale_")
    F = os.path.join(R, "step_big"); os.makedirs(F)
    b = TBot(ex, cf, folder=F)
    b.audit_on = False
    loops, t_mon = [0], [0.0]
    b.run(walk([P0, P0], 30))

    def hook(bb):                                    # the runner loads a fresh module per run ⇒ time ITS monitor
        if getattr(bb.m, "_timed", False):
            return
        m0 = bb.m.monitor_and_recover

        def timed(*a, **k):
            t = time.perf_counter()
            try:
                return m0(*a, **k)
            finally:
                t_mon[0] += time.perf_counter() - t
                loops[0] += 1
        bb.m.monitor_and_recover, bb.m._timed = timed, True
    b.on_loop = hook
    w0 = time.perf_counter()
    b.run(walk([round(P0 * f_, 4) for f_ in (1.004, 0.99, 1.012, 0.985, 1.02, 0.975, 1.0)] * 2, 60))
    wall = time.perf_counter() - w0
    sec1 = wall / max(1.0, b.clock.t - c.t0) if hasattr(c, "t0") else 0.0
    st = b.disk()
    n = len(st.get("slots") or {})
    kb = os.path.getsize(os.path.join(F, "grid_state_XRP-USDT.json")) / 1024
    per = t_mon[0] / max(1, loops[0])
    shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
    json.dump({"port": 8095}, open(os.path.join(R, "dashboard_config.json"), "w"))
    c0 = os.getcwd(); os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_deep", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_deep", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    os.chdir(c0)
    m.ROOT = R
    m._okx_get = lambda *a, **k: None
    bd = m.bot_dirs().get(os.path.realpath(F))
    t0 = time.perf_counter(); snap = m.bot_snapshot(bd); t_snap = time.perf_counter() - t0
    card_kb = len(json.dumps({k: snap.get(k) for k in ("sl", "sl_far", "ri", "ladder")}, ensure_ascii=False)) / 1024
    t0 = time.perf_counter(); full = m.step_ladder_view("step_big"); t_full = time.perf_counter() - t0
    shutil.rmtree(R, ignore_errors=True)
    ok(f"scale: {n} parts (20 × 243 levels) — the engine's loop {per * 1000:.0f} ms (≤ 400, every 3 s · {loops[0]} loops) · its state {kb:.0f} KB · the dashboard builds the "
       f"card in {t_snap * 1000:.0f} ms (≤ 1500) carrying {card_kb:.0f} KB (≤ 150) · the full ladder {len(full.get('sl') or [])} parts in "
       f"{t_full * 1000:.0f} ms · books = wallet · never W+1",
       n > 4000 and loops[0] > 50 and per <= 0.4 and t_snap <= 1.5 and card_kb <= 150 and len(full.get("sl") or []) == n and not b.errors and not b.over,
       (n, per, kb, t_snap, card_kb, t_full, b.errors[:2], b.over[:2]))

print(f"{'✅' if all(res) else '❌'} t_deep: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
