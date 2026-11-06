# 🪜 📈 v3.36.16 in a real browser: the graded-grid deploy form — two fields (first sell · between sells) · the body sent ·
#   the plan table (the owner's example 1.010 · 1.015 · 1.020) · the refusal of a losing first sell · the card's settings line
#   The dashboard runs from a closed folder (fake keys) · no background loops · every call out of the machine raises ·
#   the browser may only reach 127.0.0.1.        python3 devtests/step/ui_first.py [Holy_Dashboard.pyw] [-q] [--shot=/abs/path.png]
import json, os, shutil, socket, subprocess, sys, tempfile, threading, urllib.request, importlib.machinery, importlib.util
import requests

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def _no_net(*a, **k):
    raise OSError("devtests: no network")


requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net

s = socket.socket(); s.bind(("127.0.0.1", 0)); PORT = s.getsockname()[1]; s.close()
R = tempfile.mkdtemp(prefix="ui_first_")
json.dump({"port": PORT}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-uifirst", "sec": "SECA-uifirst", "pass": "PASA-uifirst"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_ui_first", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_ui_first", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda p: {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None
m._okx_get = lambda *a, **k: None
m.PX.update({"XRP-USDT": 1.0})
m.tg_send = lambda *a, **k: True
srv = m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
r = subprocess.run(["node", os.path.join(H, "ui_first.js"), f"http://127.0.0.1:{PORT}/"] + (["-q"] if Q else []) + [x for x in sys.argv if x.startswith("--shot=")],
                   capture_output=True, text=True, timeout=300, cwd="/tmp")
print(r.stdout.strip() or r.stderr.strip()[-1500:])
srv.shutdown()
shutil.rmtree(R, ignore_errors=True)
sys.exit(r.returncode)
