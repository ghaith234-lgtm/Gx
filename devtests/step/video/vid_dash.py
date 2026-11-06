# 🎬 the dashboard for the video: a closed folder · fake keys · no background loops · every call out of the machine raises
#   python3 vid_dash.py ROOT PORT        (ROOT holds Holy_Dashboard.pyw + its two config files + the bot's folder)
import os, sys, urllib.request, importlib.machinery, importlib.util
import requests

R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])


def _no_net(*a, **k):
    raise OSError("devtests: no network")


requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_vid", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_vid", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_pub = lambda p: {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None
m._okx_get = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
import threading, time


def _ledger():                                   # the card's profit comes from the ledger (a background loop in the real dashboard)
    while True:
        try:
            m.ledger_tick()
        except Exception:
            pass
        time.sleep(1.5)


threading.Thread(target=_ledger, daemon=True).start()
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
