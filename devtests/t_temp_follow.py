# ⏳ the temporary buy pause follows the price (v3.36.74 · p129) — the owner (21-11), a SUI grid bot: «ايقاف الشراء المؤقت ما يتحرك يمشي على
#   اقصى شي افحصه» ⇒ he chose «العدد يلحق السعر». The real engines (♾️ · ➕ · 🎚️) in the closed box (fake clock · paper exchange · no network)
#   with the guard's rounds and the card's own buttons, on the SUI story (0.8% · 2.5$ a level · 6$ · 320 SUI):
#   ① 0.72 ⇒ 0.60 with too few dollars: it closes at the gap's beginning · every level the price crosses is kept · nothing bought under it
#   ② back up to 0.6447: «⏳ مؤقت (N)» and «📦 شراء N» count only what is above the price (fewer) · the rest «تنتظر بأماكنها» (shown, not
#      counted) · the store itself is kept (nothing lost) · the floor stays where it closed
#   ③ down again to 0.62: the count grows again · ④ the open window says it: missed above · waiting under · ⑤ dollars + «🔓 افتح»: the
#      missed ones are bought in ONE order at the market · the ones under the price go back to their places on the ladder (orders at their
#      own prices or memory) — none bought above its level · no refused order · the pause opens
#   python3 devtests/t_temp_follow.py [Holy_Dashboard.pyw] [-q] [--kind=grid|grid_plus|grid_range]
import collections, importlib.machinery, importlib.util, json, math, os, shutil, sys, tempfile, urllib.request, collections

DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Holy_Dashboard.pyw")))
Q = "-q" in sys.argv
KINDS = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--kind=")] or ["grid_plus", "grid", "grid_range", "grid_step"]
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1600]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
urllib.request.urlopen = _no_net
R = tempfile.mkdtemp(prefix="t_tp_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_tp", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_tp", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
TG = []
m.tg_send = lambda t, *a, **k: TG.append(str(t)) or True
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.1", "minSz": "1"}]} if "instruments" in p else None)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the dashboard placed/canceled an order"))
SYM, QC, WID, DT, P0, T0 = "SUI-USDT", "USDT", "w1", 60.0, 0.7200, m._BT_T0
SPEC = {"tickSz": 0.0001, "lotSz": 0.1, "minSz": 1}
BOTS = os.path.join(R, "bots")
os.makedirs(BOTS, exist_ok=True)
m.ROOT = BOTS
m.CASHW_FILE = os.path.join(BOTS, "Holy_CashWatch.json")
STEP = {}


def step_cfg():
    if not STEP:
        body = {"symbol": SYM, "usd_value": "30", "step_parts": "3", "step_sell_pct": "0.8", "grid_pct": "1.5", "min_price": "50", "up_groups": "2"}
        m.PX[SYM] = P0
        keep = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs") if hasattr(m, k)}
        cfg, err = m._bt_dry_cfg("grid_step", body, SYM, SPEC, P0)
        for k, v in keep.items():
            setattr(m, k, v)
        STEP.update(cfg=cfg)
    return dict(STEP["cfg"])


def cfg_of(kind):
    if kind == "grid_step":
        return step_cfg()
    return {"grid_percentage": 0.008, "usd_value": 2.5, "min_price": 0.3, "forced_base_price": P0, "knife_guard": False, "bot_type": kind,
            "lower_price": 0.4 if kind == "grid_range" else 0.0, "upper_price": 1.2 if kind == "grid_range" else 0.0, "buy_offset": 0.012}


def need_of(cfg):
    u = float(cfg.get("usd_value") or 10)
    return u / max(1, int(float(cfg.get("step_parts") or 1))) if cfg.get("bot_type") == "grid_step" else u


class Box:
    """one bot folder (under ROOT, as the dashboard sees it) · the paper exchange · the guard's rounds · the card's buttons"""

    def __init__(self, kind, name, q0, b0, dca_hold=0.0):
        self.kind, self.cfg = kind, cfg_of(kind)
        self.cfg.update({"api_key": "backtest", "secret_key": "backtest", "passphrase": "backtest", "symbol": SYM, "is_demo": False, "auto_restart": False})
        self.f = os.path.join(BOTS, name)
        shutil.rmtree(self.f, ignore_errors=True)
        if os.path.exists(m.CASHW_FILE):
            os.remove(m.CASHW_FILE)                                  # each box is its own wallet (its own watcher file)
        m._CW_CACHE.update(sig=None, d=None)
        os.makedirs(self.f)
        json.dump(self.cfg, open(os.path.join(self.f, f"config_{SYM}.json"), "w"))
        self.ex = m._BtEx(SYM, P0, q0, b0, SPEC["tickSz"], SPEC["lotSz"], SPEC["minSz"], 0.0008, 0.001, 0.0005)
        self.g = m._gd_empty()
        self.dca_hold = dca_hold
        self.need = need_of(self.cfg)
        self.snaps, self.hooks, self.ctl = [], {}, {}
        self.src, self.script, _ = m.engine_for(self.cfg)
        b = {"dir": self.f, "symbol": SYM, "cfg": dict(self.cfg), "cfg_path": os.path.join(self.f, f"config_{SYM}.json")}
        self.bd = {os.path.realpath(self.f): b}

    def st(self):
        return json.load(open(os.path.join(self.f, f"grid_state_{SYM}.json"), encoding="utf-8"))

    def rec(self):
        return (m._cw_load()["bots"] or {}).get(m._cw_key(self.f))

    def press(self, action, value=None):
        m.bot_dirs = lambda: self.bd
        return m.control(os.path.relpath(self.f, m.ROOT), action, value)

    def round_(self, now):
        m.bot_dirs = lambda: self.bd
        st = self.st()
        cp = self.ex.p
        m.PX[SYM] = cp
        W = self.g["wallets"].setdefault(WID, {"label": "main", "coins": {}, "quotes": {}, "orders": {"missing": {}, "stray": {}}})
        rec = W["quotes"].setdefault(QC, {})
        rec.update(avail=self.ex.avail(QC), cash=self.ex.avail(QC), frozen=0.0, okx_frozen=None, bots_frozen=0.0, min_next=self.need,
                   dca_hold=self.dca_hold, ts=now)
        snap = {"wid": WID, "ok_bal": True, "bots": {"b": {"dir": self.f, "sym": SYM, "type": self.kind, "quote": QC, "usd": self.need,
                                                         "cp": cp, "g": float(self.cfg.get("grid_percentage") or 0.006), "alive": True, "destruct": False}}}
        m._gd_save(self.g)                                           # the open button reads the guard's last wallet round
        m._cw_low(self.g, WID, QC, rec, snap, now)
        m._cash_watch(self.g, now, [snap])
        m._gd_save(self.g)
        st = self.st()
        b = self.bd[os.path.realpath(self.f)]
        quiet = m._safe(m._accx_tick, b, st, cp, default=[]) or []
        r = self.rec()
        self.snaps.append({"t": now, "p": cp, "floor": float(st.get("buy_floor") or 0), "rec": dict(r) if r else None, "av": self.ex.avail(QC),
                           "chip": m._cw_card(self.f), "acc": len(st.get("accum_buys") or {}), "px": quiet, "ntp": len(self.ev("tp_close"))})

    def run(self, px, stop_at=None, off=0):
        """the story over px (one point a minute) · a guard round every 10 points · hooks at points · stop_at: the program stops there
        and is off `off` points (the price keeps moving — the exchange fills) then starts again from its files"""
        parts = [(0, stop_at if stop_at is not None else len(px) - 1)]
        if stop_at is not None:
            parts.append((stop_at + off, len(px) - 1))
        box = self
        for n, (a, z) in enumerate(parts):
            if n:
                for j in range(parts[0][1] + 1, a + 1):
                    self.ex.clock.t = T0 + j * DT
                    self.ex.set_price(px[j])
                    if j % 10 == 0:
                        self.round_(T0 + j * DT)             # the dashboard keeps watching while the bot is off
            sub = px[a:z + 1] if (n or stop_at is None) else px[a:z + 2]

            class C(m._BtClock):
                def __init__(s, ex, pp, t0, dt):
                    super().__init__(ex, pp, t0, dt, s._pt)
                    s.settle = m._BT_SETTLE if box.kind == "grid_step" else 0.0

                def _pt(s, j):
                    gi = a + j
                    f = box.hooks.get(gi)
                    if f:
                        f(box)
                    if gi % 10 == 0 and os.path.exists(os.path.join(box.f, f"grid_state_{SYM}.json")):
                        box.round_(box.ex.now())
                    if n == 0 and stop_at is not None and gi >= stop_at:
                        raise m._BtDone()
            c = C(self.ex, sub, T0 + a * DT, DT)
            m._bt_exec(self.src, self.script, self.f, m._bt_fakes(self.ex, c))
        return self

    def buys(self, t0=None, t1=None):
        return [f for f in self.ex.fills if f[1] == "buy" and (t0 is None or f[0] >= t0) and (t1 is None or f[0] < t1)]

    def rej(self, t0=None, t1=None):
        return [x for x in self.ex.rejects if (t0 is None or x[0] >= t0) and (t1 is None or x[0] < t1)]

    def ev(self, kind):
        return [e for e in self.g["events"] if e.get("kind") == kind]


def tt(i):
    return T0 + i * DT


def first_closed(bx):
    return next((s for s in bx.snaps if s["rec"]), None)



KINDS = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--kind=")] or ["grid", "grid_plus", "grid_range"]
LO, BACK, MID = 0.6000, 0.6447, 0.6200
PX = ([P0] * 30 + [P0 - (P0 - LO) * i / 900 for i in range(1, 901)] + [LO] * 120 + [LO + (BACK - LO) * i / 600 for i in range(1, 601)] + [BACK] * 120
      + [BACK - (BACK - MID) * i / 300 for i in range(1, 301)] + [MID] * 60)
I_LOW1, I_BACK1, I_MID1 = 30 + 900 + 120, 30 + 900 + 120 + 600 + 120, len(PX)
EV = {}
for kind in KINDS:
    K = {"grid": "♾️", "grid_plus": "➕", "grid_range": "🎚️"}[kind]
    EV.clear()
    bx = Box(kind, f"follow_{kind}", 6.0, 320.0)
    bd = bx.bd[os.path.realpath(bx.f)]

    def look(tag):
        def f(b):
            st = b.st()
            EV[tag] = {"p": b.ex.p, "ax": m._accx_snap(bd, st), "cw": m._cw_card(b.f), "n": len(st.get("accum_buys") or {}), "floor": float(st.get("buy_floor") or 0),
                       "lv": [p for p, q in m._tp_stored(bd, st, b.ex.p)], "info": b.press("temp_info")}
        return f
    bx.hooks.update({I_LOW1 - 1: look("low"), I_BACK1 - 1: look("back"), I_MID1 - 2: look("mid")})
    bx.run(PX)
    L, Bk, Md = EV.get("low") or {}, EV.get("back") or {}, EV.get("mid") or {}
    cl = first_closed(bx)
    ok(f"{K} ① the fall to 0.60 with too few dollars: closed at the gap's beginning ({cl and cl['rec'] and round(cl['rec']['temp'], 4)}) · "
       f"{L.get('n')} levels kept · «⏳ مؤقت ({(L.get('cw') or {}).get('n')})» = what the price crossed · nothing bought under the floor",
       cl and L.get("n", 0) >= 15 and (L.get("ax") or {}).get("nb") == len([p for p in L.get("lv") or [] if p >= L["p"]]) and (L.get("cw") or {}).get("n", 0) >= L["n"] - 2
       and not [f for f in bx.buys() if f[0] > cl["t"] + 1200 and f[2] < cl["rec"]["temp"]], (cl and cl["rec"], {k: L.get(k) for k in ("n", "ax", "cw")}))
    above = [p for p in Bk.get("lv") or [] if p >= BACK]
    ok(f"{K} ② back up to 0.6447: the count follows the price — «⏳ مؤقت ({(Bk.get('cw') or {}).get('n')})» · «📦 شراء {(Bk.get('ax') or {}).get('nb')}» = the {len(above)} "
       f"above the price (was {(L.get('cw') or {}).get('n')}) · {(Bk.get('cw') or {}).get('w')} under it wait in their places · the store kept ({Bk.get('n')}) · the floor where it closed",
       Bk and (Bk.get("cw") or {}).get("n") == len(above) == (Bk.get("ax") or {}).get("nb") and (Bk.get("cw") or {}).get("w") == Bk.get("n", 0) - len(above) > 0
       and len(above) < (L.get("cw") or {}).get("n", 0) and Bk.get("n") == L.get("n") and abs(Bk.get("floor", 0) - L.get("floor", -1)) < 1e-9,
       {k: Bk.get(k) for k in ("ax", "cw", "n", "floor")})
    above2 = [p for p in Md.get("lv") or [] if p >= MID]
    ok(f"{K} ③ down again to 0.62: the count grows again ({(Bk.get('cw') or {}).get('n')} ⇒ {(Md.get('ax') or {}).get('nb')})",
       Md and (Md.get("ax") or {}).get("nb") == len(above2) > len(above), {k: Md.get(k) for k in ("ax", "cw")})
    I = Bk.get("info") or {}
    ok(f"{K} ④ the open window's numbers: missed above {I.get('na')} · waiting under {I.get('nw')} (of {I.get('n')})", I.get("ok") and I.get("na") == len(above)
       and I.get("nw") == I.get("n", 0) - len(above), I)
    # ⑤ the dollars come back at 0.6447 and the owner opens: the missed in one market order · the rest back to the ladder
    bx2 = Box(kind, f"follow2_{kind}", 6.0, 320.0)
    bd2 = bx2.bd[os.path.realpath(bx2.f)]
    I_OPEN = I_BACK1 - 60

    def dep_open(b):
        st = b.st()
        lv = m._tp_stored(bd2, st, b.ex.p)
        EV["lv5"], EV["p5"] = lv, b.ex.p
        b.ex.bal[QC] += 200.0
        b.round_(b.ex.now())
        EV["i5"] = b.press("temp_info")
        EV["t5"] = b.ex.now()
        EV["o5"] = b.press("temp_open")
    bx2.hooks[I_OPEN] = dep_open
    bx2.run(PX[:I_BACK1])
    lv5, p5, o5, i5 = EV.get("lv5") or [], EV.get("p5") or 0, EV.get("o5") or {}, EV.get("i5") or {}
    up5 = [(p, q) for p, q in lv5 if p >= p5]
    b5 = bx2.buys(EV.get("t5", 0))
    mk = [f for f in b5 if f[0] < EV.get("t5", 0) + 600]
    got = sum(f[3] for f in mk)
    st5 = bx2.st()
    back = sorted(round(float(v.get("target_price")), 4) for d_ in ("limit_buys", "virtual_buys") for v in (st5.get(d_) or {}).values())
    under = [round(p, 4) for p, q in lv5 if p < p5]
    ok(f"{K} ⑤ dollars + «🔓 افتح» at {p5:.4f}: «{o5.get('msg', '')[:110]}» · the {len(up5)} missed bought in one order at the market ({got:.1f} SUI) · "
       f"the {len(under)} under the price back to their places ({sum(1 for x in under if any(abs(x - y) <= x * 0.003 for y in back))} found on the ladder) · "
       f"no refused order · the pause open · the store empty",
       o5.get("ok") and i5.get("na") == len(up5) and abs(got - sum(q for p, q in up5)) <= max(0.2, sum(q for p, q in up5) * 0.01)
       and all(f[2] <= p5 * 1.006 for f in mk) and all(any(abs(x - y) <= x * 0.003 for y in back) for x in under)
       and not bx2.rej(EV.get("t5", 0)) and not bx2.rec() and not (st5.get("accum_buys") or {}),
       (o5, i5, mk[:4], under[:6], back[:12], bx2.rej(EV.get("t5", 0))[:3], bx2.rec(), len(st5.get("accum_buys") or {})))

shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_temp_follow: {sum(res)}/{len(res)} (the temporary pause follows the price)")
sys.exit(0 if all(res) else 1)
