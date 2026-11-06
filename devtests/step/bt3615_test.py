# v3.36.15 — 🧪 the trial path knows 🪜 the graded grid: the embedded engine (main_step.py, unchanged) in the closed box (fake clock · fake
#   OKX · no network) · the settings = what deploy_step writes · the suggested wallet = the plan's totals · the result splits into buy/sell
#   profit (= the engine's own net book) + the open position · dollars on the box = the engine's slots to the millime · 3 coins (XRP · SOL · PEPE rules)
#   python3 p3375/bt3615_test.py <v3.36.15 dashboard.pyw> [-q]
import os, sys, json, shutil, tempfile, importlib.machinery, importlib.util
DASH = os.path.abspath(sys.argv[1]); Q = "-q" in sys.argv
R = tempfile.mkdtemp(prefix="bt3615_")
res = []


def ok(n, c, x=""):
    res.append(bool(c))
    if not Q or not c:
        print(("✅ " if c else "❌ ") + n + (" — " + str(x)[:400] if x != "" and not c else ""), flush=True)


json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-bt3615", "sec": "SECA-bt3615", "pass": "PASA-bt3615"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
SPEC = {"XRP-USDT": ("0.0001", "0.000001", "0.1"), "SOL-USDT": ("0.01", "0.000001", "0.001"), "PEPE-USDT": ("0.0000000001", "1", "100000")}
m._okx_pub = lambda p: ({"code": "0", "data": [dict(zip(("tickSz", "lotSz", "minSz"), SPEC[p.split("instId=")[1]]))]} if "instruments" in p and p.split("instId=")[1] in SPEC else None)
m.PX.update({"XRP-USDT": 1.32, "SOL-USDT": 140.0, "PEPE-USDT": 0.00001234})
m.tg_send = lambda *a, **k: True
ok("🪜 grid_step is a trial-path kind (all 9 kinds except the accumulator)", "grid_step" in m._BT_KINDS and len(m._BT_KINDS) == 9, m._BT_KINDS)
for sym, Qv, N, d, G, fl, up in (("XRP-USDT", 15, 3, 1.0, 3.0, 1.0, 2), ("SOL-USDT", 30, 4, 0.8, 2.5, 110, 1), ("PEPE-USDT", 12, 3, 1.2, 4.0, 0.000008, 2)):
    p0 = m.PX[sym]
    body = {"symbol": sym, "usd_value": str(Qv), "step_parts": str(N), "step_sell_pct": str(d), "grid_pct": str(G), "min_price": str(fl), "up_groups": str(up)}
    P = m.bt_prep({"kind": "grid_step", "body": body})
    plan = m.step_plan(dict(body, forced_base=p0))
    ok(f"{sym}: bt_prep ok · kind grid_step · the suggested wallet covers the plan (dollars to the floor · coins above)",
       P.get("ok") and P["kind"] == "grid_step" and P["quote_def"] >= plan["tot"]["usd"] and P["base_def"] >= plan["tot"]["coins"] - 1e-9, (P, plan.get("tot")))
    spec = P["spec"]
    _keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
             if hasattr(m, k)}
    cfg, err = m._bt_dry_cfg("grid_step", body, sym, spec, p0)     # (made for the separate trial process: it swaps module globals — put back here)
    for k, v in _keep.items():
        setattr(m, k, v)
    ok(f"{sym}: the box settings = deploy_step's own config (grid_step · start price fixed = the price · no keys)",
       cfg and cfg.get("bot_type") == "grid_step" and abs(cfg.get("forced_base_price") - p0) < 1e-12 and cfg.get("step_parts") == N
       and abs(cfg.get("step_sell") - d / 100) < 1e-12 and not any(k in cfg for k in ("api_key", "secret_key", "passphrase")), (cfg, err))
    if not cfg:
        continue
    days, dt = m._BT_PER["7d"] if "7d" in m._BT_PER else list(m._BT_PER.values())[0]
    px = m._bt_path(p0, days, dt, 0.05, 11)
    r = m._bt_run("grid_step", cfg, sym, px, dt, float(P["quote_def"]), float(P["base_def"]), spec)
    st = r["state"] or {}
    S = st.get("slots") or {}
    ex = r["ex"]
    sells = sum(1 for f in ex.fills if f[1] == "sell"); buys = sum(1 for f in ex.fills if f[1] == "buy")
    ok(f"{sym}: the real engine ran the whole path in the box ({r['why']}) · {len(S)} slots · {buys} buys / {sells} sells · no refusal",
       r["i_end"] == r["n"] and len(S) == plan["tot"]["orders"] and sells > 3 and not ex.rejects, (r["why"], r["i_end"], r["n"], len(S), ex.rejects[:3]))
    inv_sold = sum(float(s["q"]) * float(s["bp"]) for s in S.values() if s["j"] >= 0 and int(s.get("n") or 0) >= 1)
    held_spent = sum(float(s.get("spent") or 0) for s in S.values() if s["side"] == "sell" and float(s.get("cost") or 0) > 0)
    part_buy = sum(float(s.get("accv") or 0) for s in S.values() if s["side"] == "buy")
    part_sell = sum(float(s.get("accv") or 0) - float(s.get("accf") or 0) for s in S.values() if s["side"] == "sell")
    inflight = 0.0
    for s in S.values():
        o = s.get("o") or {}
        eo = ex.orders.get(str(o.get("id") or "")) if o.get("id") else None
        if eo and eo["acc"] > 0:
            inflight += (-eo["acc"] * eo["avg"]) if eo["side"] == "buy" else (eo["acc"] * eo["avg"] - abs(eo.get("fee", 0)))
    books = float(P["quote_def"]) + float(st.get("total_profit") or 0) + inv_sold - held_spent - part_buy + part_sell + inflight
    if any("dq" in s for s in S.values()):          # v3.36.17 (F2): every cost dollar is held (a selling slot's spent · any slot's
        fee = float(plan["fee"])                    # leftover dc) or was used by a sale ⇒ start + profit + the wallet's «as if
        V0 = sum(round(x["qn"] * r_["bp"] / (1.0 - fee), 10) for r_ in plan["rows"] if r_["j"] >= 0 for x in r_["sells"] if not x["skip"])
        held = sum(float(s.get("spent") or 0) for s in S.values() if s["side"] == "sell") + sum(float(s.get("dc") or 0) for s in S.values())
        books = float(P["quote_def"]) + float(st.get("total_profit") or 0) + V0 - held - part_buy + part_sell + inflight   # bought» − held
    ok(f"{sym}: dollars on the box = the engine's slots to the millime (start + profit + wallet parts sold − coins held at cost)",
       abs(books - ex.bal[ex.quote]) < 1e-4, (round(books, 8), round(ex.bal[ex.quote], 8)))
    s_ = m._bt_summary("grid_step", r, float(P["quote_def"]), float(P["base_def"]), p0, dt)
    ok(f"{sym}: the card: buy/sell profit = the engine's own net book · open = the rest (starts = ends at the start price) · no 💠 coins",
       abs(s_["trade"] - float(st.get("total_profit") or 0)) < 1e-6 and abs(s_["trade"] + s_["open_usd"] - s_["result"]) < 1e-6
       and s_["od"]["k"] == "grid" and s_["ri_coin"] is None and s_["trade"] > 0, {k: s_[k] for k in ("trade", "open_usd", "result", "realized", "od")})
    det = m._bt_detail(r, dt, s_)
    ok(f"{sym}: the replay ends on the card's number (last sample profit = buy/sell profit)", abs(det["c"][-1][4] - s_["trade"]) < 1e-6, (det["c"][-1], s_["trade"]))
print(f"✅ bt3615_test: {sum(res)}/{len(res)}" if all(res) else f"❌ bt3615_test: {sum(res)}/{len(res)}", flush=True)
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
