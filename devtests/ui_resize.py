# ⚠️ «خلل واجهة: ResizeObserver loop completed with undelivered notifications» — the owner (7-11): «عند تشغيل البرنامج تخرج هذه
#   المشكلة صلحها». The 🔁 periodic bot's order box (3 orders, the rest scroll) is fitted from a ResizeObserver; the fit set the box's
#   own height INSIDE that callback ⇒ the browser reports a loop (harmless: the size is delivered on the next frame) as a page error,
#   and the dashboard's error catcher shows every page error as a toast. The real dashboard in a closed folder (fake keys · no
#   network · nothing launched) with a 🔁 bot holding 8 open orders · the steps in ui_resize.js:
#   ① open + the window resized 6 times (phone ⇄ wide) ⇒ no ResizeObserver error and no «خلل واجهة» toast
#   ② the box still fits exactly 3 orders after every resize (the fit still works) · the same browser note from elsewhere is no toast ·
#      a real page error still shows its toast · the page's OKX live socket is answered by the test (never the network)
#   python3 devtests/ui_resize.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_resize_")
P1 = port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-uires", "sec": "SECA-uires", "pass": "PASA-uires"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
g = os.path.join(R, "rec_trx_a1b2c3")
os.makedirs(g)
json.dump({"symbol": "TRX-USDT", "bot_type": "rec_buy", "mode": "lots", "amount": 10, "every": 1, "unit": "d", "tp_pct": 1, "cap": 100,
           "api_key": "KEYA-uires", "secret_key": "SECA-uires", "passphrase": "PASA-uires", "bot_id": "HBRESIZE0001"},
          open(os.path.join(g, "config_TRX-USDT.json"), "w"))
t0 = time.time() - 9 * 86400
json.dump({"px": 0.25, "lots": [{"id": f"L{i}", "n": i, "ts": t0 + i * 86400, "q": 40.0 + i, "c": 10.0, "ri": 0, "px": round(0.25 - 0.002 * i, 4)}
                                for i in range(1, 9)]}, open(os.path.join(g, "rec_state_TRX-USDT.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_resize.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=300, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
