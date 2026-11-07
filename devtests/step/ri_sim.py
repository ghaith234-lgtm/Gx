# 🪜💠 the bot for ui_ri: the REAL graded-grid engine with reinvest on the mock OKX, paced in real time, inside the dashboard's
#   folder (the dashboard shows its real card and writes its real requests: 💉 ➖ ⚖️ 🔓 — the engine picks them up) ·
#   /st.json = the engine's live state + the audit (books = wallet) · waits for /go · the market oscillates around level −1
#   (its parts buy and sell over and over, so the pots grow), then holds over it (calm: the UI acts on stable slots) until /stop.        python3 ri_sim.py ROOT PORT [PACE]
import json, os, shutil, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import okxsim
from okxsim import Clock, Ex, Bot

R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
PACE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
GO, STOP = threading.Event(), threading.Event()
VIEW = {}


class Srv(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/go"):
            GO.set()
        if self.path.startswith("/stop"):
            STOP.set()
        body = json.dumps(VIEW, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)


threading.Thread(target=ThreadingHTTPServer(("127.0.0.1", PORT), Srv).serve_forever, daemon=True).start()
fold = os.path.join(R, "step_xrp")
os.makedirs(fold, exist_ok=True)
shutil.copy(okxsim.ENGINE, os.path.join(fold, "main.py"))
c = Clock(t0=time.time())
ex = Ex(c, base=100, quote=1000)
CFG = {"usd_value": 15.0, "step_parts": 3, "step_sell": 0.005, "step_first": 0.01, "grid_percentage": 0.03, "min_price": 0.7,
       "up_groups": 1, "forced_base_price": 1.0, "step_window": 8, "reinvest": True, "reinvest_pct": 100}
b = Bot(ex, CFG, folder=fold)


def loop(bb):
    st = bb.st or {}
    VIEW.update(px=float(ex.price), errors=bb.errors[:3], audits=bb.audits, tp=float(st.get("total_profit") or 0),
                rb=st.get("reinvest") or {}, slots={k: {"side": s["side"], "q": s["q"], "g": s.get("g", 0), "sq": s.get("sq"),
                                                        "o": (s.get("o") or {}).get("sz")} for k, s in (st.get("slots") or {}).items()},
                orders={o["ordId"]: [o["side"], str(o["px"]), str(o["sz"])] for o in bb.mine_open()},
                lines=[m for m in bb.hist()[:60] if m.startswith(("💉", "➖", "⚖️", "🔄", "🔓", "🪙", "⚠️", "💠"))][:30])
    if STOP.is_set():
        raise okxsim.Stop()
    time.sleep(PACE)


b.on_loop = loop
OSC = [0.97, 0.9706, 0.981, 0.9858, 0.9907, 0.995]          # level −1 (0.9708): its parts buy, then sell at 0.9806 · 0.9854 · 0.9903
CALM = ("do", lambda bb: VIEW.update(calm=True))             # the pots grew ⇒ the price holds over level −1 (its parts are buys)
P = [("px", 1.0, 3.0)] * 2 + [("px", p, 3.0) for p in (0.99, 0.98)] + [("px", p, 3.0) for p in OSC * 30] + [CALM] + [("px", 0.995, 3.0)] * 4000
print("sim ready", flush=True)
GO.wait()
b.run(P)
print(json.dumps({"errors": b.errors[:2], "audits": b.audits}), flush=True)
