# ➕🎚️ the plus and range bots through 8 price paths in the trial sandbox (v3.36.44) — the owner (14-11): «افحص البوت البلس كليا اشك فيه
#   مشاكل». The real engine in the closed box (fake clock · fake OKX · no network · fake keys) over 3 days of minutes per path:
#   oscillate ±3% · crash −25% and recover · pump +25% and back · saw · ⏸ buying paused on the drop · ⏸ selling paused on the pump ·
#   both paused · no coins at all. After each path:
#   · it ran to the end · OKX refused nothing but «not enough dollars» (51008 — the crash spends them all)
#   · no line repeated more than 30 times (the trade lines aside) · no two live orders on one price
#   · ➕ the sells the book promises never exceed the coins in the wallet (🎚️ range prints its whole ladder from the start by design)
#   · the log prints clean numbers (no float tail like 0.12000000000000001 — p67 · p69 · the sandbox's own numbers p68)
#   python3 devtests/t_plus_paths.py [Holy_Dashboard.pyw] [-q] [--range] [--only=path]
import importlib.machinery, importlib.util, json, math, os, re, shutil, sys, tempfile, urllib.request, collections

DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Holy_Dashboard.pyw")))
Q = "-q" in sys.argv
KIND = "grid_range" if "--range" in sys.argv else "grid_plus"
ONLY = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="pluspaths_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pp", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pp", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
SYM, DT = "SOL-USDT", 60.0
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
EV = {"folder": None, "log": [], "state": None, "hooks": {}, "snap": []}
_mk = m._bt_tmp.mkdtemp
m._bt_tmp.mkdtemp = lambda *a, **k: EV.__setitem__("folder", _mk(*a, **k)) or EV["folder"]
_rm = m.shutil.rmtree


def _keep(p, *a, **k):
    if EV["folder"] and os.path.abspath(p) == os.path.abspath(EV["folder"]):
        try:
            EV["log"] = json.load(open(os.path.join(p, "trade_history_SOL.json"), encoding="utf-8")) or []
        except Exception:
            EV["log"] = []
        try:
            EV["state"] = json.load(open(os.path.join(p, f"grid_state_{SYM}.json"), encoding="utf-8"))
        except Exception:
            EV["state"] = None
    return _rm(p, *a, **k)


m.shutil.rmtree = _keep
_Clock = m._BtClock


class Clock(_Clock):
    def __init__(self, ex, px_, t0, dt, on_point):
        def hook(i):
            on_point(i)
            f = EV["hooks"].get(i)
            if f or i % 50 == 0:
                sp = os.path.join(EV["folder"], f"grid_state_{SYM}.json")
                try:
                    st = json.load(open(sp, encoding="utf-8"))
                except Exception:
                    return
                if i % 50 == 0:
                    EV["snap"].append((i, ex.p, dict(ex.bal), dict(ex.frz), st))
                if f:
                    f(st, ex)
                    json.dump(st, open(sp, "w", encoding="utf-8"))
        super().__init__(ex, px_, t0, dt, hook)


m._BtClock = Clock


def norm(s):
    return re.sub(r"[0-9]+(\.[0-9]+)?(e-?[0-9]+)?", "#", s)


def run(name, px, hooks=None, q=400.0, b=6.0, cfg=None):
    EV.update(hooks=hooks or {}, snap=[], log=[], state=None)
    P0 = px[0]
    CFG = {"grid_percentage": 0.006, "usd_value": 10.0, "min_price": P0 * 0.5, "forced_base_price": P0, "knife_guard": False,
           "bot_type": KIND, "lower_price": P0 * 0.6 if KIND == "grid_range" else 0.0, "upper_price": P0 * 1.6 if KIND == "grid_range" else 0.0,
           "buy_offset": 0.012}
    CFG.update(cfg or {})
    r = m._bt_run(KIND, CFG, SYM, px, DT, q, b, SPEC, samples=400)
    ex = r["ex"]
    L = EV["log"]
    bad = []
    rej = collections.Counter(sc for t, sc in ex.rejects)
    if r["i_end"] < r["n"] - 1:
        bad.append(f"stopped at {r['i_end']}/{r['n']}: {r['why']}")
    for k in rej:
        if k != "51008":
            bad.append(f"refused {k} ×{rej[k]}")
    # spam: the same line (numbers aside) more than 30 times
    TRADE = ("[شراء", "[بيع", "ربح", "🟢", "🔴", "💰", "⏸️ [انتظار مؤقت]", "حُجز مستوى", "♻️", "🔄")
    cnt = collections.Counter(norm(e["msg"]) for e in L if not any(x in e["msg"] for x in TRADE))
    for k, v in cnt.most_common(5):
        if v > 30:
            bad.append(f"line ×{v}: {k[:120]}")
    # live orders: duplicates on one price / buys above the market / sells below
    live = [o for o in ex.orders.values() if o["state"] == "live"]
    dup = collections.Counter((o["side"], round(o["px"], 6)) for o in live)
    d2 = [k for k, v in dup.items() if v > 1]
    if d2:
        bad.append(f"two live orders on one price: {d2[:4]}")
    # the engine's book vs the wallet (every snapshot): coins promised to sells ≤ coins held
    worst = 0.0
    for i, p, bal, frz, st in EV["snap"]:
        need = sum(float((v or {}).get("locked_qty") or 0) for d in ("limit_sells", "virtual_sells", "accum_sells") for v in (st.get(d) or {}).values())
        have = bal.get("SOL", 0)
        if need > have * 1.02 + 0.02:
            worst = max(worst, need - have)
    if worst and KIND == "grid_plus":
        bad.append(f"sells promise {worst:.4f} SOL more than the wallet holds")
    tail = [e["msg"][:160] for e in L if re.search(r"\d\.\d*0000000\d|\d\.\d*9999999\d", e["msg"])]
    if tail:
        bad.append(f"float tail ×{len(tail)}: {tail[:2]}")
    sells = [f for f in ex.fills if f[1] == "sell"]
    buys = [f for f in ex.fills if f[1] == "buy"]
    RES.append(not bad)
    if Q and not bad:
        return r, L, bad
    print(f"{'✅' if not bad else '❌'} {KIND} {name}: {len(buys)} buys · {len(sells)} sells · realized {r['realized']:.4f}$ · "
          f"{len(L)} lines · refused {dict(rej)} · live {len(live)}" + ("" if not bad else "\n    " + "\n    ".join(bad)), flush=True)
    return r, L, bad


RES = []
P0 = 80.0
N = 4320                                        # 3 days of minutes
S = {
    "oscillate": [P0 * (1 + 0.03 * math.sin(i / 90.0)) for i in range(N)],
    "crash_recover": [P0 * (1 - 0.25 * min(1, i / 1440)) for i in range(1440)] + [P0 * 0.75] * 720 + [P0 * (0.75 + 0.35 * min(1, i / 2160)) for i in range(2160)],
    "pump_dump": [P0 * (1 + 0.25 * min(1, i / 1440)) for i in range(1440)] + [P0 * (1.25 - 0.25 * min(1, i / 1440)) for i in range(2880)],
    "saw": [P0 * (1 + 0.04 * (((i // 1) % 600) / 600.0 - 0.5)) for i in range(N)],
}
H = {
    "pause_buy_drop": (S["crash_recover"], {300: lambda st, ex: st.update(buy_floor=float(f"{ex.p:.10g}"), pause_buy=False),
                                            2100: lambda st, ex: st.update(buy_floor=0, pause_buy=False)}),
    "pause_sell_pump": (S["pump_dump"], {300: lambda st, ex: st.update(sell_ceiling=float(f"{ex.p:.10g}"), pause_sell=False),
                                         1500: lambda st, ex: st.update(sell_ceiling=0, pause_sell=False)}),
    "both_paused_osc": (S["oscillate"], {200: lambda st, ex: st.update(buy_floor=float(f"{ex.p:.10g}"), sell_ceiling=float(f"{ex.p:.10g}")),
                                         2600: lambda st, ex: st.update(buy_floor=0, sell_ceiling=0)}),
    "no_coins_pump": (S["pump_dump"], {}),
}
for k, px in S.items():
    if not ONLY or ONLY == k:
        run(k, px)
for k, (px, hk) in H.items():
    if not ONLY or ONLY == k:
        if k == "no_coins_pump":
            run(k, px, q=400.0, b=0.0)
        else:
            run(k, px, hk)
if ONLY != "none":
    shutil.rmtree(R, ignore_errors=True)
    _nm = "t_plus_paths" + (" --range" if KIND == "grid_range" else "")
    print(f"✅ {_nm}: {sum(RES)}/{len(RES)}" if RES and all(RES) else f"❌ {_nm}: {sum(RES)}/{len(RES)}")
    sys.exit(0 if RES and all(RES) else 1)
