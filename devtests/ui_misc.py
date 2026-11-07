# 🧩 the owner's requests 7-11 in a real browser — the real dashboard in a closed folder (fake keys · no network · nothing
#   launched): a ♾️ grid bot · an accumulator · a bot deleted before this version in _archive · the steps in ui_misc.js
#   python3 devtests/ui_misc.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, shutil, socket, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_misc_")
P1 = port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-uimisc", "sec": "SECA-uimisc", "pass": "PASA-uimisc"}],
           "accumulators": [{"id": "A1", "symbol": "XRP-USDT", "name": "XRP", "pct": 10, "coin_pct": 0, "enabled": True, "start": "2026-11-01"}]},
          open(os.path.join(R, "monitor_config.json"), "w"))
g = os.path.join(R, "grid_xrp")
os.makedirs(g)
json.dump({"symbol": "XRP-USDT", "bot_type": "grid", "grid_percentage": 0.01, "usd_value": 10, "api_key": "KEYA-uimisc", "secret_key": "SECA-uimisc",
           "passphrase": "PASA-uimisc", "bot_id": "HBMISCGRID01"}, open(os.path.join(g, "config_XRP-USDT.json"), "w"))
json.dump({"current_price": 1.0, "total_profit": 1.0, "limit_buys": {"1": {"target_price": 0.99, "locked_qty": 10}},
           "limit_sells": {"2": {"target_price": 1.01, "locked_qty": 10}}, "ladder_base": 1.0}, open(os.path.join(g, "grid_state_XRP-USDT.json"), "w"))
old = os.path.join(R, "_archive", "20260101_120000_dca_sol")
os.makedirs(old)
json.dump({"symbol": "SOL-USDT", "bot_type": "dca", "usd_value": 20, "api_key": "KEYA-uimisc", "secret_key": "SECA-uimisc", "passphrase": "PASA-uimisc"},
          open(os.path.join(old, "config_SOL-USDT.json"), "w"))
json.dump({"bots": {"dca_sol@1767268800": {"key": "dca_sol", "sym": "SOL-USDT", "type": "dca", "ts": 1767268800.0, "rel": 0.0, "coin": {"SOL": 0.0123}}}},
          open(os.path.join(R, "Holy_Gone.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_misc.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=300, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
