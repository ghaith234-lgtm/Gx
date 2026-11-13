# 🔬🟢🔔🎞️ v3.36.27 — the owner (8-11): «التوقعات والمؤشرات سويهم اقوى عبر الاختبارات حقيقية … مؤشر القاع حتى اعرف متى اشتري … اطفيه
#   (الانقلاب) … من يجيني اشعار له قيمه … الشريط المتحرك ملخص لكل عملة معدل المؤشرات … الصادق خليه بالبداية … مفهوم كلغة»
#   a closed folder · fake keys · no network (synthetic candles fed to the dashboard's own functions):
#   ① 🔮 every horizon carries what FOLLOWED its lean on the real prices (FC_REAL — the CI tables): day «strongly down» ⇒ ↗️ 52.1 vs
#      47.8 · month ⇒ «not proven» · this coin's own count of the same lean (the backtest counts per lean · FC_VER 5)
#   ② 🟢 the bottom score = ci/sig_check3.py's weighting B to the point (an independent copy of its formula on every day of a synthetic
#      history) · its levels · its parts in words · its own record (episodes 10 days apart · 14 days later) · Bitcoin above/below 200 days
#   ③ 🔔 the alerts: only the bottom (no turn · no squeeze · no near-level even when those fire) · quiet = 🟢 only · medium = 🟡+ ·
#      sensitive = 👀+ · once per level per episode · a new episode alerts right after a start, an old one stays silent · the text
#      carries the parts, the 28-coin record, Bitcoin's state, the coin's own record · the panel's rule and the test sample say so
#   ④ 🎞️ the strip summary per coin: the average in words · «tomorrow» only with a measured edge · the bottom badge only in a zone
#   ⑤ 📖 the guide has the bottom entry (the audit finds nothing missing)
#   ⑥ a real browser: 🔮 — the bottom line on the card, «higher after» with the normal share, the details (parts · record · Bitcoin ·
#      limits), the indicators truthful first · 📊 — the most accurate first · the strip in words · clear standard Arabic · no page error
#   python3 devtests/t_signals.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import importlib.machinery, importlib.util, json, math, os, random, shutil, socket, subprocess, sys, tempfile, time

H_ = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H_, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_signals_")
json.dump({"port": 8090}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_sig", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_sig", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m.ROOT = R
for k in ("INA_FILE", "FC_FILE", "IND2_FILE"):
    if hasattr(m, k):
        setattr(m, k, os.path.join(R, os.path.basename(getattr(m, k))))
SENT = []
m.tg_send = lambda *a, **k: SENT.append(("tg", a)) or True
m.app_feed_push = lambda *a, **k: SENT.append(("app", a)) or True
m._okx_pub = lambda p: None
m._okx_get = lambda *a, **k: None
m._http_json = lambda *a, **k: None
NOW = time.time()


def walk(n, dt, p0, vol, seed, crash=0, end=None):
    rnd, p, out = random.Random(seed), p0, []
    t1 = (int(end or NOW) // dt) * dt - dt
    for i in range(n):
        r = rnd.gauss(0, vol) if i < n - crash else -abs(vol) * 2.5
        o = p; p = p * math.exp(r)
        out.append([t1 - (n - 1 - i) * dt, o, max(o, p) * (1 + abs(rnd.gauss(0, vol / 3))), min(o, p) * (1 - abs(rnd.gauss(0, vol / 3))), p, 1000 + rnd.random() * 500])
    return out


D1 = {"BTC-USDT": walk(1200, 86400, 60000, 0.025, 1), "ETH-USDT": walk(1200, 86400, 3000, 0.03, 2, crash=7), "XRP-USDT": walk(1200, 86400, 1.0, 0.035, 3)}
H4 = {s: walk(1500, 14400, D1[s][-1][4] / math.exp(0), 0.012, 10 + i, crash=(14 if s == "ETH-USDT" else 0)) for i, s in enumerate(D1)}
m.fc_candles = lambda sym, db: (D1[sym], None)
m.fc_candles4 = lambda sym, db: (H4[sym], None)
m._fc_fund = lambda sym, db: None
m._XC_BTC["m"] = {int(r[0]): float(r[4]) for r in D1["BTC-USDT"]}
db = {}
FCR = {s: m.fc_coin(s, db, None) for s in D1}
m.FC.update(ts=time.time(), coins=FCR, order=list(D1), err="")

# ── ①
E = FCR["ETH-USDT"]["h"]
d, mo = E["d"].get("real") or {}, E["m"].get("real") or {}
G = m.FC_REAL["d"]["b"].get(E["d"]["vk"])
exp_k = "up" if G - 47.8 >= 2 else "dn" if G - 47.8 <= -2 else "eq"
bkd = (db.get("bt") or {}).get("ETH-USDT", {}).get("d", {}).get("bk") or {}
ok(f"① 🔮 each horizon carries what followed its lean on the real prices: ETH day lean «{E['d']['vk']}» ⇒ {d.get('t')} ({d.get('p')}% vs {d.get('base')}%) · "
   f"month ⇒ {mo.get('t')} · the coin's own count of the same lean ({d.get('own_n')} times) · FC_VER 5",
   m.FC_VER == 5 and d.get("p") == G and d.get("base") == 47.8 and d.get("k") == exp_k and mo.get("k") == "na" and "غير مؤكد" in (mo.get("t") or "")
   and sum(v[0] for v in bkd.values()) > 50 and d.get("own_n") == (bkd.get(E["d"]["vk"]) or [0])[0]
   and all((FCR[s]["h"][k].get("real") or {}).get("t") for s in FCR for k in ("d", "w", "m", "q") if not FCR[s]["h"][k].get("short")), (d, mo, list(bkd.items())[:3]))
ok("… the real table is the CI's: day strongly down 52.1 · up 45.1 · strongly up 44.9 · normal 47.8 · week strongly down 48.4 · normal 46.3 · month and 3 months «not proven»",
   m.FC_REAL["d"]["b"] == {"sd": 52.1, "d": 49.7, "f": 45.2, "u": 45.1, "su": 44.9} and m.FC_REAL["w"]["base"] == 46.3 and m.FC_REAL["w"]["b"]["sd"] == 48.4
   and not m.FC_REAL["m"]["ok"] and not m.FC_REAL["q"]["ok"] and m.FC_REAL["d"]["ok"], m.FC_REAL)


# ── ② the bottom score = ci/sig_check3.py weighting B (an independent copy)
def ci_score(C, rsi, t):
    lr = [0.0] + [math.log(C[i] / C[i - 1]) for i in range(1, len(C))]
    rs = lr[t - 59:t + 1]; rm = sum(rs) / 60; sd = math.sqrt(sum((x - rm) ** 2 for x in rs) / 59) or 1e-9
    z7 = math.log(C[t] / C[t - 7]) / (sd * math.sqrt(7))
    w = C[t - 19:t + 1]; mu = sum(w) / 20; sdp = math.sqrt(sum((x - mu) ** 2 for x in w) / 20)
    r = rsi[t]
    p = {"z7": z7 <= -2.0, "rsi25": r is not None and r <= 25, "rsi30": r is not None and 25 < r <= 30, "bb": C[t] < mu - 2 * sdp}
    return sum({"z7": 50, "rsi25": 30, "rsi30": 20, "bb": 20}[k] for k, on in p.items() if on)


mism, seen = [], set()
for s in D1:
    rows = D1[s]
    T, O, Hh, L, C, V = ([r[i] for r in rows] for i in range(6))
    S = m._i2_series(O, Hh, L, C, V)
    for t in range(210, len(C)):
        a = m._bot_at(C, S["rsi"], t)
        x = ci_score(C, S["rsi"], t)
        seen.add(x)
        if (a[0] if a else None) != x:
            mism.append((s, t, a and a[0], x))
b = FCR["ETH-USDT"]["bot"] or {}
ok(f"② 🟢 the bottom score is the real-price checker's formula to the point: {sum(len(D1[s]) - 210 for s in D1)} days on 3 coins, 0 differences · scores seen {sorted(seen)}",
   not mism and len(seen) >= 3, mism[:5])
ok(f"… ETH after a 7-day crash: {b.get('score')}/100 «{b.get('lbl')}» since {b.get('since')} day(s) · parts in words · its own record {b.get('own')} · "
   f"Bitcoin above 200 days: {b.get('btc_up')} · the 28-coin record for its level",
   b.get("lv") in ("zone", "strong") and b.get("score") >= 50 and any(p["on"] for p in b.get("parts") or []) and "نزل" in (b["parts"][0]["txt"])
   and b.get("btc_up") in (True, False) and (b.get("real") or {}).get("p14") in (61, 64) and b.get("normal", {}).get("p14") == 46 and "2026" in b.get("years", ""), b)

# ── ③ the alerts: only the bottom
INDROWS = []
for i, s in enumerate(D1):
    INDROWS.append({"sym": s, "base": s.split("-")[0], "px": D1[s][-1][4], "score": 60 if i == 1 else -60, "conf": 95, "ts": time.time(),
                    "parts": [{"k": "trend", "s": 1.0}, {"k": "st", "s": 1.0}, {"k": "rsi", "s": -0.2}], "levels": {"sw_hi": D1[s][-1][4] * 1.001},
                    "sq": {"on": True, "n": 9, "rel": True, "rel_n": 9, "d": "up", "t": time.time()}, "txt": "↗️", "verdict": "up"})
m.ticker_cfg = lambda: {"on": True, "coins": list(D1), "speed": 45}
m.indic_cfg = lambda: {"on": True, "coins": list(D1)}
m.TG_MUTED["v"] = False


def run(sens, coins_bot, fresh_state=True, since=0):
    for s, (lv, sc) in coins_bot.items():
        bb = dict(FCR[s].get("bot") or {}, lv=lv, score=sc, lbl={"watch": "👀 راقب", "zone": "🟡 منطقة شراء", "strong": "🟢 قاع قوي", "none": "لا إشارة"}[lv], since=since,
                  vol=True)                                   # (v3.36.31: only the bottom confirmed by volume alerts — t_alerts.py checks the rest)
        FCR[s]["bot"] = bb
    m.app_cfg = lambda: {"ina_on": True, "ina_sens": sens, "ina_ch": "both"}
    if fresh_state and os.path.exists(m.INA_FILE):
        os.remove(m.INA_FILE)
    SENT.clear()
    return m.ina_tick(now=time.time(), rows=INDROWS, send=True)


day = FCR["ETH-USDT"]["bot"]["day"]
run("mid", {s: ("none", 0) for s in D1})                                           # the first look: silent
a1 = m.ina_tick(now=time.time(), rows=INDROWS, send=True)
ok("③ 🔔 no turn, squeeze or near-level alert even with the average at ±60, a squeeze release and a level 0.1% away — nothing without a bottom reading",
   a1 == [] and not SENT, (a1, SENT[:2]))
al = {}
for sens in ("low", "mid", "high"):
    run(sens, {s: ("none", 0) for s in D1})
    out = []
    for lv, sc in (("watch", 30), ("zone", 50), ("strong", 70)):
        for s in D1:
            FCR[s]["bot"] = dict(FCR[s]["bot"], lv=lv, score=sc, lbl={"watch": "👀 راقب", "zone": "🟡 منطقة شراء", "strong": "🟢 قاع قوي"}[lv], since=1, day=day, vol=True)
        out += [x["t"].split(" — ")[0] for x in m.ina_tick(now=time.time(), rows=INDROWS, send=True) if x["sym"] == "ETH-USDT"]
    al[sens] = out
ok(f"… by sensitivity, one alert per level as the episode deepens (confirmed by volume · v3.36.31): quiet {al['low']} · medium {al['mid']} · sensitive {al['high']}",
   al["low"] == ["🟢 قاع قوي ✅ مؤكد بالحجم"] and al["mid"] == ["🟡 منطقة شراء ✅ مؤكد بالحجم", "🟢 قاع قوي ✅ مؤكد بالحجم"]
   and al["high"] == ["🟡 منطقة شراء ✅ مؤكد بالحجم", "🟢 قاع قوي ✅ مؤكد بالحجم"], al)
again = m.ina_tick(now=time.time(), rows=INDROWS, send=True)
ok("… the same level in the same episode never again", not [x for x in again if x["sym"] == "ETH-USDT"], again)
run("mid", {"ETH-USDT": ("strong", 70)}, since=1)
new_ep = [x for x in m.ina_tick(now=time.time(), rows=INDROWS, send=True) if x["sym"] == "ETH-USDT"]
os.remove(m.INA_FILE)
for s in D1:
    FCR[s]["bot"] = dict(FCR[s]["bot"], since=6)
old_ep = [x for x in m.ina_tick(now=time.time(), rows=INDROWS, send=True) if x["sym"] == "ETH-USDT"]
os.remove(m.INA_FILE)
for s in D1:
    FCR[s]["bot"] = dict(FCR[s]["bot"], since=1)
m.ina_tick(now=time.time(), rows=INDROWS, send=True)
first = [x for x in m.ina_tick(now=time.time(), rows=INDROWS, send=True) if x["sym"] == "ETH-USDT"]
os.remove(m.INA_FILE)
SENT.clear()
fresh_new = [x for x in m.ina_tick(now=time.time(), rows=INDROWS, send=True) if x["sym"] == "ETH-USDT"]
txt = fresh_new[0] if fresh_new else {}
ok(f"… right after a start: a NEW episode (began ≤ 1 day ago) alerts ({len(fresh_new)}) · an old one (6 days) stays silent ({len(old_ep)})",
   len(fresh_new) == 1 and not old_ep, (fresh_new, old_ep))
ok("… the alert carries its parts, the 28-coin record with volume (14 days · normal 46% · lately), without volume like chance, and the limit · sent to Telegram and the app",
   "مؤشر القاع" in txt.get("t", "") and "مؤكد بالحجم" in txt.get("t", "") and "نزل" in txt.get("b", "") and "أعلى بعد 14 يوماً" in txt.get("r", "") and "العادي 46%" in txt.get("r", "")
   and "السنوات الأخيرة" in txt.get("r", "") and "مثل الصدفة" in txt.get("r", "") and "دفعات" in txt.get("r", "") and any(k == "tg" for k, _ in SENT) and any(k == "app" for k, _ in SENT), (txt, SENT[:1]))
v = m.ina_view()
ok("… the panel's rule says it (bottom only · the others off with the reason) · the test sample is a bottom alert",
   "مؤشر القاع" in v["rule"] and "لم تثبت لها قيمة" in v["rule"] and "🔄" not in v["rule"], v["rule"])

# ── ④ the strip summary
m.IND2.update(coins={r["sym"]: dict(r, parts=[{"k": "trend", "s": 1.0}, {"k": "st", "s": 0.8}, {"k": "rsi", "s": -0.4}, {"k": "macd", "s": 0.0}]) for r in INDROWS},
              order=list(D1), ts=time.time())
cs = m._tape_sum()
e = cs.get("ETH-USDT") or {}
x = cs.get("XRP-USDT") or {}
qx = (FCR["XRP-USDT"]["h"]["d"].get("real") or {})
ok(f"④ 🎞️ the strip per coin: the average and its counts (ETH {e.get('sc')} · {e.get('up')} up / {e.get('dn')} down of {e.get('n')}) · «tomorrow» only with a measured edge "
   f"(XRP {qx.get('k')} ⇒ {'nx' in x}) · the bottom badge only in a zone (ETH {e.get('bot')})",
   e.get("sc") == 60 and e.get("up") == 2 and e.get("dn") == 1 and e.get("n") == 4 and ("nx" in x) == (qx.get("k") in ("up", "dn"))
   and (e.get("bot") or {}).get("lv") in ("watch", "zone", "strong") and "cs" in m.indic_view(), (e, x, qx))
# ── ⑤
ok("⑤ 📖 the guide has the bottom indicator (idea · calculation · reading · measured · limits) and the audit finds nothing missing",
   "bot" in m._GUIDE and m.guide_audit() == [] and "64%" in m._GUIDE["bot"]["meas"] and "2026" in m._GUIDE["bot"]["limit"], m.guide_audit())


# ── ⑥ the real browser
def port():
    s_ = socket.socket(); s_.bind(("127.0.0.1", 0)); p = s_.getsockname()[1]; s_.close(); return p


R2 = tempfile.mkdtemp(prefix="t_signals_ui_")
P1 = port()
shutil.copy(DASH, os.path.join(R2, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R2, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R2, "monitor_config.json"), "w"))
pk = os.path.join(R2, "state.json")
for s in FCR:                                                         # the ETH card in a strong bottom
    FCR[s]["bot"] = dict(FCR[s]["bot"], since=2)
FCR["ETH-USDT"]["bot"] = dict(FCR["ETH-USDT"]["bot"], lv="strong", score=70, lbl="🟢 قاع قوي")
json.dump({"fc": FCR, "ind2": m.IND2["coins"], "order": list(D1),
           "indic": [{"sym": s, "base": s.split("-")[0], "px": D1[s][-1][4], "rsi": 40, "trend": "down", "atr": 1.0, "pos": 30, "lo": 1, "hi": 2} for s in D1]},
          open(pk, "w"), default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
RUN = r'''
import importlib.machinery, importlib.util, json, os, sys, time, urllib.request
import requests
R, PORT = sys.argv[1], int(sys.argv[2])
def _no(*a, **k): raise OSError("devtests: no network")
requests.get = requests.post = requests.request = _no
urllib.request.urlopen = _no
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_ui", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_ui", ld)); sys.argv = ["x"]; ld.exec_module(m)
m._okx_pub = lambda p: None; m._okx_get = lambda *a, **k: None; m.tg_send = lambda *a, **k: True
st = json.load(open(os.path.join(R, "state.json")))
coins = st["order"]
m.ticker_cfg = lambda: {"on": True, "coins": coins, "speed": 45}
m.indic_cfg = lambda: {"on": True, "coins": coins}
m.FC.update(ts=time.time(), coins=st["fc"], order=coins, err="")
m.IND2.update(ts=time.time(), coins={s: dict(v, acc=None) for s, v in st["ind2"].items()}, order=coins, summary={"up": 1, "down": 2, "flat": 0})
for s, v in m.IND2["coins"].items():
    v["parts"] = [dict(p, name=p["k"], ico="•", txt="سطر " + p["k"], what="", w=1.0, acc=a, n=40) for p, a in zip(v["parts"], (48, 61, 55, None))]
m.INDIC.update(ts=time.time(), rows=st["indic"], fng={}, err="")
m._fc_run = lambda: None; m._ind2_run = lambda: None
print("dashboard up", flush=True)
m.ThreadingHTTPServer(("127.0.0.1", PORT), m.Handler).serve_forever()
'''
open(os.path.join(R2, "run.py"), "w").write(RUN)
JS = r'''
const { chromium } = require('playwright');
(async () => {
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 430, height: 1200 }, deviceScaleFactor: process.env.SIG_SHOT ? 2 : 1 });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof openFc === 'function' && typeof DATA !== 'undefined' && DATA && DATA.indic, null, { timeout: 40000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.waitForTimeout(1500);
  const o = {};
  o.tape = await pg.evaluate(() => [...document.querySelectorAll('#tape2in .ik')].slice(0, 3).map(e => e.innerText.replace(/\s+/g, ' ')));
  const SHOT = process.env.SIG_SHOT;                                  // (optional: screenshots for the owner — synthetic data)
  if (SHOT) { await pg.evaluate(() => { const t = document.getElementById('tape2in'); if (t) t.style.animation = 'none'; if (TAPES.i && TAPES.i.halt) TAPES.i.halt() });
    const t2 = await pg.$('#tape2'); if (t2) await t2.screenshot({ path: SHOT + '/tape.png' }) }
  await pg.evaluate(() => openFc()); await pg.waitForTimeout(1500);
  o.card = await pg.evaluate(() => { const c = [...document.querySelectorAll('#fc_body .fc-c')].find(e => e.innerText.includes('ETH')); return c ? c.innerText : '' });
  if (process.env.SIG_SHOT) await (await pg.$('#modal')).screenshot({ path: process.env.SIG_SHOT + '/fc.png' });
  await pg.evaluate(() => fcTog('ETH-USDT')); await pg.waitForTimeout(500);
  if (process.env.SIG_SHOT) { const c = await pg.$('#fc_body .fc-c.open'); if (c) await c.screenshot({ path: process.env.SIG_SHOT + '/fc_eth.png' }) }
  o.det = await pg.evaluate(() => { const c = [...document.querySelectorAll('#fc_body .fc-c')].find(e => e.innerText.includes('ETH')); return c ? c.innerText : '' });
  o.order = await pg.evaluate(() => { const c = [...document.querySelectorAll('#fc_body .fc-c')].find(e => e.innerText.includes('ETH'));
    return c ? [...c.querySelectorAll('.ind-row .fb')].map(x => x.className.replace('fb ', '')) : [] });
  await pg.evaluate(() => { hideModal(); openInd() }); await pg.waitForTimeout(1200);
  await pg.evaluate(() => indTog('ETH-USDT')); await pg.waitForTimeout(400);
  o.ind = await pg.evaluate(() => { const c = [...document.querySelectorAll('#ind_body .ind-c')].find(e => e.innerText.includes('ETH')); return c ? [...c.querySelectorAll('.ind-row')].map(r => { const s = r.querySelectorAll('small'); return s.length ? s[s.length - 1].innerText : '' }).filter(t => t.startsWith('سطر')) : [] });
  o.indh = await pg.evaluate(() => (document.querySelector('#modal h2') || {}).innerText || '');
  o.errs = errs; console.log(JSON.stringify(o)); await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
'''
jsf = os.path.join(R2, "ui.js"); open(jsf, "w").write(JS)
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
dproc = None
try:
    dproc = subprocess.Popen([sys.executable, os.path.join(R2, "run.py"), R2, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in dproc.stdout.readline()
    rr = subprocess.run(["node", jsf, f"http://127.0.0.1:{P1}/"], capture_output=True, text=True, timeout=180, cwd="/tmp", env=env)
    U = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.stdout.strip() else {"err": rr.stderr[-600:]}
except Exception as ex:
    U = {"err": repr(ex)}
finally:
    if dproc:
        dproc.kill()
card, det = U.get("card") or "", U.get("det") or ""
ok("⑥ the browser 🔮: the ETH card shows «🟢 قاع قوي 70/100» · the column «أعلى بعدها» with the share and the normal (…% /48) · the indicators' lean kept",
   "قاع قوي" in card and "70/100" in card and "أعلى بعدها" in card and "/48" in card and "غير مؤكد" in card, {k: U.get(k) for k in ("card", "err")})
ok("… the details: the bottom's parts, its 28-coin record (14 days · normal 46%), Bitcoin's state, the limits (2026 · in parts · no confirmation) · what followed the lean",
   "مؤشر القاع" in det and "نزل" in det and "العادي 46%" in det and "البيتكوين" in det and "دفعات" in det and "2026" in det and "على الأسعار الحقيقية" in det, det[:1500])
rk = {"g": 0, "y": 1, "n": 2, "short": 3, "r": 4}
od = [rk.get(c.split()[0], 3) for c in U.get("order") or []]
ok(f"… the indicators under the horizon truthful first ({U.get('order')})", od and od == sorted(od), U.get("order"))
ok(f"⑥ 📊: the most accurate first ({[x.split('·')[-1].strip() for x in (U.get('ind') or [])]}) · the title in standard Arabic «{U.get('indh')}»",
   len(U.get("ind") or []) == 4 and "61%" in U["ind"][0] and "55%" in U["ind"][1] and "48%" in U["ind"][2] and "هل تصعد العملة أم تهبط" in (U.get("indh") or ""),
   {k: U.get(k) for k in ("ind", "indh")})
tp = " | ".join(U.get("tape") or [])
ok(f"⑥ 🎞️ the strip in words: «{tp[:160]}»", "صاعدة بقوة" in tp and "هابطة بقوة" in tp and "/4" in tp and "قاع قوي" in tp and "RSI" not in tp, U.get("tape"))
ok("… no page error", not U.get("errs") and not U.get("err"), (U.get("errs"), U.get("err")))
shutil.rmtree(R, ignore_errors=True)
shutil.rmtree(R2, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_signals: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
