# 🎯 v3.36.66 — the signals (p112). The owner (20-11): «اني اريد اتضيف كل الاشارات … الثناىية وفوق كذلك على حدى … بدون مستويات · الاشعارات
#   حسب المؤشر اذا شراء او تجميع او بيع او صعود او نزول حسب كل عملة وكذلك بشكل عام · انا احدد النسبة … انا ابحث على التركيبة النادرة … كيف
#   احدد النسبة الاشعارات اخاف يطلع مزعج … افحص وضيف وكذلك التوقعات لا تنسها».
#   A closed folder (no network · no keys · synthetic candles for 12 coins · synthetic macro series):
#   ① the 36 systems in the dashboard ARE ci/sig_check6.py's block (byte for byte) · the names · the types
#   ② the catalog: every signal alone + combinations 2 … 6 + 💎 rare · learn/test · random · weeks · the compass history
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
   out.get("ok") and cat and sizes[1] > 100 and sizes[2] > 0 and sizes[3] > 0 and sizes[4] > 0, out)
ok(f"② every kind of signal is in it ({len(codes)} codes): the 36 systems · 📊 the old readings · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️",
   sum(1 for c in L.SYS if c in codes) >= 30 and any(c.startswith("O-") for c in codes) and any(c.startswith("F-") for c in codes)
   and "W-crash" in codes and "M-fng" in codes and any(c in codes for c in ("M-vix", "M-dxy", "M-us10", "M-epu", "M-gpr")), sorted(codes))
ok("② BUY and SELL, both frames · every entry has its learn and test record · the 💎 rare are flagged (6–30 learn cases · ≥ 75%)",
   {e["s"] for e in E} == {1, -1} and {e["f"] for e in E} == {"4H", "1D"} and all(e["nl"] + e["nt"] >= 3 for e in E)
   and any(e["rare"] for e in E) and all(6 <= e["nl"] <= 30 and e["wl"] / e["nl"] >= 0.75 for e in E if e["rare"] and len(e["k"]) > 1),
   [e for e in E if e["rare"]][:2])
ok("② random for comparison per frame and side · weeks of the test period · the compass history (up · flat · down)",
   all(k in cat["base"] for k in ("4H|1", "4H|-1", "1D|1", "1D|-1")) and cat["wk"]["4H"] > 1 and cat["wk"]["1D"] > 1
   and set((cat.get("compass") or {}).keys()) <= {"up", "flat", "down"} and cat.get("compass"), (cat["base"], cat["wk"], cat.get("compass")))
e1 = next(e for e in E if len(e["k"]) == 1 and e["k"][0] == "W-crash" and e["f"] == "4H" and e["s"] == 1)
ok(f"② 🌊 the market-wide crash alone has its record ({e1['nl']} + {e1['nt']} cases) and its test events for the weekly estimate",
   e1["nl"] + e1["nt"] >= 3 and (e1["ev"] is None or len(e1["ev"]) == e1["nt"]), e1)

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
    {"id": "4H|1|18+43+W-crash", "f": "4H", "s": 1, "k": ["18", "43", "W-crash"], "ty": "buy", "nl": 60, "wl": 48, "ml": 0.03, "nt": 24, "wt": 20, "mt": 0.04, "rare": False, "ev": []},
    {"id": "4H|1|18", "f": "4H", "s": 1, "k": ["18"], "ty": "buy", "nl": 900, "wl": 400, "ml": 0.001, "nt": 500, "wt": 230, "mt": 0.0, "rare": False, "ev": None},
    {"id": "1D|1|12+35", "f": "1D", "s": 1, "k": ["12", "35"], "ty": "up", "nl": 40, "wl": 28, "ml": 0.05, "nt": 22, "wt": 15, "mt": 0.06, "rare": False, "ev": []},
    {"id": "1D|1|20+37+O-rsi", "f": "1D", "s": 1, "k": ["20", "37", "O-rsi"], "ty": "buy", "nl": 9, "wl": 8, "ml": 0.1, "nt": 4, "wt": 3, "mt": 0.12, "rare": True, "ev": []},
    {"id": "1D|-1|X-ad", "f": "1D", "s": -1, "k": ["X-ad"], "ty": "dist", "nl": 120, "wl": 50, "ml": -0.01, "nt": 60, "wt": 31, "mt": -0.01, "rare": False, "ev": []},
    {"id": "1D|1|M-fng", "f": "1D", "s": 1, "k": ["M-fng"], "ty": "fng", "nl": 300, "wl": 120, "ml": -0.01, "nt": 100, "wt": 30, "mt": -0.02, "rare": False, "ev": []},
    {"id": "4H|1|W-crash", "f": "4H", "s": 1, "k": ["W-crash"], "ty": "crash", "nl": 50, "wl": 30, "ml": 0.01, "nt": 25, "wt": 14, "mt": 0.012, "rare": False, "ev": []}],
    "base": {"4H|1": {"ht": 43.0, "mt": 0.0}, "1D|1": {"ht": 43.0, "mt": 0.0}, "1D|-1": {"ht": 56.0, "mt": 0.0}, "4H|-1": {"ht": 54.0, "mt": 0.0}},
    "wk": {"4H": 40, "1D": 40}, "coins": ["XRP-USDT", "SOL-USDT", "ADA-USDT"]}
CAT["idx"] = {e["id"]: e for e in CAT["e"]}
m.app_cfg = lambda: dict(_CFG)
_CFG = {"ticker_coins": ["XRP", "SOL"], "sg_thr": 60, "sg_min": 15}
m.ina_cfg = lambda: {"on": False}
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
           {"XRP-USDT": ["12:1", "35:1", "X-ad:-1", "M-fng:1"]}, {}, crash=True)
b1 = m._sg_process(sc1, ["4H", "1D"], st, cfg, CAT, CDB, NOW)
ids = sorted(p[0] + "@" + p[1] for p in st["pend"])
ok("⑤ a combination fires when it starts: 18 + 43 + 🌊 on XRP · SOL · ADA (4H) · 12 + 35 on XRP (1D) — every fire goes to the live record "
   "(the coins outside your list too, flagged 0)", "4H|1|18+43+W-crash@ADA-USDT" in ids and "1D|1|12+35@XRP-USDT" in ids
   and all(p[4] == 0 for p in st["pend"] if p[1] == "ADA-USDT"), ids)
tys = sorted((b["sym"], b["ty"], b.get("f")) for b in b1)
ok("⑤ notified: one message per coin and type, only your coins (XRP · SOL — not ADA) and what passes your settings "
   "(60% · 15 cases · better than random): 🟢 XRP · 🟢 SOL (4H) · 📈 XRP (1D) · 😨 (market) — not the weak single «18» nor 🔻 the distribution",
   tys == sorted([("XRP-USDT", "buy", "4H"), ("SOL-USDT", "buy", "4H"), ("XRP-USDT", "up", "1D"), ("السوق", "fng", "1D"), ("السوق", "crash", "4H")]), tys)
bx = next(b for b in b1 if b["sym"] == "XRP-USDT" and b["ty"] == "buy")
txt = bx["t"] + "\n" + bx["b"]
ok("⑤ the text: «🟢 شراء — XRP-USDT · 4 ساعات» · the signals by name · «📊 السجل: صدقت 20 من 24 مرة (83%) · الشراء العشوائي 43% · المتوسط بعد 3 أيام» · "
   "price + where it fails · ⚠️ not a guarantee", bx["t"] == "🟢 شراء — XRP-USDT · 4 ساعات" and "عودة من تحت حد بولنجر بقوة" in txt and "كسر قاعدة سعرية (QFL)" in txt
   and "🌊 انهيار السوق كله" in txt and "📊 السجل: صدقت 20 من 24 مرة (83%) · الشراء العشوائي 43% · المتوسط بعد 3 أيام +4.0%" in txt
   and "💵 السعر الآن 2.45 · ❌ تبطل إذا أُغلقت شمعة 4 ساعات تحت 2.3" in txt and "⚠️ ليست ضماناً — القرار لك" in txt, txt)
bc = next(b for b in b1 if b["ty"] == "crash")
ok("⑤ 🌊 the market-wide crash: «11 من 28 عملة هبطت بقوة» + its record + your coins that fell most", "11 من 28 عملة" in bc["b"] and "📊 تاريخياً" in bc["b"]
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
ok("⑤ 💎 a rare combination: «💎 تركيبة نادرة — شراء — SOL-USDT · يومي» · «ظهرت 13 مرة فقط، صدقت 11 (85%)» · ⚠️ few cases",
   len(b6) == 1 and b6[0]["t"] == "💎 تركيبة نادرة — شراء — SOL-USDT · يومي" and "📊 ظهرت 13 مرة فقط، صدقت 11 (85%)" in b6[0]["b"]
   and "⚠️ عدد المرات قليل — قد تكون صدفة" in b6[0]["b"], b6)
_CFG.update(sg_rare=False)
st_r = {}
b6b = m._sg_process(scan(T4E, TDE + 86400, {}, {}, {"SOL-USDT": ["20:1", "37:1", "O-rsi:1"]}, {}), ["1D"], st_r, m.sg_cfg(), CAT, CDB, NOW)
ok("⑤ 💎 off ⇒ the rare one is recorded but not notified", not b6b and st_r["pend"][0][4] == 0, (b6b, st_r.get("pend")))
_CFG.update(sg_rnd=False, sg_thr=50, sg_min=10, sg_types={"dist": True})
st_d = {}
b7 = m._sg_process(scan(T4E, TDE, {}, {}, {"XRP-USDT": ["X-ad:-1"]}, {}), ["1D"], st_d, m.sg_cfg(), CAT, CDB, NOW)
ok("⑤ 🔻 the distribution passes only without «better than random» — and then it says so: «⚠️ تاريخياً ليست أفضل من العشوائي»",
   len(b7) == 1 and b7[0]["t"] == "🔻 تصريف — XRP-USDT · يومي" and "السيولة تخرج والسعر لم ينزل بعد" in b7[0]["b"]
   and "⚠️ تاريخياً ليست أفضل من العشوائي" in b7[0]["b"], b7)
_CFG.update(sg_rnd=True, sg_thr=60, sg_min=15)
_CFG.pop("sg_types", None)

# ⑥ the live record grades itself
cd2 = {"c4": {"XRP-USDT": {"d": [[T4E + i * 14400, 1, 1, 1, 2.45 * (1.05 if i == 18 else 1), 1] for i in range(0, 30)]}}, "c": {}}
st6 = {"pend": [["4H|1|18+43+W-crash", "XRP-USDT", T4E, 2.45, 1], ["4H|1|18", "XRP-USDT", T4E + 14400, 2.45, 0]]}
res6 = m._sg_grade(st6, cd2, CAT, NOW + 30 * 14400)
r6 = m._sg_rec(CAT["idx"]["4H|1|18+43+W-crash"], st6)
ok("⑥ after 3 days (18 candles) the fire is graded by itself: +5% − 0.2% fees ⇒ a win · the record grows to 21 of 25 · the one 4 hours later "
   "too (its candle is there, a loss)", st6["rec"]["4H|1|18+43+W-crash"][:2] == [1, 1] and abs(st6["rec"]["4H|1|18+43+W-crash"][2] - 0.048) < 1e-6
   and r6["n"] == 25 and r6["w"] == 21 and st6["rec"]["4H|1|18"][:2] == [1, 0] and len(res6) == 1 and not st6["pend"], (st6, res6))
rb = m._sg_res_block(res6, st6, CAT)
ok("⑥ the result of what you were told: «✅ نتيجة إشارة شراء XRP قبل 3 أيام: +4.8%» · «السجل الآن: 21 من 25 مرة (84%)»",
   rb and rb["t"] == "✅ نتيجة إشارة شراء XRP قبل 3 أيام: +4.8%" and rb["b"] == "السجل الآن: 21 من 25 مرة (84%)", rb)

# ⑦ delivery
SENT.clear()
blocks = [{"sym": f"C{i}-USDT", "ty": "buy", "f": "4H", "t": f"🟢 شراء — C{i}-USDT · 4 ساعات", "b": "x"} for i in range(5)]
st7 = {}
_CFG.update(sg_cap=3)
outd = m._sg_deliver(blocks, st7, m.sg_cfg(), NOW)
ok("⑦ one Telegram message for the round · the daily cap 3 ⇒ 3 of 5 sent + «🔕 وصلت حد إشعارات الإشارات اليوم (3)» · all 5 in the page log",
   len(outd) == 3 and len([x for x in SENT if x[0] == "tg"]) == 1 and "🎯 إشارات جديدة (3)" in SENT[0][1] and "🔕 وصلت حد إشعارات الإشارات اليوم (3)" in SENT[0][1]
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
ok("⑦ at 09:00 they come as one message «🌙 إشارات وصلت أثناء ساعات الهدوء (2)»", len(SENT) == 2 and "🌙 إشارات وصلت أثناء ساعات الهدوء (2)" in SENT[0][1]
   and not st8.get("qq"), SENT)
SENT.clear()
_CFG.update(sg_quiet=None, sg_sum=20)
st9 = {}
m._sg_deliver(blocks[:3], st9, m.sg_cfg(), night + 9 * 3600)
m._sg_flush(st9, m.sg_cfg(), night + 9 * 3600)
ok("⑦ 🗓️ the daily summary at 20:00: nothing at noon …", not SENT and len(st9.get("sumq") or []) == 3, (SENT, st9.get("sumq")))
m._sg_flush(st9, m.sg_cfg(), night + 17 * 3600 + 60)
m._sg_flush(st9, m.sg_cfg(), night + 17 * 3600 + 120)
ok("⑦ … at 20:00 one message «🗓️ ملخص الإشارات اليوم (3)» (once a day)", len([x for x in SENT if x[0] == "tg"]) == 1 and "🗓️ ملخص الإشارات اليوم (3)" in SENT[0][1], SENT)
SENT.clear()
_CFG.update(sg_sum=None, sg_ch="app")
m.TG_MUTED["v"] = True
m._sg_deliver(blocks[:1], {}, m.sg_cfg(), NOW + 99)
m.TG_MUTED["v"] = False
m._sg_deliver(blocks[1:2], {}, m.sg_cfg(), NOW + 99)
ok("⑦ 🔕 mute ⇒ nothing goes out · the channel «التطبيق فقط» ⇒ the app only (opens 🎯 · the indicators' channel)",
   SENT == [("app", "🟢 شراء — C1-USDT · 4 ساعات\nx", "sig", "ind")], SENT)
_CFG.pop("sg_ch", None)
m.ina_cfg = lambda: {"on": True}
b10 = m._sg_process(scan(T4E + 40 * 14400, TDE, {}, {}, {}, {}, crash=False) | {"c": {"XRP-USDT": {"4H": {"t": T4E + 40 * 14400, "px": 2.4,
                    "a1": ["W-crash:1"], "a0": [], "lo": 2.3, "hi": 2.5, "ch": -0.1}}}}, ["4H"], {}, m.sg_cfg(), CAT, CDB, NOW + 40 * 14400)
ok("⑦ 🌊 not twice: «📊 تنبيهات المؤشرات» on (it already sends the crash) ⇒ 🎯 does not", not [b for b in b10 if b["ty"] == "crash"], b10)
m.ina_cfg = lambda: {"on": False}
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

# ⑧ settings
real_cfg = {}
m.app_cfg = lambda: dict(real_cfg)
m.save_app_cfg = lambda c: real_cfg.clear() or real_cfg.update(c) or c
r = m.sg_set({"thr": 120, "min": 1, "rmin": 99, "cap": -4, "coins": ["xrp", "sol-usdt", "bad coin!", "XRP"], "quiet": [23, 7], "sum": 25, "ch": "tg",
              "types": {"sell": False, "nope": True}, "fr": {"4H": False}})
c = r["cfg"]
ok("⑧ settings are bounded and cleaned: 95% · 3 · 50 · cap 0 · coins XRP-USDT · SOL-USDT (no junk, no duplicate) · quiet 23–07 · summary 01:00 · "
   "Telegram only · 🔴 off · 4H off", c["thr"] == 95 and c["min"] == 3 and c["rmin"] == 50 and c["cap"] == 0 and c["coins"] == ["XRP-USDT", "SOL-USDT"]
   and c["quiet"] == [23, 7] and c["sum"] == 1 and c["ch"] == "tg" and c["types"]["sell"] is False and "nope" not in c["types"] and c["fr"]["4H"] is False, c)
m.sg_set({"coins": None})
ok("⑧ «↩️ مثل الشريط» ⇒ your coins follow the ticker again", m.sg_cfg()["coins"] is None and "sg_coins" not in real_cfg, real_cfg)
real_cfg.update(ticker_coins=list(cat["coins"]), sg_thr=50, sg_min=3, sg_rnd=False, sg_cap=0)
e50 = m.sg_estimate()
e70 = m.sg_estimate(m._sg_cfg_merge(m.sg_cfg(), {"thr": 70, "min": 20}))
ok(f"⑧ the weekly estimate falls when the threshold rises: 50% ≈ {e50['wk']} a week ({e50['n']} pass) · 70% & 20 cases ≈ {e70['wk']} ({e70['n']})",
   e50["n"] > e70["n"] and e50["wk"] >= e70["wk"] and e50["wk"] > 0, (e50, e70))
real_cfg.update(sg_cap=5)
e5 = m.sg_estimate()
ok("⑧ … and after the daily cap 5 it is at most 35 a week", e5["cut"] <= 35 and (e5["capped"] or e5["wk"] <= 35), e5)

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
real_cfg.update(ticker_coins=["XRP", "SOL"], sg_thr=50, sg_min=3, sg_rnd=False, sg_cap=0)
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
v = m.sg_view()
ok("⑩ the 🎯 window's data: the catalog · now per coin (your coins first) · the estimate · the log · the compass",
   v["cat"] and v["now"] and v["now"][0]["mine"] and v["est"] and v["comp"] and isinstance(v["log"], list), {k: bool(v.get(k)) for k in ("cat", "now", "est", "comp")})
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
print(f"{'✅' if all(res) else '❌'} {sum(res)}/{len(res)} signals checks")
sys.exit(0 if all(res) else 1)
