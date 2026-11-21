# 📈 the market now and next (v3.36.75 · p130 — the new analyst rebuilt from scratch after checks 13 and 14). The owner (21-11): «اريد يقلي
#   شديصير بالسوق بالحاضر وشراح يصير للسوق بشكل عام وبالعملات بشكل خاص».
#   A closed folder (no network · no keys · synthetic candles):
#   ① 🔎 the present: the market's lines (trend and since when · coins above their mean · alts vs Bitcoin · calm/stormy · fear & greed) and
#      every coin's (daily trend · short term · vs Bitcoin and rank · volatility · unusual volume · support / resistance / busiest area ·
#      accumulation · overbought) — plain Arabic, no Latin letters
#   ② 🔮 the range for 4 hours · tomorrow · the week (80%): the price inside · wider with time · ③ its live record: bands issued only at their
#      frame's close (no overlap) and graded at their end (inside ⇒ ✅ · outside ⇒ ❌ · Bitcoin apart)
#   ④ the facts notifications: trend change · vs Bitcoin · unusual volume · support break / resistance breakout · outside the range ·
#      accumulation · the market's trend · stormy · crash · extreme fear — each type off ⇒ nothing · once per event (20 hours)
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
ok(f"② the range for 4 hours · tomorrow · the week around the price ({SOL['px']:.4g}): ±{rg['4h']['w']}% · ±{rg['1d']['w']}% · ±{rg['1w']['w']}% — wider with time",
   set(rg) == {"4h", "1d", "1w"} and all(rg[k]["lo"] < SOL["px"] < rg[k]["hi"] for k in rg) and rg["4h"]["w"] < rg["1d"]["w"] < rg["1w"]["w"]
   and M.get("rng") and M["rng"]["4h"]["lo"] < M["btc"] < M["rng"]["4h"]["hi"], rg)

# ③ the live record of the range
A = m._an_load()
m._an_issue(A, P, ["4H"], float(NOW))
k4 = {p[1] for p in A["pend"]}
A2 = m._an_load()
m._an_issue(A2, P, ["1D"], float(NOW))
k1 = {p[1] for p in A2["pend"]}
ok("③ bands are issued only at their frame's close: the 4-hour close ⇒ «4h» only · the daily close ⇒ «1d» (and «1w» on Mondays)", k4 == {"4h"} and "1d" in k1 and "4h" not in k1, (k4, k1))
t_end = T1E - 3600
A3 = {"v": 1, "rec": {}, "pend": [["SOL-USDT", "4h", 9.0, 11.0, t_end], ["XRP-USDT", "4h", 9.0, 11.0, t_end], ["BTC-USDT", "1d", 1.0, 100.0, t_end],
                                   ["ETH-USDT", "1w", 1.0, 2.0, NOW + 86400], ["DOT-USDT", "1d", 1.0, 2.0, NOW - 5 * 86400]], "sent": {}}
cdb3 = {"c1": {"SOL-USDT": {"d": [[t_end - 3600, 1, 1, 1, 10.5, 1]]}, "XRP-USDT": {"d": [[t_end - 3600, 1, 1, 1, 12.0, 1]]},
               "BTC-USDT": {"d": [[t_end - 3600, 1, 1, 1, 50.0, 1]]}}}
m._an_grade(A3, cdb3, float(NOW))
ok("③ graded at the band's end: SOL inside ⇒ ✅ · XRP outside ⇒ ❌ · Bitcoin also counted apart · one still running waits · one without its candle for days dropped",
   A3["rec"].get("4h") == [1, 1] and A3["rec"].get("1d") == [1, 0] and A3["rec"].get("btc_1d") == [1, 0] and [p[0] for p in A3["pend"]] == ["ETH-USDT"], A3)

# ④ the facts
prev = json.loads(json.dumps(P))
new = json.loads(json.dumps(P))
c0, c1 = prev["coins"]["SOL-USDT"], new["coins"]["SOL-USDT"]
c0.update(trend="side", rs7=-1.0, rs30=-2.0, volx=1.0, ad="flat")
c1.update(trend="up", rs7=2.0, rs30=3.0, volx=2.6, ad="acc")
c1["px"] = c0["px"] * 1.05
LVD = {"SOL-USDT": {"px": c0["px"], "res": c0["px"] * 1.01, "sup": c0["px"] * 0.9}}         # yesterday's close and its levels
prev["coins"]["SOL-USDT"]["rng"] = {"4h": {"lo": c0["px"] * 0.98, "hi": c0["px"] * 1.02, "w": 2.0, "t": T1E}}
prev["mkt"].update(trend="side", vk="normal", fng=30)
new["mkt"].update(trend="down", vk="storm", fng=18)
rng_prev = {s: c.get("rng") for s, c in prev["coins"].items()}
F = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], {}, {"on": True, "t": T4E, "k": 6, "n": 12}, LVD)
tys = sorted({b["ty"] for k, b in F})
ok(f"④ what changed becomes a notice: {' · '.join(tys)}", tys == sorted(["trend", "rs", "vol", "lvl", "out", "ad", "mtrend", "storm", "wave", "fng"]), [(k, b["t"]) for k, b in F])
tt = {b["ty"]: b["t"] for k, b in F}
ok(f"④ in plain words: «{tt['out']}» · «{tt['lvl']}» · «{tt['trend']}» · «{tt['wave']}»", "أكثر من المتوقع" in tt["out"] and "اخترق المقاومة" in tt["lvl"]
   and "الاتجاه اليومي أصبح صاعد" in tt["trend"] and "انهيار" in tt["wave"] and "خوف شديد" in tt["fng"], tt)
F0 = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], {k: False for k in m.AN_TY}, {"on": True, "t": T4E, "k": 6, "n": 12}, LVD)
Fh = m._an_facts(prev, new, rng_prev, ["SOL-USDT"], {}, None, None)
ok("④ every type off ⇒ nothing (each one is the owner's switch)", F0 == [], F0)
ok("④ a support break or resistance breakout counts only on the daily close (an hour's spike above it is not a breakout)",
   not any(b["ty"] == "lvl" for k, b in Fh) and any(b["ty"] == "lvl" and "أغلق اليوم على" in b["b"] for k, b in F), [b["t"] for k, b in Fh])

# ⑤ the tick end to end
for f in (m.AN_FILE, m.SG_FILE, m.SB_FILE, m.SG_CAT):
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
   A1.get("now") and "SOL-USDT" in A1["now"]["coins"] and A1["now"].get("mkt") and not SENT and m._SG.get("build") is None and not os.path.exists(m.SG_CAT),
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
   [c["sym"] for c in V["coins"]] == ["SOL-USDT", "XRP-USDT"] and V["mkt"] and V["coins"][0]["rng"] and [h[0] for h in V["hz"]] == ["4h", "1d", "1w"], {k: V.get(k) for k in ("mine", "hz")})
c = m.sg_cfg()
ok("⑥ settings: every facts type on by default · the daily cap inside (12) · no daily summary", all(c["atypes"].values()) and set(c["atypes"]) == set(m.AN_TY)
   and c["cap"] == 12 and c["sum"] is None, c)
r = m.sg_set({"atypes": {"vol": False, "nope": False}})
c2 = m.sg_cfg()
ok(f"⑥ «{r['msg']}» — a type turned off is saved · an unknown one ignored", c2["atypes"]["vol"] is False and "nope" not in c2["atypes"] and "تنبيهات السوق" in r["msg"], c2["atypes"])


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
