# 🎯 the daily tendency (v3.36.76 · p131 — champions of the pooled daily tables). The owner (21-11): «نعم اريد إضافة ميل يومي ضعيف».
#   A closed folder (no network · no keys) with PLANTED firings on 12 coins × 400 days, so every rule is checked exactly:
#   ① no peeking: a row becomes a champion only from results already known (its first champion day comes after ≥ 50 different days of results)
#   ② the good row (75%) becomes a champion · a coin-flip row never does · a move under 0.2% is not counted
#   ③ at most two champions per family (three good «trend» rows ⇒ the two best)
#   ④ the safety gap: a champion that turns bad stays until it falls under 52% (not at 59%) — then it is silent
#   ⑤ the tendency: champions on one side ⇒ a tendency graded at the next close · a champion on each side ⇒ none · its own record (td_score)
#   ⑥ td_pack for the dashboard (today's tendency per coin · the champions with their record · the record of the last year)
#   ⑦ the daily scan returns «td» (the whole daily history) · nothing else changes · no orders
#   python3 devtests/t_tendency.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, shutil, sys, tempfile, time

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

R = tempfile.mkdtemp(prefix="t_tend_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_tend", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_tend", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
ORD = []
m._okx_post = lambda *a, **k: ORD.append(a) or (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
DAY = 86400
rnd = random.Random(5)
N, COINS = 400, [f"C{j}-USDT" for j in range(12)]
T0 = (int(time.time()) // DAY - N) * DAY
GOOD = {"O-trend": 0.78, "O-st": 0.74, "O-adx": 0.70}          # three good rows of the «trend» family
FLIP = "09"                                                    # a coin flip (trend family too)
TURN = "O-macd"                                                # momentum: right 80% for 200 days, then wrong 80%
fam = {c: m._td_fam(c) for c in list(GOOD) + [FLIP, TURN]}


def build(plan):
    """plan(sym, i, rnd) ⇒ {code: side} for candle i ⇒ the next candle moves by the planted outcome"""
    F = {}
    for sym in COINS:
        C, T, E = [100.0], [T0], {}
        out = []
        for i in range(N):
            f = plan(sym, i)
            out.append(f)
            for code, side in f.items():
                E.setdefault((code, side), []).append(i)
        for i in range(1, N):
            prev = out[i - 1]
            want = 0
            if len(set(prev.values())) > 1:                     # both sides at once ⇒ a coin flip (neither row's record is touched much)
                prev = {}
            for code, side in prev.items():                    # the planted truth: the first planted row decides tomorrow's move
                p = GOOD.get(code) or (0.8 if (code == TURN and i < 200) else 0.2 if code == TURN else 0.5)
                want = side if rnd.random() < p else -side
                break
            mv = (0.01 + 0.02 * rnd.random()) * (want or rnd.choice((1, -1)))
            C.append(C[-1] * (1 + mv))
            T.append(T0 + i * DAY)
        F[sym] = ({"T": T, "C": C, "n": N}, E)
    return F


def plan_a(sym, i):
    r = rnd.random()
    if r < 0.18:
        return {"O-trend": 1 if rnd.random() < 0.5 else -1}
    if r < 0.30:
        return {"O-st": 1 if rnd.random() < 0.5 else -1}
    if r < 0.40:
        return {"O-adx": 1 if rnd.random() < 0.5 else -1}
    if r < 0.55:
        return {FLIP: 1 if rnd.random() < 0.5 else -1}
    if r < 0.70:
        return {TURN: 1 if rnd.random() < 0.5 else -1}
    return {}


F = build(plan_a)
W = m.td_walk(F)
rec = W["rec"]
acc = {c: round(rec[c][0] / max(1, rec[c][0] + rec[c][1]), 3) for c in rec}
# ① no peeking — replay day by day: the first day each row could be a champion vs the days of results it had then
first = {}
for t, sym, side, r_, codes in W["tend"]:
    for c in codes:
        first.setdefault(c, t)
fires = {}
for sym, (D, E) in F.items():
    for (code, s), lst in E.items():
        for i in lst:
            fires.setdefault(code, set()).add(D["T"][i])
early = {c: sum(1 for t in fires.get(c, ()) if t < first[c]) for c in first}
ok(f"① no peeking: every champion's first tendency came after it had fired on ≥ 50 earlier days ({early})", first and all(v >= 50 for v in early.values()), early)
ok(f"② the good rows are champions at the end ({sorted(W['champ'])}) · the coin flip is not ({acc.get(FLIP)}) · the records: {acc}",
   "O-trend" in W["champ"] and FLIP not in W["champ"] and FLIP not in first and acc["O-trend"] > 0.7, (W["champ"], acc))
ok(f"③ at most two champions per family: three good «trend» rows ⇒ the two best ({[c for c in W['champ'] if fam.get(c) == 'trend']})",
   len([c for c in W["champ"] if fam.get(c) == "trend"]) == 2 and "O-adx" not in W["champ"] and "O-adx" in W["on"], (W["champ"], W["on"]))
# ④ the safety gap: when did «momentum» stop being a champion, and what was its record then?
dem = None
on_days = sorted(t for t, s, sd, r_, cs in W["tend"] if TURN in cs)
if on_days:
    last_on = on_days[-1]
    W2 = m.td_walk({s: ({"T": D["T"][:(last_on - T0) // DAY + 2], "C": D["C"][:(last_on - T0) // DAY + 2], "n": (last_on - T0) // DAY + 2},
                        {k: [i for i in v if i <= (last_on - T0) // DAY + 1] for k, v in E.items()}) for s, (D, E) in F.items()})
    r2 = W2["rec"].get(TURN) or [0, 1]
    dem = round(r2[0] / (r2[0] + r2[1]), 3)
ok(f"④ the safety gap: «momentum» (80% for 200 days, then wrong) stayed a champion until its record fell to ~52% ({dem}) — not at 59% · then silent",
   on_days and TURN not in W["champ"] and dem is not None and 0.50 <= dem <= 0.56 and (on_days[-1] - T0) // DAY > 230, (dem, on_days[-1:] and (on_days[-1] - T0) // DAY))
# ⑤ the tendency and its record
done = [x for x in W["tend"] if x[3] in (0, 1)]
sc = m.td_score(W["tend"])
right = sum(1 for t, sym, sd, r_, cs in done if r_ == 1)
ok(f"⑤ the tendency graded at the next close: {right} of {len(done)} right ({100 * right / max(1, len(done)):.0f}% — the planted champions are right ~75%) · td_score agrees",
   done and sc == [right, len(done)] and right / len(done) > 0.65, sc)


def plan_c(sym, i):                                            # long solo history (both become champions) · the last candle: opposite sides on even coins
    if i == N - 1:
        return {"O-trend": 1, "O-st": -1} if int(sym[1:].split("-")[0]) % 2 == 0 else {"O-trend": 1}
    r = rnd.random()
    return {"O-trend": 1 if rnd.random() < 0.5 else -1} if r < 0.3 else {"O-st": 1 if rnd.random() < 0.5 else -1} if r < 0.6 else {}


Fc = build(plan_c)
Wc = m.td_walk(Fc)
Pc = m.td_pack(Fc)
ev = sorted(s for s in COINS if int(s[1:].split("-")[0]) % 2 == 0)
ok("⑤ both champions firing on opposite sides of the same candle ⇒ no tendency for that coin (none against is the rule) · the others ⬆️",
   {"O-trend", "O-st"} <= set(Wc["champ"]) and not any(s in Pc["now"] for s in ev) and all(Pc["now"].get(s, [0])[0] == 1 for s in COINS if s not in ev),
   (Wc["champ"], Pc["now"]))

# a move under 0.2% is not counted
Fs = {s: ({"T": D["T"], "C": [100.0 * (1 + 0.001 * (k % 2)) for k in range(N)], "n": N}, E) for s, (D, E) in F.items()}
Ws = m.td_walk(Fs)
ok("② a move under 0.2% is not counted (prices that only wiggle 0.1% ⇒ no row has a record · no champion)", not Ws["rec"] and not Ws["champ"], (len(Ws["rec"]), Ws["champ"]))
# ⑥ td_pack
P = m.td_pack(F)
tl = max(D["T"][-1] for D, E in F.values())
ok(f"⑥ td_pack: today's tendency per coin ({len(P['now'])}) · {len(P['ch'])} champions with number, % and days · the record {P['rec']} · last year {P['rec1']}",
   P["t"] == tl and all(isinstance(v, list) and v[0] in (1, -1) for v in P["now"].values()) and all(x[1] == m.SB_NUM[x[0]] and x[3] >= 50 for x in P["ch"])
   and P["rec"] == sc and P["rec1"][1] <= P["rec"][1] and P["coins"] == 12, P)
ok("⑥ fewer than 5 coins ⇒ no tendency (too few to pool)", m.td_pack({s: F[s] for s in COINS[:4]}) is None, "")

# ⑦ the daily scan carries «td» (its whole daily history)
NOW = int(time.time())
TDE = NOW // DAY * DAY - DAY
cdb = {"c": {}, "c4": {}, "c1": {}}
for j, s in enumerate(["BTC-USDT"] + COINS[:7]):
    p, rows = 10.0 + j, []
    for i in range(400):
        r = rnd.gauss(0.0005, 0.03)
        o, c = p, p * math.exp(r)
        rows.append([TDE - (399 - i) * DAY, o, max(o, c) * 1.01, min(o, c) * 0.99, c, 1000 + rnd.random() * 500])
        p = c
    cdb["c"][s] = {"d": rows}
os.makedirs(m.SG_DIR, exist_ok=True)
json.dump(cdb, open(m.SG_CFILE, "w"))
jd = os.path.join(m.SG_DIR, "job_t")
os.makedirs(jd, exist_ok=True)
out = m.sg_scan_calc(jd, {"coins": ["BTC-USDT"] + COINS[:7], "frs": ["1D"]})
td = out.get("td") or {}
ok(f"⑦ the daily scan returns «td» from the whole daily history ({td.get('coins')} coins · rule {td.get('p', {}).get('dmin')} days · {td.get('p', {}).get('up')})",
   out.get("ok") and td.get("coins") == 8 and td.get("t") == TDE and "rec" in td and isinstance(td.get("ch"), list), {k: td.get(k) for k in ("coins", "t", "rec")})
out4 = m.sg_scan_calc(jd, {"coins": ["BTC-USDT"] + COINS[:7], "frs": ["4H"]})
ok("⑦ only the daily close computes it (a 4-hour scan carries none) · no order was sent", out4.get("td") is None and not ORD, out4.get("td"))

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_tendency: {sum(res)}/{len(res)} (the daily tendency)")
sys.exit(0 if all(res) else 1)
