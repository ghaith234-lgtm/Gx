# 🏦 the new data (v3.36.77 · p142): derivatives (open interest · top traders · funding · the quarterly premium) · the Coinbase premium ·
#   the stablecoins · the US calendar. The owner (21-11): «وهذه ضيفها : بيانات العقود (التمويل، العقود المفتوحة، العلاوة الفصلية، مراكز
#   الكبار)، وعلاوة كوينبيس، والعملات المستقرة، وتقويم الأخبار الأمريكية»
#   A closed folder (no network · no keys): the public answers are STUBBED (OKX · Coinbase · DefiLlama), so every rule is checked exactly:
#   ① the fetchers: open interest and top traders page ~400 days back the first time (then one page) and keep their own column · funding
#     becomes a daily mean · the quarterly premium is annualised from the quarterly future vs its index · Coinbase daily closes (complete days
#     only) · the stablecoins' total · each waits for its schedule · a failed answer retries in half an hour · nothing is ever sent to OKX
#   ② the readings: top traders (follow) · funding and the quarterly premium (reverse) · open interest with the price · the Coinbase premium
#     · the stablecoins' week
#   ③ the events: the new members fire from the same _sg_series on the right days · 🗓️ M-cal fires on the candle BEFORE a high-impact release
#   ④ the members: 🏦 of the coin gets the derivatives · 🏦 of the market also the Coinbase premium and the stablecoins · 🎢 the calendar ·
#     the market-wide readings stay out of the coin groups · every new member has its neutral name (no Latin letters)
#   ⑤ 📈 the market now: the new lines (🇺🇸 · 💵 · 🏦 · 📆 · 🗓️) in plain words
#   ⑥ 🗓️ the notice ~30 minutes before a high-impact US release: once per release · not for a far or a medium one · ⛔ silences it ·
#     an English-only title becomes plain Arabic · the tick delivers it
#   python3 devtests/t_newdata.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, re, shutil, sys, tempfile, time

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

R = tempfile.mkdtemp(prefix="t_newdata_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_newdata", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_newdata", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
ORD = []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
m.tg_send = lambda *a, **k: True
time.sleep = lambda *a, **k: None
DAY = 86400
NOW = float(int(time.time()) // DAY * DAY + 5 * 3600)          # 05:00 UTC today
D0 = int(NOW) // DAY * DAY                                    # today's start
CALLS = []


def okx(path):
    CALLS.append(path)
    q = dict(x.split("=", 1) for x in path.split("?", 1)[1].split("&")) if "?" in path else {}
    end = int(q["end"]) // 1000 if "end" in q else D0 + DAY
    if "open-interest-history" in path or "top-trader" in path:
        if q.get("instId", "").startswith("NOPE"):
            return {"code": "0", "data": []}
        days = [end - k * DAY for k in range(1, 101)]
        days = [d for d in days if d >= D0 - 420 * DAY]
        if "open-interest" in path:
            return {"code": "0", "data": [[str(d * 1000), "1", str(1000.0 + (d - D0) / DAY), "1"] for d in days]}
        return {"code": "0", "data": [[str(d * 1000), str(1.0 + 0.001 * ((d - D0) // DAY))] for d in days]}
    if "funding-rate-history" in path:
        aft = int(q["after"]) // 1000 if "after" in q else D0 + 16 * 3600
        ts = [aft - k * 8 * 3600 for k in range(1, 101)]
        return {"code": "0", "data": [{"fundingTime": str(t * 1000), "realizedRate": str(0.0001 if (t // DAY) % 2 else 0.0003)} for t in ts]}
    if "instruments" in path:
        if "BTC-USD" in path and "USDT" not in path:
            return {"code": "0", "data": [{"alias": "this_week", "instId": "BTC-USD-W", "expTime": str((D0 + 5 * DAY) * 1000)},
                                          {"alias": "quarter", "instId": "BTC-USD-Q", "expTime": str(int(NOW + 73 * DAY) * 1000)}]}
        return {"code": "0", "data": []}
    if "market/ticker" in path:
        return {"code": "0", "data": [{"last": "101000"}]}
    if "index-tickers" in path:
        return {"code": "0", "data": [{"idxPx": "100000"}]}
    return None


HJ = []


def hj(url, *a, **k):
    HJ.append(url)
    if "coinbase" in url:
        e = int(time.mktime(time.strptime(url.split("end=")[1][:10], "%Y-%m-%d"))) - time.timezone
        return [[e - k_ * DAY, 1, 1, 1, 100.0 + k_, 1] for k_ in range(0, 291) if e - k_ * DAY >= D0 - 900 * DAY]
    if "stablecoins.llama.fi" in url:
        return [{"date": str(D0 - k_ * DAY), "totalCirculatingUSD": {"peggedUSD": 2.0e11 + 1e8 * (500 - k_)}} for k_ in range(500, -1, -1)]
    return None


m._okx_pub = okx
m._http_json = hj
db = {}
ch = [m._pro_oi(db, NOW, ["BTC", "NOPE"]), m._pro_top(db, NOW, ["BTC"]), m._pro_fund(db, NOW, ["BTC"]), m._pro_basis(db, NOW), m._pro_cbp(db, NOW), m._pro_stb(db, NOW)]
oi, top, fd = db["oi"]["BTC"]["d"], db["top"]["BTC"]["d"], db["fund"]["BTC"]["d"]
n_oi = sum(1 for c in CALLS if "open-interest" in c and "BTC" in c)
ok(f"① open interest and top traders: {len(oi)} and {len(top)} days the first time ({n_oi} pages of 100) · their own column (the coins: {oi[str(D0 - DAY)]}) · "
   f"a coin without contracts is marked", all(ch) and len(oi) >= 390 and len(top) >= 390 and n_oi == 4 and oi[str(D0 - DAY)] == 999.0
   and abs(top[str(D0 - DAY)] - 0.999) < 1e-9 and db["oi"]["NOPE"].get("na") is True, (len(oi), n_oi, list(oi.items())[:2]))
ok(f"① funding: the daily mean of the realised rate ({len(fd)} days · {fd.get(str(D0 - 2 * DAY))} · {fd.get(str(D0 - 3 * DAY))})",
   len(fd) >= 90 and {round(fd[str(D0 - 2 * DAY)], 6), round(fd[str(D0 - 3 * DAY)], 6)} == {0.0001, 0.0003}, list(fd.items())[:3])
b = db["basis"]["BTC"]["d"].get(str(D0))
ok(f"① the quarterly premium: the quarterly future (not the weekly) vs the index, annualised: {b}% (1% over 73 days ≈ 5.0%) · ETH without a quarterly ⇒ nothing, retry soon",
   b is not None and abs(b - 5.0) < 0.05 and not (db["basis"].get("ETH") or {}).get("d") and float(db["basis"]["ETH"]["ts"]) < NOW, db["basis"])
cb = db["cbp"]["d"]
ok(f"① Coinbase: {len(cb)} daily closes (years back the first time · complete days only — not today) · kept to the last {m.PRO_KEEP} days",
   len(cb) == m.PRO_KEEP and str(D0) not in cb and str(D0 - DAY) in cb and sum(1 for u in HJ if "coinbase" in u) >= 3, (len(cb), sorted(cb)[-2:]))
ok(f"① the stablecoins: {len(db['stb']['d'])} days of the total supply", len(db["stb"]["d"]) >= 500 and db["stb"]["d"][str(D0)] == 2.5e11, list(db["stb"]["d"].items())[-1:])
CALLS.clear()
HJ.clear()
again = [m._pro_oi(db, NOW + 3600, ["BTC"]), m._pro_top(db, NOW + 3600, ["BTC"]), m._pro_fund(db, NOW + 3600, ["BTC"]), m._pro_cbp(db, NOW + 3600), m._pro_stb(db, NOW + 3600)]
ok("① each waits for its schedule (an hour later: no request at all)", not any(again) and not CALLS and not HJ, (again, CALLS, HJ))
m._pro_oi(db, NOW + 13 * 3600, ["BTC"])
ok(f"① after 12 hours: one page only (the history is kept) — {len(CALLS)} request", len(CALLS) == 1 and len(db["oi"]["BTC"]["d"]) >= 390, CALLS)
m._okx_pub = lambda p: None
e = {}
dbf = {"oi": {"ETH": e}}
m._pro_oi(dbf, NOW, ["ETH"])
ok("① a failed answer retries in half an hour (not after 12 hours)", abs(float(dbf["oi"]["ETH"]["ts"]) - (NOW - m.PRO_EVERY["oi"] + 1800)) < 1, dbf)
m._okx_pub = okx

# ② the readings
up = [1.0 + 0.0 * i for i in range(89)]
ok("② the readings: top traders follow (crowded long ⇒ +1) · funding and the quarterly premium are reverse (crowded ⇒ −1) · a short history ⇒ nothing",
   m._pro_top_sig(up + [2.0], 89) == 1.0 and m._pro_top_sig([2.0 - 0.01 * i for i in range(89)] + [0.1], 89) == -1.0
   and m._pro_fund_sig([0.0001] * 89 + [0.001], 89) == -1.0 and m._pro_fund_sig([0.0001 + 0.000001 * i for i in range(89)] + [-0.001], 89) == 1.0
   and m._pro_basis_sig([5.0 + 0.01 * i for i in range(89)] + [30.0], 89) == -1.0 and m._pro_top_sig([1.0] * 10, 9) is None, "")
oiv = [[1000.0 + (i % 5), 100.0] for i in range(60)] + [[1000.0, 100.0], [1000.0, 100.0], [1000.0, 100.0], [1100.0, 103.0]]
oiw = [[1000.0 + (i % 5), 100.0] for i in range(60)] + [[1000.0, 100.0], [1000.0, 100.0], [1000.0, 100.0], [1100.0, 97.0]]
oif = [[1000.0 + (i % 5), 100.0] for i in range(60)] + [[1000.0, 100.0], [1000.0, 100.0], [1000.0, 100.0], [900.0, 97.0]]
ok("② open interest with the price: new money with a rising price ⇒ +1 · with a falling price ⇒ −1 · money leaving ⇒ nothing",
   m._pro_oi_sig(oiv, len(oiv) - 1) == 1.0 and m._pro_oi_sig(oiw, len(oiw) - 1) == -1.0 and m._pro_oi_sig(oif, len(oif) - 1) == 0.0, "")
stb = [1e11 * (1 + 0.0005 * i) for i in range(400)]
stb2 = stb[:-1] + [stb[-8] * 1.02]
ok("② the Coinbase premium (high ⇒ +1 · low ⇒ −1) · the stablecoins' week (a jump above the year's 80% ⇒ +1)",
   m._mkt_cbp_sig([0.0] * 89 + [0.3], 89) == 1.0 and m._mkt_cbp_sig([0.0 + 0.001 * i for i in range(89)] + [-0.3], 89) == -1.0
   and m._mkt_stb_sig(stb2, len(stb2) - 1) == 1.0, "")

# ③ the events from a candles file and the readings
N = 420
rows = []
p = 100.0
for i in range(N):
    t = D0 - (N - i) * DAY
    c = p * (1 + 0.01 * math.sin(i / 5.0))
    rows.append([t, p, max(p, c) * 1.01, min(p, c) * 0.99, c, 1000.0])
    p = c
cdb = {"c": {"BTC-USDT": {"d": rows}}}
pdb = json.loads(json.dumps(db))
TS = D0 - 10 * DAY                                             # the spike day for the top traders
for k in list(pdb["top"]["BTC"]["d"]):
    pdb["top"]["BTC"]["d"][k] = 1.0 - 0.0001 * ((int(k) - D0) // DAY)
pdb["top"]["BTC"]["d"][str(TS)] = 5.0
EV = D0 - 20 * DAY + 14 * 3600                                 # a high-impact release at 14:00, 20 days ago
pdb["cal"] = {"ev": [{"t": EV, "ti": "CPI m/m", "im": "h"}, {"t": D0 - 30 * DAY + 3600, "ti": "Retail", "im": "m"}]}
ctx = m._sg_ctx("BTC-USDT", rows, pdb, m._sg_mkt(pdb, {}, cdb), None, {})
Dd, Ed = m._sg_events(rows, True, ctx, t0=210, dx=DAY)
tops = [Dd["T"][i] for i in Ed.get(("P-top", 1), [])]
cal1 = [Dd["T"][i] for i in Ed.get(("M-cal", 1), [])]
have = sorted({c for (c, s) in Ed if c in ("P-oi", "P-top", "P-fund", "M-cbp", "M-stb", "M-cal")})
ok(f"③ the events: the new members fire from the same readings ({' · '.join(have)}) · the top traders' spike day reads on its own daily candle "
   f"({[time.strftime('%m-%d', time.gmtime(t)) for t in tops[-1:]]}) · 🗓️ M-cal on the day BEFORE the release ({[time.strftime('%m-%d', time.gmtime(t)) for t in cal1]})",
   TS in tops and cal1 == [EV // DAY * DAY - DAY] and {"P-top", "M-cal", "M-cbp"} <= set(have), (have, tops[-3:], cal1, EV))
hrows = [[D0 - (300 - i) * 3600, 100.0, 101.0, 99.0, 100.0 + math.sin(i / 3.0), 50.0] for i in range(300)]
pdb2 = dict(pdb, cal={"ev": [{"t": D0 - 30 * 3600 + 1800, "ti": "FOMC", "im": "h"}]})
ctxh = m._sg_ctx("BTC-USDT", rows, pdb2, m._sg_mkt(pdb2, {}, cdb), None, {})
Dh, Eh = m._sg_events(hrows, False, ctxh, t0=210, dx=3600)
calh = [Dh["T"][i] for i in Eh.get(("M-cal", 1), [])]
ok(f"③ 🗓️ on the hour: M-cal fires on the candle that closes just before the hour of the release ({[time.strftime('%d %H:%M', time.gmtime(t)) for t in calh]})",
   calh == [D0 - 30 * 3600 - 3600], (calh, D0 - 30 * 3600 + 1800))

# ④ the members
nm = {c: m.GP_NM.get(c) for c in ("P-oi", "P-top", "P-fund", "P-basis", "M-cbp", "M-stb", "M-cal")}
ok(f"④ the members: 🏦 coin {[c for c in m.gp_members('c_pro')]} · 🏦 market + {[c for c in m.gp_members('m_pro') if c.startswith('M-')]} · 🎢 + M-cal · "
   f"no market-wide reading in a coin group · neutral names {list(nm.values())}",
   {"P-oi", "P-top", "P-fund", "P-basis", "P-ls", "P-tk"} <= set(m.gp_members("c_pro")) and {"M-cbp", "M-stb", "P-oi"} <= set(m.gp_members("m_pro"))
   and "M-cal" in m.gp_members("m_vol") and not any(c.startswith(("M-", "W-")) for g in m.GP_GROUPS if g.startswith("c_") for c in m.gp_members(g))
   and all(v and not re.search(r"[A-Za-z]", v) for v in nm.values()) and all(m._sg_plain(c) for c in nm), nm)

# ⑤ 📈 the market now
L = m._an_newdata(pdb, cdb)
txt = " | ".join(x[1] for x in L)
ok(f"⑤ 📈 the market now: {len(L)} new lines — «{txt[:240]}»", [x[0] for x in L] == ["🇺🇸", "💵", "🏦", "📆"] and "علاوة كوينبيس" in txt and "مليار دولار" in txt
   and "التمويل" in txt and "العقود المفتوحة" in txt and "مراكز الكبار" in txt and "سنوياً" in txt and not re.search(r"[A-Za-z]{2,}", txt), L)
pdb3 = dict(pdb, cal={"ev": [{"t": int(NOW) + 3 * 3600, "ti": "Non-Farm Employment Change", "im": "h"}]})
L3 = m._an_newdata(pdb3, cdb)
ok(f"⑤ 🗓️ the next high-impact US release in its own line: «{L3[-1][1] if L3 else ''}»", L3 and L3[-1][0] == "🗓️" and "أقرب خبر أمريكي مهم" in L3[-1][1], L3)

# ⑥ 🗓️ the notice before a release
st = {}
cal = {"cal": {"ev": [{"t": int(NOW) + 28 * 60, "ti": "Non-Farm Employment Change", "im": "h"}, {"t": int(NOW) + 2 * 3600, "ti": "CPI m/m", "im": "h"},
                      {"t": int(NOW) + 20 * 60, "ti": "Pending Home Sales", "im": "m"}, {"t": int(NOW) + 25 * 60, "ti": "Some Speech", "im": "h"}]}}
F1 = m._cal_facts(cal, st, NOW, {})
F2 = m._cal_facts(cal, st, NOW + 120, {})
F0 = m._cal_facts(cal, {}, NOW, {"cal": "off"})
ln = [f["ln"] for f in F1]
ok(f"⑥ 🗓️ ~30 minutes before: «{(ln or [''])[0][:110]}» · the far one and the medium one wait · once per release · ⛔ silences it",
   len(F1) == 2 and not F2 and not F0 and all(f["ty"] == "cal" and f["sym"] == "السوق" and f["lv"] == "now" for f in F1) and "بعد 28 دقيقة" in ln[0] + ln[1], F1)
ok("⑥ plain words: a known release by its Arabic name · an English-only title becomes «خبر اقتصادي أمريكي عالي التأثير» · no Latin letters",
   any("خبر اقتصادي أمريكي عالي التأثير" in x for x in ln) and not any(re.search(r"[A-Za-z]", x) for x in ln), ln)
m.save_json_atomic(m.PRO_FILE, cal)
m._sg_universe = lambda: []
m._sg_cidx = lambda cdb=None: {"c": {}, "c4": {}, "c1": {}}
os.environ["HOLY_SIG_THREAD"] = "1"
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump({"c": {}, "c4": {}, "c1": {}}, open(m.SG_CFILE, "w"))
SENT = []
m._sg_tg = lambda text, cfg: SENT.append(text) or True
m.sg_tick(now=NOW, send=True)
lg = [x for x in (m._sg_st().get("log") or []) if x.get("ty") == "cal"]
ok(f"⑥ the tick delivers it (📲 «{(SENT or [''])[0][:70]}…») and logs it ({len(lg)}) · no order", SENT and "🗓️" in SENT[0] and len(lg) == 2 and not ORD, (SENT, lg))

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_newdata: {sum(res)}/{len(res)} (the new data)")
sys.exit(0 if all(res) else 1)
