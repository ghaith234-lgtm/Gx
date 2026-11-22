# 📈 v3.36.75 — the market window in a real browser (p130 · before it 🎯 v3.36.66 p112). The owner (21-11): «اريد يقلي شديصير بالسوق بالحاضر
#   وشراح يصير للسوق بشكل عام وبالعملات بشكل خاص».
#   A closed folder (no network · no keys): synthetic candles for 12 coins (1 hour · 4 hours · a day, all ending at the same price) → the
#   dashboard's own scan, market layer and groups (the functions t_market.py / t_groups.py check) → a second hour where SOL jumps (a notice) →
#   the page (ui_sig.js): «📈 السوق — الآن والمتوقع» and its 5 tabs · 🌐 the market now + Bitcoin's range · 🪙 your coins open to their facts
#   and ranges · 📋 the groups (🪙 · 🌐) · 📜 the range record and the last notices · ⚙️ the groups and facts and coins · 🔮 · ⚙️ · the ticker · a
#   notification tap · settings saved · a phone width.
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
    rnd = random.Random(5)
    NOW = int(time.time())
    T1E, T4E, TDE = NOW // 3600 * 3600 - 3600, NOW // 14400 * 14400 - 14400, NOW // 86400 * 86400 - 86400
    COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "LTC-USDT", "TRX-USDT", "DOT-USDT", "AVAX-USDT", "BNB-USDT"]

    def path(t_end, step, n, p_end, vol, drift):
        """candles that END at p_end (every frame agrees on today's price)"""
        lr = [rnd.gauss(drift, vol) for _ in range(n)]
        p, rows = p_end / math.exp(sum(lr)), []
        for i, r in enumerate(lr):
            o, c = p, p * math.exp(r)
            rows.append([t_end - (n - 1 - i) * step, o, max(o, c) * (1 + abs(rnd.gauss(0, vol / 2))), min(o, c) * (1 - abs(rnd.gauss(0, vol / 2))), c,
                         abs(rnd.gauss(1000, 300)) * (3 if abs(r) > 2 * vol else 1)])
            p = c
        return rows
    CDB = {"c1": {}, "c4": {}, "c": {}}
    for j, s in enumerate(COINS):
        px = 10 + j * 7
        CDB["c"][s] = {"d": path(TDE, 86400, 330, px, 0.034, 0.012 if s == "SOL-USDT" else 0.0006)}
        CDB["c4"][s] = {"d": path(T4E, 14400, 820, px, 0.014 + 0.002 * j, 0.0002)}
        CDB["c1"][s] = {"d": [r[:5] + [r[5] / 24] for r in path(T1E, 3600, 420, px, 0.006, 0.0)]}     # (an hour trades ~1/24 of a day)
    os.makedirs(m.SG_DIR, exist_ok=True)
    json.dump({"c1": {}, "c4": {}, "c": {}}, open(m.SG_CFILE, "w"))
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
    t_a = float(T1E + 3600 + 100)
    m.sg_tick(now=t_a)
    for s in COINS:                                    # the next hour: SOL jumps 9% (outside its 4-hour range ⇒ a notice in 📜)
        last = CDB["c1"][s]["d"][-1]
        jump = 1.09 if s == "SOL-USDT" else 1.0004
        CDB["c1"][s]["d"].append([last[0] + 3600, last[4], last[4] * jump * 1.002, last[4] * 0.999, last[4] * jump, 50.0])
    m.sg_tick(now=t_a + 3600)
    st, A = m._sg_st(), m._an_load()
    ok(f"the closed folder is ready: a scan · the market now ({len((A.get('now') or {}).get('coins') or {})} coins) · the ranges waiting for their end "
       f"({len(A.get('pend') or [])}) · the SOL notice in the log · no old catalog", (A.get("now") or {}).get("mkt") and A.get("pend")
       and any("SOL" in x["t"] for x in st.get("log") or []) and not os.path.exists(os.path.join(m.SG_DIR, "catalog.json")), {"now": bool(A.get("now")), "log": [x["t"] for x in st.get("log") or []][:3]})
    G = m.gp_load()                                    # 🧩 v3.36.77: the first tick built the groups — one champion planted on SOL's 4-hour trend (to see it fire)
    ok(f"🧩 the first tick built the groups on the same candles (frames {sorted((G or {}).get('f') or {})} · your coins {(G or {}).get('keep')})",
       G and sorted(G["f"]) == ["1D", "1H", "4H"] and G.get("keep") == ["XRP-USDT", "SOL-USDT"], G and G.get("n"))
    g4 = G["f"]["4H"]["coin"]["g"]["c_trend"]
    key = next(x[0] for x in g4["m"] if "+" not in x[0])
    for x in g4["m"]:
        if x[0] == key:
            x[1], x[2], x[3], x[4], x[5] = 630, 370, 120, 2, 0.5
        elif x[4] == 2:
            x[4] = 1                                   # (the only champion now: the planted one)
    g4["ch"], g4["rec"] = [key], [600, 1000, 500.0]
    g4["coin"].setdefault("SOL-USDT", {"rec": [0, 0, 0.0], "m": {}})["rec"] = [70, 120, 60.0]
    gm = G["f"]["1D"]["mkt"]["g"]["m_trend"]
    mkey = next(x[0] for x in gm["m"] if "+" not in x[0])
    m.save_json_atomic(m.GP_FILE, G)
    st = m._sg_st()
    st["gpn"] = {"1H": {}, "4H": {"coin": {"c_trend": {"SOL-USDT": [1, [key], T4E]}}}, "1D": {"mkt": {"m_trend": {"BTC-USDT": [-1, [mkey], TDE]}}}}
    m._sg_save(st)
    P1 = port()
    open(os.path.join(R, "_l.py"), "w").write(LAUNCH)
    d = subprocess.Popen([sys.executable, os.path.join(R, "_l.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    OUT = os.path.join(R, "_js.json")
    r = subprocess.run(["node", os.path.join(H, "ui_sig.js"), f"http://127.0.0.1:{P1}/", OUT, SHOTS or "-"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:], flush=True)
    cfg = json.load(open(m.APP_CFG, encoding="utf-8"))
    ok("after the browser: the buttons saved the settings (📊 unusual volume → 👁 · 🌙 quiet hours on · coins back to the ticker)",
       (cfg.get("an_lv") or {}).get("vol") == "view" and "trend" not in (cfg.get("an_lv") or {}) and cfg.get("sg_quiet") == [0, 8]
       and "sg_coins" not in cfg, {k: v for k, v in cfg.items() if k.startswith(("sg_", "an_"))})
    ok("after the browser: the group «⚡ قوة الحركة» is 📲 (saved as an exception to its 👁 default)", (cfg.get("an_lv") or {}).get("g_c_mom") == "now", cfg.get("an_lv"))
    ok("the browser part", r.returncode == 0)
    rc = 0 if res and all(res) else 1
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ ui_sig: {sum(res)}/{len(res)}" if res and all(res) else f"❌ ui_sig: {sum(res)}/{len(res)}")
sys.exit(rc)
