# ⚡ v3.36.59 — DCA+ الشرائي (the owner 16-11: «Dca + خليه زر بالخارج وضيف معه الشرائية وسويلهم تيست»): the free ladder going DOWN —
#   every order its own distance under the one before, its size and its exit % ABOVE the average — the engine shipped inside the
#   dashboard (`_DCAPB_B64`, patch 101 = the buy DCA + patch 94's ladder), driven step by step against a small fake exchange in a closed
#   folder (no network · fake keys), then the whole engine on the dashboard's paper exchange. The mirror of t_dca_plus:
#   ① the normal buy DCA is untouched (dca_buy byte for byte) · a buy DCA with dca_plus gets dca_plus_buy · the sell DCA+ keeps its own ·
#     the deploy «dca_plus_buy» writes a buy DCA with the rows and the classic fields that follow · bad rows refused before any folder
#   ② the ladder = the rows (each price = the one before × (1 − its distance)) · the target = the weighted average × (1 + the exit % of
#     the DEEPEST order filled) · never under 0.20% · the preview = the same numbers (a DOLLAR profit · the dollars it needs)
#   ③ an edit while it runs: exactly the DCA+ rules (cancel and place again · filled orders locked · a part filled is booked · wait for a
#     grouped order / an unconfirmed cancel · between cycles ⇒ the next cycle · refusals with the reason)
#   ④ the dashboard's «plus_edit» on a buy DCA+ (state fields only · no order) · the card snapshot · the card's table (exit ABOVE)
#   ⑤ the whole engine on the paper exchange (a fall through every order and back up · a long oscillation · an edit mid-cycle): no
#     refused order · every cycle closed sold EVERYTHING it bought at a dollar gain · every safety buy at the ladder (never dearer) · the
#     wallet = the books to the cent
#   ⑥ the trial path from the form (the kind · the settings · the dollars it needs) · the demo's kind
#   python3 devtests/t_dca_plus_buy.py [Holy_Dashboard.pyw] [-q]
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


ENG = lit("_DCAPB_B64")
SYM = "XRP-USDT"
ROWS = [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 5, "x": 0.6}, {"d": 1.5, "q": 10, "x": 0.8}, {"d": 2, "q": 20, "x": 1.0},
        {"d": 3, "q": 40, "x": 0.4}, {"d": 4, "q": 60, "x": 0.3}]


# ── a small fake exchange: limit sells wait (live) · cancel (optionally after a part filled) · lookups · a cancel that is not confirmed
class FX:
    def __init__(self):
        self.p, self.n, self.orders, self.by_cl, self.sent, self.cancels, self.part_on_cancel, self.blind = 1.0, 0, {}, {}, [], [], {}, False

    def place_order(self, instId=None, tdMode=None, clOrdId="", stpMode=None, side=None, ordType=None, sz=None, px=None, tgtCcy=None, **k):
        self.n += 1
        oid = f"O{self.n}"
        sz, px = float(sz), float(px or 0)
        self.sent.append({"oid": oid, "cl": clOrdId, "side": side, "type": ordType, "sz": sz, "px": px})
        o = {"ordId": oid, "clOrdId": clOrdId, "side": side, "state": "live", "avgPx": "0", "accFillSz": "0", "fee": "0", "feeCcy": "USDT",
             "px": str(px), "sz": str(sz)}
        self.orders[oid] = o
        self.by_cl[clOrdId] = oid
        return {"code": "0", "data": [{"ordId": oid, "sCode": "0"}]}

    def get_order(self, instId=None, ordId=None, clOrdId=None, **k):
        if self.blind:
            raise ConnectionError("no reply")
        oid = ordId or self.by_cl.get(clOrdId)
        if oid in self.orders:
            return {"code": "0", "data": [dict(self.orders[oid])]}
        return {"code": "51603", "msg": "Order does not exist", "data": []}

    def get_order_list(self, instId=None, **k):
        return {"code": "0", "data": [dict(o) for o in self.orders.values() if o["state"] in ("live", "partially_filled")]}

    def cancel_order(self, instId=None, ordId=None, **k):
        self.cancels.append(ordId)
        o = self.orders.get(ordId)
        if o and o["state"] in ("live", "partially_filled") and not self.blind:
            part = self.part_on_cancel.pop(ordId, 0.0)
            if part > 0:
                q = float(o["sz"]) * part
                o.update(accFillSz=str(q), avgPx=o["px"], fee=str(-q * float(o["px"]) * 0.0008))
            o["state"] = "canceled"
        return {"code": "0", "data": [{}]}

    def get_ticker(self, instId):
        return {"code": "0", "data": [{"last": str(self.p), "bidPx": str(self.p), "askPx": str(self.p)}]}


R = tempfile.mkdtemp(prefix="t_dcapb_")
os.chdir(R)
CFG = {"symbol": SYM, "bot_type": "dca_buy", "dca_plus": True, "api_key": "x", "secret_key": "x", "passphrase": "x", "plus_rows": ROWS,
       "base_order_qty": 5, "avg_order_qty": 5, "first_deviation": 1, "step_multiplier": 1, "size_multiplier": 1, "max_safety_orders": 5,
       "take_profit_pct": 0.5, "exchange_orders": 2, "cycle_wait_sec": 30, "bot_id": "HDTEST00001"}
json.dump(CFG, open(f"config_{SYM}.json", "w"))
for nm in ("okx", "okx.Trade", "okx.MarketData"):
    sys.modules[nm] = types.ModuleType(nm)
sys.modules["okx.Trade"].TradeAPI = object
sys.modules["okx.MarketData"].MarketAPI = object
sys.modules["okx"].Trade, sys.modules["okx"].MarketData = sys.modules["okx.Trade"], sys.modules["okx.MarketData"]


def engine():
    g = {"__name__": "dcap_test", "__file__": os.path.join(R, "dca.py")}
    exec(compile(ENG, os.path.join(R, "dca.py"), "exec"), g)
    g["INSTRUMENT_SPEC"].update({"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 1, "loaded": True})
    g["time"].sleep = lambda s: None
    return g


E = engine()


def cfg_():
    c = json.loads(json.dumps(CFG))
    E["plus_apply_rows"](c, json.loads(json.dumps(ROWS)))
    return c


def state_(cfg, fx, filled=(0, 1), live=(2, 3)):
    """a cycle in progress: `filled` bought · `live` resting at the fake exchange · the rest in the store"""
    st = {"phase": "selling", "total_coin_profit": 0, "cycles_done": 0, "active_sells": {}, "filled": [], "pending_levels": [], "base_price": 1.0}
    st["planned_levels"] = E["compute_sell_levels"](cfg, 1.0)
    for l in st["planned_levels"]:
        px, q = round(l["price"], 4), l["qty"]
        if l["n"] in filled:
            E["_rec_fill"](SYM, st, {"avgPx": px, "fillSz": q, "fee": -q * 0.0008, "feeCcy": "XRP"}, px, q, l["n"])   # a buy pays its fee in the coin
        elif l["n"] in live:
            o = E["place_sell"](fx, SYM, l["price"], q, str(l["n"]))
            st["active_sells"][o["ordId"]] = {"price": o["price"], "qty": o["qty"], "n": l["n"]}
        else:
            st["pending_levels"].append(dict(l))
    E["_recalc"](st, cfg)
    E["save_json"](E["STATE_FILE"], st)
    return st


def lv_px(st):
    return {int(l["n"]): round(l["price"], 6) for l in st["planned_levels"]}


# ① engines and the deploy
ld = importlib.machinery.SourceFileLoader("hd_dcapb", DASH)
os.makedirs(os.path.join(R, "root"), exist_ok=True)
_cwd = os.getcwd(); os.chdir(os.path.join(R, "root"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcapb", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(_cwd)
work = open(os.path.join(H, "step", "eng", "dca_buy.py"), encoding="utf-8").read()
ok("① the normal buy DCA's engine is the same file byte for byte (dca_buy) · a buy DCA with dca_plus gets DCA+ الشرائي (its own "
   "fingerprint) · the sell DCA+ and the sell DCA keep theirs", m.DCAB_SRC == work and m.engine_for({"bot_type": "dca_buy"})[0] == m.DCAB_SRC
   and m.engine_for({"bot_type": "dca_buy", "dca_plus": True})[0] == m.DCAPB_SRC and m.DCAPB_VERSION not in (m.DCAB_VERSION, m.DCAP_VERSION)
   and m.engine_for({"bot_type": "dca", "dca_plus": True})[0] == m.DCAP_SRC and m.engine_for({"bot_type": "dca"})[0] == m.DCA_SRC
   and "plus_edit_apply" in m.DCAPB_SRC and 'p * (1 - float(r["d"]) / 100.0)' in m.DCAPB_SRC and "target = avg * (1 + tp_pct)" in m.DCAPB_SRC)
m.ROOT = os.path.join(R, "root"); m.launch = lambda b: (True, "test"); m.wallet_keys = lambda w: {"api_key": "k", "secret_key": "s", "passphrase": "p"}
m.tg_send = lambda *a, **k: True; m.journal = lambda *a, **k: None
body = {"symbol": SYM, "wallet": "w", "dca_type": "dca_plus_buy", "plus_rows": json.dumps(ROWS), "exchange_orders": "2", "cycle_wait_sec": "30",
        "base_order_qty": "999", "max_safety_orders": "1"}
r = m.deploy_dca(dict(body))
dirs = [d for d in os.listdir(m.ROOT) if os.path.isdir(os.path.join(m.ROOT, d))]
cf = [json.load(open(os.path.join(m.ROOT, d, f"config_{SYM}.json"))) for d in dirs]
eng_f = [open(os.path.join(m.ROOT, d, "dca.py"), encoding="utf-8").read() for d in dirs]
c0 = cf[0] if cf else {}
ok("① deploy «DCA+ شرائي»: a buy DCA (bot_type dca_buy) with dca_plus and the six rows · the classic fields follow the rows (base 5 · 5 safety · "
   "first distance 1% · exit 0.5%) — not the form's leftovers · its folder holds DCA+ الشرائي",
   r.get("ok") and len(cf) == 1 and c0["bot_type"] == "dca_buy" and c0.get("dca_plus") is True and c0.get("plus_rows") == [dict(x, d=float(x["d"])) for x in ROWS]
   and float(c0["base_order_qty"]) == 5 and int(c0["max_safety_orders"]) == 5 and float(c0["first_deviation"]) == 1
   and float(c0["take_profit_pct"]) == 0.5 and eng_f[0] == m.DCAPB_SRC and "DCA+ شرائي" in r.get("msg", ""), (r, c0))
BAD = {"a size of 0": [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 0, "x": 0.5}],
       "a distance of 0 on a safety order": [{"d": 0, "q": 5, "x": 0.5}, {"d": 0, "q": 5, "x": 0.5}],
       "an exit of 0": [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 5, "x": 0}], "an exit of 60%": [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 5, "x": 60}],
       "a distance of 70%": [{"d": 0, "q": 5, "x": 0.5}, {"d": 70, "q": 5, "x": 0.5}], "the base alone": [{"d": 0, "q": 5, "x": 0.5}],
       "text instead of rows": "abc", "a word in a number": [{"d": 0, "q": 5, "x": 0.5}, {"d": "x", "q": 5, "x": 0.5}],
       "NaN": [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": float("nan"), "x": 0.5}], "102 rows": [{"d": 0, "q": 5, "x": 0.5}] + [{"d": 1, "q": 5, "x": 0.5}] * 101}
bad = {k: m.deploy_dca(dict(body, plus_rows=json.dumps(v) if not isinstance(v, str) else v)).get("msg") for k, v in BAD.items()}
ok("① refused before any folder is made: " + " · ".join(BAD), all(v and not str(v).startswith(("✅", "🚀")) for v in bad.values())
   and len([d for d in os.listdir(m.ROOT) if os.path.isdir(os.path.join(m.ROOT, d))]) == 1, bad)
r2 = m.deploy_dca(dict(body, dca_type="dca_buy", base_order_qty="5", avg_order_qty="5", first_deviation="1", step_multiplier="1",
                       size_multiplier="1", max_safety_orders="3", take_profit_pct="1"))
c2 = [json.load(open(os.path.join(m.ROOT, d, f"config_{SYM}.json"))) for d in sorted(os.listdir(m.ROOT)) if os.path.isdir(os.path.join(m.ROOT, d))]
ok("① a normal buy DCA deployed next to it has none of the DCA+ fields (and gets its own engine)",
   r2.get("ok") and sum(1 for c in c2 if not c.get("dca_plus") and "plus_rows" not in c) == 1, (r2, c2))

# ② the ladder and the target
c = cfg_()
lv = E["compute_sell_levels"](c, 1.0)
want, p = [], 1.0
for i, x in enumerate(ROWS):
    p = p * (1 - x["d"] / 100) if i else p
    want.append((i, round(p, 8), x["q"]))
ok("② the ladder = the owner's rows going DOWN: each price = the one before × (1 − its distance) · each size its own (1 · 0.99 · 0.97515 · 0.955647 · …)",
   [(l["n"], round(l["price"], 8), l["qty"]) for l in lv] == want, (lv, want))
fx = FX()
tg = {}
for deep in range(6):
    st = state_(c, fx, filled=tuple(range(deep + 1)), live=())
    tq = sum(f["qty"] for f in st["filled"]); tv = sum(f["price"] * f["qty"] for f in st["filled"])
    tg[deep] = (st["avg_price"], st["target_price"], tv / tq * (1 + max(ROWS[deep]["x"], 0.2) / 100))
ok("② the target = the weighted average × (1 + the exit % of the DEEPEST order filled): rows 0…5 ⇒ 0.5 · 0.6 · 0.8 · 1.0 · 0.4 · 0.3%",
   all(abs(t[1] - t[2]) < 1e-12 for t in tg.values()), tg)
cl = cfg_(); cl["plus_rows"][3]["x"] = 0.05
st = state_(cl, fx, filled=(0, 1, 2, 3), live=())
ok("② an exit under 0.20% (0.05%) ⇒ the engine uses 0.20% (the two fees are covered)", abs(st["target_price"] - st["avg_price"] * 1.002) < 1e-12,
   (st["avg_price"], st["target_price"]))
pv = m.compute_dca_table(dict(dca_type="dca_plus_buy", plus_rows=ROWS), 1.0)
pr = pv.get("rows") or []
ex_t, cq_, cv_ = {}, 0.0, 0.0
for i, (_n, px_, q_) in enumerate(want):
    cq_ += q_; cv_ += px_ * q_
    ex_t[i] = cv_ / cq_ * (1 + max(ROWS[i]["x"], 0.2) / 100)
ok("② the deploy preview (the form's table) = the same ladder · per row the average and the exit ABOVE it with ITS exit % · the "
   "DOLLAR profit after the fees is a gain on every row · it needs the dollars of every row at its price",
   [(x["n"], round(x["price"], 8), x["order_qty"]) for x in pr] == want and all(abs(pr[d]["target"] - ex_t[d]) < 1e-8 for d in range(6))
   and all(x["exit_profit"] > 0 for x in pr) and pv["summary"].get("plus") and not pv["summary"]["low_rows"] and pv["summary"].get("is_buy") is True
   and abs(pv["summary"]["capital_needed"] - round(cv_, 2)) < 0.011 and all(abs(x["exit_usd"] - x["exit_profit"]) < 1e-4 for x in pr)
   and all(x["gap_pct"] > 0 for x in pr), (pr[:2], pv.get("summary")))
pvb = m.compute_dca_table(dict(dca_type="dca_plus_buy", plus_rows=[{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 5, "x": 0.1}]), 1.0)
ok("② the preview warns when an exit does not cover the fees (0.1%)", pvb["summary"].get("fee_warn") is True, pvb.get("summary"))

# ③ the edit while it runs (the engine side)
NEW = [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": 5, "x": 0.7}, {"d": 2.5, "q": 15, "x": 0.6}, {"d": 2.5, "q": 25, "x": 0.5},
       {"d": 3, "q": 30, "x": 0.4}, {"d": 3, "q": 50, "x": 0.3}, {"d": 4, "q": 80, "x": 0.25}]
c = cfg_(); fx = FX()
st = state_(c, fx)
old_live = list(st["active_sells"])
px0 = lv_px(st)
st["plus_edit"] = {"seq": 11, "rows": json.loads(json.dumps(NEW))}
done = E["plus_edit_apply"](fx, SYM, c, st)
npx = lv_px(st)
want_new = {}
p = 1.0
for i, x in enumerate(NEW):
    p = p * (1 - x["d"] / 100) if i else p
    want_new[i] = round(p, 6)
ok("③ an edit while it runs (base + safety 1 filled · 2 and 3 live at the exchange): both live orders are cancelled · nothing at the "
   "exchange until the next pass · the orders not filled take their new prices (2.5% · 2.5% · 3% …) · the new 7th order is added",
   done is True and sorted(fx.cancels) == sorted(old_live) and st["active_sells"] == {} and npx[0] == px0[0] and npx[1] == px0[1]
   and all(npx[n] == want_new[n] for n in range(2, 7)) and sorted(l["n"] for l in st["pending_levels"]) == [2, 3, 4, 5, 6], (npx, want_new, st["pending_levels"]))
ok("… the target follows at once: the exit % of the deepest filled order (safety 1) is now 0.7%",
   abs(st["target_price"] - st["avg_price"] * (1 + 0.007)) < 1e-12 and st.get("plus_seq") == 11 and not st.get("plus_edit_err")
   and c["plus_rows"] == NEW and c["max_safety_orders"] == 6, (st["avg_price"], st["target_price"]))
fx.p = 1.0
E["topup_ladder"](fx, SYM, c, st, 1.0)
lv_sent = sorted(((round(float(v["price"]), 4), v["n"]) for v in st["active_sells"].values()), key=lambda z: z[1])
ok("… the next pass places the nearest two again at their NEW prices (2 and 3)", [n for _, n in lv_sent] == [2, 3]
   and all(abs(px - want_new[n]) <= 0.0001 + 1e-12 for px, n in lv_sent), (lv_sent, want_new))
disk = json.load(open(E["STATE_FILE"]))
ok("… all of it is in the state file (saved · the edit marked done)", disk.get("plus_seq") == 11 and len(disk.get("planned_levels") or []) == 7)
again = len(fx.sent)
E["plus_edit_apply"](fx, SYM, c, st)
ok("… the same edit is applied once (the next pass does nothing)", len(fx.sent) == again and len(fx.cancels) == 2)

# a part filled just before the cancel
c = cfg_(); fx = FX()
st = state_(c, fx)
o2 = next(k for k, v in st["active_sells"].items() if v["n"] == 2)
q2, p2 = st["active_sells"][o2]["qty"], st["active_sells"][o2]["price"]
fx.part_on_cancel[o2] = 0.4
st["plus_edit"] = {"seq": 12, "rows": json.loads(json.dumps(NEW))}
E["plus_edit_apply"](fx, SYM, c, st)
f2 = [f for f in st["filled"] if f["n"] == 2]
rest2 = [l for l in st["pending_levels"] if l["n"] == 2]
ok("③ safety 2 had filled 40% when it was cancelled: that part is booked · safety 2 is now «filled» (locked at ITS price) · its rest "
   "(60%) waits at the same price · the target uses safety 2's exit (0.6%)",
   len(f2) == 1 and abs(f2[0]["qty"] - q2 * 0.4) < 1e-6 and len(rest2) == 1 and abs(rest2[0]["qty"] - q2 * 0.6) < 1e-6
   and abs(rest2[0]["price"] - p2) < 1e-12 and lv_px(st)[2] == round(st["planned_levels"][2]["price"], 6)
   and abs(st["planned_levels"][2]["price"] - E["compute_sell_levels"](cfg_(), 1.0)[2]["price"]) < 1e-12
   and abs(st["target_price"] - st["avg_price"] * (1 + 0.006)) < 1e-12, (f2, rest2, st["planned_levels"][2]))

# a grouped order not settled yet · a cancel not confirmed
c = cfg_(); fx = FX()
st = state_(c, fx)
st["pending_grp"] = {"oid": "G1", "levels": [], "why": "t"}
st["plus_edit"] = {"seq": 13, "rows": json.loads(json.dumps(NEW))}
r_ = E["plus_edit_apply"](fx, SYM, c, st)
ok("③ a grouped order not settled yet ⇒ the edit waits (nothing cancelled · nothing moved)", r_ is False and fx.cancels == [] and st.get("plus_seq") is None
   and c["plus_rows"] == cfg_()["plus_rows"])
st.pop("pending_grp")
fx.blind = True
r_ = E["plus_edit_apply"](fx, SYM, c, st)
fx.blind = False
ok("③ the cancel cannot be confirmed (no reply) ⇒ the edit waits · the rows are not half-applied", r_ is False and st.get("plus_seq") is None
   and c["plus_rows"] == cfg_()["plus_rows"] and len(st["active_sells"]) == 2, (r_, st.get("active_sells")))
r_ = E["plus_edit_apply"](fx, SYM, c, st)
ok("… the next pass (replies back) applies it", r_ is True and st.get("plus_seq") == 13 and c["plus_rows"] == NEW and st["active_sells"] == {})

# between cycles · bad rows · removing a filled order · removing a live one
for ph in ("waiting", "init", "buying"):
    c = cfg_(); fx = FX()
    st = {"phase": ph, "plus_edit": {"seq": 20, "rows": json.loads(json.dumps(NEW))}}
    E["plus_edit_apply"](fx, SYM, c, st)
    ok(f"③ phase «{ph}»: the rows are kept for the next cycle · no order sent or cancelled", c["plus_rows"] == NEW and st.get("plus_seq") == 20
       and fx.sent == [] and fx.cancels == [] and c["max_safety_orders"] == 6)
c = cfg_(); fx = FX()
st = state_(c, fx)
n_sent = len(fx.sent)
st["plus_edit"] = {"seq": 21, "rows": [{"d": 0, "q": 5, "x": 0.5}, {"d": 1, "q": -3, "x": 0.5}]}
E["plus_edit_apply"](fx, SYM, c, st)
ok("③ bad rows (a negative size) ⇒ refused with the reason (plus_edit_err) · nothing cancelled · the rows unchanged",
   st.get("plus_seq") == 21 and st.get("plus_edit_err") and fx.cancels == [] and c["plus_rows"] == cfg_()["plus_rows"] and len(fx.sent) == n_sent)
st = state_(c, fx, filled=(0, 1, 2), live=(3,))
st["plus_edit"] = {"seq": 22, "rows": json.loads(json.dumps(NEW[:2]))}
E["plus_edit_apply"](fx, SYM, c, st)
ok("③ an edit that removes safety 2 (filled this cycle) ⇒ refused with the reason · nothing cancelled",
   st.get("plus_seq") == 22 and "نُفّذ" in str(st.get("plus_edit_err")) and fx.cancels == [] and len(st["active_sells"]) == 1)
c = cfg_(); fx = FX()
st = state_(c, fx, filled=(0, 1), live=(2, 3))
st["plus_edit"] = {"seq": 23, "rows": json.loads(json.dumps(NEW[:3]))}
E["plus_edit_apply"](fx, SYM, c, st)
ok("③ an edit that removes orders not filled (3, 4, 5): they are cancelled and gone · the ladder is the three rows",
   sorted(lv_px(st)) == [0, 1, 2] and [l["n"] for l in st["pending_levels"]] == [2] and st["active_sells"] == {} and len(fx.cancels) == 2)
c = cfg_(); fx = FX()
st = state_(c, fx, filled=(0, 1, 2), live=(3,))
e2 = json.loads(json.dumps(ROWS)); e2[2]["x"] = 0.35
st["plus_edit"] = {"seq": 24, "rows": e2}
E["plus_edit_apply"](fx, SYM, c, st)
ok("③ the exit % of a filled order changed (safety 2: 0.8 → 0.35%) ⇒ its price stays · the target moves closer at once",
   abs(st["target_price"] - st["avg_price"] * (1 + 0.0035)) < 1e-12 and lv_px(st) == lv_px(state_(cfg_(), FX(), filled=(0, 1, 2), live=(3,)))
   , (st["avg_price"], st["target_price"]))

# ④ the dashboard's control
dp = [d for d in sorted(os.listdir(m.ROOT)) if os.path.isdir(os.path.join(m.ROOT, d)) and json.load(open(os.path.join(m.ROOT, d, f"config_{SYM}.json"))).get("dca_plus")][0]
b = m.bot_dirs()[dp] if dp in m.bot_dirs() else [x for x in m.bot_dirs().values() if x["dir"].endswith(dp)][0]
d_rel = [k for k, v in m.bot_dirs().items() if v["dir"] == b["dir"]][0]
sp = m.paths_of(b)[0]
cfgd = json.loads(json.dumps(b["cfg"]))
st = state_(cfgd, FX())
m.save_json_atomic(sp, st)
m._JC.clear() if hasattr(m, "_JC") else None
posted = []
_op = getattr(m, "_okx_post", None)
m._okx_post = lambda *a, **k: posted.append(a) or {"code": "1"}
mv = json.loads(json.dumps(NEW)); mv[1]["d"], mv[1]["q"] = 9, 99
r = m.control(d_rel, "plus_edit", {"rows": mv})
s2 = json.load(open(sp, encoding="utf-8"))
c3 = json.load(open(b["cfg_path"], encoding="utf-8"))
pe = s2.get("plus_edit") or {}
ok("④ «plus_edit» from the card: accepted · safety 1 (filled) keeps its distance and size even if the edit moved it (9% · 99 → 1% · 5) · "
   "its exit % changes (0.7) · the config holds the new rows (the next start reads them) · the state holds the edit for the engine",
   r.get("ok") and pe.get("rows") and pe["rows"][1]["d"] == 1 and pe["rows"][1]["q"] == 5 and pe["rows"][1]["x"] == 0.7
   and c3.get("plus_rows") == pe["rows"] and int(c3["max_safety_orders"]) == 6 and pe["rows"][2] == dict(NEW[2], d=float(NEW[2]["d"])), (r, pe, c3.get("plus_rows")))
ok("… the dashboard sent nothing to the exchange (state fields only) · the fills and the books are untouched",
   posted == [] and s2.get("filled") == json.loads(json.dumps(st["filled"])) and s2.get("active_sells") == json.loads(json.dumps(st["active_sells"])))
snap = m._dca_snapshot(dict(b, cfg=c3), s2)
pl = snap.get("plus") or {}
ok("… the card shows it: the rows · the locked orders (0 and 1) · «waiting for the bot» until the engine applies it",
   pl.get("rows") == pe["rows"] and pl.get("locked") == [0, 1] and pl.get("pending") is True and not pl.get("err"), pl)
s2["plus_seq"] = pe["seq"]; s2["plus_edit_err"] = "x"
pl2 = (m._dca_snapshot(dict(b, cfg=c3), s2).get("plus") or {})
ok("… after the engine: not pending · a refusal from the engine is shown", pl2.get("pending") is False and pl2.get("err") == "x", pl2)
rows_live = m._dca_live(s2, dict(c3, plus_rows=NEW), True, 1.0, False)
ok("… the card's table: each row carries ITS exit % and its exit price (ABOVE the average) uses it", [x.get("x") for x in rows_live][:3] == [0.5, 0.7, 0.6]
   and abs(rows_live[2]["tgt"] - m._pv_sig(rows_live[2]["avg"] * (1 + 0.006))) < 1e-6, rows_live[:3])
st["filled"] += [{"price": 0.9752, "qty": 10, "n": 2, "net": 9.992}]
m.save_json_atomic(sp, st)
rb = [m.control(d_rel, "plus_edit", {"rows": NEW[:2]}), m.control(d_rel, "plus_edit", {"rows": [{"d": 0, "q": 5, "x": 0.5}]}),
      m.control(d_rel, "plus_edit", {"rows": "junk"}), m.control(d_rel, "plus_edit", None)]
ok("④ refused: removing safety 2 (filled this cycle) · the base alone · junk · nothing", all(not x.get("ok") for x in rb), rb)
dn = [k for k, v in m.bot_dirs().items() if not v["cfg"].get("dca_plus")][0]
ok("④ a normal buy DCA refuses «plus_edit»", not m.control(dn, "plus_edit", {"rows": NEW}).get("ok"))
if _op is not None:
    m._okx_post = _op

# ⑤ the whole engine on the dashboard's paper exchange
SPEC = {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 1}
B = {"dca_type": "dca_plus_buy", "plus_rows": json.dumps(ROWS), "exchange_orders": "2", "cycle_wait_sec": "60", "symbol": SYM}
P0 = 1.0
bot = 1.0
for x in ROWS[1:]:
    bot *= 1 - x["d"] / 100
paths = {"a fall through every order, then back up": [P0] * 30 + [P0 * (1 - (1 - bot * 0.99) * i / 300) for i in range(300)] + [P0 * bot * 0.99] * 60
         + [P0 * (bot * 0.99 + (1.02 - bot * 0.99) * i / 900) for i in range(901)] + [P0 * 1.02] * 200,
         "a long oscillation ±4%": [P0] * 30 + [P0 * (1 - 0.04 * math.sin(2 * math.pi * i / 150)) for i in range(1500)] + [P0 * 1.03] * 200}
keep = {k: m.__dict__.get(k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
_mk = m._bt_tmp.mkdtemp
box = {}


def _mk2(*a, **k):
    d = _mk(*a, **k)
    if str(k.get("prefix", "")).startswith("holy_bt_"):
        box["dir"] = d
    return d


m._bt_tmp.mkdtemp = _mk2


def run(nm, px, edit_at=None):
    cfg, err = m._bt_dry_cfg("dca_buy", dict(B), SYM, SPEC, P0)
    m.__dict__.update(keep)
    q0, b0 = m._bt_wallet_def("dca_buy", cfg or {}, dict(B, plus_rows=json.dumps(NEW)) if edit_at is not None else B, P0, SPEC)   # the edit adds orders ⇒ dollars for them
    sent = {}

    def prog(i, n):
        if edit_at is not None and i >= edit_at and not sent and box.get("dir"):
            f = os.path.join(box["dir"], f"dca_state_{SYM}.json")
            s = m.load_json(f) or {}
            if s.get("phase") == "selling":
                rows = json.loads(json.dumps(NEW))
                for n_ in m._plus_locked(s):
                    rows[n_]["d"], rows[n_]["q"] = ROWS[n_]["d"], ROWS[n_]["q"]
                sent["n"] = len(m._plus_locked(s))
                m.save_state_keys(f, {"plus_edit": {"seq": 77, "rows": rows}})

    rr = m._bt_run("dca_buy", cfg, SYM, px, 60.0, q0, b0, SPEC, samples=2000, prog=prog)
    ex, stt = rr["ex"], rr.get("state") or {}
    spent = sum(float(f["price"]) * float(f["qty"]) for f in stt.get("filled") or [])       # the dollars inside the open cycle
    chk = (ex.bal[ex.quote] - q0) + spent - float(stt.get("total_coin_profit") or 0)       # the dollar wallet = the books
    coin = (ex.bal[ex.base] - b0) - sum(float(f.get("net") or 0) for f in stt.get("filled") or []) - float(stt.get("dust_coin") or 0)
    chk = max(abs(chk), abs(coin))
    cyc = stt.get("cycles_log") or []
    return cfg, err, rr, ex, stt, chk, cyc, sent


for nm, px in paths.items():
    cfg, err, rr, ex, stt, chk, cyc, _s = run(nm, px)
    ok(f"⑤ the real DCA+ الشرائي engine on the paper exchange — {nm}: to the end · no refused order · {len(cyc)} cycles closed, every one "
       f"a DOLLAR gain that sold EVERYTHING it bought (the coins = the open cycle + the dust) · the wallet = the books ({chk:.1e})",
       cfg and cfg.get("dca_plus") and cfg.get("plus_rows") and cfg.get("bot_type") == "dca_buy" and rr["why"] == "end" and not ex.rejects and cyc
       and min(c_["profit"] for c_ in cyc) > 0 and abs(chk) < 1e-6, (err, rr["why"], ex.rejects[:3], cyc[:2], chk))
F = [1.0]
for x in ROWS[1:]:
    F.append(F[-1] * (1 - x["d"] / 100))
base_px, miss, n_mk = None, [], 0
for f in ex.fills:                                     # (ts, side, px, qty, fee, maker)
    if f[1] == "sell":
        base_px = None                                 # the cycle closed (sold) ⇒ the next market buy is a new base
    elif not f[5] and base_px is None:
        base_px = f[2]
    elif f[5]:
        n_mk += 1
        if base_px is None or min(abs(f[2] - base_px * k) for k in F[1:]) > 0.0002 + 1e-12:
            miss.append((f, base_px))
    elif base_px is not None and f[2] > base_px * F[1] + 0.0002:
        miss.append((f, base_px))
ok(f"⑤ … every safety buy ({n_mk} limit fills) was at the owner's ladder: the cycle's base × (1 − its distances) — never dearer",
   n_mk > 0 and not miss, miss[:4])
cfg, err, rr, ex, stt, chk, cyc, s_ = run("an edit in the middle of a cycle", paths["a fall through every order, then back up"], edit_at=200)
ok(f"⑤ an edit from the card in the middle of a cycle (the paper exchange · the real engine): applied (plus_seq) · {s_.get('n')} filled "
   f"orders kept · to the end with no refused order · the cycle closed at a dollar gain selling everything · the wallet = the books ({chk:.1e})",
   s_ and stt.get("plus_seq") == 77 and not stt.get("plus_edit_err") and rr["why"] == "end" and not ex.rejects and cyc and min(c_["profit"] for c_ in cyc) > 0
   and abs(chk) < 1e-6, (s_, stt.get("plus_seq"), stt.get("plus_edit_err"), rr["why"], ex.rejects[:3], chk))
lvl = sorted(round(float(l["price"]), 4) for l in (stt.get("planned_levels") or []))
m._bt_tmp.mkdtemp = _mk

# ⑥ the trial path from the form · the demo's kind
kd = m._bt_kind_of({"dca_type": "dca_plus_buy"})
cfg6, err6 = m._bt_dry_cfg("dca_buy", dict(B), SYM, SPEC, P0)
m.__dict__.update(keep)
q6, b6 = m._bt_wallet_def("dca_buy", cfg6 or {}, B, P0, SPEC)
need, p_ = 0.0, P0
for i, x in enumerate(ROWS):
    p_ = p_ * (1 - x["d"] / 100) if i else p_
    need += p_ * x["q"]
ok(f"⑥ «🧪 جرّب» from the form: «dca_plus_buy» ⇒ the buy kind ({kd}) · the trial's settings = a buy DCA with dca_plus and the rows "
   f"(the real deploy's own) · its wallet = the dollars of every row at its price + 3% + 1$ ({q6}$ · {b6} coin)",
   kd == "dca_buy" and cfg6 and cfg6.get("bot_type") == "dca_buy" and cfg6.get("dca_plus") and len(cfg6.get("plus_rows") or []) == 6
   and abs(q6 - round(need * 1.03 + 1.0, 2)) < 0.011 and b6 == 0, (kd, err6, cfg6, q6, b6, need))
ok("⑥ the classic kinds still: «dca» ⇒ dca · «dca_buy» ⇒ dca_buy · «dca_plus» ⇒ dca", m._bt_kind_of({"dca_type": "dca"}) == "dca"
   and m._bt_kind_of({"dca_type": "dca_buy"}) == "dca_buy" and m._bt_kind_of({"dca_type": "dca_plus"}) == "dca")

print(f"✅ t_dca_plus_buy: {sum(res)}/{len(res)}" if all(res) else f"❌ t_dca_plus_buy: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
