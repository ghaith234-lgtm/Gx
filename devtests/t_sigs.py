# 🎯 v3.36.66 — the signals (p112). The owner (20-11): «اني اريد اتضيف كل الاشارات … الثناىية وفوق كذلك على حدى … بدون مستويات · الاشعارات
#   حسب المؤشر اذا شراء او تجميع او بيع او صعود او نزول حسب كل عملة وكذلك بشكل عام · انا احدد النسبة … انا ابحث على التركيبة النادرة … كيف
#   احدد النسبة الاشعارات اخاف يطلع مزعج … افحص وضيف وكذلك التوقعات لا تنسها».
#   A closed folder (no network · no keys · synthetic candles for 12 coins · synthetic macro series):
#   ① the 36 systems in the dashboard ARE ci/sig_check6.py's block (byte for byte) · the names · the types
#   ② the catalog (🧠 v3.36.69): every signal alone + agreeing combinations 2 … 6 proven in all 4 periods · random per period · the
#     compass history · ②b the rule on planted signals · the target/stop judge · the horizons (غداً · الشهر القادم)
#   ③ the macro readings move later by their publication delay (the GPR 8 days)
#   ④ the scan: the last closed candle · 🌊 a planted crash on the last 4-hour candle is seen
#   ⑤ firing: a combination fires once when it starts (not again on the next candle) · every fire goes to the live record · only coins and
#     signals that pass the owner's settings are notified · one message per coin and type · no repeat for a day unless clearly stronger
#   ⑥ the live record grades itself after its time (net after fees) · a notified one sends its result
#   ⑦ delivery: the daily cap (the rest stays in the page) · quiet hours wait and come as one message · the daily summary · 🔕 mute ·
#     the channel · 🌊 not twice when «📊 تنبيهات المؤشرات» already sends it · 🧭 a new state of the market
#   ⑧ settings: bounds · coins cleaned · the weekly estimate falls when the threshold rises
#   ⑨ the worker: its own process with no network writes its answer · the thread mode leaves the dashboard's network alone
#   ⑩ the tick end to end (candles stubbed): history → the catalog built → a scan at the close → notifications · 🔮 gets every coin's signals
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
M = m._sg_meta()
miss = [c for c in L.SYS if c not in m._SG_NM]
ok("① every system has an Arabic name for BUY and SELL · the old readings · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️ · 🏦", not miss and all(k in M for k in
   ["O-st", "O-verdict", "O-bottom", "F-lc", "F-nw", "F-vote", "X-ad", "X-adt", "X-rs", "W-crash", "M-fng", "M-vix", "M-gpr", "P-ls"]), miss)
ty = {("X-ad",): (m._sg_type(["X-ad"], 1), m._sg_type(["X-ad", "18"], -1)), ("12", "35"): m._sg_type(["12", "35"], 1),
      ("18", "43", "W-crash"): m._sg_type(["18", "43", "W-crash"], 1), ("W-crash",): m._sg_type(["W-crash"], 1), ("M-fng",): m._sg_type(["M-fng"], 1),
      ("M-gpr",): m._sg_type(["M-gpr"], -1), ("12", "M-gpr"): m._sg_type(["12", "M-gpr"], -1), ("O-st", "O-macd"): m._sg_type(["O-st", "O-macd"], -1)}
ok("① the types: 🧲 تجميع / 🔻 تصريف (accumulation inside) · 📈 صعود (trend + momentum) · 🟢 شراء (a dip) · 🌊 · 😨 · 🗞️ (alone, market-wide) · "
   "📉 نزول · 🔴 بيع (a macro reading with a coin's signal)",
   ty[("X-ad",)] == ("acc", "dist") and ty[("12", "35")] == "up" and ty[("18", "43", "W-crash")] == "buy" and ty[("W-crash",)] == "crash"
   and ty[("M-fng",)] == "fng" and ty[("M-gpr",)] == "eco" and ty[("12", "M-gpr")] == "sell" and ty[("O-st", "O-macd")] == "down", ty)

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

# ② the catalog (in this process — the worker's own function)
jd = os.path.join(m.SG_DIR, "job_t")
os.makedirs(jd, exist_ok=True)
t0 = time.time()
out = m.sg_build(jd, {"coins": COINS})
cat = m._sg_cat()
E = cat["e"] if cat else []
sizes = {k: sum(1 for e in E if len(e["k"]) == k) for k in range(1, 7)}
codes = set(k for e in E for k in e["k"])
ok(f"② the catalog is built ({out.get('n')} signals and combinations from {out.get('coins')} coins in {time.time() - t0:.0f}s) · sizes {sizes}",
   out.get("ok") and cat and sizes[1] > 100, out)
ok(f"② every kind of signal is in it ({len(codes)} codes): the 36 systems · 📊 the old readings · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️",
   sum(1 for c in L.SYS if c in codes) >= 30 and any(c.startswith("O-") for c in codes) and any(c.startswith("F-") for c in codes)
   and "W-crash" in codes and "M-fng" in codes and any(c in codes for c in ("M-vix", "M-dxy", "M-us10", "M-epu", "M-gpr")), sorted(codes))
ok("② 🧠 v3.36.69: BUY and SELL, both frames · every entry has its record in the 4 periods (cases · wins · average · separate windows) and a "
   "«proven» flag · no 💎 rare any more · every COMBINATION in the catalog is proven (beat random in all four periods)",
   {e["s"] for e in E} == {1, -1} and {e["f"] for e in E} == {"4H", "1D"} and all(e["nt"] >= 3 and len(e["pp"]) == 4 and "c4" in e for e in E)
   and not any(e["rare"] for e in E) and all(e["c4"] for e in E if len(e["k"]) > 1) and cat.get("rule") == "c4"
   and all(sum(x[0] for x in e["pp"]) == e["nt"] and sum(x[1] for x in e["pp"]) == e["wt"] for e in E), [e for e in E if len(e["k"]) > 1][:2])
ok("② random for comparison per frame and side (and per period) · weeks of history · the compass history (up · flat · down) with a month",
   all(k in cat["base"] and len(cat["base"][k]["pp"]) == 4 for k in ("4H|1", "4H|-1", "1D|1", "1D|-1")) and cat["wk"]["4H"] > 1 and cat["wk"]["1D"] > 1
   and set((cat.get("compass") or {}).keys()) <= {"up", "flat", "down"} and cat.get("compass")
   and all("m30" in v for v in cat["compass"].values()), (cat["base"], cat["wk"], cat.get("compass")))
_bk = {}
for e in E:
    _bk.setdefault((e["f"], e["s"], e["nt"], e["wt"], tuple(tuple(x) for x in e["pp"])), []).append(set(e["k"]))
ok(f"② no combination repeats a smaller one with the very same cases (the extra signal added nothing — {cat.get('dup')} removed)",
   cat.get("dup") is not None and not any(a < b for g in _bk.values() for a in g for b in g), cat.get("dup"))
ok("② every entry knows in how many separate windows its cases fell (a day for «tomorrow» · 30 days for the month — a market-wide reading hits "
   "every coin the same day)", all(0 <= e["nd"] <= e["nt"] and (e["nd"] >= 1 or e["nt"] == 0) for e in E),
   [e for e in E if not (0 <= e.get("nd", -1) <= e["nt"])][:2])
e1 = next(e for e in E if len(e["k"]) == 1 and e["k"][0] == "W-crash" and e["f"] == "4H" and e["s"] == 1)
ok(f"② 🌊 the market-wide crash alone has its record ({e1['nt']} cases — its own other side is not «against» it) and its events for the "
   "weekly estimate", e1["nt"] >= 3 and (e1["ev"] is None or len(e1["ev"]) == e1["nt"]), e1)

# ②b the owner's rule on planted signals (deterministic): agreeing groups that beat random in EVERY period are proven · one that fails
#     in the last period is not · an opposite signal on at the same time removes the case
prnd = random.Random(5)


def planted(n, daily, plant):
    rows, p = [], 100.0
    up = {}
    for i0, kind in plant:
        for j in range(1, 7):
            up[i0 + j] = 0.012 if kind == "win" else -0.012
    for i in range(n):
        r = up.get(i, prnd.gauss(0, 0.004))
        o, c = p, p * math.exp(r)
        rows.append([1600000000 + i * (86400 if daily else 14400), o, max(o, c) * 1.001, min(o, c) * 0.999, c, 1000.0])
        p = c
    return m._sg_D(rows, daily)


PC = {}
for j in range(6):
    idx = list(range(230 + j * 3, 1180, 26))
    q4 = 230 + (1190 - 230) * 3 // 4
    plant = [(i, "win") for i in idx]
    plant_c = [(i + 13, "win" if i + 13 < q4 else "loss") for i in idx]
    D4 = planted(1200, False, plant + plant_c)
    E4 = {("08", 1): sorted(idx + [i + 7 for i in idx]), ("09", 1): sorted(idx + [i + 20 for i in idx]),
          ("10", 1): [i + 13 for i in idx], ("11", 1): [i + 13 for i in idx],
          ("12", 1): list(idx[::2]), ("13", -1): list(idx[::2])}
    Dd = planted(400, True, [])
    PC[f"C{j}-USDT"] = (D4, E4, Dd, {}, D4["T"][700])
cp = m._sg_search(PC)
ix = {e["id"]: e for e in cp["e"]}
g1, g2 = ix.get("4H|1|08+09"), ix.get("4H|1|10+11")
ok("②b «08 + 09» always together before a rise ⇒ proven (all 4 periods beat random) · accuracy shown over the whole history",
   g1 and g1["c4"] and g1["wt"] / g1["nt"] > 0.9 and all(x[0] >= m.SG_PMIN["4H"] and x[3] >= 3 for x in g1["pp"]), g1)
ok("②b «10 + 11» rose in periods 1–3 but fell in period 4 ⇒ NOT proven (it is listed with its %, never notified)",
   g2 is not None and not g2["c4"] and g2["pp"][3][1] == 0 and not m._sg_pass(g2, {}, m.sg_cfg(), cp) if g2 else
   not any(e["c4"] and set(e["k"]) == {"10", "11"} for e in cp["e"]), g2)
e12 = ix.get("4H|1|12")
ok("②b «12» fires only together with «13» on the other side (a SELL on at the same time) ⇒ no case is counted for it (the owner: «لازم متفقين»)",
   e12 is None or e12["nt"] == 0, e12)
H_, L_, C_ = [1, 1.01, 1.06, 1, 1], [1, 0.99, 1.0, 1, 1], [1, 1.0, 1.05, 1, 1.02]
ok("②b the judge (history and live record alike): target +5% touched first ⇒ +5% − fee · the stop first ⇒ −5% − fee · both in one candle ⇒ "
   "the stop (careful) · neither ⇒ the move at the end", abs(m._sg_out(H_, L_, C_, 0, 4, 1, 0.05) - (0.05 - m.SG_FEE)) < 1e-9
   and abs(m._sg_out([1, 1.01, 1, 1, 1], [1, 0.94, 1, 1, 1], C_, 0, 4, 1, 0.05) - (-0.05 - m.SG_FEE)) < 1e-9
   and abs(m._sg_out([1, 1.06, 1, 1, 1], [1, 0.94, 1, 1, 1], C_, 0, 4, 1, 0.05) - (-0.05 - m.SG_FEE)) < 1e-9
   and abs(m._sg_out([1, 1.01, 1.01, 1.01, 1.02], [1, 0.99, 0.99, 0.99, 0.99], C_, 0, 4, 1, 0.05) - (0.02 - m.SG_FEE)) < 1e-9
   and abs(m._sg_out([1, 1.01, 1, 1, 1], [1, 0.94, 1, 1, 1], C_, 0, 4, -1, 0.05) - (0.05 - m.SG_FEE)) < 1e-9
   and m._sg_out(H_, L_, C_, 2, 4, 1, 0.05) is None, [m._sg_out(H_, L_, C_, 0, 4, 1, 0.05)])
sg_ = m._sg_sig([100 * math.exp(0.01 * ((-1) ** i)) for i in range(300)], 6)
ok("②b the target/stop distance comes from the coin's own moves before the entry (×√horizon) — bounded 0.4% … 40%",
   sg_[100] == 0.0 and 0.004 <= sg_[200] <= 0.4 and abs(sg_[200] - 0.02 * math.sqrt(6)) < 0.005, sg_[200])
ok("②b the horizons: the 4-hour frame is judged after a day («غداً») · the daily after 30 days («الشهر القادم») · the daily history ~7 years",
   {k: m.SG_HZ[k] for k in ("4H", "1D")} == {"4H": 6, "1D": 30} and m.SG_HZW == {"4H": "غداً", "1D": "الشهر القادم"} and m.SG_N["1D"] >= 2500, (m.SG_HZ, m.SG_N))

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

# ⑤ firing — a small catalog and planted scans (deterministic)
CAT = {"e": [
    {"id": "4H|1|18+43+W-crash", "f": "4H", "s": 1, "k": ["18", "43", "W-crash"], "ty": "buy", "nl": 60, "wl": 48, "ml": 0.03, "nt": 24, "wt": 20, "mt": 0.04, "rare": False, "nd": 16, "ev": [], "c4": True},
    {"id": "4H|1|18", "f": "4H", "s": 1, "k": ["18"], "ty": "buy", "nl": 900, "wl": 400, "ml": 0.001, "nt": 500, "wt": 230, "mt": 0.0, "rare": False, "ev": None},
    {"id": "1D|1|12+35", "f": "1D", "s": 1, "k": ["12", "35"], "ty": "up", "nl": 40, "wl": 28, "ml": 0.05, "nt": 22, "wt": 15, "mt": 0.06, "rare": False, "ev": [], "c4": True},
    {"id": "1D|1|20+37+O-rsi", "f": "1D", "s": 1, "k": ["20", "37", "O-rsi"], "ty": "buy", "nl": 9, "wl": 8, "ml": 0.1, "nt": 13, "wt": 11, "mt": 0.12, "rare": False, "ev": [], "c4": False},
    {"id": "1D|-1|X-ad", "f": "1D", "s": -1, "k": ["X-ad"], "ty": "dist", "nl": 120, "wl": 50, "ml": -0.01, "nt": 60, "wt": 31, "mt": -0.01, "rare": False, "ev": [], "c4": True},
    {"id": "1D|1|M-fng", "f": "1D", "s": 1, "k": ["M-fng"], "ty": "fng", "nl": 300, "wl": 120, "ml": -0.01, "nt": 100, "wt": 30, "mt": -0.02, "rare": False, "ev": [], "c4": True},
    {"id": "4H|1|W-crash", "f": "4H", "s": 1, "k": ["W-crash"], "ty": "crash", "nl": 50, "wl": 30, "ml": 0.01, "nt": 25, "wt": 14, "mt": 0.012, "rare": False, "nd": 9, "ev": [], "c4": True}],
    "base": {"4H|1": {"ht": 43.0, "mt": 0.0}, "1D|1": {"ht": 43.0, "mt": 0.0}, "1D|-1": {"ht": 56.0, "mt": 0.0}, "4H|-1": {"ht": 54.0, "mt": 0.0}},
    "wk": {"4H": 40, "1D": 40}, "coins": ["XRP-USDT", "SOL-USDT", "ADA-USDT"]}
CAT["idx"] = {e["id"]: e for e in CAT["e"]}
m.app_cfg = lambda: dict(_CFG)
_CFG = {"ticker_coins": ["XRP", "SOL"], "sg_thr": 60, "sg_min": 15}
cfg = m.sg_cfg()


def scan(t4, td, a4, a4p, ad, adp, crash=False):
    c = {}
    for s in ("XRP-USDT", "SOL-USDT", "ADA-USDT"):
        c[s] = {"4H": {"t": t4, "px": 2.45, "a1": a4.get(s, []), "a0": a4p.get(s, []), "lo": 2.3, "hi": 2.6, "ch": -0.08},
                "1D": {"t": td, "px": 2.45, "a1": ad.get(s, []), "a0": adp.get(s, []), "lo": 2.31, "hi": 2.6, "ch": 0.01}}
    return {"ok": True, "c": c, "crash": {"t": t4, "n": 28, "k": 11 if crash else 0, "on": crash}}


full = ["18:1", "43:1", "W-crash:1"]
st = {}
sc1 = scan(T4E, TDE, {s: full for s in ("XRP-USDT", "SOL-USDT", "ADA-USDT")}, {s: ["43:1"] for s in ("XRP-USDT", "SOL-USDT", "ADA-USDT")},
           {"XRP-USDT": ["12:1", "35:1", "M-fng:1"]}, {}, crash=True)
b1 = m._sg_process(sc1, ["4H", "1D"], st, cfg, CAT, CDB, NOW)
ids = sorted(p[0] + "@" + p[1] for p in st["pend"])
ok("⑤ a combination fires when it starts: 18 + 43 + 🌊 on XRP · SOL · ADA (4H) · 12 + 35 on XRP (1D) — every fire goes to the live record "
   "(the coins outside your list too, flagged 0)", "4H|1|18+43+W-crash@ADA-USDT" in ids and "1D|1|12+35@XRP-USDT" in ids
   and all(p[4] == 0 for p in st["pend"] if p[1] == "ADA-USDT"), ids)
tys = sorted((b["sym"], b["ty"], b.get("f")) for b in b1)
ok("⑤ notified: one message per coin and type, only your coins (XRP · SOL — not ADA) and what passes your settings "
   "(60% · 15 cases · better than random): 🟢 XRP · 🟢 SOL (tomorrow) · 🟢 XRP (next month — 🧠 v3.36.69: «📈 صعود» folds into 🟢 دخول شراء) · 😨 (market) — not the weak single «18» nor 🔻 the distribution",
   tys == sorted([("XRP-USDT", "buy", "4H"), ("SOL-USDT", "buy", "4H"), ("XRP-USDT", "buy", "1D"), ("السوق", "fng", "1D"), ("السوق", "crash", "4H")]), tys)
st_o = {}
m._sg_process(scan(T4E, TDE, {}, {}, {"XRP-USDT": ["12:1", "35:1", "X-ad:-1"]}, {}), ["1D"], st_o, cfg, CAT, CDB, NOW)
ok("⑤ 🤝 the owner's rule live too: «12 + 35» with a SELL signal on at the same time (🔻 X-ad) ⇒ not on, nothing fired for it · 🌊 the crash "
   "does not count as «against» (18 + 43 + 🌊 fired above)", not any(p[0] == "1D|1|12+35" for p in st_o.get("pend") or [])
   and "1D|1|12+35" not in ((st_o.get("now") or {}).get("XRP-USDT") or {}).get("1D", {}).get("alive", []), st_o.get("pend"))
bx = next(b for b in b1 if b["sym"] == "XRP-USDT" and b["ty"] == "buy")
txt = bx["t"] + "\n" + bx["b"]
ok("⑤ 🧠 the text is analysis, not prices: «🟢 دخول شراء — XRP-USDT · غداً» · «اتفقت عليه مجموعة مؤشرات صدقت في الفترات الأربع» · its record "
   "(«صدقت 20 من 24 مرة (83%) — اختبارها في 16 يوماً مختلفاً · الشراء العشوائي 43% · المتوسط بعد يوم») · why in plain words · no indicator names · "
   "no price · «الدخول والهدف والوقف في نافذة المؤشرات» · ⚠️ not a guarantee", bx["t"] == "🟢 دخول شراء — XRP-USDT · غداً"
   and "اتفقت عليه مجموعة مؤشرات صدقت في الفترات الأربع من التاريخ" in txt
   and "📊 السجل: صدقت 20 من 24 مرة (83%) — اختبارها في 16 يوماً مختلفاً · الشراء العشوائي 43% · المتوسط بعد يوم +4.0%" in txt
   and "لماذا: " in txt and "بولنجر" not in txt and "QFL" not in txt and "2.45" not in txt and "💵" not in txt
   and "📊 الدخول والهدف والوقف في نافذة المؤشرات" in txt and "⚠️ ليست ضماناً — القرار لك" in txt, txt)
bc = next(b for b in b1 if b["ty"] == "crash")
ok("⑤ 🌊 the market-wide crash: «11 من 28 عملة هبطت بقوة» + its record with the real number of days («في 9 أيام مختلفة · 25 حالة على العملات») + "
   "your coins that fell most", "11 من 28 عملة" in bc["b"] and "📊 تاريخياً (في 9 أيام مختلفة · 25 حالة على العملات): الشراء بعده صدق 56%" in bc["b"]
   and "عملاتك الأكثر هبوطاً الآن" in bc["b"], bc)
b2 = m._sg_process(sc1, ["4H", "1D"], st, cfg, CAT, CDB, NOW + 60)
ok("⑤ the same candle again (a second scan) ⇒ nothing fires twice · nothing notified twice", not b2 and len(st["pend"]) == len(ids), (b2, len(st["pend"])))
sc3 = scan(T4E + 14400, TDE, {s: full for s in ("XRP-USDT", "SOL-USDT")}, {s: full for s in ("XRP-USDT", "SOL-USDT")}, {}, {})
b3 = m._sg_process(sc3, ["4H"], st, cfg, CAT, CDB, NOW + 14400)
ok("⑤ the next candle with the combination still on ⇒ not a new fire (edge-triggered, like the measurement)", not b3, b3)
sc4 = scan(T4E + 5 * 14400, TDE, {"XRP-USDT": full}, {"XRP-USDT": []}, {}, {})
b4 = m._sg_process(sc4, ["4H"], st, cfg, CAT, CDB, NOW + 5 * 14400)
ok("⑤ it starts again 20 hours later ⇒ a new fire for the record, but no new message (same coin and type within a day)",
   not b4 and sum(1 for p in st["pend"] if p[0] == "4H|1|18+43+W-crash" and p[1] == "XRP-USDT") == 2, (b4, st["pend"][-2:]))
st["sent"]["XRP-USDT|buy|4H"][0] -= 86400
sc5 = scan(T4E + 12 * 14400, TDE, {"XRP-USDT": full}, {"XRP-USDT": []}, {}, {})
b5 = m._sg_process(sc5, ["4H"], st, cfg, CAT, CDB, NOW + 12 * 14400)
ok("⑤ after a day ⇒ the message comes again", [b["sym"] for b in b5 if b["ty"] == "buy"] == ["XRP-USDT"], b5)
_CFG.update(sg_rare=True, sg_rmin=6)
sc6 = scan(T4E, TDE + 86400, {}, {}, {"SOL-USDT": ["20:1", "37:1", "O-rsi:1"]}, {"SOL-USDT": ["20:1"]})
b6 = m._sg_process(sc6, ["1D"], st, m.sg_cfg(), CAT, CDB, NOW + 86400)
ok("⑤ 🧠 a combination that did NOT hold in all four periods (13 cases · 85%) is recorded for the live record but never notified — even with "
   "the old «💎» switch on", not b6 and any(p[0] == "1D|1|20+37+O-rsi" and p[4] == 0 for p in st["pend"]), (b6, st["pend"][-2:]))
_CFG.update(sg_rare=False)
_CFG.update(sg_thr=50, sg_types={"dist": True})
m.SG_MINC, m.SG_RNDC = 10, False                  # 🎯 v3.36.71: fixed inside (no longer a setting) — loosened here to see the sell
st_d = {}
b7 = m._sg_process(scan(T4E, TDE, {}, {}, {"XRP-USDT": ["X-ad:-1"]}, {}), ["1D"], st_d, m.sg_cfg(), CAT, CDB, NOW)
b7s = next((b for b in b7 if b["ty"] == "sell"), None)
b7n = next((b for b in b7 if b["ty"] == "nst"), None)
ok("⑤ a SELL group passes only without «better than random» (the inside switch — the owner can no longer turn it off) — and then it says so: «🔴 دخول بيع — XRP-USDT · الشهر القادم» · «⚠️ تاريخياً "
   "ليست أفضل من العشوائي» · why «السيولة تخرج من العملة»", b7s and b7s["t"] == "🔴 دخول بيع — XRP-USDT · الشهر القادم"
   and "⚠️ تاريخياً ليست أفضل من العشوائي" in b7s["b"] and "لماذا: السيولة تخرج من العملة" in b7s["b"], b7)
ok("⑤ 🔎 a new state on a coin of yours: «🔎 XRP الآن: 🔻 السيولة تخرج والسعر لم ينزل بعد (تصريف)» · «وصف لما يحدث الآن على المنصة — ليس توقعاً» "
   "· once a day at most", b7n and b7n["t"] == "🔎 XRP الآن: 🔻 السيولة تخرج والسعر لم ينزل بعد (تصريف)" and "ليس توقعاً" in b7n["b"]
   and not [b for b in m._sg_process(scan(T4E, TDE + 86400, {}, {}, {"XRP-USDT": ["X-ad:-1"]}, {}), ["1D"], st_d, m.sg_cfg(), CAT, CDB, NOW + 3600) if b["ty"] == "nst"], b7)
st_q = {}
bq = m._sg_process(scan(T4E, TDE, {}, {}, {"XRP-USDT": ["X-adt:-1", "P-ls:-1", "X-rs:1"]}, {}), ["1D"], st_q, m.sg_cfg(), CAT, CDB, NOW)
ok("⑤ 🔎 quiet: the trend with liquidity · the crowding · the strength vs BTC are shown in the window but not notified (only accumulation/"
   "distribution and aggressive buying/selling are)", not [b for b in bq if b["ty"] == "nst"] and set((st_q.get("nst") or {}).get("XRP-USDT", {}))
   == {"1D|X-adt", "1D|P-ls", "1D|X-rs"}, (bq, st_q.get("nst")))
CAT["e"].append({"id": "1D|1|M-gpr", "f": "1D", "s": 1, "k": ["M-gpr"], "ty": "eco", "nl": 0, "wl": 0, "ml": 0.0, "nt": 392, "wt": 110, "mt": -0.11,
                 "rare": False, "nd": 9, "ev": [], "c4": False})
CAT["idx"] = {e["id"]: e for e in CAT["e"]}
st_g = {}
b8 = m._sg_process(scan(T4E, TDE, {}, {}, {"XRP-USDT": ["M-gpr:1"]}, {}), ["1D"], st_g, m.sg_cfg(), CAT, CDB, NOW)
ok("⑤ 🗞️ a market reading that did NOT hold in the four periods is not sent (the real check of 20-11 sent «المخاطر الجيوسياسية منخفضة» at 28% "
   "vs random 47%) — it still goes to the live record", not [b for b in b8 if b["ty"] == "eco"] and any(p[0] == "1D|1|M-gpr" for p in st_g.get("pend") or []), b8)
_CFG.update(sg_thr=60)
m.SG_MINC, m.SG_RNDC = 15, True
_CFG.pop("sg_types", None)

# ⑤ a market-wide combination counts its DAYS, not its coins (the real check of 20-11: the best «panic bounce» had 22 cases on ONE day)
e1d = dict(CAT["idx"]["4H|1|18+43+W-crash"], nd=1)
r1d = m._sg_rec(e1d, {})
ok("⑤ 19 of 22 coins on one single crash day = one case: «— اختبارها كلها في يوم واحد» · it does not pass 15 cases (it counts 1) · until the live "
   "record adds 14 more different days", r1d["d"] == 1 and not m._sg_pass(e1d, {}, cfg, CAT) and "— اختبارها كلها في يوم واحد" in m._sg_rec_line(e1d, r1d, CAT)
   and m._sg_pass(e1d, {"rec": {e1d["id"]: [14, 12, 0.3, list(range(14))]}}, cfg, CAT), (r1d, m._sg_rec_line(e1d, r1d, CAT)))
ok("⑤ the days in words: يوم واحد · يومين مختلفين · 6 أيام مختلفة · 16 يوماً مختلفاً", [m._sg_dtxt(x) for x in (1, 2, 6, 16)] ==
   ["كلها في يوم واحد", "في يومين مختلفين", "في 6 أيام مختلفة", "في 16 يوماً مختلفاً"], [m._sg_dtxt(x) for x in (1, 2, 6, 16)])

# ⑥ the live record grades itself
cd2 = {"c4": {"XRP-USDT": {"d": [[T4E + i * 14400, 1, 1, 1, 2.45 * (1.05 if i == 6 else 1), 1] for i in range(0, 30)]}}, "c": {}}
st6 = {"pend": [["4H|1|18+43+W-crash", "XRP-USDT", T4E, 2.45, 1], ["4H|1|18", "XRP-USDT", T4E + 14400, 2.45, 0]]}
res6 = m._sg_grade(st6, cd2, CAT, NOW + 30 * 14400)
r6 = m._sg_rec(CAT["idx"]["4H|1|18+43+W-crash"], st6)
ok("⑥ after a day (6 candles) the fire is graded by itself: +5% − 0.2% fees ⇒ a win · the record grows to 21 of 25 (its day kept for the "
   "independent count) · the one 4 hours later too (its candle is there, a loss)", st6["rec"]["4H|1|18+43+W-crash"][:2] == [1, 1]
   and st6["rec"]["4H|1|18+43+W-crash"][3] == [T4E // 86400] and abs(st6["rec"]["4H|1|18+43+W-crash"][2] - 0.048) < 1e-6
   and r6["n"] == 25 and r6["w"] == 21 and st6["rec"]["4H|1|18"][:2] == [1, 0] and len(res6) == 1 and not st6["pend"], (st6, res6))
cd3 = {"c4": {"SOL-USDT": {"d": [[T4E + i * 14400, 2.45, 2.46, 2.45 * (0.96 if i == 2 else 0.999), 2.45 * (1.05 if i == 6 else 1), 1] for i in range(0, 30)]}}, "c": {}}
st6b = {"pend": [["4H|1|18", "SOL-USDT", T4E, 2.45, 0, 0.03]]}
m._sg_grade(st6b, cd3, CAT, NOW + 30 * 14400)
ok("⑥ 🎯 a fire saved with its target/stop distance (3%) is judged like the history: the stop was touched on the 2nd candle ⇒ ❌ −3% − fee, "
   "even though the price ended the day +5%", st6b["rec"]["4H|1|18"][:2] == [1, 0] and abs(st6b["rec"]["4H|1|18"][2] - (-0.03 - m.SG_FEE)) < 1e-6, st6b)
rb = m._sg_res_block(res6, st6, CAT)
ok("⑥ the result of what you were told: «✅ نتيجة إشارة شراء XRP قبل يوم: +4.8%» · «السجل الآن: 21 من 25 مرة (84%)»",
   rb and rb["t"] == "✅ نتيجة إشارة شراء XRP قبل يوم: +4.8%" and rb["b"] == "السجل الآن: 21 من 25 مرة (84%)", rb)

mon6 = m._sg_mon(st6)
ok("⑥ 📅 the accuracy of what reached you, month by month and per horizon: only the notified fire counts (1 of 1 tomorrow) · the record keeps "
   "3,000 judged fires", mon6 == [[time.strftime("%Y-%m", time.gmtime(T4E)), {"4H": [1, 1]}]] and "del hist[3000:]" in open(DASH, encoding="utf-8").read(), mon6)

# ⑥b 🧠 the analyst (v3.36.69) — one word · tomorrow and next month · why · entry/target/stop · the state now
F_b = {"4H": {"t": T4E, "px": 2.0, "alive": ["4H|1|18+43+W-crash"], "s": 0.05},
       "1D": {"t": TDE, "px": 2.0, "alive": [], "s": 0.2, "m50": 1.8, "m200": 1.5}}
st_a = {"nst": {"XRP-USDT": {"1D|X-ad": [-1, TDE - 3 * 86400], "1D|P-tk": [1, TDE - 40 * 86400], "4H|X-rs": [1, T4E]}}}
an1 = m._sg_analyst("XRP-USDT", F_b, st_a, CAT, cfg)
h4 = an1["hz"]["4H"]
ok("⑥b 🧠 a proven BUY group on now (83%) and nothing against ⇒ «🟢 فرصة شراء» · غداً: صعود 83% · target 2.1 · stop 1.9 (its own 5%) · "
   "why in plain words (no indicator names) · the month: no group ⇒ nothing invented",
   an1["w"] == "buy" and an1["wt"] == "فرصة شراء" and h4["dir"] == 1 and h4["h"] == 83 and abs(h4["tgt"] - 2.1) < 1e-9
   and abs(h4["stop"] - 1.9) < 1e-9 and h4["why"] and not any(c.isascii() and c.isalpha() for c in "".join(h4["why"]))
   and an1["hz"]["1D"]["dir"] == 0, an1)
ok("⑥b 🔎 the state now: 🔻 distribution 3 days ago and 💪 stronger than BTC are shown · aggressive buying 40 days ago is too old · the trend "
   "«السعر فوق متوسطي 50 و200 يوم»", [n[0] for n in an1["nst"]] == ["💪 أقوى من البيتكوين", "🔻 السيولة تخرج والسعر لم ينزل بعد (تصريف)"]
   and an1["tr"].startswith("📈 السعر فوق متوسطي 50 و200 يوم"), (an1["nst"], an1["tr"]))
F_c = {"4H": dict(F_b["4H"]), "1D": dict(F_b["1D"], alive=["1D|-1|X-ad"])}
an2 = m._sg_analyst("XRP-USDT", F_c, st_a, CAT, cfg)
an3 = m._sg_analyst("XRP-USDT", {"4H": dict(F_b["4H"], alive=[]), "1D": F_c["1D"]}, st_a, CAT, cfg)
an4 = m._sg_analyst("XRP-USDT", {"4H": dict(F_b["4H"], alive=["4H|1|18"]), "1D": dict(F_b["1D"])}, st_a, CAT, cfg)
ok("⑥b the word: BUY 83% with a SELL 52% on too ⇒ «🟢 فرصة شراء بحذر» (the month shows the sell: هبوط 52%) · only the SELL 52% ⇒ «🟠 تجنّب "
   "الشراء الآن» · only an unproven signal ⇒ «⏸️ انتظر»", an2["w"] == "buyc" and an2["hz"]["1D"]["dir"] == -1 and an2["hz"]["1D"]["h"] == 52
   and an3["w"] == "avoid" and an4["w"] == "wait", (an2["w"], an3["w"], an4["w"]))

# ⑦ delivery
SENT.clear()
blocks = [{"sym": f"C{i}-USDT", "ty": "buy", "f": "4H", "t": f"🟢 شراء — C{i}-USDT · 4 ساعات", "b": "x"} for i in range(5)]
st7 = {}
_CFG.update(sg_cap=3)
outd = m._sg_deliver(blocks, st7, m.sg_cfg(), NOW)
ok("⑦ one Telegram message for the round · the daily cap 3 ⇒ 3 of 5 sent + «🔕 وصلت حد إشعارات المحلل اليوم (3)» · all 5 in the page log",
   len(outd) == 3 and len([x for x in SENT if x[0] == "tg"]) == 1 and "🧠 المحلل — إشعارات جديدة (3)" in SENT[0][1] and "🔕 وصلت حد إشعارات المحلل اليوم (3)" in SENT[0][1]
   and len(st7["log"]) == 5 and any(x[0] == "app" and x[2] == "sig" and x[3] == "ind" for x in SENT), SENT)
SENT.clear()
m._sg_deliver(blocks[:1], st7, m.sg_cfg(), NOW + 60)
ok("⑦ the cap reached ⇒ nothing more today (no second note)", not SENT, SENT)
SENT.clear()
_CFG.update(sg_cap=0, sg_quiet=[0, 8])
night = time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime(NOW)) + " 03:00", "%Y-%m-%d %H:%M"))
st8 = {}
m._sg_deliver(blocks[:2], st8, m.sg_cfg(), night)
ok("⑦ 🌙 quiet hours (00–08): nothing sent at 03:00, the two wait", not SENT and len(st8.get("qq") or []) == 2, (SENT, st8))
m._sg_flush(st8, m.sg_cfg(), night + 6 * 3600)
ok("⑦ at 09:00 they come as one message «🌙 إشعارات المحلل أثناء ساعات الهدوء (2)»", len(SENT) == 2 and "🌙 إشعارات المحلل أثناء ساعات الهدوء (2)" in SENT[0][1]
   and not st8.get("qq"), SENT)
SENT.clear()
_CFG.update(sg_quiet=None, sg_sum=20)
st9 = {}
m._sg_deliver(blocks[:3], st9, m.sg_cfg(), night + 9 * 3600)
m._sg_flush(st9, m.sg_cfg(), night + 9 * 3600)
ok("⑦ 🗓️ the daily summary at 20:00: nothing at noon …", not SENT and len(st9.get("sumq") or []) == 3, (SENT, st9.get("sumq")))
m._sg_flush(st9, m.sg_cfg(), night + 17 * 3600 + 60)
m._sg_flush(st9, m.sg_cfg(), night + 17 * 3600 + 120)
ok("⑦ … at 20:00 one message «🗓️ ملخص المحلل اليوم (3)» (once a day)", len([x for x in SENT if x[0] == "tg"]) == 1 and "🗓️ ملخص المحلل اليوم (3)" in SENT[0][1], SENT)
SENT.clear()
_CFG.update(sg_sum=None, sg_ch="app")
m.TG_MUTED["v"] = True
m._sg_deliver(blocks[:1], {}, m.sg_cfg(), NOW + 99)
m.TG_MUTED["v"] = False
m._sg_deliver(blocks[1:2], {}, m.sg_cfg(), NOW + 99)
ok("⑦ 🔕 mute ⇒ nothing goes out · the channel «التطبيق فقط» ⇒ the app only (opens 🎯 · the indicators' channel)",
   SENT == [("app", "🟢 شراء — C1-USDT · 4 ساعات\nx", "sig", "ind")], SENT)
_CFG.pop("sg_ch", None)
SENT.clear()
_CFG.update(sg_cap=0)
long_ = [{"sym": f"C{i}-USDT", "ty": "buy", "f": "4H", "t": f"🟢 شراء — C{i}-USDT · 4 ساعات", "b": "اتفقت 4 إشارات: " + "س" * 380} for i in range(30)]
m._sg_deliver(long_, {}, m.sg_cfg(), NOW + 120)
tg_ = [x[1] for x in SENT if x[0] == "tg"]
ok(f"⑦ a long round (30 notifications ≈ {sum(len(b['t']) + len(b['b']) for b in long_)} letters) reaches Telegram in {len(tg_)} parts, each under its "
   "4096-letter limit, nothing lost", len(tg_) >= 3 and all(len(t) <= 3800 for t in tg_) and all(f"C{i}-USDT" in "".join(tg_) for i in range(30)),
   [len(t) for t in tg_])
_st10 = {}
_crash = lambda t_: m._sg_process(scan(t_, TDE, {}, {}, {}, {}, crash=True) | {"c": {"XRP-USDT": {"4H": {"t": t_, "px": 2.4, "a1": ["W-crash:1"], "a0": [],
                                  "lo": 2.3, "hi": 2.5, "ch": -0.1}}}}, ["4H"], _st10, m.sg_cfg(), CAT, CDB, NOW + (t_ - T4E))
b10 = _crash(T4E + 40 * 14400)
b11 = _crash(T4E + 42 * 14400)
b12 = _crash(T4E + 47 * 14400)
ok("⑦ 🌊 the market crash comes from 🎯 (the old alerts are gone) · at most once a day: a second crash 8 hours later is not sent · the next day it is",
   [b["ty"] for b in b10] == ["crash"] and not b11 and [b["ty"] for b in b12] == ["crash"], (b10, b11, b12))
comp = {"s": "up", "days": 4, "btc": True, "k": 19, "n": 28, "m14": 0.036}
cb = m._sg_comp_block(comp)
ok("⑦ 🧭 a new state of the market: «🧭 السوق الآن: صاعد 🟢 (منذ 4 أيام)» · BTC above its 200-day average · 19 of 28 · two weeks +3.6%",
   cb["t"] == "🧭 السوق الآن: صاعد 🟢 (منذ 4 أيام)" and "البيتكوين فوق متوسط 200 يوم · 19 من 28 عملة فوق متوسطها" in cb["b"] and "+3.6%" in cb["b"], cb)
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
r = m.sg_set({"thr": 120, "min": 1, "rmin": 99, "cap": -4, "coins": ["xrp", "sol-usdt", "bad coin!", "XRP"], "quiet": [23, 7], "sum": 25, "ch": "tg",
              "types": {"sell": False, "nope": True}, "fr": {"4H": False}})
c = r["cfg"]
ok("⑧ settings are bounded and cleaned: 95% · the count stays 15 (fixed inside · v3.36.71) · 50 · cap 0 · coins XRP-USDT · SOL-USDT (no junk, no duplicate) · quiet 23–07 · summary 01:00 · "
   "Telegram only · 🔴 off · 4H off", c["thr"] == 95 and c["min"] == 15 and "sg_min" not in real_cfg and c["rmin"] == 50 and c["cap"] == 0 and c["coins"] == ["XRP-USDT", "SOL-USDT"]
   and c["quiet"] == [23, 7] and c["sum"] == 1 and c["ch"] == "tg" and c["types"]["sell"] is False and "nope" not in c["types"] and c["fr"]["4H"] is False, c)
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
   r_sol["msg"] == "🪙 أُضيفت SOL لإشعاراتك" and r_tk["msg"] == "↩️ عملات إشعارات المحلل الآن نفس عملات الشريط" and not _t_sol, (r_sol["msg"], r_tk["msg"], _t_sol))
m.sg_set({"coins": None})
time.sleep(0.3)
real_cfg.update(ticker_coins=list(cat["coins"]), sg_thr=50, sg_cap=0)
m.SG_MINC, m.SG_RNDC = 3, False
_c4 = {e["id"]: e.get("c4") for e in m._sg_cat()["e"]}
for e in m._sg_cat()["e"]:
    e["c4"] = True                                       # (the random synthetic history proves nothing — as if every entry held in the 4 periods)
e50 = m.sg_estimate()
e70 = m.sg_estimate(m._sg_cfg_merge(m.sg_cfg(), {"thr": 70}))
ok(f"⑧ the weekly estimate falls when the threshold rises: 50% ≈ {e50['wk']} a week ({e50['n']} pass) · 70% ≈ {e70['wk']} ({e70['n']})",
   e50["n"] > e70["n"] and e50["wk"] >= e70["wk"] and e50["wk"] > 0, (e50, e70))
real_cfg.update(sg_cap=5)
e5 = m.sg_estimate()
ok("⑧ … and after the daily cap 5 it is at most 35 a week", e5["cut"] <= 35 and (e5["capped"] or e5["wk"] <= 35), e5)
for e in m._sg_cat()["e"]:
    e["c4"] = _c4.get(e["id"])

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
for f in (m.SG_FILE, m.SG_CAT):
    try:
        os.remove(f)
    except Exception:
        pass
m._SG.update(cat=None, cat_mt=0, cidx=None, build=None)
real_cfg.clear()
real_cfg.update(ticker_coins=["XRP", "SOL"], sg_thr=50, sg_cap=0)
m.SG_MINC, m.SG_RNDC = 3, False
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
ok("⑩ first tick: the history of every coin is fetched (both frames) and the catalog is started in its own worker",
   len(CALLS) >= 2 * len(COINS) and m._SG.get("build") is not None and st_a.get("cat_try"), (len(CALLS), m._SG.get("build"), st_a))
job = m._SG["build"]
job["th"].join(600) if "th" in job else None
m.sg_tick(now=t_a + 30)
cat2 = m._sg_cat()
ok("⑩ the catalog is ready on the next tick", cat2 and len(cat2["e"]) > 100 and m._SG.get("build") is None, m._SG.get("err"))
ok("⑩ the catalog carries its code's version (cv) — one built by an older code (without a new signal) is rebuilt by itself",
   cat2 and cat2.get("cv") == m.SG_CAT_VER, cat2 and cat2.get("cv"))
st_b = m._sg_st()
ok("⑩ … and the scan of the closed candles ran (both frames) · the live record started · 🧭 the compass is there",
   st_b.get("t_4H") == T4E and st_b.get("t_1D") == TDE and len(st_b.get("pend") or []) > 0 and (st_b.get("comp") or {}).get("s") in ("up", "flat", "down")
   and set(st_b.get("now") or {}) == set(COINS), {k: st_b.get(k) for k in ("t_4H", "t_1D", "comp")})
n_calls = len(CALLS)
m.sg_tick(now=t_a + 400)
ok("⑩ a tick before the next close fetches nothing and scans nothing (no load on the exchange)", len(CALLS) == n_calls, len(CALLS) - n_calls)
sent_tg = [x for x in SENT if x[0] == "tg"]
ok(f"⑩ notifications of that scan reached Telegram ({len(sent_tg)} message) — only XRP · SOL and the market", sent_tg and all(
   ("ADA-USDT" not in x[1] and "ETH-USDT" not in x[1] and "BNB-USDT" not in x[1]) for x in sent_tg), sent_tg[:1])
st_bad = m._sg_st()
st_bad["bad"] = ["ZZZ-USDT"]
m._sg_save(st_bad)
real_cfg.update(sg_coins=["XRP-USDT", "SOL-USDT", "ZZZ-USDT"])
vb = m.sg_view()
ok("⑩ 🪙 a coin of yours the exchange does not have is marked ⚠️ (bad) · XRP and SOL are not", vb["bad"] == ["ZZZ-USDT"] and vb["short"] == [], (vb["bad"], vb["short"]))
real_cfg.pop("sg_coins", None)
v = m.sg_view()
ok("⑩ the 🎯 window's data: the catalog · now per coin (your coins first) · the estimate · the log · the compass",
   v["cat"] and v["now"] and v["now"][0]["mine"] and v["est"] and v["comp"] and isinstance(v["log"], list), {k: bool(v.get(k)) for k in ("cat", "now", "est", "comp")})
ok("⑩ «the truest first» counts how many times: 13 of 15 (87%) ranks above 2 of 2 (100%) (Wilson's 95% lower bound)",
   m._sg_wlb(13, 15) > m._sg_wlb(2, 2) and m._sg_wlb(20, 24) > m._sg_wlb(3, 3) and abs(m._sg_wlb(0, 0)) < 1e-9, (m._sg_wlb(13, 15), m._sg_wlb(2, 2)))
qa = m.sg_catlist({})
ok("⑩ … and the catalog's default order is that bound, highest first", qa["rows"] == sorted(qa["rows"], key=lambda r: -r["lb"]), [r["lb"] for r in qa["rows"][:5]])
q = m.sg_catlist({"fr": ["1D"], "side": ["1"], "size": ["2"]})
ok(f"⑩ the catalog browser filters: daily · buy · 2 together ({q['total']})", q["ok"] and all(r["f"] == "1D" and r["s"] == 1 and len(r["k"]) == 2 for r in q["rows"]),
   q.get("rows", [])[:2])
rows = [{"sym": "XRP-USDT"}, {"sym": "SOL-USDT"}]
fs = m.sg_fc(rows)
ok("⑩ 🔮 the forecasts get every coin's signals (daily · 4-hour) and the compass", fs["ready"] and "sig" in rows[0] and set(rows[0]["sig"]) <= {"4H", "1D"}
   and rows[0]["sig"] and fs.get("comp"), (fs, rows[0].get("sig")))

# ⑪ safety
blob = ""
for f in (m.SG_FILE, m.SG_CAT, m.SG_CFILE):
    blob += open(f, encoding="utf-8").read()
ok("⑪ no order was sent · no key, secret or passphrase in any signals file", not ORD and not any(w in blob.lower() for w in ("api_key", "secret", "passphrase", "apikey")),
   (ORD, [w for w in ("api_key", "secret", "passphrase") if w in blob.lower()]))
src = open(os.path.join(R, "Holy_Dashboard.pyw"), encoding="utf-8").read()
a, b = src.index("# ═══════════════ 🎯 v3.36.66"), src.index("# ═══════════════ 🔔 v3.26.6: إشعارات الأسعار")
ok("⑪ the signals' code calls no order function (_okx_post · place · cancel) and never turns certificate checks off",
   not any(w in src[a:b] for w in ("_okx_post", "place_order", "cancel_order", "verify=False", "CERT_NONE")), "")

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_sigs: {sum(res)}/{len(res)} (the signals)")
sys.exit(0 if all(res) else 1)
