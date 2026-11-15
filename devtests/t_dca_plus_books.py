# ⚡ v3.36.56 — DCA+ in the books (rule 12 «🔗 الترابط»): a DCA+ bot = a sell DCA with dca_plus, so every place that counts the sell DCA
#   counts it — and each layer exit is its own entry in cycles_log. A closed folder (fake keys · no network · nothing launched): a DCA+
#   bot and a normal sell DCA, each with today's cycles (the DCA+ one: one closed cycle + two layer exits — one of them by hand, at a loss):
#   · 🪙 the coin ledger today: the DCA+ coin = its cycle + both exits (to the last decimal) · the normal DCA's coin = its cycle
#   · 🧾 the day's trades (bot_day_events · trade_log): three lines for the DCA+ bot
#   · 📉 the losses: the hand exit at a loss is listed (DCA بيعي) · the automatic ones are not
#   · 🔗 the linkage audit (link_audit): no ❌
#   python3 devtests/t_dca_plus_books.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time, urllib.request
from datetime import datetime

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

R = tempfile.mkdtemp(prefix="t_dcapb_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
json.dump({"port": 8096}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "devtests-a", "sec": "devtests-s", "pass": "devtests-p"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_dcapb", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_dcapb", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
m.launch = lambda b: (True, "test")
m._okx_get = lambda *a, **k: None
m._okx_pub = lambda p: None
m.wallet_keys = lambda w: {"api_key": "devtests-a", "secret_key": "devtests-s", "passphrase": "devtests-p"}
BODY = {"base_order_qty": "0.01", "avg_order_qty": "0.01", "first_deviation": "0.5", "step_multiplier": "1.2", "size_multiplier": "1.5",
        "max_safety_orders": "5", "take_profit_pct": "1", "exchange_orders": "3", "cycle_wait_sec": "30", "wallet": "main"}
made = {}
for sym, extra in (("ETH-USDT", {"dca_type": "dca_plus", "lx_pct": "0.5"}), ("LTC-USDT", {"dca_type": "dca"})):
    before = set(m.bot_dirs())
    r = m.deploy_dca(dict(BODY, symbol=sym, **extra))
    made[sym] = sorted(set(m.bot_dirs()) - before)[0]
    assert r.get("ok"), r
bots = m.bot_dirs()
bp, bn = bots[made["ETH-USDT"]], bots[made["LTC-USDT"]]
ok("the two bots: ETH a DCA+ (sell DCA + dca_plus · its engine dca_plus.py) · LTC a normal sell DCA (dca.py)",
   bp["cfg"].get("dca_plus") and bp["cfg"]["bot_type"] == "dca" and not bn["cfg"].get("dca_plus")
   and m.engine_for(bp["cfg"])[0] == m.DCAP_SRC and m.engine_for(bn["cfg"])[0] == m.DCA_SRC)
now = time.time()
CP = [{"id": "HDP-1-%d" % int(now - 7200), "n": 1, "ts": now - 7200, "profit": 0.0004, "px": 1990.0, "out": 0.05, "in": 0.0504, "manual": False},
      {"id": "HDP-x3-%d-1" % int(now - 3600), "n": 1, "ts": now - 3600, "profit": 0.00007, "px": 2026.3, "out": 0.0225, "in": 0.02257, "manual": False, "lx": [3]},
      {"id": "HDP-x4-%d-2" % int(now - 1800), "n": 1, "ts": now - 1800, "profit": -0.00011, "px": 2060.0, "out": 0.03375, "in": 0.03364, "manual": True, "lx": [4]}]
CN = [{"id": "HDN-1-%d" % int(now - 5400), "n": 1, "ts": now - 5400, "profit": 0.0123, "px": 70.0, "out": 1.0, "in": 1.0123, "manual": False}]
for b, cl in ((bp, CP), (bn, CN)):
    sp = m.paths_of(b)[0]
    st = m.load_json(sp) or {}
    st.update(phase="selling", current_price=2030.0 if b is bp else 70.0, cycles_done=1, cycles_log=cl, total_coin_profit=round(sum(c["profit"] for c in cl), 10),
              filled=[{"price": 2000.0 if b is bp else 70.0, "qty": 0.01, "n": 0, "net": 19.98 if b is bp else 0.699, "fid": 1}])
    m.save_json_atomic(sp, st)
today = datetime.now().strftime("%Y-%m-%d")
json.dump({"since": now - 4 * 3600, "items": [], "done": []}, open(m.LOSS_FILE, "w"))   # the losses book started 4 h ago (a dashboard already running)
for fn in ("ledger_tick", "coin_ledger_tick"):
    try:
        getattr(m, fn)()
    except Exception as e:
        ok(f"{fn} runs", False, repr(e))
cl_today = m._safe(m.coin_ledger_view, default=None) if hasattr(m, "coin_ledger_view") else None
led = m.load_json(m.COIN_LEDGER) if hasattr(m, "COIN_LEDGER") else {}
day = ((led or {}).get("days") or {}).get(today) or {}
eth = (day.get("total_dca") or day.get("dca") or {})
txt = json.dumps(led, ensure_ascii=False)[:3000]
want_p = round(sum(c["profit"] for c in CP), 10)
got_p = None
for k in ("total_dca",):
    v = (((led or {}).get("days") or {}).get(today) or {}).get(k) or {}
    if "ETH" in v:
        got_p = round(float(v["ETH"]), 10)
if got_p is None:                                   # the ledger's shape: look for the ETH amount wherever today's DCA total is kept
    def walk(o, path=()):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk(v, path + (k,))
        else:
            yield path, o
    for pth, v in walk(led or {}):
        if today in pth and "ETH" in pth and isinstance(v, (int, float)) and abs(float(v) - want_p) < 1e-9:
            got_p = round(float(v), 10)
ok(f"🪙 the coin ledger today: ETH = its cycle + both layer exits ({want_p:+.8f} — the hand exit at a loss included)", got_p is not None and abs(got_p - want_p) < 1e-9, txt)
ev = m.bot_day_events(bp, today) or []
ok("🧾 the day's events of the DCA+ bot: three (the cycle · two layer exits)", len(ev) == 3, ev)
tl = m.trade_log(today) or {}
crow = [e for e in (tl.get("coin_rows") or []) if "ETH" in json.dumps(e, ensure_ascii=False)]
ok("🧾 the day's trade log: the DCA+ bot's three entries in the coin section (to the last decimal)", len(crow) == 3
   and abs(sum(float(e.get("q") or e.get("profit") or e.get("v") or 0) for e in crow) - want_p) < 1e-9, crow)
lv = m.loss_view() or {}
s_lv = json.dumps(lv, ensure_ascii=False)
li = [x for x in (lv.get("items") or []) if "ETH" in json.dumps(x, ensure_ascii=False)]
ok("📉 the losses page: the hand exit at a loss is there (−0.00011 ETH) · the automatic exits (profits) are not", len(li) == 1 and "-0.00011" in json.dumps(li, ensure_ascii=False)
   or (len(li) == 1 and abs(abs(float(li[0].get("q") or li[0].get("coin") or li[0].get("amt") or 0)) - 0.00011) < 1e-9), (li, s_lv[:600]))
la = m.link_audit(force=True) or {}
s_la = json.dumps(la, ensure_ascii=False)
bad = [x for x in (la.get("items") or la.get("rows") or []) if "❌" in json.dumps(x, ensure_ascii=False)]
ok("🔗 the linkage audit (link_audit): no ❌ with a DCA+ bot and its layer exits in the books", "❌" not in s_la, (bad or s_la)[:1500] if isinstance(bad, list) else bad)
print(f"✅ t_dca_plus_books: {sum(res)}/{len(res)}" if all(res) else f"❌ t_dca_plus_books: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
