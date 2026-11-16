# 💵 the dollar outage — the wallet's rules (v3.36.44 · p70 · ⏳ v3.36.58 · p99) — the owner (14-11): «عند نزول السعر ونفاذ الدولار يضل البوتات تصرخ تريد دولار» ⇒ «ثلاثتهم
#   طبقهم · ايقاف الشراء اعلى بشوي حتى لو مسوي ايقاف شراء قبل وبوت اخر اخذ الدولار او نصرف يتحرك · … تنبيه بشكل ايموجي بالكرت».
#   ⏳ v3.36.58: the bots' side (the temporary buy pause — closing from the gap start · no calling · the sell DCA's dollars reserved ·
#   opened by the owner · power cuts) is devtests/t_temp_pause.py on the real engines. Here, the wallet's rules:
#   · the balance flapping 3$ ⇄ 12$ opens no second message · the sell DCA's dollars don't count as free (the message says how much)
#   · the owner's own floor above the temporary one: kept as his valve · the dollars back open nothing · «🔓» leaves his floor
#   · ▶️ on the card while closed moves his valve only · the wallet message stays in 🛡️ without Telegram while the temporary pause is
#     on (with it off: once, no reminders) · the recurring bot's «الرصيد لا يكفي»: once, then quiet until a buy goes through · the 🔔
#     centre hides the engines' dollar lines while the wallet message is open · the card chips (the page's own function, in node)
#   python3 devtests/t_cash_watch.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, re, shutil, subprocess, sys, tempfile, urllib.request

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

R = tempfile.mkdtemp(prefix="t_cashw_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_cashw", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_cashw", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
TG = []
m.tg_send = lambda t, *a, **k: TG.append(str(t)) or True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the dashboard placed/canceled an order"))
WID, QC = "w1", "USDT"


def wallet(g, av, now, mn=10.0):
    W = g["wallets"].setdefault(WID, {"label": "main", "coins": {}, "quotes": {}, "orders": {"missing": {}, "stray": {}}})
    rec = W["quotes"].setdefault(QC, {})
    rec.update(avail=float(av), cash=float(av), frozen=0.0, okx_frozen=None, bots_frozen=0.0, min_next=float(mn), ts=now)
    return rec


def round_(g, snap, av, now, mn=10.0):
    rec = wallet(g, av, now, mn)
    m._cw_low(g, WID, QC, rec, snap, now)
    m._cash_watch(g, now, [snap])
    return rec


def evs(g, kind):
    return [e for e in g["events"] if e.get("kind") == kind]


# ═══════════ B · the rules one by one (bot folders with a state file — no engine) ═══════════
SYM = "SOL-USDT"
CFG = {"grid_percentage": 0.006, "usd_value": 10.0, "min_price": 60.0, "forced_base_price": 80.0, "knife_guard": False,
       "bot_type": "grid_plus", "lower_price": 0.0, "upper_price": 0.0, "buy_offset": 0.012}
B = os.path.join(R, "bots")
os.makedirs(B, exist_ok=True)
m.ROOT = R
m.CASHW_FILE = os.path.join(R, "Holy_CashWatch.json")


def mkbot(name, floor=0.0, cp=74.0, buys=4):
    d = os.path.join(B, name)
    os.makedirs(d, exist_ok=True)
    st = {"buy_floor": floor, "pause_buy": False, "current_price": cp,
          "limit_buys": {f"o{j}": {"target_price": round(cp * (1 - 0.006 * (j + 1)), 4), "locked_qty": 0.13} for j in range(buys)}}
    json.dump(st, open(os.path.join(d, f"grid_state_{SYM}.json"), "w"))
    return d


def stf(d):
    return json.load(open(os.path.join(d, f"grid_state_{SYM}.json"), encoding="utf-8"))


def snapof(ds, cp=74.0):
    return {"wid": WID, "ok_bal": True, "bots": {os.path.basename(d): {"dir": d, "sym": SYM, "type": "grid_plus", "quote": QC, "usd": 10.0,
                                                                         "cp": cp, "g": 0.006, "alive": True, "destruct": False} for d in ds}}


def fresh():
    if os.path.exists(m.CASHW_FILE):
        os.remove(m.CASHW_FILE)
    m._CW_CACHE.update(sig=None, d=None)
    shutil.rmtree(B, ignore_errors=True)
    os.makedirs(B, exist_ok=True)
    return m._gd_empty()


T = m.time.time()                 # the guard's events carry the real clock
# flapping
g = fresh()
d1 = mkbot("p1")
m.bot_dirs = lambda: {d1: {"dir": d1, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
for j, av in enumerate([3, 12, 3, 12, 3, 12, 3]):
    round_(g, snapof([d1]), av, T + j * 600)
ok("B · the balance flapping 3$ ⇄ 12$ every 10 minutes: one message, no «back», nothing sent twice",
   len(evs(g, "low_quote")) == 1 and not evs(g, "quote_back") and evs(g, "low_quote")[0]["status"] == "open", [(e["title"], e["status"]) for e in g["events"]])
# the owner's own floor (76) above the temporary one — his valve
g = fresh()
d2 = mkbot("own", floor=76.0, cp=74.0)
m.bot_dirs = lambda: {os.path.realpath(d2): {"dir": d2, "symbol": SYM, "cfg": dict(CFG, symbol=SYM), "cfg_path": os.path.join(d2, f"config_{SYM}.json")}}
round_(g, snapof([d2], 74.0), 3, T)
round_(g, snapof([d2], 74.0), 3, T + 600)
r2 = m._cw_load()["bots"].get(m._cw_key(d2)) or {}
f_a = stf(d2)["buy_floor"]
for j in range(5):
    round_(g, snapof([d2], 74.0), 300, T + 1200 + j * 600)
f_b = stf(d2)["buy_floor"]
r_own = m.control(os.path.relpath(d2, R), "temp_open", None)
f_c = stf(d2)["buy_floor"]
ok(f"… the owner's floor (76) above the temporary one: kept as his valve (own {r2.get('own')} · temp {r2.get('temp')} · the engine {f_a}) · the dollars "
   f"back open nothing ({f_b}) · «🔓 افتح المؤقت» leaves his floor ({f_c} · «{r_own.get('msg', '')[:60]}»)",
   r2.get("own") == 76.0 and 0 < r2.get("temp", 0) < 76 and f_a == 76.0 and f_b == 76.0 and f_c == 76.0 and r_own.get("ok")
   and not m._cw_load()["bots"].get(m._cw_key(d2)), (r2, f_a, f_b, f_c, r_own))
# the sell DCA's dollars are reserved
g = fresh()
d9 = mkbot("dcar")
m.bot_dirs = lambda: {d9: {"dir": d9, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
rec9 = wallet(g, 205.0, T)
rec9["dca_hold"] = 200.0
m._cw_low(g, WID, QC, rec9, snapof([d9]), T)
m._cash_watch(g, T, [snapof([d9])])
lowd = (evs(g, "low_quote") or [{}])[0].get("detail", "")
ok("… 205$ free of which 200$ belong to a sell DCA: the wallet message opens (5$ unreserved < 10$) and says the 200$ are reserved · the bot closes "
   "at the first round (a reserve in the wallet)", "200.00 محجوز لـ DCA البيعي" in lowd and m._cw_load()["bots"].get(m._cw_key(d9)), (lowd, m._cw_load()["bots"]))
# the owner presses ▶️ on the card while closed — his valve only
g = fresh()
d3 = mkbot("touch")
m.bot_dirs = lambda: {os.path.realpath(d3): {"dir": d3, "symbol": SYM, "cfg": dict(CFG, symbol=SYM), "cfg_path": os.path.join(d3, f"config_{SYM}.json")}}
round_(g, snapof([d3]), 3, T)
round_(g, snapof([d3]), 3, T + 600)
f1 = stf(d3)["buy_floor"]
r_res = m.control(os.path.relpath(d3, R), "accum_buy", 0)
f2 = stf(d3)["buy_floor"]
ok(f"… ▶️ on the card while the temporary valve is closed: «{r_res.get('msg', '')[:70]}» · the engine's floor unchanged ({f1} ⇒ {f2})",
   f1 > 0 and f2 == f1 and "المؤقت" in r_res.get("msg", ""), (f1, f2, r_res))
# Telegram: the wallet message stays in 🛡️ while the temporary pause is on · with it off: once, no reminders
g = fresh()
d4 = mkbot("rem")
m.bot_dirs = lambda: {d4: {"dir": d4, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
round_(g, snapof([d4]), 3, T)
out_on = [x for x in m._gd_outbox(g, m.time.time()) if x[0] == "ev" and "نفد الدولار" in x[-1]]
g = fresh()
g["cash_pause"] = False
round_(g, snapof([d4]), 3, T)
out1 = [x for x in m._gd_outbox(g, m.time.time()) if x[0] == "ev" and "نفد الدولار" in x[-1]]
for e in g["events"]:
    if e.get("id") in {x[1] for x in out1}:
        e["tg"] = True
round_(g, snapof([d4]), 3, T + 86400 + 60)
out2 = [x for x in m._gd_outbox(g, m.time.time() + 86400 + 60) if x[0] == "ev" and "الدولار" in x[-1]]
ok(f"… Telegram: the wallet message stays in 🛡️ while the temporary pause is on ({len(out_on)}) · with it off: once ({len(out1)}) and no reminder a day later ({len(out2)})",
   not out_on and len(out1) == 1 and not out2, (out_on, out1, out2))
# the recurring bot's «not enough dollars»
TG.clear()
m.REC_TG_FILE = os.path.join(R, "rec_tg.json")
rb = {"dir": os.path.join(B, "rec"), "symbol": SYM, "cfg": {"bot_type": "rec_buy", "symbol": SYM, "bot_id": "R1", "amount": 10}}
os.makedirs(rb["dir"], exist_ok=True)
EVR = []


def rec_ev(k, **kw):
    EVR.append(dict({"id": f"R1-E{len(EVR) + 1}", "k": k, "ts": m.time.time(), "why": kw.pop("why", None)}, **kw))
    m._rec_notify(rb, {"events": list(EVR), "ev_n": len(EVR)})


m._rec_notify(rb, {"events": [], "ev_n": 0})
for _ in range(4):
    rec_ev("skip", why="balance", need=10)
n_a = sum("الرصيد لا يكفي" in t for t in TG)
rec_ev("open", q=0.13, c=10, px=74)
rec_ev("skip", why="balance", need=10)
n_b = sum("الرصيد لا يكفي" in t for t in TG)
ok(f"… the recurring bot's «تخطّى … الرصيد لا يكفي»: once for 4 schedules ({n_a}) · again only after a buy went through ({n_b})", n_a == 1 and n_b == 2, TG[-4:])
# the 🔔 centre
g = fresh()
d6 = mkbot("feed")
lines = [{"time": "2026-11-14 05:30:00", "msg": "💵 [شراء مجمّع] دولارك الحر 3.0$ ما يكفي ولا درجة من 11"},
         {"time": "2026-11-14 05:31:00", "msg": "⚠️ [رفض أمر شراء] كمية (0.12) بسعر (79.52): Order failed. Insufficient USDT balance in account"},
         {"time": "2026-11-14 05:32:00", "msg": "🔴 [بيع فوري] السعر: 81.2 | الكمية: 0.12 | الربح: +0.05$"}]
json.dump(lines, open(os.path.join(d6, "trade_history_SOL.json"), "w"))
m.bot_dirs = lambda: {d6: {"dir": d6, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
m.acc_cfgs = lambda: []
f_open = None
round_(g, snapof([d6]), 3, T)
f_open = [x["msg"][:30] for x in m.feed_all() if x.get("sym") == SYM and x.get("dir")]
for j in range(5):
    round_(g, snapof([d6]), 300, T + 600 + j * 600)
f_back = [x["msg"][:30] for x in m.feed_all() if x.get("sym") == SYM and x.get("dir")]
ok("… the 🔔 centre: while the wallet message is open the engines' dollar lines stay in the bot's 📜 log only (the sell still shows) · back once it closes",
   len(f_open) == 1 and "بيع" in f_open[0] and len(f_back) == 3, (f_open, f_back))
# the card chip — the page's own function, run in node
page = open(DASH, encoding="utf-8").read()
js = page[page.index("function accChipsOf(b){"):]
js = js[:js.index("\nfunction accumPrompt(")]
try:
    out = subprocess.run(["node", "-e", "function f4(v){return (+v).toFixed(4)}\n" + js + "\nconst r=[accChipsOf({dir:'b0',cashw:{tp:true,temp:79.5,own:0,n:5,k:0}}),accChipsOf({cashw:{need:12.5,auto:false}}),accChipsOf({cashw:null})];"
                          "console.log(JSON.stringify(r))"], capture_output=True, text=True, timeout=30)
    C = json.loads(out.stdout.strip().splitlines()[-1])
except Exception as e:
    C = [str(e), "", "x"]
ok("③ the card chip (the page's function): «⏳ مؤقت (5)» while closed · «🟠 ينتظر دولار — يحتاج $12.50» (waiting, not closed) · nothing without a wait",
   "⏳ مؤقت (5)" in C[0] and "tempOpen('b0')" in C[0] and "يحتاج $12.50<" in C[1] and "⏸<" not in C[1] and C[2] == "", C)
ok("no order placed or cancelled by the dashboard (only control fields)", True)
print(f"✅ t_cash_watch: {sum(res)}/{len(res)}" if all(res) else f"❌ t_cash_watch: {sum(res)}/{len(res)}")
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
