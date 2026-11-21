# 🔌 v3.36.49 — the engines' lines about connection cuts stay in the bot's file but are not shown: the owner (14-11) «زيل من السجل بس ما
#   اتغير في المحرك». A closed folder (no network · no keys): a plus bot whose trade_history holds the engines' real cut lines between
#   normal ones ⇒ 📜 the log window · 🔔 the notification centre · the card's last line · the detailed journals show none of them ·
#   the file is not changed · the normal lines (and the profit line) are all there.
#   python3 devtests/t_hide_cut.py [Holy_Dashboard.pyw] [-q]
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

R = tempfile.mkdtemp(prefix="t_hidecut_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
BOT = os.path.join(R, "bot_sol")
os.makedirs(BOT)
json.dump({"symbol": "SOL-USDT", "bot_type": "grid_plus", "grid_percentage": 0.008, "usd_value": 3, "buy_offset": 0.01, "min_price": 70},
          open(os.path.join(BOT, "config_SOL.json"), "w", encoding="utf-8"))
# the engines' own wording (♾️ ➕ 🎚️ — _net_mark · the order-sheet recovery · the aggregated-order journal), newest first
CUT = ["🌐 عاد الإنترنت بعد 42ث — إعادة مزامنة",
       "🧾 [قيد الأمر المجمّع] انقطاع بنص المعالجة — 2 درجة انعالجت قبله، نكمل الباقي بلا تكرار",
       "🧾 [ورقة الأمر] أمر بيع بسعر 83.2794 انرسل قبل الانقطاع (filled) — تسجّل بالدفتر، ما انرسل ثاني",
       "🧾 [انقطاع] أمر شراء بسعر 80.0267 انلغى قبل الانقطاع وما لحق ينحفظ نقله — كمّلنا نقله (المخزن) بسجلّه",
       "🔌 انقطع الإنترنت — إيقاف الأوامر الجديدة مؤقتاً"]
NORMAL = ["📦 [مخزن الشراء] حُجز مستوى 71.5793 | المخزون الآن: 17 أوامر",
          "🔴 بيع 0.04 SOL بسعر 83.2794 — الربح: +0.0262 USDT",
          "🟢 شراء 0.04 SOL بسعر 82.6177"]
rows, t = [], 0
for msg in [CUT[0], NORMAL[0], CUT[1], CUT[2], NORMAL[1], CUT[3], CUT[4], NORMAL[2]]:
    rows.append({"time": time.strftime("%Y-%m-%d %H:%M:00", time.localtime(time.time() - 3600 - t * 60)), "msg": msg}); t += 1   # (relative: the journals keep 7 days — the fixed 14-11 ran out on 21-11)
HP = os.path.join(BOT, "trade_history_SOL.json")
json.dump(rows, open(HP, "w", encoding="utf-8"), ensure_ascii=False)
raw0 = open(HP, "rb").read()
# a journal line copied in by an older version (before v3.36.49) — yesterday's file (the journals keep 7 days: a fixed date ran out on 20-11)
os.makedirs(os.path.join(R, "Holy_Journal"), exist_ok=True)
_yt = time.time() - 86400
with open(os.path.join(R, "Holy_Journal", time.strftime("%Y-%m-%d", time.localtime(_yt)) + ".jsonl"), "w", encoding="utf-8") as f:
    f.write(json.dumps({"t": int(_yt), "c": "trade", "lv": "info", "m": "🔌 انقطع الإنترنت — إيقاف الأوامر الجديدة مؤقتاً", "bot": "bot_sol",
                        "sym": "SOL-USDT"}, ensure_ascii=False) + "\n")
    f.write(json.dumps({"t": int(_yt) + 1, "c": "trade", "lv": "info", "m": "🟢 شراء 0.04 SOL بسعر 81.9", "bot": "bot_sol", "sym": "SOL-USDT"},
                       ensure_ascii=False) + "\n")

ld = importlib.machinery.SourceFileLoader("hd_hidecut", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_hidecut", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
ok("the dashboard runs from the closed folder and finds the bot", m.ROOT == R and any(b["symbol"] == "SOL-USDT" for b in m.bot_dirs().values()), m.ROOT)

h = m.history_of("bot_sol")
msgs = [e.get("msg") for e in h]
ok("📜 the bot's log window: none of the 5 cut lines (🔌 انقطع · 🌐 عاد · [انقطاع] · قبل الانقطاع · المجمّع انقطاع)", not any(c in msgs for c in CUT), msgs)
ok("… every normal line is there, in order (the store line · the sell with its profit · the buy)", msgs == NORMAL, msgs)
ok("… the bot's own file is not touched (byte for byte — the engine and the books read it as before)", open(HP, "rb").read() == raw0)

feed = [e.get("msg") for e in m.feed_all() if e.get("sym") == "SOL-USDT"]
ok("🔔 the notification centre: no cut line", not any(c in feed for c in CUT) and NORMAL[1] in feed, feed)

b = next(b for b in m.bot_dirs().values() if b["symbol"] == "SOL-USDT")
snap = m.bot_snapshot(b)
le = str(snap.get("last_event") or snap.get("last") or "")
ok("the card's last line skips the newest line («🌐 عاد الإنترنت …») and shows the newest normal one", le.startswith("📦 [مخزن الشراء]"), le or list(snap)[:20])

m.journal_ingest_bots()
q = m.journal_query(limit=400)
jm = [e.get("m") for e in q.get("items") or []]
ok("📒 the detailed journals: the cut lines are not copied in · the normal ones are", not any(c in jm for c in CUT) and NORMAL[1] in jm, jm[:12])
ok("… and a cut line copied in by an older version is not shown (the normal line next to it is)",
   "🔌 انقطع الإنترنت — إيقاف الأوامر الجديدة مؤقتاً" not in jm and "🟢 شراء 0.04 SOL بسعر 81.9" in jm, jm[:12])
ok("the filter is only on what is shown: a sell line about profit is never taken for a cut line", not m._cut_line({"msg": NORMAL[1]}) and m._cut_line({"msg": CUT[4]}))
print(f"✅ t_hide_cut: {sum(res)}/{len(res)}" if all(res) else f"❌ t_hide_cut: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
