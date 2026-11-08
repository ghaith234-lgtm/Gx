# 🧪⏩ the 🪜 trial path runs fast and shows its progress — the owner (7-11/8): «المتدرج عند فحص المسار التجريبي … يضل ينتظر ما يشتغل
#   ما اعرف فيه تأخير ام ما يشتغل». It ran, but the box walked every virtual second for the 🪜 (its engine sleeps 1 s a turn): a week
#   ≈ 9 minutes, a month ≈ 40, a year ≈ 7 hours per path, with «⏳ يحضّر المحرك…» on the screen the whole time.
#   A closed folder · fake keys · no network (the trial worker seals itself) · the owner's settings (25$ · 3 parts 0.45/0.15 · 0.6% ·
#   1 level from coins · reinvest 100%):
#   ① the same path, the box as it was (every second) vs now (6 s of live pace per price point, then the next point): the SAME fills
#      (side · price · size, in order) and the same wallet to the last digit — at the week's step (60 s) with reinvest and at the
#      month's step (300 s) without · now at least ×5 faster
#   ② only the 🪜 gets it: a ♾️ grid in the box keeps settle 0 (one look per point as before)
#   ③ a real trial (bt_start → the worker process → bt_status): a week path ends in under 150 s (was ≈ 536) · while it runs the status
#      carries the progress (0 < prog < 1) and a time left · then «done» with its result
#   ④ the bar in a real browser: «⏳ يعمل المحرك على المسار — 37% · المتبقي ≈ 0:42» (was «⏳ يحضّر المحرك…» until a path ended)
#   python3 devtests/step/t_btfast.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR` for ④)
import importlib.machinery, importlib.util, json, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_btfast_")
json.dump({"port": 8093}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-btfast", "sec": "SECA-btfast", "pass": "PASA-btfast"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_btfast", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_btfast", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None)
m._okx_get = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
P0 = 1.1698
m.PX["XRP-USDT"] = P0
BODY = {"symbol": "XRP-USDT", "usd_value": "25", "step_parts": "3", "step_sell_pct": "0.15", "step_first_pct": "0.45", "grid_pct": "0.6",
        "min_price": "0.9", "up_groups": "1", "forced_base": "", "wallet": "main", "auto": False, "reinvest": True, "reinvest_pct": "100"}
PREP = m.bt_prep({"kind": "grid_step", "body": BODY})
SPEC = PREP["spec"]
KEEP = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
        if hasattr(m, k)}


def dry(kind, body):
    c, e = m._bt_dry_cfg(kind, body, "XRP-USDT", SPEC, P0)      # (made for the separate worker: it swaps module globals — put back)
    for k, v in KEEP.items():
        setattr(m, k, v)
    return c, e


OLD_SLEEP = m._BtClock.sleep


def every_second(self, s):                                     # the box's clock before v3.36.25: jumps only on a sleep of ≥ 2 s
    try:
        s = max(0.0, float(s or 0))
    except Exception:
        s = 0.0
    with self.lk:
        t = self.t + s
        if s >= self.JUMP:
            t = max(t, self._next())
        self._go(t)


def run(kind, cfg, days, dt, seed, slow):
    px = m._bt_path(P0, days, dt, 0.045, seed)
    m._BtClock.sleep = every_second if slow else OLD_SLEEP
    t0 = time.time()
    r = m._bt_run(kind, cfg, "XRP-USDT", px, dt, float(PREP["quote_def"]), float(PREP["base_def"]), SPEC)
    m._BtClock.sleep = OLD_SLEEP
    ex = r["ex"]
    return {"secs": time.time() - t0, "fills": [(f[1], repr(float(f[2])), repr(float(f[3]))) for f in ex.fills],
            "q": ex.bal[ex.quote], "b": ex.bal[ex.base], "why": r["why"], "rej": len(ex.rejects)}


# ── ① slow vs fast on the same path
for lbl, ri, days, dt, seed in (("the week's step (60 s) · reinvest 100% · 12 hours", True, 0.5, 60, 7),
                                ("the month's step (300 s) · no reinvest · a day and a half", False, 1.5, 300, 3)):
    cfg, err = dry("grid_step", dict(BODY, reinvest=ri))
    if not cfg:
        ok(f"① {lbl}: the settings", False, err); continue
    a, b = run("grid_step", cfg, days, dt, seed, slow=True), run("grid_step", cfg, days, dt, seed, slow=False)
    ok(f"① {lbl}: the same path every second vs now — the SAME {len(a['fills'])} fills in order · the same wallet "
       f"({a['q']:.6f}$ · {a['b']:.8f} XRP) · ×{a['secs'] / max(b['secs'], 1e-3):.0f} faster ({a['secs']:.0f} s ⇒ {b['secs']:.1f} s)",
       len(a["fills"]) >= 10 and a["fills"] == b["fills"] and a["q"] == b["q"] and a["b"] == b["b"] and a["why"] == b["why"] == "end"
       and not a["rej"] and not b["rej"] and a["secs"] >= 5 * b["secs"], {"slow": {k: a[k] for k in ("secs", "q", "b", "why", "rej")}, "n": (len(a["fills"]), len(b["fills"])),
                                                                         "fast": {k: b[k] for k in ("secs", "q", "b", "why", "rej")}})

# ── ② only the 🪜
seen = []
_init = m._BtClock.__init__


def rec_init(self, *a, **k):
    _init(self, *a, **k)
    seen.append(self)


m._BtClock.__init__ = rec_init
gcfg, gerr = dry("grid", {"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "min_price": "0.9", "wallet": "main", "g_type": "grid"})
g = run("grid", gcfg, 0.5, 60, 7, slow=False) if gcfg else {}
scfg, _ = dry("grid_step", BODY)
run("grid_step", scfg, 0.02, 60, 7, slow=False)
m._BtClock.__init__ = _init
ok("② only the 🪜 gets the live-pace window: a ♾️ grid in the box keeps settle 0 (one look per point, as before) · the 🪜 6 s",
   len(seen) == 2 and getattr(seen[0], "settle", None) == 0 and getattr(seen[1], "settle", None) == getattr(m, "_BT_SETTLE", None) == 6.0
   and g.get("why") == "end", [(getattr(c, "settle", None)) for c in seen])

# ── ③ a real trial through the worker process
S = m.bt_start({"kind": "grid_step", "body": BODY, "period": "week", "mood": "normal", "paths": 1, "seed": "7", "p0": PREP["p0"],
                "quote": PREP["quote_def"], "base": PREP["base_def"], "maker": "0.08", "taker": "0.1", "slip": "0.05"})
t0, mid, last = time.time(), [], {}
while S.get("ok") and time.time() - t0 < 300:
    last = m.bt_status({"id": S["id"]})
    if last.get("state") == "run" and last.get("prog") is not None and 0 < last["prog"] < 1:
        mid.append((round(time.time() - t0), last["prog"], last.get("eta")))
    if last.get("state") in ("done", "error", "stopped", "lost"):
        break
    time.sleep(1)
took = time.time() - t0
p = (last.get("paths") or [{}])[0].get("sum") or {}
ok(f"③ a real trial (the worker process): a week path ends in {took:.0f} s (was ≈ 536) · {len(mid)} looks while running with the progress "
   f"({', '.join(f'{x[1]:.0%}' for x in mid[::max(1, len(mid) // 5)])}) and a time left · then «done» · {p.get('buys')} buys / {p.get('sells')} sells",
   S.get("ok") and last.get("state") == "done" and took < 150 and len(mid) >= 2 and any(x[2] is not None for x in mid)
   and all(mid[i][1] <= mid[i + 1][1] for i in range(len(mid) - 1)) and (p.get("sells") or 0) > 20, (S, last.get("state"), last.get("err"), mid[:6], took))
if S.get("ok"):
    m.bt_stop({"id": S["id"]})

# ── ④ the bar in a real browser
os.chdir(cwd0)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); pp = s.getsockname()[1]; s.close(); return pp


R2 = tempfile.mkdtemp(prefix="t_btfast_ui_")
P1 = port()
shutil.copy(DASH, os.path.join(R2, "Holy_Dashboard.pyw"))
json.dump({"port": P1}, open(os.path.join(R2, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R2, "monitor_config.json"), "w"))
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
JS = r"""
const { chromium } = require('playwright');
(async () => {
  const br = await chromium.launch(); const pg = await br.newPage();
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof btProg === 'function', null, { timeout: 30000 });
  const t = await pg.evaluate(() => { const d = document.createElement('div'); d.id = 'bt_prog'; document.body.appendChild(d); const o = [];
    btProg({ state: 'run', done: 0, total: 1, prog: 0, eta: null }); o.push(d.innerText);
    btProg({ state: 'run', done: 0, total: 1, prog: 0.37, eta: 42 }); o.push(d.innerText);
    btProg({ state: 'run', done: 2, total: 5, prog: 0.5, eta: 90 }); o.push(d.innerText); return o });
  console.log(JSON.stringify(t)); await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
"""
jsf = os.path.join(R2, "bar.js"); open(jsf, "w").write(JS)
d = None
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_dash.py"), R2, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", jsf, f"http://127.0.0.1:{P1}/"], capture_output=True, text=True, timeout=120, cwd="/tmp", env=env)
    T = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"err": r.stderr[-500:]}
except Exception as e:
    T = {"err": repr(e)}
finally:
    if d:
        d.kill()
ok("④ the bar in a real browser: before the first number «⏳ يحضّر المحرك…» · then «⏳ يعمل المحرك على المسار — 37% · المتبقي ≈ 0:42» · "
   "with paths done «✅ 2 من 5 مسار · 50%»",
   isinstance(T, list) and "يحضّر المحرك" in T[0] and "يعمل المحرك على المسار" in T[1] and "37%" in T[1] and "0:42" in T[1]
   and "2 من 5 مسار" in T[2] and "50%" in T[2], T)
shutil.rmtree(R, ignore_errors=True)
shutil.rmtree(R2, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_btfast: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
