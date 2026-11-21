# 🎯 the indicators in plain words (v3.36.71 · p121) — the owner (21-11): «اريد المؤشرات مفهومة وسهلة وكلامها مفهوم واي مؤشرات جديدة
#   انضيفها بالمستقبل لان حاليا صاير عشوائية».
#   THE RULE FOR EVERY FUTURE INDICATOR (HANDOFF §١ · «المؤشرات بكلام واضح»): a new signal code is not done until it has its plain entry
#   (_SG_NM for one of the 36 systems · _SG_XNM for anything else): its name for a rise and for a fall in plain Arabic without technical
#   letters · what it means in one sentence each · its technical name · one of the families of SG_GRP. This test finds every code the
#   analyst can produce (from the code AND by running the dashboard's own event code on synthetic candles with every market series) and
#   fails on any code without its entry.
#   ① every code has its entry (36 systems · the ten · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️ · 🏦) · ② the entry is plain (no Latin letters in the
#   names or meanings · no dialect · short · a rise and a fall that differ) · ③ the same names everywhere (_sg_name · the window's table)
#   · ④ one tab «🎯 المؤشرات» (no «📈 المؤشرات العشرة» / «🎯 الإشارات الشغّالة») — the tables since v3.36.73 · ⑤ one setting: the % (the minimum 15 and «better than
#   random» fixed inside, whatever an old config says)
#   python3 devtests/t_plain.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, random, re, shutil, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "tools"))
import msa_scan                     # noqa: E402

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
SRC = open(DASH, encoding="utf-8").read()
WEAK = {"بعد", "كلها", "كله", "يعني", "ترى", "كلي", "انقطع", "يرجع", "ترجع", "رجعت", "مال", "مالك", "يحسبها", "يحسبه", "يعرفه", "رح"}
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_plain_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_plain", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_plain", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda *a, **k: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
m._http_json = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
try:
    L = m._sg_lib()
    # ── ① every code: from the code itself …
    fn = lambda name: SRC[SRC.index(f"def {name}("):SRC.index("\ndef ", SRC.index(f"def {name}(") + 5)]
    body = fn("_sg_old") + fn("_sg_extra") + fn("_sg_crash")
    codes = set(L.SYS) | {"O-" + k for k, *_ in m._IND2_K}
    codes |= set(re.findall(r'"((?:[OFXWMP])-[a-z0-9]+)"', body))
    codes |= {"F-" + k for k in re.findall(r'for kk in \(([^)]*)\)', body) for k in re.findall(r'"([a-z0-9]+)"', k)}
    codes |= {"M-" + k for k in list(m.SG_MLAG)}
    codes |= {"P-" + k for k in re.findall(r'"(ls|tk|pc|mv)": lambda', body)}
    codes.discard("O-")
    # … and by running the event code on synthetic candles with every market and professional series
    rnd = random.Random(4)

    def walk(n, step, sd, t1=1763683200):
        p, rows = 100.0, []
        for i in range(n):
            o = p
            p *= 1 + rnd.gauss(0, sd)
            rows.append([t1 - (n - i) * step, o, max(o, p) * (1 + abs(rnd.gauss(0, sd / 2))), min(o, p) * (1 - abs(rnd.gauss(0, sd / 2))), p,
                         1000 + rnd.random() * 900 * (4 if rnd.random() < 0.03 else 1)])
        return rows
    rd = walk(700, 86400, 0.035)
    r4 = walk(1500, 14400, 0.014)
    days = [int(r[0]) for r in rd]
    ser = lambda lo, hi: (days, [lo + (hi - lo) * (0.5 + 0.5 * math.sin(i / 9.0)) for i in range(len(days))])
    mkt = {"vix": ser(10, 40), "dxy": ser(95, 110), "us10": ser(3, 5), "epu": ser(80, 400), "gpr": ser(60, 250), "tone": ser(-3, 3), "fng": ser(5, 95)}
    pro = {"ls": ser(0.5, 3.0), "tk": ser(0.6, 1.6), "pc": ser(0.4, 1.4), "mv": ser(0.6, 3.6)}
    btc = {int(r[0]): float(r[4]) * 300 for r in walk(700, 86400, 0.03)}
    ctx = {"sym": "ETH-USDT", "drows": rd, "fng": mkt["fng"], "btc": btc, "mkt": mkt, "pro": pro}
    seen = set()
    for daily, rows in ((False, r4), (True, rd)):
        D, E = m._sg_events(rows, daily, ctx)
        seen |= {c for c, s in E}
    F4 = {f"C{i}-USDT": m._sg_events(walk(400, 14400, 0.01), False, dict(ctx, mkt={}, pro={})) for i in range(12)}
    for s_, (D, E) in F4.items():                          # 🌊 a market-wide crash on the last candle of every coin
        for k in (D["n"] - 2,):
            D["C"][k] = D["C"][k - 1] * 0.85
    m._sg_crash(F4)
    seen |= {c for D, E in F4.values() for c, s in E}
    allc = sorted(codes | seen)
    miss = [c for c in allc if not m._sg_plain(c)]
    ok(f"① every code the analyst can produce has its plain entry ({len(allc)} codes: {len(L.SYS)} systems · the ten · 🔮 · 🧲 · 💪 · 🌊 · "
       f"😨 · 🗞️ · 🏦 · {len(seen)} seen running the event code)", not miss and len(allc) >= 67 and len(seen) >= 30, (miss, len(allc), len(seen)))
    ok("① …the running event code found nothing the code list missed (both ways find the same set)", not (seen - codes), sorted(seen - codes))

    # ── ② plain
    grp = {g[0] for g in m.SG_GRP}
    one = {"W-crash", "O-bottom", "O-botv"}
    bad = []
    for c in allc:
        p = m._sg_plain(c)
        if not p:
            continue
        g, bn, sn, bm, sm, tech = p
        why = []
        if g not in grp:
            why.append("family " + g)
        for t in (bn, sn, bm, sm):
            if not t or not t.strip():
                why.append("empty")
            elif re.search(r"[A-Za-z]", t):
                why.append("Latin letters: " + t)
            elif {x.group(0) for x in msa_scan.DRX.finditer(t)} - WEAK:
                why.append("dialect: " + t)
        if len(bn) > 60 or len(sn) > 60:
            why.append("name too long")
        if len(bm) > 140 or len(sm) > 140:
            why.append("meaning too long")
        if c not in one and (bn == sn or bm == sm):
            why.append("a rise and a fall read the same")
        if why:
            bad.append((c, why))
    ok("② every entry is plain: a family of the window · names and meanings in Arabic without technical letters (those go to the small «technical "
       "name») · no dialect · names ≤ 60 · meanings ≤ 140 · a rise and a fall that differ", not bad, bad[:8])
    ok(f"② the families in the window: {' · '.join(g[1] + ' ' + g[2] for g in m.SG_GRP)} — each with what it measures",
       len(m.SG_GRP) == 7 and all(len(g) == 4 and g[3] for g in m.SG_GRP), m.SG_GRP)
    sysg = {m._sg_plain(c)[0] for c in L.SYS}
    ok("② the 36 systems keep their measured family (trend · momentum · volatility · pattern · volume) · the professional readings their own (🏦)",
       sysg <= grp and m._sg_plain("P-tk")[0] == "pro" and m._sg_plain("M-fng")[0] == "market" and m._sg_plain("X-ad")[0] == "volume", sysg)

    # ── ③ the same names everywhere
    diff = [c for c in allc if m._sg_plain(c) and (m._sg_name(c, 1) != m._sg_plain(c)[1] or m._sg_name(c, -1) != m._sg_plain(c)[2])]
    ok("③ the notifications · the record · the CSV use the same plain names (_sg_name = the table)", not diff, diff[:8])
    pa = m.sg_plain_all()
    ok("③ the window gets the whole table (/api/signals «plain» · «grp»)", all(c in pa for c in allc) and len(pa[allc[0]]) == 6
       and '"plain"], v["grp"] = sg_plain_all()' in SRC, len(pa))
    ok("③ examples: «المتوسط السريع عبر فوق الأبطأ» · «شمعة صاعدة ابتلعت الهابطة قبلها» · «📈 الاتجاه العام صاعد» · «😱 أسواق الأسهم قلقة»",
       m._sg_name("09", 1) == "المتوسط السريع عبر فوق الأبطأ" and m._sg_name("20", 1) == "شمعة صاعدة ابتلعت الهابطة قبلها"
       and m._sg_name("O-trend", 1) == "📈 الاتجاه العام صاعد" and m._sg_name("M-vix", -1) == "😱 أسواق الأسهم قلقة"
       and m._sg_plain("09")[5] == L.SYS["09"][0], [m._sg_name(c, s) for c, s in (("09", 1), ("20", 1), ("O-trend", 1), ("M-vix", -1))])
    E1 = {"id": "1D|1|35", "f": "1D", "s": 1, "k": ["35"], "ty": "up", "nl": 0, "wl": 0, "ml": 0.0, "nt": 40, "wt": 25, "mt": 0.02, "rare": False,
          "ev": [], "c4": True}
    E2 = dict(E1, id="1D|1|12", k=["12"])
    m._sg_cat = lambda: {"e": [E1, E2], "idx": {"1D|1|35": E1, "1D|1|12": E2}, "base": {"1D|1": {"ht": 45.0, "mt": 0.0}}, "wk": {"1D": 40}, "coins": []}
    m._sg_st = lambda: {}
    f1 = m.sg_catlist({"q": ["MACD"], "side": ["1"]})
    f2 = m.sg_catlist({"q": ["Supertrend"], "side": ["1"]})
    f3 = m.sg_catlist({"q": ["الدفع انقلب"], "side": ["1"]})
    ok("③ the catalog's search still finds the technical names (MACD · Supertrend) and the plain words", [r["id"] for r in f1["rows"]] == ["1D|1|35"]
       and [r["id"] for r in f2["rows"]] == ["1D|1|12"] and [r["id"] for r in f3["rows"]] == ["1D|1|35"], (f1, f2, f3))

    # ── ④ one tab
    js = SRC[SRC.index("function sgRender(){"):SRC.index("function sgFcTop(")]
    ok("④ the window's tabs (📈 v3.36.75): 🌐 السوق · 🪙 العملات · 📋 المؤشرات · 📜 السجل · ⚙️ الإشعارات (the old analyst and groups tabs are gone)",
       "[['mkt','🌐 السوق'],['coins','🪙 العملات'],['ind','📋 المؤشرات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']]" in js
       and "🧠 المحلل'" not in js and "📚 المجموعات" not in js
       and "📈 المؤشرات العشرة" not in js and "الإشارات الشغّالة" not in js, js[:400])
    ok("④ the old parts are gone (sgNow · sgCoin · indRender · indTog · indLoad · sgAn · sgCatUI) — the old names open the new tabs (now → 🪙 · an → 🌐 · cat → 📋)",
       not any(f"function {f}(" in SRC for f in ("sgNow", "sgCoin", "indRender", "indTog", "indLoad", "sgAn", "sgCatUI")) and "({now:'coins',an:'mkt',cat:'ind'})" in SRC, "")
    ok("④ the tab is the tables (📋 v3.36.73): «🌐 السوق» + a table per coin · each row its plain name and job · the coin table keeps "
       "«📊 اتجاه المؤشرات الآن» («ليس توقعاً») · the old per-coin cards with the history records are gone",
       "اتجاه المؤشرات الآن" in SRC and "وصف لحال المؤشرات العشرة الآن — ليس توقعاً" in SRC and "function sbTable(" in SRC and "if(I)h+=sgIndAvg(I)" in SRC
       and "function sgIndRow(" not in SRC and "function sgIndCoin(" not in SRC and "return h+sbTable(V)" in SRC, "")

    # ── ⑤ one setting
    m.app_cfg = lambda: {"sg_thr": 60, "sg_min": 3, "sg_rnd": False}
    c = m.sg_cfg()
    ok("⑤ one setting: the % · «أقل عدد مرات» stays 15 and «أفضل من العشوائي» stays on whatever an old config says",
       c["thr"] == 60 and c["min"] == 15 and c["rnd"] is True, c)
    cfgjs = SRC[SRC.index("function sgCfg(V){"):SRC.index("function sgCoinAdd(")]
    ok("⑤ ⚙️ الإشعارات (📈 v3.36.75 · 🔔 v3.36.76): the facts by group (🔴 طوارئ · 🪙 عملاتك · 🌐 السوق كله) each 📲 · 👁 · ⛔ · no % · no count · no random switch · no estimate · "
       "no daily summary · no cap", "sgSet({alv:" in cfgjs and "🪙 عملاتك" in cfgjs and "🔴 طوارئ" in cfgjs and "👁 بالنافذة" in cfgjs and "🌐 السوق كله" in cfgjs and "لا يصلك إلا ما صدق في" not in cfgjs
       and 'id="sg_min"' not in cfgjs and "rnd:" not in cfgjs and "sg_est" not in cfgjs and "sum:" not in cfgjs and "cap:" not in cfgjs, cfgjs[:300])
finally:
    os.chdir(H)
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_plain: {sum(res)}/{len(res)} (the indicators in plain words)")
sys.exit(0 if all(res) else 1)
