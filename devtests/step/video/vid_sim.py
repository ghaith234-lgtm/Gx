# 🎬 the bot for the video: the REAL graded-grid engine on the mock OKX, paced in real time, inside the dashboard's folder
#   (the dashboard shows its real card) · serves the «OKX side» for the video panel: /okx.json (the bot's open orders on the
#   exchange · the price · its fills · the profit · books = wallet) · waits for /go · scripted market: buys · sells · an order
#   deleted by hand · a power cut while the price moves · a −5% jump · fast oscillation.   python3 vid_sim.py ROOT PORT [PACE]
import json, os, shutil, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H))
import okxsim
from okxsim import Clock, Ex, Bot, Cut

R, PORT = os.path.abspath(sys.argv[1]), int(sys.argv[2])
PACE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
VIEW = {"cap": "", "events": [], "done": False, "off": False}
GO = threading.Event()


class Srv(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/go"):
            GO.set()
        body = json.dumps(VIEW, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


threading.Thread(target=ThreadingHTTPServer(("127.0.0.1", PORT), Srv).serve_forever, daemon=True).start()

fold = os.path.join(R, "step_xrp")
os.makedirs(fold, exist_ok=True)
shutil.copy(okxsim.ENGINE, os.path.join(fold, "main.py"))
c = Clock(t0=time.time())
ex = Ex(c, base=100, quote=1000)
CFG = {"usd_value": 15.0, "step_parts": 3, "step_sell": 0.005, "step_first": 0.01, "grid_percentage": 0.03, "min_price": 0.7,
       "up_groups": 1, "forced_base_price": 1.0, "step_window": 8}
b = Bot(ex, CFG, folder=fold)
WATCH = {}
seen = {"lines": 0}


def say(t):
    VIEW["cap"] = t


def ev(t):
    VIEW["events"] = ([t] + VIEW["events"])[:7]


def slot_of(oid):
    for k, s in ((b.st or {}).get("slots") or {}).items():
        if str((s.get("o") or {}).get("id")) == str(oid):
            return k
    return None


def publish(bb):
    S = (bb.st or {}).get("slots") or {}
    where = {str((s.get("o") or {}).get("id")): k for k, s in S.items() if (s.get("o") or {}).get("id")}
    rows = []
    for o in bb.mine_open():
        k = where.get(o["ordId"], "")
        j, kk = (k.split(":") + ["", ""])[:2] if k else ("", "")
        rows.append({"side": o["side"], "px": float(o["px"]), "sz": float(o["sz"]), "acc": float(o["acc"]), "j": j, "k": kk})
    rows.sort(key=lambda r: -r["px"])
    for line in bb.fill_lines[seen["lines"]:]:             # every fill as the engine logged it
        try:
            px = line.split("السعر: ")[1].split(" ")[0]
            q = line.split("الكمية: ")[1].split(" ")[0]
            lv = line.split("المستوى ")[1].split(" ")[0]
            pt = line.split("الجزء ")[1].split(" ")[0]
            if line.startswith("🟢"):
                ev(f"🟢 شراء {float(q):g} XRP بـ{px} — المستوى {lv} · الجزء {pt}")
            else:
                pr = line.split("الربح: ")[1].split("$")[0]
                ev(f"🔴 بيع {float(q):g} XRP بـ{px} — ربح {float(pr):+.4f}$ — المستوى {lv} · الجزء {pt}")
        except Exception:
            pass
    seen["lines"] = len(bb.fill_lines)
    if WATCH.get("key"):
        s = S.get(WATCH["key"]) or {}
        o = s.get("o") or {}
        if o.get("id") and str(o["id"]) != WATCH["old"] and o.get("st") == "live":
            j, kk = WATCH["key"].split(":")
            ev(f"↩️ رجع نشر أمر المستوى {j} · الجزء {kk} بنفس سعره {o.get('px')}")
            say("↩️ البوت لگى الأمر انلغى بلا تنفيذ ⇒ رجع نشره بنفس سعره (ولا خانة ضاعت)")
            WATCH.clear()
    nb, ns = bb.n_bl, bb.n_sl
    prs = [float(x.split("الربح: ")[1].split("$")[0]) for x in bb.fill_lines if x.startswith("🔴")]
    VIEW.update(px=float(ex.price), orders=rows,
                mem={"buy": sum(1 for s in S.values() if s["side"] == "buy" and not s.get("o")),
                     "sell": sum(1 for s in S.values() if s["side"] == "sell" and not s.get("o"))},
                stats={"tp": round(float((bb.st or {}).get("total_profit") or 0), 6), "nb": nb, "ns": ns, "cuts": bb.cuts,
                       "ok": not bb.errors, "audits": bb.audits, "err": bb.errors[:1],
                       "minpr": round(min(prs), 6) if prs else None}, off=False)


def loop(bb):
    publish(bb)
    time.sleep(PACE)


b.on_loop = loop


def cap(t):
    return ("do", lambda bb: say(t))


def px(p):
    return ("px", p, 3.0)


def cancel_by_hand(bb):
    mine = [o for o in bb.mine_open() if o["side"] == "buy"]
    if not mine:
        return
    o = max(mine, key=lambda o: o["px"])
    key = slot_of(o["ordId"])
    bb.ex._cancel(o["ordId"])
    WATCH.update(key=key, old=o["ordId"])
    j, k = (key or "?:?").split(":")
    ev(f"✋ مسحت بإيدك أمر شراء بالمنصة (المستوى {j} · الجزء {k} بـ{float(o['px']):g})")
    say("✋ أمر انمسح بالمنصة بالغلط…")
    publish(bb)


CUT = {"done": False}


def power_cut(bb):
    if CUT["done"]:                              # (the runner replays this step after the restart — once is the cut)
        return
    CUT["done"] = True
    say("⚡ انقطاع كهرباء! البوت طافي… والسعر نزل لـ0.9705 ⇒ أوامره تنفّذت بالمنصة وهو طافي")
    VIEW["off"] = True
    n0 = len(ex.fills)
    bb.ex.move("0.9705")
    VIEW["px"] = 0.9705
    VIEW["offfills"] = len(ex.fills) - n0
    ev(f"⚡ البوت طافي — {len(ex.fills) - n0} أمر تنفّذ بالمنصة وهو طافي")
    time.sleep(3.0)
    bb.cuts += 1
    raise Cut("power cut (video)")


def back(bb):
    say("🔌 رجع البوت: قرا ملفاته وسأل المنصة ⇒ لگى التنفيذات اللي صارت وهو طافي وحسبها مرة وحدة — ولا شي ضاع ولا تكرر")


P = []
P += [cap("🪜 يولد: المستوى 0 يبيع 3 أجزاء من عملاتك (1.01 · 1.015 · 1.02) · تحته شراءات ثابتة كل 3% · "
          "على المنصة الأقرب 8 لكل جهة والباقي بذاكرة البوت")] + [px(1.0)] * 4
P += [cap("📉 السعر ينزل نحو المستوى −1 (0.9708)…")] + [px(p) for p in (0.995, 0.99, 0.985, 0.98, 0.975, 0.972)]
P += [px(0.9702), cap("🟢 المستوى −1 اشترى أجزاءه الثلاثة (3 أوامر منفصلة بنفس السعر) ⇒ كل جزء صار إله بيعة: +1% · +1.5% · +2%"),
      px(0.9702), px(0.9702)]
P += [cap("📉 ويكمل نزول ⇒ المستوى −2 (0.9425) هم يشتري…")] + [px(p) for p in (0.965, 0.958, 0.95, 0.946, 0.9422, 0.9422)]
P += [cap("📈 السعر يصعد: كل جزء يبيع بسعره ⇒ يرجع يحط شراء لنفس كمية العملات بسعر مستواه الثابت (الربح دولار والعملة نفسها)")]
P += [px(p) for p in (0.948, 0.953, 0.958, 0.9625, 0.967, 0.972, 0.977, 0.9815, 0.986, 0.9905, 0.995)]
P += [("do", cancel_by_hand), px(0.995), px(0.995)]
P += [cap("🔴 فوق البداية يبيع من عملاتك بأسعارها: 1.01 ثم 1.015…")] + [px(p) for p in (1.0, 1.005, 1.0102, 1.0102, 1.0152, 1.0152)]
P += [("do", power_cut), ("do", back)] + [px(p) for p in (0.9705, 0.9705, 0.975, 0.98, 0.986, 0.99)]
P += [cap("📉 قفزة −5% بلحظة: المستويات اللي عبرها السعر تنرسل بسعر السوق وتنفّذ فوراً بسعر أحسن من سعرها"), px(0.938), px(0.938)]
P += [cap("📈 يرجع يصعد ويبيع اللي اشتراه بالقفزة…")] + [px(p) for p in (0.945, 0.952, 0.957, 0.962, 0.966, 0.97, 0.975, 0.981, 0.986, 0.991)]
P += [cap("🔁 تذبذب سريع: كل مرة يبيع بسعره ويرجع يشتري بمكانه — الربح يتجمّع")] + [px(p) for p in (0.969, 0.9815) * 5]
P += [cap("✅ الخلاصة")] + [px(p) for p in (0.99, 0.995)]

print("sim ready", flush=True)
say("⏳ …")
if os.environ.get("VID_DRY"):
    GO.set()
GO.wait()
b.run(P)
publish(b)
VIEW["done"] = True
say("✅ الخلاصة")
print(json.dumps({"tp": VIEW["stats"]["tp"], "nb": b.n_bl, "ns": b.n_sl, "cuts": b.cuts, "errors": b.errors[:2]}, ensure_ascii=False), flush=True)
time.sleep(0 if os.environ.get("VID_DRY") else 30)
