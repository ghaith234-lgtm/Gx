# 🪜 📈 the first sell's distance apart from the distance between sells (v3.36.16) — sp_k = bp × (1 + d1 + (k−1)·d)
#   d1 = step_first (buy → first sell) · d = step_sell (sell → sell, equal between every two sells) · no d1 ⇒ exactly as before
#   ① the layout: the owner's example · equal gaps · no d1 / d1 = d ⇒ the old floats bit for bit · only the sell prices move
#   ② the table = the engine: the dashboard's copy of the layout gives the same slots as the engine's, d1 or not
#   ③ the table refuses any sell that would lose after the two fees · the engine refuses the same settings at birth (no order)
#   ④ the real engine on the mock OKX with d1 ≠ d: the owner's example step by step · random markets audited at every loop ·
#      d1 kept from birth (a later config edit changes nothing) · deploy writes step_first · the clone reads it back
#   python3 devtests/step/t_first.py [Holy_Dashboard.pyw] [-q] [--seeds=N]        (STEP_ENGINE=… tests another engine copy)
import ast, json, math, os, random, re, shutil, sys, tempfile, importlib.machinery, importlib.util
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okxsim
from okxsim import Clock, Ex, Bot, walk

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
SEEDS = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--seeds=")), "12"))
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


def funcs(path, names, ns):
    """the named top-level functions of a file, run alone in ns (no import of the file itself)"""
    src = open(path, encoding="utf-8").read()
    for n in ast.parse(src).body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            exec(compile(ast.Module([n], []), path, "exec"), ns)
    return ns


ENG = funcs(okxsim.ENGINE, {"_dec", "_step_round", "_sig", "step_layout"},
            {"math": math, "Decimal": Decimal, "ROUND_FLOOR": ROUND_FLOOR, "ROUND_CEILING": ROUND_CEILING, "ROUND_HALF_UP": ROUND_HALF_UP})
DSH = funcs(DASH, {"_step_round", "_step_layout"}, {"math": math})
lay_e, lay_d, sig = ENG["step_layout"], DSH["_step_layout"], ENG["_sig"]
SPECS = [(None, None), (0.000001, 0.1), (0.00000001, 0.00001), (1.0, 10.0), (1.0, 100000.0), (0.01, 0.001)]


def rnd(rng):
    p0 = 10 ** rng.uniform(-5, 4.8)
    lot, mn = rng.choice(SPECS)
    d = rng.choice([0.002, 0.004, 0.005, 0.006, 0.01, 0.0125, 0.015, 0.02, 0.033])
    d1 = rng.choice([None, d, 0.0017, 0.003, 0.008, 0.01, 0.012, 0.02, 0.05, rng.uniform(0.0017, 0.06)])
    return dict(P0=p0, G=rng.choice([0.01, 0.02, 0.025, 0.03, 0.05, 0.1]), d=d, N=rng.randint(1, 8),
                Q=rng.choice([5, 10, 15, 30, 60, 250]) * (1 + (mn or 0) * p0), floor=p0 * rng.uniform(0.3, 0.95),
                up=rng.randint(0, 4), fee=rng.choice([0.0008, 0.001, 0.0015]), lot=lot, mn=mn, d1=d1)


def call(fn, a, d1="omit"):
    kw = {} if d1 == "omit" else {"d1": d1}
    return fn(a["P0"], a["G"], a["d"], a["N"], a["Q"], a["floor"], a["up"], a["fee"], a["lot"], a["mn"], **kw)


# ── ① the layout
L = call(lay_e, dict(P0=1.0, G=0.03, d=0.005, N=3, Q=15, floor=0.7, up=1, fee=0.0008, lot=None, mn=None), 0.01)
s0 = [r["sp"] for r in sorted(L, key=lambda r: r["k"]) if r["j"] == 0]
ok("① the owner's example: buy 1.00 · first sell 1% · between sells 0.5% · 3 sells ⇒ 1.010 · 1.015 · 1.020", s0 == [1.01, 1.015, 1.02], s0)
rng = random.Random(7)
gaps, same, moved = [], [], []
for _ in range(500):
    a = rnd(rng)
    d1 = a["d1"] if a["d1"] is not None else a["d"]
    A = call(lay_e, a, None)
    B = call(lay_e, a, a["d"])
    C = call(lay_e, a, d1)
    O = call(lay_e, a)                                   # the old call (no d1 at all)
    old = [sig(r["bp"] * (1.0 + r["k"] * a["d"])) for r in A]
    if not (A == B == O and [r["sp"] for r in A] == old):
        same.append(a)
    if [{k: v for k, v in r.items() if k != "sp"} for r in C] != [{k: v for k, v in r.items() if k != "sp"} for r in A]:
        moved.append(a)
    by = {}
    for r in C:
        by.setdefault(r["j"], []).append(r)
    for j, rs in by.items():
        rs.sort(key=lambda r: r["k"])
        bp = rs[0]["bp"]
        if abs(rs[0]["sp"] - bp * (1 + d1)) > 1e-11 * bp:
            gaps.append(("first", a, j))
        for x, y in zip(rs, rs[1:]):
            if abs((y["sp"] - x["sp"]) - bp * a["d"]) > 1e-10 * bp:
                gaps.append(("gap", a, j, x["k"]))
ok("① 500 random settings: first sell = buy × (1 + d1) · every gap between two sells = buy × d (equal)", not gaps, gaps[:2])
ok("① no d1 · d1 = None · d1 = d ⇒ the old prices bit for bit (bp × (1 + k·d)) — a bot made before stays the same", not same, same[:2])
ok("① d1 moves only the sell prices: the same slots, buy prices, coins, sides, skips", not moved, moved[:2])

# ── ② the table = the engine
diff = []
for _ in range(600):
    a = rnd(rng)
    for d1 in ("omit", None, a["d1"]):
        if call(lay_e, a, d1) != call(lay_d, a, d1):
            diff.append((a, d1))
ok("② 600 random settings × (no d1 · None · d1): the dashboard's table layout = the engine's, slot for slot, float for float", not diff, diff[:2])

# ── ③ + ④: the dashboard module (as in bt3615_test: a closed folder · fake keys · no network)
R = tempfile.mkdtemp(prefix="t_first_")
json.dump({"port": 8098}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-tfirst", "sec": "SECA-tfirst", "pass": "PASA-tfirst"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_first", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_first", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
SPEC = {"XRP-USDT": ("0.0001", "0.000001", "0.1"), "DOGE-USDT": ("0.00001", "1", "10"), "PEPE-USDT": ("0.0000000001", "1", "100000")}
m._okx_pub = lambda p: ({"code": "0", "data": [dict(zip(("tickSz", "lotSz", "minSz"), SPEC[p.split("instId=")[1]]))]}
                        if "instruments" in p and p.split("instId=")[1] in SPEC else None)
m.PX.update({"XRP-USDT": 1.0, "DOGE-USDT": 0.15, "PEPE-USDT": 0.0000123})
m.tg_send = lambda *a, **k: True
F = m.FEE_RATE_DEFAULT
T = max(F, getattr(m, "STEP_TAKER_FEE", F))     # v3.36.18: the table and the birth rule count the taker fee (the worst)


def body(**kw):
    b = {"symbol": "XRP-USDT", "usd_value": "15", "step_parts": "3", "step_sell_pct": "0.5", "step_first_pct": "1", "grid_pct": "3",
         "min_price": "0.7", "up_groups": "1", "forced_base": "1"}
    b.update({k: str(v) for k, v in kw.items()})
    return b


P = m.step_plan(body())
r0 = next((r for r in P.get("rows") or [] if r["j"] == 0), {})
ok("③ the table, the owner's example: level 0 sells at 1.010 · 1.015 · 1.020 · every sell's net profit > 0 · no refusal",
   P.get("ok") and not P["err"] and [s["sp"] for s in r0.get("sells", [])] == [1.01, 1.015, 1.02]
   and all(s["pr"] > 0 for r in P["rows"] for s in r["sells"]) and P["args"]["d1"] == 0.01 and P["args"]["d"] == 0.005, (P.get("err"), r0))
P2 = m.step_plan(body(step_first_pct=""))
a2 = (P2.get("args") or {})
lay2 = lay_e(1.0, 0.03, 0.005, 3, 15, 0.7, 1, F, 0.000001, 0.1)
ok("③ the first-sell field empty ⇒ d1 = the sell spacing ⇒ the table = the old engine layout (bp × (1 + k·d))",
   P2.get("ok") and a2.get("d1") == a2.get("d") == 0.005
   and sorted(s["sp"] for r in P2["rows"] for s in r["sells"]) == sorted(r["sp"] for r in lay2), a2)
for v, word in (("0", "أكبر من صفر"), ("-1", "أكبر من صفر"), ("abc", "تأكد من الأرقام")):
    Pv = m.step_plan(body(step_first_pct=v))
    ok(f"③ first sell «{v}» ⇒ refused ({word})", not Pv.get("ok") and word in str(Pv.get("msg")), Pv.get("msg"))
lim = 1.0 / (1.0 - T) ** 2 - 1.0                          # (1 + d1)(1 − taker)² = 1 — under it a first sell can lose
verdicts = []
for d1 in (0.0005, 0.001, lim * 0.999, lim * 1.001, lim * 1.01, 0.002, 0.003):
    Pv = m.step_plan(body(step_first_pct=repr(d1 * 100), step_sell_pct="0.2"))
    refused = bool(Pv.get("ok") and any("لا تغطي العمولتين" in e and "مسافة أول بيعة" in e for e in Pv["err"]))
    lose = any(s["pr"] <= 0 for r in Pv["rows"] for s in r["sells"] if not s["skip"]) if Pv.get("ok") else None
    eng = any(not r.get("skip") and r["sp"] * (1 - T) * (1 - T) <= r["bp"]
              for r in lay_e(1.0, 0.03, 0.002, 3, 15, 0.7, 1, F, 0.000001, 0.1, d1=d1))
    verdicts.append((round(d1 * 100, 5), refused, lose, eng, d1 > lim))
ok(f"③ around the two taker fees ({lim * 100:.5f}%): the table refuses ⇔ a sell shows ≤ 0 ⇔ the engine's birth rule refuses ⇔ d1 under the limit",
   all(x[1] == x[2] == x[3] == (not x[4]) for x in verdicts), verdicts)
Pw = m.step_plan(body(step_first_pct="2.5", step_sell_pct="0.5", step_parts="4", grid_pct="3"))
ok("③ overlap warning counts buy → last sell = d1 + (N−1)·d (2.5% + 3 × 0.5% = 4% > 3%)",
   any("تمتد (4%)" in w for w in Pw.get("warn") or []), Pw.get("warn"))
Pn = m.step_plan(body(step_first_pct="2.5", step_sell_pct="0.1", step_parts="4", grid_pct="3"))
ok("③ no overlap warning when d1 + (N−1)·d ≤ G (2.5% + 0.3% = 2.8% ≤ 3%)", Pn.get("ok") and not any("تتداخل" in w for w in Pn["warn"]), Pn.get("warn"))
_keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
         if hasattr(m, k)}
spec = {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 0.1}
cfg, err = m._bt_dry_cfg("grid_step", body(step_first_pct="1.2", step_sell_pct="0.6"), "XRP-USDT", spec, 1.0)
for k, v in _keep.items():
    setattr(m, k, v)
ok("④ deploy writes what the engine reads: step_first = 1.2% · step_sell = 0.6%",
   cfg and abs(cfg.get("step_first") - 0.012) < 1e-15 and abs(cfg.get("step_sell") - 0.006) < 1e-15, (cfg, err))
cfg_bad, err_bad = m._bt_dry_cfg("grid_step", body(step_first_pct="0.1", step_sell_pct="0.6"), "XRP-USDT", spec, 1.0)
for k, v in _keep.items():
    setattr(m, k, v)
ok("④ deploy refuses a first sell that loses (0.1% < the two fees) — nothing written", not cfg_bad and "مسافة أول بيعة" in str(err_bad), (cfg_bad, err_bad))
txt = m._pv_cfg_txt({"bot_type": "grid_step", "step_parts": 3, "step_sell": 0.005, "step_first": 0.01, "grid_percentage": 0.03, "usd_value": 15})
txt0 = m._pv_cfg_txt({"bot_type": "grid_step", "step_parts": 3, "step_sell": 0.01, "grid_percentage": 0.03, "usd_value": 15})
ok("④ the settings text shows both distances when they differ · the old text when they don't",
   "أول بيعة 1% · بين البيعات 0.5%" in txt and "البيع 1% ·" in txt0 and "أول بيعة" not in txt0, (txt, txt0))
# ── ⑤ v3.36.18 (the owner 6-11): the table counts the TAKER fee on both sides (the worst) · one graded grid per coin
if hasattr(m, "STEP_TAKER_FEE"):
    Pt = m.step_plan(body())
    s1 = next(x for x in Pt["rows"] if x["j"] == 0)["sells"][0]
    want_pr = s1["q"] * (1 - T) * s1["sp"] * (1 - T) - s1["q"] * 1.0
    ok(f"⑤ the table's profit is the worst case (taker {T * 100:g}% on the buy and the sell): first sell {s1['pr']:+.6f}$ = q·(1−t)·sp·(1−t) − q·bp",
       abs(s1["pr"] - round(want_pr, 6)) < 1e-9 and Pt.get("taker") == T, (s1, want_pr, Pt.get("taker")))
    P18 = m.step_plan(body(step_first_pct="0.18", step_sell_pct="0.3"))
    ok("⑤ first sell 0.18% (covers the maker fees, not the taker ones) ⇒ refused before deploy",
       P18.get("ok") and any("مسافة أول بيعة 0.18%" in e for e in P18["err"]), P18.get("err"))
    _bd = m.bot_dirs
    fake_dir = os.path.join(R, "step_xrp")
    m.bot_dirs = lambda: {fake_dir: {"dir": fake_dir, "symbol": "XRP-USDT", "cfg": {"bot_type": "grid_step", "symbol": "XRP-USDT"}}}
    Pl, Pn = m.step_plan(body(), live=True), m.step_plan(body(), live=False)
    Pd = m.step_plan(body(symbol="DOGE-USDT", forced_base="0.15", min_price="0.1", up_groups="0"), live=True)
    m.launch = lambda bb: (True, "")
    m.wallet_keys = lambda w: {"api_key": "KEYA-tfirst", "secret_key": "SECA-tfirst", "passphrase": "PASA-tfirst"}
    m.ROOT = R
    dx = m.deploy_step(body(wallet="main"))
    dd = m.deploy_step(body(symbol="DOGE-USDT", forced_base="0.15", min_price="0.1", up_groups="0", wallet="main"))
    m.bot_dirs = _bd
    ok("⑤ one graded grid per coin: a 🪜 on XRP-USDT exists ⇒ the form's table says so · deploy refuses · DOGE-USDT is deployed · "
       "the trial path's table (not live) does not refuse",
       any("واحد لكل عملة" in e for e in Pl["err"]) and not any("واحد لكل عملة" in e for e in Pn["err"])
       and not any("واحد لكل عملة" in e for e in Pd.get("err", [])) and not dx.get("ok") and "واحد لكل عملة" in dx.get("msg", "")
       and dd.get("ok"), (Pl["err"][:1], dx.get("msg"), dd.get("msg")))
    cfg_t = json.load(open(os.path.join(R, dd.get("dir", "x"), "config_DOGE-USDT.json"))) if dd.get("ok") else {}
    ok("⑤ deploy writes the taker fee for the bot's own birth rule (taker_rate)", cfg_t.get("taker_rate") == T, cfg_t.get("taker_rate"))
shutil.rmtree(R, ignore_errors=True)

# ── ④ the real engine on the mock OKX
LINE = re.compile(r"^(🟢|🔴) \[(?:شراء|بيع) فوري\] السعر: ([0-9.e+-]+) \| الكمية: ([0-9.e+-]+)(?: \| الربح: ([+-][0-9.e+-]+)\$)?.* المستوى (-?\d+) · الجزء (\d+)/")


def trades(b):
    out = []
    for msg in reversed(b.hist()):
        x = LINE.match(msg)
        if x:
            out.append({"side": "buy" if x.group(1) == "🟢" else "sell", "px": float(x.group(2)), "qty": float(x.group(3)),
                        "profit": float(x.group(4)) if x.group(4) else None, "key": f"{x.group(5)}:{x.group(6)}"})
    return out


def discipline(b, d, d1, fee=0.001):
    S, bad = b.st["slots"], []
    for s in S.values():
        if abs(s["sp"] - sig(s["bp"] * (1.0 + d1 + (s["k"] - 1) * d))) > 1e-12 * s["bp"] and not (d1 == d and s["sp"] == sig(s["bp"] * (1 + s["k"] * d))):
            bad.append(("slot price", s["j"], s["k"], s["sp"]))
    for t in trades(b):
        s = S.get(t["key"])
        if not s:
            bad.append(("unknown slot", t)); continue
        if t["side"] == "buy" and t["px"] > s["bp"] * (1 + 1e-9):
            bad.append(("bought above its price", t["key"], t["px"], s["bp"]))
        if t["side"] == "sell" and t["px"] < s["sp"] * (1 - 1e-9):
            bad.append(("sold under its price", t["key"], t["px"], s["sp"]))
        if t["side"] == "sell" and t["profit"] is not None and t["profit"] <= 0:
            kept = max(0.0, float(s["q"]) * (1 - fee) - t["qty"])
            if not t["profit"] + kept * t["px"] * (1 - fee) > 0:          # (a coarse quantity step: finding F2 — kept coins cover it)
                bad.append(("sell without profit", t["key"], t["profit"]))
    return bad


c = Clock(); ex = Ex(c, base=100, quote=1000)
b = Bot(ex, {"step_first": 0.01, "step_sell": 0.005, "up_groups": 1})
b.run(walk([1.0, 1.0101, 1.0151, 1.0201, 1.0201, 1.0, 1.0, 0.97, 0.9708, 0.9806, 0.9855, 0.9904, 0.9904], 30))
S = b.st["slots"]
f = [(x[2], float(x[3])) for x in ex.fills]
lv = [r for r in sorted(S.values(), key=lambda s: s["k"]) if r["j"] == -1]
ok("④ engine, the owner's example: level 0 sells 1.010 → 1.015 → 1.020 as the price climbs · back to 1.00 buys the three back at 1.00",
   [p for s_, p in f[:3]] == [1.01, 1.015, 1.02] and all(s_ == "sell" for s_, p in f[:3]) and [x for x in f[3:6]] == [("buy", 1.0)] * 3, f[:8])
ok("④ engine: level −1 (0.9708) sells at 0.9805 · 0.9854 · 0.9902 (1% then 0.5% steps of 0.9708) — each sold once on the way up",
   [s["sp"] for s in lv] == [sig(0.970873786408 * x) for x in (1.01, 1.015, 1.02)] and all(s.get("n", 0) == 1 for s in lv), [(s["sp"], s.get("n")) for s in lv])
ok("④ engine: the birth line names both distances · every sell paid after both fees · books = wallet every loop",
   any("مسافة أول بيعة 1.0% · بين البيعات 0.5%" in x for x in b.hist()) and not discipline(b, 0.005, 0.01) and not b.errors
   and all(t["profit"] > 0 for t in trades(b) if t["side"] == "sell"), (b.errors, discipline(b, 0.005, 0.01)))

# d1 is fixed at birth: an edited config later changes nothing
p = os.path.join(b.dir, f"config_{ex.sym}.json")
cf = json.load(open(p)); cf["step_first"] = 0.05; json.dump(cf, open(p, "w"))
sp0 = {k: s["sp"] for k, s in S.items()}
b.run(walk([0.9904, 1.0, 1.0101], 30))
ok("④ engine: step_first edited in the config after birth ⇒ the slots keep their prices (the table = what runs)",
   {k: s["sp"] for k, s in b.st["slots"].items()} == sp0 and b.st["step"].get("d1") == 0.01 and not b.errors, b.errors)

# the engine refuses a losing first sell at birth (a config written by hand — the dashboard refuses it first)
c = Clock(); ex = Ex(c, base=100, quote=1000)
b = Bot(ex, {"step_first": 0.0015, "step_sell": 0.005})
b.audit_on = False
b.run(walk([1.0, 0.97, 1.02], 600))
nlog = sum(1 for x in b.hist() if "لا تغطي العمولتين" in x)
ok("④ engine: first sell 0.15% (under the two fees) ⇒ no slot · no order on OKX · the reason logged once per 10 min (30 min ⇒ 3)",
   not (b.st or {}).get("slots") and not ex.orders and nlog == 3 and (b.st or {}).get("step", {}).get("d1") == 0.0015, (nlog, len(ex.orders)))

# v3.36.18: the birth rule counts the taker fee — 0.18% covers the maker fees but not the taker ones
born18 = []
for extra in ({}, {"taker_rate": 0.0008}):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex, dict({"step_first": 0.0018, "step_sell": 0.005}, **extra))
    b.audit_on = False
    b.run(walk([1.0, 1.0], 30))
    born18.append(bool((b.st or {}).get("slots")))
ok("④ engine: first sell 0.18% ⇒ refused at birth with the default taker fee (0.1%) · born when the config says maker-only (taker_rate 0.08%)",
   born18 == [False, True], born18)

# random markets with d1 ≠ d (both closer and farther than the between-sells distance)
COINS = [("XRP-USDT", "0.0001", "0.000001", "0.1", 1.0), ("BTC-USDT", "0.1", "0.00000001", "0.00001", 65000.0),
         ("DOGE-USDT", "0.00001", "1", "10", 0.15), ("PEPE-USDT", "0.00000001", "1", "100000", 0.0000123)]
worst, nsell = [], 0
for seed in range(SEEDS):
    rng = random.Random(3100 + seed)
    sym, tick, lot, mn, p0 = COINS[seed % 4]
    N = rng.randint(1, 5)
    d = rng.choice([0.002, 0.004, 0.006, 0.01])
    d1 = rng.choice([0.0025, 0.004, 0.008, 0.012, 0.02, 0.03])
    Qv = max(2.5 * N, rng.choice([10, 15, 30])) * (3 if sym == "PEPE-USDT" else 1)
    cfg = {"step_parts": N, "step_sell": d, "step_first": d1, "grid_percentage": rng.choice([0.01, 0.02, 0.03]), "usd_value": float(Qv),
           "min_price": p0 * rng.uniform(0.5, 0.8), "up_groups": rng.randint(0, 3), "forced_base_price": p0, "step_window": rng.choice([4, 8])}
    c = Clock()
    ex = Ex(c, sym=sym, price=p0, tick=tick, lot=lot, mn=mn, base=round(Qv * 6 / p0, 6), quote=4000 * (3 if sym == "PEPE-USDT" else 1),
            partial=rng.choice([0, 0.4]), seed=seed)
    b = Bot(ex, cfg)
    pr, out = p0, []
    for _ in range(150):
        rr = rng.gauss(0, rng.choice([0.004, 0.01]))
        if rng.random() < 0.03:
            rr += rng.choice([-1, 1]) * rng.uniform(0.04, 0.1)
        pr = max(p0 * 0.4, min(p0 * 2.2, pr * math.exp(rr)))
        out.append(pr)
    b.run(walk(out, hold=rng.choice([3.0, 9.0])))
    dis = discipline(b, d, d1)
    nsell += sum(1 for t in trades(b) if t["side"] == "sell")
    if b.errors or dis or b.audits < 50:
        worst.append((seed, sym, cfg, b.errors[:2], dis[:2]))
ok(f"④ engine: {SEEDS} random markets × 4 coin kinds with d1 ≠ d (closer and farther) ⇒ every slot priced bp × (1 + d1 + (k−1)·d) · "
   f"books = wallet every loop · never bought over / sold under · every sell paid ({nsell} sells)", not worst and nsell > SEEDS * 3, worst[:2])

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
