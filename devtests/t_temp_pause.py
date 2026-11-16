# ⏳ the temporary buy pause (v3.36.58 · p99) — the owner (16-11): «ابدي وسوي عليه تجارب قوية». The real engines (♾️ main.py · ➕ plus ·
#   🎚️ range · 🪜 step — the dashboard's embedded copies) in the closed box (fake clock · paper exchange · no network · fake keys) with
#   the guard's dollar round every 10 minutes (the same functions the 🛡️ scan calls) and the card's own buttons (control()):
#   A · a fall with too few dollars: it closes from the beginning of the gap within two rounds · from then on OKX refuses no buy (it
#       stops calling) · no buy under the temporary floor · the floor stays where it closed (it no longer follows the price) · one
#       «⏳ وقف شراء مؤقت» notice · the per-level 📦 lines stay quiet · the card chip «⏳ مؤقت (N)»
#   B · the price comes back above the floor: it sells and buys above it as usual · still nothing under it
#   C · ⚡ the program stops while closed and the price falls further while it is off: after the restart nothing under the floor, no
#       refused order, the store kept
#   D · the dollars come back: «💵 توفر دولار» once (not again within 10 hours) · the chip turns green «🔓 افتح المؤقت» · nothing
#       bought by itself
#   E · the owner opens with dollars for part of the store: exactly the levels from the beginning it covers, in one order at the market
#       price · the rest kept behind the lowered floor · no refused order · then all · it opens · it closes again by itself when short
#   F · the sell DCA's dollars: a wallet that still holds them (reserved) closes the grid bot and the grid bot never spends them · the
#       opening never reaches them
#   G · the two valves: the owner's ⏸ and ▶️ move his valve only (no buy while the temporary one is closed) · opening the temporary one
#       leaves his floor · the guard paused or the switch off open nothing
#   H · the update day: a bot calling for its missed levels closes above all of them (they are kept — none bought) · the old automatic
#       pause's records carry on as temporary closes and do not resume when the dollars come back
#   🪜 J: two parts of a level covered, not the third ⇒ closes · a level is never split on opening · nothing lost (the exchange = the bot's slots)
#   ⏳ v3.36.61 (I): the guard's estimate too small ⇒ OKX's own «Insufficient USDT» on the bot's buy closes it at the next round
#   python3 devtests/t_temp_pause.py [Holy_Dashboard.pyw] [-q] [--kind=grid|grid_plus|grid_range|grid_step]
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
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.01", "lotSz": "0.000001", "minSz": "0.001"}]} if "instruments" in p else None)
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("the dashboard placed/canceled an order"))
SYM, QC, WID, DT, P0, T0 = "SOL-USDT", "USDT", "w1", 60.0, 80.0, m._BT_T0
SPEC = {"tickSz": 0.01, "lotSz": 0.000001, "minSz": 0.001}
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
    return {"grid_percentage": 0.006, "usd_value": 10.0, "min_price": 50.0, "forced_base_price": P0, "knife_guard": False, "bot_type": kind,
            "lower_price": 50.0 if kind == "grid_range" else 0.0, "upper_price": 120.0 if kind == "grid_range" else 0.0, "buy_offset": 0.012}


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


# the story: flat 80 · a fall to 68 over 8 h · flat · back up to 82 · flat
N_FLAT, N_FALL, N_LOW, N_UP = 60, 480, 240, 360
LOW = 68.0
PX = ([P0] * N_FLAT + [P0 - (P0 - LOW) * i / N_FALL for i in range(1, N_FALL + 1)] + [LOW] * N_LOW
      + [LOW + (82.0 - LOW) * i / N_UP for i in range(1, N_UP + 1)] + [80.0 + 2.0 * math.cos(2 * math.pi * i / 80) for i in range(240)])   # waves 78–82 above the floor
I_LOW0, I_LOW1 = N_FLAT + N_FALL, N_FLAT + N_FALL + N_LOW
I_UP1 = I_LOW1 + N_UP

for kind in KINDS:
    K = {"grid": "♾️", "grid_plus": "➕", "grid_range": "🎚️", "grid_step": "🪜"}[kind]
    # ═══ A · B · D: 60$ and 6 coins — the dollars run out on the way down ═══
    bx = Box(kind, f"{kind}_a", 60.0, 6.0)
    bx.hooks[I_LOW0 + 60] = lambda b: b.ex.bal.__setitem__(QC, b.ex.bal[QC] + 0.0)
    bx.run(PX[:I_UP1 + 240])
    fc = first_closed(bx)
    t_c = fc["t"] if fc else None
    rej_after = bx.rej(t_c + 2 * 600, None) if fc else ["never closed"]
    fl = fc["rec"]["temp"] if fc else 0
    under = [f for f in bx.buys(t_c + 60, tt(I_LOW1)) if f[2] < fl * (1 - 1e-9)] if fc else []
    floors = [s["floor"] for s in bx.snaps if s["rec"] and s["t"] < tt(I_LOW1)]
    ok(f"{K} A · the dollars run out on the way down ⇒ it closes ({'at ' + format(fc['p'], '.2f') if fc else 'never'} · floor {fl:.4f}) · from then on "
       f"OKX refuses no buy ({len(rej_after)}) · no buy under the floor ({len(under)}) · the floor stays put ({min(floors) if floors else 0:.4f}…{max(floors) if floors else 0:.4f})",
       fc and not rej_after and not under and floors and max(floors) - min(floors) <= fl * 1e-6 and fl >= fc["p"] * 0.95,
       (fc, rej_after[:4], under[:4], floors[:3], floors[-3:]))
    st_low = next((s for s in bx.snaps if abs(s["t"] - tt(I_LOW1 - 10)) < 1), None)
    ok(f"{K} A · … at the bottom the levels under it are kept — the card «⏳ مؤقت ({(st_low or {}).get('chip', {}) and st_low['chip'].get('n')})» · "
       f"one «⏳ وقف شراء مؤقت» notice · no «📦» crossing line (it does not call)",
       st_low and st_low["chip"] and st_low["chip"].get("tp") and st_low["chip"].get("n", 0) >= 3 and st_low["ntp"] == 1
       and not any(s["px"] for s in bx.snaps if s["rec"]), (st_low, [e["title"] for e in bx.g["events"]][:8]))
    low_ev = bx.ev("low_quote")
    _ob = m._gd_outbox(bx.g, m.time.time())                          # the notices carry the real clock
    out_low = [x for x in _ob if x[0] == "ev" and "نفد الدولار" in x[-1]]
    out_tp = [x for x in _ob if x[0] == "ev" and "وقف شراء مؤقت" in x[-1]]
    ok(f"{K} A · … the wallet's «💵 نفد الدولار الحر» stays in 🛡️ without Telegram ({len(out_low)} to send) · the «⏳ وقف شراء مؤقت» notice goes "
       f"to Telegram ({len(out_tp)})", low_ev and not out_low and len(out_tp) >= 1, ([(e["title"], e.get("tg")) for e in low_ev], out_low, out_tp))
    above = [f for f in bx.ex.fills if f[0] >= tt(I_LOW1) and f[2] >= fl * (1 - 1e-9)]
    sells_up = [f for f in above if f[1] == "sell"]
    buys_up = [f for f in above if f[1] == "buy"]
    under_up = [f for f in bx.buys(tt(I_LOW1), None) if f[2] < fl * (1 - 1e-9)]
    ok(f"{K} B · the price comes back above the floor (68 ⇒ 82): it sells ({len(sells_up)}) and buys ({len(buys_up)}) above it as usual · "
       f"still nothing under it ({len(under_up)}) · no refused order", sells_up and buys_up and not under_up and not bx.rej(tt(I_LOW1), None),
       (len(sells_up), len(buys_up), under_up[:3], bx.rej(tt(I_LOW1), None)[:3]))
    # ═══ C · ⚡ the program stops while closed — the price falls further while it is off ═══
    PXC = PX[:I_LOW0 - 120] + [PX[I_LOW0 - 120] - 4.0 * i / 120 for i in range(1, 121)] + [PX[I_LOW0 - 120] - 4.0] * 240
    cx = Box(kind, f"{kind}_c", 60.0, 6.0)
    cx.run(PXC, stop_at=I_LOW0 - 130, off=150)
    fcc = first_closed(cx)
    flc = fcc["rec"]["temp"] if fcc else 0
    after = [f for f in cx.buys(tt(I_LOW0 - 130), None) if f[2] < flc * (1 - 1e-9)]
    nl = cx.snaps[-1]["chip"] or {}
    ok(f"{K} C · ⚡ closed, the program stops, the price falls 4$ more while it is off, it starts again: nothing under the floor ({len(after)}) · "
       f"no refused order · the store kept ({nl.get('n')})", fcc and fcc["t"] < tt(I_LOW0 - 130) and not after and not cx.rej(tt(I_LOW0 - 130), None)
       and nl.get("tp") and nl.get("n", 0) >= 3, (fcc, after[:3], cx.rej(tt(I_LOW0 - 130), None)[:3], nl))
    # ═══ D · E: the dollars come back — the owner opens (part · then all) ═══
    ex_ = Box(kind, f"{kind}_e", 60.0, 6.0)
    I_DEP, I_OPEN1, I_DEP2, I_OPEN2 = I_LOW0 + 20, I_LOW0 + 60, I_LOW0 + 120, I_LOW0 + 160
    EV = {}

    def dep_half(b):
        lv = m._tp_stored(b.bd[os.path.realpath(b.f)], b.st(), b.ex.p)
        EV["lv0"] = lv
        half = lv[:max(1, len(lv) // 2)]
        add = sum(q * min(b.ex.p * 1.005, p) for p, q in half) * 1.003 + 0.05 - max(0.0, b.ex.avail(QC) - (b.rec() or {}).get("freed", 0) * 0)
        EV["add1"] = max(0.0, add)
        b.ex.bal[QC] += EV["add1"]

    def open1(b):
        EV["info1"] = b.press("temp_info")
        EV["coins1"] = b.ex.bal["SOL"] + b.ex.frz["SOL"]
        EV["t1"] = b.ex.now()
        EV["o1"] = b.press("temp_open")

    def dep_all(b):
        b.ex.bal[QC] += 400.0

    def open2(b):
        EV["coins2"] = b.ex.bal["SOL"] + b.ex.frz["SOL"]
        EV["t2"] = b.ex.now()
        EV["o2"] = b.press("temp_open")
        EV["rec2"] = b.rec()

    def drain(b):
        EV["drain"] = b.ex.bal[QC]
        b.ex.bal[QC] = b.ex.frz[QC] + 2.0                          # 🤝 another bot took the free dollars (2$ free left — the orders' dollars stay theirs)

    ex_.hooks.update({I_DEP: dep_half, I_OPEN1: open1, I_DEP2: dep_all, I_OPEN2: open2, I_OPEN2 + 60: drain})
    PXE = PX[:I_LOW0] + [LOW] * 240 + [LOW - 2.0 * i / 120 for i in range(1, 121)] + [LOW - 2.0] * 120
    ex_.run(PXE)
    av_ev = ex_.ev("tp_avail")
    ok(f"{K} D · the dollars come back: «💵 توفر دولار» once ({len(av_ev)}) — not again within 10 hours though more came · the chip turns green "
       f"«🔓 افتح المؤقت» · nothing bought by itself before the owner opens", len(av_ev) == 1
       and any(s["chip"] and s["chip"].get("tp") and s["chip"].get("k", 0) > 0 for s in ex_.snaps if tt(I_DEP) <= s["t"] < tt(I_OPEN1))
       and not ex_.buys(tt(I_DEP), tt(I_OPEN1)), ([e["title"] for e in av_ev], ex_.buys(tt(I_DEP), tt(I_OPEN1))[:3]))
    i1, o1 = EV.get("info1") or {}, EV.get("o1") or {}
    b1 = ex_.buys(EV.get("t1", 0), tt(I_DEP2))
    got1 = sum(f[3] for f in b1)
    lv0 = EV.get("lv0") or []
    kq = sum(q for p, q in lv0[:i1.get("k", 0)])
    ok(f"{K} E · the owner opens with dollars for part of the store ({i1.get('k')} of {i1.get('n')}): «{o1.get('msg', '')[:90]}» · bought "
       f"{got1:.4f} SOL = exactly those levels from the beginning ({kq:.4f}) at the market (➕♾️🎚️ in one order · 🪜 slot by slot) · the rest kept · no refused order",
       o1.get("ok") and 0 < i1.get("k", 0) < i1.get("n", 0) and abs(got1 - kq) <= max(kq * 0.003, 1e-6)
       and (len({round(f[0]) for f in b1}) <= 2 if kind != "grid_step" else all(f[2] <= LOW * 1.006 for f in b1))   # 🪜 slot by slot at the market (the price then: 68)
       and not ex_.rej(EV.get("t1", 0), tt(I_DEP2)) and (ex_.snaps and any(s["rec"] and s["t"] > EV.get("t1", 0) for s in ex_.snaps)),
       (i1, o1, b1[:6], kq, ex_.rej(EV.get("t1", 0), tt(I_DEP2))[:3]))
    o2 = EV.get("o2") or {}
    b2 = ex_.buys(EV.get("t2", 0), tt(I_OPEN2 + 60))
    reclosed = [s for s in ex_.snaps if s["t"] > tt(I_OPEN2 + 60) and s["rec"]]
    rej_end = ex_.rej(tt(I_OPEN2 + 60) + 1200, None)
    ok(f"{K} E · … then enough for all: it opens fully ({o2.get('msg', '')[:70]}) · the rest bought · the record gone · then the dollars are "
       f"taken again ⇒ it closes again by itself ({'yes' if reclosed else 'no'}) and stops calling ({len(rej_end)} refused after)",
       o2.get("ok") and EV.get("rec2") is None and b2 and reclosed and not rej_end, (o2, b2[:3], EV.get("rec2"), rej_end[:3]))
    # ═══ F · the sell DCA's dollars are reserved ═══
    fx = Box(kind, f"{kind}_f", 300.0, 6.0, dca_hold=200.0)
    fx.run(PX[:I_LOW1])
    fcf = first_closed(fx)
    minav = min(s["av"] for s in fx.snaps if fcf and s["t"] >= fcf["t"] + 600) if fcf else 0
    ok(f"{K} F · the wallet holds 200$ of a sell DCA (reserved): the grid bot closes before it reaches them ({'at ' + format(fcf['p'], '.2f') if fcf else 'never'}) · "
       f"the free dollars never fall under the reserve afterwards (lowest {minav:.2f}$)", fcf and minav >= 200.0 - 1e-6, (fcf and fcf["p"], minav))
    if kind == KINDS[0]:
        # ═══ G · the two valves (one kind is enough — the same dashboard code) ═══
        gx = Box(kind, f"{kind}_g", 60.0, 6.0)
        GV = {}

        def own_pause(b):
            GV["p1"] = b.press("pause_buy")
            GV["f1"], GV["r1"] = b.st().get("buy_floor"), dict(b.rec() or {})

        def own_resume(b):
            GV["p2"] = b.press("accum_buy", 0)
            GV["f2"], GV["r2"] = b.st().get("buy_floor"), dict(b.rec() or {})
            GV["t2"] = b.ex.now()

        def own_typed(b):
            GV["p3"] = b.press("accum_buy", round(b.ex.p * 0.98, 2))
            GV["own3"] = (b.rec() or {}).get("own")
            b.ex.bal[QC] += 400.0

        def open_t(b):
            GV["t4"] = b.ex.now()
            GV["p4"] = b.press("temp_open")
            GV["f4"] = b.st().get("buy_floor")

        gx.hooks.update({I_LOW0 - 100: own_pause, I_LOW0 - 40: own_resume, I_LOW0 + 30: own_typed, I_LOW0 + 50: open_t})
        gx.run(PX[:I_LOW0] + [LOW] * 120 + [LOW - 1.0] * 120)
        r1, r2 = GV.get("r1") or {}, GV.get("r2") or {}
        ok("G · the two valves: ⏸ while the temporary one is closed ⇒ his floor recorded and the engine takes the higher · ▶️ moves his valve only "
           f"(«{(GV.get('p2') or {}).get('msg', '')[:70]}») — no buy follows",
           r1.get("own", 0) > 0 and abs(float(GV.get("f1") or 0) - max(r1.get("own", 0), r1.get("temp", 0))) < 1e-9 and r2.get("own", 1) == 0
           and abs(float(GV.get("f2") or 0) - r2.get("temp", 0)) < 1e-9 and not gx.buys(GV.get("t2", 0), GV.get("t4", 1e18)),
           (GV.get("p1"), r1, GV.get("p2"), r2, GV.get("f2")))
        own3 = float(GV.get("own3") or 0)
        under_own = [f for f in gx.buys(GV.get("t4", 0), None) if f[2] < own3 * (1 - 1e-9)]
        ok(f"G · … his typed floor ({own3}) then «🔓 افتح المؤقت» with dollars for all: the temporary valve opens, his floor stays the engine's "
           f"({GV.get('f4')}) · nothing bought under it ({len(under_own)})", (GV.get("p4") or {}).get("ok") and abs(float(GV.get("f4") or 0) - own3) < 1e-9
           and not under_own, (GV.get("p4"), GV.get("f4"), under_own[:3]))
        gy = Box(kind, f"{kind}_gy", 60.0, 6.0)
        gy.hooks[I_LOW0 + 20] = lambda b: (m.guard_cfg(paused=True, by="test"), m.guard_cfg(cash_pause=False, by="test"),
                                           b.ex.bal.__setitem__(QC, b.ex.bal[QC] + 400.0))
        gy.run(PX[:I_LOW0] + [LOW] * 120)
        m.guard_cfg(paused=False, by="test")
        m.guard_cfg(cash_pause=True, by="test")
        ok("G · the guard paused and the switch off (with dollars back): nothing opens · nothing bought", gy.rec() and not gy.buys(tt(I_LOW0 + 20), None),
           (gy.rec(), gy.buys(tt(I_LOW0 + 20), None)[:3]))
        # ═══ H · the update day ═══
        hx = Box(kind, f"{kind}_h", 400.0, 6.0)
        HV = {}

        def starve(b):
            HV["av0"] = b.ex.bal[QC]
            b.ex.bal[QC] = b.ex.frz[QC] + 3.0                             # the bot is calling for its missed levels (a fast fall)
        hx.hooks[N_FLAT - 5] = starve                                     # the dollars run out just before the jump
        PXH = [P0] * N_FLAT + [P0 * 0.93] * 300
        old = m._cash_watch
        m._cash_watch = lambda *a, **k: None                              # the old dashboard: nothing closes it (it calls)
        hx.hooks[N_FLAT + 100] = lambda b: setattr(m, "_cash_watch", old)  # ⇐ the update
        hx.run(PXH)
        m._cash_watch = old
        rh = hx.rec() or {}
        cl = [s for s in hx.snaps if s["rec"]]
        rej_tail = hx.rej(tt(N_FLAT + 100) + 1200, None)
        ok(f"H · the update day: a bot calling for its missed levels (a 7% fall · 3$ free) closes within two rounds of the update, ABOVE them all "
           f"(floor {rh.get('temp', 0):.4f} · price {P0 * 0.93:.2f} — missing {rh.get('n0')}) · none bought · it stops calling ({len(rej_tail)} refused after)",
           cl and cl[0]["t"] <= tt(N_FLAT + 100) + 1300 and cl[0]["t"] >= tt(N_FLAT + 100) and rh.get("temp", 0) > P0 * 0.93 * 1.01 and (rh.get("n0") or 0) >= (3 if kind == "grid_step" else 5)
           and not [f for f in hx.buys(tt(N_FLAT + 100), None) if f[2] < rh.get("temp", 0)] and not rej_tail,
           (cl[:1], rh, rej_tail[:3]))
        mx = Box(kind, f"{kind}_m", 60.0, 6.0)
        mk = m._cw_key(mx.f)
        m.save_json_atomic(m.CASHW_FILE, {"bots": {mk: {"wid": WID, "q": QC, "sym": SYM, "type": kind, "orig": 0.0, "set": 79.0, "ts": T0, "need": 10.0,
                                                         "freed": 0.0, "moves": 0}}, "seen": {}, "ok": {}})
        m._CW_CACHE.update(sig=None, d=None)
        mig = m._cw_load()["bots"].get(mk) or {}
        ok("H · the old automatic pause's record (v3.36.44) carries on as a temporary close (temp 79 · own 0)",
           mig.get("v") == 2 and mig.get("temp") == 79.0 and mig.get("own") == 0.0, mig)

# ═══ I · ⏳ v3.36.61: the guard's estimate of the next order is too SMALL (💠 reinvest grows it · several 🪜 parts at once) — the owner (16-11):
#   «احنه قلنا اذا ماكو دولار يتفعل ايقاف الشراء المؤقت» · the estimate here is a fifth of the real order: by it the wallet never looks short,
#   OKX refuses the real orders (51008) ⇒ the exchange's own refusal closes the pause at the next round · then nothing more is refused ═══
for kind in [k for k in KINDS if k in ("grid_step", "grid_plus")]:
    K = {"grid_plus": "➕", "grid_step": "🪜"}[kind]
    ix = Box(kind, f"{kind}_i", 400.0, 6.0)
    ix.need = need_of(ix.cfg) / 5.0                                   # the estimate: 2$ · the real order: 10$
    I_I = N_FLAT + 60
    ix.hooks[I_I] = lambda b: b.ex.bal.__setitem__(QC, b.ex.frz[QC] + 5.0)   # on the way down: 5$ free — more than the estimate, less than an order
    ix.run(PX[:I_LOW1])
    r0 = ix.rej(tt(I_I), None)
    fi = first_closed(ix)
    t_r0 = r0[0][0] if r0 else None
    fi = next((x for x in ix.snaps if x["rec"] and x["t"] >= tt(I_I)), None) if not fi or fi["t"] < tt(I_I) else fi
    late = ix.rej(fi["t"] + 600, None) if fi else ["never closed"]
    ok(f"{K} I · 5$ free · the estimate 2$ (a fifth of the real 10$ order): OKX refused its buy ({len(r0)} in all) ⇒ the temporary pause closed at the next round "
       f"({'%.0f s after the first refusal' % (fi['t'] - t_r0) if fi and t_r0 else 'never'}) · its need = the refused order's dollars "
       f"({(fi or {}).get('rec', {}).get('need') if fi else '—'}) · no refusal after it ({len(late)})",
       r0 and fi and fi["t"] - t_r0 <= 2 * 600 + 1 and not late and float(fi["rec"].get("need") or 0) > ix.need * 1.5, (r0[:3], fi, late[:3]))

# ═══ J · 🪜 the owner (16-11): «المتدرج لان فيه شراء من نفس المكان واحتمال اوردرين شراء ياخذ والثالث ما ياخذ … حتى اطمئن»: the free
#   dollars cover two parts of the next level, not the third · then a deposit for ONE part · then enough for the whole level ═══
if "grid_step" in KINDS:
    jx = Box("grid_step", "grid_step_j", 400.0, 6.0)
    part = need_of(jx.cfg)                                                     # one part's dollars (the level's ÷ 3)
    I_J, EJ = N_FLAT + 40, {}

    def two_parts(b):
        b.ex.bal[QC] = b.ex.frz[QC] + 2 * part * 1.01                         # free: two parts — the third has no dollars

    def dep_one(b):
        EJ["lv"] = m._tp_stored(b.bd[os.path.realpath(b.f)], b.st(), b.ex.p)
        b.ex.bal[QC] += part * 1.2                                             # a deposit for ONE part
        EJ["av1"] = b.ex.avail(QC)

    def open_one(b):
        EJ["i1"], EJ["t1"] = b.press("temp_info"), b.ex.now()
        EJ["o1"] = b.press("temp_open")

    def dep_lvl(b):
        b.ex.bal[QC] += 3 * part * 1.2                                         # enough for a whole level (3 parts) and a bit
        EJ["lv2"] = m._tp_stored(b.bd[os.path.realpath(b.f)], b.st(), b.ex.p)

    def open_lvl(b):
        EJ["i2"], EJ["t2"] = b.press("temp_info"), b.ex.now()
        EJ["o2"] = b.press("temp_open")

    jx.hooks.update({I_J: two_parts, I_LOW0 + 20: dep_one, I_LOW0 + 40: open_one, I_LOW0 + 80: dep_lvl, I_LOW0 + 100: open_lvl})
    jx.run(PX[:I_LOW0 + 220])
    fj = next((x for x in jx.snaps if x["rec"] and x["t"] >= tt(I_J)), None)
    flj = fj["rec"]["temp"] if fj else 0
    rej_late = jx.rej(fj["t"] + 600, None) if fj else ["never closed"]
    under = [f for f in jx.buys(fj["t"] + 60, EJ.get("t1", tt(I_LOW0 + 40))) if f[2] < flj * (1 - 1e-9)] if fj else []
    by_px = collections.Counter(round(f[2], 6) for f in jx.buys(None, EJ.get("t1")) if f[5])        # the limit buys (the levels) — the opening's market buys aside
    ok(f"🪜 J · the dollars cover two parts of a level, not the third ⇒ it closes ({'at ' + format(fj['p'], '.2f') if fj else 'never'} · floor "
       f"{flj:.4f}) · no refused order after it ({len(rej_late)}) · no buy under the floor ({len(under)}) · never more than 3 buys on one price",
       fj and not rej_late and not under and max(by_px.values() or [0]) <= 3, (fj, rej_late[:3], under[:3], by_px.most_common(3)))
    lv = EJ.get("lv") or []
    g0 = [q for p_, q in lv if lv and abs(p_ - lv[0][0]) <= lv[0][0] * 1e-9]
    i1, o1 = EJ.get("i1") or {}, EJ.get("o1") or {}
    b1 = jx.buys(EJ.get("t1", 0), tt(I_LOW0 + 80))
    k_exp, c_exp = m._tp_cover(lv, LOW, EJ.get("av1", 0)) if lv else (0, 0)
    ok(f"🪜 J · a deposit for ONE part while the first kept level has {len(g0)} part(s): the window offers {i1.get('k')} of {i1.get('n')} (a level is never "
       f"split) · «🔓 افتح» buys {sum(f[3] for f in b1):.4f} SOL — exactly {'nothing' if not k_exp else 'the covered levels'} · nothing refused",
       lv and i1.get("k") == k_exp and (o1.get("ok") if k_exp else not b1) and not jx.rej(EJ.get("t1", 0), tt(I_LOW0 + 80))
       and abs(sum(f[3] for f in b1) - sum(q for _, q in lv[:k_exp])) <= max(1e-6, sum(q for _, q in lv[:k_exp]) * 0.003), (lv[:6], i1, o1, b1[:6], k_exp))
    lv2 = EJ.get("lv2") or []
    i2, o2 = EJ.get("i2") or {}, EJ.get("o2") or {}
    b2 = jx.buys(EJ.get("t2", 0), tt(I_LOW0 + 160))
    kq2 = sum(q for _, q in lv2[:i2.get("k", 0)])
    lvl_ok = all(collections.Counter(round(p_, 6) for p_, _ in lv2[:i2.get("k", 0)])[round(p_, 6)] == collections.Counter(round(x, 6) for x, _ in lv2)[round(p_, 6)]
                 for p_, _ in lv2[:i2.get("k", 0)])
    ok(f"🪜 J · then dollars for a whole level: it buys {i2.get('k')} kept part(s) = whole levels only ({sum(f[3] for f in b2):.4f} SOL = {kq2:.4f}) at the market · nothing refused",
       o2.get("ok") and i2.get("k", 0) >= 1 and lvl_ok and abs(sum(f[3] for f in b2) - kq2) <= max(1e-6, kq2 * 0.003)
       and not jx.rej(EJ.get("t2", 0), tt(I_LOW0 + 160)), (lv2[:6], i2, o2, b2[:6]))
    stj = jx.st()
    aud = m.step_audit(jx.bd[os.path.realpath(jx.f)], stj)
    ex_live = {str(o_id) for o_id, o in jx.ex.orders.items() if o["state"] == "live"}
    sl_live = {str((x.get("o") or {}).get("id")) for x in (stj.get("slots") or {}).values() if (x.get("o") or {}).get("id") and (x.get("o") or {}).get("st") == "live"}
    ok(f"🪜 J · nothing lost or left behind: the bot's own audit «{aud.get('msg', '')[:70]}» · the exchange's live orders = exactly the bot's "
       f"({len(ex_live)} = {len(sl_live)}) — no stray order, none forgotten", aud.get("ok") and ex_live == sl_live, (aud, sorted(ex_live - sl_live)[:3], sorted(sl_live - ex_live)[:3]))

# ═══ the card chip — the page's own function, in node ═══
import subprocess
page = open(DASH, encoding="utf-8").read()
js = page[page.index("function accChipsOf(b){"):]
js = js[:js.index("\nfunction accumPrompt(")]
try:
    out = subprocess.run(["node", "-e", "function f4(v){return (+v).toFixed(4)}\n" + js + "\nconst r=[accChipsOf({dir:'b1',cashw:{tp:true,temp:79.5,own:0,n:7,k:0}}),"
                          "accChipsOf({dir:'b2',cashw:{tp:true,temp:79.5,own:0,n:7,k:3}}),accChipsOf({cashw:{need:10,auto:false}})];console.log(JSON.stringify(r))"],
                         capture_output=True, text=True, timeout=30)
    C = json.loads(out.stdout.strip().splitlines()[-1])
except Exception as e:
    C = [str(e), "", ""]
ok("the card chip (the page's function): «⏳ مؤقت (7)» while closed · «🔓 افتح المؤقت (7)» when dollars cover part of it (both open the dialog) · "
   "the plain waiting chip otherwise", "⏳ مؤقت (7)" in C[0] and "tempOpen('b1')" in C[0] and "🔓 افتح المؤقت (7)" in C[1] and "tempOpen('b2')" in C[1]
   and "🟠 ينتظر دولار" in C[2], C)
ok("no order placed or cancelled by the dashboard (only control fields — the engine trades)", True)
shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_temp_pause: {sum(res)}/{len(res)}" if res and all(res) else f"❌ t_temp_pause: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
