# 🔌 the owner (16-11): «عند نزل مثلا ١٥ واتت الكهرباء او اشتغل البرنامج هل راح يقف من نفس النقطه ام من اول طلب شراء لان هنا راح اتصير
#   فجوة شراء». The real grid engines (♾️ main.py · ➕ plus · 🎚️ range — the dashboard's embedded copies) in the closed box (fake clock ·
#   paper exchange · no network · fake keys). Each story is run twice on the same prices:
#     · without a stop (the reference)
#     · the program stops, the price falls ~15 levels while it is off (the orders resting on the exchange fill there), the program starts
#       again from its files and the story goes on
#   and compared at the bottom and after the price comes back:
#     · no gap: the coins the bot holds at the bottom = the reference (every level between the last buy and the price is bought — the
#       ones the exchange filled while off + one grouped order for the rest at the current price, cheaper)
#     · nothing bought twice · no refused order but «not enough dollars» · no two live orders on one price · the bot's book = the wallet
#   With ⏸ buying paused before the stop: the levels crossed while off are stored (not bought) · the stop doesn't lose them · ▶️ buys
#   exactly those at once.
#   🪜 the step bot too (several buys per level — its own settings from deploy_step): the same stop/fall/restart, slot by slot.
#   python3 devtests/t_gap_restart.py [Holy_Dashboard.pyw] [-q] [--kind=grid|grid_plus|grid_range|grid_step]
import importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, urllib.request, collections

DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Holy_Dashboard.pyw")))
Q = "-q" in sys.argv
KINDS = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--kind=")] or ["grid", "grid_plus", "grid_range", "grid_step"]
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="gaprestart_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_gr", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_gr", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.01", "lotSz": "0.000001", "minSz": "0.001"}]} if "instruments" in p else None)   # the coin's rules (no network)
SYM, DT, P0, G = "SOL-USDT", 60.0, 80.0, 0.006
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
T0 = m._BT_T0


class Clock(m._BtClock):
    """the trial clock + hooks (state edits at a point, like the card's buttons) + the stop (the process dies at a point)"""
    def __init__(self, ex, px, t0, dt, hooks, folder, stop_at=None, base_i=0, settle=0.0):
        self.hooks, self.folder, self.stop_at, self.base_i = hooks, folder, stop_at, base_i
        super().__init__(ex, px, t0, dt, self._pt)
        self.settle = settle                                     # 🪜 the step bot's own pace in the box (as _bt_run)

    def _pt(self, j):
        gi = self.base_i + j
        f = self.hooks.get(gi)
        if f:
            sp = os.path.join(self.folder, f"grid_state_{SYM}.json")
            st = json.load(open(sp, encoding="utf-8"))
            f(st, self.ex)
            m.save_json_atomic(sp, st)
        if self.stop_at is not None and gi >= self.stop_at:
            raise m._BtDone()                                    # ⚡ the program stops here (like closing it / a power cut)


def snap(folder, ex, per_px=1):
    """per_px: live orders allowed on one price (🪜 the step bot puts its N parts of a level on the same price — by design)"""
    st = json.load(open(os.path.join(folder, f"grid_state_{SYM}.json"), encoding="utf-8"))
    live = [o for o in ex.orders.values() if o["state"] == "live"]
    dup = [k for k, v in collections.Counter((o["side"], round(o["px"], 6)) for o in live).items() if v > per_px]
    sells_need = sum(float((v or {}).get("locked_qty") or 0) for d in ("limit_sells", "virtual_sells", "accum_sells") for v in (st.get(d) or {}).values())
    return {"coins": ex.bal["SOL"] + ex.frz["SOL"], "usd": ex.bal["USDT"] + ex.frz["USDT"], "buys": len([f for f in ex.fills if f[1] == "buy"]),
            "sells": len([f for f in ex.fills if f[1] == "sell"]), "accum": len(st.get("accum_buys") or {}), "dup": dup,
            "buy_px": [f[2] for f in ex.fills if f[1] == "buy"],
            "rej": sorted({c for _, c in ex.rejects}), "need": sells_need, "profit": float(st.get("total_profit") or 0), "st": st}


STEP = {}


def step_cfg():
    """🪜 the step bot's own config — deploy_step's (as the deploy form writes it) · several buys per level"""
    if not STEP:
        body = {"symbol": SYM, "usd_value": "30", "step_parts": "3", "step_sell_pct": "0.8", "grid_pct": "1.5", "min_price": "50", "up_groups": "2"}
        m.PX[SYM] = P0
        P = m.bt_prep({"kind": "grid_step", "body": body})
        keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs") if hasattr(m, k)}
        cfg, err = m._bt_dry_cfg("grid_step", body, SYM, P["spec"], P0)
        for k, v in keep.items():
            setattr(m, k, v)
        STEP.update(cfg=cfg, q=float(P["quote_def"]), b=float(P["base_def"]), spec=P["spec"])
    return STEP


def story(kind, px, stop_at=None, off=0, hooks=None, q=400.0, b=3.0):
    """one story · stop_at: the program stops at that point and is off for `off` points (the price keeps moving · the exchange fills)"""
    folder = tempfile.mkdtemp(prefix="gr_", dir=R)
    spec = SPEC
    if kind == "grid_step":
        S_ = step_cfg()
        q, b, spec = S_["q"], S_["b"], S_["spec"]
        cfg = dict(S_["cfg"])
    else:
        cfg = {"grid_percentage": G, "usd_value": 10.0, "min_price": P0 * 0.5, "forced_base_price": P0, "knife_guard": False, "bot_type": kind,
               "lower_price": P0 * 0.6 if kind == "grid_range" else 0.0, "upper_price": P0 * 1.4 if kind == "grid_range" else 0.0, "buy_offset": 0.012}
    cfg.update({"api_key": "backtest", "secret_key": "backtest", "passphrase": "backtest", "symbol": SYM, "is_demo": False, "auto_restart": False})
    ex = m._BtEx(SYM, px[0], q, b, spec["tickSz"], spec["lotSz"], spec["minSz"], 0.0008, 0.001, 0.0005)
    json.dump(cfg, open(os.path.join(folder, f"config_{SYM}.json"), "w"))
    src, script, _v = m.engine_for(cfg)
    hooks = dict(hooks or {})
    parts = [(0, stop_at if stop_at is not None else len(px) - 1)]
    if stop_at is not None:
        parts.append((stop_at + off, len(px) - 1))
    whys = []
    for n, (a, z) in enumerate(parts):
        if n:                                                # ⚡ off: the price moves without the bot — the exchange fills its resting orders
            for j in range(parts[0][1] + 1, a + 1):
                ex.clock.t = T0 + j * DT
                ex.set_price(px[j])
        sub = px[a:z + 1] if n or stop_at is None else px[a:z + 2]
        c = Clock(ex, sub, T0 + a * DT, DT, hooks, folder, stop_at=(stop_at if n == 0 and stop_at is not None else None), base_i=a,
                  settle=m._BT_SETTLE if kind == "grid_step" else 0.0)
        whys.append(m._bt_exec(src, script, folder, m._bt_fakes(ex, c)))
    out = snap(folder, ex, per_px=int(cfg.get("step_parts") or 1) if kind == "grid_step" else 1)
    out["whys"] = whys
    out["q0"], out["b0"] = q, b
    shutil.rmtree(folder, ignore_errors=True)
    return out


# the story: flat at 80 · down 9% (≈15 levels of 0.6%) · held at the bottom · back to 80
N0, ND, NB, NU = 60, 40, 120, 160
LOW = P0 * 0.91
PX = [P0] * N0 + [P0 - (P0 - LOW) * i / ND for i in range(1, ND + 1)] + [LOW] * NB + [LOW + (P0 - LOW) * i / NU for i in range(1, NU + 1)] + [P0] * 60
I_BOT = N0 + ND + NB - 1                                      # the last point at the bottom
PX_BOT = PX[:I_BOT + 1]
for kind in KINDS:
    ref_b = story(kind, PX_BOT)
    cut_b = story(kind, PX_BOT, stop_at=N0 + 2, off=ND + 5)
    q0 = ref_b["q0"]
    per = (float(step_cfg()["cfg"]["usd_value"]) / float(step_cfg()["cfg"]["step_parts"])) if kind == "grid_step" else 10.0   # $ in one buy order
    tol = per / LOW * 0.6                                                       # under one order's coins (the rounding of a grouped order)
    lv = int(round(math.log(P0 / LOW) / math.log(1 + G)))
    nb_ref = ref_b["buys"]
    ok(f"{kind} · the program stops at 80, the price falls ~9% (to {LOW:.2f} · {nb_ref} buys in the run with no stop) while it is off, it "
       f"starts again: at the bottom it holds the same coins as the run with no stop (stop {cut_b['coins']:.4f} · no stop {ref_b['coins']:.4f} SOL) — "
       f"no gap, nothing twice", abs(cut_b["coins"] - ref_b["coins"]) <= tol and ref_b["coins"] - ref_b["b0"] > per / P0 * 8 and not cut_b["dup"]
       and set(cut_b["rej"]) <= {"51008"} and all(w in ("end", "returned") for w in cut_b["whys"]), (cut_b, ref_b))
    ok(f"{kind} · … the dollars it spent are no more than without a stop (the missed levels bought at the bottom price — cheaper): "
       f"stop {q0 - cut_b['usd']:.2f}$ · no stop {q0 - ref_b['usd']:.2f}$", q0 - cut_b["usd"] <= q0 - ref_b["usd"] + 0.5, (cut_b["usd"], ref_b["usd"]))
    ref = story(kind, PX)
    cut = story(kind, PX, stop_at=N0 + 2, off=ND + 5)
    ok(f"{kind} · … and after the price comes back to 80: its book = the wallet (every sell has its coins) · no refused order but «not enough "
       f"dollars» · profit stop {cut['profit']:.4f}$ · no stop {ref['profit']:.4f}$",
       (cut["need"] <= cut["coins"] + 1e-6 if kind in ("grid", "grid_plus") else cut["need"] <= ref["need"] + 1e-6)   # 🎚️ prints its whole ladder to the ceiling by design (as in t_plus_paths) · 🪜 keeps its own slots ⇒ against its own no-stop run
       and not cut["dup"] and set(cut["rej"]) <= {"51008"} and cut["profit"] >= ref["profit"] * 0.8 - 0.01, (cut, ref))
    # ⏸ buying paused (at 80) before the stop · the stop · the fall while off · start again · ▶️ at the bottom
    HP = {N0 - 10: lambda st, ex: st.update(buy_floor=float(f"{ex.p:.10g}"), pause_buy=False)}
    paused = story(kind, PX_BOT, stop_at=N0 + 2, off=ND + 5, hooks=HP)
    under = [p_ for p_ in paused["buy_px"] if p_ < P0 * (1 - 1e-9)]
    ok(f"{kind} · ⏸ buying paused before the stop: after the fall and the restart nothing was bought under the floor (80)"
       + ("" if kind == "grid_step" else f" · the crossed levels are stored ({paused['accum']}) — none lost"),
       not under and not paused["dup"] and (kind == "grid_step" or paused["accum"] >= lv - 3), (under[:5], paused))
    HR = dict(HP)
    HR[I_BOT - 30] = lambda st, ex: st.update(buy_floor=0, pause_buy=False)                # ▶️ at the bottom (the card's resume button)
    resumed = story(kind, PX_BOT, stop_at=N0 + 2, off=ND + 5, hooks=HR)
    ok(f"{kind} · … ▶️ at the bottom buys exactly the crossed levels at once: coins {resumed['coins']:.4f} = no pause {ref_b['coins']:.4f} SOL "
       f"(cheaper: {q0 - resumed['usd']:.2f}$ ≤ {q0 - ref_b['usd']:.2f}$) · nothing left waiting",
       abs(resumed["coins"] - ref_b["coins"]) <= tol and resumed["accum"] == 0 and q0 - resumed["usd"] <= q0 - ref_b["usd"] + 0.5
       and not resumed["dup"], (resumed, ref_b))

shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_gap_restart: {sum(res)}/{len(res)}" if res and all(res) else f"❌ t_gap_restart: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
