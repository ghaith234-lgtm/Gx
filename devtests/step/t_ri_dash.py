# 🪜💠 reinvest phase E — the dashboard's side for the graded grid (a closed folder · fake keys · no network · launch never runs)
#   deploy with reinvest (the percentage checked · written for the engine · the trial path reads it) · the 🔄 action: on = the
#   setting (no restart) · off = the setting + the release flag · 💉 ➖ ⚖️ write the same request files as the grid, keyed by the
#   slot «j:k» · the snapshot from the slots (a row per slot · io = the growth inside its order · unwind · desync) · launch never
#   wraps 🪜 in the grid's reinvest.py · the card's buy size = base + growth · the trial path's profit = ordinary + reinvested
#   python3 devtests/step/t_ri_dash.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_ri_dash_")
json.dump({"port": 8097}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-tridash", "sec": "SECA-tridash", "pass": "PASA-tridash"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_ridash", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_ridash", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m._okx_pub = lambda p: {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None
m._okx_get = lambda *a, **k: None
m.PX.update({"XRP-USDT": 1.0, "DOGE-USDT": 0.15})
m.tg_send = lambda *a, **k: True
m.ROOT = R
REAL_LAUNCH = m.launch
LAUNCHED = []
m.launch = lambda bb: (LAUNCHED.append(bb["cfg"]) or (True, ""))
m.wallet_keys = lambda w: {"api_key": "KEYA-tridash", "secret_key": "SECA-tridash", "passphrase": "PASA-tridash"}


def body(**kw):
    b = {"symbol": "DOGE-USDT", "usd_value": "15", "step_parts": "3", "step_sell_pct": "0.5", "step_first_pct": "1", "grid_pct": "3",
         "min_price": "0.1", "up_groups": "0", "forced_base": "0.15", "wallet": "main"}
    b.update(kw)
    return b


if not hasattr(m, "_step_ri_snapshot"):
    print("❌ this dashboard has no 🪜 reinvest (before v3.36.18 phase E)"); sys.exit(1)

# ── deploy
d1 = m.deploy_step(body(reinvest=True, reinvest_pct="60"))
c1 = json.load(open(os.path.join(R, d1["dir"], "config_DOGE-USDT.json"))) if d1.get("ok") else {}
ok("deploy with «💠 إعادة الاستثمار» 60%: the bot's settings carry reinvest = on · 60 (the engine reinvests from its first sale)",
   d1.get("ok") and c1.get("reinvest") is True and c1.get("reinvest_pct") == 60.0, (d1, c1))
shutil.rmtree(os.path.join(R, d1.get("dir", "none")), ignore_errors=True)
d2 = m.deploy_step(body(reinvest=True, reinvest_pct="150"))
d3 = m.deploy_step(body(reinvest=True, reinvest_pct="nan"))
d4 = m.deploy_step(body())
c4 = json.load(open(os.path.join(R, d4["dir"], "config_DOGE-USDT.json"))) if d4.get("ok") else {}
ok("deploy refuses 150% and NaN · without the box: no reinvest keys at all (the engine never makes a book)",
   not d2.get("ok") and not d3.get("ok") and "0 إلى 100" in d2.get("msg", "") and d4.get("ok") and "reinvest" not in c4, (d2, d3, c4))
shutil.rmtree(os.path.join(R, d4.get("dir", "none")), ignore_errors=True)
spec = {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 0.1}
_keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
         if hasattr(m, k)}
cfg_bt, err_bt = m._bt_dry_cfg("grid_step", body(reinvest=True, reinvest_pct="50"), "DOGE-USDT", spec, 0.15)
for k, v in _keep.items():
    setattr(m, k, v)
ok("the trial path reads the same form: its engine reinvests 50%", cfg_bt and cfg_bt.get("reinvest") is True and cfg_bt.get("reinvest_pct") == 50.0, (cfg_bt, err_bt))

# ── a running 🪜 bot folder (its state as the engine writes it)
F = os.path.join(R, "step_xrp")
os.makedirs(F)
CFG = {"symbol": "XRP-USDT", "bot_type": "grid_step", "usd_value": 15, "step_parts": 3, "step_sell": 0.005, "step_first": 0.01,
       "grid_percentage": 0.03, "min_price": 0.7, "up_groups": 1, "forced_base_price": 1.0, "fee_rate": 0.0008, "taker_rate": 0.001,
       "api_key": "KEYA-tridash", "secret_key": "SECA-tridash", "passphrase": "PASA-tridash", "bot_id": "HBTRIDASH001"}
json.dump(CFG, open(os.path.join(F, "config_XRP-USDT.json"), "w"))
ST = {"step": {"P0": 1.0, "G": 0.03, "d": 0.005, "N": 3, "Q": 15, "f": 0.0008, "t": 0.001}, "total_profit": 0.5, "current_price": 0.99,
      "slots": {"-1:1": {"j": -1, "k": 1, "bp": 0.970873786408, "sp": 0.980582524272, "q": 5.149999, "side": "buy", "sq": 0, "acc": 0, "g": 0.2,
                         "o": {"id": "11", "st": "live", "px": 0.9708, "sz": 5.349999}},
                "-1:2": {"j": -1, "k": 2, "bp": 0.970873786408, "sp": 0.985436893204, "q": 5.149999, "side": "sell", "sq": 5.345879,
                         "acc": 0, "g": 0.2, "spent": 5.2, "o": {"id": "12", "st": "live", "px": 0.9854, "sz": 5.345879}},
                "-1:3": {"j": -1, "k": 3, "bp": 0.970873786408, "sp": 0.990291262136, "q": 5.149999, "side": "buy", "sq": 0, "acc": 0, "g": 0.1,
                         "o": {"id": "13", "st": "live", "px": 0.9708, "sz": 4.9}},
                "0:1": {"j": 0, "k": 1, "bp": 1.0, "sp": 1.01, "q": 5.0, "side": "sell", "sq": 4.996, "acc": 0, "o": None}},
      "reinvest": {"on": True, "pct": 100, "credited": 0.6, "out_usd": 0.1, "inj_total": 0.0, "cycles": 9, "started_ts": 1.0,
                   "levels": {"-1:1": {"base_qty": 5.149999, "grown_qty": 0.2, "usd_book": 0.0003, "px": 0.970873786408, "inj_book": 0, "inj_grown": 0, "cycles": 3},
                              "-1:2": {"base_qty": 5.149999, "grown_qty": 0.2, "usd_book": 0.0002, "px": 0.970873786408, "inj_book": 0, "inj_grown": 0, "cycles": 3},
                              "-1:3": {"base_qty": 5.149999, "grown_qty": 0.1, "usd_book": 0.0001, "px": 0.970873786408, "inj_book": 0, "inj_grown": 0, "cycles": 3}}}}
json.dump(ST, open(os.path.join(F, "grid_state_XRP-USDT.json"), "w"))
b = m.bot_dirs().get(os.path.realpath(F)) or m.bot_dirs().get(F)
snap = m.reinvest_snapshot(b, ST) if b else None
rows = {r["kk"]: r for r in (snap or {}).get("rows") or []}
ok("the snapshot from the slots: a row per slot keyed «j:k» (the requests' key) · its label «المستوى · الجزء» · the pots' dollars ·"
   " a sell's growth in coins", snap and set(rows) == {"-1:1", "-1:2", "-1:3", "0:1"} and rows["-1:2"]["lbl"] == "-1 · 2/3"
   and rows["-1:1"]["s"] == "buy" and rows["-1:2"]["s"] == "sell" and abs(snap["coin"] - 0.2) < 1e-12 and snap.get("file") is True
   and abs(snap["usd"] - (0.0006 + 0.3 * 0.970873786408)) < 1e-4, (snap and {k: v for k, v in snap.items() if k != "rows"}, rows))
ok("… io = the growth really inside its order (sell: the coins above the base after its fee · buy: all of it)",
   abs(rows["-1:1"]["io"] - 0.2) < 1e-12 and abs(rows["-1:2"]["io"] - min(0.2, 5.345879 - 5.149999 * (1 - 0.0008))) < 1e-9, rows["-1:2"])
ok("… desync: a live buy whose size ≠ base + growth is flagged (-1:3: 4.9 at OKX, 5.249999 wanted) · -1:1 right",
   [d["kk"] for d in snap["desync"]] == ["-1:3"], snap["desync"])
sv = {(x[0], x[1]): x for x in m._step_slots_view(ST)}
ok("the card's slot view: a buy's size = base + growth (-1:1 → 5.349999)", abs(sv[(-1, 1)][4] - 5.349999) < 1e-9, sv[(-1, 1)])
ok("the trial path's profit for 🪜 = total_profit + reinvested − released (0.5 + 0.6 − 0.1 = 1.0)",
   abs(m._bt_cum(ST, "total_profit", None) - 1.0) < 1e-12 and abs(m._bt_cum({"total_profit": 0.5}, "total_profit", None) - 0.5) < 1e-12)
rc = m._bt_ri_coin("grid_step", {"state": ST})
ok("the trial path's reinvested coins for 🪜 (growth 0.5 · pots 0.0006$)", rc and abs(rc["q"] - 0.5) < 1e-12 and abs(rc["usd"] - 0.0006) < 1e-12, rc)

# ── the actions
d_rel = os.path.basename(F)
LAUNCHED.clear()
r_on = m.control(d_rel, "reinvest", None)
c_on = json.load(open(os.path.join(F, "config_XRP-USDT.json")))
ok("🔄 on: the setting on · no restart (the engine reads it live) · no flag", r_on.get("ok") and c_on.get("reinvest") is True and not LAUNCHED
   and not os.path.exists(os.path.join(F, "reinvest_release.flag")), (r_on, c_on.get("reinvest"), LAUNCHED))
r_pct = m.control(d_rel, "ri_pct", 40)
ok("⚖️ the percentage: written for the engine (40)", r_pct.get("ok") and json.load(open(os.path.join(F, "config_XRP-USDT.json"))).get("reinvest_pct") == 40, r_pct)
r_inj = m.control(d_rel, "ri_inject", [{"k": "-1:1", "px": 0.970873786408, "usd": 3}, {"k": "0:1", "px": 1.0, "coin": 2}])
rq = json.load(open(os.path.join(F, "reinvest_inject.json"))) if os.path.exists(os.path.join(F, "reinvest_inject.json")) else {}
ok("💉 the injection: the grid's request file, each item keyed by its slot «j:k»", r_inj.get("ok") and [x["k"] for x in rq.get("items") or []] == ["-1:1", "0:1"]
   and rq["items"][0]["usd"] == 3 and rq["items"][1]["coin"] == 2, (r_inj, rq))
os.remove(os.path.join(F, "reinvest_inject.json"))
r_wd = m.control(d_rel, "ri_withdraw", [{"k": "-1:2", "px": 0.970873786408, "cap_q": 0, "gain_q": 0.1}])
wq = json.load(open(os.path.join(F, "reinvest_withdraw.json"))) if os.path.exists(os.path.join(F, "reinvest_withdraw.json")) else {}
ok("➖ the withdrawal: the grid's request file, keyed «j:k» (coins from the sell side)", r_wd.get("ok") and wq.get("items") and wq["items"][0]["k"] == "-1:2"
   and wq["items"][0].get("gain_q") == 0.1, (r_wd, wq))
os.remove(os.path.join(F, "reinvest_withdraw.json"))
r_off = m.control(d_rel, "reinvest", None)
c_off = json.load(open(os.path.join(F, "config_XRP-USDT.json")))
ok("🔄 off: the setting off + the release flag (the engine releases within seconds) · no restart", r_off.get("ok") and c_off.get("reinvest") is False
   and os.path.exists(os.path.join(F, "reinvest_release.flag")) and not LAUNCHED, (r_off, c_off.get("reinvest")))
r_g = m.control(d_rel, "guard", None)
ok("⚔️ still refused for 🪜 (its engine has no knife guard)", not r_g.get("ok"), r_g)

# ── launch never wraps 🪜 in the grid's reinvest.py
m.launch = REAL_LAUNCH
import subprocess as _sp
CMD = []


class _P:
    pid = 4242

    def __init__(self, a, *x, **k):
        CMD.append(a)

    def poll(self):
        return None


m.subprocess.Popen = _P
open(os.path.join(F, "reinvest.py"), "w").write("# the grid's wrapper must never run for 🪜\n")
bb = dict(b, cfg=dict(CFG, reinvest=True))
try:
    okl, msg = m.launch(bb)
except Exception as e:
    okl, msg = False, f"{type(e).__name__}: {e}"
used = " ".join(map(str, CMD[0])) if CMD else ""
ok("launch with reinvest on: the 🪜 engine itself (main.py), never the grid's reinvest.py wrapper", CMD and "reinvest.py" not in used and "main.py" in used, (okl, msg, used))
m.subprocess.Popen = _sp.Popen
shutil.rmtree(R, ignore_errors=True)
print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
