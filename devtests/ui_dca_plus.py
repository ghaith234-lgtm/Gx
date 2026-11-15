# ⚡ v3.36.56 — DCA+ in the browser: every card kind (devtests/seed_cards.py) + one DCA+ bot (deployed through deploy_dca as the form
#   sends it) with a cycle in progress: three filled layers (safety 2 switched off), exits already made. Closed folder · fake keys ·
#   no network · nothing launched. The steps are in ui_dca_plus.js; afterwards this file reads what the clicks wrote into the bot's
#   state file (the engine is not running — only the dashboard writes):
#   · «⚡ يخرج وحده» on safety 2 ⇒ lx_off [] · 💾 the settings ⇒ lx_pct 0.7 · re-open on · «⏏ أخرجها الآن» on safety 3 ⇒ lx_now [its id]
#   · the normal sell DCA next to it: its state file not touched
#   python3 devtests/ui_dca_plus.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
if len(sys.argv) < 2:
    sys.argv.append(DASH)                                     # seed_cards reads argv[1] when imported
import seed_cards                                             # noqa: E402

res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_dcap_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    seed_cards.seed(R, DASH)
    # the DCA+ bot — the dashboard's own deploy, as the form sends it
    def _no_net(*a, **k):
        raise OSError("devtests: no network")
    import requests
    requests.get = requests.post = requests.request = _no_net
    urllib.request.urlopen = _no_net
    cwd = os.getcwd(); os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_dcap_ui", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcap_ui", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.launch = lambda b: (True, "test"); m.tg_send = lambda *a, **k: True
    m.wallet_keys = lambda w: {"api_key": "devtests-k", "secret_key": "devtests-s", "passphrase": "devtests-p"}
    before = set(m.bot_dirs())
    r = m.deploy_dca({"symbol": "ETH-USDT", "dca_type": "dca_plus", "dca_plus": "1", "lx_pct": "0.5", "lx_from": "1", "lx_reopen": False,
                      "base_order_qty": "0.01", "avg_order_qty": "0.01", "first_deviation": "0.5", "step_multiplier": "1.2", "size_multiplier": "1.5",
                      "max_safety_orders": "5", "take_profit_pct": "1", "exchange_orders": "3", "cycle_wait_sec": "30", "wallet": "main"})
    new = sorted(set(m.bot_dirs()) - before)
    assert r.get("ok") and len(new) == 1, r
    b = m.bot_dirs()[new[0]]
    sp = m.paths_of(b)[0]
    P = {0: (2000.0, 0.01), 1: (2010.0, 0.01), 2: (2022.06, 0.015), 3: (2036.53, 0.0225), 4: (2053.89, 0.03375), 5: (2074.73, 0.050625)}
    filled = [{"price": P[n][0], "qty": P[n][1], "n": n, "net": round(P[n][0] * P[n][1] * 0.9992, 8), "fid": n + 1} for n in range(4)]
    tq = sum(f["qty"] for f in filled); tv = sum(f["price"] * f["qty"] for f in filled); avg = tv / tq
    st = {"phase": "selling", "current_price": 2030.0, "planned_levels": [{"n": n, "price": P[n][0], "qty": P[n][1]} for n in P],
          "filled": filled, "pending_levels": [{"n": 5, "price": P[5][0], "qty": P[5][1]}],
          "active_sells": {"OK4": {"price": P[4][0], "qty": P[4][1], "n": 4}}, "avg_price": avg, "target_price": avg * 0.99,
          "total_sold_qty": tq, "total_usdt": tv, "total_net": round(sum(f["net"] for f in filled), 8), "total_coin_profit": 0.00031,
          "cycles_done": 2, "lx_off": [2], "lx_count": 3, "lx_profit": 0.00021, "lx_cycle_n": 1, "lx_cycle_p": 0.00007, "_fid": 4,
          "lx_log": [{"ts": time.time() - 3600, "ns": [3], "sold": 2036.53, "px": 2026.3, "out": 0.0225, "in": 0.02258, "profit": 0.00007,
                      "manual": False, "whole": True, "back": [3]}],
          "cycles_log": [{"id": "HDX-x4-1-1", "n": 2, "ts": time.time() - 3600, "profit": 0.00007, "px": 2026.3, "out": 0.0225, "in": 0.02258,
                          "manual": False, "lx": [3]}]}
    m.save_json_atomic(sp, st)
    os.chdir(cwd)
    dca_n = [x for x in m.bot_dirs().values() if x["symbol"] == "DOGE-USDT"][0]
    nsp = m.paths_of(dca_n)[0]
    n0 = open(nsp, "rb").read()
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    rr = subprocess.run(["node", os.path.join(H, "ui_dca_plus.js"), f"http://127.0.0.1:{P1}/", os.path.relpath(b["dir"], R)] + (["-q"] if Q else []),
                        capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    out = (rr.stdout or "").strip()
    import re as _re
    for ln in out.splitlines():
        if ln.startswith(("✅", "❌")) and not ln.startswith(("✅ ui_dca_plus.js", "❌ ui_dca_plus.js")):
            if not Q or ln.startswith("❌"):
                print(ln, flush=True)
    _m = _re.search(r"ui_dca_plus\.js: (\d+)/(\d+)", out)
    if _m:
        res += [True] * int(_m.group(1)) + [False] * (int(_m.group(2)) - int(_m.group(1)))
    if rr.returncode and not out:
        print(rr.stderr[-1500:])
        res.append(False)
    s2 = json.load(open(sp, encoding="utf-8"))
    ok("the clicks wrote into the DCA+ state file: safety 2 exits alone again (lx_off []) · bounce 0.7% · re-open on · «exit now» on safety 3 "
       "(its id) — and nothing else changed (the fills, the profit)",
       s2.get("lx_off") == [] and s2.get("lx_pct") == 0.7 and s2.get("lx_reopen") is True and s2.get("lx_now") == [4]
       and s2.get("filled") == filled and s2.get("total_coin_profit") == 0.00031, {k: s2.get(k) for k in ("lx_off", "lx_pct", "lx_reopen", "lx_now")})
    ok("the normal sell DCA next to it: its state file not touched (byte for byte)", open(nsp, "rb").read() == n0)
    rc = 0 if all(res) else 1
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_dca_plus: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_dca_plus: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
