# 🧪 v3.36.46 — the demo bots on the page (p76): the owner (14-11): «… وينشرن تحت بعد الحقيقيات يعني خط فاصل بينهم ما فيه مجموع بينهم
#   فقط كل بوت وكرته وينكتب عليه ديمو». Every card kind in a closed folder (devtests/seed_cards.py) + one demo bot (the plus bot's
#   folder as a demo: no keys · a paper wallet · a big profit in its state that must not reach any total) · the steps in ui_demo.js
#   python3 devtests/ui_demo.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, os, shutil, socket, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
import seed_cards                                             # noqa: E402


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_demo_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    seed_cards.seed(R, DASH)
    src = next(os.path.join(R, n) for n in os.listdir(R) if os.path.exists(os.path.join(R, n, "config_SOL-USDT.json")))
    dd = os.path.join(R, "demo_sol_t1")
    shutil.copytree(src, dd)
    cp = os.path.join(dd, "config_SOL-USDT.json")
    c = json.load(open(cp, encoding="utf-8"))
    c.update(is_demo=True, api_key="", secret_key="", passphrase="", auto_restart=False)
    c.pop("bot_id", None)
    json.dump(c, open(cp, "w", encoding="utf-8"))
    sp = os.path.join(dd, "grid_state_SOL-USDT.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["total_profit"] = 999.0
    json.dump(st, open(sp, "w", encoding="utf-8"))
    json.dump({"v": 1, "sym": "SOL-USDT", "bal": {"USDT": 400.0, "SOL": 3.0}, "frz": {"USDT": 40.0, "SOL": 0.4}, "start": {"USDT": 400.0, "SOL": 3.0},
               "orders": {}, "by_cl": {}, "fills": [], "px": 182.37}, open(os.path.join(dd, "demo_wallet.json"), "w"))
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_demo.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
