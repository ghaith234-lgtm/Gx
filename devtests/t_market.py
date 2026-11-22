# 📈 the market now and next (v3.36.75 · p130 — the new analyst rebuilt from scratch after checks 13 and 14). The owner (21-11): «اريد يقلي
#   شديصير بالسوق بالحاضر وشراح يصير للسوق بشكل عام وبالعملات بشكل خاص».
#   A closed folder (no network · no keys · synthetic candles):
#   ① 🔎 the present: the market's lines (trend and since when · coins above their mean · alts vs Bitcoin · calm/stormy · fear & greed) and
#      every coin's (daily trend · short term · vs Bitcoin and rank · volatility · unusual volume · support / resistance / busiest area ·
#      accumulation · overbought) — plain Arabic, no Latin letters
#   ② 🔮 the range for 4 hours · tomorrow · the week (80%): the price inside · wider with time · ③ its live record: bands issued only at their
#      frame's close (no overlap) and graded at their end (inside ⇒ ✅ · outside ⇒ ❌ · Bitcoin apart)
#   ④ the facts (🔔 v3.36.76): 14 types in plain words · a level per type (📲 · 👁 · ⛔) · 🔴 urgent (crash · surge · Bitcoin 3% an hour)
#      past quiet hours and the cap · one card per coin + 🔮 tomorrow · 6 hours between a coin's cards unless its trend turned · the cap 12
#   ⑤ the tick end to end (candles stubbed): the scan carries «an» · the first tick only learns the present (no notification) · the next hour's
#      jump outside the range reaches Telegram once · no old catalog is built · ⑥ /api/market · settings: the types saved · no numbers
#   python3 devtests/t_market.py [Holy_Dashboard.pyw] [-q]
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

R = tempfile.mkdtemp(prefix="t_market_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_mkt", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_mkt", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
ORD, SENT = [], []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
m._okx_pub = m._http_json = lambda *a, **k: None
m.tg_send = lambda text, *a, **k: SENT.append(text) or True
m.app_feed_push = lambda *a, **k: True

rnd = random.Random(9)
NOW = int(time.time())
T1E, T4E, TDE = NOW // 3600 * 3600 - 3600, NOW // 14400 * 14400 - 14400, NOW // 86400 * 86400 - 86400
COINS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "LTC-USDT", "TRX-USDT", "DOT-USDT", "AVAX-USDT", "BNB-USDT"]
BASE = {s: 10.0 + 7 * j for j, s in enumerate(COINS)}


def series(t_end, step, n, p_end, vol, drift):
    """a path that ENDS at p_end (all frames agree on today's price)"""
    lr = [rnd.gauss(drift, vol) for _ in range(n)]
    p = p_end / math.exp(sum(lr))
    rows = []
    for i, r in enumerate(lr):
        o, c = p, p * math.exp(r)
        rows.append([t_end - (n - 1 - i) * step, o, max(o, c) * (1 + vol / 3), min(o, c) * (1 - vol / 3), c, (1000.0 + rnd.random() * 200) * step / 86400])
        p = c
    return rows


CDB = {"c1": {}, "c4": {}, "c": {}}
for j, s in enumerate(COINS):
    drift = 0.015 if s == "SOL-USDT" else -0.001
    CDB["c"][s] = {"d": series(TDE, 86400, 330, BASE[s], 0.02 if s == "SOL-USDT" else 0.03, drift)}
    CDB["c4"][s] = {"d": series(T4E, 14400, 420, BASE[s], 0.012, 0.0)}
    CDB["c1"][s] = {"d": series(T1E, 3600, 420, BASE[s], 0.005, 0.0)}
FDB = {"fng": {"d": {str(TDE - (29 - i) * 86400): 50 + i for i in range(30)}}}

# ① the present
P = m.an_scan(CDB, {}, FDB, ["SOL-USDT", "XRP-USDT"])
M, SOL = P["mkt"], P["coins"]["SOL-USDT"]
ml = [x[1] for x in M["lines"]]
cl = [x[1] for x in SOL["lines"]]
lat = [t for t in ml + cl if re.search(r"[A-Za-z]{2,}", t)]
ok(f"① the market now: {len(ml)} lines — «{ml[0][:70]}…» · coins above their mean · alts vs Bitcoin · calm/stormy · fear & greed",
   len(ml) >= 5 and ml[0].startswith("اتجاه السوق (البيتكوين)") and any("فوق متوسط 50 يوماً" in t for t in ml) and any("مزاج السوق" in t for t in ml)
   and any("البيتكوين مقابل العملات" in t for t in ml) and any("حركة السوق" in t for t in ml), ml)
ok(f"① SOL now: «{cl[0][:60]}…» · the short term · vs Bitcoin with its rank · volatility · support / resistance / busiest area",
   cl[0].startswith("الاتجاه اليومي:") and any(t.startswith("على المدى القصير") for t in cl) and any(t.startswith("مقابل البيتكوين") and "من العملات" in t for t in cl)
   and any(t.startswith("التذبذب") for t in cl) and any("أقرب دعم" in t or "أقرب مقاومة" in t for t in cl), cl)
ok("① plain Arabic — no Latin words in any line (the numbers and prices only)", not lat, lat)
H1 = [[T1E - (719 - i) * 3600, 0, 11.0 + (i % 9) * 0.5, 10.0 + (i % 9) * 0.5, 10.5 + (i % 9) * 0.5, 50000.0 if i % 9 == 4 else 100.0] for i in range(720)]
DD = CDB["c"]["SOL-USDT"]["d"]
lvh = m._an_levels(*([float(r[k]) for r in DD] for k in (2, 3, 4, 5)), px=12.0, h1=H1)
lvd = m._an_levels(*([float(r[k]) for r in DD] for k in (2, 3, 4, 5)), px=12.0, h1=H1[:100])
ok(f"① 📍 the busiest area from 30 days of hourly candles (typical price × volume — v3.36.76): the heavy hours traded around 12.5 ⇒ {lvh['poc']:.2f} · "
   f"fewer than 240 hourly candles ⇒ the daily way ({lvd['poc']:.2f})", abs(lvh["poc"] - 12.5) < 0.12 and abs(lvd["poc"] - 12.5) > 0.12, (lvh, lvd))
ok("① SOL climbed for months (its own drift) ⇒ «صاعد» and stronger than Bitcoin", SOL["trend"] == "up" and (SOL.get("rs30") or 0) > 0, (SOL["trend"], SOL.get("rs30")))

# ② the range
rg = SOL["rng"]
ok(f"② the range for 4 hours · tomorrow · the week · the month · three months (🔮 v3.36.76) around the price ({SOL['px']:.4g}): " + " · ".join(f"±{rg[k]['w']}%" for k in ("4h", "1d", "1w", "1m", "3m") if k in rg) + " — wider with time",
   set(rg) == {"4h", "1d", "1w", "1m", "3m"} and all(rg[k]["lo"] < SOL["px"] < rg[k]["hi"] for k in rg) and rg["4h"]["w"] < rg["1d"]["w"] < rg["1w"]["w"] < rg["1m"]["w"] < rg["3m"]["w"]
   and M.get("rng") and M["rng"]["4h"]["lo"] < M["btc"] < M["rng"]["4h"]["hi"], rg)

# ③ the live record of the range
A = m._an_load()
m._an_issue(A, P, ["4H"], float(NOW))
k4 = {p[1] for p in A["pend"]}
A2 = m._an_load()
m._an_issue(A2, P, ["1D"], float(NOW))
k1 = {p[1] for p in A2["pend"]}
ok("③ bands are issued only at their frame's close: the 4-hour close ⇒ «4h» only · the daily close ⇒ «1d» (and «1w» on Mondays)", k4 == {"4h"} and "1d" in k1 and "4h" not in k1, (k4, k1))
KS = {}
for nm_, day_ in (("Jan 1 (a Monday in 2029)", "2029-01-01"), ("Feb 1", "2029-02-01"), ("Feb 2", "2029-02-02")):
    A_ = m._an_load()
    A_["pend"] = []
    m._an_issue(A_, P, ["1D"], float(time.mktime(time.strptime(day_ + " 12", "%Y-%m-%d %H")) - time.timezone))
    KS[nm_] = sorted({p[1] for p in A_["pend"]})
ok(f"③ 🔮 the month on the 1st of every month · the three months on Jan/Apr/Jul/Oct the 1st: {KS}",
   KS["Jan 1 (a Monday in 2029)"] == ["1d", "1m", "1w", "3m"] and KS["Feb 1"] == ["1d", "1m"] and KS["Feb 2"] == ["1d"], KS)
t_end = T1E - 3600
A3 = {"v": 1, "rec": {}, "pend": [["SOL-USDT", "4h", 9.0, 11.0, t_end], ["XRP-USDT", "4h", 9.0, 11.0, t_end], ["BTC-USDT", "1d", 1.0, 100.0, t_end],
                                   ["ETH-USDT", "1w", 1.0, 2.0, NOW + 86400], ["DOT-USDT", "1d", 1.0, 2.0, NOW - 5 * 86400]], "sent": {}}
cdb3 = {"c1": {"SOL-USDT": {"d": [[t_end - 3600, 1, 1, 1, 10.5, 1]]}, "XRP-USDT": {"d": [[t_end - 3600, 1, 1, 1, 12.0, 1]]},
               "BTC-USDT": {"d": [[t_end - 3600, 1, 1, 1, 50.0, 1]]}}}
m._an_grade(A3, cdb3, float(NOW))
ok("③ graded at the band's end: SOL inside ⇒ ✅ · XRP outside ⇒ ❌ · Bitcoin also counted apart · one still running waits · one without its candle for days dropped",
   A3["rec"].get("4h") == [1, 1] and A3["rec"].get("1d") == [1, 0] and A3["rec"].get("btc_1d") == [1, 0] and [p[0] for p in A3["pend"]] == ["ETH-USDT"], A3)

# ④ the facts (🔔 v3.36.76: a level per type · 🔴 urgent · one card per coin)
prev = json.loads(json.dumps(P))
new = json.loads(json.dumps(P))
c0, c1 = prev["coins"]["SOL-USDT"], new["coins"]["SOL-USDT"]
c0.update(trend="side", rs7=-1.0, rs30=-2.0, volx=1.0, ad="flat")
c1.update(trend="up", rs7=2.0, rs30=3.0, volx=2.6, ad="acc")
c1["px"] = c0["px"] * 1.05
LVD = {"SOL-USDT": {"px": c0["px"], "res": c0["px"] * 1.01, "sup": c0["px"] * 0.9}}         # yesterday's close and its levels
prev["coins"]["SOL-USDT"]["rng"] = {"4h": {"lo": c0["px"] * 0.98, "hi": c0["px"] * 1.02, "w": 2.0, "t": T1E}}
prev["mkt"].update(trend="side", vk="normal", fng=30, season="mix", rng={"4h": {"lo": 9.0, "hi": 11.0}})
new["mkt"].update(trend="down", vk="storm", fng=18, season="alt", beat=9, rsn=11)
rng_prev = {s: c.get("rng") for s, c in prev["coins"].items()}
cdbu = {"c1": {"BTC-USDT": {"d": [[T1E - 3600, 1, 1, 1, 100.0, 1], [T1E, 1, 1, 1, 103.5, 1]]},
               "SOL-USDT": {"d": [[T1E - 4 * 3600 + k * 3600, 1, 1, 1, 20.0 - k, 1] for k in range(5)]}}}
SCX = {"crash": {"on": True, "t": T4E, "k": 6, "n": 12}, "c": {"BTC-USDT": {"1H": {"e1": ["W-surge:1"]}}}}
ALL = {k: "now" for k in m.AN_TY}
F = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], ALL, SCX, LVD, cdbu)
tys = sorted({f["ty"] for k, f in F})
ok(f"④ what changed becomes a notice — all {len(tys)} fact types (the group types 🧩 come from the groups): {' · '.join(tys)}",
   tys == sorted(k for k in m.AN_TY if not k.startswith("g_")) and "tend" not in m.AN_TY, [(k, f["ln"][:40]) for k, f in F])
L = {f["ty"]: f["ln"] for k, f in F}
ok(f"④ plain words with the numbers: «{L['trend']}» · «{L['out'][:60]}…» · «{L['lvl'][:60]}…»",
   L["trend"].startswith("📈 الاتجاه اليومي أصبح صاعداً") and "صعد أكثر من المتوقع" in L["out"] and "فوق المدى المتوقع للساعات الأربع" in L["out"]
   and "اخترق المقاومة" in L["lvl"] and "بإغلاق اليوم" in L["lvl"] and "الحجم ×2.6" in L["lvl"] and "حجم تداول غير عادي: ×2.6" in L["vol"], L)
ok(f"④ the market: «{L['mtrend'][:50]}…» · «{L['season'][:55]}…» · «{L['fng']}»", L["mtrend"].startswith("📉 السوق: اتجاه البيتكوين اليومي أصبح هابطاً")
   and L["season"].startswith("🪙 السيولة تتجه إلى العملات البديلة: 9 من 11 عملة") and L["fng"] == "😨 مزاج السوق: خوف شديد (18 من 100)" and L["storm"].startswith("🎢 هاج السوق"), L)
ok(f"④ 🔴 urgent: «{L['wave'].splitlines()[0]}» (6 of 12 · Bitcoin +3.5% in an hour · your coins in 4 hours) · «{L['surge'].splitlines()[0]}» · «{L['bstorm'].splitlines()[0]}»",
   "6 من 12 عملة" in L["wave"] and "البيتكوين: +3.5% خلال ساعة" in L["wave"] and "من عملاتك (4 ساعات): SOL -20.0%" in L["wave"]
   and L["surge"].startswith("🚀 صعود جماعي") and L["bstorm"].startswith("⚡ البيتكوين يتحرك بعنف: +3.5% خلال ساعة") and "كان 9 – 11" in L["bstorm"]
   and all(f["urg"] for k, f in F if f["ty"] in ("wave", "surge", "bstorm")), L)
lat = [f["ln"] for k, f in F if re.search(r"[A-Za-z]{2,}", f["ln"].replace("SOL", ""))]
ok("④ no Latin words in any notice (only the coin's own name)", not lat, lat)
F0 = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], {k: "off" for k in m.AN_TY}, SCX, LVD, cdbu)
FV = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], {}, SCX, LVD, cdbu)
lvd = {f["ty"]: f["lv"] for k, f in FV}
ok("④ ⛔ every type off ⇒ nothing at all · the defaults: 📲 for the trend, breakouts, out of range, volume, the market's trend and storms, the urgent · "
   "👁 for vs Bitcoin, accumulation, money between Bitcoin and the alts, fear & greed", F0 == [] and lvd["rs"] == lvd["ad"] == lvd["season"] == lvd["fng"] == "view"
   and all(lvd[k] == "now" for k in ("trend", "lvl", "out", "vol", "mtrend", "storm", "wave", "surge", "bstorm")), lvd)
Fh = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], ALL, None, None, cdbu)
ok("④ a breakout counts only on the daily close (yesterday's levels)", not any(f["ty"] == "lvl" for k, f in Fh), [f["ty"] for k, f in Fh])

# ④ delivery — cards
CFG = dict(m.sg_cfg(), quiet=None, ch="both", cap=12, on=True)


def fk(sym, ty, ln, lv="now", rng=None):
    return {"sym": sym, "ty": ty, "lv": lv, "urg": m.AN_TY[ty][2] == "urgent", "ln": ln, "t": ln, "b": "", **({"rng": rng} if rng else {})}


SENT.clear()
st = {}
out = m._sg_deliver([fk("SOL-USDT", "out", "⚡ صعد أكثر من المتوقع", rng="🔮 المتوقع غداً: بين 24.70 و27.70 (صدق هذا المدى 81% من 212 مرة)"),
                     fk("SOL-USDT", "vol", "📊 حجم تداول غير عادي: ×2.6"), fk("XRP-USDT", "lvl", "🧱 كسر الدعم 2.10 بإغلاق اليوم"),
                     fk("SOL-USDT", "rs", "💪 أصبحت أقوى من البيتكوين", lv="view"), fk("السوق", "mtrend", "📈 السوق: اتجاه البيتكوين اليومي أصبح صاعداً")], st, CFG, float(NOW))
tg = list(SENT)
T0 = tg[0] if tg else ""
ok(f"④ one message for the round: a card per coin (SOL with its two facts + 🔮 tomorrow) · XRP · the market — «{T0[:80]}…»", len(tg) == 1
   and T0.startswith("📈 السوق — تنبيهات جديدة (3)") and "📈 SOL — حدث الآن\n⚡ صعد أكثر من المتوقع\n📊 حجم تداول غير عادي: ×2.6\n🔮 المتوقع غداً" in T0
   and "📈 XRP — حدث الآن\n🧱 كسر الدعم" in T0 and "📈 السوق: اتجاه البيتكوين" in T0, SENT)
ok("④ 👁 «أصبحت أقوى من البيتكوين» is in the window's log only (not sent) · the log says what reached you", "أقوى من البيتكوين" not in T0
   and [x["st"] for x in st["log"] if x["ty"] == "rs"] == ["view"] and {x["st"] for x in st["log"] if x["ty"] != "rs"} == {"sent"}, st["log"])
SENT.clear()
m._sg_deliver([fk("SOL-USDT", "vol", "📊 حجم تداول غير عادي مرة أخرى")], st, CFG, float(NOW + 3600))
m._sg_deliver([fk("SOL-USDT", "trend", "📉 الاتجاه اليومي أصبح هابطاً")], st, CFG, float(NOW + 7200))
ok("④ ⏱ SOL's next card waits 6 hours (nothing sent an hour later) · unless its daily trend turned (sent at once)",
   len(SENT) == 1 and "هابطاً" in SENT[0] and st["log"][1]["st"] == "cool", (SENT, [x["st"] for x in st["log"][:3]]))
SENT.clear()
st2 = {}
m._sg_deliver([fk("SOL-USDT", "out", "⚡ نزل أكثر من المتوقع"), fk("السوق", "wave", "🌊 انهيار في السوق كله الآن\nهبطت 6 من 12 عملة"),
               fk("السوق", "bstorm", "⚡ البيتكوين يتحرك بعنف: -3.4% خلال ساعة")], st2, dict(CFG, quiet=[0, 23]), float(NOW))
ok("④ 🔴 urgent in quiet hours: sent at once as ONE market message · SOL's own card stopped in that round (🌊 in the log)",
   len(SENT) == 1 and SENT[0].startswith("🌊 انهيار في السوق كله الآن") and "يتحرك بعنف" in SENT[0] and "نزل أكثر من المتوقع" not in SENT[0]
   and [x["st"] for x in st2["log"] if x["ty"] == "out"] == ["storm"] and not st2.get("qq") and not st2.get("n"), (SENT, st2))
SENT.clear()
night = time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime(NOW)) + " 03:00", "%Y-%m-%d %H:%M"))
st3 = {}
m._sg_deliver([fk("SOL-USDT", "out", "⚡ صعد أكثر من المتوقع"), fk("XRP-USDT", "vol", "📊 حجم تداول غير عادي")], st3, dict(CFG, quiet=[0, 8]), night)
q_ok = not SENT and len(st3.get("qq") or []) == 2
m._sg_flush(st3, dict(CFG, quiet=[0, 8]), night + 6 * 3600)
ok("④ 🌙 quiet hours: the two cards wait · at 09:00 one message «🌙 تنبيهات السوق أثناء ساعات الهدوء (2)» with both cards",
   q_ok and len(SENT) == 1 and SENT[0].startswith("🌙 تنبيهات السوق أثناء ساعات الهدوء (2)\n\n📈 SOL — حدث الآن") and not st3.get("qq"), (SENT, st3))
SENT.clear()
st4 = {}
m._sg_deliver([fk(f"C{i}-USDT", "out", f"⚡ صعد أكثر من المتوقع {i}") for i in range(15)], st4, CFG, float(NOW))
m._sg_deliver([fk("ZZ-USDT", "out", "⚡ أخرى")], st4, CFG, float(NOW + 60))
m._sg_deliver([fk("السوق", "bstorm", "⚡ البيتكوين يتحرك بعنف")], st4, CFG, float(NOW + 120))
tg4 = list(SENT)
ok("④ the daily cap: 12 cards of 15 + «🔕 بلغت تنبيهات السوق حدّها اليوم (12)» · nothing more that day · the urgent still reaches you",
   len(tg4) == 2 and tg4[0].startswith("📈 السوق — تنبيهات جديدة (12)") and "🔕 بلغت تنبيهات السوق حدّها اليوم (12)" in tg4[0] and "📈 C11 —" in tg4[0] and "📈 C12 —" not in tg4[0]
   and tg4[1].startswith("⚡ البيتكوين") and sum(1 for x in st4["log"] if x["st"] == "cap") == 4, tg4)

# ⑤ the tick end to end
for f in (m.AN_FILE, m.SG_FILE, m.GP_FILE, os.path.join(m.SG_DIR, "catalog.json")):
    try:
        os.remove(f)
    except Exception:
        pass
m.MKT_COINS = tuple(COINS)
m.SG_UNI = len(COINS)
json.dump({"ticker_coins": ["SOL", "XRP"]}, open(m.APP_CFG, "w"))


def fake_cache(sym, db, sec, bar, ib, maxn):
    src = CDB[sec].get(sym)
    if not src:
        return [], None
    db.setdefault(sec, {})[sym] = {"d": [list(r) for r in src["d"]]}
    return db[sec][sym]["d"], None


m._fc_cache = fake_cache
m._fc_db = lambda: FDB
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump({"c1": {}, "c4": {}, "c": {}}, open(m.SG_CFILE, "w"))
m._SG.update(cidx=None, build=None)
os.environ["HOLY_SIG_THREAD"] = "1"
t_a = float(T1E + 3600 + 100)
SENT.clear()
m.sg_tick(now=t_a)
A1 = m._an_load()
ok("⑤ the first tick: the scan carried the market now (SOL · XRP · the market) · nothing notified (nothing to compare yet) · no old catalog built",
   A1.get("now") and "SOL-USDT" in A1["now"]["coins"] and A1["now"].get("mkt") and not SENT and m._SG.get("build") is None and not os.path.exists(os.path.join(m.SG_DIR, "catalog.json")) and not hasattr(m, "sg_build"),
   (bool(A1.get("now")), SENT[:2], m._SG.get("build")))
for s in COINS:                                              # the next hour: SOL jumps 9% — far outside its 4-hour range
    last = CDB["c1"][s]["d"][-1]
    jump = 1.09 if s == "SOL-USDT" else 1.0005
    CDB["c1"][s]["d"].append([last[0] + 3600, last[4], last[4] * jump * 1.002, last[4] * 0.999, last[4] * jump, 50.0])
m.sg_tick(now=t_a + 3600)
got = [t for t in SENT if "SOL" in t]
no_lvl = not any("المقاومة" in t or "الدعم" in t for t in SENT)
ok(f"⑤ the next hour: SOL's 9% jump outside its range reaches Telegram (no «breakout» before the day closes) — «{(got or [''])[0][:90]}»", got and any("أكثر من المتوقع" in t for t in got) and no_lvl, SENT)
n_sent = len(SENT)
for s in COINS:
    last = CDB["c1"][s]["d"][-1]
    CDB["c1"][s]["d"].append([last[0] + 3600, last[4], last[4] * 1.001, last[4] * 0.999, last[4] * 1.0003, 42.0])
m.sg_tick(now=t_a + 7200)
ok("⑤ the same event is not sent again", not any("أكثر من المتوقع" in t and "SOL" in t for t in SENT[n_sent:]), SENT[n_sent:])
n_sent = len(SENT)
for s in COINS:                                              # a strong move: SOL jumps 9% again an hour later (outside its new range too)
    last = CDB["c1"][s]["d"][-1]
    jump = 1.09 if s == "SOL-USDT" else 1.0002
    CDB["c1"][s]["d"].append([last[0] + 3600, last[4], last[4] * jump * 1.002, last[4] * 0.999, last[4] * jump, 50.0])
m.sg_tick(now=t_a + 3 * 3600)
A4 = m._an_load()
ok("⑤ a strong move that keeps going (SOL +9% again the next hour) ⇒ «صعد أكثر من المتوقع» once a day, not every hour",
   not any("أكثر من المتوقع" in t and "SOL" in t for t in SENT[n_sent:]) and "out|SOL-USDT|u" in A4["sent"], (SENT[n_sent:], list(A4["sent"])[:6]))

# ⑥ the API · the settings
V = m.an_view()
ok("⑥ /api/market's data: your coins (SOL · XRP) with their lines and ranges · the market · the ranges' record · the three horizons",
   [c["sym"] for c in V["coins"]] == ["SOL-USDT", "XRP-USDT"] and V["mkt"] and V["coins"][0]["rng"] and [h[0] for h in V["hz"]] == ["4h", "1d", "1w", "1m", "3m"], {k: V.get(k) for k in ("mine", "hz")})
c = m.sg_cfg()
ok("⑥ settings: each type at its default level (📲 or 👁) · the daily cap inside (12) · no daily summary", c["alv"] == {k: x[3] for k, x in m.AN_TY.items()}
   and c["cap"] == 12 and "sum" not in c, c)
r = m.sg_set({"alv": {"vol": "view", "fng": "now", "rs": "off", "nope": "now", "trend": "loud"}})
c2 = m.sg_cfg()
ok(f"⑥ «{r['msg']}» — 📊 to 👁 · 😨 to 📲 · 💪 off · an unknown type or level ignored", c2["alv"]["vol"] == "view" and c2["alv"]["fng"] == "now" and c2["alv"]["rs"] == "off"
   and c2["alv"]["trend"] == "now" and "nope" not in c2["alv"] and c2["atypes"]["rs"] is False and "تنبيهات السوق" in r["msg"], c2["alv"])
cfg0 = json.load(open(m.APP_CFG))
cfg0.pop("an_lv", None)
cfg0["an_types"] = {"ad": False}
json.dump(cfg0, open(m.APP_CFG, "w"))
ok("⑥ an old setting (v3.36.75 «🧲 off») becomes ⛔ · the rest keep their defaults", m.sg_cfg()["alv"]["ad"] == "off" and m.sg_cfg()["alv"]["vol"] == "now", m.sg_cfg()["alv"])

def port():
    s_ = socket.socket(); s_.bind(("127.0.0.1", 0)); p_ = s_.getsockname()[1]; s_.close(); return p_


Pt = port()
srv = m.ThreadingHTTPServer(("127.0.0.1", Pt), m.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
try:
    with _real_urlopen(f"http://127.0.0.1:{Pt}/api/market", timeout=20) as rr:
        jm = json.loads(rr.read().decode("utf-8"))
except Exception as ex:
    jm = {"err": repr(ex)}
finally:
    srv.shutdown()
ok("⑥ GET /api/market answers", jm.get("ok") and len(jm.get("coins") or []) == 2, str(jm)[:300])
blob = open(m.AN_FILE, encoding="utf-8").read().lower()
ok("⑦ no order was sent · no key, secret or passphrase in the market file", not ORD and not any(w in blob for w in ("api_key", "secret", "passphrase")), ORD)

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_market: {sum(res)}/{len(res)} (the market now and next)")
sys.exit(0 if all(res) else 1)
