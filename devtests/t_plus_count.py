# 📦 v3.36.49 — is the plus card's «📦 شراء N ≈ $X» real? the owner (14-11, card: plus SOL · 0.8% · gap 1% · 3$ · min 70 · price 72.37 ·
#   floor 80.03 · «📦 شراء 15 ≈ 46.22$»): «في الصور شراء 15 هل الحساب حقيقي احسه اكثر». The real plus engine in the trial sandbox with
#   the owner's settings, the price falling 85 ⇒ 72.37 and the dollars running out on the way (the dashboard's 💵 watch as _cw_pause /
#   _cw_restore do it: the floor ½ a level above the price, only up · restored when the dollars come back):
#   · once  — the dollars run out once ⇒ the card counts exactly the stored levels the price crossed (15 ≈ 46$ — the owner's card)
#   · twice — a few dollars come back (one level is bought) and run out again ⇒ a NEW, lower floor · the levels stored before stay
#     owed and are counted (some above the new floor — why «15» can look like more than the floor shows) · still exact
#   · both: no level is both stored and waiting in memory (nothing is bought twice when the dollars come back)
#   python3 devtests/t_plus_count.py [Holy_Dashboard.pyw] [-q]        (runs both; one: --variant=once|twice)
import importlib.machinery, importlib.util, json, math, os, shutil, subprocess, sys, tempfile, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
VAR = next((a[10:] for a in sys.argv[1:] if a.startswith("--variant=")), None)
if VAR is None:                                     # the runner: each variant in its own process (the sandbox swaps module globals)
    res = []
    def ok(name, cond, det=""):
        res.append(bool(cond))
        if not Q or not cond:
            print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)
    D = {}
    for v in ("once", "twice"):
        p = subprocess.run([sys.executable, os.path.abspath(__file__), DASH, f"--variant={v}"], capture_output=True, text=True, timeout=1500, cwd="/tmp")
        try:
            D[v] = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            D[v] = {"err": (p.stdout + p.stderr)[-800:]}
    a, b = D["once"], D["twice"]
    ok(f"once: the run ends and the dollars ran out on the way ({a.get('events')})", a.get("ended") and a.get("events"), a)
    ok(f"once: the card counts exactly the stored levels the price crossed — «📦 شراء {a.get('card_nb')} ≈ {a.get('card_ub')}$» (the owner's card: 15 ≈ 46.22$ at 0.04 SOL a level — since v3.36.51 each level is exactly 3$, so the dollars last one level longer: 14 × 3$)",
       a.get("card_nb") == len(a.get("crossed_levels") or [1]) and 13 <= a["card_nb"] <= 15 and abs(float(a.get("card_ub") or 0) - 3.0 * a["card_nb"]) < 0.5, a)
    ok("once: every one is a different level (one per rung · each 3$ at its own price — on the coin's step since v3.36.51, it was 0.04 SOL flat) and all under the floor", a.get("distinct") and a.get("usd_each") and all(2.94 <= x <= 3.06 for x in a["usd_each"]) and not a.get("above_floor"), a)
    ok(f"twice: dollars back for a moment (one level bought) then gone again ⇒ a new, lower floor {b.get('floor')} · the card still counts every owed level: {b.get('card_nb')}",
       b.get("ended") and b.get("card_nb") == len(b.get("crossed_levels") or [1]) and b.get("distinct") and len(b.get("events") or []) >= 4, b)
    ok(f"twice: … some of them sit above the new floor ({b.get('above_floor')}) — counted because they are still owed (why the count can look like more than the floor shows)",
       len(b.get("above_floor") or []) >= 1 and b.get("card_nb", 0) > b.get("levels_floor_to_price", 99), b)
    ok("both: no level is both stored and waiting in memory · no buy left in memory above the price (nothing is bought twice when the dollars come back)",
       not a.get("acc_and_virtual_same_level") and not b.get("acc_and_virtual_same_level") and not a.get("virtual_buys_above_price") and not b.get("virtual_buys_above_price"), (a, b))
    print(f"✅ t_plus_count: {sum(res)}/{len(res)}" if all(res) else f"❌ t_plus_count: {sum(res)}/{len(res)}")
    sys.exit(0 if all(res) else 1)
def _no_net(*a, **k): raise OSError("no network")
import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="cnt49_"); shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_cnt", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_cnt", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
SYM, P0, DT = "SOL-USDT", 85.0, 60.0
# 85 flat · down to 72.37 slowly (so every level is crossed one by one) · flat
px = [P0] * 150 + [P0 - (P0 - 72.37) * i / 900 for i in range(1, 901)] + [72.37 + 0.01 * math.sin(i / 5.0) for i in range(300)]
CFG = {"grid_percentage": 0.008, "usd_value": 3.0, "min_price": 70.0, "forced_base_price": P0, "knife_guard": False,
       "bot_type": "grid_plus", "lower_price": 0.0, "upper_price": 0.0, "buy_offset": 0.01}
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
EV = {"folder": None, "state": None, "log": [], "floors": [], "events": []}
_mk = m._bt_tmp.mkdtemp
m._bt_tmp.mkdtemp = lambda *a, **k: EV.__setitem__("folder", _mk(*a, **k)) or EV["folder"]
_rm = m.shutil.rmtree
def _keep(p, *a, **k):
    if EV["folder"] and os.path.abspath(p) == os.path.abspath(EV["folder"]):
        try: EV["state"] = json.load(open(os.path.join(p, f"grid_state_{SYM}.json"), encoding="utf-8"))
        except Exception: pass
        try: EV["log"] = json.load(open(os.path.join(p, "trade_history_SOL.json"), encoding="utf-8")) or []
        except Exception: pass
    return _rm(p, *a, **k)
m.shutil.rmtree = _keep
_Clock = m._BtClock
CW = {"on": False, "set": 0.0, "orig": 0.0, "back_done": False}
class Clock(_Clock):            # the dashboard's 💵 watch, as _cw_pause / _cw_restore do it: dollars < one order ⇒ floor ½ step above the price (only up)
    def __init__(self, ex, px_, t0, dt, on_point):
        def hook(i):
            on_point(i)
            sp = os.path.join(EV["folder"], f"grid_state_{SYM}.json")
            try: st = json.load(open(sp, encoding="utf-8"))
            except Exception: return
            free = ex.bal[ex.quote]
            ch = False
            if VAR == "twice" and not CW["back_done"] and CW["on"] and ex.p < 78.0:
                ex.bal[ex.quote] += 3.5; CW["back_done"] = True; EV["events"].append((i, round(ex.p, 4), "💵 +3.5$ back"))
                free = ex.bal[ex.quote]
            if free < 3.0 * 1.0:
                tgt = float(f"{ex.p * (1 + 0.008 / 2):.10g}")
                cur = float(st.get("buy_floor") or 0)
                if not CW["on"]:
                    CW.update(on=True, orig=cur, set=max(cur, tgt)); st["buy_floor"] = CW["set"]; st["pause_buy"] = False; ch = True
                    EV["events"].append((i, round(ex.p, 4), f"⏸ floor {CW['set']}"))
                elif tgt > cur * (1 + 0.008 / 4):
                    CW["set"] = tgt; st["buy_floor"] = tgt; ch = True; EV["events"].append((i, round(ex.p, 4), f"⬆ floor {tgt}"))
            elif CW["on"] and free >= 3.0:
                st["buy_floor"] = CW["orig"]; st["pause_buy"] = False; CW["on"] = False; ch = True
                EV["events"].append((i, round(ex.p, 4), "▶ restored"))
            if ch:
                json.dump(st, open(sp, "w", encoding="utf-8"))
        super().__init__(ex, px_, t0, dt, hook)
m._BtClock = Clock
# dollars: enough for about 6 levels (≈18$) ⇒ they run out on the way down
r = m._bt_run("grid_plus", CFG, SYM, px, DT, 18.5, 1.2, SPEC, samples=200)
st = EV["state"] or {}
cp = float(st.get("current_price") or px[-1])
fl = float(st.get("buy_floor") or 0)
acc = st.get("accum_buys") or {}
vb = st.get("virtual_buys") or {}
lb = st.get("limit_buys") or {}
b = {"symbol": SYM, "dir": "x", "cfg": dict(CFG)}
m.PX[SYM] = cp
sn = m._accx_snap(b, st)
crossed = sorted([float(v["target_price"]) for v in acc.values() if float(v["target_price"]) >= cp], reverse=True)
g = 0.008
levels_between = int(math.floor(math.log(fl / cp) / math.log(1 + g))) + 1 if fl > cp else 0
overlap = sorted(set(round(float(v["target_price"]), 4) for v in acc.values()) & set(round(float(v["target_price"]), 4) for v in vb.values()))
print(json.dumps({"variant": VAR, "ended": r["i_end"] >= r["n"] - 1, "distinct": len(set(round(x, 4) for x in crossed)) == len(crossed), "price": round(cp, 4), "floor": fl, "events": EV["events"][:12],
                  "card_nb": sn.get("nb"), "card_ub": sn.get("ub"), "kb_all_stored": sn.get("kb"),
                  "crossed_levels": [round(x, 4) for x in crossed], "above_floor": [round(x, 4) for x in crossed if x > fl * (1 + 1e-9)],
                  "levels_floor_to_price": levels_between, "virtual_buys_above_price": sorted([round(float(v['target_price']), 4) for v in vb.values() if float(v['target_price']) >= cp], reverse=True),
                  "live_buys": sorted([round(float(v['target_price']), 4) for v in lb.values()], reverse=True), "acc_and_virtual_same_level": overlap,
                  "qty": sorted(set(round(float(v['locked_qty']), 6) for v in acc.values())), "usd_each": sorted(round(float(v['locked_qty']) * float(v['target_price']), 3) for v in acc.values()),
                  "store_lines": [e["msg"][:90] for e in EV["log"] if "حُجز مستوى" in e["msg"]][:3]}, ensure_ascii=False))
shutil.rmtree(R, ignore_errors=True)
