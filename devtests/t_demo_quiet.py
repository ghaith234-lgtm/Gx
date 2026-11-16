# 🧪 v3.36.59 — the demo makes no notification and its card shows its own profit (p100). The owner (16-11): «الديمو خلي الربح داخل
#   الكرتات … وما اريد اشعارات لانه حساب ديمو». A closed folder (no network · nothing launched): a real bot and a demo bot of each
#   kind that matters, the dashboard's own functions:
#   · every notification path is caught where it leaves (app_feed_push — tg_send calls it before Telegram): the card's buttons
#     (▶️ · ⏹ · 💠 · ⚖️ …) · 🗑 delete · ♻️ rebuild · the watchdog (at start and when a bot falls) · «🏁 آخر دورة» · the counts in
#     «⚡ فتح التطبيق» · «⏻ توقف» · «🛑 إغلاق» · «🧬 تحديث المحرك» — a demo: nothing · a real bot: its message as before
#   · the quiet context is per thread and restores itself (an exception inside does not leave it on)
#   · the card: a demo grid's «اليوم» from its own log × the net factor · its rates from its own profit · a real bot still from the books
#   python3 devtests/t_demo_quiet.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, threading, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="t_dq_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_dq", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dq", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.ROOT = R
SENT = []
m.app_feed_push = lambda text, *a, **k: SENT.append(str(text))      # every notification passes here first (then Telegram)
m.launch = lambda b: (True, "test")
m._okx_get = lambda *a, **k: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("devtests: no orders"))
TODAY = time.strftime("%Y-%m-%d")


def mk(folder, sym, bt, demo, state=None, hist=None, extra=None):
    d = os.path.join(R, folder)
    os.makedirs(d, exist_ok=True)
    cfg = {"symbol": sym, "bot_type": bt, "auto_restart": True, "is_demo": demo, "grid_percentage": 0.006, "usd_value": 10,
           "api_key": "" if demo else "k-dq", "secret_key": "" if demo else "s-dq", "passphrase": "" if demo else "p-dq"}
    cfg.update(extra or {})
    json.dump(cfg, open(os.path.join(d, f"config_{sym}.json"), "w"))
    b = {"dir": d, "symbol": sym, "cfg": cfg, "cfg_path": os.path.join(d, f"config_{sym}.json")}
    sp, hp, _ = m.paths_of(b)
    json.dump(state or {"status": "running"}, open(sp, "w"))
    json.dump(hist or [], open(hp, "w"))
    return b


def bot(folder):
    return m.bot_dirs()[os.path.realpath(os.path.join(R, folder))]


def said(sym):
    return [t for t in SENT if sym in t]


now = time.strftime("%Y-%m-%d %H:%M:%S")
HIST = [{"time": now, "msg": "🔴 [بيع فوري] السعر: 81.44 | الكمية: 0.1243 | الربح: +0.1192$ -> تم تجهيز شراء بسعر: 80.48"},
        {"time": now, "msg": "🔴 [بيع فوري] السعر: 80.96 | الكمية: 0.125 | الربح: +0.1199$ -> تم تجهيز شراء بسعر: 80.0"},
        {"time": "2020-01-01 10:00:00", "msg": "🔴 [بيع فوري] السعر: 70 | الكمية: 0.1 | الربح: +5.0$"}]
mk("demo_sol_aaaaaa", "SOL-USDT", "grid_plus", True, {"status": "running", "total_profit": 5.2391}, HIST)
mk("xrp_bbbbbb", "XRP-USDT", "grid_plus", False, {"status": "running", "total_profit": 3.0}, HIST)
mk("demo_ada_cccccc", "ADA-USDT", "dca", True, {"status": "running", "phase": "finished", "finished_at": time.time(), "total_coin_profit": 0.5,
                                                   "cycles_done": 2})
mk("dot_dddddd", "DOT-USDT", "dca", False, {"status": "running", "phase": "finished", "finished_at": time.time(), "total_coin_profit": 0.7,
                                            "cycles_done": 3})
DS, RX = "demo_sol_aaaaaa", "xrp_bbbbbb"

# ① the card's buttons
m.is_alive = lambda d, sp: (False, "")
for act, val in (("stop", None), ("start", None), ("auto", None), ("reinvest", None), ("ri_pct", "50")):
    SENT.clear()
    m.is_alive = (lambda d, sp: (True, "x")) if act == "reinvest" else (lambda d, sp: (False, ""))   # 💠 restarts a running bot (and says so)
    m.control(DS, act, val)
    d_said = said("SOL-USDT") + [t for t in SENT if "SOL" in t]
    m.control(RX, act, val)
    ok(f"① «{act}» on the card: the demo — nothing left ({len(d_said)}) · the real bot — as before ({len(said('XRP-USDT'))})",
       not d_said and (act in ("auto",) or said("XRP-USDT")), SENT)
# the quiet state never stays on after a button
SENT.clear(); m.tg_send("🧪 real after demo"); ok("… and a notification right after a demo's button still leaves", SENT == ["🧪 real after demo"], SENT)

# ⑥ the card's profit
m.is_alive = lambda d, sp: (True, "x")
sd = m.bot_snapshot(bot(DS))
nf = m.net_factor(bot(DS))
exp = round((0.1192 + 0.1199) * nf, 4)
ok(f"⑥ the demo grid's «اليوم» = today's profits from its own log × the net factor ({sd['today']} = {exp}) · the old day not counted",
   abs(sd["today"] - exp) < 1e-4, (sd["today"], exp))
sr = m.bot_snapshot(bot(RX))
ok(f"… the real grid's «اليوم» still from the books ({sr['today']} — no book entry here)", sr["today"] == 0, sr["today"])
bd = dict(sd, bot_type="grid_plus", age_days=2.0)
m._rate_fix(bd, {})
br = dict(sr, bot_type="grid_plus", age_days=2.0)
m._rate_fix(br, {})
ok(f"… the rates: the demo from its own profit ({bd['rate_trade']} ÷ 2 days = {bd['rate_daily']}) · the real one from the books ({br['rate_trade']})",
   abs(bd["rate_trade"] - sd["profit"]) < 1e-9 and abs(bd["rate_daily"] - sd["profit"] / 2) < 1e-9 and br["rate_trade"] == 0, (bd["rate_trade"], br["rate_trade"]))

# ② ♻️ rebuild · 🗑 delete
SENT.clear(); m.rebuild(bot(DS)); m.rebuild(bot(RX))
ok("② ♻️ rebuild: the demo silent · the real one «إعادة بناء»", not said("SOL-USDT") and any("إعادة بناء" in t for t in said("XRP-USDT")), SENT)

# ③ the watchdog: at start (both down · auto) and when a bot falls
SENT.clear()
m.WATCHDOG["on"] = True
for f in (DS, RX):
    m.write_cfg_keys(bot(f)["cfg_path"], {"auto_restart": True})
m.is_alive = lambda d, sp: (False, "")
th = threading.Thread(target=m.watchdog_loop, daemon=True); th.start()
t0 = time.time()
while time.time() - t0 < 30 and not any("طاح" in t for t in said("XRP-USDT")):
    time.sleep(0.3)
time.sleep(1.0)
ok(f"③ the watchdog relaunched both (at start and after a fall) · the real one told ({len(said('XRP-USDT'))}) · the demo silent ({len(said('SOL-USDT'))})",
   any("عند الإقلاع" in t for t in said("XRP-USDT")) and any("طاح" in t for t in said("XRP-USDT")) and not said("SOL-USDT"), SENT[:6])
ok("… «🏁 آخر دورة انتهت»: the real DCA told · the demo DCA silent (both stopped all the same)",
   any("آخر دورة" in t for t in said("DOT-USDT")) and not said("ADA-USDT")
   and not bot("demo_ada_cccccc")["cfg"].get("auto_restart") and not bot("dot_dddddd")["cfg"].get("auto_restart"), SENT)
m.WATCHDOG["on"] = False

# ④ the counts: real bots only
SENT.clear()
m.is_alive = lambda d, sp: (True, "x")
m.stop_all_bots("اختبار")
ok("④ «⏻ توقف N بوت»: counts the real bots only (2 real · 2 demo alive ⇒ «2»)", any("توقف 2 بوت" in t for t in SENT), SENT)
m.is_alive = lambda d, sp: (False, "")
n = m.start_all_bots()
ok(f"… start all: {n} started · «فتح التطبيق» would say {m._START_N['real']} (the real ones)", n == 4 and m._START_N["real"] == 2, (n, m._START_N))
SENT.clear()
m.shutdown_all(noexit=True) if False else None
m.is_alive = lambda d, sp: (True, "x")
m.shutdown_all(noexit=True)
ok("… «🛑 إغلاق مركز التحكم — تم إيقاف N بوت»: the real ones (2)", any("إيقاف `2` بوت" in t for t in SENT), SENT)
SENT.clear()
m.upgrade_engines()
ok("… «🧬 تحديث المحرك»: names the real bots only", any("🧬" in t for t in SENT) and not any(("SOL-USDT" in t or "ADA-USDT" in t) for t in SENT if "🧬" in t), SENT)

# ⑤ the context: per thread · restores itself after an exception
SENT.clear()
try:
    with m._demo_quiet(bot(DS)):
        m.tg_send("x1", force=True)
        raise ValueError("inside")
except ValueError:
    pass
m.tg_send("x2")
other = []
with m._demo_quiet(bot(DS)):
    th2 = threading.Thread(target=lambda: other.append(m.tg_send("x3")))
    th2.start(); th2.join()
ok("⑤ the quiet context: nothing inside (even «force») · off again after an exception · another thread is not silenced",
   SENT == ["x2", "x3"], SENT)

# ⑦ 🗑 delete (last: it moves the folders)
SENT.clear(); m.delete_bot(bot(DS)); m.delete_bot(bot(RX))
ok("⑦ 🗑 delete: the demo silent · the real one «حذف (أرشفة)»", not said("SOL-USDT") and any("حذف" in t for t in said("XRP-USDT")), SENT)

# ⑧ the source: every tg_send inside a per-bot loop of the watchdog/last cycle is the demo-aware one
src = open(DASH, encoding="utf-8").read()
seg = src.split("def watchdog_loop():", 1)[1].split("\ndef ", 1)[0]
ok("⑧ the watchdog's per-bot messages all go through _tg_b (demo-aware)", "tg_send(" not in seg.replace("_tg_b(", ""), seg.count("tg_send("))
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_demo_quiet: {sum(res)}/{len(res)}" if res and all(res) else f"❌ t_demo_quiet: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
