# ♻️ v3.36.65 — a deleted bot comes back through its own deploy form (p111). The owner (20-11): «اريد عند مسح بوت اقدر ارجعه يعني انسخ
#   اعداداته ويبدي من جديد واقدر اعدل عليه قبل ما انشره ، يعني حولني تلقائيا وكانما نشر البوت».
#   A closed folder (devtests/seed_cards.py: ♾️ 💠 · ➕ · 🎚️ · 🪜 · 📉 · 📈 · 🔁 · 🔂 · 💹) + more deployed here with the dashboard's own deploy
#   functions and settings off their defaults (♾️ ⚔️ 💠50% · ⚡ DCA+ sell with 🛡️ trail · ⚡ DCA+ buy · 🔁 lots with range/time/💠 · 💹 price
#   trigger + ♾️×💹 guard) + a 🧪 demo · launches faked · no network. In a real browser (ui_redeploy.js) every bot is deleted from the page
#   (🗑 — the server's own delete), the offer comes, the form opens filled, «🚀 انشر وشغّل» is pressed.
#   Here, after: every new bot's settings == the deleted one's, key by key (only its new id · 🪜 its start price = the market now)
#   python3 devtests/ui_redeploy.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
import seed_cards                                             # noqa: E402

res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


LAUNCH = r'''
import os, sys, time, threading, urllib.request, importlib.machinery, importlib.util
import requests
R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
def _no_net(*a, **k):
    raise OSError("devtests: no network")
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_rd_ui", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_rd_ui", ld))
sys.argv = ["x"]
ld.exec_module(m)
PX = __PX__
def _pub(p):
    if "instruments" in p:
        return {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.0001"}]}
    for s, v in PX.items():
        if s in p and "ticker" in p:
            return {"code": "0", "data": [{"last": str(v)}]}
    return None
m._okx_pub = _pub
m._okx_get = lambda *a, **k: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("devtests: the dashboard must not send orders"))
m.tg_send = lambda *a, **k: True
m.launch = lambda b: (True, "test")
m.stop_bot = lambda *a, **k: True
m.is_alive = lambda d, sp: (False, "")
m._acc_price = lambda s: PX.get(s, 0)
m.PX.update(PX)
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
'''


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_rd_")
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
PX = {"XRP-USDT": 2.4512, "SOL-USDT": 182.37, "ADA-USDT": 0.7421, "TRX-USDT": 0.2513, "DOGE-USDT": 0.1834, "LINK-USDT": 17.46,
      "XLM-USDT": 0.4127, "DOT-USDT": 5.214, "SUI-USDT": 3.618, "AVAX-USDT": 31.25, "ETH-USDT": 2010.5, "BTC-USDT": 91234.5,
      "OP-USDT": 1.912, "NEAR-USDT": 4.567}
d = None
rc = 1
try:
    seed_cards.seed(R, DASH)
    # more bots, settings off their defaults — deployed by the dashboard's own functions (in this process: launches faked · no network)
    import requests, urllib.request
    _nn = lambda *a, **k: (_ for _ in ()).throw(OSError("devtests: no network"))
    requests.get = requests.post = requests.request = _nn
    requests.Session.request = lambda self, *a, **k: _nn()
    urllib.request.urlopen = _nn
    cwd0 = os.getcwd()
    os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_rd_seed", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_rd_seed", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.ROOT = R
    m.tg_send = lambda *a, **k: True
    m.launch = lambda b: (True, "")
    m._okx_get = lambda *a, **k: None
    m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.0001"}]} if "instruments" in p else None)
    m._acc_price = lambda s: PX.get(s, 0)
    m.PX.update(PX)
    W = {"wallet": "main"}
    EXTRA = [
        ("deploy", dict(W, symbol="AVAX-USDT", grid_pct="1.25", usd_value="22", min_price="20", forced_base="0", g_type="grid", guard=True,
                        reinvest=True, reinvest_pct="50")),
        ("deploy_dca", dict(W, symbol="ETH-USDT", dca_type="dca_plus", exchange_orders="2", cycle_wait_sec="45", trail_on=True, trail_pct="0.6",
                            plus_rows=json.dumps([{"d": 0, "q": 0.01, "x": 0.8}, {"d": 1.2, "q": 0.015, "x": 0.7}, {"d": 2.5, "q": 0.03, "x": 0.5},
                                                  {"d": 4, "q": 0.05, "x": 0.4}]))),
        ("deploy_dca", dict(W, symbol="BTC-USDT", dca_type="dca_plus_buy", exchange_orders="3", cycle_wait_sec="60",
                            plus_rows=json.dumps([{"d": 0, "q": 0.0002, "x": 0.9}, {"d": 1.5, "q": 0.0003, "x": 0.6}, {"d": 3, "q": 0.0005, "x": 0.45}]))),
        ("deploy_rec", dict(W, symbol="OP-USDT", rec_type="rec_buy", mode="lots", amount="7", every="3", unit="d", at="21:15", tp_pct="2.5",
                            cap="140", ri_pct="40", lo="1.2", hi="3.4", start_now=False)),
        ("deploy_va", dict(W, symbol="NEAR-USDT", va_mode="grow", trigger="price", drop_pct="3", rise_pct="4.5", start_usd="20", step_usd="5",
                           band_pct="4", max_order="30", cap="400", brake_pct="25", floor_on=False, start_now=True, guard_on=True, hg_pct="1.5",
                           hg_usd="12", hg_ri=True, hg_ri_pct="60", hg_wallet=True, first_src="buy")),
    ]
    for fn, body in EXTRA:
        r = getattr(m, fn)(dict(body))
        if not r.get("ok"):
            raise SystemExit(f"❌ seed extra: {fn} {body['symbol']}: {r.get('msg')}")
    os.chdir(cwd0)
    # a 🧪 demo (the plus bot's folder as a demo, with its paper wallet's start)
    src = next(os.path.join(R, n) for n in os.listdir(R) if os.path.exists(os.path.join(R, n, "config_SOL-USDT.json")))
    dd = os.path.join(R, "demo_sol_t1")
    shutil.copytree(src, dd)
    cp = os.path.join(dd, "config_SOL-USDT.json")
    c = json.load(open(cp, encoding="utf-8"))
    c.update(is_demo=True, api_key="", secret_key="", passphrase="", auto_restart=False)
    json.dump(c, open(cp, "w", encoding="utf-8"))
    json.dump({"v": 1, "sym": "SOL-USDT", "bal": {"USDT": 400.0, "SOL": 3.0}, "frz": {}, "start": {"USDT": 432.5, "SOL": 2.75}, "orders": {},
               "by_cl": {}, "fills": [], "px": 182.37}, open(os.path.join(dd, "demo_wallet.json"), "w"))
    # the settings before (every bot)
    ORIG = {}
    for n in os.listdir(R):
        p = os.path.join(R, n)
        cf = [f for f in os.listdir(p) if f.startswith("config_") and f.endswith(".json")] if os.path.isdir(p) and n != "_archive" else []
        if cf:
            ORIG[n] = json.load(open(os.path.join(p, cf[0]), encoding="utf-8"))
    P1 = port()
    open(os.path.join(R, "_l.py"), "w").write(LAUNCH.replace("__PX__", repr(PX)))
    d = subprocess.Popen([sys.executable, os.path.join(R, "_l.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    OUT = os.path.join(R, "_js.json")
    r = subprocess.run(["node", os.path.join(H, "ui_redeploy.js"), f"http://127.0.0.1:{P1}/", OUT] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=1500, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:], flush=True)
    js_ok = r.returncode == 0
    J = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    # after: every new bot vs the deleted one
    NEW = {}
    for n in os.listdir(R):
        p = os.path.join(R, n)
        if n in ORIG or n.startswith("_") or not os.path.isdir(p):
            continue
        cf = [f for f in os.listdir(p) if f.startswith("config_") and f.endswith(".json")]
        if cf:
            NEW[n] = json.load(open(os.path.join(p, cf[0]), encoding="utf-8"))
    arch = sorted(os.listdir(os.path.join(R, "_archive"))) if os.path.isdir(os.path.join(R, "_archive")) else []
    real = {n: c for n, c in ORIG.items() if not c.get("is_demo")}
    ok(f"every real bot was deleted to 🗄️ the archive ({len(arch)} folders) · and deployed again from its filled form ({len(NEW)} new folders)",
       len(arch) == len(ORIG) and len(NEW) == len(real) and not [n for n in ORIG if os.path.isdir(os.path.join(R, n))], (arch, sorted(NEW)))
    SKIP = {"bot_id"}
    by = {(c.get("symbol"), c.get("bot_type")): (n, c) for n, c in NEW.items()}
    for n, c0 in sorted(real.items(), key=lambda x: x[1].get("symbol")):
        k = (c0.get("symbol"), c0.get("bot_type"))
        n1, c1 = by.get(k, (None, {}))
        skip = SKIP | ({"forced_base_price"} if c0.get("bot_type") == "grid_step" else set())
        diff = {kk: (c0.get(kk), c1.get(kk)) for kk in (set(c0) | set(c1)) - skip if c0.get(kk) != c1.get(kk)}
        extra = ""
        if c0.get("bot_type") == "grid_step":
            extra = f" · 🪜 start price: the market now {c1.get('forced_base_price')} (was {c0.get('forced_base_price')})"
            diff.update({} if float(c1.get("forced_base_price") or 0) == PX[c0["symbol"]] else {"forced_base_price": (c0.get("forced_base_price"), c1.get("forced_base_price"))})
        tag = ("⚡ DCA+ " + ("buy" if c0.get("bot_type") == "dca_buy" else "sell")) if c0.get("dca_plus") else c0.get("bot_type")
        ok(f"{c0.get('symbol')} {tag}: the new bot's settings == the deleted one's, key by key ({len(c0)} keys · a new folder {n1}){extra}",
           n1 and n1 != n and not diff, diff)
    ok("the 🧪 demo: its form opened as a demo with its starting balances (432.5$ · 2.75 SOL) · not deployed by the test (the demo needs live prices)",
       (J.get("demo") or {}).get("ok"), J.get("demo"))
    ok("the browser part", js_ok)
    rc = 0 if res and all(res) else 1
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_redeploy: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_redeploy: {sum(res)}/{len(res)}")
sys.exit(rc)
