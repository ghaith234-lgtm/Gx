# 🖼️ the profit card's new periods — the owner (8-11): «ضيف على بطاقة الارباح البارحه ، الاسبوع السابق ، الشهر الحالي ، والشهر السابق»
#   the real dashboard in a closed folder (no network · nothing launched) with a ledger of known daily profits (every day a different
#   amount, 120 days back):
#   ① /api/profit for each period: yesterday = that day alone · the previous week = its Monday to Sunday · the current month = the 1st to
#      today · the previous month = its 1st to its last day · today / 7 / 30 days as before — each one's days and its total to the cent
#   ② a real browser: the card has the nine periods in order · each new one draws with its name and its dates on the card · no page error
#   python3 devtests/t_card_periods.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import calendar, json, os, shutil, socket, subprocess, sys, tempfile, urllib.request
from datetime import date, datetime, timedelta

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="t_card_")
P1 = port()
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
T0 = datetime.now().date()
val = lambda d: round(0.5 + (T0 - d).days * 0.01, 2)                 # every day a different amount
DAILY = {(T0 - timedelta(days=i)).strftime("%Y-%m-%d"): val(T0 - timedelta(days=i)) for i in range(0, 121)}
json.dump({"grid_xrp": {"symbol": "XRP-USDT", "daily": DAILY}}, open(os.path.join(R, "Holy_Ledger.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
d = None
API = {}
U = {}
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    for q in ("per=yday", "per=pweek", "per=month", "per=prev", "days=1", "days=7", "days=30"):
        API[q] = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{P1}/api/profit?{q}", timeout=60).read())
    JS = r'''
const { chromium } = require('playwright');
(async () => {
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 430, height: 1300 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof cardOpen === 'function' && typeof DATA !== 'undefined' && DATA, null, { timeout: 40000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove(); try { localStorage.removeItem('holy_card') } catch (e) {} });
  await pg.evaluate(() => cardOpen()); await pg.waitForTimeout(1500);
  const o = { btns: await pg.evaluate(() => [...document.querySelectorAll('#cd_p button')].map(b => b.innerText.trim())), per: {} };
  for (const k of ['yday', 'pweek', 'month', 'prev']) {
    await pg.evaluate(k => cardSet('days', k), k);
    await pg.waitForFunction(k => CARD.M && CARD.v && CARD.v._d === k && !CARD.busy, k, { timeout: 30000 });
    o.per[k] = await pg.evaluate(() => ({ period: CARD.M.period, hero: CARD.M.hero, on: (document.querySelector('#cd_p button.primary') || {}).innerText }));
  }
  o.errs = errs; console.log(JSON.stringify(o)); await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
'''
    jsf = os.path.join(R, "ui.js"); open(jsf, "w").write(JS)
    rr = subprocess.run(["node", jsf, f"http://127.0.0.1:{P1}/"], capture_output=True, text=True, timeout=180, cwd="/tmp", env=env)
    U = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.stdout.strip() else {"err": rr.stderr[-600:]}
except Exception as ex:
    U = {"err": repr(ex)}
finally:
    if d:
        d.kill()


def span(a, b):
    out, x = [], a
    while x <= b:
        out.append(x.strftime("%Y-%m-%d")); x += timedelta(days=1)
    return out


yd = T0 - timedelta(days=1)
wk_end = T0 - timedelta(days=T0.weekday() + 1)
pm_end = T0.replace(day=1) - timedelta(days=1)
EXP = {"per=yday": span(yd, yd), "per=pweek": span(wk_end - timedelta(days=6), wk_end), "per=month": span(T0.replace(day=1), T0),
       "per=prev": span(pm_end.replace(day=1), pm_end), "days=1": span(T0, T0), "days=7": span(T0 - timedelta(days=6), T0),
       "days=30": span(T0 - timedelta(days=29), T0)}
rows = []
for q, want in EXP.items():
    v = API.get(q) or {}
    got = [x.get("d") for x in v.get("days") or []]
    tot = round(float((v.get("tot") or {}).get("t") or 0), 2)
    exp_t = round(sum(DAILY[x] for x in want), 2)
    rows.append((q, got == want, tot == exp_t, got[:1] + got[-1:], tot, exp_t))
ok("① /api/profit: yesterday alone · the previous week Monday→Sunday · the current month from the 1st · the previous month whole · today / 7 / 30 as before — "
   + " · ".join(f"{q} {g[0] if g else '—'}→{g[-1] if g else '—'} = {t}$" for q, _, _, g, t, _ in rows),
   all(a and b for _, a, b, *_ in rows), rows)
pw = API.get("per=pweek") or {}
ok(f"… the previous week starts on a Monday and ends on a Sunday ({pw.get('from')} → {pw.get('to')}) · the previous month ends on its last day ({(API.get('per=prev') or {}).get('to')})",
   pw.get("from") and datetime.strptime(pw["from"], "%Y-%m-%d").weekday() == 0 and datetime.strptime(pw["to"], "%Y-%m-%d").weekday() == 6
   and (API.get("per=prev") or {}).get("to") == pm_end.strftime("%Y-%m-%d"), (pw.get("from"), pw.get("to")))
want_b = ["اليوم", "البارحة", "آخر 7 أيام", "الأسبوع السابق", "الشهر الحالي", "الشهر السابق", "آخر 30 يوماً", "آخر 90 يوماً", "آخر سنة"]
ok(f"② the card's periods in order: {U.get('btns')}", U.get("btns") == want_b, U)
P = U.get("per") or {}
ok("… each new period draws with its name and its dates (yesterday one date · the others «from ← to») and its button lit: "
   + " | ".join(f"{k}: {(P.get(k) or {}).get('period')} · {(P.get(k) or {}).get('hero')}" for k in ("yday", "pweek", "month", "prev")),
   all(P.get(k) for k in ("yday", "pweek", "month", "prev")) and "البارحة" in P["yday"]["period"] and "←" not in P["yday"]["period"]
   and "الأسبوع السابق" in P["pweek"]["period"] and "←" in P["pweek"]["period"] and "الشهر الحالي" in P["month"]["period"]
   and "الشهر السابق" in P["prev"]["period"] and "←" in P["prev"]["period"]
   and [P[k]["on"] for k in ("yday", "pweek", "month", "prev")] == ["البارحة", "الأسبوع السابق", "الشهر الحالي", "الشهر السابق"]
   and P["yday"]["hero"] == f"+{DAILY[yd.strftime('%Y-%m-%d')]:.2f}$", P)
ok("… no page error", not U.get("errs") and not U.get("err"), (U.get("errs"), U.get("err")))
shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_card_periods: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
