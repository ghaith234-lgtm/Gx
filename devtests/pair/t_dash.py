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

print(f"\n{'✅' if all(RES) else '❌'} t_dash: {sum(RES)}/{len(RES)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(RES) else 1)
