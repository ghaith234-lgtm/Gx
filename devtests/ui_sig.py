# 🎯 v3.36.66 — the signals in a real browser (p112). The owner (20-11): «… افحص وضيف وكذلك التوقعات لا تنسها».
#   A closed folder (no network · no keys): synthetic candles for 12 coins → the dashboard's own catalog build, scan and live record (the
#   functions t_sigs.py checks) → the page (ui_sig.js): 🎯 the window and its 4 tabs · 🔮 the forecasts show the signals · 📊 · ⚙️ · the
#   ticker's settings · a notification tap · the slider's weekly estimate · settings saved · a phone width.
#   python3 devtests/ui_sig.py [Holy_Dashboard.pyw] [-q] [--shots DIR]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, math, os, random, shutil, socket, subprocess, sys, tempfile, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else ""
DASH = os.path.abspath(next((a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("-") and sys.argv[i - 1] != "--shots"),
                            os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net

LAUNCH = r'''
import os, sys, time, urllib.request, importlib.machinery, importlib.util
import requests
R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
def _no_net(*a, **k):
    raise OSError("devtests: no network")
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_sig_ui", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_sig_ui", ld))
sys.argv = ["x"]
ld.exec_module(m)
m._okx_pub = lambda p: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
m.tg_send = lambda *a, **k: True
m.sg_tick = lambda *a, **k: None                       # the page reads the prepared files (no new scan while the browser looks)
m.SG_MINC, m.SG_RNDC = 5, False
m._fc_run = lambda *a, **k: None
m.FC.update(ts=time.time(), coins={s: {"sym": s, "base": s.split("-")[0], "px": px, "chg": 1.2, "h": {}} for s, px in (("XRP-USDT", 2.4512), ("SOL-USDT", 182.37))},
            order=["XRP-USDT", "SOL-USDT"], err="")
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
'''


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_sig_")
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d = None
rc = 1
try:
    shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
    os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_sig_prep", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_sig_prep", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.tg_send = lambda *a, **k: True
    m.app_feed_push = lambda *a, **k: True
    json.dump({"ticker_coins": ["XRP", "SOL"], "sg_thr": 55, "indic_on": True}, open(m.APP_CFG, "w"))
    m.SG_MINC, m.SG_RNDC = 5, False                    # 🎯 v3.36.71: fixed inside — loosened for the random synthetic history
    rnd = random.Random(5)
    NOW = int(time.time())
    T4E, TDE = NOW // 14400 * 14400 - 14400, NOW // 86400 * 86400 - 86400
    COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "LTC-USDT", "TRX-USDT", "DOT-USDT", "AVAX-USDT", "BNB-USDT"]
    N4, ND = 820, 330
    MK = [rnd.gauss(0, 0.011) for _ in range(N4)]
    for k in range(60, N4 - 5, 140):
        MK[k] = -0.085

    def path(n, px, vol, drift, mk=None):
        rows, p = [], px
        for i in range(n):
            r = rnd.gauss(drift, vol) + (mk[i] if mk else 0)
            o, c = p, max(1e-6, p * math.exp(r))
            rows.append([o, max(o, c) * (1 + abs(rnd.gauss(0, vol / 2))), min(o, c) * (1 - abs(rnd.gauss(0, vol / 2))), c,
                         abs(rnd.gauss(1000, 300)) * (3 if abs(r) > 2 * vol else 1)])
            p = c
        return rows
    CDB = {"c4": {}, "c": {}}
    for j, s in enumerate(COINS):
        CDB["c4"][s] = {"d": [[T4E - (N4 - 1 - i) * 14400] + r for i, r in enumerate(path(N4, 10 + j * 7, 0.014 + 0.002 * j, 0.0002, MK))]}
        CDB["c"][s] = {"d": [[TDE - (ND - 1 - i) * 86400] + r for i, r in enumerate(path(ND, 10 + j * 7, 0.034, 0.0006))]}
    os.makedirs(m.SG_DIR, exist_ok=True)
    json.dump(CDB, open(m.SG_CFILE, "w"))
    json.dump({"fng": {"d": {str(TDE - (499 - i) * 86400): int(50 + 42 * math.sin(i / 13)) for i in range(500)}, "ts": NOW}}, open(m.FC_FILE, "w"))
    m.MKT_COINS = tuple(COINS)
    m.SG_UNI = len(COINS)

    def fake_cache(sym, db, sec, bar, ib, maxn):
        src = CDB[sec].get(sym)
        if not src:
            return [], None
        db.setdefault(sec, {})[sym] = {"d": [list(r) for r in src["d"]]}
        return db[sec][sym]["d"], None
    m._fc_cache = fake_cache
    os.environ["HOLY_SIG_THREAD"] = "1"
    m.sg_tick(now=float(T4E + 14400 + 100))
    j = m._SG.get("build")
    if j and "th" in j:
        j["th"].join(600)
    m.sg_tick(now=float(T4E + 14400 + 130))
    st = m._sg_st()
    ok(f"the closed folder is ready: the catalog ({len((m._sg_cat() or {}).get('e') or [])} signals and combinations) · a scan · the live record · 🧭",
       m._sg_cat() and st.get("now") and st.get("comp"), {k: bool(st.get(k)) for k in ("now", "comp", "pend")})
    P1 = port()
    open(os.path.join(R, "_l.py"), "w").write(LAUNCH)
    d = subprocess.Popen([sys.executable, os.path.join(R, "_l.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    OUT = os.path.join(R, "_js.json")
    r = subprocess.run(["node", os.path.join(H, "ui_sig.js"), f"http://127.0.0.1:{P1}/", OUT, SHOTS or "-"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:], flush=True)
    cfg = json.load(open(m.APP_CFG, encoding="utf-8"))
    ok("after the browser: the slider and the buttons saved the settings (90% · 🔴 off · the daily cap 5)", cfg.get("sg_thr") == 90
       and (cfg.get("sg_types") or {}).get("sell") is False and cfg.get("sg_cap") == 5, {k: v for k, v in cfg.items() if k.startswith("sg_")})
    ok("the browser part", r.returncode == 0)
    rc = 0 if res and all(res) else 1
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_sig: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_sig: {sum(res)}/{len(res)}")
sys.exit(rc)
