# 🎯 v3.36.66 — the signals' machinery (p112 · trimmed in v3.36.76 p135: the old analyst's catalog, firing, record and words are gone —
#   the tables live in t_board.py, the market layer and its notices in t_market.py, the tendency in t_tendency.py).
#   A closed folder (no network · no keys · synthetic candles for 12 coins · synthetic macro series):
#   ① the 36 systems in the dashboard ARE ci/sig_check6.py's block (byte for byte) · every code has its plain names
#   ③ the macro readings move later by their publication delay (the GPR 8 days)
#   ④ the scan: the last closed candle · 🌊 a planted crash on the last 4-hour candle is seen
#   ⑦ delivery: 🔕 mute · the channel · a long round in parts · 🧭 the compass smoothed
#   ⑧ settings: what is left (on · coins cleaned · quiet hours · the channel) · a coin added starts a round
#   ⑨ the worker: its own process with no network writes its answer · the thread mode leaves the dashboard's network alone
#   ⑩ the tick end to end (candles stubbed): history → a scan at the close → the market now saved · nothing of the old analyst
#   ⑪ safety: no order function is called · no key in any signals file
#   python3 devtests/t_sigs.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, shutil, subprocess, sys, tempfile, time, urllib.request

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
urllib.request.urlopen = _no_net

R = tempfile.mkdtemp(prefix="t_signals_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_sig", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_sig", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
SENT = []
m.tg_send = lambda text, *a, **k: SENT.append(("tg", text)) or True
m.app_feed_push = lambda text, go=None, kind=None: SENT.append(("app", text, go, kind)) or True
ORD = []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders from the signals"))
REAL_PUB = m._okx_pub

# ① the library
ci = open(os.path.join(H, "..", "ci", "sig_check6.py"), encoding="utf-8").read()
blk = ci[ci.index("# ───────────────────────── indicators"):ci.index("\ndef mean(v):")].rstrip() + "\n"
ok("① the 36 systems in the dashboard are ci/sig_check6.py's block, byte for byte (the measurement and the live signals = one code)",
   m._SG_LIB == blk, (len(m._SG_LIB), len(blk)))
L = m._sg_lib()
ok("① the library runs in its own namespace: 36 systems · its sma/ema do not replace the dashboard's names", len(L.SYS) == 36 and not hasattr(m, "sma"),
   len(L.SYS))
miss = [c for c in L.SYS if c not in m._SG_NM]
noname = [c for c in ["O-st", "O-verdict", "O-bottom", "F-lc", "F-nw", "F-vote", "X-ad", "X-adt", "X-rs", "W-crash", "M-fng", "M-vix", "M-gpr", "P-ls"] if not m._sg_plain(c)]
ok("① every system has its plain names for a rise and a fall · the old readings · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️ · 🏦", not miss and not noname, (miss, noname))

# synthetic history (12 coins · 4-hour 820 · daily 330) + macro series
rnd = random.Random(11)
NOW = int(time.time())
T4E, TDE = NOW // 14400 * 14400 - 14400, NOW // 86400 * 86400 - 86400
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "LTC-USDT", "TRX-USDT", "DOT-USDT", "AVAX-USDT", "BNB-USDT"]
N4, ND = 820, 330
MK = [rnd.gauss(0, 0.011) for _ in range(N4)]
for k in range(60, N4 - 5, 140):
    MK[k] = -0.085                                       # 🌊 market-wide crashes in the history
MK[-1] = -0.12                                           # 🌊 … and one on the last closed 4-hour candle


def path(n, px, vol, drift, mk=None):
    rows, p = [], px
    for i in range(n):
        r = rnd.gauss(drift, vol) + (mk[i] if mk else 0)
        o, c = p, max(1e-6, p * math.exp(r))
        h, l_ = max(o, c) * (1 + abs(rnd.gauss(0, vol / 2))), min(o, c) * (1 - abs(rnd.gauss(0, vol / 2)))
        rows.append([o, h, l_, c, abs(rnd.gauss(1000, 300)) * (3 if abs(r) > 2 * vol else 1)])
        p = c
    return rows


CDB = {"c4": {}, "c": {}}
for j, s in enumerate(COINS):
    CDB["c4"][s] = {"d": [[T4E - (N4 - 1 - i) * 14400] + [float(f"{x:.10g}") for x in r] for i, r in enumerate(path(N4, 10 + j * 7, 0.014 + 0.002 * j, 0.0002, MK))]}
    CDB["c"][s] = {"d": [[TDE - (ND - 1 - i) * 86400] + [float(f"{x:.10g}") for x in r] for i, r in enumerate(path(ND, 10 + j * 7, 0.034, 0.0006))]}
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump(CDB, open(m.SG_CFILE, "w"))
PRO = {}
for k, base, sd in (("vix", 18, 3), ("dxy", 100, 1), ("us10", 4, 0.1), ("epu", 120, 40), ("gpr", 110, 30), ("tone", -1, 0.5)):
    v, d = base, {}
    for i in range(420):
        v = max(0.1, v + rnd.gauss(0, sd * 0.35))
        d[str(TDE - (419 - i) * 86400)] = round(v, 2)
    PRO[k] = {"d": d, "ts": NOW}
json.dump(PRO, open(m.PRO_FILE, "w"))
json.dump({"fng": {"d": {str(TDE - (499 - i) * 86400): int(50 + 42 * math.sin(i / 13)) for i in range(500)}, "ts": NOW}}, open(m.FC_FILE, "w"))

jd = os.path.join(m.SG_DIR, "job_t")
os.makedirs(jd, exist_ok=True)

# ③ the publication delay
pdb, fdb = m._pro_db(), m._fc_db()
mk0 = m._sg_mkt(pdb, fdb)
ks0, _ = m._pro_sorted(pdb.get("gpr"))
ok(f"③ the macro readings move later by their publication delay: GPR {m.SG_MLAG['gpr']} days · EPU {m.SG_MLAG['epu']} · VIX {m.SG_MLAG['vix']} · "
   f"fear & greed {m.SG_MLAG['fng']}", mk0["gpr"][0][0] - ks0[0] == 8 * 86400 and m.SG_MLAG["epu"] == 2 and m.SG_MLAG["vix"] == 1,
   (mk0["gpr"][0][:2], ks0[:2]))

# ④ the scan
t0 = time.time()
sc = m.sg_scan_calc(jd, {"coins": COINS, "frs": ["4H", "1D"]})
ok(f"④ the scan of the last closed candle ({time.time() - t0:.1f}s): every coin, both frames, the signals active now and one candle before",
   sc.get("ok") and set(sc["c"]) == set(COINS) and all(set(F) == {"4H", "1D"} for F in sc["c"].values())
   and all(isinstance(x["a1"], list) and x["t"] in (T4E, TDE) for F in sc["c"].values() for x in F.values()), list(sc["c"].items())[:1])
ok(f"④ 🌊 the planted crash on the last 4-hour candle is seen ({sc['crash']['k']} of {sc['crash']['n']} coins)", sc["crash"]["on"] and
   all("W-crash:1" in sc["c"][s]["4H"]["a1"] for s in COINS), sc["crash"])

m.app_cfg = lambda: dict(_CFG)
_CFG = {"ticker_coins": ["XRP", "SOL"]}
NOW = int(time.time())

# ⑦ delivery (🔔 v3.36.76: the cards, levels, urgent, quiet hours and the cap are checked in t_market ④ — here: mute · the channel · long rounds)
SENT.clear()
fk = lambda sym, ty, ln: {"sym": sym, "ty": ty, "lv": "now", "urg": m.AN_TY[ty][2] == "urgent", "ln": ln, "t": ln, "b": ""}
_CFG.update(sg_ch="app")
m.TG_MUTED["v"] = True
m._sg_deliver([fk("C0-USDT", "out", "⚡ صعد أكثر من المتوقع")], {}, m.sg_cfg(), NOW + 99)
m.TG_MUTED["v"] = False
m._sg_deliver([fk("C1-USDT", "out", "⚡ صعد أكثر من المتوقع")], {}, m.sg_cfg(), NOW + 99)
ok("⑦ 🔕 mute ⇒ nothing goes out · the channel «التطبيق فقط» ⇒ the app only (one card · opens 📈 · the indicators' channel)",
   SENT == [("app", "📈 C1 — حدث الآن\n⚡ صعد أكثر من المتوقع", "sig", "ind")], SENT)
_CFG.pop("sg_ch", None)
SENT.clear()
long_ = [fk(f"C{i}-USDT", "out", "⚡ صعد أكثر من المتوقع: " + "س" * 380) for i in range(30)]
m._sg_deliver(long_, {}, dict(m.sg_cfg(), cap=0), NOW + 120)
tg_ = [x[1] for x in SENT if x[0] == "tg"]
ok(f"⑦ a long round (30 cards ≈ {sum(len(b['ln']) for b in long_)} letters) reaches Telegram in {len(tg_)} parts, each under its 4096-letter limit, nothing lost",
   len(tg_) >= 3 and all(len(t) <= 3800 for t in tg_) and all(f"C{i} —" in "".join(tg_) for i in range(30)), [len(t) for t in tg_])
seq = m._sg_compass_states(m._sg_D(CDB["c"]["BTC-USDT"]["d"], True), [m._sg_D(CDB["c"][s]["d"], True) for s in COINS])
raw_ch = sum(1 for a, b in zip(seq, seq[1:]) if a[1] != b[1])
sm_ch = sum(1 for a, b in zip(seq, seq[1:]) if a[2] != b[2])
ok(f"⑦ 🧭 the compass is smoothed: the raw state changed {raw_ch} times, the shown one {sm_ch} (a new state must hold 3 days)",
   seq and sm_ch < raw_ch and all(any(seq[j][1] == seq[i][2] for j in range(max(0, i - 2), i + 1)) for i in range(len(seq)) if i and seq[i][2] != seq[i - 1][2]),
   (raw_ch, sm_ch))

# ⑧ settings (a coin added starts a round in the background — the real round is stubbed here; ⑩ runs it for real)
_RT = m.sg_tick
_ticks = []
m.sg_tick = lambda *a, **k: _ticks.append(1)
real_cfg = {}
m.app_cfg = lambda: dict(real_cfg)
m.save_app_cfg = lambda c: real_cfg.clear() or real_cfg.update(c) or c
r = m.sg_set({"thr": 120, "cap": -4, "coins": ["xrp", "sol-usdt", "bad coin!", "XRP"], "quiet": [23, 7], "sum": 25, "ch": "tg", "types": {"sell": False}})
c = r["cfg"]
ok("⑧ settings are cleaned: coins XRP-USDT · SOL-USDT (no junk, no duplicate) · quiet 23–07 · Telegram only · the cap stays 12 · the old keys "
   "(% · types · summary) are not kept (🧹 v3.36.76)", c["coins"] == ["XRP-USDT", "SOL-USDT"] and c["quiet"] == [23, 7] and c["ch"] == "tg" and c["cap"] == 12
   and not any(k in real_cfg for k in ("sg_thr", "sg_types", "sg_sum", "sg_cap")) and set(c) == {"on", "coins", "cap", "quiet", "ch", "alv", "atypes"}, (c, real_cfg))
m.sg_set({"coins": None})
ok("⑧ «↩️ مثل الشريط» ⇒ your coins follow the ticker again", m.sg_cfg()["coins"] is None and "sg_coins" not in real_cfg, real_cfg)
_ticks.clear()
r_add = m.sg_set({"coins": ["XRP-USDT", "NEWC-USDT"]})
time.sleep(0.5)
ok("⑧ 🪙 adding a coin of your own («NEWC») starts a round at once (its history in the background) and says so", _ticks and
   r_add["msg"].startswith("🪙 أُضيفت NEWC — تُجلب بياناتها بالخلفية") and r_add["cfg"]["coins"] == ["XRP-USDT", "NEWC-USDT"], (r_add["msg"], _ticks))
_ticks.clear()
m.sg_set({"coins": ["XRP-USDT"]})
time.sleep(0.3)
ok("⑧ 🪙 removing one starts nothing (no fetch needed)", not _ticks, _ticks)
_ci0 = m._SG.get("cidx")
m._SG["cidx"] = {"c4": {"SOL-USDT": 900}, "c": {"SOL-USDT": 400}}
r_sol = m.sg_set({"coins": ["XRP-USDT", "SOL-USDT"]})
time.sleep(0.3)
_t_sol = list(_ticks)
r_tk = m.sg_set({"coins": None})
time.sleep(0.3)
m._SG["cidx"] = _ci0
ok("⑧ 🪙 a coin whose data is already here: «🪙 أُضيفت SOL لإشعاراتك» (nothing to fetch, no round) · «↩️ مثل الشريط» says so",
   r_sol["msg"] == "🪙 أُضيفت SOL لإشعاراتك" and r_tk["msg"] == "↩️ عملات تنبيهات السوق الآن نفس عملات الشريط" and not _t_sol, (r_sol["msg"], r_tk["msg"], _t_sol))
m.sg_set({"coins": None})
time.sleep(0.3)
m.sg_tick = _RT

# ⑨ the worker
os.environ.pop("HOLY_SIG_THREAD", None)
job = m._sg_spawn("scan", {"coins": COINS[:4], "frs": ["1D"]})
t1 = time.time()
while not m._sg_job_done(job) and time.time() - t1 < 300:
    time.sleep(0.5)
o9 = m._sg_job_out(job) or {}
lg = open(os.path.join(job["jd"], "w.log"), encoding="utf-8", errors="replace").read()[-800:]
ok(f"⑨ the worker in its own process ({time.time() - t1:.0f}s · «--holy-sig») answers: 4 coins scanned", "p" in job and o9.get("ok") and len(o9.get("c") or {}) == 4,
   (o9.get("err"), lg))
probe = os.path.join(R, "probe.py")
open(probe, "w").write(
    "import importlib.machinery, importlib.util, sys, os\n"
    f"ld = importlib.machinery.SourceFileLoader('hdp', {os.path.join(R, 'Holy_Dashboard.pyw')!r})\n"
    "m = importlib.util.module_from_spec(importlib.util.spec_from_loader('hdp', ld)); sys.argv = ['x']; ld.exec_module(m)\n"
    "jd = sys.argv[0]\n"
    "os.makedirs('pjob', exist_ok=True); import json; json.dump({'mode': 'scan', 'coins': [], 'frs': []}, open('pjob/job.json', 'w'))\n"
    "m.sg_child('pjob', proc=True)\n"
    "print('NET', m._okx_pub('/api/v5/market/ticker?instId=BTC-USDT'), m._http_json('https://example.com'), m.tg_send('x'))\n")
pr = subprocess.run([sys.executable, probe], cwd=R, capture_output=True, text=True, timeout=120)
ok("⑨ inside the worker every fetch and send is switched off (OKX · the web · Telegram ⇒ nothing)", "NET None None None" in pr.stdout, pr.stdout[-400:] + pr.stderr[-400:])
os.environ["HOLY_SIG_THREAD"] = "1"
job = m._sg_spawn("scan", {"coins": COINS[:2], "frs": ["1D"]})
job["th"].join(120)
ok("⑨ the thread mode (the Windows program) works and leaves the dashboard's own network functions as they were", (m._sg_job_out(job) or {}).get("ok")
   and m._okx_pub is REAL_PUB and m.tg_send is not None, m._sg_job_out(job))

# ⑩ the tick end to end (the candles stubbed — the history above · no network)
for f in (m.SG_FILE, os.path.join(m.SG_DIR, "catalog.json")):
    try:
        os.remove(f)
    except Exception:
        pass
m._SG.update(cidx=None)
real_cfg.clear()
real_cfg.update(ticker_coins=["XRP", "SOL"])
open(os.path.join(m.SG_DIR, "catalog.json"), "w").write("{}")          # an old catalog left on disk (removed by the first tick)
st_old = {"pend": [1, 2], "now": {"X": {}}, "cat_try": 1, "t_4H": 1}
m._sg_save(st_old)
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
json.dump({"c4": {}, "c": {}}, open(m.SG_CFILE, "w"))
SENT.clear()
t_a = float(T4E + 14400 + 100)
m.sg_tick(now=t_a)
st_a = m._sg_st()
mk = m._an_load()
ok("⑩ first tick (📈 v3.36.75): the history of every coin is fetched (every frame) · the scan of the closed candles ran · the market now is saved · "
   "no old catalog (🧹 v3.36.76: the old catalog file and the old state keys are removed)", len(CALLS) >= 2 * len(COINS) and not os.path.exists(os.path.join(m.SG_DIR, "catalog.json"))
   and not any(k in st_a for k in ("pend", "now", "cat_try", "t_4H"))
   and st_a.get("b_4H") == T4E and st_a.get("b_1D") == TDE and (mk.get("now") or {}).get("coins"),
   (len(CALLS), {k: st_a.get(k) for k in ("b_4H", "b_1D", "cat_try", "pend")}))
ok("⑩ … 🧭 the compass is still read (the market's daily state)", (st_a.get("comp") or {}).get("s") in ("up", "flat", "down"), st_a.get("comp"))
n_calls = len(CALLS)
m.sg_tick(now=t_a + 400)
ok("⑩ a tick before the next close fetches nothing and scans nothing (no load on the exchange)", len(CALLS) == n_calls, len(CALLS) - n_calls)
sent_tg = [x for x in SENT if x[0] == "tg"]
ok("⑩ the old analyst's notifications never go out (no «دخول شراء» · no «🧠»): the first look has nothing to compare yet ⇒ nothing sent",
   not sent_tg and not any("دخول" in x[1] or "🧠" in x[1] for x in SENT), sent_tg[:1])
st_bad = m._sg_st()
st_bad["bad"] = ["ZZZ-USDT"]
m._sg_save(st_bad)
real_cfg.update(sg_coins=["XRP-USDT", "SOL-USDT", "ZZZ-USDT"])
vb = m.sg_view()
ok("⑩ 🪙 a coin of yours the exchange does not have is marked ⚠️ (bad) · XRP and SOL are not", vb["bad"] == ["ZZZ-USDT"] and vb["short"] == [], (vb["bad"], vb["short"]))
va = m.an_view()
ok("⑩ … and the market window says so too (missing ZZZ)", "ZZZ-USDT" in (va.get("missing") or []) and "XRP-USDT" not in (va.get("missing") or []), va.get("missing"))
real_cfg.pop("sg_coins", None)
ok("⑩ «the truest first» counts how many times: 13 of 15 (87%) ranks above 2 of 2 (100%) (Wilson's 95% lower bound — the tables' order)",
   m._sg_wlb(13, 15) > m._sg_wlb(2, 2) and m._sg_wlb(20, 24) > m._sg_wlb(3, 3) and abs(m._sg_wlb(0, 0)) < 1e-9, (m._sg_wlb(13, 15), m._sg_wlb(2, 2)))

# ⑪ safety
blob = ""
for f in (m.SG_FILE, m.SG_CFILE, m.AN_FILE):
    blob += open(f, encoding="utf-8").read() if os.path.exists(f) else ""
ok("⑪ no order was sent · no key, secret or passphrase in any signals or market file", not ORD and not any(w in blob.lower() for w in ("api_key", "secret", "passphrase", "apikey")),
   (ORD, [w for w in ("api_key", "secret", "passphrase") if w in blob.lower()]))
src = open(os.path.join(R, "Holy_Dashboard.pyw"), encoding="utf-8").read()
a, b = src.index("# ═══════════════ 🎯 v3.36.66"), src.index("# ═══════════════ 🔔 v3.26.6: إشعارات الأسعار")
ok("⑪ the signals' code calls no order function (_okx_post · place · cancel) and never turns certificate checks off · 🧹 the old analyst's functions are gone",
   not any(w in src[a:b] for w in ("_okx_post", "place_order", "cancel_order", "verify=False", "CERT_NONE"))
   and not any(hasattr(m, f) for f in ("sg_build", "_sg_search", "_sg_process", "_sg_analyst", "sg_catlist", "sg_record", "sg_estimate", "sg_fc")), "")

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_sigs: {sum(res)}/{len(res)} (the signals)")
sys.exit(0 if all(res) else 1)
