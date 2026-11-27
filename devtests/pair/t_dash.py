# 🔀 شبكة عملتين — the dashboard side (p146 + p147 …): python3 devtests/pair/t_dash.py [Holy_Dashboard.pyw]
#   A «شبكة عملتين» bot folder (its config + the state its engine writes) beside a normal ♾️ bot, in a throw-away root:
#   · the embedded engine = devtests/pair/eng/main_pair.py · engine_for · the kinds audit
#   · ⚠️ the DOLLAR ledger never books its profit (it is XRP) — the ♾️ bot beside it still is booked
#   · the coin ledger (fourth source «pair») and the coin trade book book every sale ONCE, in XRP, on its day
#   · the card's data (`pair`): profit · today · the two next orders · the books · the wallet counted in XRP
#   · the coins it holds free (main · other · the dollar booked) for every other bot / deploy
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))


def _no_net(*a, **k):
    raise OSError("no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="pairdash_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pair", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pair", ld))
a0 = sys.argv
sys.argv = ["x"]
ld.exec_module(m)
sys.argv = a0
m.tg_send = lambda *a, **k: True
RES = []


def ok(name, cond, det=""):
    RES.append(bool(cond))
    print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:600]}"), flush=True)


# ── the engine and the type
src = open(os.path.join(H, "eng", "main_pair.py"), encoding="utf-8").read()
ok("the embedded engine = devtests/pair/eng/main_pair.py (byte for byte)", m.GRIDX_SRC == src)
ok("engine_for(grid_pair) = the pair engine as main.py", m.engine_for({"bot_type": "grid_pair"}) == (m.GRIDX_SRC, "main.py", m.GRIDX_VERSION))
bad = [x for x in m.kinds_audit() if not x[1]]
ok("📐 the kinds audit: every type and every derived list ok", not bad, bad)
ok("its profit route: the coin books (not the dollar)", m._BOT_KINDS["grid_pair"]["cur"] == "coin" and "ledger" not in m._BOT_KINDS["grid_pair"]["route"])
ok("no grid ladder / reinvest wrapper / ladder audit for it (_NONGRID)", "grid_pair" in m._NONGRID)

# ── a pair bot folder + a ♾️ bot beside it
now = time.time()
today = time.strftime("%Y-%m-%d")
yday = time.strftime("%Y-%m-%d", time.localtime(now - 86400))
pd = os.path.join(R, "pair_sol_test1")
os.makedirs(pd)
cfg = {"api_key": "K", "secret_key": "S", "passphrase": "P", "symbol": "SOL-XRP", "bot_type": "grid_pair", "bridge": "USDT", "main_value": 20.0,
       "grid_percentage": 0.02, "down_levels": 3, "up_levels": 2, "profit_to": "main", "forced_base_ratio": 75.0, "fee_rate": 0.001, "is_demo": False}
json.dump(cfg, open(os.path.join(pd, "config_SOL-XRP.json"), "w"))
slots = {str(j): {"j": j, "bp": 75 * 1.02 ** j, "sp": 75 * 1.02 ** (j + 1), "side": "buy" if j < 0 else "sell", "q": 0.0 if j < 0 else 20 / (75 * 1.02 ** j),
                  "c": 0.0 if j < 0 else 20.0, "dq": 0.0} for j in range(-3, 2)}
swaps = [{"t": now - 86400 - 50, "kind": "buy", "j": -1, "sold": 20.0, "got": 0.27, "profit": 0.0},
         {"t": now - 86400, "kind": "sell", "j": -1, "sold": 0.27, "got": 20.31, "profit": 0.31},
         {"t": now - 3600, "kind": "sell", "j": 0, "sold": 0.266, "got": 20.29, "profit": 0.29},
         {"t": now - 60, "kind": "sell", "j": -2, "sold": 0.28, "got": 20.3, "profit": 0.3}]
st = {"pair": {"other": "SOL", "main": "XRP", "bridge": "USDT", "r0": 75.0, "g": 0.02, "mv": 20.0, "dn": 3, "up": 2, "fee": 0.001, "cap": 0.002,
               "capb": 0.0005, "pt": "main", "born": now - 2 * 86400}, "slots": slots, "total_profit": 0.9, "main_book": 60.9, "main_start": 60.0,
      "other_start": 0.53, "other_book": 0.53, "usd_dust": 0.02, "usd_booked": 0.02, "daily": {yday: 0.31, today: 0.59}, "swaps": swaps,
      "next_buy": {"j": -1, "ratio": 73.5, "main": 20.0}, "next_sell": {"j": 0, "ratio": 76.5, "qty": 0.266}, "ratio": 75.4, "px_main": 2.0,
      "px_other": 150.8, "current_price": 150.8, "n_buy": 3, "n_sell": 2, "op": None}
json.dump(st, open(os.path.join(pd, "grid_state_SOL-XRP.json"), "w"))
gd = os.path.join(R, "grid_xrp_test1")
os.makedirs(gd)
json.dump({"api_key": "K", "secret_key": "S", "passphrase": "P", "symbol": "XRP-USDT", "bot_type": "grid", "grid_percentage": 0.01, "usd_value": 10,
           "min_price": 1, "is_demo": False}, open(os.path.join(gd, "config_XRP-USDT.json"), "w"))
json.dump({"total_profit": 1.5}, open(os.path.join(gd, "grid_state_XRP-USDT.json"), "w"))
B = m.bot_dirs()
bp = next(b for b in B.values() if b["cfg"].get("bot_type") == "grid_pair")
bg = next(b for b in B.values() if b["cfg"].get("bot_type") == "grid")
ok("both bots found", bp and bg)

# ── the dollar ledger
m.ledger_tick()
led = m.load_json(m.LEDGER) or {}
kp, kg = os.path.relpath(bp["dir"], m.ROOT), os.path.relpath(bg["dir"], m.ROOT)
ok("⚠️ the dollar ledger never books the pair bot (its 0.9 is XRP, not dollars)", kp not in led and "SOL-XRP" not in led, list(led))
ok("… and still books the ♾️ bot beside it", kg in led, list(led))

# ── the coin books
m.coin_ledger_tick()
cl = m.load_json(m.COIN_LEDGER) or {}
ok("🪙 coin ledger: total in XRP (the main coin) = the three sales 0.9", abs(float((cl.get("total_pair") or {}).get("XRP") or 0) - 0.9) < 1e-9
   and not (cl.get("total_pair") or {}).get("SOL"), cl.get("total_pair"))
ok("… on their days (yesterday 0.31 · today 0.59)", abs(float(((cl.get("daily") or {}).get(yday) or {}).get("XRP", {}).get("pair") or 0) - 0.31) < 1e-9
   and abs(float(((cl.get("daily") or {}).get(today) or {}).get("XRP", {}).get("pair") or 0) - 0.59) < 1e-9, cl.get("daily"))
m.coin_ledger_tick()
cl2 = m.load_json(m.COIN_LEDGER) or {}
ok("… and once only (a second pass books nothing)", abs(float((cl2.get("total_pair") or {}).get("XRP") or 0) - 0.9) < 1e-9, cl2.get("total_pair"))
T = m.load_json(m.COINTR_FILE) or {}
tr_x = sum(float(e.get("q") or 0) for d in (T.get("daily") or {}).values() for e in (d or {}).values() if isinstance(e, dict) and e.get("b") == "XRP")
ok("🪙 the coin trade book: the same 0.9 XRP", abs(tr_x - 0.9) < 1e-9, T.get("daily"))
cp_ = m.coins_period(yday, today)
ok("the period view shows it under «pair» in XRP", abs(float((cp_.get("XRP") or {}).get("pair") or 0) - 0.9) < 1e-9, cp_)

# ── the card's data
snap = m.bot_snapshot(bp)
P = snap.get("pair") or {}
ok("the card: today = the engine's day book (0.59 XRP)", abs(float(snap.get("today") or 0) - 0.59) < 1e-9, snap.get("today"))
ok("the card: profit 0.9 XRP ≈ 1.8$ · the two next orders · the books", abs(P.get("profit", 0) - 0.9) < 1e-9 and abs((P.get("profit_usd") or 0) - 1.8) < 1e-9
   and (P.get("next_buy") or {}).get("ratio") == 73.5 and (P.get("next_sell") or {}).get("ratio") == 76.5 and P.get("main") == "XRP" and P.get("other") == "SOL", P)
ok("the card: the wallet counted in XRP (now vs the start)", P.get("wallet_main") and P.get("wallet_main0") and P.get("wallet_pct") is not None,
   (P.get("wallet_main"), P.get("wallet_main0"), P.get("wallet_pct")))
ok("the card: no net factor on it (the engine's profit is already net)", m.net_factor(bp) == 1.0)

# ── the coins it holds
cla = m._gd_free_claims(bp, st)
ok("the coins it holds free: XRP 60.9 · SOL 0.53 · USDT 0.02", abs(cla.get("XRP", 0) - 60.9) < 1e-9 and abs(cla.get("SOL", 0) - 0.53) < 1e-9
   and abs(cla.get("USDT", 0) - 0.02) < 1e-9, cla)

# ── Telegram (p148): one message per completed sale, in XRP — nothing for a buy, nothing at the first look
if hasattr(m, "_pair_coin_events") and "grid_pair" in open(DASH, encoding="utf-8").read().split("def notifier_loop", 1)[1][:9000]:
    msgs = []
    m.tg_send = lambda t, *a, **k: msgs.append(str(t)) or True

    class _Brk(BaseException):
        pass

    _sl0 = m.time.sleep

    def _once():
        m.time.sleep = lambda *a, **k: (_ for _ in ()).throw(_Brk())
        try:
            m.notifier_loop()
        except _Brk:
            pass
        finally:
            m.time.sleep = _sl0
    sp_ = os.path.join(pd, "grid_state_SOL-XRP.json")
    st["last_trade"] = {"side": "sell", "ratio": 76.9, "qty": 0.28, "main": 20.3, "profit": 0.3, "kept": 0.0, "ts": now - 60, "n": 7}
    json.dump(st, open(sp_, "w"))
    _once()
    n0 = len([x for x in msgs if "شبكة عملتين" in x])
    st["last_trade"] = {"side": "buy", "ratio": 75.0, "qty": 0.27, "main": 20.0, "ts": now - 30, "n": 8}
    json.dump(st, open(sp_, "w"))
    _once()
    n1 = len([x for x in msgs if "شبكة عملتين" in x])
    st["last_trade"] = {"side": "sell", "ratio": 76.6, "qty": 0.27, "main": 20.31, "profit": 0.31, "kept": 0.0, "ts": now - 5, "n": 9}
    st["total_profit"] = 1.21
    json.dump(st, open(sp_, "w"))
    _once()
    pm = [x for x in msgs if "شبكة عملتين" in x]
    ok("📲 Telegram: nothing at the first look (old sales are not re-sent) · nothing for a buy", n0 == 0 and n1 == 0, msgs)
    ok("📲 … one message for the new sale, in XRP with ≈ $ — never «$» on the XRP number",
       len(pm) == 1 and "`+0.31` XRP" in pm[0] and "≈ `0.6200$`" in pm[0] and "`1.21` XRP" in pm[0] and "0.31$" not in pm[0], pm)
    m.ledger_tick()
    led = m.load_json(m.LEDGER) or {}
    ok("… and still no dollar booking after it", kp not in led, list(led))
    rc = m.reconcile()
    ok("the dollar reconciliation skips it (its profit is XRP)", all(str(r.get("sym") or r.get("symbol") or "") != "SOL-XRP" for r in (rc.get("bots") or [])),
       [r.get("sym") or r.get("symbol") for r in (rc.get("bots") or [])])

# ── the calculator and the deploy (p149)
if hasattr(m, "pair_plan"):
    PXS = {"XRP-USDT": 2.0, "SOL-USDT": 150.0, "XLM-USDT": 0.26}
    SPECS = {"XRP-USDT": {"lotSz": 0.000001, "minSz": 1.0}, "SOL-USDT": {"lotSz": 0.000001, "minSz": 0.01}, "XLM-USDT": {"lotSz": 0.000001, "minSz": 10.0}}
    m._acc_price = lambda s_: PXS.get(s_, 0)
    m._acc_spec = lambda s_: SPECS.get(s_, {"lotSz": 1e-8, "minSz": 0.0})
    BAL = {"XRP": 1000.0, "SOL": 5.0}
    m._okx_get = lambda path, *a, **k: {"code": "0", "data": [{"details": [{"ccy": c, "availBal": str(BAL.get(c, 0))} for c in BAL if ("ccy=" + c) in path]}]}
    m.wallet_keys = lambda name: {"api_key": "KW", "secret_key": "SW", "passphrase": "PW"} if name == "W" else None
    LA = []
    m.launch = lambda b, *a, **k: (LA.append(b) or (True, "ok"))
    base_ = {"wallet": "W", "main": "XRP", "other": "SOL", "step_pct": 2, "main_value": 20, "main_amount": 200, "other_amount": 1.0}
    P0 = m.pair_plan(dict(base_))
    ok("🧮 the calculator: 10 buys below from 200 XRP · the levels above the 1 SOL covers", P0.get("ok") and P0["dn"] == 10 and P0["up"] == 3 and not P0["err"],
       {k: P0.get(k) for k in ("dn", "up", "err", "other_need")})
    ok("🧮 the cycle profit after the four fees and the spread ≈ 0.30 XRP on 20 XRP (≈ 0.60$ — conservative · the engine measured +0.31)",
       abs(P0["cycle_main"] - 20 * (1.02 * 0.999 ** 4 * 0.9998 ** 4 - 1)) < 1e-12 and 0.30 < P0["cycle_main"] < 0.31
       and abs(P0["cycle_usd"] - P0["cycle_main"] * 2) < 1e-12, P0.get("cycle_main"))
    ok("🧮 the smallest step that still profits at the worst capped price ≈ 1.2%", 0.011 < P0["min_step"] < 0.0125, P0.get("min_step"))
    for bad, why in (({"step_pct": "nan"}, "الأرقام"), ({"main_value": "inf"}, "الأرقام"), ({"step_pct": 1}, "لا تغطي"), ({"main_value": 0.5}, "1.5 × أدنى حجم"),
                     ({"main": "SOL"}, "مختلفتين"), ({"other": "USDT"}, "وسيط"), ({"main_amount": 0, "other_amount": 0}, "ضع كمية")):
        P1 = m.pair_plan(dict(base_, **bad))
        msg = P1.get("msg") or " · ".join(P1.get("err") or [])
        ok(f"🧮 refused: {bad} ⇒ «{why}»", (not P1.get("ok") or P1.get("err")) and why in msg, msg)
    shutil.rmtree(pd)                                   # (the test folder of the same pair — one per pair)
    r = m.deploy_pair(dict(base_))
    ok("🚀 deploy: launched", r.get("ok") and LA, r)
    nb = next((b for b in m.bot_dirs().values() if b["cfg"].get("bot_type") == "grid_pair" and b["cfg"].get("api_key") == "KW"), None)
    c = (nb or {}).get("cfg") or {}
    ok("🚀 the config = the calculator (pair SOL-XRP · 2% · 20 XRP · 10 below · 3 above · the ratio fixed at 75)",
       c.get("symbol") == "SOL-XRP" and c.get("down_levels") == 10 and c.get("up_levels") == 3 and abs(float(c.get("forced_base_ratio") or 0) - 75.0) < 1e-12
       and abs(float(c.get("grid_percentage")) - 0.02) < 1e-12 and c.get("profit_to") == "main", c)
    ok("🚀 the engine written = the pair engine", nb and open(os.path.join(nb["dir"], "main.py"), encoding="utf-8").read() == m.GRIDX_SRC)
    r2 = m.deploy_pair(dict(base_))
    ok("🚀 one bot per pair", not r2.get("ok") and "واحد لكل زوج" in str(r2.get("msg")), r2)
    BAL["XRP"] = 1250.0
    r3 = m.deploy_pair(dict(base_, other="XLM", other_amount=0, main_amount=1300))
    ok("🚀 not enough free XRP (the SOL bot deployed a second ago, not born yet, holds its 200 by its config) ⇒ refused with the numbers", not r3.get("ok") and "الحر بمحفظتك" in str(r3.get("msg")), r3)
    rd_ = m.deploy_pair(dict(base_, demo=True))
    dmo = next((b for b in m.bot_dirs().values() if b["cfg"].get("bot_type") == "grid_pair" and b["cfg"].get("is_demo")), None)
    ok("🧪 the demo (p153) deploys beside the real one: no keys · its own paper wallet with two legs · the real one is not touched",
       rd_.get("ok") and dmo and not dmo["cfg"].get("api_key") and (m.load_json(os.path.join(dmo["dir"], m.DEMO_WALLET)) or {}).get("pair") is True, rd_)
    if dmo:
        shutil.rmtree(dmo["dir"])
    # the table = the engine: the engine born from this config has exactly the calculator's levels
    sys.path.insert(0, H)
    import pairsim as PS
    ex = PS.market(bal_xrp="400", bal_sol="2")
    pb = PS.PBot(ex, cfg={k: c[k] for k in ("main_value", "grid_percentage", "down_levels", "up_levels", "forced_base_ratio", "profit_to")})
    pb.run([(5, lambda b_: None)], end=30)
    sl = (pb.state() or {}).get("slots") or {}
    same = len(sl) == len(P0["rows"]) and all(abs(sl[str(rw["j"])]["bp"] - rw["bp"]) < 1e-9 * rw["bp"] and abs(sl[str(rw["j"])]["sp"] - rw["sp"]) < 1e-9 * rw["sp"]
                                                and sl[str(rw["j"])]["side"] == rw["side"] for rw in P0["rows"])
    ok("🧮 the table = the engine: every level (ratio to buy · to sell · side) is what the engine is born with", same, (len(sl), len(P0["rows"])))
    pb.cleanup()

# ── «ولا بوت لازم ياخذ هذا الدولار» (p150): the wallet snapshot books the bot's dollar in flight under USDT; the free dollar subtracts it
if "pair_hold" in open(DASH, encoding="utf-8").read():
    m._gd_load = lambda: {"wallets": {"w1": {"quotes": {"USDT": {"avail": 100.0, "dca_hold": 10.0, "pair_hold": 5.0}}}}}
    ok("💵 a bot's budget (the temporary pause) = 100 − 10 (DCA) − 5 (the pair's dollar in flight) = 85",
       abs(m._tp_budget({"wid": "w1", "q": "USDT"}, {"bots": {}}) - 85.0) < 1e-9, m._tp_budget({"wid": "w1", "q": "USDT"}, {"bots": {}}))
    rec = {"avail": 100.0, "dca_hold": 10.0, "pair_hold": 5.0, "min_next": 0.0}
    try:
        m._cw_low({"events": []}, "w1", "USDT", rec, {"bots": {}}, time.time())
    except Exception:
        pass
    ok("💵 the wallet's low-dollar watch: free not reserved = 100 − 5 − 10 = 85 (what the temporary pause reads)", abs(float(rec.get("free_u") or 0) - 85.0) < 1e-9, rec)
    src_ = open(DASH, encoding="utf-8").read()
    gi = src_.split("def _gd_gather", 1)[1][:20000]
    ok("💵 the snapshot books it under the bridge (USDT), never under XRP", 'snap["quotes"].setdefault(_qb' in gi and 'usd_booked' in gi)

# ── the card (p152): the nearest levels · the pause by the ratio · no delete mid-swap · the archive and its re-deploy
if hasattr(m, "_pair_del_wait"):
    ld_ = os.path.join(R, "pair_link_test2")
    os.makedirs(ld_)
    cfg2 = {"api_key": "K", "secret_key": "S", "passphrase": "P", "symbol": "LINK-XRP", "bot_type": "grid_pair", "bridge": "USDT", "main_value": 20.0,
            "grid_percentage": 0.02, "down_levels": 100, "up_levels": 100, "profit_to": "half", "forced_base_ratio": 7.5, "fee_rate": 0.001,
            "is_demo": False, "auto_restart": True}
    json.dump(cfg2, open(os.path.join(ld_, "config_LINK-XRP.json"), "w"))
    sl2 = {str(j): {"j": j, "bp": 7.5 * 1.02 ** j, "sp": 7.5 * 1.02 ** (j + 1), "side": "buy" if j < 0 else "sell",
                    "q": 0.0 if j < 0 else 20 / (7.5 * 1.02 ** j), "c": 0.0 if j < 0 else 20.0, "dq": 0.0, "n": 2 if j in (-1, -2, 5) else 0} for j in range(-100, 100)}
    st2 = {"pair": {"other": "LINK", "main": "XRP", "bridge": "USDT", "r0": 7.5, "g": 0.02, "mv": 20.0, "dn": 100, "up": 100, "pt": "half", "born": now - 86400},
           "slots": sl2, "total_profit": 1.2, "main_book": 2000.0, "other_book": 30.0, "main_start": 2000.0, "other_start": 30.0, "usd_booked": 0.0,
           "ratio": 7.52, "px_main": 2.0, "px_other": 15.04, "op": None, "daily": {today: 0.4}, "swaps": []}
    sp2 = os.path.join(ld_, "grid_state_LINK-XRP.json")
    json.dump(st2, open(sp2, "w"))
    b2 = next(b for b in m.bot_dirs().values() if b["symbol"] == "LINK-XRP")
    P2 = (m.bot_snapshot(b2).get("pair") or {})
    L2 = P2.get("levels") or []
    ok("🪜 the card gets the NEAREST 30 levels each side (not all 200 every tick) · the count of all · the completed sales",
       len(L2) == 60 and {x["j"] for x in L2} == set(range(-30, 30)) and P2.get("n_levels") == 200 and P2.get("sales") == 6,
       (len(L2), P2.get("n_levels"), P2.get("sales"), sorted(x["j"] for x in L2)[:3]))
    m.PX["LINK-XRP"] = 7.52
    rel2 = os.path.relpath(b2["dir"], m.ROOT)
    r_ = m.control(rel2, "pause_buy", None)
    s_ = json.load(open(sp2))
    ok("⏸ pause buy = a floor at the ratio now (7.52) — the control fields only", r_.get("ok") and abs(float(s_.get("buy_floor") or 0) - 7.52) < 1e-12
       and not s_.get("pause_buy") and "7.52" in r_.get("msg", ""), (r_, s_.get("buy_floor")))
    ok("⏸ … a second press says it is paused already (the floor stays)", "أصلاً" in m.control(rel2, "pause_buy", None).get("msg", "")
       and abs(float(json.load(open(sp2)).get("buy_floor") or 0) - 7.52) < 1e-12)
    r_ = m.control(rel2, "resume_buy", None)
    ok("▶️ resume buy clears the floor", r_.get("ok") and float(json.load(open(sp2)).get("buy_floor") or 0) == 0 and "استُؤنف" in r_.get("msg", ""), r_)
    m.control(rel2, "accum_sell", 99)
    a1 = float(json.load(open(sp2)).get("sell_ceiling") or 0)
    m.control(rel2, "accum_sell", None)
    a2 = float(json.load(open(sp2)).get("sell_ceiling") or 0)
    ok("📦 the grid's accum buttons only toggle the pause at the ratio (no price typed in a pair)", abs(a1 - 7.52) < 1e-12 and a2 == 0, (a1, a2))
    rg_ = [m.control(rel2, a_, None) for a_ in ("guard", "reinvest", "edit", "buy_now", "pause")]
    ok("🔀 the grid-only buttons are refused with a clear line", all(not x.get("ok") and "غير متاح" in x.get("msg", "") for x in rg_), rg_)
    # — the delete never mid-swap
    _al0, _sl0, _og0 = m.is_alive, m.time.sleep, m._okx_get
    OK_CALLS = []
    m._okx_get = lambda *a, **k: OK_CALLS.append(a) or {"code": "0", "data": []}
    s_ = json.load(open(sp2))
    s_.update(op={"id": "HBx1", "k": "-1", "kind": "buy"}, usd_booked=3.5)
    json.dump(s_, open(sp2, "w"))
    m.is_alive = lambda d_, sp_: (False, "")
    r_ = m.delete_purge(b2)
    ok("🗑 a stopped bot with a swap in flight is NOT deleted (3.5 USDT between the two coins) — start it to finish the swap",
       not r_.get("ok") and "⛔ لم يُحذف" in r_.get("msg", "") and "3.5000 USDT" in r_.get("msg", "") and os.path.isdir(ld_), r_)
    ok("🗑 … and no exchange call to cancel orders (it has none)", not OK_CALLS, OK_CALLS)
    m.is_alive = lambda d_, sp_: (True, "dash")
    m.time.sleep = lambda *a, **k: None
    r_ = m.delete_bot(b2)
    s_ = json.load(open(sp2))
    ok("🗑 a running bot mid-swap: asked to withdraw (self_destruct) — not deleted until it finishes («⏳ … أعد الحذف بعد قليل»)",
       not r_.get("ok") and "⏳" in r_.get("msg", "") and s_.get("self_destruct") is True and os.path.isdir(ld_), r_)

    def _finish(*a, **k):                                 # the engine finishes the swap and withdraws while the dashboard waits
        x = json.load(open(sp2))
        x.update(op=None, usd_booked=0.0, destruct_done=True)
        json.dump(x, open(sp2, "w"))
    m.time.sleep = _finish
    r_ = m.delete_purge(b2)
    m.is_alive, m.time.sleep, m._okx_get = _al0, _sl0, _og0
    arch = [n_ for n_ in os.listdir(os.path.join(m.ROOT, "_archive")) if n_.endswith("pair_link_test2")] if os.path.isdir(os.path.join(m.ROOT, "_archive")) else []
    ok("🗑 … once the engine says it withdrew (the dollar back to a coin) the delete goes through and archives it", r_.get("ok") and not os.path.isdir(ld_) and arch, r_)
    if arch:
        ri = m.redeploy_info(arch[0])
        pr = ri.get("pre") or {}
        want_ao = sum(20.0 / (7.5 * 1.02 ** j) for j in range(100))
        ok("♻️ the archive re-deploys it in its own form (XRP · LINK · 2% · 20 XRP · 2000 XRP below · the LINK above · half) — the ratio left empty",
           ri.get("ok") and ri.get("form") == "pair" and pr.get("main") == "XRP" and pr.get("other") == "LINK" and abs(pr.get("step_pct", 0) - 2) < 1e-9
           and pr.get("main_value") == 20.0 and abs(pr.get("main_amount", 0) - 2000) < 1e-9 and abs(float(pr.get("other_amount") or 0) - want_ao) < 1e-6 * want_ao
           and pr.get("profit_to") == "half" and "forced_ratio" not in pr and ri.get("ico") == "🔀", ri)
    ok("🗄️ its settings in one line for the archive/report", m._pv_cfg_txt(cfg2) == "LINK/XRP · الخطوة 2% · 20 XRP لكل شراء · 100 تحت · 100 فوق", m._pv_cfg_txt(cfg2))
    ok("🏷️ its name in every list (free coins · archive type · widgets · icons)", m._FREE_T.get("grid_pair") == "🔀 شبكة عملتين"
       and m._PV_TYPE_ALL.get("grid_pair") == "شبكة عملتين" and m._WD_E.get("grid_pair") == "🔀" and m._RD_FORM.get("grid_pair") == "pair")

# ── p154: the balance refresh reads its coins but never asks OKX for orders on «SOL-XRP» (no such instrument)
if hasattr(m, "_pair_del_wait"):
    CALLS = []
    m._okx_get = lambda path, *a, **k: CALLS.append(path) or {"code": "0", "data": [{"details": []}]}
    only = {k_: v_ for k_, v_ in m.bot_dirs().items() if v_["cfg"].get("bot_type") == "grid_pair" and not v_["cfg"].get("is_demo")}
    _bd0 = m.bot_dirs
    m.bot_dirs = lambda *a, **k: only
    m.balances_once()
    m.bot_dirs = _bd0
    ok("💰 the balance refresh reads the pair's coins and never asks for pending orders of a pair symbol", only and CALLS
       and all("orders-pending" not in c for c in CALLS) and any("account/balance" in c for c in CALLS), CALLS)

print(f"\n{'✅' if all(RES) else '❌'} t_dash: {sum(RES)}/{len(RES)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(RES) else 1)
