# 🪜⬆️ up to 500 levels above the price (v3.36.30) — the owner (10-11): «المشكلة البوت حده 200 اذا انزيده نگدر اريد مثلا 500».
#   A closed folder · fake keys · no network · XRP's real OKX rules (tick 0.0001 · lot 0.000001 · min 1 XRP) · start 1.10 · floor 0.90:
#   ① the plan: 500 levels accepted when every sell stays ≥ OKX's 1 XRP at the top price (75$/0.6% ⇒ up to 21.9 · 16$/0.3% ⇒ up to 4.94)
#      · with the owner's 25$ / 12.5$ the sells above 8.33$ / 4.17$ a coin are under 1 XRP ⇒ refused with the count (as on OKX) · 501 refused
#      with the range · more than 3,000 slots refused with the number · 12.5$/0.3% with 414 levels sells up to ≥ 3.8 (the owner's example)
#   ② a real deploy (launch stubbed) with 414 levels: accepted, its config carries 414
#   ③ the REAL engine in the box, 12.5$/0.3% · 414 levels, the price walks 1.10 → 3.85 then rests: every planned sell above fills
#      (1,242) · exactly the planned coins sold · its highest sell = the plan's · no order refused · the dollars it took = the plan's
#   python3 devtests/step/t_up500.py [Holy_Dashboard.pyw] [-q]
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_up500_")
json.dump({"port": 8107}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-up500", "sec": "SECA-up500", "pass": "PASA-up500"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_up500", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_up500", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
SPEC = {"tickSz": 0.0001, "lotSz": 1e-06, "minSz": 1.0}
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "1"}]} if "instruments" in p else None)
m._okx_get = lambda *a, **k: {"code": "0", "data": [{"details": [{"ccy": "XRP", "availBal": "100000"}]}]}
m._acc_spec = lambda s: SPEC
m.tg_send = lambda *a, **k: True
P0 = 1.10
m.PX["XRP-USDT"] = P0
m._acc_price = lambda s: P0
BASE = {"symbol": "XRP-USDT", "step_parts": "3", "step_first_pct": "0.3", "step_sell_pct": "0.2", "min_price": "0.90", "forced_base": "", "wallet": "main",
        "auto": False}
A = dict(BASE, usd_value="25", grid_pct="0.6")
B = dict(BASE, usd_value="12.5", grid_pct="0.3")


def plan(body, up, **kw):
    return m.step_plan(dict(body, up_groups=str(up), **kw), px=P0)


def top(pl):
    return max((s["sp"] for r in pl.get("rows") or [] if r["side"] == "inv" for s in r["sells"]), default=0)


try:
    # ── ① the plan
    pa, pb, pb414 = plan(dict(A, usd_value="75"), 500), plan(dict(B, usd_value="16"), 500), plan(B, 414)
    oa, ob = plan(A, 500), plan(B, 500)
    p501 = plan(B, 501)
    pbig = plan(dict(B, usd_value="50", step_parts="20"), 200)
    T = lambda p: p.get("tot") or {}
    ok(f"① 500 levels accepted: 75$/0.6% sells up to {top(pa):.2f} with {T(pa).get('coins', 0):.0f} XRP ({T(pa).get('orders')} orders) · 16$/0.3% up to "
       f"{top(pb):.2f} with {T(pb).get('coins', 0):.0f} XRP ({T(pb).get('orders')} orders) · 414 levels of 0.3% (12.5$) reach {top(pb414):.3f} (≥ 3.8)",
       pa.get("ok") and not pa["err"] and pb.get("ok") and not pb["err"] and pb414.get("ok") and not pb414["err"] and top(pb414) >= 3.8
       and T(pa).get("ni") == 500 and T(pb).get("ni") == 500 and T(pb414).get("ni") == 414, (pa.get("err") or pa.get("msg"), pb.get("err") or pb.get("msg"), pb414.get("err")))
    ok(f"… the owner's 25$ / 12.5$ with 500 levels: the sells above 8.33$ / 4.17$ a coin are under OKX's 1 XRP ⇒ refused with the count: "
       f"«{(oa.get('err') or [''])[0]}» · «{(ob.get('err') or [''])[0]}»",
       oa.get("ok") and ob.get("ok") and any("أصغر من حد المنصة" in e for e in oa.get("err") or []) and any("أصغر من حد المنصة" in e for e in ob.get("err") or []),
       (oa.get("err") or oa.get("msg"), ob.get("err") or ob.get("msg")))
    ok(f"… 501 refused: «{p501.get('msg')}» · 20 sells × 200 levels + the buys ({len(m._step_layout(P0, 0.003, 0.002, 20, 50, 0.9, 200, 0.0008, d1=0.003))} "
       f"slots) refused: «{(pbig.get('err') or [''])[0]}»",
       not p501.get("ok") and "500" in str(p501.get("msg")) and pbig.get("ok") and (pbig.get("err") or [""])[0].find("3000") >= 0, (p501, pbig.get("err")))

    # ── ② a real deploy with 414 levels
    launched = []
    m.launch = lambda b: (launched.append(b) or True, "ok")
    m.bot_dirs = lambda: {}
    dep = m.deploy_step(dict(B, up_groups="414"))
    cfgs = [os.path.join(R, d, "config_XRP-USDT.json") for d in os.listdir(R) if os.path.isdir(os.path.join(R, d)) and d.startswith("step_")]
    cf = json.load(open(cfgs[0])) if cfgs else {}
    ok(f"② a real deploy (launch stubbed) with 414 levels: «{dep.get('msg')}» · config up_groups {cf.get('up_groups')} · launched {len(launched)}",
       dep.get("ok") and cf.get("up_groups") == 414 and len(launched) == 1, (dep, cf.get("up_groups")))

    # ── ③ the real engine in the box: 1.10 → 3.85
    KEEP = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
    body = dict(B, up_groups="414")
    cfg, err = m._bt_dry_cfg("grid_step", body, "XRP-USDT", SPEC, P0)
    for k, v in KEEP.items():
        setattr(m, k, v)
    pl = pb414
    if not pl.get("ok"):
        raise RuntimeError(f"the plan with 414 levels is refused: {pl.get('msg')}")
    sells_plan = [s for r in pl["rows"] if r["side"] == "inv" for s in r["sells"] if not s["skip"]]
    q0, b0 = m._bt_wallet_def("grid_step", None, body, P0, SPEC)
    n_up = 1500
    px = [P0 * (3.85 / P0) ** (i / n_up) for i in range(n_up + 1)] + [3.85] * 60
    t0 = time.time()
    r = m._bt_run("grid_step", cfg, "XRP-USDT", px, 60, q0, b0, SPEC)
    secs = time.time() - t0
    ex = r["ex"]
    sold = [f for f in ex.fills if f[1] == "sell"]
    coins_sold = sum(f[3] for f in sold)
    usd_in = sum(f[3] * f[2] for f in sold)
    plan_coins = sum(s["qn"] for s in sells_plan)
    plan_usd = sum(s["qn"] * s["sp"] for s in sells_plan)
    hi = max((f[2] for f in sold), default=0)
    ok(f"③ the REAL engine, 12.5$/0.3% · 414 levels, 1.10 → 3.85: {len(sold)} sells of {len(sells_plan)} planned · {coins_sold:.4f} XRP sold "
       f"(plan {plan_coins:.4f}) for {usd_in:.2f}$ (plan {plan_usd:.2f}$ · each price on OKX's tick) · highest sell {hi:.4f} (plan {max(s['sp'] for s in sells_plan):.6f}) · "
       f"{len(ex.rejects)} refused · {r['why']} · {secs:.0f} s",
       len(sold) == len(sells_plan) == 1242 and abs(coins_sold - plan_coins) <= 1e-6 * len(sold) + 1e-6 and abs(usd_in - plan_usd) <= 0.01 * len(sold)
       and abs(hi - max(s["sp"] for s in sells_plan)) <= SPEC["tickSz"] and not ex.rejects and r["why"] == "end",       # (the engine puts a price on OKX's tick)
       (len(sold), len(sells_plan), coins_sold, plan_coins, usd_in, plan_usd, hi, ex.rejects[:3], r["why"]))
except Exception as ex_:
    import traceback
    traceback.print_exc()
    ok("the test ran to its end", False, repr(ex_))
finally:
    os.chdir("/")
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_up500: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
