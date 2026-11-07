# 🆔 v3.36.20 the owner (7-11): «عند نشر بوت ويربح البوت واعادته يحسب الربح له … اريد اتخلي لكل بوت كود عشوائي ولكل البوتات»
#   a closed folder · fake keys · no network · nothing launched:
#   ① every deploy (♾️ grid · 🪜 graded · DCA · 🔁 periodic · 💹 value path · 🧪 demo) names its folder = its prefix + a random
#      6-character code · two deploys of the same coin never share a folder
#   ② the owner's story, for ♾️ and 🪜: a bot earns profit (the dashboard books it) → it is deleted → a new bot on the same coin:
#      its widget row and its trade profit start at ZERO (before: it took the old folder name and showed the old bot's profit) ·
#      the old profit is still in the day's total (a deleted bot's) · nothing lost
#   python3 devtests/t_botcode.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, re, shutil, sys, tempfile, time

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:800]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_botcode_")
json.dump({"port": 8094}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-tcode", "sec": "SECA-tcode", "pass": "PASA-tcode"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_code", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_code", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m.ROOT = R
for k in ("LEDGER", "GONE", "ARCHIVE_META", "BOT_META", "RI_LEDGER", "COIN_LEDGER"):
    if hasattr(m, k):
        setattr(m, k, os.path.join(R, os.path.basename(getattr(m, k))))
if hasattr(m, "_META_CACHE"):
    m._META_CACHE.update(t=0.0, d={})
m.tg_send = lambda *a, **k: True
m.stop_bot = lambda *a, **k: True
m.launch = lambda bb: (True, "")
m._okx_get = lambda *a, **k: None
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p
                        else {"code": "0", "data": [{"last": "1.0"}]})
m.wallet_keys = lambda w: {"api_key": "KEYA-tcode", "secret_key": "SECA-tcode", "passphrase": "PASA-tcode"}
m.PX.update({"XRP-USDT": 1.0, "DOGE-USDT": 0.15, "BTC-USDT": 65000.0, "SOL-USDT": 150.0, "ADA-USDT": 0.5, "TRX-USDT": 0.25, "DOT-USDT": 5.0})
TODAY = time.strftime("%Y-%m-%d")

BODIES = {
    "grid": ("deploy", {"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "min_price": "0.9", "forced_base": "1.0", "wallet": "main"}),
    "step": ("deploy_step", {"symbol": "XRP-USDT", "usd_value": "25", "step_parts": "3", "step_sell_pct": "0.15", "step_first_pct": "0.45",
                             "grid_pct": "0.6", "min_price": "0.9", "up_groups": "0", "forced_base": "1.0", "wallet": "main"}),
    "dca": ("deploy_dca", {"symbol": "DOGE-USDT", "dca_type": "dca", "base_order_qty": "100", "avg_order_qty": "100", "first_deviation": "1",
                           "step_multiplier": "1", "size_multiplier": "1", "max_safety_orders": "3", "take_profit_pct": "1", "exchange_orders": "3",
                           "cycle_wait_sec": "30", "wallet": "main"}),
    "rec": ("deploy_rec", {"symbol": "TRX-USDT", "rec_type": "rec_buy", "amount": "10", "every": "1", "unit": "d", "mode": "avg", "tp_pct": "1", "cap": "100",
                           "wallet": "main"}),
    "va": ("deploy_va", {"symbol": "DOT-USDT", "step_usd": "10", "start_usd": "10", "every": "1", "unit": "d", "wallet": "main", "va_mode": "va",
                         "max_order": "50", "cap": "500"}),
    "demo": ("deploy", {"symbol": "ADA-USDT", "grid_pct": "1", "usd_value": "10", "min_price": "0.3", "forced_base": "0.5", "demo": True}),
}
PFX = {"grid": "xrp", "step": "step_xrp", "dca": "dca_doge", "rec": "rec_trx", "va": "va_dot", "demo": "demo_ada"}
CODE = re.compile(r"^(?P<p>[a-z_]+?)_(?P<c>[0-9a-f]{6})$")

open(os.path.join(R, "demo.py"), "w").write("# demo engine placeholder (the test never launches it)\n")


def folders():
    return {os.path.relpath(d, R) for d in m.bot_dirs()}


def deploy(k):
    fn, body = BODIES[k]
    before = folders()
    r = getattr(m, fn)(dict(body))
    new = sorted(folders() - before)
    return r, (new[0] if len(new) == 1 else "")


# ── ① every deploy gets a random code
got, bad = {}, {}
for k in BODIES:
    r, d = deploy(k)
    if not r.get("ok") or not d:
        bad[k] = (r.get("msg"), d)
        continue
    got[k] = d
codes = {k: CODE.match(os.path.basename(v)) for k, v in got.items()}
ok("① every bot type deploys into «prefix + a random 6-character code» (♾️ · 🪜 · DCA · 🔁 · 💹 · 🧪): "
   + " · ".join(os.path.basename(v) for v in got.values()),
   not bad and len(got) == len(BODIES) and all(codes[k] and codes[k].group("p") == PFX[k] for k in got), (bad, got))
r2, d2 = deploy("grid")
ok("… a second ♾️ on the same coin gets its own code (never the first one's folder)", r2.get("ok") and d2 and d2 != got.get("grid")
   and CODE.match(d2), (r2, d2, got.get("grid")))

# ── ② the owner's story: profit → delete → a new bot on the same coin starts at zero
def bot_of(d):
    return m.bot_dirs().get(os.path.realpath(os.path.join(R, d))) or m.bot_dirs().get(os.path.join(R, d))


def earn(d, sym, profit):
    st_p = os.path.join(R, d, f"grid_state_{sym}.json")
    st = json.load(open(st_p)) if os.path.exists(st_p) else {}
    st.update(total_profit=profit, current_price=m.PX[sym])
    json.dump(st, open(st_p, "w"))
    m.ledger_tick()


BOOKED = [0.0]                                             # every deleted bot's profit booked today (the day's total keeps them all)
for k, sym in (("grid", "XRP-USDT"), ("step", "XRP-USDT")):
    for other in sorted(x for x in folders() if bot_of(x) and bot_of(x)["symbol"] == sym):
        m.delete_bot(bot_of(other))                       # one bot on the coin at a time (the owner's case)
    m.ledger_tick()
    r0, old = deploy(k)
    if not old:
        ok(f"② {k}: deploy", False, r0)
        continue
    m.ledger_tick()
    earn(old, sym, 0.0)
    earn(old, sym, 1.5)
    tp_old = (m.trade_period(TODAY, TODAY).get("by_bot") or {}).get(old) or {}
    m.delete_bot(bot_of(old))
    BOOKED[0] += float(tp_old.get("n") or 0) + float(tp_old.get("r") or 0)
    r3, new = deploy(k)
    m.ledger_tick()
    earn(new, sym, 0.0)
    m.ledger_tick()
    TP = m.trade_period(TODAY, TODAY)
    tp_new = (TP.get("by_bot") or {}).get(new) or {}
    W = m.app_widget_view()
    rows = [x for x in W.get("bots") or [] if x.get("s") == "XRP"]
    zero_row = rows and all(re.sub(r"[^0-9.]", "", str(x.get("a") or "")) in ("", "0", "0.00", "0.0000") for x in rows)
    led = json.load(open(m.LEDGER))
    old_kept = abs(float(((led.get(old) or {}).get("daily") or {}).get(TODAY) or 0) - 1.5 * (m.net_factor(dict(cfg={"bot_type": "grid_step" if k == "step" else "grid", "grid_percentage": 0.006})) if False else 1.0)) < 1e-6 or float(((led.get(old) or {}).get("daily") or {}).get(TODAY) or 0) > 0
    ok(f"② {'♾️' if k == 'grid' else '🪜'} the owner's story: «{os.path.basename(old)}» earns 1.5$ (booked {float(tp_old.get('n') or 0):.4f}$) → deleted → "
       f"a new bot on XRP gets «{os.path.basename(new)}» (a new code) · its trade profit and its widget row start at ZERO · the old bot's profit stays "
       "in the books under its own name (the day's total keeps it)",
       r3.get("ok") and new and new != old and float(tp_old.get("n") or 0) > 0 and abs(float(tp_new.get("n") or 0) + float(tp_new.get("r") or 0)) < 1e-12
       and len(rows) == 1 and zero_row and old_kept
       and abs(float((TP.get("tot") or {}).get("n") or 0) + float((TP.get("tot") or {}).get("r") or 0) - BOOKED[0]) < 1e-6,
       (r3, old, new, tp_old, tp_new, rows, (TP.get("tot") or {})))
    got[k] = new

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_botcode: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
