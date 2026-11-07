# 🧩 the owner's requests 7-11 (all bot types) — a closed folder · fake keys · no network · nothing launched
#   ① ⏱️ every card's run time from a start date saved once (bots · the accumulator): the same after the config is rewritten
#      or copied (new file dates) · a card from before starts from now · the rates keep the profit's own period · a deleted bot's
#      folder name used again starts afresh
#   ② 🗄️ the archive: a deletion records it (settings without keys · started · deleted · profit: trading + released) · a bot
#      deleted before this version shows from its folder («تقريبي») · /api/archive
#   ③ «👛 المحافظ» ⇒ «🔗 الارتباط» (the button · its page · the messages) · 🗄️ between 🛡️ and 📉
#   ④ 📱 the widget: trading profit (ordinary + 💠) in every cell — today · this month · total · each USD bot
#   python3 devtests/t_misc.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, re, shutil, sys, tempfile, time

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_misc_")
json.dump({"port": 8096}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-tmisc", "sec": "SECA-tmisc", "pass": "PASA-tmisc"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_misc", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_misc", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m.ROOT = R
m.BOT_META = os.path.join(R, "Holy_BotMeta.json"); m._META_CACHE.update(t=0.0, d={})
for k in ("LEDGER", "GONE", "ARCHIVE_META"):
    if hasattr(m, k):
        setattr(m, k, os.path.join(R, os.path.basename(getattr(m, k))))
m.tg_send = lambda *a, **k: True
m.stop_bot = lambda *a, **k: True
m._okx_get = lambda *a, **k: None
if not hasattr(m, "started_of"):
    print("❌ this dashboard has none of the 7-11 changes"); sys.exit(1)


def mkbot(name, sym, cfg, st):
    d = os.path.join(R, name)
    os.makedirs(d, exist_ok=True)
    c = dict({"symbol": sym, "bot_type": "grid", "grid_percentage": 0.01, "usd_value": 10, "api_key": "KEYA-tmisc", "secret_key": "SECA-tmisc",
              "passphrase": "PASA-tmisc", "bot_id": "HBTMISC" + name.upper()[:5]}, **cfg)
    json.dump(c, open(os.path.join(d, f"config_{sym}.json"), "w"))
    json.dump(st, open(os.path.join(d, f"grid_state_{sym}.json"), "w"))
    json.dump([], open(os.path.join(d, f"trade_history_{sym.split('-')[0]}.json"), "w"))
    return d


# ── ① the fixed start date
d1 = mkbot("grid_xrp", "XRP-USDT", {}, {"total_profit": 2.5, "current_price": 1.0})
b1 = m.bot_dirs().get(os.path.realpath(d1)) or m.bot_dirs().get(d1)
t0 = time.time()
s1 = m.bot_snapshot(b1)
time.sleep(1.2)
cp = os.path.join(d1, "config_XRP-USDT.json")
c = json.load(open(cp)); c["usd_value"] = 11; json.dump(c, open(cp + ".tmp", "w")); os.replace(cp + ".tmp", cp)   # rewritten (new dates)
os.utime(cp, (t0 - 40 * 86400, t0 - 40 * 86400))                                                              # … and an old date
m._META_CACHE.update(t=0.0)
s2 = m.bot_snapshot(m.bot_dirs().get(os.path.realpath(d1)) or b1)
ok("① a card from before starts from now · its start date is saved once and stays the same after the config is rewritten / its"
   " file dates change", s1.get("started") and abs(s1["started"] - t0) < 5 and s2.get("started") == s1["started"] and s2["age_days"] < 0.01,
   (s1.get("started"), s2.get("started"), s2.get("age_days"), t0))
ok("① the rates keep the profit's own period (the oldest sign, 40 days here) — not the new start", s2.get("rate_daily") is not None
   and abs(s2["rate_daily"] - s2["profit"] / ((time.time() - (t0 - 40 * 86400)) / 86400.0)) < 0.002, (s2.get("rate_daily"), s2.get("profit"), s2.get("age_days")))
meta = json.load(open(m.BOT_META))
ok("① the start date lives in the dashboard's own book (Holy_BotMeta.json), not in a file date", abs(float(meta["grid_xrp"]["started"]) - s1["started"]) < 0.1, meta)
a_t = m.started_of("acc:A1")
ok("① the accumulator's card: its own fixed start («acc:<id>»), the same on every read", a_t and m.started_of("acc:A1") == a_t, a_t)

# ── ② the archive
m._safe(lambda: None)
led = {"grid_xrp": {"symbol": "XRP-USDT", "daily": {time.strftime("%Y-%m-%d"): 2.5}, "last_seen_total": 2.5}}
json.dump(led, open(m.LEDGER, "w"))
r = m.delete_bot(m.bot_dirs().get(os.path.realpath(d1)) or b1)
arch = sorted(os.listdir(os.path.join(R, "_archive")))
am = json.load(open(m.ARCHIVE_META)) if os.path.exists(m.ARCHIVE_META) else {}
it = (am.get("items") or {}).get(arch[-1] if arch else "", {})
ok("② deleting records it: the folder in _archive · started (the fixed date) · deleted · its released profit (net, as the card) · its"
   " trading profit · its start leaves the book",
   r.get("ok") and arch and abs(float(it.get("started") or 0) - s1["started"]) < 0.1 and abs(float(it.get("rel") or 0) - s1["profit"]) < 1e-4
   and it.get("trade") is not None and it.get("deleted")
   and "grid_xrp" not in json.load(open(m.BOT_META)), (r, arch, it))
d1b = mkbot("grid_xrp", "XRP-USDT", {}, {"total_profit": 0.0})                         # the same folder name again
m._META_CACHE.update(t=0.0)
s3 = m.bot_snapshot(m.bot_dirs().get(os.path.realpath(d1b)))
ok("② a new bot in the same folder name starts afresh (not the deleted one's date)", s3.get("started") and s3["started"] > s1["started"], (s3.get("started"), s1["started"]))
old = os.path.join(R, "_archive", "20260101_120000_dca_sol")                           # deleted before this version
os.makedirs(old)
json.dump({"symbol": "SOL-USDT", "bot_type": "dca", "usd_value": 20, "api_key": "KEYA-tmisc", "secret_key": "SECA-tmisc", "passphrase": "PASA-tmisc",
           "wallet": "main"}, open(os.path.join(old, "config_SOL-USDT.json"), "w"))
json.dump({"bots": {"dca_sol@1767268800": {"key": "dca_sol", "sym": "SOL-USDT", "type": "dca", "ts": time.mktime(time.strptime("20260101_120000", "%Y%m%d_%H%M%S")),
                                           "rel": 0.0, "coin": {"SOL": 0.0123}}}}, open(m.GONE, "w"))
V = m.archive_view()
names = [x["name"] for x in V.get("items") or []]
xo = next((x for x in V["items"] if x["folder"] == "dca_sol"), {})
xn = next((x for x in V["items"] if x["folder"] == "grid_xrp"), {})
flat = json.dumps(V, ensure_ascii=False)
ok("② /api/archive lists both, newest first: the one just deleted (its fixed start · its profit) and one deleted before this"
   " version (from its folder · its coin profit from the gone book · start unknown)", V.get("ok") and len(names) == 2 and names[0].endswith("grid_xrp")
   and abs(float(xn.get("started") or 0) - s1["started"]) < 0.1 and not xn.get("approx") and abs(xn.get("rel") - s1["profit"]) < 1e-4 and xo.get("type") == "dca"
   and abs(float((xo.get("coin") or {}).get("SOL") or 0) - 0.0123) < 1e-12 and xo.get("started") is None, (names, xn, xo))
ok("② the archive never shows a key, a secret, a passphrase or the wallet", not re.search(r"KEYA|SECA|PASA|api_key|secret_key|passphrase|\"wallet\"", flat), flat[:500])
ok("② each shows its settings (a line + the full list)", "usd_value" in json.dumps(xo.get("cfg")) and xn.get("cfg_txt") is not None, xo.get("cfg"))

# ── ③ the page: «الارتباط» · 🗄️ between 🛡️ and 📉 · ④ the widget
H = m.HTML_PAGE if hasattr(m, "HTML_PAGE") else open(DASH, encoding="utf-8").read()
nav = H[H.index('<div class="grp" aria-label="الصفحات">'):H.index("</nav>")]
order = [t for t in re.findall(r">([^<>]*?)</button>", nav)]
ok("③ the button «🔗 الارتباط» (no «👛 المحافظ» left on a button or pointing to one) · its page titled so",
   "🔗 الارتباط" in order and not any("المحافظ" in t for t in order) and "🔗 الارتباط — المحافظ وتيليغرام" in H
   and not re.search(r"(من|افتح) 👛 المحافظ", H), order)
ig, ia, il = (next(i for i, t in enumerate(order) if k in t) for k in ("🛡️", "🗄️ الأرشيف", "📉 الخسائر"))
ok("③ «🗄️ الأرشيف» between «🛡️ الرقابة» and «📉 الخسائر»", ig + 1 == ia and ia + 1 == il, order)
m.overview = lambda: {"running": 2, "today_profit": 0.1, "total_profit": 5.0, "stats": {"mtd": 3.3, "first": "2026-10-01"},
                      "bots": [{"dir": "grid_a", "bot_type": "grid", "symbol": "XRP-USDT", "alive": True, "profit": 1.0, "today": 0.1},
                               {"dir": "step_b", "bot_type": "grid_step", "symbol": "SOL-USDT", "alive": True, "profit": 0.0, "today": 0.0},
                               {"dir": "dca_c", "bot_type": "dca", "symbol": "DOGE-USDT", "alive": False, "dca": {"coin_profit": 12.5, "base_coin": "DOGE"}}]}
m.trade_now = lambda: {"today": 0.7, "trade_all": 9.25}
m.trade_period = lambda a, b: {"by_bot": ({"grid_a": {"n": 0.1, "r": 0.2}, "step_b": {"n": 0.0, "r": 0.4}} if a == b else
                                          {"grid_a": {"n": 1.0, "r": 2.0}, "step_b": {"n": 0.0, "r": 6.25}})}
W = m.app_widget_view()
kk = {x[0]: x[1] for x in W["k"]}
rows = {x["s"]: x for x in W["bots"]}
ok("④ the widget's cells are trading profit: today 0.7$ (was the released 0.1$) · this month 3.3$ · total 9.25$ (was 5$)",
   kk.get("ربح اليوم") == "+0.7000$" and kk.get("هذا الشهر") == "+3.3000$" and kk.get("الإجمالي") == "9.2500$", W["k"])
ok("④ each USD bot's today / total = its trading profit (a 🪜 at 100% reinvest: 0.4$ / 6.25$, not 0) · a coin bot keeps its coin",
   rows["XRP"]["a"] == "+0.3000$" and rows["XRP"]["b"] == "3.0000$" and rows["SOL"]["a"] == "+0.4000$" and rows["SOL"]["b"] == "6.2500$"
   and rows["DOGE"]["b"] == "12.50 DOGE", rows)
shutil.rmtree(R, ignore_errors=True)
print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
