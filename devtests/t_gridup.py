# 🧮 the grid's «levels above the price (from your coins)» calculator — the owner (8-11): «حساب للاوردرات البعيدة … الرقم فوق المستويات
#   وخليه مفتوح مو ثابت على رقم وفيه افحص اخر بيع او الي اين يصلل البيعات ، المهم ليس له علاقة لا بالمحرك ولا بأعدادات النشر»
#   a closed folder · fake keys · no network:
#   ① the numbers: base 1.0 · grid 1% · order 10$ · 5 levels ⇒ sells at 1.01 … 1.0510 (the range preview's own formula: base × 1.01^n)
#      · each level's coins = 10$ at the level under it (10 × 1.01 / price) · their sum · the last sell +5.101% · value now / sold
#   ② open: 37 · 1,000 (the middle is folded: 300 rows each end) · a huge number stops at the safety cap and says so
#   ③ «where do the sells reach» backwards: the last sell price you want ⇒ how many levels reach it (1.06 ⇒ 5 · 1.0615 ⇒ 6)
#   ④ the market price when no base is set · 🎚️ the levels above the range's top are counted (♾️ never) · bad input ⇒ a clear message
#   ⑤ nothing written: the folder is byte-for-byte the same before and after
#   ⑥ a real browser, «➕ نشر بوت جرد»: folded by default · open ⇒ the result · typing a last price fills the level count and back ·
#      the deploy body (gridFormBody) carries none of it · a real deploy writes a config without any calculator key · no page error
#   python3 devtests/t_gridup.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import hashlib, importlib.machinery, importlib.util, json, math, os, shutil, socket, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_gridup_")
json.dump({"port": 8092}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-gridup", "sec": "SECA-gridup", "pass": "PASA-gridup"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_gridup", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_gridup", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m._okx_pub = lambda p: None
m._okx_get = lambda *a, **k: None
m._acc_price = lambda s: 0.0
m.PX["XRP-USDT"] = 2.5


def snap():
    out = {}
    for dp, _, fs in os.walk(R):
        for f in fs:
            fp = os.path.join(dp, f)
            out[os.path.relpath(fp, R)] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
    return out


S0 = snap()
calc = getattr(m, "grid_up_calc", None)
C = (lambda d: calc(d)) if calc else (lambda d: {"ok": False, "msg": "no calculator"})

# ── ①
r = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "n": "5", "g_type": "grid"})
want = [1.01 ** k for k in range(1, 6)]
qs = [10 * 1.01 / p for p in want]
ok("① base 1.0 · 1% · 10$ · 5 levels ⇒ sells at 1.01 · 1.0201 · 1.0303 · 1.0406 · 1.0510 · coins 10$ at the level under each · "
   f"total {sum(qs):.6f} · the last sell +5.101% · value now {sum(qs):.4f}$ / sold {sum(q * p for q, p in zip(qs, want)):.4f}$",
   r.get("ok") and r["n"] == 5 and r["src"] == "forced" and [x["n"] for x in r["rows"]] == [1, 2, 3, 4, 5]
   and all(abs(x["p"] - p) < 1e-7 and abs(x["q"] - q) < 1e-7 for x, p, q in zip(r["rows"], want, qs))
   and abs(r["coins"] - sum(qs)) < 1e-8 and abs(r["last"] - want[-1]) < 1e-7 and abs(r["last_pct"] - 5.101) < 1e-3
   and abs(r["now_usd"] - sum(qs)) < 1e-3 and abs(r["sell_usd"] - 50.5) < 1e-3, r)
range_tbl = m.compute_grid_range_table({"grid_pct": "1", "usd_value": "10", "upper_price": 1.06, "forced_base_price": 1.0}, 1.0)
ok("… the same prices and coins as the range preview already in the form (compute_grid_range_table)",
   r.get("ok") and [round(x["p"], 6) for x in r["rows"]] == [s_["price"] for s_ in range_tbl.get("sells", [])][:5]
   and [round(x["q"], 4) for x in r["rows"]] == [s_["coin_qty"] for s_ in range_tbl.get("sells", [])][:5], (r.get("rows"), range_tbl.get("sells")))

# ── ②
r37 = C({"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "forced_base": "1.1698", "n": "37"})
r1k = C({"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "forced_base": "1.1698", "n": "1000"})
rbig = C({"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "forced_base": "1.1698", "n": "10000000"})
ok(f"② open: 37 levels (last sell {r37.get('last')} +{r37.get('last_pct')}%) · 1,000 (rows {len(r1k.get('rows') or [])}: the first and last 300) · "
   f"10,000,000 stops at the cap ({rbig.get('max')}) and says so",
   r37.get("ok") and r37["n"] == 37 and len(r37["rows"]) == 37 and abs(r37["last"] - 1.1698 * 1.006 ** 37) < 1e-6
   and r1k.get("ok") and r1k["n"] == 1000 and r1k["cut"] and len(r1k["rows"]) == 600 and r1k["rows"][299]["n"] == 300 and r1k["rows"][300]["n"] == 701
   and rbig.get("ok") and rbig["capped"] and rbig["n"] == rbig["max"], (r37.get("n"), r1k.get("n"), len(r1k.get("rows") or []), rbig.get("n")))

# ── ③
t5 = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "top": "1.06"})
t6 = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "top": str(1.01 ** 6)})
tlo = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "top": "1.005"})
ok("③ backwards: «the last sell at 1.06» ⇒ 5 levels (1.0510 · the 6th 1.0615 is above) · exactly 1.0615 ⇒ 6 · under the first level ⇒ a clear message",
   t5.get("ok") and t5["n"] == 5 and t6.get("ok") and t6["n"] == 6 and not tlo.get("ok") and "أول مستوى" in (tlo.get("msg") or ""), (t5, t6.get("n"), tlo))

# ── ④
mk = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "0", "n": "3"})
rg = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "n": "10", "g_type": "grid_range", "upper_price": "1.05"})
inf = C({"symbol": "XRP-USDT", "grid_pct": "1", "usd_value": "10", "forced_base": "1.0", "n": "10", "g_type": "grid", "upper_price": "1.05"})
bad = [C(d) for d in ({"grid_pct": "0", "usd_value": "10", "forced_base": "1", "n": "3"}, {"grid_pct": "1", "usd_value": "10", "forced_base": "1", "n": "0"},
                      {"symbol": "NOPE-USDT", "grid_pct": "1", "usd_value": "10", "n": "3"}, {"grid_pct": "x", "usd_value": "10", "n": "3"})]
ok(f"④ no base ⇒ the market price ({mk.get('base')}) · 🎚️ top 1.05 ⇒ {rg.get('above')} of 10 levels above it (♾️: {inf.get('above')}) · "
   "grid 0 · 0 levels · an unknown price · letters ⇒ a clear message each",
   mk.get("ok") and mk["base"] == 2.5 and mk["src"] == "market" and rg.get("ok") and rg["above"] == 6 and sum(1 for x in rg["rows"] if x["up"]) == 6
   and inf.get("ok") and inf["above"] == 0 and all(not b.get("ok") and b.get("msg") for b in bad), (mk, rg.get("above"), inf.get("above"), bad))

# ── ⑤
ok("⑤ nothing written: the dashboard's folder is byte-for-byte the same after every calculation", snap() == S0, set(snap()) ^ set(S0))


# ── ⑥ the real browser
def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R2 = tempfile.mkdtemp(prefix="t_gridup_ui_")
P1 = port()
shutil.copy(DASH, os.path.join(R2, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R2, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-gridup", "sec": "SECA-gridup", "pass": "PASA-gridup"}]}, open(os.path.join(R2, "monitor_config.json"), "w"))
JS = r"""
const { chromium } = require('playwright');
(async () => {
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 430, height: 900 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof openDeploy === 'function' && typeof DATA !== 'undefined', null, { timeout: 30000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  await pg.evaluate(() => openDeploy({ symbol: 'ADA-USDT', grid_pct: 1, usd_value: 10, forced_base: 1 })); await pg.waitForTimeout(600);
  const o = {};
  o.folded = await pg.evaluate(() => { const d = document.getElementById('n_upc'); return d ? !d.open : null });
  await pg.evaluate(() => { const d = document.getElementById('n_upc'); d.open = true }); await pg.waitForTimeout(900);
  o.r1 = await pg.evaluate(() => (document.getElementById('n_upres') || {}).innerText || '');
  o.top1 = await pg.evaluate(() => document.getElementById('n_uptop').value);
  await pg.fill('#n_uptop', '1.06'); await pg.waitForTimeout(900);
  o.n2 = await pg.evaluate(() => document.getElementById('n_upn').value);
  o.r2 = await pg.evaluate(() => document.getElementById('n_upres').innerText);
  await pg.fill('#n_upn', '25'); await pg.waitForTimeout(900);
  o.top3 = await pg.evaluate(() => document.getElementById('n_uptop').value);
  o.body = await pg.evaluate(() => gridFormBody());
  o.errs = errs; console.log(JSON.stringify(o)); await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
"""
jsf = os.path.join(R2, "ui.js"); open(jsf, "w").write(JS)
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d = None
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R2, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    rr = subprocess.run(["node", jsf, f"http://127.0.0.1:{P1}/"], capture_output=True, text=True, timeout=180, cwd="/tmp", env=env)
    U = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.stdout.strip() else {"err": rr.stderr[-600:]}
except Exception as e:
    U = {"err": repr(e)}
finally:
    if d:
        d.kill()
body = U.get("body") or {}
# the browser's own deploy body through the real deploy — in this process, nothing launched, no network
m.ROOT = R
m.launch = lambda bb: (True, "")
m.stop_bot = lambda *a, **k: True
m.tg_send = lambda *a, **k: True
m.wallet_keys = lambda w: {"api_key": "KEYA-gridup", "secret_key": "SECA-gridup", "passphrase": "PASA-gridup"}
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else {"code": "0", "data": [{"last": "1.0"}]})
m.PX["ADA-USDT"] = 1.0
for k in ("LEDGER", "GONE", "ARCHIVE_META", "BOT_META", "RI_LEDGER", "COIN_LEDGER"):
    if hasattr(m, k):
        setattr(m, k, os.path.join(R, os.path.basename(getattr(m, k))))
dep = m.deploy(dict(body)) if body else {"ok": False}
cfgs = []
for dp, _, fs in os.walk(R):
    for f in fs:
        if f.startswith("config_ADA-USDT") and f.endswith(".json"):
            cfgs.append(json.load(open(os.path.join(dp, f))))
U["dep"] = dep
ok("⑥ the browser: folded by default · open ⇒ «10 levels — the last sell at 1.1046 (+10.462%)» and the coins · the last price field filled",
   U.get("folded") is True and "10" in (U.get("r1") or "") and "1.1046" in (U.get("r1") or "") and "+10.462%" in (U.get("r1") or "")
   and "العملات المطلوبة" in (U.get("r1") or "") and str(U.get("top1")).startswith("1.1046"), {k: U.get(k) for k in ("folded", "r1", "top1", "err")})
ok(f"… typing the last sell 1.06 ⇒ the level count becomes {U.get('n2')} · typing 25 levels ⇒ the last price becomes {U.get('top3')}",
   U.get("n2") == "5" and str(U.get("top3")).startswith(f"{1.01 ** 25:.4f}"[:5]), {k: U.get(k) for k in ("n2", "top3", "r2")})
CALC_KEYS = {"n", "top", "up_n", "n_upn", "n_uptop", "upcalc"}
ok(f"… not part of the deploy: the form's body has none of it ({sorted(body)}) · the deployed config has no calculator key · no page error",
   body and not (CALC_KEYS & set(body)) and dep.get("ok") and cfgs and not any(CALC_KEYS & set(c) for c in cfgs) and not U.get("errs"),
   {"body": body, "dep": U.get("dep"), "cfgs": [sorted(c) for c in cfgs], "errs": U.get("errs")})
shutil.rmtree(R, ignore_errors=True)
shutil.rmtree(R2, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_gridup: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
