# 📒 v3.36.52 — the full audit, batch 3: the first time the ledger sees a grid bot that already has profit, the profit goes to the days
#   of the bot's own sell lines (it all went on «today»). A closed folder (no network · nothing launched): a grid bot with sells on
#   three days (the engine's own line format) and its book total; the ledger ticks.
#   python3 devtests/t_ledger_first.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, urllib.request
from datetime import datetime, timedelta

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="t_ledfirst_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
now = datetime.now()
D = [(now - timedelta(days=k)).strftime("%Y-%m-%d") for k in (2, 1, 0)]
GROSS = {D[0]: [0.5, 0.5, 1.0], D[1]: [1.5, 1.5], D[2]: [1.0]}          # 2 · 3 · 1 = 6 in the engine's book
rows = []
for day in reversed(D):
    for i, g in enumerate(reversed(GROSS[day])):
        rows.append({"time": f"{day} 00:0{5 - i}:00", "msg": f"🔴 [بيع فوري] السعر: 80.5 | الكمية: 0.125 | الربح: +{g}$"})
    rows.append({"time": f"{day} 00:00:30", "msg": "🟢 [شراء فوري] السعر: 80.0 | الكمية: 0.125"})


def bot(name, sym, total, hist):
    d = os.path.join(R, name); os.makedirs(d)
    json.dump({"symbol": sym, "bot_type": "grid", "grid_percentage": 0.006, "usd_value": 10, "min_price": 50}, open(os.path.join(d, f"config_{sym}.json"), "w"))
    json.dump({"total_profit": total, "current_price": 80.0}, open(os.path.join(d, f"grid_state_{sym}.json"), "w"))
    json.dump(hist, open(os.path.join(d, f"trade_history_{sym.split('-')[0]}.json"), "w", encoding="utf-8"), ensure_ascii=False)


bot("old_sol", "SOL-USDT", 6.0, rows)                 # ran for three days before the dashboard ever saw it
bot("new_xrp", "XRP-USDT", 0.0, [])                   # deployed just now
ld = importlib.machinery.SourceFileLoader("hd_ledfirst", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_ledfirst", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
b = next(x for x in m.bot_dirs().values() if x["symbol"] == "SOL-USDT")
nf = float(m.net_factor(b))
led = m.ledger_tick()
day = dict((led.get("old_sol") or {}).get("daily") or {})
want = {D[0]: 2.0 * nf, D[1]: 3.0 * nf, D[2]: 1.0 * nf}
ok(f"first sight of a bot with three days of sells: each day gets its own share ({[round(want[d], 4) for d in D]} after fees) — not everything on today",
   set(day) == set(D) and all(abs(day[d] - want[d]) < 2e-4 for d in D), (day, want))
ok("… the total is exactly the book's (after fees) — nothing added, nothing lost", abs(sum(day.values()) - 6.0 * nf) < 1e-5, (sum(day.values()), 6.0 * nf))
ok("… the mark of a first sight is not kept in the ledger file", "_first" not in json.dumps(json.load(open(m.LEDGER, encoding="utf-8"))), None)
# a new sell now ⇒ today only (the ordinary path) · a second tick adds nothing
h = json.load(open(os.path.join(R, "old_sol", "trade_history_SOL.json"), encoding="utf-8"))
h.insert(0, {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "msg": "🔴 [بيع فوري] السعر: 80.5 | الكمية: 0.125 | الربح: +0.4$"})
json.dump(h, open(os.path.join(R, "old_sol", "trade_history_SOL.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump({"total_profit": 6.4, "current_price": 80.0}, open(os.path.join(R, "old_sol", "grid_state_SOL-USDT.json"), "w"))
led = m.ledger_tick(); d2 = dict(led["old_sol"]["daily"]); led = m.ledger_tick(); d3 = dict(led["old_sol"]["daily"])
ok("… afterwards a new sell is booked on today only, once (earlier days untouched · a second tick adds nothing)",
   abs(d2[D[2]] - (want[D[2]] + 0.4 * nf)) < 2e-4 and all(abs(d2[d] - want[d]) < 2e-4 for d in D[:2]) and d3 == d2, (d2, d3))
ok("a bot deployed just now (no profit, no lines) books nothing", not ((led.get("new_xrp") or {}).get("daily") or {}), led.get("new_xrp"))
print(f"✅ t_ledger_first: {sum(res)}/{len(res)}" if all(res) else f"❌ t_ledger_first: {sum(res)}/{len(res)}")
os.chdir(H); shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
