# 🔔 the measured bottom-with-volume (v3.36.31) — and since v3.36.68 the old «📊 تنبيهات المؤشرات» are gone (the owner 20-11: «زيل القديمة
#   لا اريدها … اتحدثها نفسها مو تفتح واحد اخر»): their useful part lives inside 🎯 the signals. A closed folder · no network:
#   ① 🟢 the volume part = ci/sig_check4.py's formula to the point (every day of 3 synthetic coins) · a crash WITH a volume blow-off is
#      «✅ مؤكد بالحجم», the same crash without it is not · the score itself unchanged · the coin's own record with volume
#   ② the old alerts are gone: no round, no sending, no settings, no panel, no routes · the indicators and the forecasts no longer run
#      «for the alerts» with the ticker off · 🔔 price alerts stay
#   ③ 🟢 «القاع المؤكد بالحجم» is a 🎯 signal now (O-botv — the same rule: the bottom score ≥ 50 with the volume blow-off ≥ 2.5×) · the
#      same crash without the volume gives only «🟢 مؤشر القاع»
#   ④ the 🔮 card still shows «✅ مؤكد بالحجم» / «بلا تأكيد حجم» and the volume record (the dashboard's own JS run in node)
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
SENT = []
m.tg_send = lambda t, *a, **k: SENT.append(("tg", t)) or True
m.app_feed_push = lambda t, *a, **k: SENT.append(("app", t)) or True
m._okx_pub = lambda p: None
m._okx_get = lambda *a, **k: None
m.TG_MUTED["v"] = False
TICK = ["XRP-USDT", "SOL-USDT", "PEPE-USDT"]
m.ticker_cfg = lambda: {"on": True, "coins": list(TICK), "speed": 45}
m.indic_cfg = lambda: {"on": True, "coins": list(TICK)}


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

    # ── ② the old alerts are gone
    src = open(os.path.join(R, "Holy_Dashboard.pyw"), encoding="utf-8").read()
    gone = [w for w in ("ina_cfg", "ina_tick", "ina_view", "ina_set", "ina_test", "_ina_send", "mkt_scan", "INA_FILE", "inaPanel", "inaSet", "inaTest")
            if hasattr(m, w) or ("function " + w) in src]
    ok("② 🗑️ the old «📊 تنبيهات المؤشرات» are gone: no round · no sending · no settings · no page panel (nothing of ina_* / mkt_scan left)", not gone, gone)
    pg = src[src.index("function pxaRender("):src.index("function pxaRender(") + 300]
    il = src[src.index("def indic_loop():"):src.index("def indic_loop():") + 900]
    fl = src[src.index("def fc_loop():"):src.index("def fc_loop():") + 600]
    ok("② the ticker's settings show 🔔 price alerts + 🎯 the signals only · the indicators and the forecasts run only when they are on (not «for the alerts»)",
       "pxaPanel(PXAV)" in pg and "sgMini()" in pg and "ina" not in pg and 'if indic_cfg()["on"] and indic_cfg()["coins"]:' in il
       and 'if indic_cfg()["on"] and ticker_cfg()["coins"]:' in fl and hasattr(m, "pxa_view") and hasattr(m, "_ina_sq") and len(m.MKT_COINS) == 28, (pg, il[:300]))

    # ── ③ 🟢 the bottom with volume inside 🎯
    rv, rn = series(7, crash=True, spike=True), series(7, crash=True, spike=False)
    Dv, Ev = m._sg_events(rv, True, m._sg_ctx("TST-USDT", rv, {}, {}, None, {}))
    Dn, En = m._sg_events(rn, True, m._sg_ctx("TST-USDT", rn, {}, {}, None, {}))
    Vv, Cv = [r[5] for r in rv], [r[4] for r in rv]
    S2 = m._i2_series([r[1] for r in rv], [r[2] for r in rv], [r[3] for r in rv], Cv, Vv)
    want = []
    prev = 0
    for t in range(210, len(rv)):
        a_ = m._bot_at(Cv, S2["rsi"], t)
        cur = 1 if a_ and a_[0] >= 50 and m._bot_vx(Vv, t) >= m.BOT_VOL_X else 0
        if cur and not prev:
            want.append(t)
        prev = cur
    ok(f"③ 🟢 «القاع المؤكد بالحجم» is a 🎯 signal (O-botv · the bottom ≥ 50 with the volume ≥ {m.BOT_VOL_X}×): fires on {Ev.get(('O-botv', 1))} "
       f"= the rule's own days {want} · the same crash without the volume: only «🟢 مؤشر القاع» {En.get(('O-bottom', 1))}",
       Ev.get(("O-botv", 1)) == want and want and not En.get(("O-botv", 1)) and En.get(("O-bottom", 1))
       and m._sg_plain("O-botv")[1] == "🟢 القاع المؤكد بالحجم" and "O-botv" in m.gp_members("c_rev") and m.GP_NM.get("O-botv") == "القاع المؤكد بالحجم", (Ev.get(("O-botv", 1)), want, En.get(("O-bottom", 1))))

    # ── ④ the 🔮 card
    src = open(os.path.join(R, "Holy_Dashboard.pyw"), encoding="utf-8").read()
    js = src[src.index("function fcBot("):src.index("const FCK=")]
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
