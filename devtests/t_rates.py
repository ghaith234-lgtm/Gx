# 📈 every card's profit rate from its own trading (v3.36.33) — the owner (13-11): «اريد معدل الربح المتوقع يومي شهري سنوي لكل الكروت ،
#   زيل القديم لان القديم عند تشغيل اعادة الاستثمار يطفي لانه مرتبط بعداد الربح ، لا اتعدل على عداد الربح ، بس خلي الكروت تعتمد كل واحد
#   على تداولها ان كان بدون استثمار او استثمار». A closed folder with every card kind (devtests/seed_cards.py: fake keys · no network ·
#   nothing launched · ten days of run time and of trading in the books):
#   ① the ♾️ grid with 💠 reinvest 100%: its profit counter stays ~0 (the old rate died: counter ÷ days) — the new rate = its trading
#      (n + 💠 r per day, the same `trade_period` as the widget and the reports) ÷ its 10 days · the counter itself unchanged
#   ② every USD card (➕ 🎚️ 🪜 · 📈 DCA buy · 🟢 periodic buy · 💹 value path) = its own trading ÷ its days, each its own number ·
#      📉 DCA sell and 🔴 periodic sell = their coin profit ÷ days, in the coin
#   ③ under half a day ⇒ no rate («—») · the books unreadable ⇒ the card's own profit as before (never a crash) · the all-time trading
#      is read once a minute (not on every refresh)
#   python3 devtests/t_rates.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


sys.path.insert(0, H)
import seed_cards                                             # noqa: E402

R = tempfile.mkdtemp(prefix="t_rates_")
cwd0 = os.getcwd()
try:
    made = seed_cards.seed(R, DASH)
    os.chdir(R)
    ld = importlib.machinery.SourceFileLoader("hd_rates", os.path.join(R, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_rates", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m._okx_get = lambda *a, **k: None
    m._okx_pub = lambda p: None
    m.tg_send = lambda *a, **k: True
    m.PX.update({"XRP-USDT": 2.4512, "SOL-USDT": 182.37, "ADA-USDT": 0.7421, "TRX-USDT": 0.2513, "DOGE-USDT": 0.1834, "LINK-USDT": 17.46,
                 "XLM-USDT": 0.4127, "DOT-USDT": 5.214, "SUI-USDT": 3.618})
    O = m.overview()
    B = {b["symbol"]: b for b in O["bots"]}
    led = json.load(open(os.path.join(R, "Holy_Ledger.json")))
    tot = lambda sym: round(sum((led.get(os.path.relpath(made[sym], R)) or {}).get("daily", {}).values()), 8)

    # ── ① the reinvesting grid
    x = B["XRP-USDT"]
    xr = round(sum(0.8 + 0.1 * (i % 2) for i in range(10)), 8)
    st = json.load(open(os.path.join(made["XRP-USDT"], "grid_state_XRP-USDT.json")))
    ok(f"① ♾️ 💠 100%: the counter stays ~0 ({x['profit']}$ — the old rate would be {round(x['profit'] / 10, 6)}$/day) · the new rate = "
       f"its trading {xr}$ (all 💠) ÷ 10 days = {x['rate_daily']}$/day",
       abs(x["rate_trade"] - xr) < 1e-6 and abs(x["rate_days"] - 10) < 0.01 and abs(x["rate_daily"] - xr / x["rate_days"]) < 1e-6
       and x["profit"] < 0.05 and x["rate_unit"] == "$", x)
    ok("① the profit counter itself untouched (= the engine's total_profit × the fee factor, as before)",
       abs(x["profit"] - round(float(st["total_profit"]) * x["net_f"], 4)) < 1e-9, (x["profit"], st.get("total_profit"), x.get("net_f")))

    # ── ② every card its own
    want = {"SOL-USDT": "grid_plus", "ADA-USDT": "grid_range", "SUI-USDT": "grid_step", "LINK-USDT": "dca_buy", "TRX-USDT": "rec_buy", "DOT-USDT": "rec_va"}
    bad = {}
    for sym, bt in want.items():
        b = B[sym]
        t = tot(sym) if bt != "dca_buy" else 3.2109
        if b["bot_type"] != bt or b["rate_unit"] != "$" or abs(b["rate_trade"] - t) > 1e-6 or abs(b["rate_daily"] - t / b["rate_days"]) > 1e-6:
            bad[sym] = (b["bot_type"], b["rate_trade"], t, b["rate_daily"], b["rate_unit"])
    ok("② ➕ 🎚️ 🪜 · 📈 DCA buy · 🟢 periodic buy · 💹 value path: each = its own trading (the books / its USDT profit) ÷ its days, in $", not bad, bad)
    d, xl = B["DOGE-USDT"], B["XLM-USDT"]
    ok(f"② 📉 DCA sell = its coin profit {d['rate_trade']} DOGE ÷ days · 🔴 periodic sell = {xl['rate_trade']} XLM ÷ days — in the coin",
       d["rate_unit"] == "DOGE" and abs(d["rate_trade"] - 12.3456) < 1e-9 and abs(d["rate_daily"] - 12.3456 / d["rate_days"]) < 1e-9
       and xl["rate_unit"] == "XLM" and abs(xl["rate_trade"] - 18.25) < 1e-9 and abs(xl["rate_daily"] - 18.25 / xl["rate_days"]) < 1e-9, (d, xl))
    ok("② every one of the 9 cards has a rate (none left empty by reinvest)", all(b.get("rate_daily") is not None for b in O["bots"]),
       {b["symbol"]: b.get("rate_daily") for b in O["bots"]})

    # ── ③ edges
    meta = json.load(open(os.path.join(R, "Holy_BotMeta.json")))
    k_sol = os.path.relpath(made["SOL-USDT"], R)
    meta[k_sol]["started"] = meta[k_sol]["first_seen"] = time.time() - 6 * 3600
    m.save_json_atomic(m.BOT_META, meta)
    if hasattr(m, "_META_CACHE"):
        m._META_CACHE.update(t=0.0, d={})
    m._BTA_CACHE.update(t=0.0, v=None)
    s1 = next(b for b in m.overview()["bots"] if b["symbol"] == "SOL-USDT")
    ok("③ a bot running for 6 hours ⇒ no rate yet («—» on the card: needs half a day)", s1.get("rate_daily") is None and s1["rate_days"] < 0.5, s1)
    calls = []
    real_tp = m.trade_period
    m.trade_period = lambda a, b: calls.append((a, b)) or real_tp(a, b)
    m._BTA_CACHE.update(t=0.0, v=None)
    for _ in range(3):
        m.overview()
    ok(f"③ the all-time trading is read once a minute: 3 refreshes ⇒ {sum(1 for c in calls if c[0] != c[1])} long ledger read(s)",
       sum(1 for c in calls if c[0] != c[1] and c[1] == time.strftime('%Y-%m-%d')) <= 2, calls)
    m.trade_period = lambda a, b: (_ for _ in ()).throw(RuntimeError("books broken"))
    m._BTA_CACHE.update(t=0.0, v=None)
    O2 = m._safe(m.overview, default=None)
    x2 = next(b for b in (O2 or {}).get("bots", []) if b["symbol"] == "XRP-USDT") if O2 else {}
    ok("③ the books unreadable ⇒ no crash · the card falls back to its own profit (as before)",
       O2 is not None and x2 and abs(x2["rate_trade"] - x2["profit"]) < 1e-9, x2)
    m.trade_period = real_tp
finally:
    os.chdir(cwd0)
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_rates: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
