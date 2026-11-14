# 💵 the dollar outage (v3.36.44 · p70) — the owner (14-11): «عند نزول السعر ونفاذ الدولار يضل البوتات تصرخ تريد دولار» ⇒ «ثلاثتهم
#   طبقهم · ايقاف الشراء اعلى بشوي حتى لو مسوي ايقاف شراء قبل وبوت اخر اخذ الدولار او نصرف يتحرك · … تنبيه بشكل ايموجي بالكرت».
#   A · the real ➕ engine in the trial sandbox (closed folder · fake clock · fake OKX · no network) with the guard's dollar round every
#       10 minutes (the same functions the 🛡️ scan calls): the price falls · another bot takes the dollars · the price climbs back ·
#       the dollars come back:
#       ① one «💵 نفد الدولار الحر» for the wallet (which bot waits · what it needs) and one «✅ عاد الدولار الحر» — nothing between
#       ② ⏸ after two scans the floor goes a little ABOVE the price · OKX refuses no buy while it waits · the floor follows the price
#          up · the dollars the pulled orders freed are not «dollars back» · back for 30 minutes ⇒ the floor goes back (none) and the
#          engine buys the stored levels in one order
#       ③ the card says «🟠 ينتظر دولار — يحتاج X$» (⏸ automatic) and nothing once the dollars are back
#   B · the rules one by one: the balance flapping 3$ ⇄ 12$ opens no second message · the owner's own floor is kept and comes back ·
#       the owner presses ▶️ while paused ⇒ the system lets that bot alone · a daily reminder (and it is really sent) · the switch
#       off (or the guard paused — p71: at once) ⇒ the paused bots resume · the recurring bot's «الرصيد لا يكفي»: once, then quiet until a buy goes through · the 🔔
#       centre hides the engines' dollar lines while the wallet message is open · the card chip (the page's own function, in node)
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


# ═══════════ A · the real engine in the sandbox ═══════════
SYM, P0, DT = "SOL-USDT", 80.0, 60.0
px = [P0] * 200 + [P0 - 6.0 * i / 500 for i in range(1, 501)] + [74.0] * 300 + [74.0 + 5.6 * i / 300 for i in range(1, 301)] + [79.6] * 500
# (the climb ends at 79.6 — above the first floor ≈ 78.9 · under the plus bot's first inventory sell 80.48: no sell brings dollars back)
I_DRAIN, I_BACK = 300, 1350
CFG = {"grid_percentage": 0.006, "usd_value": 10.0, "min_price": 60.0, "forced_base_price": P0, "knife_guard": False,
       "bot_type": "grid_plus", "lower_price": 0.0, "upper_price": 0.0, "buy_offset": 0.012}
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
EV = {"folder": None, "log": [], "g": m._gd_empty(), "fl": [], "chip": [], "drained": 0.0, "at": {}}
_mk = m._bt_tmp.mkdtemp
m._bt_tmp.mkdtemp = lambda *a, **k: EV.__setitem__("folder", _mk(*a, **k)) or EV["folder"]
_rm = m.shutil.rmtree


def _keep(p, *a, **k):
    if EV["folder"] and os.path.abspath(p) == os.path.abspath(EV["folder"]):
        try:
            EV["log"] = json.load(open(os.path.join(p, "trade_history_SOL.json"), encoding="utf-8")) or []
        except Exception:
            EV["log"] = []
        try:
            EV["st"] = json.load(open(os.path.join(p, f"grid_state_{SYM}.json"), encoding="utf-8"))
        except Exception:
            EV["st"] = None
    return _rm(p, *a, **k)


m.shutil.rmtree = _keep
_Clock = m._BtClock


class Clock(_Clock):
    def __init__(self, ex, px_, t0, dt, on_point):
        def hook(i):
            on_point(i)
            f = EV["folder"]
            if not f:
                return
            if i == I_DRAIN:
                EV["drained"] = ex.bal[ex.quote] - 3.0
                ex.bal[ex.quote] = 3.0 + ex.frz[ex.quote]          # 🤝 another bot took the free dollars (3$ free left)
            if i == I_BACK:
                ex.bal[ex.quote] += 300.0                          # 💵 back
            if i % 10:
                return
            m.bot_dirs = lambda: {f: {"dir": f, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
            try:
                st = json.load(open(os.path.join(f, f"grid_state_{SYM}.json"), encoding="utf-8"))
            except Exception:
                return
            snap = {"wid": WID, "ok_bal": True, "bots": {"plus": {"dir": f, "sym": SYM, "type": "grid_plus", "quote": QC, "usd": 10.0,
                                                                   "cp": ex.p, "g": 0.006, "alive": True, "destruct": False}}}
            now = ex.now()
            round_(EV["g"], snap, ex.avail(ex.quote), now)
            st = json.load(open(os.path.join(f, f"grid_state_{SYM}.json"), encoding="utf-8"))
            EV["fl"].append((i, ex.p, float(st.get("buy_floor") or 0), ex.avail(ex.quote)))
            EV["chip"].append((i, m._cw_card(f)))
            for e in EV["g"]["events"]:
                EV["at"].setdefault(e.get("kind"), i)                   # the guard round where each message first appeared
        super().__init__(ex, px_, t0, dt, hook)


m._BtClock = Clock
r = m._bt_run("grid_plus", CFG, SYM, px, DT, 400.0, 6.0, SPEC, samples=400)
m._BtClock = _Clock
L, g, FL = EV["log"], EV["g"], EV["fl"]
idx = lambda e: (m.time.mktime(m.time.strptime(e["time"], "%Y-%m-%d %H:%M:%S")) - m._BT_T0) / DT
ok(f"A · the run reached its end ({r['i_end']}/{r['n']} points · {len(FL)} guard rounds)", r["i_end"] >= r["n"] - 1 and len(FL) > 150, r["why"])
low, back = evs(g, "low_quote"), evs(g, "quote_back")
ok("① one «💵 نفد الدولار الحر» message for the wallet (with the waiting bot and what it needs) and one «✅ عاد الدولار الحر»",
   len(low) == 1 and len(back) == 1 and "SOL ➕ (10$)" in low[0]["detail"] and low[0]["status"] == "resolved", [(e["title"], e["status"], e["detail"][:160]) for e in low + back])
t_low, t_back = EV["at"].get("low_quote", -1), EV["at"].get("quote_back", -1)
ok(f"… opened at the first round without dollars ({t_low:.0f}) and «back» only after 30 minutes of dollars ({t_back:.0f} ≥ {I_BACK + 30})",
   I_DRAIN <= t_low <= I_DRAIN + 10 and I_BACK + 30 <= t_back <= I_BACK + 40, (t_low, t_back))
fl_on = [(i, p, f) for i, p, f, a in FL if f > 0]
first = fl_on[0] if fl_on else None
ok("② ⏸ after two rounds the floor goes a little above the price (half a grid step)",
   first and I_DRAIN + 10 <= first[0] <= I_DRAIN + 20 and first[1] < first[2] <= first[1] * 1.0035, first)
rej = [(round((t - m._BT_T0) / DT), sc) for t, sc in r["ex"].rejects if sc == "51008"]
rej_wait = [x for x in rej if I_DRAIN + 20 <= x[0] < I_BACK]
ok(f"… while it waits OKX refuses no buy ({len(rej_wait)} refused between the pause and the dollars back · {len(rej)} in the whole run)", not rej_wait, rej[:10])
up = [(i, p, f) for i, p, f in fl_on if 1000 <= i < I_BACK]
ok("… the floor follows the price up (74 ⇒ 79.6 — past the first floor) and stays above it", up and up[-1][2] > up[0][2] * 1.005
   and all(f >= p * 0.998 for i, p, f in up),
   (up[:2], up[-2:]))
heldv = [(i, a) for i, p, f, a in FL if I_DRAIN + 30 <= i < I_BACK]
ok("… the pulled orders' dollars show in the wallet but are not «dollars back» (no «back» before the deposit)",
   heldv and max(a for _, a in heldv) > 10 and t_back >= I_BACK, heldv[:3])
rest = [(i, f) for i, p, f, a in FL if i >= I_BACK + 40]
ok("… back for 30 minutes ⇒ the floor goes back (it had none)", rest and all(f == 0 for i, f in rest), rest[:3])
res_l = [e["msg"] for e in L if "[استئناف الشراء]" in e["msg"] or "[إعادة نشر]" in e["msg"]]
st_end = EV.get("st") or {}
ok("… and the engine takes its stored levels back (the price climbed above them ⇒ they return to their places as buy orders — none bought dearer) · "
   "the store empty · buy orders live again", res_l and all(idx(e) >= I_BACK + 30 for e in L if "[استئناف الشراء]" in e["msg"] or "[إعادة نشر]" in e["msg"])
   and not (st_end.get("accum_buys") or {}) and (st_end.get("limit_buys") or {}) and not float(st_end.get("buy_floor") or 0),
   (res_l, len(st_end.get("accum_buys") or {}), len(st_end.get("limit_buys") or {})))
ch_w = [c for i, c in EV["chip"] if I_DRAIN + 20 <= i < I_BACK]
ch_b = [c for i, c in EV["chip"] if i >= I_BACK + 40]
ok("③ the card: «🟠 ينتظر دولار — يحتاج 10$ · ⏸» while it waits · nothing once the dollars are back",
   ch_w and all(c and c["auto"] and c["need"] == 10 for c in ch_w) and ch_b and not any(ch_b), (ch_w[:2], ch_b[:2]))
dash = [e["msg"] for e in m.DASH_EVENTS]
ok("… and the 🔔 centre says it once each way (⏸ paused · ▶️ resumed)", sum("⏸💵" in x for x in dash) == 1 and sum("▶️💵" in x for x in dash) == 1, dash[:4])

# ═══════════ B · the rules one by one (bot folders with a state file — no engine) ═══════════
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
# the owner's own floor
g = fresh()
d2 = mkbot("own", floor=76.0, cp=74.0)
m.bot_dirs = lambda: {d2: {"dir": d2, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
_de0 = len(m.DASH_EVENTS)
round_(g, snapof([d2], 74.0), 3, T)
round_(g, snapof([d2], 74.0), 3, T + 600)
f_a = stf(d2)["buy_floor"]
_quiet = not any("⏸💵" in e["msg"] for e in m.DASH_EVENTS[:len(m.DASH_EVENTS) - _de0])
round_(g, snapof([d2], 79.0), 3, T + 1200)
f_b = stf(d2)["buy_floor"]
for j in range(5):
    round_(g, snapof([d2], 79.0), 300, T + 1800 + j * 600)
f_c = stf(d2)["buy_floor"]
ok(f"… the owner's floor (76, the price under it): kept while it is above the price ({f_a}) · moved up with the price ({f_b}) · back to 76 when the dollars are ({f_c})",
   f_a == 76.0 and 79.0 < f_b <= 79.0 * 1.0035 and f_c == 76.0, (f_a, f_b, f_c))
ok("… and while the owner's floor already covers the price nothing changed ⇒ no «⏸💵 أُوقف الشراء تلقائياً» line (p73)", _quiet,
   [e["msg"][:80] for e in m.DASH_EVENTS[:4]])
# the owner presses ▶️ while paused
g = fresh()
d3 = mkbot("touch")
m.bot_dirs = lambda: {d3: {"dir": d3, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
round_(g, snapof([d3]), 3, T)
round_(g, snapof([d3]), 3, T + 600)
f1 = stf(d3)["buy_floor"]
m.save_state_keys(os.path.join(d3, f"grid_state_{SYM}.json"), {"buy_floor": 0, "pause_buy": False})
for j in range(3):
    round_(g, snapof([d3]), 3, T + 1200 + j * 600)
f2 = stf(d3)["buy_floor"]
cw = m._cw_load()["bots"]
ok("… the owner presses ▶️ while it is paused ⇒ the system lets that bot alone (no new pause while the dollars stay out)",
   f1 > 74 and f2 == 0 and all(v.get("hands_off") for v in cw.values()), (f1, f2, cw))
# a reminder once a day — and it is really sent
g = fresh()
d4 = mkbot("rem")
m.bot_dirs = lambda: {d4: {"dir": d4, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
round_(g, snapof([d4]), 3, T)
out1 = [x for x in m._gd_outbox(g, T) if x[0] == "ev" and "نفد الدولار" in x[-1]]
for e in g["events"]:
    if e.get("id") in {x[1] for x in out1}:
        e["tg"] = True
round_(g, snapof([d4]), 3, T + 3600)
out2 = [x for x in m._gd_outbox(g, T + 3600) if x[0] == "ev" and "الدولار" in x[-1]]
round_(g, snapof([d4]), 3, T + 86400 + 60)
out3 = [x for x in m._gd_outbox(g, T + 86400 + 60) if x[0] == "ev" and "تذكير" in x[-1]]
ok("… Telegram: the message once · nothing an hour later · a «⏰ تذكير» a day later (and it goes out — not dropped as old)",
   len(out1) == 1 and not out2 and len(out3) == 1, (len(out1), [x[-1][:80] for x in out2], [x[-1][:80] for x in out3]))
# the switch off ⇒ resume
g = fresh()
d5 = mkbot("off")
m.bot_dirs = lambda: {d5: {"dir": d5, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
round_(g, snapof([d5]), 3, T)
round_(g, snapof([d5]), 3, T + 600)
f_on = stf(d5)["buy_floor"]
g["cash_pause"] = False
round_(g, snapof([d5]), 3, T + 1200)
f_off = stf(d5)["buy_floor"]
round_(g, snapof([d5]), 3, T + 1800)
ok("… 🛡️ the switch off ⇒ the paused bot resumes at the next round and is not paused again", f_on > 74 and f_off == 0 and stf(d5)["buy_floor"] == 0
   and not m._cw_load()["bots"], (f_on, f_off))
# ⏸️ the guard paused ⇒ no next round ⇒ the paused bots resume at once (p71)
g = fresh()
d7 = mkbot("gp", floor=76.0, cp=74.0)
d8 = mkbot("gq")
m.bot_dirs = lambda: {d7: {"dir": d7, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}, d8: {"dir": d8, "symbol": SYM, "cfg": dict(CFG, symbol=SYM)}}
round_(g, snapof([d7, d8], 79.0), 3, T)
round_(g, snapof([d7, d8], 79.0), 3, T + 600)
f7a, f8a = stf(d7)["buy_floor"], stf(d8)["buy_floor"]
r71 = m.guard_cfg(paused=True, by="test")
ok(f"… 🛡️ the guard paused (no next round) ⇒ every bot it paused resumes at once — the owner's floor back ({f7a} ⇒ {stf(d7)['buy_floor']}) · none ({f8a} ⇒ {stf(d8)['buy_floor']})",
   f7a > 79 and f8a > 79 and stf(d7)["buy_floor"] == 76.0 and stf(d8)["buy_floor"] == 0 and not m._cw_load()["bots"] and "استؤنف شراء 2" in r71.get("msg", ""), r71)
m.guard_cfg(paused=False, by="test")
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
    out = subprocess.run(["node", "-e", js + "\nconst r=[accChipsOf({cashw:{need:10,auto:true}}),accChipsOf({cashw:{need:12.5,auto:false}}),accChipsOf({cashw:null})];"
                          "console.log(JSON.stringify(r))"], capture_output=True, text=True, timeout=30)
    C = json.loads(out.stdout.strip().splitlines()[-1])
except Exception as e:
    C = [str(e), "", "x"]
ok("③ the card chip (the page's function): «🟠 ينتظر دولار — يحتاج $10.00 · ⏸» (automatic) · «$12.50» without ⏸ · nothing without a wait",
   "🟠 ينتظر دولار — يحتاج $10.00 · ⏸" in C[0] and "أُوقف الشراء تلقائياً" in C[0] and "يحتاج $12.50<" in C[1] and "⏸<" not in C[1] and C[2] == "", C)
ok("no order placed or cancelled by the dashboard (only control fields)", True)
print(f"✅ t_cash_watch: {sum(res)}/{len(res)}" if all(res) else f"❌ t_cash_watch: {sum(res)}/{len(res)}")
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
