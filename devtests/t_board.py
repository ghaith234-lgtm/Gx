# 📋 the indicator tables (v3.36.73 · p127 engine) — the owner (21-11): «افضل اتسوي المؤشرات والتوليفات جدول للسوق بشكل عام وللعملة بشكل
#   خاص جدول كلهم يشتغلون ويتنبؤون ويمهم رقمين كم نجح والاخر فشل والنسبة تزداد وتنقص حسب هذه الرقمين وانخلي ثلاث خانات للمؤشرات (الآن ،
#   ٤ ساعات ، يوم) وكذلك تشغيل واطفاء … افضل تبدي من الصفر».
#   A closed folder (no network · no keys · synthetic candles):
#   ① the rows: fixed numbers 1–70 · every row an indicator the scan can fire · a neutral plain name (no Latin) · its plain entry (rule 16)
#   ② the scan sees the hour too: every frame (1H · 4H · 1D) answers what fired on that very candle («e1») · every fired code has a row
#   ③ the whole market's readings: 🚀 a third of the coins jumping together on the last hour · 🌊 the crash on the hour · 📊 most coins
#      crossing above their 50-candle mean · 🧭 the compass turning up (after three days) — each on every coin's last candle
#   ④ a fired row predicts its side for the next candle of its frame · graded at that close: ✅ its way · ❌ the other way · under 0.2% ⇒ not
#      counted · a one-sided event (🌊) predicts only its side · both sides at once ⇒ nothing · the same scan twice ⇒ once · from zero ·
#      «🌐 السوق» from Bitcoin · «*» every coin together · days counted · a prediction without its candle for long is dropped
#   ⑤ the table: 70 rows × ⏱ 🕓 📅 with ✅ ❌ % and the lower bound we trust · the running prediction · the last result · ⏸ per table
#   ⑥ the tick end to end (candles stubbed): the hour is due every hour · the scan runs without the analyst's catalog · the board fills ·
#      the next hour grades it · the analyst still sees only 4H and 1D
#   ⑦ /api/board · the «sb_off» action · safety: no order · no key in the board file
#   python3 devtests/t_board.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, re, shutil, socket, sys, tempfile, threading, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
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
_real_urlopen = urllib.request.urlopen

R = tempfile.mkdtemp(prefix="t_board_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_board", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_board", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
ORD, SENT = [], []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders from the tables"))
m._okx_pub = m._http_json = lambda *a, **k: None
m.tg_send = lambda text, *a, **k: SENT.append(text) or True
m.app_feed_push = lambda *a, **k: True

# ① the rows
nums = [n for n, c, nm in m.SB_ROWS]
codes = [c for n, c, nm in m.SB_ROWS]
L = m._sg_lib()
ev_codes = set(L.SYS) | {c for c in m._SG_XNM if c != "P-fund"}
lat = [(n, nm) for n, c, nm in m.SB_ROWS if re.search(r"[A-Za-z]", nm)]
ok("① 70 rows numbered 1 … 70 once each · one row per indicator (the 36 systems · the ten · the readings · 🚀 📊 🧭 new) · P-fund waits for its data",
   nums == list(range(1, 71)) and len(set(codes)) == 70 and set(codes) == ev_codes, (set(codes) ^ ev_codes, nums[:5]))
ok("① every row has a neutral plain name (no Latin letters) and its plain entry (family · the two names · the two meanings)",
   not lat and all(m._sg_plain(c) and m._sg_plain(c)[1] and m._sg_plain(c)[3] for c in codes), lat or [c for c in codes if not m._sg_plain(c)])
ok("① the frames: ⏱ الآن (the next hour) · 🕓 4 ساعات · 📅 يوم — the hour has its candles (c1 · 1H) · the analyst keeps 4H and 1D",
   m.SB_FR == ("1H", "4H", "1D") and m.SG_BAR["1H"][0] == "c1" and m.SG_SEC["1H"] == 3600 and m.SG_FR == ("4H", "1D")
   and m.SB_FRN["1H"][1] == "الآن", (m.SB_FR, m.SG_FR))

# synthetic candles: 12 coins · 1H 420 · 4H 420 · 1D 330 · a market-wide jump on the last hour · a crash on the last 4 hours
rnd = random.Random(7)
NOW = int(time.time())
T1E, T4E, TDE = NOW // 3600 * 3600 - 3600, NOW // 14400 * 14400 - 14400, NOW // 86400 * 86400 - 86400
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "LTC-USDT", "TRX-USDT", "DOT-USDT", "AVAX-USDT", "BNB-USDT"]


def path(n, px, vol, drift, shock=None):
    rows, p = [], px
    for i in range(n):
        r = rnd.gauss(drift, vol) + ((shock or {}).get(i - n) or 0.0)
        o, c = p, max(1e-6, p * math.exp(r))
        h, l_ = max(o, c) * (1 + abs(rnd.gauss(0, vol / 2))), min(o, c) * (1 - abs(rnd.gauss(0, vol / 2)))
        rows.append([o, h, l_, c, abs(rnd.gauss(1000, 300)) * (3 if abs(r) > 2 * vol else 1)])
        p = c
    return rows


def mk(t_end, sec, rows):
    return {"d": [[t_end - (len(rows) - 1 - i) * sec] + [float(f"{x:.10g}") for x in r] for i, r in enumerate(rows)]}


CDB = {"c1": {}, "c4": {}, "c": {}}
for j, s in enumerate(COINS):
    CDB["c1"][s] = mk(T1E, 3600, path(420, 10 + j * 7, 0.006, 0.0, {-1: 0.09}))
    CDB["c4"][s] = mk(T4E, 14400, path(420, 10 + j * 7, 0.012, 0.0, {-1: -0.12}))
    CDB["c"][s] = mk(TDE, 86400, path(330, 10 + j * 7, 0.03, 0.0005))
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump(CDB, open(m.SG_CFILE, "w"))
os.environ["HOLY_SIG_THREAD"] = "1"

# ② ③ the scan (the worker's own code, in a thread)
job = m._sg_spawn("scan", {"coins": COINS, "frs": ["1H", "4H", "1D"]})
job["th"].join(600)
sc = m._sg_job_out(job) or {}
C = sc.get("c") or {}
fr_ok = all(set((C.get(s) or {}).keys()) == {"1H", "4H", "1D"} and all(isinstance((C[s][f] or {}).get("e1"), list) for f in ("1H", "4H", "1D")) for s in COINS)
ok("② the scan answers every coin on the hour, the 4 hours and the day · each frame says what fired on that very candle («e1»)",
   sc.get("ok") and fr_ok, (sc.get("err"), {s: list((C.get(s) or {}).keys()) for s in COINS[:3]}))
fired = {k.rsplit(":", 1)[0] for s in C for f in C[s] for k in (C[s][f].get("e1") or []) + (C[s][f].get("a1") or [])}
ok(f"② every code the scan fired has its row ({len(fired)} codes seen)", fired and fired <= set(codes), fired - set(codes))
ok("③ 🚀 a third of the coins jumping together on the last hour ⇒ «W-surge» on every coin's hour", all("W-surge:1" in C[s]["1H"]["e1"] for s in COINS),
   {s: C[s]["1H"]["e1"] for s in COINS[:2]})
ok("③ 🌊 the crash of the last 4 hours is on every coin's 4 hours (as before) · and not on the hour that jumped",
   all("W-crash:-1" in C[s]["4H"]["e1"] for s in COINS) and not any("W-crash:-1" in C[s]["1H"]["e1"] for s in COINS) and (sc.get("crash") or {}).get("on"),
   (C["SOL-USDT"]["4H"]["e1"], sc.get("crash")))

# ③ breadth and the compass on built series (the readings' own function)
n = 300
F = {}
for j, s in enumerate(COINS):
    Cs = [100.0] * (n - 2) + [99.0, 110.0]
    D = {"T": [T1E - (n - 1 - i) * 3600 for i in range(n)], "C": Cs, "O": Cs, "H": Cs, "L": Cs, "V": [1.0] * n, "n": n, "blk": 6}
    F[s] = (D, {})
m._sb_wide({"1H": F})
ok("③ 📊 every coin crossing above its 50-candle mean on the last hour ⇒ «W-breadth» up on that candle (once)",
   all(F[s][1].get(("W-breadth", 1)) == [n - 1] for s in COINS) and not any(F[s][1].get(("W-breadth", -1)) for s in COINS), F["BTC-USDT"][1])
nd = 330
Fd = {}
for j, s in enumerate(COINS):
    Cs = [100.0] * 260 + [100.0 - 0.3 * k for k in range(1, 68)] + [140.0, 141.0, 142.0]
    D = {"T": [TDE - (nd - 1 - i) * 86400 for i in range(nd)], "C": Cs, "O": Cs, "H": Cs, "L": Cs, "V": [1.0] * nd, "n": nd, "blk": 5}
    Fd[s] = (D, {})
m._sb_wide({"1D": Fd})
ok("③ 🧭 the compass turning up after three days (Bitcoin above its 200-day mean · most coins above their 50-day) ⇒ «W-comp» up on the last day",
   all(Fd[s][1].get(("W-comp", 1)) == [nd - 1] for s in COINS), Fd["BTC-USDT"][1])

# ④ predictions and their grading
B0 = m._sb_load()
ok("④ the board starts from zero (no record · no prediction)", not B0["rec"] and not B0["pend"], B0)
t0 = T1E - 7200
cdb = {"c1": {"SOL-USDT": {"d": [[t0, 1, 1, 1, 100.0, 1], [t0 + 3600, 1, 1, 1, 105.0, 1]]},
              "BTC-USDT": {"d": [[t0, 1, 1, 1, 50.0, 1], [t0 + 3600, 1, 1, 1, 49.0, 1]]},
              "XRP-USDT": {"d": [[t0, 1, 1, 1, 2.0, 1], [t0 + 3600, 1, 1, 1, 2.002, 1]]}}}     # +0.1%: under the fees (v3.36.76)
S1 = {"c": {"SOL-USDT": {"1H": {"t": t0, "px": 100.0, "e1": ["O-trend:1", "09:-1", "W-crash:1", "W-crash:-1", "14:1", "14:-1", "ZZ-unknown:1"], "a1": [], "a0": []}},
            "BTC-USDT": {"1H": {"t": t0, "px": 50.0, "e1": ["O-trend:1"], "a1": [], "a0": []}},
            "XRP-USDT": {"1H": {"t": t0, "px": 2.0, "e1": ["O-trend:1"], "a1": [], "a0": []}}}}
r1 = m.sb_feed(S1, ["1H"], {}, float(t0 + 3700))
r1b = m.sb_feed(S1, ["1H"], {}, float(t0 + 3800))
B1 = m._sb_load()
P1 = sorted((p[0], p[1], p[3]) for p in B1["pend"])
want = sorted([("SOL-USDT", 1, 1), ("SOL-USDT", 5, -1), ("SOL-USDT", 60, -1), ("BTC-USDT", 1, 1), ("MKT", 1, 1), ("XRP-USDT", 1, 1)])
ok("④ fired rows predict their side: 1 up · 5 down · 🌊 60 only down · «14» fired both ways ⇒ nothing · an unknown code ⇒ nothing · "
   "Bitcoin also feeds «🌐 السوق» · the same scan twice ⇒ once", P1 == want and r1["added"] == 6 and r1b["added"] == 0, (P1, r1, r1b))
r2 = m.sb_feed({"c": {}}, ["1H"], cdb, float(t0 + 7300))
B2 = m._sb_load()
rc = B2["rec"]
g = lambda sc_, n_, f="1H": (rc.get(sc_) or {}).get(str(n_), {}).get(f)
ok("④ graded at the next hour's close: SOL up 5% ⇒ row 1 ✅ · row 5 (down) ❌ · 🌊 60 (down) ❌ · Bitcoin down 2% ⇒ row 1 ❌ on BTC and on «🌐 السوق»",
   g("SOL-USDT", 1)[:2] == [1, 0] and g("SOL-USDT", 5)[:2] == [0, 1] and g("SOL-USDT", 60)[:2] == [0, 1] and g("BTC-USDT", 1)[:2] == [0, 1]
   and g("MKT", 1)[:2] == [0, 1], rc)
ok("④ XRP moved +0.1% — under the 0.2% fees ⇒ not counted (⚖️ v3.36.76: before, any move was a ✅) · «*» (every coin together) = SOL ✅ + BTC ❌ for row 1 (the market table not counted twice) · days counted",
   g("XRP-USDT", 1) is None and g("*", 1)[:3] == [1, 1, 1] and g("SOL-USDT", 1)[2] == 1 and r2["graded"] == 5 and not B2["pend"], (g("*", 1), r2, B2["pend"]))
ok("④ the last result is kept per row (side · time · ✅/❌ · the move)", (B2["last"]["SOL-USDT"]["1"]["1H"][:3] == [1, t0, 1]
   and abs(B2["last"]["SOL-USDT"]["1"]["1H"][3] - 0.05) < 1e-6), B2["last"].get("SOL-USDT"))
B2["pend"] = [["ETH-USDT", 3, "1D", 1, t0 - 10 * 86400, 10.0], ["ETH-USDT", 3, "4H", 1, t0, 10.0]]
m.save_json_atomic(m.SB_FILE, B2)
m.sb_feed({"c": {}}, ["1H"], cdb, float(t0 + 7300))
B3 = m._sb_load()
ok("④ a prediction whose candle never came (10 days) is dropped · a recent one waits", [p[2] for p in B3["pend"]] == ["4H"], B3["pend"])

# ⑤ the table · ⏸
B3["pend"].append(["SOL-USDT", 2, "4H", -1, T4E, 12.0])
m.save_json_atomic(m.SB_FILE, B3)
m.SG_COINS_FORCE = None
V = m.sb_view("SOL-USDT")
r_1 = next(r for r in V["rows"] if r["n"] == 1)
r_2 = next(r for r in V["rows"] if r["n"] == 2)
ok("⑤ the table: 70 rows · each with ⏱ 🕓 📅 (✅ ❌ · % · the lower bound we trust) · its name, family and both meanings",
   V["ok"] and len(V["rows"]) == 70 and set(r_1["f"]) == {"1H", "4H", "1D"} and r_1["f"]["1H"]["w"] == 1 and r_1["f"]["1H"]["p"] == 100.0
   and 0 < r_1["f"]["1H"]["lb"] < 30 and r_1["nm"] and r_1["mu"] and r_1["md"] and r_1["g"] == "trend", r_1)
ok("⑤ the running prediction shows (row 2 · 🕓 down) · the last result shows (row 1 · ⏱ ✅)", r_2["f"]["4H"]["now"] == -1 and r_1["f"]["1H"]["last"][2] == 1,
   (r_2["f"]["4H"], r_1["f"]["1H"]))
Vm, Vx = m.sb_view(""), m.sb_view("NOPE-USDT")
ok("⑤ no scope ⇒ «🌐 السوق» · an unknown coin ⇒ «🌐 السوق» · the coins list is the notification coins", Vm["s"] == "MKT" and Vx["s"] == "MKT"
   and isinstance(Vm["coins"], list), (Vm["s"], Vx["s"]))
o1 = m.sb_off({"s": "SOL-USDT", "n": 5, "on": False})
V5 = next(r for r in m.sb_view("SOL-USDT")["rows"] if r["n"] == 5)
Vb = next(r for r in m.sb_view("BTC-USDT")["rows"] if r["n"] == 5)
o2 = m.sb_off({"s": "SOL-USDT", "n": 5, "on": True})
V5b = next(r for r in m.sb_view("SOL-USDT")["rows"] if r["n"] == 5)
o3 = m.sb_off({"s": "SOL-USDT", "n": 999, "on": False})
ok("⑤ ⏸ a row off in one table (SOL) — not in another (BTC) · back on · an unknown row refused", o1["ok"] and V5["off"] and not Vb["off"] and o2["ok"]
   and not V5b["off"] and not o3["ok"], (o1, o2, o3))

# ⑥ the tick end to end
for f in (m.SB_FILE, m.SG_FILE):
    try:
        os.remove(f)
    except Exception:
        pass
m.MKT_COINS = tuple(COINS)
m.SG_UNI = len(COINS)
CALLS = []


def fake_cache(sym, db, sec, bar, ib, maxn):
    CALLS.append((sym, sec))
    src = CDB[sec].get(sym)
    if not src:
        return [], None
    db.setdefault(sec, {})[sym] = {"d": [list(r) for r in src["d"]]}
    return db[sec][sym]["d"], None


m._fc_cache = fake_cache
m._sg_cat = lambda: None
json.dump({"c1": {}, "c4": {}, "c": {}}, open(m.SG_CFILE, "w"))
m._SG.update(cidx=None, build=None)
t_a = float(T1E + 3600 + 100)
st0 = m._sg_st()
st0["cat_try"] = t_a
m._sg_save(st0)
m.sg_tick(now=t_a, send=False)
st1 = m._sg_st()
Bt = m._sb_load()
ok("⑥ first tick: every coin's history on the three frames · the scan ran without the analyst's catalog · the tables saw the hour, 4 hours and "
   "day · the analyst's marks wait for its catalog (it sees that candle when its catalog is ready)",
   {x[1] for x in CALLS} == {"c1", "c4", "c"} and st1.get("b_1H") == T1E and st1.get("b_4H") == T4E and st1.get("b_1D") == TDE and m._SG.get("build") is None
   and not st1.get("t_4H") and not st1.get("t_1D"), ({k: st1.get(k) for k in ("b_1H", "b_4H", "b_1D", "t_4H", "t_1D")}, m._SG.get("err")))
ok(f"⑥ … and the board filled with that candle's predictions ({len(Bt['pend'])}) on every frame · «🌐 السوق» among them",
   Bt["pend"] and {p[2] for p in Bt["pend"]} >= {"1H"} and any(p[0] == "MKT" for p in Bt["pend"]), Bt["pend"][:4])
ok("⑥ the analyst's own state saw no hour (its «now» has only 4H and 1D — nothing at all without its catalog)",
   all(set(v) <= {"4H", "1D"} for v in (st1.get("now") or {}).values()), st1.get("now"))
n_calls = len(CALLS)
m.sg_tick(now=t_a + 600, send=False)
ok("⑥ a tick inside the same hour fetches nothing", len(CALLS) == n_calls, CALLS[n_calls:][:4])
for s in COINS:
    last = CDB["c1"][s]["d"][-1]
    CDB["c1"][s]["d"].append([last[0] + 3600, last[4], last[4] * 1.02, last[4] * 0.97, last[4] * (1.01 if COINS.index(s) % 2 else 0.99), 1000.0])
stc = m._sg_st()
stc["cat_try"] = t_a + 3600                              # (no catalog in this test — the analyst's weekly build stays out of the way)
m._sg_save(stc)
m.sg_tick(now=t_a + 3600, send=False)
st2 = m._sg_st()
Bt2 = m._sb_load()
nh = sum(r[0] + r[1] for sc_, rows in Bt2["rec"].items() if sc_ != "*" for n_, fr_ in rows.items() for f_, r in fr_.items() if f_ == "1H")
fetched = {x[1] for x in CALLS[n_calls:]}
due_secs = {m.SG_BAR[f][0] for f in m.SB_FR if int((t_a + 3600) // m.SG_SEC[f]) != int(t_a // m.SG_SEC[f])}
ok(f"⑥ the next hour: only the frames that closed a candle are fetched (here {sorted(due_secs)}) · its scan graded the last hour's predictions ({nh} results)",
   fetched == due_secs and "c1" in fetched and st2.get("b_1H") == T1E + 3600 and nh > 0, (fetched, due_secs, st2.get("b_1H"), nh))

# ⑦ the API · the action · safety
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))


def port():
    s_ = socket.socket(); s_.bind(("127.0.0.1", 0)); p_ = s_.getsockname()[1]; s_.close(); return p_


P = port()
srv = m.ThreadingHTTPServer(("127.0.0.1", P), m.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
try:
    with _real_urlopen(f"http://127.0.0.1:{P}/api/board?s=BTC-USDT", timeout=20) as r:
        jb = json.loads(r.read().decode("utf-8"))
    rq = urllib.request.Request(f"http://127.0.0.1:{P}/api/control", data=json.dumps({"action": "sb_off", "value": {"s": "BTC-USDT", "n": 7, "on": False}}).encode(),
                                headers={"Content-Type": "application/json"})
    with _real_urlopen(rq, timeout=20) as r:
        jo = json.loads(r.read().decode("utf-8"))
except Exception as ex:
    jb, jo = {"err": repr(ex)}, {}
finally:
    srv.shutdown()
ok("⑦ GET /api/board?s=BTC-USDT ⇒ Bitcoin's table · the «sb_off» action turns row 7 off there",
   jb.get("ok") and jb.get("s") == "BTC-USDT" and len(jb.get("rows") or []) == 70 and jo.get("ok") and next(r for r in m.sb_view("BTC-USDT")["rows"] if r["n"] == 7)["off"],
   (str(jb)[:300], jo))
blob = open(m.SB_FILE, encoding="utf-8").read().lower()
ok("⑦ no order was sent · no key, secret or passphrase in the board file", not ORD and not any(w in blob for w in ("api_key", "secret", "passphrase", "apikey")), ORD)

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_board: {sum(res)}/{len(res)} (the indicator tables)")
sys.exit(0 if all(res) else 1)
