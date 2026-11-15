# ⚡ v3.36.56 — DCA+ (the sell DCA + the layered exit ج1): the engine shipped inside the dashboard (`_DCAP_B64`), driven step by step
#   against a small fake exchange in a closed folder (no network · fake keys). The owner (15-11): «اتضيف واحد اخر وانسميه dca+ بس
#   لازم انجربه». What must hold before it ever touches real money:
#   ① the normal sell DCA is untouched (dca.py byte for byte) and a DCA+ bot gets dca_plus.py — the deploy writes its settings
#   ② a layer exits ALONE when the price comes back lx_pct under its sell price · the highest first · a profit > 0 after the fees ·
#      the books: total_coin_profit += its profit · one entry in cycles_log (the dashboard counts it like a closed cycle) · the
#      average and the target follow · it goes back to the store (re-open) with its planned price and size
#   ③ the controls: a layer you switched off stays · lx_from · re-open off · «exit now» (your decision: even at a loss · no re-open)
#   ④ safety: a partial fill exits that part (the rest exits later — the same total) · the engine stops right after sending ⇒ on the
#      next start the order is settled ONCE (never bought twice) · a lost reply ⇒ found by its id, ONE order · a layer smaller than
#      the exchange's minimum is never sent · a size never spends more than that layer's own dollars
#   ⑤ the whole engine on the dashboard's paper exchange (rise through every order and back · a long oscillation): to the end, no
#      refused order, the wallet = the books to the last decimal, every layer exit a profit
#   python3 devtests/t_dca_plus.py [Holy_Dashboard.pyw] [-q]
import base64, importlib.machinery, importlib.util, json, math, os, re, shutil, sys, tempfile, types, urllib.request, zlib

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1400]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net

DSRC = open(DASH, encoding="utf-8").read()


def lit(var):
    i = DSRC.index(var + " = (")
    j = DSRC.index("\n)\n", i)
    return zlib.decompress(base64.b64decode("".join(re.findall(r'"([A-Za-z0-9+/=]+)"', DSRC[i:j])))).decode("utf-8")


ENG = lit("_DCAP_B64")
SYM = "SOL-USDT"


# ── a small fake exchange: IOC buys fill at the ask (as much as `liq` allows) · ids · lookup by clOrdId · a lost reply on demand
class FX:
    def __init__(self):
        self.bid, self.ask, self.liq, self.n, self.orders, self.by_cl, self.lose, self.sent = 81.0, 81.0, 1.0, 0, {}, {}, False, []

    def place_order(self, instId=None, tdMode=None, clOrdId="", stpMode=None, side=None, ordType=None, sz=None, px=None, **k):
        self.n += 1
        oid = f"O{self.n}"
        sz, px = float(sz), float(px or 0)
        self.sent.append({"oid": oid, "cl": clOrdId, "side": side, "type": ordType, "sz": sz, "px": px})
        fill = 0.0
        if ordType == "ioc" and side == "buy" and px >= self.ask:
            fill = round(sz * self.liq, 4)
        o = {"ordId": oid, "clOrdId": clOrdId, "state": "filled" if fill >= sz - 1e-12 else "canceled", "avgPx": str(self.ask) if fill else "0",
             "accFillSz": str(fill), "fee": str(-fill * 0.001), "feeCcy": "SOL"}
        self.orders[oid] = o
        self.by_cl[clOrdId] = oid
        if self.lose:
            self.lose = False
            raise ConnectionError("reply lost")
        return {"code": "0", "data": [{"ordId": oid, "sCode": "0"}]}

    def get_order(self, instId=None, ordId=None, clOrdId=None, **k):
        oid = ordId or self.by_cl.get(clOrdId)
        if oid in self.orders:
            return {"code": "0", "data": [self.orders[oid]]}
        return {"code": "51603", "msg": "Order does not exist", "data": []}

    def cancel_order(self, **k):
        return {"code": "0", "data": [{}]}

    def get_ticker(self, instId):
        return {"code": "0", "data": [{"last": str((self.bid + self.ask) / 2), "bidPx": str(self.bid), "askPx": str(self.ask)}]}


R = tempfile.mkdtemp(prefix="t_dcap_")
os.chdir(R)
CFG = {"symbol": SYM, "bot_type": "dca", "dca_plus": True, "api_key": "x", "secret_key": "x", "passphrase": "x", "base_order_qty": 0.1,
       "avg_order_qty": 0.1, "first_deviation": 0.6, "step_multiplier": 1.2, "size_multiplier": 1.5, "max_safety_orders": 6,
       "take_profit_pct": 1.0, "exchange_orders": 3, "cycle_wait_sec": 30, "lx_on": True, "lx_pct": 0.5, "lx_from": 1, "lx_reopen": True,
       "bot_id": "HDTEST00001"}
json.dump(CFG, open(f"config_{SYM}.json", "w"))
for nm in ("okx", "okx.Trade", "okx.MarketData"):
    sys.modules[nm] = types.ModuleType(nm)
sys.modules["okx.Trade"].TradeAPI = object
sys.modules["okx.MarketData"].MarketAPI = object
sys.modules["okx"].Trade, sys.modules["okx"].MarketData = sys.modules["okx.Trade"], sys.modules["okx.MarketData"]


def engine():
    g = {"__name__": "dcap_test", "__file__": os.path.join(R, "dca.py")}
    exec(compile(ENG, os.path.join(R, "dca.py"), "exec"), g)
    g["INSTRUMENT_SPEC"].update({"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01, "loaded": True})
    g["time"].sleep = lambda s: None
    return g


E = engine()
fx = FX()


def fresh_state(lv=(1, 2, 3)):
    st = {"phase": "selling", "total_coin_profit": 0, "cycles_done": 0, "active_sells": {}, "filled": [], "pending_levels": []}
    st["planned_levels"] = E["compute_sell_levels"](CFG, 80.0)
    for l in st["planned_levels"]:
        if l["n"] == 0 or l["n"] in lv:
            px, q = round(l["price"], 2), l["qty"]
            E["_rec_fill"](SYM, st, {"avgPx": px, "fillSz": q, "fee": -px * q * 0.0008, "feeCcy": "USDT"}, px, q, l["n"])
        else:
            st["pending_levels"].append(dict(l))
    E["_recalc"](st, CFG)
    E["save_json"](E["STATE_FILE"], st)
    return st


def lxs(st):
    return [c for c in st.get("cycles_log") or [] if c.get("lx")]


def ns_of(st):
    return sorted(n for f in st["filled"] for n in E["_lx_ns"](f))


# ① the normal sell DCA is untouched · a DCA+ bot gets its own engine · the deploy writes the settings
ld = importlib.machinery.SourceFileLoader("hd_dcap", DASH)
os.makedirs(os.path.join(R, "root"), exist_ok=True)
_cwd = os.getcwd(); os.chdir(os.path.join(R, "root"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcap", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(_cwd)
work = open(os.path.join(H, "step", "eng", "dca.py"), encoding="utf-8").read()
ok("① the normal sell DCA's engine is the same file byte for byte (dca.py) · a DCA+ config gets dca_plus.py (its own fingerprint)",
   m.DCA_SRC == work and m.engine_for({"bot_type": "dca"})[0] == m.DCA_SRC and m.engine_for({"bot_type": "dca", "dca_plus": True})[0] == m.DCAP_SRC
   and m.DCAP_VERSION != m.DCA_VERSION and m.engine_for({"bot_type": "dca_buy", "dca_plus": True})[0] == m.DCAB_SRC)
m.ROOT = os.path.join(R, "root"); m.launch = lambda b: (True, "test"); m.wallet_keys = lambda w: {"api_key": "k", "secret_key": "s", "passphrase": "p"}
m.tg_send = lambda *a, **k: True; m.journal = lambda *a, **k: None
body = {"symbol": SYM, "wallet": "w", "base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2",
        "size_multiplier": "1.5", "max_safety_orders": "6", "take_profit_pct": "1", "dca_type": "dca_plus", "lx_pct": "0.7", "lx_from": "2", "lx_reopen": "0"}
r = m.deploy_dca(dict(body))
cf = [json.load(open(os.path.join(m.ROOT, d, f"config_{SYM}.json"))) for d in os.listdir(m.ROOT) if os.path.isdir(os.path.join(m.ROOT, d))]
eng_f = [open(os.path.join(m.ROOT, d, "dca.py"), encoding="utf-8").read() for d in os.listdir(m.ROOT) if os.path.isdir(os.path.join(m.ROOT, d))]
ok("① deploy «DCA+»: a sell DCA (bot_type dca) with dca_plus · lx_pct 0.7 · lx_from 2 · re-open off · its folder holds dca_plus.py",
   r.get("ok") and len(cf) == 1 and cf[0]["bot_type"] == "dca" and cf[0].get("dca_plus") is True and cf[0]["lx_pct"] == 0.7
   and cf[0]["lx_from"] == 2 and cf[0]["lx_reopen"] is False and eng_f[0] == m.DCAP_SRC and "DCA+" in r.get("msg", ""), (r, cf))
bad = [m.deploy_dca(dict(body, lx_pct=v)).get("msg") for v in ("0.1", "11", "abc")] + [m.deploy_dca(dict(body, lx_from=v)).get("msg") for v in ("0", "7")]
ok("① refused: a bounce under 0.3% (it would not cover the fees) or over 10% · a start layer outside 1…6 · nothing written",
   all(b and "✅" not in b for b in bad) and len(os.listdir(m.ROOT)) == 1, bad)
r2 = m.deploy_dca(dict(body, dca_type="dca"))
c2 = [json.load(open(os.path.join(m.ROOT, d, f"config_{SYM}.json"))) for d in sorted(os.listdir(m.ROOT))]
ok("① a normal sell DCA deployed next to it has none of the DCA+ fields (and gets dca.py)",
   r2.get("ok") and sum(1 for c in c2 if not c.get("dca_plus") and not any(k.startswith("lx_") for k in c)) == 1)

# ② the layer exit
st = fresh_state()
fx.ask = fx.bid = 81.5
E["lx_run"](fx, fx, SYM, CFG, st, 81.5)
ok("② the price above every layer's exit line ⇒ nothing is sent", fx.sent == [] and not lxs(st), fx.sent)
L3 = next(f for f in st["filled"] if f["n"] == 3)
p3 = L3["price"]
fx.ask = fx.bid = round(p3 * 0.995 - 0.01, 2)
avg0, tgt0 = st["avg_price"], st["target_price"]
E["lx_run"](fx, fx, SYM, CFG, st, fx.ask)
x = lxs(st)
ok(f"② the price {fx.ask} (0.5% under the sell price {p3} of safety order 3) ⇒ safety order 3 exits ALONE (1 and 2 are not yet there)",
   len(fx.sent) == 1 and fx.sent[0]["side"] == "buy" and fx.sent[0]["type"] == "ioc" and ns_of(st) == [0, 1, 2] and len(x) == 1 and x[0]["lx"] == [3],
   (fx.sent, ns_of(st), x))
ok("… its profit is a gain after both fees (coins back > coins sold) · total_coin_profit = that profit · cycles_log has its id and price",
   x and x[0]["profit"] > 0 and abs(st["total_coin_profit"] - x[0]["profit"]) < 1e-12 and x[0]["id"].startswith("HDTEST00001-x") and x[0]["px"] == fx.ask
   and x[0]["in"] > x[0]["out"], x)
ok("… the size never spends more than that layer's own dollars", fx.sent[0]["sz"] * fx.sent[0]["px"] <= L3["net"] + 1e-9, (fx.sent[0], L3["net"]))
ok("… the average and the cycle's target follow (they fall — the layer that pulled them up is out)",
   st["avg_price"] < avg0 and st["target_price"] < tgt0, (avg0, st["avg_price"], tgt0, st["target_price"]))
pl3 = next(l for l in st["planned_levels"] if l["n"] == 3)
ok("… it is back in the store with its planned price and size (re-open) — once", [(l["n"], l["price"], l["qty"]) for l in st["pending_levels"] if l["n"] == 3]
   == [(3, pl3["price"], pl3["qty"])], st["pending_levels"])
disk = json.load(open(E["STATE_FILE"]))
ok("… all of it is in the state file (saved)", len([c for c in disk.get("cycles_log") or [] if c.get("lx")]) == 1 and not disk.get("pending_lx"))

# ③ the controls
st = fresh_state(); fx.sent.clear()
st["lx_off"] = [2]
fx.ask = fx.bid = 79.9
E["lx_run"](fx, fx, SYM, CFG, st, 79.9)
ok("③ «switched off» safety order 2 stays (1 and 3 exit — the highest first)", ns_of(st) == [0, 2] and [c["lx"] for c in lxs(st)] == [[3], [1]], (ns_of(st), lxs(st)))
st = fresh_state(); fx.sent.clear()
E["lx_run"](fx, fx, SYM, dict(CFG, lx_from=3), st, 79.9)
ok("③ lx_from 3: only safety order 3 exits · 1 and 2 keep the cycle's target", ns_of(st) == [0, 1, 2] and [c["lx"] for c in lxs(st)] == [[3]], ns_of(st))
st = fresh_state(); fx.sent.clear()
st["lx_reopen"] = False
E["lx_run"](fx, fx, SYM, CFG, st, 79.9)
ok("③ re-open off (from the card): the layers exit and do not come back to the store", ns_of(st) == [0] and not any(l["n"] in (1, 2, 3) for l in st["pending_levels"]),
   st["pending_levels"])
st = fresh_state(); fx.sent.clear()
st["lx_on"] = False
E["lx_run"](fx, fx, SYM, CFG, st, 79.9)
ok("③ the layered exit switched off: nothing exits (it is a normal sell DCA)", fx.sent == [] and ns_of(st) == [0, 1, 2, 3])
L2 = next(f for f in st["filled"] if f["n"] == 2)
st["lx_now"] = [L2["fid"]]
fx.ask = fx.bid = round(L2["price"] * 1.01, 2)
E["lx_run"](fx, fx, SYM, CFG, st, fx.ask)
xm = lxs(st)
ok("③ «exit this layer now» (even with the switch off and the price 1% ABOVE its sell price): it exits · your decision ⇒ a loss is written "
   "as a loss · manual · not re-opened · the request is cleared",
   ns_of(st) == [0, 1, 3] and len(xm) == 1 and xm[0]["manual"] and xm[0]["profit"] < 0 and not st.get("lx_now")
   and not any(l["n"] == 2 for l in st["pending_levels"]), (ns_of(st), xm, st.get("lx_now")))

# ④ safety
st = fresh_state(); fx.sent.clear()
L3 = next(f for f in st["filled"] if f["n"] == 3); q3, u3 = L3["qty"], L3["net"]
fx.liq = 0.4
fx.ask = fx.bid = round(L3["price"] * 0.994, 2)
E["lx_run"](fx, fx, SYM, CFG, st, fx.ask)
L3b = next((f for f in st["filled"] if f["n"] == 3), None)
ok("④ a partial fill (40%): that part exits with its own profit · the layer stays with the rest (same price)",
   L3b is not None and abs(L3b["qty"] - q3 * 0.6) < 0.002 and len(lxs(st)) == 1 and lxs(st)[0]["profit"] > 0, (L3b, lxs(st)))
fx.liq = 1.0
E["lx_run"](fx, fx, SYM, CFG, st, fx.ask)
tot = sum(c["profit"] for c in lxs(st))
st_w = fresh_state(); fx.sent.clear()
E["lx_run"](fx, fx, SYM, CFG, st_w, fx.ask)
ok("… the next pass exits the rest · the two parts make the same profit as one whole exit",
   ns_of(st) == [0, 1, 2] and len(lxs(st)) == 2 and abs(tot - lxs(st_w)[0]["profit"]) < 2e-6, (tot, lxs(st_w)))
# the engine stops right after sending (before the confirmation)
st = fresh_state(); fx.sent.clear()
_co = E["confirm_order"]
E["confirm_order"] = lambda *a, **k: None
fx.ask = fx.bid = 81.2
r_ = E["lx_run"](fx, fx, SYM, CFG, st, 81.2)
disk = json.load(open(E["STATE_FILE"]))
ok("④ the engine stops right after sending: the order's id was saved first (pending_lx in the file) · nothing counted yet",
   r_ is False and disk.get("pending_lx", {}).get("oid") == fx.sent[-1]["oid"] and not lxs(disk), disk.get("pending_lx"))
E2 = engine()                                         # the next start: a new engine, the state from the file
st2 = E2["load_json"](E2["STATE_FILE"])
E2["lx_settle"](fx, SYM, CFG, st2)
E2["lx_run"](fx, fx, SYM, CFG, st2, 81.2)
E2["lx_settle"](fx, SYM, CFG, st2)
ok("… the next start settles it ONCE: one exit in the books · one order at the exchange (never bought twice)",
   len(lxs(st2)) == 1 and len([o for o in fx.sent if o["cl"].endswith(str(o["cl"])[-7:]) and o["side"] == "buy"]) == 1 and not st2.get("pending_lx"),
   (lxs(st2), fx.sent))
E["confirm_order"] = _co
# a lost reply
E = engine()
st = fresh_state(); fx.sent.clear()
fx.lose = True
E["lx_run"](fx, fx, SYM, CFG, st, 81.2)
n_after_lost = len(fx.sent)
pend_key = [k for k in E["_xs"]() if k.startswith("X")]
for _ in range(3):
    E["_xs_settle"](fx, SYM, st)
    E["lx_settle"](fx, SYM, CFG, st)
    E["lx_run"](fx, fx, SYM, CFG, st, 81.2)
ok("④ the exchange's reply is lost: its id waits in the send journal · found by its id · ONE order · ONE exit in the books",
   n_after_lost == 1 and pend_key and len(fx.sent) == 1 and len(lxs(st)) == 1 and not [k for k in E["_xs"]() if k.startswith("X")],
   (n_after_lost, pend_key, fx.sent, lxs(st)))
# smaller than the exchange's minimum
st = fresh_state(); fx.sent.clear()
st["filled"].append({"price": 82.0, "qty": 0.005, "n": 4, "net": 0.41, "fid": 99})
E["lx_run"](fx, fx, SYM, CFG, st, 81.0)
ok("④ a layer smaller than the exchange's minimum (0.005 < 0.01) is never sent — it stays for the cycle's target",
   all(abs(o["sz"] - 0.005) > 1e-9 for o in fx.sent) and any(f.get("fid") == 99 and f.get("lx_small") for f in st["filled"]))
# a grouped fill (one IOC for levels 4–5) exits as one and both levels come back
st = fresh_state(); fx.sent.clear()
pl = {l["n"]: l for l in st["planned_levels"]}
st["pending_levels"] = [l for l in st["pending_levels"] if l["n"] not in (4, 5)]
q45 = pl[4]["qty"] + pl[5]["qty"]
E["_rec_fill"](SYM, st, {"avgPx": 83.6, "fillSz": q45, "fee": -83.6 * q45 * 0.001, "feeCcy": "USDT"}, 83.6, q45, -1, {"ns": [4, 5]})
E["_recalc"](st, CFG)
fx.ask = fx.bid = 83.1
E["lx_run"](fx, fx, SYM, CFG, st, 83.1)
ok("④ a grouped fill (safety orders 4–5 in one order) exits as one · both levels come back to the store",
   [c["lx"] for c in lxs(st)] == [[4, 5]] and sorted(l["n"] for l in st["pending_levels"] if l["n"] in (4, 5)) == [4, 5], (lxs(st), st["pending_levels"]))

# ⑤ the whole engine on the dashboard's paper exchange
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
B = {"base_order_qty": "0.1", "avg_order_qty": "0.1", "first_deviation": "0.6", "step_multiplier": "1.2", "size_multiplier": "1.5",
     "max_safety_orders": "6", "take_profit_pct": "1", "dca_type": "dca", "exchange_orders": "3", "cycle_wait_sec": "60", "symbol": SYM,
     "dca_plus": "1", "lx_pct": "0.5", "lx_from": "1", "lx_reopen": "1"}
P0 = 80.0
paths = {"rise through every order, then back": [P0] * 30 + [P0 * (1 + 0.12 * i / 300) for i in range(300)] + [P0 * 1.12] * 60
         + [P0 * (1.12 - 0.13 * i / 900) for i in range(901)] + [P0 * 0.99] * 200,
         "a long oscillation ±3%": [P0] * 30 + [P0 * (1 + 0.03 * math.sin(2 * math.pi * i / 150)) for i in range(1500)] + [P0 * 0.985] * 200}
keep = {k: m.__dict__.get(k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
for nm, px in paths.items():
    cfg, err = m._bt_dry_cfg("dca", dict(B), SYM, SPEC, P0)
    m.__dict__.update(keep)
    q0, b0 = m._bt_wallet_def("dca", cfg or {}, B, P0, SPEC)
    rr = m._bt_run("dca", cfg, SYM, px, 60.0, q0, b0, SPEC, samples=2000)
    ex, stt = rr["ex"], rr.get("state") or {}
    opn = sum(float(f["qty"]) for f in stt.get("filled") or [])
    chk = (ex.bal[ex.base] - b0) + opn - float(stt.get("total_coin_profit") or 0)
    xl = [c for c in stt.get("cycles_log") or [] if c.get("lx")]
    ok(f"⑤ the real DCA+ engine on the paper exchange — {nm}: to the end · no refused order · {len(xl)} layer exits, every one a profit · "
       f"the wallet = the books ({chk:+.1e} coin)",
       cfg and cfg.get("dca_plus") and rr["why"] == "end" and not ex.rejects and xl and min(c["profit"] for c in xl) > 0 and abs(chk) < 1e-6
       and not stt.get("pending_lx"), (err, rr["why"], ex.rejects[:3], len(xl), chk))

print(f"✅ t_dca_plus: {sum(res)}/{len(res)}" if all(res) else f"❌ t_dca_plus: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
