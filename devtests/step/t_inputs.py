# 🪜 🔢 F7 — numbers that are not finite («nan» · «inf» · «1e999») in any field of the graded-grid form, or in a config
#   written by hand: NaN compares false both ways, so it used to pass every «> 0» check (the table showed no refusal, deploy
#   wrote NaN into the config, the engine failed on every order — inf: sell prices at infinity, bought coins never sold).
#   Now: the table and deploy refuse them (nothing written) · the engine treats them as invalid settings (no slot, no order).
#   python3 devtests/step/t_inputs.py [Holy_Dashboard.pyw] [-q]        (STEP_ENGINE=… tests another engine copy)
import ast, json, math, os, shutil, sys, tempfile, importlib.machinery, importlib.util
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okxsim
from okxsim import Clock, Ex, Bot, walk

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:700]}"), flush=True)


def funcs(path, names, ns):
    for n in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            exec(compile(ast.Module([n], []), path, "exec"), ns)
    return ns


ENG = funcs(okxsim.ENGINE, {"_dec", "_step_round", "_sig", "step_layout"},
            {"math": math, "Decimal": Decimal, "ROUND_FLOOR": ROUND_FLOOR, "ROUND_CEILING": ROUND_CEILING, "ROUND_HALF_UP": ROUND_HALF_UP})
DSH = funcs(DASH, {"_step_round", "_step_layout"}, {"math": math})
BAD = [float("nan"), float("inf"), float("-inf")]

# ── the layout (engine and the dashboard's copy): any non-finite setting ⇒ no slot
base = dict(P0=1.0, G=0.03, d=0.01, Q=15.0, floor=0.7, fee=0.0008, d1=0.012)
miss = []
for k in base:
    for v in BAD:
        a = dict(base, **{k: v})
        for nm, fn in (("engine", ENG["step_layout"]), ("dashboard", DSH["_step_layout"])):
            try:
                out = fn(a["P0"], a["G"], a["d"], 3, a["Q"], a["floor"], 1, a["fee"], None, None, d1=a["d1"])
            except Exception as e:
                out = f"{type(e).__name__}"
            if out != []:
                miss.append((nm, k, v, out if isinstance(out, str) else len(out)))
ok("the layout (engine + the table's copy): nan / inf / −inf in the start · buy · sell · first-sell distance · amount · floor · fee "
   "⇒ no slot at all (no exception)", not miss and ENG["step_layout"](1.0, 0.03, 0.01, 3, 15, 0.7, 1, 0.0008), miss[:3])

# ── the dashboard: the table and deploy (as in bt3615_test: a closed folder · fake keys · no network)
R = tempfile.mkdtemp(prefix="t_inputs_")
json.dump({"port": 8096}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-tin", "sec": "SECA-tin", "pass": "PASA-tin"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd(); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_inputs", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_inputs", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
os.chdir(cwd0)
m._okx_pub = lambda p: {"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None
m.PX.update({"XRP-USDT": 1.0})
m.tg_send = lambda *a, **k: True
body0 = {"symbol": "XRP-USDT", "usd_value": "15", "step_parts": "3", "step_sell_pct": "1", "step_first_pct": "1.2", "grid_pct": "3",
         "min_price": "0.7", "up_groups": "1", "forced_base": "1"}
P0k = m.step_plan(body0)
ok("the table with sane numbers is accepted (the control)", P0k.get("ok") and not P0k["err"], P0k.get("err") or P0k.get("msg"))
spec = {"tickSz": 0.0001, "lotSz": 0.000001, "minSz": 0.1}
keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
        if hasattr(m, k)}
bad_plan, bad_dep, n = [], [], 0
for k in ("usd_value", "step_parts", "step_sell_pct", "step_first_pct", "grid_pct", "min_price", "up_groups", "forced_base"):
    for v in ("nan", "NaN", " nan ", "inf", "-inf", "Infinity", "1e999", "-1e999"):
        n += 1
        b = dict(body0, **{k: v})
        try:
            P = m.step_plan(b)
        except Exception as e:
            P = {"ok": "crash", "msg": f"{type(e).__name__}: {e}"}
        if P.get("ok") is not False:
            bad_plan.append((k, v, P.get("ok"), (P.get("err") or [P.get("msg")])[:1]))
        cfg, err = m._bt_dry_cfg("grid_step", b, "XRP-USDT", spec, 1.0)
        for kk, vv in keep.items():
            setattr(m, kk, vv)
        if cfg:
            bad_dep.append((k, v, {x: cfg.get(x) for x in ("usd_value", "step_sell", "step_first", "grid_percentage", "min_price")}))
ok(f"the table: {n} non-finite entries (8 fields × nan · NaN · « nan » · inf · −inf · Infinity · 1e999 · −1e999) ⇒ each refused, never a crash",
   not bad_plan, bad_plan[:3])
ok(f"deploy: the same {n} entries ⇒ refused · no config written", not bad_dep, bad_dep[:3])
shutil.rmtree(R, ignore_errors=True)

# ── the engine with a config written by hand
bad_eng = []
for kv in ({"step_sell": float("nan")}, {"step_sell": float("inf")}, {"step_first": float("inf")}, {"step_first": float("nan")},
           {"grid_percentage": float("nan")}, {"usd_value": float("inf")}, {"min_price": float("nan")}, {"forced_base_price": float("inf")}):
    c = Clock(); ex = Ex(c, base=100, quote=1000)
    b = Bot(ex, kv)
    b.audit_on = False
    try:
        b.run(walk([1.0, 0.97, 1.02], 60))
        crash = None
    except BaseException as e:
        crash = f"{type(e).__name__}: {e}"
    S = (b.st or {}).get("slots") or {}
    if crash or S or ex.orders or not any("الإعداد غير صالح" in x for x in b.hist()):
        bad_eng.append((kv, crash, len(S), len(ex.orders), b.hist()[:2]))
ok("the engine, config written by hand with nan / inf (sell · first sell · buy distance · amount · floor · start) ⇒ no slot · no order · "
   "the «invalid settings» line", not bad_eng, bad_eng[:2])

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
