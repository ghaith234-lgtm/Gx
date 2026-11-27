# 🔀 شبكة عملتين — its CARD in a real browser (ui_pair_card.js): a LINK/XRP bot planted with the state its engine writes (a profit · the
#   levels · a swap in flight · today) — the card in the main coin · ⏸/▶️ by the ratio (the state file changes) · 🪜 the levels · ⚙ details ·
#   the four skins · the compact row · a phone width · no page error. A closed folder: no network, fake keys, no orders, launch stubbed.
#   python3 devtests/pair/ui_pair_card.py [Holy_Dashboard.pyw] [-q] [--shots DIR]        (run with `unset TMPDIR`)
import os, shutil, socket, subprocess, sys, tempfile, time
H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else ""
DASH = os.path.abspath(next((a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("-") and sys.argv[i - 1] != "--shots"),
                            os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
LAUNCH = r'''
import os, sys, json, time, urllib.request, importlib.machinery, importlib.util
import requests
R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
def _no_net(*a, **k):
    raise OSError("devtests: no network")
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pair_ui", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pair_ui", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_pub = lambda p: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
m.tg_send = lambda *a, **k: True
PXS = {"XRP-USDT": 2.0, "SOL-USDT": 150.0}
m._acc_price = lambda s: PXS.get(s, 0)
m._acc_spec = lambda s: {"XRP-USDT": {"lotSz": 0.000001, "minSz": 1.0}, "SOL-USDT": {"lotSz": 0.000001, "minSz": 0.01}}.get(s, {"lotSz": 1e-8, "minSz": 0.0})
m._okx_get = lambda path, *a, **k: {"code": "0", "data": [{"details": [{"ccy": c, "availBal": v} for c, v in (("XRP", "1000"), ("SOL", "5")) if ("ccy=" + c) in path]}]}
m.wallet_keys = lambda name: {"api_key": "FAKE-KEY", "secret_key": "FAKE-SECRET", "passphrase": "FAKE-PASS"}
def _launch(b, *a, **k):
    json.dump({"launched": b["symbol"]}, open(os.path.join(R, "_launched.json"), "w"))
    return True, "ok"
m.launch = _launch
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
'''


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_pairc_")


def plant(R):
    """a LINK/XRP bot as its engine leaves it: 6 levels below · 5 above · 3 sales · a swap in flight (1.25 USDT between the legs)"""
    import json
    d = os.path.join(R, "pair_link_ui")
    os.makedirs(d)
    now = time.time()
    json.dump({"api_key": "FAKE-KEY", "secret_key": "FAKE-SECRET", "passphrase": "FAKE-PASS", "symbol": "LINK-XRP", "bot_type": "grid_pair",
               "bridge": "USDT", "main_value": 20.0, "grid_percentage": 0.02, "down_levels": 6, "up_levels": 5, "profit_to": "main",
               "forced_base_ratio": 7.5, "fee_rate": 0.001, "is_demo": False, "auto_restart": True}, open(os.path.join(d, "config_LINK-XRP.json"), "w"))
    sl = {str(j): {"j": j, "bp": 7.5 * 1.02 ** j, "sp": 7.5 * 1.02 ** (j + 1), "side": "buy" if j < 0 else "sell",
                   "q": 0.0 if j < 0 else 20 / (7.5 * 1.02 ** j), "c": 0.0 if j < 0 else 20.0, "dq": 0.0, "n": 1 if j in (-1, -2, 0) else 0} for j in range(-6, 5)}
    sw = [{"t": now - 7200, "kind": "buy", "j": -1, "sold": 20.0, "got": 2.72, "profit": 0.0},
          {"t": now - 3600, "kind": "sell", "j": -1, "sold": 2.72, "got": 20.4, "profit": 0.4}]
    json.dump({"pair": {"other": "LINK", "main": "XRP", "bridge": "USDT", "r0": 7.5, "g": 0.02, "mv": 20.0, "dn": 6, "up": 5, "pt": "main",
                        "born": now - 3 * 86400},
               "slots": sl, "total_profit": 1.2, "profit_other": 0.0, "main_book": 100.0, "other_book": 3.0, "main_start": 120.0, "other_start": 13.2,
               "usd_booked": 1.25, "usd_dust": 0.0, "ratio": 7.52, "px_main": 2.0, "px_other": 15.04, "current_price": 15.04,
               "next_buy": {"j": -1, "ratio": 7.3529411765, "main": 20.0}, "next_sell": {"j": 0, "ratio": 7.65, "qty": 2.6666666667},
               "n_buy": 6, "n_sell": 5, "op": {"id": "HBui1", "k": "-1", "kind": "buy", "ts": now - 2}, "daily": {time.strftime("%Y-%m-%d"): 0.4},
               "swaps": sw, "last_trade": {"side": "sell", "ratio": 7.64, "qty": 2.72, "main": 20.4, "profit": 0.4, "ts": now - 3600, "n": 2}},
              open(os.path.join(d, "grid_state_LINK-XRP.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d, rc = None, 1
try:
    shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
    open(os.path.join(R, "_l.py"), "w").write(LAUNCH)
    plant(R)
    P1 = port()
    d = subprocess.Popen([sys.executable, os.path.join(R, "_l.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    t0 = time.time()
    while time.time() - t0 < 60:
        try:
            socket.create_connection(("127.0.0.1", P1), timeout=1).close()
            break
        except OSError:
            time.sleep(0.3)
    r = subprocess.run(["node", os.path.join(H, "ui_pair_card.js"), f"http://127.0.0.1:{P1}/", R, SHOTS or "-"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=600, env=env)
    print(r.stdout.strip())
    if r.returncode and r.stderr.strip():
        print(r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.terminate()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
