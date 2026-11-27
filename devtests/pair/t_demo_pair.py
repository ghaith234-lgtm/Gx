# 🔀 «شبكة عملتين» — the DEMO end to end (p153): python3 devtests/pair/t_demo_pair.py [Holy_Dashboard.pyw]
#   The dashboard deploys a demo (the real calculator) ⇒ the REAL engine starts on the two-leg paper exchange (a local price file instead
#   of OKX · no network · no keys) ⇒ SOL falls 2.5% against XRP ⇒ it buys (XRP → USDT → SOL) ⇒ SOL comes back ⇒ it sells with a profit in
#   XRP ⇒ the paper wallet = the engine's books (to the dust) ⇒ the card's data · out of the coin books · one demo per pair · the delete:
#   the engine withdraws by itself and the folder goes to the archive. The single-coin demo runner is untouched.
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def _no_net(*a, **k):
    raise OSError("no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="pairdemo_")
FEED = os.path.join(R, "_feed.json")
os.environ["HOLY_DEMO_FEED"] = FEED
SPEC = {"XRP-USDT": {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 1.0}, "SOL-USDT": {"tickSz": 0.01, "lotSz": 0.000001, "minSz": 0.01}}


def feed(sol, xrp=2.0):
    json.dump({"XRP-USDT": dict(SPEC["XRP-USDT"], last=xrp), "SOL-USDT": dict(SPEC["SOL-USDT"], last=sol)}, open(FEED + ".tmp", "w"))
    os.replace(FEED + ".tmp", FEED)


feed(150.0)
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pair_demo", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pair_demo", ld))
a0 = sys.argv
sys.argv = ["x"]
ld.exec_module(m)
sys.argv = a0
m.tg_send = lambda *a, **k: True
m._acc_price = lambda s: {"XRP-USDT": 2.0, "SOL-USDT": 150.0}.get(s, 0)
m._acc_spec = lambda s: dict(SPEC.get(s) or {})
RES = []


def ok(name, cond, det=""):
    RES.append(bool(cond))
    print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


def wait(fn, t=60):
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            v = fn()
            if v:
                return v
        except Exception:
            pass
        time.sleep(0.5)
    return None


ok("the single-coin demo runner is untouched (no pair code in it) · the pair runner has the two-leg exchange",
   "_PairPaper" not in m.demo_runner_src() and "_PairPaper" in m.demo_runner_src(True) and "class _BtEx" in m.demo_runner_src(True))
b = None
try:
    base = {"demo": True, "main": "XRP", "other": "SOL", "step_pct": 2, "main_value": 20, "main_amount": 200, "other_amount": 1, "auto": False}
    r = m.deploy_pair(dict(base))
    ok("🧪 the demo deploys without any OKX wallet (the real calculator · the real engine launched)", r.get("ok") and "ديمو" in r.get("msg", ""), r)
    b = next((x for x in m.bot_dirs().values() if x["cfg"].get("bot_type") == "grid_pair" and x["cfg"].get("is_demo")), None)
    c = (b or {}).get("cfg") or {}
    ok("🧪 its config: no keys · is_demo · 10 below · 3 above · the ratio 75 fixed", b and not c.get("api_key") and c.get("is_demo") and c.get("down_levels") == 10
       and c.get("up_levels") == 3 and abs(float(c.get("forced_base_ratio") or 0) - 75) < 1e-12, c)
    sp = m.paths_of(b)[0]
    wp = os.path.join(b["dir"], m.DEMO_WALLET)
    st = lambda: m.load_json(sp) or {}
    w = lambda: m.load_json(wp) or {}
    born = wait(lambda: (st().get("slots") and st().get("pair")) and st(), 90)
    log_ = lambda: open(m.paths_of(b)[2], encoding="utf-8", errors="ignore").read()[-1500:] if os.path.exists(m.paths_of(b)[2]) else ""
    ok("🧪 the engine is born on the paper exchange (11 levels)", born and len(born.get("slots") or {}) == 13, (log_(), (born or {}).get("slots")))
    ok("🧪 the paper wallet = the two amounts (200 XRP · 1 SOL · 0 USDT)", abs(float((w().get("bal") or {}).get("XRP") or 0) - 200) < 1e-9
       and abs(float((w().get("bal") or {}).get("SOL") or 0) - 1) < 1e-12, w().get("bal"))
    r2 = m.deploy_pair(dict(base))
    ok("🧪 one demo per pair", not r2.get("ok") and "واحد لكل زوج" in r2.get("msg", ""), r2)
    feed(146.0)                                                     # 1 SOL = 73 XRP < the first buy level 73.53
    got_buy = wait(lambda: any(s.get("kind") == "buy" for s in (st().get("swaps") or [])) and not st().get("op"), 60)
    ok("🟢 SOL falls against XRP ⇒ it buys through the dollar (XRP → USDT → SOL) on the paper exchange", got_buy, (log_(), st().get("swaps")))
    feed(151.0)                                                     # 75.5 ≥ the sell 75
    got_sell = wait(lambda: any(s.get("kind") == "sell" for s in (st().get("swaps") or [])) and not st().get("op") and st(), 60)
    tp = float((got_sell or {}).get("total_profit") or 0)
    # it swaps at the ratio it can execute (it bought at 73, below its 73.53 level · sold at 75.5, above its 75): the paper exchange's spread
    # (0.03% each side) and the four taker fees (0.1% each) ⇒ 20 XRP × (75.5·0.9997² / (73·1.0003²) × 0.999⁴ − 1)
    #   (the prices on the exchange's ticks: SOL ask 146.05 · XRP bid 1.9994 · SOL bid 150.95 · XRP ask 2.0006) · the cents of dollar the last
    #   leg could not spend stay with the bot as dust (usd_booked — swept into its next sale), so profit + dust = the whole cycle
    want = 20 * ((150.95 / 2.0006) / (146.05 / 1.9994) * 0.999 ** 4 - 1)
    dust = float((got_sell or {}).get("usd_booked") or 0) / 2.0006
    ok(f"🔴 SOL comes back ⇒ it sells with a profit in XRP after the four fees and the spread (≈ {want:.4f} XRP with its dust)",
       got_sell and 0 < tp < want and abs(tp + dust - want) < 0.003 * want, (tp, dust, want, log_()))
    time.sleep(2.5)                                                 # the paper wallet saves every second
    S, W = st(), w()
    bal = W.get("bal") or {}
    on = float(S.get("other_book") or 0)
    ok("⚖️ the paper wallet = the engine's books: XRP = main_book · SOL = other_book + the SOL left outside · USDT = the dust it keeps",
       abs(float(bal.get("XRP") or 0) - float(S.get("main_book") or 0)) < 1e-6 and abs(float(bal.get("SOL") or 0) - on - (1 - float(born.get("other_start") or 0))) < 1e-9
       and abs(float(bal.get("USDT") or 0) - float(S.get("usd_booked") or 0)) < 1e-6, (bal, {k: S.get(k) for k in ("main_book", "other_book", "usd_booked", "other_start")}))
    ok("⚖️ … and the two legs are real orders on the paper exchange (IOC · by its own ids)", len((W.get("orders") or {}).get("SOL-USDT") or {}) >= 2
       and len((W.get("orders") or {}).get("XRP-USDT") or {}) >= 2, {k: len(v) for k, v in (W.get("orders") or {}).items()})
    sn = m.bot_snapshot(b)
    P = sn.get("pair") or {}
    ok("🃏 the card's data: demo · profit in XRP · the sale counted", sn.get("demo") and abs(float(P.get("profit") or 0) - tp) < 1e-9 and P.get("sales") == 1, (sn.get("demo"), P.get("profit"), P.get("sales")))
    m.coin_ledger_tick()
    cl = m.load_json(m.COIN_LEDGER) or {}
    ok("📒 outside every total: the coin books do not book the demo", not float((cl.get("total_pair") or {}).get("XRP") or 0), cl.get("total_pair"))
    r3 = m.delete_purge(b)
    gone = wait(lambda: not os.path.isdir(b["dir"]), 30)
    ok("🗑 the delete: the engine withdraws by itself, the folder goes to the archive", r3.get("ok") and gone, r3)
finally:
    try:
        for d_, p_ in list(m.PROCS.items()):
            if p_.poll() is None:
                p_.kill()
    except Exception:
        pass
    try:
        if b:
            m.kill_bot_pids(b["dir"])
    except Exception:
        pass
print(f"\n{'✅' if all(RES) else '❌'} t_demo_pair: {sum(RES)}/{len(RES)}")
os.chdir("/")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(RES) else 1)
