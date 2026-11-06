# 🪜 the graded grid's card in a real browser, every skin — the real dashboard (closed folder · fake keys · no network) + the real
#   engine on the mock OKX (video/vid_sim.py, its scripted market) + a ♾️ grid bot folder next to it (its card must not change)
#   python3 devtests/step/ui_card.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_card_")
P1, P2 = port(), port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "FAKE-KEY", "sec": "FAKE-SECRET", "pass": "FAKE-PASS"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
g = os.path.join(R, "grid_btc")                           # a ♾️ grid bot: its card keeps its own ladder and strip
os.makedirs(g)
json.dump({"symbol": "BTC-USDT", "bot_type": "grid", "grid_percentage": 0.01, "usd_value": 10, "api_key": "FAKE-KEY",
           "secret_key": "FAKE-SECRET", "passphrase": "FAKE-PASS", "bot_id": "HBGRIDTEST01"}, open(os.path.join(g, "config_BTC-USDT.json"), "w"))
json.dump({"current_price": 65000, "total_profit": 1.0, "limit_buys": {"1": {"target_price": 64350, "locked_qty": 0.00016}},
           "limit_sells": {"2": {"target_price": 65650, "locked_qty": 0.00016}}, "ladder_base": 65000}, open(os.path.join(g, "grid_state_BTC-USDT.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
procs = []
rc = 1
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env); procs.append(d)
    assert "dashboard up" in d.stdout.readline()
    s = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_sim.py"), R, str(P2), "0.25"], stdout=subprocess.PIPE, text=True, env=env); procs.append(s)
    assert "sim ready" in s.stdout.readline()
    import urllib.request as U
    time.sleep(1.5)
    U.urlopen(f"http://127.0.0.1:{P2}/go", timeout=5).read()
    time.sleep(10)                                        # the bot buys and sells a little first
    r = subprocess.run(["node", os.path.join(H, "ui_card.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=300, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    for p in procs:
        p.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
