# 🧩 the indicator groups (v3.36.77 · p138 — 🪙 coin and 🌐 market groups · each group = one job = one notification · tested on history).
#   The owner (21-11): «قسمين للعملات وللسوق … كل مجموعه تختص باشعار … تصنف التجارب على اختباراتك ما نبدي من الجديد … يكون المصدر مفتوح …
#   عندما ياتي توليفة او مؤشر تنضاف مع شغل جماعتها ويختبر قبل ما يدخل … الاشعارات فقط ساعه ٤ ساعات يوم»
#   A closed folder (no network · no keys) with PLANTED firings, so every rule is checked exactly:
#   ① no peeking: a member becomes a champion only from results already known (≥ 30 different days of results before its first notice)
#   ② the good member (75%) becomes a champion · a coin flip never · a move under 0.2% is not counted
#   ③ at most two champions per group (three good «trend» members ⇒ the two best · the third is ✅ proven but waits)
#   ④ the safety gap: a champion that turns bad stays until it falls under the usual + 2% — then it is silent
#   ⑤ combos: two members that are coin flips alone but right 85% together ⇒ the combo «a+b» is a champion
#   ⑥ the usual (base) removes the market's drift: in a market that rises 70% of the time «always up» (70%) is NOT a champion · a member
#     right 90% is
#   ⑦ the «big move» job: no side · its usual = the share of big moves · a member before big moves 60% (usual ~15%) is a champion
#   ⑧ the «vs Bitcoin» job: graded by the coin's move minus Bitcoin's · Bitcoin itself is never graded on it
#   ⑨ champions on opposite sides of the same candle ⇒ nothing is sent for that coin
#   ⑩ gp_pack for the dashboard (record · usual · members with their state · untested members 🧪 · per coin of yours)
#   ⑪ the live check (gp_now) gives exactly what the history walk would have sent on the last candle (one function for both)
#   ⑫ open to new members: a new indicator of the «trend» family joins «📈 الاتجاه» by itself, is tested, and becomes a champion when it earns it
#   ⑬ gp_build end to end (three frames · 🪙 + 🌐 · market-wide readings on the whole history) · no network · no orders
#   ⑭ the notices (text · your coins only · the market · 📲 only for a proven group · ⛔ · dedupe key) · one notice type per group
#   ⑮ the tick end to end (the first tick builds · the next hour does not · a new coin needs a build · /api/groups · ⚙️ · 🔮)
#   ⑯ a daily derivatives reading is read only after its day has closed (no hourly candle peeks at it)
#   python3 devtests/t_groups.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, re, shutil, sys, tempfile, time

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

R = tempfile.mkdtemp(prefix="t_groups_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_groups", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_groups", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
ORD = []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
DAY = 86400
rnd = random.Random(5)
N, COINS = 400, [f"C{j}-USDT" for j in range(12)]
T0 = (int(time.time()) // DAY - N) * DAY
NOC = {"combo": 0}


def build(gen, coins=COINS, n=N, dx=DAY, t0=T0):
    """gen(sym, i) ⇒ ({code: side} fired on candle i, the move of candle i+1) ⇒ F = {sym: (candles, events)}"""
    F = {}
    for sym in coins:
        C, T, E = [100.0], [t0], {}
        for i in range(n):
            f, mv = gen(sym, i)
            for code, side in f.items():
                E.setdefault((code, side), []).append(i)
            if i < n - 1:
                C.append(C[-1] * (1 + mv))
                T.append(t0 + (i + 1) * dx)
        F[sym] = ({"T": T, "C": C, "O": list(C), "n": n}, E)
    return F


def mag():
    return 0.01 + 0.02 * rnd.random()


def pick(p, side):
    return side if rnd.random() < p else -side


# ── scenario A (the direction job · singles only): three good «trend» members · a coin flip · a «momentum» member that turns bad
GOOD = {"O-trend": 0.78, "O-st": 0.74, "O-adx": 0.70}
FLIP, TURN = "09", "O-macd"


def gen_a(sym, i):
    r, s = rnd.random(), rnd.choice((1, -1))
    if r < 0.18:
        f = {"O-trend": s}
    elif r < 0.30:
        f = {"O-st": s}
    elif r < 0.40:
        f = {"O-adx": s}
    elif r < 0.55:
        f = {FLIP: s}
    elif r < 0.70:
        f = {TURN: s}
    else:
        return {}, mag() * rnd.choice((1, -1))
    c = next(iter(f))
    p = GOOD.get(c) or ((0.8 if i < 200 else 0.2) if c == TURN else 0.5)
    return f, mag() * pick(p, s)


FA = build(gen_a)
WA = m.gp_walk(FA, "coin", "1D", p=NOC, keep=COINS[:2])
recT, recM = WA["rec"]["c_trend"], WA["rec"]["c_mom"]
acc = {c: round(r[0] / max(1, r[0] + r[1]), 3) for c, r in list(recT.items()) + list(recM.items())}
first = {}
for g in WA["sent"]:
    for t, sym, s, r_, pb, cs in WA["sent"][g]:
        for c in cs:
            first.setdefault(c, t)
days_before = {}
for c, t1 in first.items():
    dd = set()
    for sym, (D, E) in FA.items():
        for s in (1, -1):
            for i in E.get((c, s), []):
                if i + 1 < D["n"] and D["T"][i + 1] <= t1 and abs(D["C"][i + 1] / D["C"][i] - 1) >= m.GP_MV:
                    dd.add(D["T"][i] // DAY)
    days_before[c] = len(dd)
ok(f"① no peeking: every champion's first notice came after ≥ 30 different days of its results ({days_before})",
   days_before and all(v >= 30 for v in days_before.values()), days_before)
ok(f"② the good members are champions ({WA['champ']['c_trend']}) · the coin flip never ({acc.get(FLIP)}) · records {acc}",
   "O-trend" in WA["champ"]["c_trend"] and FLIP not in first and acc["O-trend"] > 0.7, (WA["champ"], acc))
ok(f"③ at most two champions per group: three good «trend» members ⇒ the two best ({WA['champ']['c_trend']}) · the third is proven but waits",
   WA["champ"]["c_trend"] == ["O-trend", "O-st"] and "O-adx" in WA["on"]["c_trend"], (WA["champ"]["c_trend"], WA["on"]["c_trend"]))
# ④ the safety gap — replay up to the last day «momentum» was a champion: its record then
on_t = sorted(t for t, sym, s, r_, pb, cs in WA["sent"]["c_mom"] if TURN in cs)
dem = None
if on_t:
    k = (on_t[-1] - T0) // DAY + 2
    W2 = m.gp_walk({s: ({"T": D["T"][:k], "C": D["C"][:k], "n": k}, {kk: [i for i in v if i < k] for kk, v in E.items()}) for s, (D, E) in FA.items()},
                   "coin", "1D", p=NOC, groups=["c_mom"])
    r2 = W2["rec"]["c_mom"].get(TURN) or [0, 1, 0, 0, 0]
    dem = (round(r2[0] / (r2[0] + r2[1]), 3), round(m._gp_pb(r2[4], r2[0] + r2[1], W2["U"]["dir"]), 3))
ok(f"④ the safety gap: «momentum» (80% for 200 days, then wrong) stayed a champion until its record fell near the usual + 2% ({dem}) — then silent",
   on_t and TURN not in WA["champ"]["c_mom"] and dem and dem[0] - dem[1] < 0.04 and (on_t[-1] - T0) // DAY > 230, (dem, on_t[-1:] and (on_t[-1] - T0) // DAY))
done = [x for x in WA["sent"]["c_trend"] if x[3] in (0, 1)]
sc = m.gp_score(WA["sent"]["c_trend"])
ok(f"② the group's record (what would have been sent): {sc[0]} of {sc[1]} ({100 * sc[0] / max(1, sc[1]):.0f}%) · usual {100 * sc[2] / max(1, sc[1]):.0f}%",
   sc[1] == len(done) and sc[0] / max(1, sc[1]) > 0.68 and 0.4 < sc[2] / max(1, sc[1]) < 0.6, sc)
FS = {s: ({"T": D["T"], "C": [100.0 * (1 + 0.001 * (k % 2)) for k in range(N)], "n": N}, E) for s, (D, E) in FA.items()}
WS = m.gp_walk(FS, "coin", "1D", p=NOC)
ok("② a move under 0.2% is not counted (prices that only wiggle 0.1% ⇒ no member has a record · no champion)",
   not any(WS["rec"][g] for g in WS["rec"]) and not any(WS["champ"][g] for g in WS["champ"]), [len(WS["rec"][g]) for g in WS["rec"]])


# ── scenario C (combos): «25» and «26» are coin flips alone · together on the same side (within the «together» window) right 85%
def gen_c(sym, i, last={}):
    f = {}
    for c in ("25", "26"):
        if rnd.random() < 0.15:
            f[c] = rnd.choice((1, -1))
    lk = m.SG_LK["1D"]
    prev = last.setdefault(sym, {})
    both = None
    for c, s in f.items():
        o = "26" if c == "25" else "25"
        q = f.get(o) if f.get(o) == s else (s if prev.get(o, (-99, 0))[1] == s and i - prev[o][0] < lk else None)
        if q:
            both = s
    for c, s in f.items():
        prev[c] = (i, s)
    if len(set(f.values())) > 1:
        f = {}
    return f, mag() * (pick(0.85, both) if both else rnd.choice((1, -1)))


FC = build(gen_c)
WC = m.gp_walk(FC, "coin", "1D", keep=COINS[:2])
rc = WC["rec"]["c_trend"]
ac = {k: round(r[0] / max(1, r[0] + r[1]), 2) for k, r in rc.items()}
ok(f"⑤ combos: «25+26» (85% together) is a champion ({WC['champ']['c_trend']}) · alone each ~55% ({ac.get('25')} · {ac.get('26')}) · combo {ac.get('25+26')}",
   "25+26" in WC["champ"]["c_trend"] and ac.get("25+26", 0) > 0.78 and ac.get("25", 1) < 0.65, ac)
WC0 = m.gp_walk(FC, "coin", "1D", p=NOC)
ok("⑤ with combos off no combo is formed (singles only)", not any("+" in k for g_ in WC0["rec"] for k in WC0["rec"][g_]), WC0["champ"]["c_trend"])


# ── scenario D (the usual removes the drift): the market rises 70% of the time
def gen_d(sym, i):
    r = rnd.random()
    if r < 0.30:
        return {"O-trend": 1}, mag() * (1 if rnd.random() < 0.7 else -1)        # «always up» ⇒ right 70% (as often as the market)
    if r < 0.45:
        return {"O-st": 1}, mag() * pick(0.9, 1)                               # right 90%
    return {}, mag() * (1 if rnd.random() < 0.7 else -1)


FD = build(gen_d)
WD = m.gp_walk(FD, "coin", "1D", p=NOC)
rd = WD["rec"]["c_trend"]
ok(f"⑥ the usual removes the drift: u = {WD['U']['dir']:.2f} · «always up» {rd['O-trend'][0] / sum(rd['O-trend'][:2]):.2f} is not a champion · "
   f"«90%» {rd['O-st'][0] / sum(rd['O-st'][:2]):.2f} is ({WD['champ']['c_trend']})",
   0.65 < WD["U"]["dir"] < 0.75 and "O-trend" not in WD["champ"]["c_trend"] and "O-trend" not in WD["on"]["c_trend"] and "O-st" in WD["champ"]["c_trend"],
   (WD["U"], WD["champ"]["c_trend"]))


# ── scenario E (the big-move job): «15» precedes a big move 60% of the time · «14» is unrelated · big moves are ~15% otherwise
def gen_e(sym, i):
    big = lambda p: (0.035 if rnd.random() < p else 0.008 + 0.004 * rnd.random()) * rnd.choice((1, -1))
    r = rnd.random()
    if r < 0.12:
        return {"15": rnd.choice((1, -1))}, big(0.6)
    if r < 0.24:
        return {"14": rnd.choice((1, -1))}, big(0.15)
    return {}, big(0.15)


FE = build(gen_e)
WE = m.gp_walk(FE, "coin", "1D", p=NOC)
re_ = WE["rec"]["c_big"]
ok(f"⑦ the big-move job: usual {WE['U']['big']:.2f} · «15» {re_['15'][0] / sum(re_['15'][:2]):.2f} is a champion · «14» {re_['14'][0] / sum(re_['14'][:2]):.2f} "
   f"is not ({WE['champ']['c_big']}) · no side (all graded as one side)",
   0.1 < WE["U"]["big"] < 0.3 and WE["champ"]["c_big"] == ["15"] and re_["15"][4] == re_["15"][0] + re_["15"][1], (WE["U"], WE["champ"]["c_big"], re_))


# ── scenario F (vs Bitcoin): the coin's move = Bitcoin's move ± 1% · «X-rs» says which way 80% of the time
BTCM = [mag() * rnd.choice((1, -1)) for _ in range(N)]


def gen_f(sym, i):
    if sym.startswith("BTC-"):
        return ({"X-rs": rnd.choice((1, -1))} if rnd.random() < 0.3 else {}), BTCM[i]
    r = rnd.random()
    if r < 0.15:
        s = rnd.choice((1, -1))
        return {"X-rs": s}, BTCM[i] + 0.01 * pick(0.8, s)
    if r < 0.30:
        return {"O-trend": rnd.choice((1, -1))}, BTCM[i] + 0.01 * rnd.choice((1, -1))
    return {}, BTCM[i] + 0.01 * rnd.choice((1, -1))


FF_ = build(gen_f, coins=["BTC-USDT"] + COINS[:9])
Db = FF_["BTC-USDT"][0]
WF = m.gp_walk(FF_, "coin", "1D", B={Db["T"][i]: Db["C"][i] for i in range(Db["n"])}, p=NOC)
rr = WF["rec"]["c_rs"]
btc_rs = any(x[1] == "BTC-USDT" for x in WF["sent"]["c_rs"])
ok(f"⑧ vs Bitcoin: «X-rs» {rr['X-rs'][0] / sum(rr['X-rs'][:2]):.2f} is a champion ({WF['champ']['c_rs']}) · «O-trend» is not · Bitcoin itself never graded on it",
   "X-rs" in WF["champ"]["c_rs"] and "O-trend" not in WF["champ"]["c_rs"] and not btc_rs and rr["X-rs"][0] + rr["X-rs"][1] < 12 * N * 0.16, (WF["champ"]["c_rs"], rr))


# ── scenario G (opposite champions on the last candle ⇒ nothing)
def gen_g(sym, i):
    if i == N - 1:
        return ({"O-trend": 1, "O-st": -1} if int(sym[1:].split("-")[0]) % 2 == 0 else {"O-trend": 1}), 0.0
    r, s = rnd.random(), rnd.choice((1, -1))
    if r < 0.3:
        return {"O-trend": s}, mag() * pick(0.8, s)
    if r < 0.6:
        return {"O-st": s}, mag() * pick(0.8, s)
    return {}, mag() * rnd.choice((1, -1))


FG = build(gen_g)
WG = m.gp_walk(FG, "coin", "1D", p=NOC)
ev = [s for s in COINS if int(s[1:].split("-")[0]) % 2 == 0]
nowg = WG["now"]["c_trend"]
ok(f"⑨ champions on opposite sides of the same candle ⇒ nothing for that coin · the others ⬆️ ({sorted(nowg)})",
   {"O-trend", "O-st"} <= set(WG["champ"]["c_trend"]) and not any(s in nowg for s in ev) and all(nowg.get(s, [0])[0] == 1 for s in COINS if s not in ev),
   (WG["champ"]["c_trend"], nowg))

# ── ⑩ gp_pack
PA = m.gp_pack(WC)
g = PA["g"]["c_trend"]
mem = m.gp_members("c_trend")
st = {x[0]: x[4] for x in g["m"]}
ok(f"⑩ gp_pack: record {g['rec']} · {len(g['m'])} rows (all {len(mem)} members + combos) · champions {g['ch']} · untested members 🧪 "
   f"({sum(1 for x in g['m'] if x[1] + x[2] == 0)}) · per coin of yours {sorted(g['coin'])}",
   g["rec"][:2] == m.gp_score(WC["sent"]["c_trend"])[:2] and set(mem) <= set(st) and all(st[c] == 2 for c in g["ch"]) and st.get("O-verdict") == 0
   and sorted(g["coin"]) == COINS[:2] and g["coin"][COINS[0]]["rec"][1] > 0 and all(len(x) == 6 for x in g["m"]), (g["rec"], g["ch"], sorted(g["coin"])))
ok("⑩ every group of the section is in the pack (🪙 8 groups) · market groups are not", sorted(PA["g"]) == sorted(k for k, v in m.GP_GROUPS.items() if v["sec"] == "coin"),
   sorted(PA["g"]))

# ── ⑪ the live check gives what the walk would have sent on the last candle
G = {"f": {"1D": {"coin": PA}}}
NW = m.gp_now({"1D": FC}, G)
live = {s: x[:2] for s, x in ((NW.get("1D") or {}).get("coin") or {}).get("c_trend", {}).items()}
hist = WC["now"]["c_trend"]
G2 = {"f": {"1D": {"coin": m.gp_pack(WG)}}}
NW2 = m.gp_now({"1D": FG}, G2, p=NOC)
live2 = {s: x[:2] for s, x in ((NW2.get("1D") or {}).get("coin") or {}).get("c_trend", {}).items()}
ok(f"⑪ the live check = the history walk on the last candle (combos: {len(hist)} coins · singles with opposite champions: {len(live2)} coins)",
   live == hist and live2 == WG["now"]["c_trend"] and len(live2) == len(COINS) - len(ev), (live, hist, live2, WG["now"]["c_trend"]))

# ── ⑫ open to new members
m._SG_XNM["Z-new"] = ("trend", "📈 جديد صاعد", "📉 جديد هابط", "معنى", "معنى", "New")
m._SG_XNM["Z-mkt"] = ("market", "🌐 جديد", "🌐 جديد", "معنى", "معنى", "New market")
inside = "Z-new" in m.gp_members("c_trend") and "Z-new" in m.gp_members("m_trend") and "Z-mkt" not in m.gp_members("c_trend")


def gen_z(sym, i):
    r, s = rnd.random(), rnd.choice((1, -1))
    if r < 0.2:
        return {"Z-new": s}, mag() * pick(0.8, s)
    if r < 0.4:
        return {"O-trend": s}, mag() * rnd.choice((1, -1))
    return {}, mag() * rnd.choice((1, -1))


WZ = m.gp_walk(build(gen_z), "coin", "1D", p=NOC)
ok(f"⑫ a new «trend» indicator joins «📈 الاتجاه» by itself (and 🧭 of the market) · a market-wide one stays out of coin groups · tested ⇒ champion "
   f"({WZ['champ']['c_trend']})", inside and WZ["champ"]["c_trend"] == ["Z-new"], (inside, WZ["champ"]["c_trend"]))
del m._SG_XNM["Z-new"], m._SG_XNM["Z-mkt"]

# ── ⑬ gp_build end to end on a candles file (12 coins · the three frames) — no network
NOW = int(time.time())
cdb = {"c": {}, "c4": {}, "c1": {}}
for sec, dx, n in (("c", DAY, 520), ("c4", 14400, 520), ("c1", 3600, 520)):
    tend = NOW // dx * dx - dx
    for j, s in enumerate(["BTC-USDT"] + COINS[:11]):
        p, rows = 10.0 + j, []
        for i in range(n):
            r = rnd.gauss(0.0003, 0.02 if sec == "c" else 0.008)
            o, c = p, p * math.exp(r)
            rows.append([tend - (n - 1 - i) * dx, o, max(o, c) * 1.004, min(o, c) * 0.996, c, 1000 + rnd.random() * 500])
            p = c
        cdb[sec][s] = {"d": rows}
t1 = time.time()
GB = m.gp_build(cdb, ["BTC-USDT"] + COINS[:11], [COINS[0]], {}, {})
okf = sorted(GB["f"]) == ["1D", "1H", "4H"] and all(sorted(GB["f"][fr]["mkt"]["g"]) == sorted(k for k, v in m.GP_GROUPS.items() if v["sec"] == "mkt") for fr in GB["f"])
wide = sum(1 for fr in GB["f"] for x in GB["f"][fr]["mkt"]["g"]["m_trend"]["m"] if x[0] in ("W-breadth", "W-comp") and x[1] + x[2] > 0)
ok(f"⑬ gp_build: three frames · 🪙 + 🌐 in each · market-wide readings graded on the whole history ({wide} rows) · {time.time() - t1:.0f}s · "
   f"coins per frame {GB['n']} · no order", okf and wide >= 2 and all(GB["n"][fr][0] == 12 for fr in GB["n"]) and GB["v"] == m.GP_VER and not ORD
   and list(GB["f"]["1D"]["coin"]["g"]["c_trend"]["coin"]) == [COINS[0]], (sorted(GB["f"]), GB["n"], wide))
json.dumps(GB)
ok(f"⑬ the build is plain JSON ({len(json.dumps(GB)) // 1024} KB)", len(json.dumps(GB)) < 1500 * 1024, len(json.dumps(GB)))

# ── ⑭ the notices from the groups (_gp_facts): text · only your coins · the market as «السوق» · 📲 only for a proven group · ⛔ · one key per side
Gf = {"v": m.GP_VER, "f": {"4H": {"coin": {"g": {"c_trend": {"rec": [600, 1000, 500.0], "m": [["O-trend", 63, 37, 80, 2, 0.5], ["O-st", 70, 30, 40, 2, 0.51]]},
                                                "c_mom": {"rec": [10, 20, 10.0], "m": [["O-macd", 30, 10, 40, 2, 0.5]]}}},
                                  "mkt": {"g": {"m_shock": {"rec": [70, 100, 50.0], "m": [["W-crash", 70, 30, 60, 2, 0.5]]}}}}}}
gpn = {"4H": {"coin": {"c_trend": {"SOL-USDT": [1, ["O-trend", "O-st"], 1], "DOGE-USDT": [-1, ["O-trend"], 1]}, "c_mom": {"SOL-USDT": [-1, ["O-macd"], 1]}},
              "mkt": {"m_shock": {"BTC-USDT": [1, ["W-crash"], 1]}}}}
ALLN = {k: "now" for k in m.AN_TY}
FX = m._gp_facts(gpn, Gf, ["SOL-USDT"], ALLN, ["4H"])
D_ = {f["ty"] + "|" + f["sym"]: f for k, f in FX}
tr, mo, sh = D_.get("g_c_trend|SOL-USDT"), D_.get("g_c_mom|SOL-USDT"), D_.get("g_m_shock|السوق")
ok(f"⑭ the notice: «{tr and tr['ln']}» — what will happen within the frame · the member's record and the usual · its name (the best champion that fired)",
   tr and tr["ln"] == "📈 🕓 يُتوقع أن يكمل الصعود خلال الساعات الأربع القادمة\nلون خط الاتجاه — صدق 70% من 100 مرة (العادي 51%)" and tr["lv"] == "now"
   and tr["dup"] == 12 * 3600 and tr["t"].startswith("SOL: 📈 🕓"), FX)
ok("⑭ only your coins (DOGE is not yours) · the market's groups speak as «السوق» · a group whose own record is not proven (20 results) ⇒ 👁 with a note",
   "g_c_trend|DOGE-USDT" not in D_ and sh and sh["ln"].startswith("🌊 🕓 بعد الصدمة: يُتوقع صعود خلال الساعات الأربع القادمة") and sh["lv"] == "now"
   and mo and mo["lv"] == "view" and "لم يثبت بعد" in mo["ln"] and mo["ln"].startswith("⚡ 🕓 يُتوقع اندفاع هابط"), D_)
ok("⑭ ⛔ a group turned off ⇒ nothing from it · the dedupe key is per group · frame · coin · side", not m._gp_facts(gpn, Gf, ["SOL-USDT"], dict(ALLN, g_c_trend="off", g_c_mom="off", g_m_shock="off"), ["4H"])
   and sorted(k for k, f in FX) == ["g|c_mom|4H|SOL-USDT|-1", "g|c_trend|4H|SOL-USDT|1", "g|m_shock|4H|BTC-USDT|1"], [k for k, f in FX])
lat = [f["ln"] for k, f in FX if re.search(r"[A-Za-z]{2,}", f["ln"])]
ok("⑭ no Latin words in a group notice", not lat, lat)
ok(f"⑭ one notice type per group ({sum(1 for k in m.AN_TY if k.startswith('g_'))}) in ⚙️ with 📲/👁/⛔ · the old 🎯 tendency type is gone · defaults: 📲 "
   f"{sorted(k[2:] for k, x in m.AN_TY.items() if k.startswith('g_') and x[3] == 'now')}",
   sum(1 for k in m.AN_TY if k.startswith("g_")) == len(m.GP_GROUPS) and "tend" not in m.AN_TY and all(m.AN_TY["g_" + g][2] == "g" + x["sec"] for g, x in m.GP_GROUPS.items()),
   [k for k in m.AN_TY])

# ── ⑮ the tick end to end: the first tick builds Holy_Groups.json (no file yet) · «gpn» per frame · the old tables' file is removed · the next
#    hour does not rebuild · the scan carries what fired now · /api/groups · ⚙️ records · 🔮 calls
NOWT = (int(time.time()) // DAY) * DAY + 600
U = ["BTC-USDT"] + COINS[:11]
CD = {"c": {}, "c4": {}, "c1": {}}
for sec, dx, n in (("c", DAY, 520), ("c4", 14400, 520), ("c1", 3600, 520)):
    tend = NOWT // dx * dx - dx
    for j, s in enumerate(U):
        p, rows = 10.0 + j, []
        for i in range(n):
            r = rnd.gauss(0.0003, 0.02 if sec == "c" else 0.008)
            o, c = p, p * math.exp(r)
            rows.append([tend - (n - 1 - i) * dx, o, max(o, c) * 1.004, min(o, c) * 0.996, c, 1000 + rnd.random() * 500])
            p = c
        CD[sec][s] = {"d": rows}
m.MKT_COINS, m.SG_UNI = tuple(U), len(U)
json.dump({"ticker_coins": ["C0", "C1"]}, open(m.APP_CFG, "w"))
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump(CD, open(m.SG_CFILE, "w"))
m._sg_refresh = lambda uni, frs, cdb, prog=None: []
m._SG.update(cidx=None)
os.environ["HOLY_SIG_THREAD"] = "1"
json.dump({"v": 1, "rec": {}}, open(os.path.join(m.ROOT, "Holy_Board.json"), "w"))
t1 = time.time()
m.sg_tick(now=float(NOWT), send=False)
G1 = m.gp_load()
st1 = m._sg_st()
ok(f"⑮ the first tick builds the groups ({time.time() - t1:.0f}s): Holy_Groups.json with the three frames · your coins kept {G1 and G1.get('keep')} · "
   f"«gpn» for {sorted(st1.get('gpn') or {})} · the old tables' file is gone",
   G1 and sorted(G1["f"]) == ["1D", "1H", "4H"] and G1.get("keep") == ["C0-USDT", "C1-USDT"] and sorted(st1.get("gpn") or {}) == ["1D", "1H", "4H"]
   and not os.path.exists(os.path.join(m.ROOT, "Holy_Board.json")) and st1.get("b_1D") == NOWT // DAY * DAY - DAY, (G1 and sorted(G1), st1.get("gpn"), st1.get("err")))
mt1 = os.path.getmtime(m.GP_FILE)
m.sg_tick(now=float(NOWT + 3600), send=False)
ok("⑮ the next hour scans again but does not rebuild (the build is daily · fresh · your coins covered)", os.path.getmtime(m.GP_FILE) == mt1 and m._sg_st().get("b_1H") == NOWT // 3600 * 3600,
   (os.path.getmtime(m.GP_FILE), mt1, m._sg_st().get("b_1H")))
cfgx = json.load(open(m.APP_CFG))
cfgx["sg_coins"] = ["C0-USDT", "C1-USDT", "C2-USDT"]
json.dump(cfgx, open(m.APP_CFG, "w"))
st_ = m._sg_st()
st_.pop("gp_try", None)
m._sg_save(st_)
ok("⑮ a new coin of yours (with candles) ⇒ a build is needed (at most every 6 hours)", m._gp_need(m._sg_st(), float(NOWT + 3600), ["C0-USDT", "C1-USDT", "C2-USDT"])
   and not m._gp_need({"gp_try": NOWT}, float(NOWT + 3600), ["C0-USDT", "C1-USDT", "C2-USDT"]), "")
V = m.gp_view()
ok(f"⑮ /api/groups: {len(V['groups'])} groups (🪙 {sum(1 for x in V['groups'].values() if x['sec'] == 'coin')} · 🌐 {sum(1 for x in V['groups'].values() if x['sec'] == 'mkt')}) · "
   f"the build · names for every indicator · each group's notice level · what fired now",
   V["ok"] and len(V["groups"]) == len(m.GP_GROUPS) and sorted(V["f"]) == ["1D", "1H", "4H"] and all(V["names"].get(c) for c in m._gp_codes())
   and set(V["lv"]) == set(m.GP_GROUPS) and sorted(V["now"]) == ["1D", "1H", "4H"] and V["frs"]["4H"][1] == "4 ساعات", {k: V[k] for k in ("ts", "n", "lv")})
SV = m.sg_view()
ok("⑮ ⚙️ gets each group's record per frame (what would have been sent)", all(sorted(SV["gpr"].get("g_" + g, {})) == ["1D", "1H", "4H"] for g in m.GP_GROUPS)
   and all(len(x) == 3 for y in SV["gpr"].values() for x in y.values()), list(SV["gpr"].items())[:2])
fake = {"1D": {"coin": {"c_trend": {"C0-USDT": [1, [x[0] for x in G1["f"]["1D"]["coin"]["g"]["c_trend"]["m"][:1]], 1]}}}}
st_ = m._sg_st()
st_["gpn"] = fake
m._sg_save(st_)
CN = m.gp_coin_now(["C0-USDT", "C1-USDT"])
ok(f"⑮ 🔮 the coin's group calls (frame · group · side · the member's name and record): {CN.get('C0-USDT')}",
   list(CN) == ["C0-USDT"] and CN["C0-USDT"][0][:3] == ["1D", "c_trend", 1] and isinstance(CN["C0-USDT"][0][3], str) and len(CN["C0-USDT"][0]) == 8, CN)
ok("⑮ no order was ever sent", not ORD, ORD)

# ── ⑯ a daily derivatives reading waits for its day to close (p141 · found by check 16): the day-D spike of the long/short accounts is read by
#    the daily candle of day D (it closes when the day closes) and by the hourly candle that closes at the day's end — never by an earlier hour
DD = (int(time.time()) // DAY) * DAY - DAY                       # the last closed day's start
DS = DD - 5 * DAY                                                # the spike day
lsd = {str(DS - k * DAY): round(1.0 + 0.001 * k, 4) for k in range(1, 70)}      # slowly falling (each new day is low ⇒ never «crowded»)
lsd[str(DS)] = 3.0                                                               # the spike: the most crowded day ⇒ a reverse reading
for k in range(1, 6):
    lsd[str(DS + k * DAY)] = round(0.9 - 0.001 * k, 4)
PDB = {"ls": {"ZZ": {"d": lsd}}}


def candles(t_end, dx, n, p0=10.0):
    p, rows = p0, []
    for i in range(n):
        c = p * (1 + 0.004 * math.sin(i / 7.0))
        rows.append([t_end - (n - 1 - i) * dx, p, max(p, c) * 1.002, min(p, c) * 0.998, c, 1000.0])
        p = c
    return rows
drows = candles(DD, DAY, 320)
hrows = candles(DD + DAY - 3600, 3600, 400)
ctx = m._sg_ctx("ZZ-USDT", drows, PDB, {}, None, {})
Dd, Ed = m._sg_events(drows, True, ctx, t0=210, dx=DAY)
Dh, Eh = m._sg_events(hrows, False, ctx, t0=210, dx=3600)
fd = [Dd["T"][i] for i in Ed.get(("P-ls", -1), [])]
fh = [Dh["T"][i] for i in Eh.get(("P-ls", -1), [])]
ok(f"⑯ a daily derivatives reading waits for its day to close: the daily candle of the spike day fires ({[time.strftime('%m-%d', time.gmtime(t)) for t in fd]}) · "
   f"the first hourly firing is the hour that closes the day ({[time.strftime('%m-%d %H:00', time.gmtime(t)) for t in fh[:1]]}) — no earlier hour",
   fd == [DS] and fh and fh[0] == DS + 23 * 3600 and all(t >= DS + 23 * 3600 for t in fh), (fd, fh[:3], DS))

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_groups: {sum(res)}/{len(res)} (the indicator groups)")
sys.exit(0 if all(res) else 1)
