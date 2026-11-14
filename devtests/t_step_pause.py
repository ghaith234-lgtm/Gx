# 🪜 ⏸ the graded-grid bot's pause-buy and pause-sell — the same pattern as the grid (v3.36.45 · p74) — the owner (14-11): «بوت المتدرج افحص
#   ايقاف الشراء وايقاف البيع شوفه نفس نمط الشبكي يعني من المكان المحدد وكذلك سوي فحص عليه اذا بدون استثمار او استثمار».
#   The real 🪜 engine in the trial sandbox (closed folder · fake clock · fake OKX · no network), the card's own buttons pressed through
#   the dashboard's control() (as the card does) — without reinvest and with 💠 100%:
#   · ⏸ buy at the market (the drop) ⇒ the floor = the price at the press · no buy under it while paused · the card counts every level
#     the price crosses («▶️ استئناف الشراء (N)» · «📦 شراء N ≈ $X») · one «📦» notification per level, never twice
#   · ▶️ ⇒ exactly those N levels are bought at once at the market (each cheaper than its level) · their sells at their own places ·
#     the counter back to 0
#   · ⏸ sell at the market (the pump) ⇒ the same upside down (sold dearer than their levels)
#   · ⏸ from a typed price (under the market) ⇒ buys go on down to it, none under it — «من المكان المحدد»
#   · 💠: after the profitable sells the levels bought again carry their growth (quantity above the base) and the counter counts it
#   python3 devtests/t_step_pause.py [Holy_Dashboard.pyw] [-q] [--ri]
import importlib.machinery, importlib.util, json, os, shutil, sys, tempfile, urllib.request, collections

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
RI = "--ri" in sys.argv
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
R = tempfile.mkdtemp(prefix="t_steppause_")
json.dump({"port": 8099}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-x", "sec": "SECA-x", "pass": "PASA-x"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_steppause", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_steppause", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.01", "lotSz": "0.000001", "minSz": "0.001"}]} if "instruments" in p else None)
SYM, P0, DT = "SOL-USDT", 80.0, 60.0
m.PX[SYM] = P0
m.tg_send = lambda *a, **k: True
body = {"symbol": SYM, "usd_value": "30", "step_parts": "3", "step_sell_pct": "0.8", "grid_pct": "1.5", "min_price": "50", "up_groups": "2"}
if RI:
    body.update(reinvest=True, reinvest_pct="100")
P = m.bt_prep({"kind": "grid_step", "body": body})
_keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs") if hasattr(m, k)}
cfg, err = m._bt_dry_cfg("grid_step", body, SYM, P["spec"], P0)
for k, v in _keep.items():
    setattr(m, k, v)
ok(f"the box settings = deploy_step's own config{' with 💠 100%' if RI else ''}", cfg and cfg.get("bot_type") == "grid_step" and bool(cfg.get("reinvest")) == RI, err)
# flat · drop 80 ⇒ 70 (⏸ buy at the market 300 · ▶️ 900) · flat · pump 70 ⇒ 84 (⏸ sell at the market 1350 · ▶️ 1900) · flat ·
# drop 84 ⇒ 73 (⏸ buy from a typed price 2% under the market 2200 · ▶️ 2700) · flat
px = ([P0] * 200 + [P0 - 10.0 * i / 600 for i in range(1, 601)] + [70.0] * 300 + [70.0 + 14.0 * i / 700 for i in range(1, 701)] + [84.0] * 300
      + [84.0 - 11.0 * i / 500 for i in range(1, 501)] + [73.0] * 300)
I_PB, I_RB, I_PS, I_RS, I_PT, I_RT = 300, 900, 1350, 1900, 2200, 2700
EV = {"folder": None, "snap": {}, "lim": {}, "msg": [], "ctl": {}}
_mk = m._bt_tmp.mkdtemp
m._bt_tmp.mkdtemp = lambda *a, **k: EV.__setitem__("folder", _mk(*a, **k)) or EV["folder"]
_Clock = m._BtClock


def press(f, action, value=None):
    """the card's button: the dashboard's own control() on this folder"""
    m.ROOT = os.path.dirname(f)
    cp = os.path.join(f, f"config_{SYM}.json")
    if not os.path.exists(cp):
        json.dump(dict(cfg, symbol=SYM), open(cp, "w"))
    m.bot_dirs = lambda: {os.path.realpath(f): {"dir": f, "symbol": SYM, "cfg": dict(cfg, symbol=SYM), "cfg_path": cp}}
    return m.control(os.path.basename(f), action, value)


class Clock(_Clock):
    def __init__(self, ex, px_, t0, dt, on_point):
        def hook(i):
            on_point(i)
            if i not in (I_PB, I_RB, I_PS, I_RS, I_PT, I_RT) and i % 10:
                return
            f = EV["folder"]
            sp = os.path.join(f, f"grid_state_{SYM}.json")
            try:
                st = json.load(open(sp, encoding="utf-8"))
            except Exception:
                return
            m.PX[SYM] = ex.p
            b = {"dir": f, "symbol": SYM, "cfg": dict(cfg, symbol=SYM)}
            EV["snap"][i] = {"p": ex.p, "floor": float(st.get("buy_floor") or 0), "ceil": float(st.get("sell_ceiling") or 0),
                             "ax": m._accx_snap(b, st), "lbl": None}
            m.ROOT = os.path.dirname(f)
            for t, fd in (m._safe(m._accx_tick, b, st, ex.p, default=[]) or []):
                EV["msg"].append((i, fd))
            if i == I_PB:
                EV["ctl"]["pb"] = press(f, "pause_buy"); EV["lim"]["fb"] = ex.p
            elif i in (I_RB, I_RT):
                EV["ctl"]["rb" if i == I_RB else "rt"] = press(f, "accum_buy", 0)
            elif i == I_PS:
                EV["ctl"]["ps"] = press(f, "pause_sell"); EV["lim"]["cs"] = ex.p
            elif i == I_RS:
                EV["ctl"]["rs"] = press(f, "accum_sell", 0)
            elif i == I_PT:
                EV["lim"]["ft"] = round(ex.p * 0.98, 2)
                EV["ctl"]["pt"] = press(f, "accum_buy", EV["lim"]["ft"])
                EV["lim"]["pt_p"] = ex.p
        super().__init__(ex, px_, t0, dt, hook)


m._BtClock = Clock
r = m._bt_run("grid_step", cfg, SYM, px, DT, float(P["quote_def"]), float(P["base_def"]), P["spec"], samples=400)
m._BtClock = _Clock
ex, SN, L = r["ex"], EV["snap"], EV["lim"]
T = lambda t: round((t - m._BT_T0) / DT)
F = [(T(f[0]), f[1], f[2], f[3]) for f in ex.fills]
at = lambda i: SN[max(x for x in SN if x <= i)]
ok(f"the run reached its end ({r['i_end']}/{r['n']}) · {len(F)} fills · OKX refused nothing · the buttons answered ok",
   r["i_end"] >= r["n"] - 1 and not ex.rejects and all(v.get("ok") for v in EV["ctl"].values()), (r["why"], ex.rejects[:3], EV["ctl"]))
# ⏸ buy at the market
fb = at(I_PB + 10)["floor"]
ok(f"⏸ buy (the card's button) ⇒ the floor is the market at the press ({fb} = {L['fb']:.4f})", abs(fb - L["fb"]) < 1e-6, (fb, L["fb"]))
pb = [f for f in F if I_PB < f[0] < I_RB and f[1] == "buy"]
ok("… no buy under it while paused (the price fell 78.3 ⇒ 70)", not [f for f in pb if f[2] < fb - 1e-9], pb[:4])
nb = at(I_RB - 10)["ax"]["nb"]
grow = [at(i)["ax"]["nb"] for i in range(I_PB + 10, I_RB, 50)]
ok(f"… the card counts every level the price crosses (▶️ استئناف الشراء ({nb}) · 📦 شراء {nb} ≈ ${at(I_RB - 10)['ax']['ub']}) — it was always 0 on a 🪜 card",
   nb >= 10 and grow == sorted(grow) and grow[0] < nb, grow)
mb = [x for x in EV["msg"] if I_PB <= x[0] < I_RB]
ok(f"… «📦» notifications as it crosses ({len(mb)}), none repeated", mb and len({x[1] for x in mb}) == len(mb), [x[1][:70] for x in mb[:3]])
rb = [f for f in F if I_RB <= f[0] <= I_RB + 10 and f[1] == "buy"]
pr = at(I_RB)["p"]
ok(f"▶️ ⇒ exactly the {nb} crossed levels bought at once at the market ({len(rb)} buys at ≤ {pr * 1.002:.2f} — each cheaper than its level)",
   len(rb) == nb and all(f[2] <= pr * 1.002 + 1e-9 for f in rb), [(f[0], f[2]) for f in rb[:5]])
ok("… and the counter back to 0 (no floor)", at(I_RB + 10)["ax"]["nb"] == 0 and at(I_RB + 10)["floor"] == 0, at(I_RB + 10))
# ⏸ sell at the market
cs = at(I_PS + 10)["ceil"]
ok(f"⏸ sell ⇒ the ceiling is the market at the press ({cs} = {L['cs']:.4f})", abs(cs - L["cs"]) < 1e-6, (cs, L["cs"]))
ps = [f for f in F if I_PS < f[0] < I_RS and f[1] == "sell"]
ok("… no sell over it while paused (the price climbed 75 ⇒ 84)", not [f for f in ps if f[2] > cs + 1e-9], ps[:4])
ns = at(I_RS - 10)["ax"]["ns"]
rs = [f for f in F if I_RS <= f[0] <= I_RS + 10 and f[1] == "sell"]
pr = at(I_RS)["p"]
ok(f"… counted ({ns}) · ▶️ ⇒ exactly those sold at once at the market ({len(rs)} at ≥ {pr * 0.998:.2f} — each dearer than its level) · counter 0",
   ns >= 10 and len(rs) == ns and all(f[2] >= pr * 0.998 - 1e-9 for f in rs) and at(I_RS + 10)["ax"]["ns"] == 0, (ns, len(rs), [f[2] for f in rs[:4]]))
# ⏸ from a typed price
ft = at(I_PT + 10)["floor"]
pt = [f for f in F if I_PT < f[0] < I_RT and f[1] == "buy"]
ok(f"⏸ from a typed price {L['ft']} (2% under the market {L['pt_p']:.2f}) ⇒ the floor is that price · buys go on down to it ({len([f for f in pt if f[2] >= ft])}) · none under it",
   abs(ft - L["ft"]) < 1e-9 and any(f[2] >= ft for f in pt) and not [f for f in pt if f[2] < ft - 1e-9], (ft, pt[:6]))
nt = at(I_RT - 10)["ax"]["nb"]
rt = [f for f in F if I_RT <= f[0] <= I_RT + 10 and f[1] == "buy"]
ok(f"… ▶️ ⇒ the {nt} crossed under it bought at once at the market", nt > 0 and len(rt) == nt, (nt, len(rt)))
st = r["state"] or {}
S = st.get("slots") or {}
if RI:
    rb_ = st.get("reinvest") or {}
    big = [s for s in S.values() if float(s.get("g") or 0) > 1e-12]
    q_rt = sorted(f[3] for f in rt)
    ok(f"💠 the profitable sells grew their levels ({len(big)} levels with growth · {float(rb_.get('credited') or 0):.4f}$ reinvested) and the "
       f"levels bought at ▶️ carry it (the counter counted it: {at(I_RT - 10)['ax'].get('cb')} coins)",
       big and float(rb_.get("credited") or 0) > 0 and any(f[3] > min(float(s["q"]) for s in S.values()) * 1.0001 for f in rt), (len(big), rb_.get("credited"), q_rt[:4]))
else:
    ok("without reinvest: no level grows (every quantity stays its base)", not [s for s in S.values() if float(s.get("g") or 0) > 1e-12])
_nm = "t_step_pause" + (" --ri" if RI else "")
print(f"✅ {_nm}: {sum(res)}/{len(res)}" if all(res) else f"❌ {_nm}: {sum(res)}/{len(res)}")
os.chdir(H)
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
