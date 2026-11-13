# 🃏 a closed dashboard folder holding EVERY card kind (v3.36.33): ♾️ grid (💠 reinvest 100% — its profit counter stays ~0 while it trades) ·
#   ➕ plus · 🎚️ range · 🪜 step · 📉 DCA sell · 📈 DCA buy · 🟢 periodic buy · 🔴 periodic sell · 💹 value path · 🏦 accumulator — deployed with
#   the dashboard's own deploy functions (fake keys · nothing launched · no network), then given plausible state, ten days of run time and
#   ten days of trading in the books (normal n + 💠 r per day) so every number on every card is filled.
#   python3 devtests/seed_cards.py ROOT [Holy_Dashboard.pyw]   ⇒ ROOT ready for devtests/step/video/vid_dash.py ROOT PORT
import importlib.machinery, importlib.util, json, os, shutil, sys, time
from datetime import datetime, timedelta

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1])
DASH = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(H, "..", "Holy_Dashboard.pyw"))
KEYS = {"api": "KEYA-cards", "sec": "SECA-cards", "pass": "PASA-cards"}
DAYS = 10


def seed(root=ROOT, dash=DASH):
    os.makedirs(root, exist_ok=True)
    shutil.copy(dash, os.path.join(root, "Holy_Dashboard.pyw"))
    json.dump({"port": 8099}, open(os.path.join(root, "dashboard_config.json"), "w"))
    t0 = time.time() - DAYS * 86400
    json.dump({"wallets": [dict(name="main", **KEYS)],
               "accumulators": [{"id": "A1", "symbol": "XRP-USDT", "name": "XRP", "pct": 10, "coin_pct": 0, "enabled": True,
                                 "start": (datetime.now() - timedelta(days=DAYS)).strftime("%Y-%m-%d"), "wid": "main"}]},
              open(os.path.join(root, "monitor_config.json"), "w"))
    open(os.path.join(root, "demo.py"), "w").write("# placeholder — never launched\n")
    cwd0 = os.getcwd()
    os.chdir(root)
    ld = importlib.machinery.SourceFileLoader("hd_seed_cards", os.path.join(root, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_seed_cards", ld))
    a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.ROOT = root
    for k in ("LEDGER", "GONE", "ARCHIVE_META", "BOT_META", "RI_LEDGER", "COIN_LEDGER"):
        if hasattr(m, k):
            setattr(m, k, os.path.join(root, os.path.basename(getattr(m, k))))
    if hasattr(m, "_META_CACHE"):
        m._META_CACHE.update(t=0.0, d={})
    m.tg_send = lambda *a, **k: True
    m.stop_bot = lambda *a, **k: True
    m.launch = lambda bb: (True, "")
    m._okx_get = lambda *a, **k: None
    m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p
                            else {"code": "0", "data": [{"last": "1.0"}]})
    m.wallet_keys = lambda w: {"api_key": KEYS["api"], "secret_key": KEYS["sec"], "passphrase": KEYS["pass"]}
    PX = {"XRP-USDT": 2.4512, "SOL-USDT": 182.37, "ADA-USDT": 0.7421, "TRX-USDT": 0.2513, "DOGE-USDT": 0.1834, "LINK-USDT": 17.46,
          "XLM-USDT": 0.4127, "DOT-USDT": 5.214, "SUI-USDT": 3.618}
    m.PX.update(PX)
    G = {"symbol": None, "usd_value": "25", "wallet": "main"}
    BODIES = [
        ("deploy", dict(G, symbol="XRP-USDT", grid_pct="0.6", min_price="1.8", forced_base="2.45", reinvest=True, reinvest_pct="100")),
        ("deploy", dict(G, symbol="SOL-USDT", grid_pct="0.8", min_price="150", forced_base="182", g_type="grid_plus", buy_offset="1")),
        ("deploy", dict(G, symbol="ADA-USDT", grid_pct="0.5", min_price="0.6", forced_base="0.74", g_type="grid_range", lower_price="0.6", upper_price="0.9")),
        ("deploy_step", dict(G, symbol="SUI-USDT", step_parts="3", step_sell_pct="0.2", step_first_pct="0.3", grid_pct="0.6", min_price="3",
                             up_groups="0", forced_base="3.6")),
        ("deploy_dca", {"symbol": "DOGE-USDT", "dca_type": "dca", "base_order_qty": "100", "avg_order_qty": "100", "first_deviation": "1",
                        "step_multiplier": "1", "size_multiplier": "1", "max_safety_orders": "4", "take_profit_pct": "1", "exchange_orders": "3",
                        "cycle_wait_sec": "30", "wallet": "main"}),
        ("deploy_dca", {"symbol": "LINK-USDT", "dca_type": "dca_buy", "base_order_qty": "10", "avg_order_qty": "10", "first_deviation": "1",
                        "step_multiplier": "1", "size_multiplier": "1", "max_safety_orders": "4", "take_profit_pct": "1", "exchange_orders": "3",
                        "cycle_wait_sec": "30", "wallet": "main"}),
        ("deploy_rec", {"symbol": "TRX-USDT", "rec_type": "rec_buy", "amount": "10", "every": "1", "unit": "d", "mode": "lots", "tp_pct": "1",
                        "cap": "100", "wallet": "main"}),
        ("deploy_rec", {"symbol": "XLM-USDT", "rec_type": "rec_sell", "amount": "20", "every": "1", "unit": "d", "mode": "avg", "tp_pct": "1",
                        "cap": "300", "wallet": "main"}),
        ("deploy_va", {"symbol": "DOT-USDT", "step_usd": "10", "start_usd": "10", "every": "1", "unit": "d", "wallet": "main", "va_mode": "va",
                       "max_order": "50", "cap": "500"}),
    ]
    made = {}
    for fn, body in BODIES:
        before = set(m.bot_dirs())
        r = getattr(m, fn)(dict(body))
        new = sorted(set(m.bot_dirs()) - before)
        if not r.get("ok") or len(new) != 1:
            raise SystemExit(f"❌ seed: {fn} {body.get('symbol')}: {r.get('msg')} {new}")
        made[body["symbol"]] = new[0]
    bots = m.bot_dirs()
    led = {}
    meta = m.load_json(m.BOT_META) or {}
    for sym, d in made.items():
        b = bots[d]
        key = os.path.relpath(d, root)
        bt = (b.get("cfg") or {}).get("bot_type") or "grid"
        sp = m.paths_of(b)[0]
        st = m.load_json(sp) or {}
        cp = PX[sym]
        if bt in ("grid", "grid_plus", "grid_range", "grid_step"):
            g = 0.006
            st.update(current_price=cp, total_profit=(0.0123 if sym == "XRP-USDT" else 4.8765), ladder_base=cp,
                      limit_buys={str(i): {"target_price": round(cp * (1 - g * i), 6), "locked_qty": round(25 / cp, 4)} for i in range(1, 5)},
                      limit_sells={str(i): {"target_price": round(cp * (1 + g * i), 6), "locked_qty": round(25 / cp, 4)} for i in range(1, 5)})
        elif bt in ("dca", "dca_buy"):
            st.update(current_price=cp, avg_price=round(cp * 1.012, 6), target_price=round(cp * 1.022, 6), phase="selling",
                      filled=[{"n": 0, "px": round(cp * 1.02, 6), "qty": 550.0}, {"n": 1, "px": round(cp * 1.004, 6), "qty": 600.0}],
                      total_coin_profit=(12.3456 if bt == "dca" else 3.2109), total_usdt=210.5, total_sold_qty=1150.0)
        elif bt in ("rec_buy", "rec_sell"):
            st.update(px=cp, profit_total=(2.7182 if bt == "rec_buy" else 18.25), rel_total=2.1, cycles=7,
                      lots=[{"id": f"L{i}", "n": i, "ts": t0 + i * 86400, "q": round(10 / cp, 4), "c": 10.0, "ri": 0, "px": round(cp * (1 - 0.004 * i), 6)}
                            for i in range(1, 7)])
        else:                                            # 💹 value path
            st.update(px=cp, profit_total=1.9876, n_step=6, anchor=t0)
        m.save_json_atomic(sp, st)
        meta.setdefault(key, {})["started"] = t0
        meta[key]["first_seen"] = t0
        if bt not in ("dca",):                          # the books: ten days of trading — 💠 r on the reinvesting grid (its counter stays ~0)
            daily = {}
            for i in range(DAYS):
                day = (datetime.now() - timedelta(days=DAYS - 1 - i)).strftime("%Y-%m-%d")
                daily[day] = round(0.35 + 0.05 * (i % 3) + 0.0123 * len(led), 4) if sym != "XRP-USDT" else 0.0   # each bot its own amount
            led[key] = {"symbol": sym, "daily": daily, "total": round(sum(daily.values()), 4)}
    m.save_json_atomic(m.BOT_META, meta)
    m.save_json_atomic(m.LEDGER, led)
    # 💠 the reinvesting grid trades every day, all of it back into orders (r), nothing released (its card counter ~0)
    xk = os.path.relpath(made["XRP-USDT"], root)
    arc = {"bots": {xk: {"symbol": "XRP-USDT", "daily": {(datetime.now() - timedelta(days=DAYS - 1 - i)).strftime("%Y-%m-%d"):
                                                          {"n": 0.0, "r": round(0.8 + 0.1 * (i % 2), 4), "k": 3} for i in range(DAYS)}}}}
    m.save_json_atomic(m.RI_LEDGER, arc)
    os.chdir(cwd0)
    return made


if __name__ == "__main__":
    made = seed()
    print("seeded:", " · ".join(f"{s}={os.path.basename(d)}" for s, d in made.items()))
