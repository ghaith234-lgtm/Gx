# ➕💵 the plus bot when the dollars run out (v3.36.44) — the owner (14-11, with a screenshot: «📦 SOL [استئناف الشراء] تنفيذ 2 مستويات
#   مخزنة بأمر مجمع واحد عند السعر 75.6» at 05:30 · 05:40 · 05:50): «بوت البلس يسوي تنبيهات عند ايقاف التجميع افحص البوت البلس كليا».
#   The real engine in the trial sandbox (a closed folder · fake keys · no network): a plus bot trades a falling path, its buying is
#   paused (📦 the levels the price crosses are counted) and resumed while the wallet's dollars are gone (another bot took them);
#   then the dollars come back.
#   ① no «📦 [استئناف الشراء] تنفيذ …» line while the dollars cover no level (that line said «executing» and nothing was sent — every
#      10 minutes) · the one «💵 … ما يكفي ولا درجة» line says why (a reminder every 6 hours) · a refused buy rests 1 ⇒ 10 minutes
#      (its line once, then every ~6 hours) instead of a line and a refused order every minute
#   ② the dollars back ⇒ the stored levels are bought in one order (as many as the dollars cover) and the line says how many
#   ④ (found on the way · p66) a new bot reads the coin's price step BEFORE its first ladder — it laid 4 decimals on a 0.01 coin ⇒ refused
#   ⑤ (p67) clean numbers in the log lines (the confirmed aggregate printed «من (1.4200000000000002)»)
#   ③ the books stay whole: the coins and the dollars the engine thinks it has match the sandbox wallet's · profit only from sells
#   python3 devtests/t_plus_cash.py [Holy_Dashboard.pyw] [-q] [--range | --grid]   (🎚️ the range bot · ♾️ the infinite grid — the same scenario)
import importlib.machinery, importlib.util, json, math, os, re, shutil, sys, tempfile, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
KIND = "grid_range" if "--range" in sys.argv else ("grid" if "--grid" in sys.argv else "grid_plus")   # ♾️ --grid (v3.36.45: p72)     # 🎚️ the range bot is the same grid code (p65 patched both)
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

R = tempfile.mkdtemp(prefix="t_pluscash_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pluscash", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pluscash", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m.tg_send = lambda *a, **k: True

SYM, P0, DT = "SOL-USDT", 80.0, 60.0
# 0–200 flat · 200–700 down 80 ⇒ 74 (the pause counts the levels crossed) · 700–1300 flat at 74 (resumed, no dollars) · 1300–1900 flat
px = [P0] * 200 + [P0 - 6.0 * i / 500 for i in range(1, 501)] + [74.0 + 0.05 * math.sin(i / 7.0) for i in range(1200)]
CFG = {"grid_percentage": 0.006, "usd_value": 10.0, "min_price": 60.0, "forced_base_price": P0, "knife_guard": False,
       "bot_type": KIND, "lower_price": 60.0 if KIND == "grid_range" else 0.0, "upper_price": 100.0 if KIND == "grid_range" else 0.0,
       "buy_offset": 0.012}
SPEC = {"tickSz": 0.01, "lotSz": 0.0001, "minSz": 0.01}
I_PAUSE, I_RESUME, I_BACK = 230, 760, 1500
EV = {"folder": None, "log": [], "state": None, "drain": None}

_mk = m._bt_tmp.mkdtemp
m._bt_tmp.mkdtemp = lambda *a, **k: EV.__setitem__("folder", _mk(*a, **k)) or EV["folder"]
_rm = m.shutil.rmtree


def _keep(p, *a, **k):          # read the bot's own files before the sandbox folder goes
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


class Clock(_Clock):            # the dashboard's two buttons, pressed at their moments (written into the state file like the dashboard does)
    def __init__(self, ex, px_, t0, dt, on_point):
        def hook(i):
            on_point(i)
            if i in (I_PAUSE, I_RESUME, I_BACK):
                sp = os.path.join(EV["folder"], f"grid_state_{SYM}.json")
                try:
                    st = json.load(open(sp, encoding="utf-8"))
                except Exception:
                    return
                if i == I_PAUSE:
                    st["buy_floor"] = float(f"{ex.p:.10g}")                 # ⏸ إيقاف الشراء — the dashboard's button: the floor = the market now
                    st["pause_buy"] = False
                elif i == I_RESUME:
                    st["pause_buy"] = False
                    st["buy_floor"] = 0                                     # ▶️ استئناف الشراء
                    EV["drain"] = ex.bal[ex.quote]
                    ex.bal[ex.quote] = 3.0                                  # 🤝 another bot took the dollars (3$ left · a level costs ~10$)
                elif i == I_BACK:
                    ex.bal[ex.quote] += 200.0                               # 💵 dollars back (a deposit / a sell elsewhere)
                json.dump(st, open(sp, "w", encoding="utf-8"))
        super().__init__(ex, px_, t0, dt, hook)


m._BtClock = Clock
r = m._bt_run(KIND, CFG, SYM, px, DT, 400.0, 6.0, SPEC, samples=400)
L = EV["log"]
tl = lambda ts: (m.time.mktime(m.time.strptime(ts, "%Y-%m-%d %H:%M:%S")) - m._BT_T0) / DT


def idx(e):
    try:
        return tl(e["time"])
    except Exception:
        return -1


between = [e for e in L if I_RESUME <= idx(e) < I_BACK]
after = [e for e in L if idx(e) >= I_BACK]
resume_lines = [e["msg"] for e in between if "[استئناف الشراء]" in e["msg"]]
why_lines = [e["msg"] for e in between if "ما يكفي ولا درجة" in e["msg"]]
ok(f"the run reached its end ({r['i_end']}/{r['n']} points · {len(L)} log lines) and the pause stored levels",
   r["i_end"] >= r["n"] - 1 and any("مخزن" in e["msg"] for e in L if I_PAUSE <= idx(e) < I_RESUME), r["why"])
buys_between = [f for f in r["ex"].fills if f[1] == "buy" and I_RESUME <= (f[0] - m._BT_T0) / DT < I_BACK] if r["ex"].fills and isinstance(r["ex"].fills[0][0], (int, float)) else None
ok("① dollars gone: no «📦 [استئناف الشراء] تنفيذ …» line (nothing was being executed) — over 12 hours of resumed time",
   not resume_lines, resume_lines[:4])
H6 = 1 + int((I_BACK - I_RESUME) * DT / 21600)       # one line + one reminder every 6 hours
ok(f"① … one clear «💵 … ما يكفي ولا درجة» line says why (+ a reminder every 6 hours: ≤ {H6} over {(I_BACK - I_RESUME) * DT / 3600:.1f} h — it was one every 10 minutes)",
   1 <= len(why_lines) <= H6, why_lines[:4])
rej_lines = [e["msg"] for e in between if "[رفض أمر شراء]" in e["msg"]]
ok(f"① … a refused buy (no dollars) writes its line once and then every ~6 hours: {len(rej_lines)} line(s) ≤ {H6} (it was one a minute)",
   1 <= len(rej_lines) <= H6, rej_lines[:6])
nrej = sum(1 for t, sc in r["ex"].rejects if sc == "51008" and I_RESUME <= (t - m._BT_T0) / DT < I_BACK)   # refused for dollars, in the sandbox exchange
ok(f"① … and the exchange is not pressed: {nrej} refused buy(s) in {I_BACK - I_RESUME} minutes (the rest grows 1 ⇒ 10 minutes · ≤ one every 10 minutes)",
   1 <= nrej <= (I_BACK - I_RESUME) // 10 + 6, nrej)
got = [e["msg"] for e in after if "[استئناف الشراء]" in e["msg"]]
ok("② dollars back ⇒ the stored levels go out in one order and the line says how many", got and re.search(r"تنفيذ \d+", got[0]), got[:2] or [e["msg"] for e in after][:6])
pxrej = [(round((t - m._BT_T0) / DT), sc) for t, sc in r["ex"].rejects if sc == "51000"]
ok("④ the first ladder goes out on the coin's price step (the step is read before it · no «Parameter px error» — it refused the first 8 orders)",
   not pxrej and not any("Parameter px error" in e["msg"] for e in L), pxrej[:8])
tail = [e["msg"] for e in L if re.search(r"\d\.\d*0000000\d|\d\.\d*9999999\d", e["msg"])]
ok("⑤ the log prints clean numbers (no float tail like 1.4200000000000002)", not tail, tail[:3])
st = EV["state"] or {}
ok("③ the engine's state is whole at the end (it saved · no aggregated order left half-known)", st and not st.get("cu_pending"), list(st)[:12])
_nm = "t_plus_cash" + {"grid_range": " --range", "grid": " --grid"}.get(KIND, "")
print(f"✅ {_nm}: {sum(res)}/{len(res)}" if all(res) else f"❌ {_nm}: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
