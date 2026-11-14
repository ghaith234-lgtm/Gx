# 🧪 the demo bot on the REAL engine (v3.36.46 · p75) — the owner (14-11): «اريد اسوي نشر demo بنفس المحركات … كل بوت وكرته وينكتب عليه
#   ديمو» · «البوت الديمو يتحدث مع المحرك يعني هو نفسه». A closed folder · the price from a local file (HOLY_DEMO_FEED — no network) ·
#   the dashboard's own deploy_demo() and launch(); a real process runs the bot:
#   · the settings are the real deploy's own (the deploy function in a separate process · no keys anywhere) · the folder holds the
#     very engine a real bot of that kind runs (byte for byte) + holy_demo.py + the paper wallet with the chosen balances
#   · the bot trades on the paper exchange: its ladder appears as orders in the paper wallet · the price moves (the file) ⇒ orders
#     fill there and the engine books them (its own state) · the paper wallet stays whole (coins and dollars add up with the fills)
#   · the card reads the paper wallet (free dollars · coins · open orders) · nothing is sent anywhere (no OKX private call)
#   · stop and start again: the paper wallet survives (the same orders, the same balances)
#   python3 devtests/t_demo.py [Holy_Dashboard.pyw] [-q] [--kind=grid_plus|grid|grid_range|grid_step|dca|dca_buy|rec_buy|rec_sell|rec_va] [--ri]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
KIND = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--kind=")), "grid_plus")
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="t_demo_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_demo", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_demo", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.ROOT = R
SYM, P0 = "SOL-USDT", 80.0
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
m._bt_spec = lambda s: dict(SPEC)
m._acc_price = lambda s: P0
m.PX[SYM] = P0
TG = []
m.tg_send = lambda t, *a, **k: TG.append(t) or True
m._okx_get = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the demo called OKX's private side"))
FEED = os.path.join(R, "feed.json")


def feed(p):
    json.dump(dict(SPEC, last=p), open(FEED + ".tmp", "w"))
    os.replace(FEED + ".tmp", FEED)


feed(P0)
os.environ["HOLY_DEMO_FEED"] = FEED
BODY = {"grid_plus": {"symbol": SYM, "g_type": "grid_plus", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0", "buy_offset": "1.2"},
        "grid": {"symbol": SYM, "g_type": "grid", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0"},
        "grid_range": {"symbol": SYM, "g_type": "grid_range", "grid_pct": "0.6", "usd_value": "10", "min_price": "50", "forced_base": "0",
                       "lower_price": "70", "upper_price": "90"},
        "grid_step": {"symbol": SYM, "usd_value": "30", "step_parts": "3", "step_sell_pct": "0.8", "grid_pct": "1.5", "min_price": "50", "up_groups": "2"},
        "dca": {"symbol": SYM, "base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2",
                "size_multiplier": "1.2", "max_safety_orders": "5", "take_profit_pct": "0.6", "dca_type": "dca"},
        "dca_buy": {"symbol": SYM, "base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2",
                    "size_multiplier": "1.2", "max_safety_orders": "5", "take_profit_pct": "0.6", "dca_type": "dca_buy"},
        "rec_buy": {"symbol": SYM, "rec_type": "rec_buy", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6",
                    "cap": "300", "lo": "60", "hi": "120"},
        "rec_sell": {"symbol": SYM, "rec_type": "rec_sell", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6", "cap": "300"},
        "rec_va": {"symbol": SYM, "start_usd": "20", "va_mode": "fixed", "every": "1", "unit": "h", "band_pct": "2", "max_order": "20", "cap": "300"}}[KIND]
GRID = KIND in ("grid", "grid_plus", "grid_range", "grid_step")
RI = "--ri" in sys.argv                                  # 💠 reinvest on (the grid family runs through reinvest.py — the runner imports the engine for it)
if RI:
    BODY.update(reinvest=True, reinvest_pct="100")
r = m.deploy_demo(KIND, dict(BODY, demo=True, demo_usd="400", demo_coin="3", auto=False))
ok(f"🧪 deploy_demo({KIND}) answered ok — «{str(r.get('msg'))[:90]}»", r.get("ok") and r.get("dir"), r)
D = os.path.join(R, r.get("dir") or "x")
cfgp = os.path.join(D, f"config_{SYM}.json")
cfg = json.load(open(cfgp, encoding="utf-8")) if os.path.exists(cfgp) else {}
ok("the settings are a demo's: is_demo · the kind asked · no keys anywhere", cfg.get("is_demo") is True and cfg.get("bot_type") == KIND
   and not any(cfg.get(k) for k in ("api_key", "secret_key", "passphrase")), {k: cfg.get(k) for k in ("is_demo", "bot_type", "api_key")})
eng_src, eng_script, _ = m.engine_for(cfg)
ok(f"the folder holds the very engine a real {KIND} bot runs ({eng_script} · byte for byte) + the demo runner + the paper wallet",
   os.path.exists(os.path.join(D, eng_script)) and open(os.path.join(D, eng_script), encoding="utf-8").read() == eng_src
   and os.path.exists(os.path.join(D, m.DEMO_RUNNER)) and os.path.exists(os.path.join(D, m.DEMO_WALLET)), os.listdir(D) if os.path.isdir(D) else None)
WP = os.path.join(D, m.DEMO_WALLET)


def wallet():
    for _ in range(20):
        try:
            return json.load(open(WP, encoding="utf-8"))
        except Exception:
            time.sleep(0.1)
    return {}


def state():
    try:
        return json.load(open(m.paths_of({"dir": D, "symbol": SYM, "cfg": cfg})[0], encoding="utf-8"))
    except Exception:
        return {}


def wait(cond, sec=60):
    t = time.time()
    while time.time() - t < sec:
        if cond():
            return True
        time.sleep(0.5)
    return False


w0 = wallet()
ok("the paper wallet starts with the chosen balances (400 USDT · 3 SOL — kept as its «start»)", (w0.get("start") or {}).get("USDT") == 400 and (w0.get("start") or {}).get("SOL") == 3, w0.get("start"))
live = lambda: [o for o in (wallet().get("orders") or {}).values() if o.get("state") == "live"]
anyo = lambda: list((wallet().get("orders") or {}).values())
if GRID:
    ok("the real engine laid its ladder on the paper exchange (live buy and sell orders in the paper wallet)",
       wait(lambda: any(o["side"] == "buy" for o in live()) and any(o["side"] == "sell" for o in live()), 90), (len(live()), open(os.path.join(D, "log_main.txt"), encoding="utf-8", errors="ignore").read()[-800:]))
else:
    ok("the real engine traded on the paper exchange (its first order is in the paper wallet — live or filled)",
       wait(lambda: len(anyo()) >= 1, 90), open(os.path.join(D, "log_main.txt"), encoding="utf-8", errors="ignore").read()[-900:])
b = {"dir": D, "symbol": SYM, "cfg": cfg}
m._demo_bal(b)
ent = m.BAL.get(D) or {}
nb, ns = sum(1 for o in live() if o["side"] == "buy"), sum(1 for o in live() if o["side"] == "sell")
wn = wallet()
ok(f"the card reads the paper wallet: free dollars {ent.get('usdt')} · coins {ent.get('base_eq')} · open orders {ent.get('ob')} buy / {ent.get('os')} sell",
   ent.get("demo") and ent.get("ob") == nb and ent.get("os") == ns
   and abs(float(ent.get("usdt") or 0) - round(wn["bal"]["USDT"] - (wn.get("frz") or {}).get("USDT", 0), 2)) < 0.02, ent)
if GRID:
    top_buy = max(float(o["px"]) for o in live() if o["side"] == "buy")
    feed(round(top_buy * 0.995, 2))                   # the price falls through the top buy
    ok("the price falls (the feed) ⇒ the top buy fills on the paper exchange and the engine books it", wait(lambda: any(f[1] == "buy" for f in (wallet().get("fills") or [])), 60)
       and wait(lambda: "شراء" in json.dumps(json.load(open(os.path.join(D, "trade_history_SOL.json"), encoding="utf-8")) if os.path.exists(os.path.join(D, "trade_history_SOL.json")) else [], ensure_ascii=False), 60),
       (wallet().get("fills"), open(os.path.join(D, "log_main.txt"), encoding="utf-8", errors="ignore").read()[-600:]))
else:
    feed(round(P0 * 0.98, 2))                         # the price moves — whatever the engine does, the paper wallet must add up
    time.sleep(6)
w1 = wallet()
fills = w1.get("fills") or []
b_in = sum(f[3] - f[4] for f in fills if f[1] == "buy") - sum(f[3] for f in fills if f[1] == "sell")   # (fill: t · side · px · qty · fee · maker)
q_out = sum(f[2] * f[3] for f in fills if f[1] == "buy") - sum(f[2] * f[3] - f[4] for f in fills if f[1] == "sell")
ok(f"the paper wallet stays whole: coins = 3 + bought − sold ({w1['bal']['SOL']:.6f}) · dollars = 400 − spent + received ({w1['bal']['USDT']:.4f})",
   abs(w1["bal"]["SOL"] - (3 + b_in)) < 1e-9 and abs(w1["bal"]["USDT"] - (400 - q_out)) < 1e-6, (w1["bal"], b_in, q_out))
n_live = len(live())
ok("stop ⇒ the process ends", m.stop_bot(b) is not None and wait(lambda: not m.bot_pids(D, ttl=0), 30), m.bot_pids(D, ttl=0))
wb = wallet()
ok2, msg2 = m.launch(b)
time.sleep(4)
ok("start again ⇒ the same paper wallet (balances and open orders kept — not reset)", ok2 and m.bot_pids(D, ttl=0)
   and (not GRID or wait(lambda: len(live()) >= 1, 30))
   and abs(wallet()["bal"]["USDT"] - wb["bal"]["USDT"]) < 1e-6 and abs(wallet()["bal"]["SOL"] - wb["bal"]["SOL"]) < 1e-9, (msg2, wb.get("bal"), wallet().get("bal")))
ok("nothing went to Telegram (the demo is kept apart)", not TG, TG[:2])
m.stop_bot(b)
wait(lambda: not m.bot_pids(D, ttl=0), 30)
for p in list(m.PROCS.values()):
    try:
        p.kill()
    except Exception:
        pass
if RI and KIND != "grid_step":
    ok("💠 reinvest: the bot ran through reinvest.py with the real engine imported (the runner's «main»)", cfg.get("reinvest") is True
       and os.path.exists(os.path.join(D, "reinvest.py")) and "reinvest.py" in open(os.path.join(D, "log_main.txt"), encoding="utf-8", errors="ignore").read()[:400],
       open(os.path.join(D, "log_main.txt"), encoding="utf-8", errors="ignore").read()[:400])
_nm = "t_demo" + ("" if KIND == "grid_plus" else f" --kind={KIND}") + (" --ri" if RI else "")
print(f"✅ {_nm}: {sum(res)}/{len(res)}" if all(res) else f"❌ {_nm}: {sum(res)}/{len(res)}")
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
