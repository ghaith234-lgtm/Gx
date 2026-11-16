# 🚨 v3.36.60 — the «فشل أوامر متكرر» alert (p104). The owner (16-11) sent: «🚨 [فشل أوامر متكرر] XRP-USDT — مرفوضة آخر ساعة: 0 ·
#   متتالية: 21 · آخر خطأ: ⚠️ [رفض أمر شراء] الكمية 2.002192 بسعر 0.9586 (المستوى -13 · الجزء 1): Order f…» — «ما مشكلة هذه».
#   A closed folder (no network · nothing launched): bots with the engines' own log lines, the dashboard's own health_of / health_alert_tick:
#   ① his case: 21 buy refusals (the dollars ran out — 51008) all older than an hour, nothing since ⇒ not «bad» (no 🚨 on the card) · no
#     alert · (v3.36.59 sent it every hour)
#   ② the same refusals NOW (in the last hour): the card shows 🚨 · still no alert — a buy refused for dollars has its own notices
#     (⏳ the temporary pause · 💵 «توفر دولار» · 🛡️ «نفد الدولار الحر»)
#   ③ another refusal (OKX's price limit) three times in the last hour ⇒ the alert, once an hour, with the reason in Arabic and its code
#     («السعر خارج حدود المنصة (51006)») — not the cut English
#   ④ a SELL refused for lack of coins is a real problem ⇒ alerted («الرصيد لا يكفي (51008)») · a trade after the refusals ⇒ fine again ·
#     a demo bot ⇒ nothing
#   python3 devtests/t_health_alert.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time, urllib.request

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
R = tempfile.mkdtemp(prefix="t_ha_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_ha", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_ha", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.ROOT = R
SENT = []
m.tg_send = lambda t, *a, **k: SENT.append(str(t)) or True
NOW = time.time()
T = lambda ago: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(NOW - ago))
BUY_CASH = "⚠️ [رفض أمر شراء] الكمية 2.002192 بسعر 0.9586 (المستوى -13 · الجزء 1): Order failed. Insufficient USDT balance in account"
SELL_COIN = "⚠️ [رفض أمر بيع] كمية (12.5) بسعر (1.0412): Order failed. Insufficient XRP balance in account"
PX_LIM = "⚠️ [رفض أمر شراء] كمية (12.5) بسعر (0.7012): The order price is higher than the highest bid limit — sCode 51006"
FILL = "🟢 [شراء] السعر: 0.9601 | الكمية: 2.0 -> تم تجهيز بيع بسعر: 0.9701"


def mk(folder, sym, bt, hist, demo=False):
    d = os.path.join(R, folder)
    os.makedirs(d, exist_ok=True)
    cfg = {"symbol": sym, "bot_type": bt, "is_demo": demo, "api_key": "" if demo else "k", "secret_key": "" if demo else "s", "passphrase": "" if demo else "p"}
    json.dump(cfg, open(os.path.join(d, f"config_{sym}.json"), "w"))
    b = {"dir": d, "symbol": sym, "cfg": cfg, "cfg_path": os.path.join(d, f"config_{sym}.json")}
    json.dump(hist, open(m.paths_of(b)[1], "w"), ensure_ascii=False)
    return b


def reset():
    SENT.clear()
    m._ALERT_SENT.clear()
    m._HEALTH_CACHE.clear()
    for n in os.listdir(R):
        if os.path.isdir(os.path.join(R, n)):
            shutil.rmtree(os.path.join(R, n))


# ① the owner's case: 21 old refusals, nothing since
reset()
b = mk("xrp_step", "XRP-USDT", "grid_step", [{"time": T(3700 + 300 * i), "msg": BUY_CASH} for i in range(21)] + [{"time": T(30000), "msg": FILL}])
h = m.health_of(b)
m.health_alert_tick()
ok(f"① his case — 21 buy refusals (dollars ran out) all older than an hour: not «bad» ({h['state']} · streak {h['streak']} · last hour "
   f"{h['fails_1h']}) · no 🚨 · no alert", h["state"] != "bad" and h["streak"] == 21 and h["fails_1h"] == 0 and not SENT, (h, SENT))
# ② the same refusals now
reset()
b = mk("xrp_step", "XRP-USDT", "grid_step", [{"time": T(60 + 300 * i), "msg": BUY_CASH} for i in range(6)])
h = m.health_of(b)
m.health_alert_tick()
ok(f"② the same refusals in the last hour ({h['fails_1h']}): the card shows 🚨 (bad) · no alert — a buy refused for dollars has its own "
   f"notices (⏳ · 💵 · 🛡️)", h["state"] == "bad" and not SENT, (h, SENT))
# ③ another reason, three times in the hour
reset()
b = mk("ada_grid", "ADA-USDT", "grid", [{"time": T(60 + 200 * i), "msg": PX_LIM} for i in range(3)] + [{"time": T(9000), "msg": FILL}])
m.health_alert_tick()
m.health_alert_tick()
ok(f"③ a price-limit refusal ×3 in the hour ⇒ one alert (not one per scan) with the reason in Arabic: «{(SENT[0] if SENT else '').splitlines()[-1][:150]}»",
   len(SENT) == 1 and "السعر خارج حدود المنصة (51006)" in SENT[0] and "[رفض أمر شراء]" in SENT[0] and "highest bid" not in SENT[0], SENT)
# ④ a sell refused for coins · a trade after · a demo
reset()
b = mk("xrp_grid", "XRP-USDT", "grid", [{"time": T(60 + 200 * i), "msg": SELL_COIN} for i in range(3)])
m.health_alert_tick()
ok("④ a SELL refused for lack of coins (a real problem) ⇒ alerted: «الرصيد لا يكفي (51008)»", len(SENT) == 1 and "الرصيد لا يكفي (51008)" in SENT[0]
   and "[رفض أمر بيع]" in SENT[0], SENT)
reset()
b = mk("xrp_grid", "XRP-USDT", "grid", [{"time": T(30), "msg": FILL}] + [{"time": T(60 + 200 * i), "msg": PX_LIM} for i in range(4)])
h = m.health_of(b)
m.health_alert_tick()
ok(f"④ a trade after the refusals ⇒ the streak ends ({h['streak']}) · warn at most · no alert", h["streak"] == 0 and h["state"] != "bad" and not SENT, (h, SENT))
reset()
b = mk("demo_xrp", "XRP-USDT", "grid", [{"time": T(60 + 200 * i), "msg": PX_LIM} for i in range(5)], demo=True)
m.health_alert_tick()
ok("④ a demo bot ⇒ nothing", not SENT, SENT)
ok("the reason helper: 51008 · 51020 · 51006 · 50011 · unknown kept", m._rej_why("Order failed. Insufficient USDT balance")[1] == "51008"
   and m._rej_why("sCode 51020 below minimum")[1] == "51020" and m._rej_why("price limit")[1] == "51006" and m._rej_why("Too Many Requests")[1] == "50011"
   and m._rej_why("something else") == ("", "") and "something else" in m._rej_short("⚠️ [رفض أمر بيع] كمية (1) بسعر (2): something else"))
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_health_alert: {sum(res)}/{len(res)}" if res and all(res) else f"❌ t_health_alert: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
