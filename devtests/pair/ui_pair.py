# 🔀 شبكة عملتين — the page in a real browser (ui_pair.js): the deploy button · the form · the calculator table (/api/pair_plan) · a refusal ·
#   the deploy (/api/deploy_pair — launch stubbed, no orders) · the 📖 guide · a phone width · no page error. A closed folder: no network,
#   fake keys, the two prices and OKX's minimums stubbed (XRP 2$ · SOL 150$ ⇒ 1 SOL = 75 XRP).
#   python3 devtests/pair/ui_pair.py [Holy_Dashboard.pyw] [-q] [--shots DIR]        (run with `unset TMPDIR`)
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


R = tempfile.mkdtemp(prefix="ui_pair_")
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d, rc = None, 1
try:
    shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
    open(os.path.join(R, "_l.py"), "w").write(LAUNCH)
    P1 = port()
    d = subprocess.Popen([sys.executable, os.path.join(R, "_l.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    t0 = time.time()
    while time.time() - t0 < 60:
        try:
            socket.create_connection(("127.0.0.1", P1), timeout=1).close()
            break
        except OSError:
            time.sleep(0.3)
    r = subprocess.run(["node", os.path.join(H, "ui_pair.js"), f"http://127.0.0.1:{P1}/", R, SHOTS or "-"] + (["-q"] if Q else []),
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
