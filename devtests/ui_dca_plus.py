# ⚡ v3.36.57 — the new DCA+ in the browser (the free ladder: the table and the chart together). Every card kind (devtests/seed_cards.py)
#   + one DCA+ bot (deployed through deploy_dca as the form sends it) with a cycle in progress: the base and safety 1–2 filled, safety 3
#   live, 4–5 in the store. Closed folder · fake keys · no network (the candles come from a fake public feed) · nothing launched.
#   The steps are in ui_dca_plus.js; afterwards this file reads what the clicks wrote:
#   · ✏️ the card's editor → the bot's config and state (plus_edit): filled orders kept · the moved order · the new one · no fills changed
#   · 🚀 the deploy form → a new DCA+ bot with exactly the editor's rows · the normal sell DCA next to it untouched
#   python3 devtests/ui_dca_plus.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, math, os, re, shutil, socket, subprocess, sys, tempfile, time, urllib.request

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


LAUNCH = r'''
import os, sys, math, time, threading, urllib.request, importlib.machinery, importlib.util
import requests
R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
def _no_net(*a, **k):
    raise OSError("devtests: no network")
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_dcap_ui", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcap_ui", ld))
sys.argv = ["x"]
ld.exec_module(m)
CALLS = []
def _pub(p):
    CALLS.append(p)
    if "instruments" in p:
        return {"code": "0", "data": [{"tickSz": "0.01", "lotSz": "0.0001", "minSz": "0.001"}]}
    if "/market/candles" in p:                                     # a fake public feed: 168 hourly candles around 2000 (ETH) · newest first like OKX
        t0 = 1798761600000
        out = []
        for i in range(168):
            c = 1990 + 20 * math.sin(i / 9.0) + i * 0.05
            o = c - 3 * math.cos(i / 5.0)
            out.append([str(t0 + i * 3600000), f"{o:.2f}", f"{max(o, c) + 4:.2f}", f"{min(o, c) - 4:.2f}", f"{c:.2f}", "1", "1", "1", "1"])
        return {"code": "0", "data": out[::-1]}
    return None
m._okx_pub = _pub
m._okx_get = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
m.launch = lambda b: (True, "test")
m.wallet_keys = lambda w: {"api_key": "devtests-k", "secret_key": "devtests-s", "passphrase": "devtests-p"}
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("devtests: the dashboard must not send orders"))
def _ledger():
    while True:
        try:
            m.ledger_tick()
        except Exception:
            pass
        time.sleep(1.5)
threading.Thread(target=_ledger, daemon=True).start()
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
'''

ROWS = [{"d": 0, "q": 0.01, "x": 0.5}, {"d": 1, "q": 0.01, "x": 0.6}, {"d": 1.5, "q": 0.02, "x": 0.8}, {"d": 2, "q": 0.03, "x": 0.7},
        {"d": 2.5, "q": 0.05, "x": 0.5}, {"d": 3, "q": 0.08, "x": 0.4}]
R = tempfile.mkdtemp(prefix="ui_dcap_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    seed_cards.seed(R, DASH)
    def _no_net(*a, **k):
        raise OSError("devtests: no network")
    import requests
    requests.get = requests.post = requests.request = _no_net
    urllib.request.urlopen = _no_net
    cwd = os.getcwd(); os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_dcap_ui0", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcap_ui0", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.launch = lambda b: (True, "test"); m.tg_send = lambda *a, **k: True
    m.wallet_keys = lambda w: {"api_key": "devtests-k", "secret_key": "devtests-s", "passphrase": "devtests-p"}
    before = set(m.bot_dirs())
    r = m.deploy_dca({"symbol": "ETH-USDT", "dca_type": "dca_plus", "plus_rows": json.dumps(ROWS), "exchange_orders": "1", "cycle_wait_sec": "30", "wallet": "main"})
    new = sorted(set(m.bot_dirs()) - before)
    assert r.get("ok") and len(new) == 1, r
    b = m.bot_dirs()[new[0]]
    sp = m.paths_of(b)[0]
    P, p = {}, 2000.0
    for i, x in enumerate(ROWS):
        p = p * (1 + x["d"] / 100) if i else p
        P[i] = (round(p, 2), x["q"])
    filled = [{"price": P[n][0], "qty": P[n][1], "n": n, "net": round(P[n][0] * P[n][1] * 0.9992, 8), "fid": n + 1} for n in range(3)]
    tq = sum(f["qty"] for f in filled); tv = sum(f["price"] * f["qty"] for f in filled); avg = tv / tq
    st = {"phase": "selling", "current_price": 2025.0, "base_price": 2000.0, "planned_levels": [{"n": n, "price": P[n][0], "qty": P[n][1]} for n in P],
          "filled": filled, "pending_levels": [{"n": n, "price": P[n][0], "qty": P[n][1]} for n in (4, 5)],
          "active_sells": {"OK3": {"price": P[3][0], "qty": P[3][1], "n": 3}}, "avg_price": avg, "target_price": avg * (1 - 0.008),
          "total_sold_qty": tq, "total_usdt": tv, "total_net": round(sum(f["net"] for f in filled), 8), "total_coin_profit": 0.00031,
          "cycles_done": 2, "_fid": 3, "cycles_log": []}
    m.save_json_atomic(sp, st)
    m.PX["ETH-USDT"] = 2025.0
    os.chdir(cwd)
    dca_n = [x for x in m.bot_dirs().values() if x["symbol"] == "DOGE-USDT"][0]
    nsp = m.paths_of(dca_n)[0]
    n0 = open(nsp, "rb").read()
    open(os.path.join(R, "_ui_launch.py"), "w").write(LAUNCH)
    d = subprocess.Popen([sys.executable, os.path.join(R, "_ui_launch.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    rr = subprocess.run(["node", os.path.join(H, "ui_dca_plus.js"), f"http://127.0.0.1:{P1}/", os.path.relpath(b["dir"], R)] + (["-q"] if Q else []),
                        capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    out = (rr.stdout or "").strip()
    for ln in out.splitlines():
        if ln.startswith(("✅", "❌")) and not ln.startswith(("✅ ui_dca_plus.js", "❌ ui_dca_plus.js")):
            if not Q or ln.startswith("❌"):
                print(ln, flush=True)
    _m = re.search(r"ui_dca_plus\.js: (\d+)/(\d+)", out)
    if _m:
        res += [True] * int(_m.group(1)) + [False] * (int(_m.group(2)) - int(_m.group(1)))
    if rr.returncode and not _m:
        print(out[-1500:], rr.stderr[-1500:])
        res.append(False)
    jv = {}
    for ln in out.splitlines():
        if ln.startswith("JSON "):
            jv.update(json.loads(ln[5:]))
    s2 = json.load(open(sp, encoding="utf-8"))
    c2 = json.load(open(b["cfg_path"], encoding="utf-8"))
    pe = s2.get("plus_edit") or {}
    rows = pe.get("rows") or []
    exp = jv.get("edit_rows") or []
    ok("✏️ the editor's 💾 wrote the bot's edit (state plus_edit + config): the rows exactly as the editor showed them · the filled orders "
       "(base · safety 1 · safety 2) kept their distance and size · 7 orders (one added on the chart) · safety 4 moved",
       rows and rows == c2.get("plus_rows") and len(rows) == 7 and all(rows[i]["d"] == float(ROWS[i]["d"]) and rows[i]["q"] == ROWS[i]["q"] for i in range(3))
       and len(exp) == 7 and all(abs(rows[i]["d"] - exp[i]["d"]) < 1e-9 and abs(rows[i]["q"] - exp[i]["q"]) < 1e-9 and abs(rows[i]["x"] - exp[i]["x"]) < 1e-9 for i in range(7))
       and abs(rows[4]["d"] - ROWS[4]["d"]) > 0.05, (rows, exp))
    ok("… and nothing else changed in the bot's state (the fills · the live order · the profit) — the engine applies it, the dashboard only writes fields",
       s2.get("filled") == filled and s2.get("active_sells") == st["active_sells"] and s2.get("total_coin_profit") == 0.00031)
    nb = [x for x in m.bot_dirs().values() if x["symbol"] == "SOL-USDT" and x["cfg"].get("dca_plus")] if True else []
    m2 = {}
    for dd in os.listdir(R):
        f = os.path.join(R, dd, "config_SOL-USDT.json")
        if os.path.exists(f):
            c = json.load(open(f, encoding="utf-8"))
            if c.get("dca_plus"):
                m2 = c
    dep = jv.get("deploy_rows") or []
    ok("🚀 the deploy form made a DCA+ bot (SOL-USDT) with exactly the editor's rows (the quick fill + a size typed by hand) · a sell DCA "
       "(bot_type dca) · its engine dca_plus.py",
       m2 and m2.get("bot_type") == "dca" and m2.get("plus_rows") and len(dep) == len(m2["plus_rows"])
       and all(abs(a["d"] - b_["d"]) < 1e-9 and abs(a["q"] - b_["q"]) < 1e-9 and abs(a["x"] - b_["x"]) < 1e-9 for a, b_ in zip(m2["plus_rows"], dep)),
       (m2.get("plus_rows"), dep))
    ok("the normal sell DCA next to it: its state file not touched (byte for byte)", open(nsp, "rb").read() == n0)
    rc = 0 if all(res) else 1
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_dca_plus: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_dca_plus: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
