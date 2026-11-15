# 🩺 v3.36.51 — the full audit, batch 2: the real engines on hard price paths, their books against the wallet. The owner (14-11): «سوي فحص
#   لكل البوت واكتشف ان هناك اخطاء بكل شي» ⇒ (on the two engine faults found) «صلح الاثنين ويا تحذير النموذج».
#   Each case = the real engine in the trial sandbox (a closed folder · fake keys · no network), in its own process:
#   ① every bot kind (9) through a fast oscillation and a 45% crash-and-back: reaches the end · no negative balance · no order refused
#      for anything but balance · no broken number in its state · what it says it earned = what the wallet gained (after fees, within
#      what the coins still held can explain)
#   ② ♾️ ➕ 🎚️ on a 64,000$ coin (price step 0.1 — BTC) and a 3,000$ coin (step 0.05) with a 10$ order: they TRADE (it was quantity 0 ⇒
#      never one order · and the price went out as 63618.200000000004 ⇒ «Parameter px error»), every order ≈ 10$ (it was 0.01 coin =
#      640$ or nothing) and SOL keeps trading as before
#   ③ DCA with too little balance (the loop every 5 seconds, as live): refused orders ≤ one every 20–60 seconds (it was every loop) and
#      the same trades as before
#   python3 devtests/t_eng_audit.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, shutil, subprocess, sys, tempfile, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.abspath(os.environ.get("ENG_DASH") or os.path.join(H, "..", "Holy_Dashboard.pyw"))
F = float(os.environ.get("ENG_F", "1"))
SYM, P0, DT = "SOL-USDT", 80.0 * F, float(os.environ.get("ENG_DT", "60"))
SPEC = json.loads(os.environ.get("ENG_SPEC", '{"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}'))
BODY = {"grid_plus": {"g_type": "grid_plus", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0", "buy_offset": "1.2"},
        "grid": {"g_type": "grid", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0"},
        "grid_range": {"g_type": "grid_range", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0", "lower_price": "70", "upper_price": "90"},
        "grid_step": {"usd_value": "30", "step_parts": "3", "step_sell_pct": "0.8", "grid_pct": "1.5", "min_price": "50", "up_groups": "2"},
        "dca": {"base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2", "size_multiplier": "1.2", "max_safety_orders": "5", "take_profit_pct": "0.6", "dca_type": "dca"},
        "dca_buy": {"base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2", "size_multiplier": "1.2", "max_safety_orders": "5", "take_profit_pct": "0.6", "dca_type": "dca_buy"},
        "rec_buy": {"rec_type": "rec_buy", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6", "cap": "300", "lo": "60", "hi": "120"},
        "rec_sell": {"rec_type": "rec_sell", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6", "cap": "300"},
        "rec_va": {"start_usd": "20", "va_mode": "fixed", "every": "1", "unit": "h", "band_pct": "2", "max_order": "20", "cap": "300"}}
def path(sc):
    rnd = random.Random(7)
    if sc in ("osc", "thin"):
        return [P0] * 60 + [P0 * (1 + 0.03 * math.sin(2 * math.pi * i / 150)) for i in range(3000)] + [P0] * 120, 0.03
    if sc == "crash":
        return [P0] * 60 + [P0 * (1 - 0.45 * i / 1200) for i in range(1200)] + [P0 * (0.55 + 0.45 * i / 1200) for i in range(1201)] + [P0] * 240, 0.45
    if sc == "pump":
        return [P0] * 60 + [P0 * (1 + 0.45 * i / 1200) for i in range(1200)] + [P0 * (1.45 - 0.45 * i / 1200) for i in range(1201)] + [P0] * 240, 0.45
    if sc == "gaps":
        p, out = P0, [P0] * 60
        for i in range(2400):
            p *= math.exp(rnd.gauss(0, 0.0015))
            if i % 120 == 60: p *= 1 + rnd.choice((-1, 1)) * 0.06
            p = min(max(p, P0 * 0.6), P0 * 1.4); out.append(p)
        out += [p + (P0 - p) * i / 600 for i in range(1, 601)] + [P0] * 240
        return out, max(abs(x / P0 - 1) for x in out)
if os.environ.get("ENG_CHILD"):
    kind, sc, ri = sys.argv[1], sys.argv[2], len(sys.argv) > 3
    def _no_net(*a, **k): raise OSError("no network")
    import requests
    requests.get = requests.post = requests.request = _no_net
    requests.Session.request = lambda self, *a, **k: _no_net()
    urllib.request.urlopen = _no_net
    R = tempfile.mkdtemp(prefix="eng_"); shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_eng", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_eng", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.tg_send = lambda *a, **k: True
    spec = SPEC
    body = dict(BODY[kind], symbol=SYM)
    for k_ in ("min_price", "lower_price", "upper_price", "lo", "hi"):
        if k_ in body: body[k_] = repr(float(body[k_]) * F)
    for k_ in ("base_order_qty", "avg_order_qty"):
        if k_ in body: body[k_] = repr(float(body[k_]) / F)
    if ri: body.update(reinvest=True, reinvest_pct="60")
    px, A = path(sc)
    keep = {k: m.__dict__.get(k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
    cfg, err = m._bt_dry_cfg(kind, body, SYM, spec, P0)
    m.__dict__.update(keep)
    if not cfg:
        print(json.dumps({"kind": kind, "sc": sc, "err": "cfg: " + str(err)})); sys.exit(0)
    q0, b0 = m._bt_wallet_def(kind, cfg, body, P0, spec)
    if sc == "thin": q0, b0 = q0 / 6, b0 / 6
    seen = {"minq": 1e18, "minb": 1e18}
    if os.environ.get("ENG_LOG"):
        _mk = m._bt_tmp.mkdtemp; FD = {}
        m._bt_tmp.mkdtemp = lambda *a, **k: FD.__setitem__("f", _mk(*a, **k)) or FD["f"]
        _rm = m.shutil.rmtree
        def _keep(p, *a, **k):
            if FD.get("f") and os.path.abspath(p) == os.path.abspath(FD["f"]):
                for root, _, names in os.walk(p):
                    for nm in names:
                        if nm.startswith("trade_history") or nm.startswith("log_"):
                            try:
                                t = open(os.path.join(root, nm), encoding="utf-8", errors="replace").read()
                                sys.stderr.write(f"--- {nm} ({len(t)})\n" + t[-int(os.environ["ENG_LOG"]):] + "\n")
                            except Exception: pass
            return _rm(p, *a, **k)
        m.shutil.rmtree = _keep
        sys.stderr.write("CFG " + json.dumps(cfg, ensure_ascii=False)[:600] + f" wallet {q0} {b0}\n")
    r = m._bt_run(kind, cfg, SYM, px, DT, q0, b0, spec, samples=3000)
    ex = r["ex"]
    for c in r["curve"]:
        seen["minq"] = min(seen["minq"], c[2]); seen["minb"] = min(seen["minb"], c[3])
    live = [o for o in ex.orders.values() if o.get("state") == "live"]
    from collections import Counter
    dup = {k: v for k, v in Counter((o["side"], round(o["px"], 6)) for o in live).items() if v > 1}
    rej = Counter(sc_ for _, sc_ in ex.rejects)
    qe, be, pe = ex.bal[ex.quote], ex.bal[ex.base], ex.p
    if os.environ.get("ENG_FILLS"):
        cc = Counter((f[1], round(f[3], 8)) for f in ex.fills)
        sys.stderr.write("FILLS " + str(cc.most_common(14)) + "\n")
    st = r.get("state") or {}
    bad = [k for k, v in st.items() if isinstance(v, float) and not math.isfinite(v)]
    print(json.dumps({"kind": kind, "sc": sc, "ri": ri, "why": r["why"], "end": [r["i_end"], r["n"]], "secs": r["secs"], "fills": len(ex.fills),
                      "buys": sum(1 for f in ex.fills if f[1] == "buy"), "sells": sum(1 for f in ex.fills if f[1] == "sell"),
                      "q0": q0, "b0": b0, "qe": round(qe, 6), "be": round(be, 8), "pe": pe, "minq": round(seen["minq"], 6), "minb": round(seen["minb"], 8),
                      "frz": [round(ex.frz[ex.quote], 6), round(ex.frz[ex.base], 8)],
                      "dE_usd": round((qe - q0) + (be - b0) * pe, 6), "dE_coin": round((be - b0) + (qe - q0) / pe, 8), "dbase": round(be - b0, 8),
                      "pkey": r["pkey"], "realized": round(r["realized"], 8), "curve_profit": r["curve"][-1][4], "rnf": r.get("rnf"),
                      "rej": dict(rej), "dup_live": {f"{k[0]}@{k[1]}": v for k, v in dup.items()}, "live": len(live), "nan": bad, "A": round(A, 4),
                      "fees": [round(ex.fees[ex.quote], 6), round(ex.fees[ex.base], 8)],
                      "usd_fill": [round(min(f[2] * f[3] for f in ex.fills), 4), round(max(f[2] * f[3] for f in ex.fills), 4)] if ex.fills else None}, ensure_ascii=False))
    shutil.rmtree(R, ignore_errors=True); sys.exit(0)
Q = "-q" in sys.argv
DASH_ARG = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1100]}"), flush=True)


BTC = {"ENG_F": "800", "ENG_SPEC": '{"tickSz": 0.1, "lotSz": 1e-08, "minSz": 1e-05}'}
ETH = {"ENG_F": "37.5", "ENG_SPEC": '{"tickSz": 0.05, "lotSz": 1e-06, "minSz": 0.0001}'}
JOBS = [("all", k, s, {}) for k in BODY for s in ("osc", "crash")] \
     + [("btc", k, s, BTC) for k in ("grid", "grid_plus", "grid_range") for s in ("osc", "gaps")] \
     + [("eth", k, "osc", ETH) for k in ("grid", "grid_plus", "grid_range")] \
     + [("rest", k, "thin", {"ENG_DT": "5"}) for k in ("dca", "dca_buy")]


def run(j):
    tag, k, s, e = j
    env = {x: v for x, v in os.environ.items() if x != "TMPDIR"}
    env.update(e); env["ENG_CHILD"] = "1"
    if DASH_ARG:
        env["ENG_DASH"] = os.path.abspath(DASH_ARG)
    try:
        p = subprocess.run([sys.executable, os.path.abspath(__file__), k, s], capture_output=True, text=True, timeout=1500, cwd=tempfile.gettempdir(), env=env)
        r = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as x:
        r = {"err": repr(x)[:300]}
    r.update(tag=tag, kind=r.get("kind", k), sc=r.get("sc", s))
    return r


from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(3) as tp:
    RS = list(tp.map(run, JOBS))
bad = [r for r in RS if "err" in r]
ok(f"every case ran ({len(RS)} engine runs)", not bad, bad[:2])
RS = [r for r in RS if "err" not in r]
A = [r for r in RS if r["tag"] == "all"]
ok("① the 9 kinds × (oscillation · crash-and-back): each reaches the end of its path", all(r["why"] == "end" and r["end"][0] >= r["end"][1] - 1 for r in A), [(r["kind"], r["sc"], r["why"]) for r in A if r["why"] != "end"])
ok("① … no balance below zero · no broken number in the state", all(r["minq"] > -1e-6 and r["minb"] > -1e-9 and not r["nan"] for r in A), [(r["kind"], r["sc"], r["minq"], r["minb"], r["nan"]) for r in A][:4])
ok("① … no order refused for anything but balance", all(set(r["rej"]) <= {"51008"} for r in RS), [(r["tag"], r["kind"], r["sc"], r["rej"]) for r in RS if not set(r["rej"]) <= {"51008"}])
G = [r for r in A if r["kind"] in ("grid", "grid_plus", "grid_range", "grid_step", "dca_buy") and r["sc"] == "osc"]
def gap(r):          # what the engine says it earned (gross — fees apart for the grid family) against what the wallet gained
    fees = r["fees"][0] + r["fees"][1] * r["pe"]
    said = r["realized"] - (fees if r["kind"] in ("grid", "grid_plus", "grid_range") else 0.0)
    return abs(r["dE_usd"] - said), abs(r["dbase"]) * r["pe"] * r["A"] + 0.02 * max(1.0, abs(said)) + 0.05
ok("① … the grid family and the buy DCA on the oscillation: the profit in the bot's own book = what the wallet gained (after fees · within what the coins still held can explain)",
   len(G) == 5 and all(gap(r)[0] <= gap(r)[1] for r in G), [(r["kind"], r["dE_usd"], r["realized"], gap(r)) for r in G])
B = [r for r in RS if r["tag"] in ("btc", "eth")]
ok(f"② ♾️ ➕ 🎚️ on a 64,000$ coin and a 3,000$ coin with a 10$ order: they trade ({min((r['fills'] for r in B), default=0)}–{max((r['fills'] for r in B), default=0)} trades each — it was none)",
   len(B) == 9 and all(r["fills"] >= 100 for r in B), [(r["tag"], r["kind"], r["sc"], r["fills"]) for r in B])
ok("② … every order is ≈ 10$ (9–11.5$ — on a 3,000$ coin it was 0.01 coin = 30$ or nothing) · no «Parameter px error» (the 0.1 price step)",
   all(r["usd_fill"] and 9.0 <= r["usd_fill"][0] and (r["sc"] != "osc" or r["usd_fill"][1] <= 11.5) and "51000" not in r["rej"] for r in B), [(r["tag"], r["kind"], r["usd_fill"], r["rej"]) for r in B])   # (a jump over several levels is one joined order, by design ⇒ the upper bound on the oscillation only)
S_ = [r for r in A if r["kind"] in ("grid", "grid_plus", "grid_range") and r["sc"] == "osc"]
ok("② … and SOL trades as before (the same number of trades · each order ≈ 10$)", all(r["fills"] >= 300 and 9.0 <= r["usd_fill"][0] and r["usd_fill"][1] <= 11.5 for r in S_), [(r["kind"], r["fills"], r["usd_fill"]) for r in S_])
D = [r for r in RS if r["tag"] == "rest"]
ok(f"③ DCA short of balance, the loop every 5 seconds: refused orders {[r['rej'].get('51008', 0) for r in D]} in {D[0]['end'][1] if D else 0} loops — at most one every 20 s (it was one every loop)",
   len(D) == 2 and all(1 <= r["rej"].get("51008", 0) <= r["end"][1] // 4 + 5 for r in D) and all(r["fills"] >= 3 for r in D), [(r["kind"], r["rej"], r["end"], r["fills"]) for r in D])
print(f"✅ t_eng_audit: {sum(res)}/{len(res)}" if all(res) else f"❌ t_eng_audit: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
