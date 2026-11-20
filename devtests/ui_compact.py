# 📏 v3.36.63 — the compact cards (p107): the owner (20-11): «اريدها طوليه بعرض الكروت من اضغط عليها تتمدد يعني فيها انميشن وتدفع الي
#   تحت ، بحيث يتناسق مع كل اشكال الكروت حتى لو ضفنا اشكال كروت جديدة · ربح اليوم ، الحاله ، نوع البوت ، سعر العملة» ⇒ «كذلك الديمو
#   مختصر ، والمراكم كذلك سويه مختصر». Every card kind in a closed folder (devtests/seed_cards.py: 9 bots + 🏦) + one demo bot ·
#   the steps in ui_compact.js
#   python3 devtests/ui_compact.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import time, json, os, shutil, socket, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
import seed_cards                                             # noqa: E402


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_cmp_")
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
    _now = time.strftime("%Y-%m-%d %H:%M:%S")                       # 🧪 v3.36.59: today's sells in its own log ⇒ «اليوم» on its card
    json.dump([{"time": _now, "msg": "🔴 [بيع فوري] السعر: 183.1 | الكمية: 0.1 | الربح: +1.5$ -> تم تجهيز شراء بسعر: 182"},
               {"time": _now, "msg": "🔴 [بيع فوري] السعر: 184.2 | الكمية: 0.1 | الربح: +2.5$ -> تم تجهيز شراء بسعر: 183"},
               {"time": "2020-01-01 09:00:00", "msg": "🔴 [بيع فوري] السعر: 100 | الكمية: 1 | الربح: +50$"}],
              open(os.path.join(dd, "trade_history_SOL.json"), "w", encoding="utf-8"))
    json.dump({"v": 1, "sym": "SOL-USDT", "bal": {"USDT": 400.0, "SOL": 3.0}, "frz": {"USDT": 40.0, "SOL": 0.4}, "start": {"USDT": 400.0, "SOL": 3.0},
               "orders": {}, "by_cl": {}, "fills": [], "px": 182.37}, open(os.path.join(dd, "demo_wallet.json"), "w"))
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_compact.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
