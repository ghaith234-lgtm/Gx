# 🔔 the measured alerts (v3.36.31) — the owner (13-11): «اهم شي عندي التنبيه الصحيح الناتج عن اختبارك … للاثنين · لا تربط بالبوتات ·
#   اترك قاع الاربع ساعات · اختبر الجديد وحدث». A closed folder · no network (OKX's 4-hour candles are a local stand-in) · nothing sent out:
#   ① 🟢 the volume part = ci/sig_check4.py's formula to the point (every day of 3 synthetic coins) · a crash WITH a volume blow-off is
#      «✅ مؤكد بالحجم», the same crash without it is not · the score itself unchanged · the coin's own record with volume
#   ② 🔔 the bottom alerts only when confirmed by volume: quiet from 60 · medium / sensitive from 50 · without volume nothing at any
#      sensitivity · «👀 راقب» never · the text carries the 28-coin record (69/70% · normal 46% · lately 60/61% · without volume 48%)
#   ③ 🌊 the market crash: the 4-hour z and volume = ci/sig_check5.py's formula to the point · 16 of 28 coins crashing ⇒ medium alerts
#      (record of ≥ 50%), quiet does not · 22 of 28 ⇒ quiet alerts (record of ≥ 70%) · 10 of 28 ⇒ only sensitive (≥ 30%) · 5 of 28 ⇒
#      nobody · it names the ticker's coins that crashed with huge volume (a coin crashing without volume is not named · a coin outside
#      the 28 is checked too) · a candle closed 3 hours ago is stale ⇒ silent · the same candle never twice · at most once a day · fewer than
#      15 coins with data ⇒ no reading · the scan is cached per candle
#   ④ the panel's rule and the test sample say it · the card shows «✅ مؤكد بالحجم» / «بلا تأكيد حجم» and the volume record (the
#      dashboard's own JS run in node)
#   python3 devtests/t_alerts.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, shutil, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_alerts_")
json.dump({"port": 8112}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_alerts", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_alerts", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
for k in ("INA_FILE",):
    setattr(m, k, os.path.join(R, os.path.basename(getattr(m, k))))
SENT = []
m.tg_send = lambda t, *a, **k: SENT.append(("tg", t)) or True
m.app_feed_push = lambda t, *a, **k: SENT.append(("app", t)) or True
m._okx_pub = lambda p: None
m._okx_get = lambda *a, **k: None
m.TG_MUTED["v"] = False
TICK = ["XRP-USDT", "SOL-USDT", "PEPE-USDT"]
m.ticker_cfg = lambda: {"on": True, "coins": list(TICK), "speed": 45}
m.indic_cfg = lambda: {"on": True, "coins": list(TICK)}


def sens(s):
    m.app_cfg = lambda: {"ina_on": True, "ina_sens": s, "ina_ch": "both"}


try:
    # ── ① the volume part
    def series(seed, n=400, crash=False, spike=False):
        rnd = random.Random(seed)
        t0 = 1700000000 // 86400 * 86400
        p, rows = 1.0, []
        for i in range(n):
            o = p
            p = p * math.exp(rnd.gauss(0, 0.02))
            if crash and i >= n - 7:
                p = p * 0.93
            v = 1000 * (1 + rnd.random() * 0.2)
            if spike and i == n - 2:
                v *= 4
            rows.append([t0 + i * 86400, o, max(o, p) * 1.01, min(o, p) * 0.99, p, v])
        return rows

    def ci_vx(V, t):                                      # ci/sig_check4.py, verbatim
        va = sum(V[t - 22:t - 2]) / 20 or 1e-9
        return max(V[t - 2:t + 1]) / va

    mism, seen = [], 0
    for sd in (1, 2, 3):
        V = [r[5] for r in series(sd, spike=True)]
        for t in range(22, len(V)):
            seen += 1
            if abs(m._bot_vx(V, t) - ci_vx(V, t)) > 1e-9:
                mism.append((sd, t))
    bv = m.bot_coin("TST-USDT", series(7, crash=True, spike=True), {})
    bn = m.bot_coin("TST-USDT", series(7, crash=True, spike=False), {})
    pv = next((p for p in (bv or {}).get("parts") or [] if p["k"] == "vol"), {})
    pn = next((p for p in (bn or {}).get("parts") or [] if p["k"] == "vol"), {})
    ok(f"① the volume part = the checker's formula on {seen} days, 0 differences · a 7-day crash WITH a volume blow-off: {bv and bv['score']}/100 "
       f"«{bv and bv['lbl']}» vol {bv and bv['vol']} ({bv and bv['vx']}×) «{pv.get('txt')}» · the same crash without: vol {bn and bn['vol']} «{pn.get('txt')}» · the score unchanged",
       not mism and bv and bn and bv["score"] == bn["score"] >= 50 and bv["vol"] is True and bn["vol"] is False and pv.get("on") and not pn.get("on")
       and "يؤكد القاع" in pv.get("txt", "") and "بلا تأكيد" in pn.get("txt", "") and (bv.get("real_v") or {}).get("p14") in (69, 70)
       and (bv.get("novol") or {}).get("p14_l40") == 48 and isinstance(bv.get("own_v"), dict), (mism[:3], bv and {k: bv.get(k) for k in ("score", "vol", "vx", "lv")}))

    # ── ② the bottom alerts
    ROWS = [{"sym": s, "base": s.split("-")[0], "px": 1.0, "score": 0, "ts": time.time(), "parts": []} for s in TICK]
    DAY = int(time.time()) // 86400 * 86400 - 86400

    def bot(lv, sc, vol, since=1):
        lbl = {"watch": "👀 راقب", "zone": "🟡 منطقة شراء", "strong": "🟢 قاع قوي"}[lv]
        return {"lv": lv, "score": sc, "lbl": lbl, "since": since, "day": DAY, "vol": vol, "vx": 3.1 if vol else 1.2,
                "parts": [{"k": "z7", "on": True, "txt": "نزل 18.0% في 7 أيام"}, {"k": "vol", "on": vol, "txt": "حجم تداول ضخم بآخر 3 أيام (3.1× المعتاد) — يؤكد القاع"}],
                "real_v": m.BOT_REAL_V.get(lv), "own_v": {}, "real": m.BOT_REAL.get(lv), "normal": m.BOT_REAL["normal"]}

    def tick_bot(s, lv, sc, vol):
        sens(s)
        if os.path.exists(m.INA_FILE):
            os.remove(m.INA_FILE)
        m.FC = {"coins": {"XRP-USDT": {"bot": {"lv": "none", "score": 0, "day": DAY, "since": 0}}}}
        m.ina_tick(now=time.time(), rows=ROWS, send=True, mkt={})                     # the first look: silent
        m.FC = {"coins": {"XRP-USDT": {"bot": bot(lv, sc, vol)}}}
        SENT.clear()
        return [a for a in m.ina_tick(now=time.time(), rows=ROWS, send=True, mkt={}) if a["k"] == "bot"]

    grid = {}
    for s in ("low", "mid", "high"):
        for lv, sc in (("watch", 35), ("zone", 55), ("strong", 65)):
            for vol in (True, False):
                grid[(s, lv, vol)] = len(tick_bot(s, lv, sc, vol))
    want = {(s, lv, vol): int(vol and (lv == "strong" or (lv == "zone" and s != "low"))) for s in ("low", "mid", "high")
            for lv in ("watch", "zone", "strong") for vol in (True, False)}
    ok(f"② 🔔 the bottom alerts only when confirmed by volume — quiet: strong; medium/sensitive: zone and strong; never «👀 راقب»; "
       f"without volume nothing at any sensitivity ({sum(grid.values())} alerts of {len(grid)} cases)", grid == want,
       {k: (grid[k], want[k]) for k in grid if grid[k] != want[k]})
    al = tick_bot("mid", "strong", 65, True)
    t = al[0] if al else {}
    ok(f"… the text: «{t.get('t')}» · «{str(t.get('r'))[:220]}…» · sent to Telegram and the app",
       "✅ مؤكد بالحجم" in t.get("t", "") and "حجم تداول ضخم" in t.get("b", "") and "69%" in t.get("r", "") and "العادي 46%" in t.get("r", "")
       and "السنوات الأخيرة 60%" in t.get("r", "") and "مثل الصدفة (48%)" in t.get("r", "") and "قد ينزل أكثر" in t.get("r", "")
       and any(k == "tg" for k, _ in SENT) and any(k == "app" for k, _ in SENT), (t, SENT[:1]))

    # ── ③ the market crash
    NOW = (int(time.time()) // 14400) * 14400 + 1800        # half an hour after a 4-hour candle closed
    T = int(NOW // 14400) * 14400 - 14400
    DATA = {}
    CALLS = []

    def build(crash_set, vol_set, seed=5):
        DATA.clear()
        for j, sym in enumerate(list(m.MKT_COINS) + ["PEPE-USDT"]):
            rnd = random.Random(seed * 100 + j)
            p, rows = 1.0 + j, []
            for i in range(200):
                ts = T - (199 - i) * 14400
                o = p
                p = p * math.exp(rnd.gauss(0, 0.005))
                v = 1000 * (1 + rnd.random() * 0.2)
                if ts == T and sym in crash_set:
                    p = o * 0.92
                    v = 4000 if sym in vol_set else v
                rows.append([ts, o, max(o, p), min(o, p), p, v])
            DATA[sym] = rows
        m._MKT.update(t=None, res=None, try_=0)
        m._MKT["try"] = 0.0
        m._MKT["rows"].clear()

    def rows4(sym, bar, after=None, hist=True, limit=100):
        CALLS.append(sym)
        d = DATA.get(sym) or []
        if not hist:
            out = [r + [True] for r in d[-100:]] + [[T + 14400, d[-1][4], d[-1][4], d[-1][4], d[-1][4], 1.0, False]] if d else []
        else:
            out = [r + [True] for r in d if r[0] < int(after // 1000)][-100:]
        return list(reversed(out))

    m._fc_okx_rows = rows4

    def ci_z(rows, k):                                    # ci/sig_check5.py, verbatim
        C4, V4 = [r[4] for r in rows], [r[5] for r in rows]
        l4 = [0.0] + [math.log(C4[i] / C4[i - 1]) for i in range(1, len(C4))]
        rs = l4[k - 120:k]; rm = sum(rs) / 120; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 119) or 1e-9
        return l4[k] / sd, V4[k] / (sum(V4[k - 30:k]) / 30 or 1e-9)

    build(set(m.MKT_COINS[:16]) | {"PEPE-USDT"}, (set(m.MKT_COINS[:16]) | {"PEPE-USDT"}) - {"SOL-USDT"})        # SOL crashes WITHOUT volume
    zm = []
    for sym in m.MKT_COINS[:5]:
        rows = DATA[sym]
        for k in range(130, 200):
            a = m._mkt_at(rows, rows[k][0])
            b = ci_z(rows, k)
            if not a or abs(a[0] - b[0]) > 1e-9 or abs(a[1] - b[1]) > 1e-9:
                zm.append((sym, k, a, b))
    ok(f"③ 🌊 the 4-hour z and volume = the checker's formula to the point (350 candles, {len(zm)} differences)", not zm, zm[:3])

    def tick_mkt(s, now=NOW, fresh_state=True):
        sens(s)
        if fresh_state and os.path.exists(m.INA_FILE):
            os.remove(m.INA_FILE)
        SENT.clear()
        return [a for a in m.ina_tick(now=now, rows=[], send=True) if a["k"] == "mkt"]

    mk = m.mkt_scan(NOW)
    n_calls = len(CALLS)
    mk2 = m.mkt_scan(NOW)
    ok(f"… the scan: {mk and mk['k']} of {mk and mk['n']} coins crashed together · the ticker's coins crashed with huge volume "
       f"{[c['sym'] for c in (mk or {}).get('crash') or []]} (SOL crashed without volume ⇒ not named · PEPE is outside the 28 and still checked) · "
       f"cached per candle ({len(CALLS) - n_calls} new requests the second time)",
       mk and mk["k"] == 16 and mk["n"] == 28 and sorted(c["sym"] for c in mk["crash"]) == ["PEPE-USDT", "XRP-USDT"] and mk2 is mk
       and len(CALLS) == n_calls, mk)
    out = {}
    for crash_n, label in ((22, "22/28"), (16, "16/28"), (10, "10/28"), (5, "5/28")):
        cs = set(m.MKT_COINS[:crash_n])
        build(cs | {"XRP-USDT"}, cs | {"XRP-USDT"}) if "XRP-USDT" in cs else build(cs, cs)
        row = {}
        for s in ("low", "mid", "high"):
            m._MKT.update(t=None, res=None); m._MKT["try"] = 0.0
            a = tick_mkt(s)
            row[s] = a[0] if a else None
        out[label] = row
    pick = lambda lab, s: bool(out[lab][s])
    ok(f"… by sensitivity: 22/28 ⇒ quiet {pick('22/28','low')} medium {pick('22/28','mid')} sensitive {pick('22/28','high')} · 16/28 ⇒ "
       f"{pick('16/28','low')} {pick('16/28','mid')} {pick('16/28','high')} · 10/28 ⇒ {pick('10/28','low')} {pick('10/28','mid')} {pick('10/28','high')} · "
       f"5/28 ⇒ {pick('5/28','low')} {pick('5/28','mid')} {pick('5/28','high')}",
       [pick(l, s) for l in ("22/28", "16/28", "10/28", "5/28") for s in ("low", "mid", "high")]
       == [True, True, True, False, True, True, False, False, True, False, False, False], {l: {s: bool(v) for s, v in r.items()} for l, r in out.items()})
    a70, a50, a30 = out["22/28"]["low"] or {}, out["16/28"]["mid"] or {}, out["10/28"]["high"] or {}
    ok(f"… each with the record of its level: ≥ 70% «{str(a70.get('r'))[:120]}…» · ≥ 50% · ≥ 30% · the short bounce warning",
       "70% من العملات" in a70.get("r", "") and "68%" in a70.get("r", "") and "العادي 48%" in a70.get("r", "")
       and "50% من العملات" in a50.get("r", "") and "62%" in a50.get("r", "") and "56%" in a50.get("r", "") and "السنوات الأخيرة 62% و60%" in a50.get("r", "")
       and "30% من العملات" in a30.get("r", "") and "57%" in a30.get("r", "") and all("ارتداد قصير" in x.get("r", "") for x in (a70, a50, a30))
       and "22 من 28" in a70.get("t", "") and "16 من 28" in a50.get("t", ""), (a70, a50, a30))
    ok(f"… it names the ticker's coins crashed with huge volume: «{a50.get('b')}» · their record (65% after 3 days) · sent to Telegram and the app",
       "XRP -8.0% (حجم" in a50.get("b", "") and "المعتاد)" in a50.get("b", "") and "البيتكوين -8.0%" in a50.get("b", "") and "أعلى بعد 3 أيام 65%" in a50.get("r", ""), a50)
    build(set(m.MKT_COINS[:16]), set(m.MKT_COINS[:16]))
    m._MKT.update(t=None, res=None); m._MKT["try"] = 0.0
    stale = tick_mkt("mid", now=T + 14400 + 3 * 3600)
    m._MKT.update(t=None, res=None); m._MKT["try"] = 0.0
    first = tick_mkt("mid")
    again = tick_mkt("mid", fresh_state=False)
    m._MKT.update(t=None, res=None); m._MKT["try"] = 0.0
    nxt = tick_mkt("mid", now=NOW + 14400, fresh_state=False)            # the next candle (re-scanned) within a day
    for sym in list(DATA)[:16]:
        DATA[sym] = []
    m._MKT.update(t=None, res=None); m._MKT["try"] = 0.0; m._MKT["rows"].clear()
    few = m.mkt_scan(NOW)
    ok(f"… a candle closed 3 hours ago is stale ⇒ silent ({len(stale)}) · then fresh ⇒ 1 ({len(first)}) · the same candle again 0 ({len(again)}) · "
       f"another crash within a day 0 ({len(nxt)}) · fewer than 15 coins with data ⇒ no reading ({few})",
       not stale and len(first) == 1 and not again and not nxt and few is None, (stale, first, again, nxt, few))

    # ── ④ the panel's words and the card
    sens("mid")
    v = m.ina_view()
    sm = {}
    m._ina_send = lambda al, note, cfg: sm.update(a=al[0]) or True
    m.ina_test()
    ok(f"④ the panel's rule: «{v['rule'][:200]}…» · the test sample «{sm.get('a', {}).get('t')}»",
       "قاع مؤكد بالحجم" in v["rule"] and "50 فأكثر" in v["rule"] and "🌊 انهيار السوق" in v["rule"] and "50% فأكثر من 28 عملة" in v["rule"]
       and "لم تثبت لها قيمة" in v["rule"] and "القمة" in v["rule"] and "مؤكد بالحجم" in sm.get("a", {}).get("t", ""), (v["rule"], sm))
    src = open(os.path.join(R, "Holy_Dashboard.pyw"), encoding="utf-8").read()
    js = src[src.index("function fcBot("):src.index("function fcVote(")]
    jsf = os.path.join(R, "card.js")
    bvj = {"lv": "strong", "lbl": "🟢 قاع قوي", "score": 70, "since": 1, "vol": True, "parts": [{"on": True, "txt": "نزل", "w": 50}],
           "real": m.BOT_REAL["strong"], "normal": m.BOT_REAL["normal"], "real_v": m.BOT_REAL_V["strong"], "normal_v": m.BOT_REAL_V["normal"],
           "novol": m.BOT_REAL_V["novol"], "own": {}, "years": "2026", "btc_up": None}
    open(jsf, "w", encoding="utf-8").write("const gEsc=s=>String(s);\n" + js + "\nconst r1={base:'XRP',bot:" + json.dumps(bvj, ensure_ascii=False)
                                           + "};const r2={base:'XRP',bot:Object.assign({},r1.bot,{vol:false})};"
                                           + "console.log(JSON.stringify({a:fcBot(r1),b:fcBot(r2),d:fcBotDet(r1),e:fcBotDet(r2)}))")
    rr = subprocess.run(["node", jsf], capture_output=True, text=True, timeout=60)
    J = json.loads(rr.stdout.strip() or "{}") if rr.returncode == 0 else {"err": rr.stderr[-400:]}
    ok("… the 🔮 card: «✅ مؤكد بالحجم» / «بلا تأكيد حجم» · the details carry the volume record (69% · lately 60% · without 48%) and whether it holds now",
       "✅ مؤكد بالحجم" in J.get("a", "") and "بلا تأكيد حجم" in J.get("b", "") and "مع حجم ضخم" in J.get("d", "") and "69%" in J.get("d", "")
       and "60%" in J.get("d", "") and "48%" in J.get("d", "") and "✅ متحقق الآن" in J.get("d", "") and "▫️ غير متحقق الآن" in J.get("e", ""), J)
except Exception as ex:
    import traceback
    traceback.print_exc()
    ok("the test ran to its end", False, repr(ex))
finally:
    os.chdir("/")
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_alerts: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
