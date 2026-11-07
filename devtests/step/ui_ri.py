# 🪜💠 reinvest on the graded grid in a real browser — the real dashboard (closed folder · fake keys · no network) + the real
#   engine with reinvest on the mock OKX (ri_sim.py, paced in real time, in the dashboard's folder: it picks up the dashboard's
#   real requests 💉 ➖ ⚖️ 🔓) · the browser steps in ui_ri.js
#   python3 devtests/step/ui_ri.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR` · STEP_ENGINE=… another engine copy)
import json, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_ri_")
P1, P2 = port(), port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "FAKE-KEY", "sec": "FAKE-SECRET", "pass": "FAKE-PASS"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
procs = []
rc = 1
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env); procs.append(d)
    assert "dashboard up" in d.stdout.readline()
    s = subprocess.Popen([sys.executable, os.path.join(H, "ri_sim.py"), R, str(P2), "0.03"], stdout=subprocess.PIPE, text=True, env=env); procs.append(s)
    assert "sim ready" in s.stdout.readline()
    import urllib.request as U
    time.sleep(1.0)
    U.urlopen(f"http://127.0.0.1:{P2}/go", timeout=5).read()
    t0 = time.time()
    while time.time() - t0 < 120:                         # the pots grow first (a few sales at 100%)
        st = json.loads(U.urlopen(f"http://127.0.0.1:{P2}/st.json", timeout=5).read() or b"{}")
        if float((st.get("rb") or {}).get("credited") or 0) > 0.02 and st.get("calm"):
            break
        time.sleep(1.0)
    r = subprocess.run(["node", os.path.join(H, "ui_ri.js"), f"http://127.0.0.1:{P1}/", f"http://127.0.0.1:{P2}"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=400, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    for p in procs:
        p.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
